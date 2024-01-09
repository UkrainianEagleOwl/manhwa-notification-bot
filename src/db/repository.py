import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import User, UserWebsite, Bookmark, Website
from src.utils.log import logging
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from src.db.constant_manga_websites import AVAILABLE_WEBSITES


# Fernet key should be kept secret and loaded from an environment variable or secure storage
fernet_key = os.getenv("FERNET_KEY")
if fernet_key is None:
    raise ValueError("The FERNET_KEY environment variable is not set.")
cipher_suite = Fernet(fernet_key)


def create_user(db: Session, chat_id: int, notification_time: str, is_active: bool):
    try:
        db_user = User(
            chat_id=chat_id, notification_time=notification_time, is_active=is_active
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Can't create user for chat_id {chat_id}: {str(e)}")
        return None


def get_all_active_users_with_websites(db: Session):
    try:
        # Retrieve all active users and their associated websites
        active_users_with_websites = (
            db.query(User)
            .join(UserWebsite, User.chat_id == UserWebsite.chat_id)
            .join(Website, UserWebsite.website_id == Website.website_id)
            .filter(User.is_active == True)
            .all()
        )
        return active_users_with_websites
    except SQLAlchemyError as e:
        logging.error(f"Error retrieving active users with websites: {str(e)}")
        return []


def get_active_user_with_websites(db: Session, chat_id: int):
    try:
        # Retrieve the active user and their associated websites by chat_id
        active_user_with_websites = (
            db.query(User)
            .join(UserWebsite, User.chat_id == UserWebsite.chat_id)
            .join(Website, UserWebsite.website_id == Website.website_id)
            .filter(User.is_active == True, User.chat_id == chat_id)
            .first()
        )
        return active_user_with_websites
    except SQLAlchemyError as e:
        logging.error(
            f"Error retrieving active user with websites for chat_id {chat_id}: {str(e)}"
        )
        return None


def update_notification_time(db: Session, chat_id: int, new_notification_time: str):
    try:
        # Find the user by chat ID
        user = db.query(User).filter(User.chat_id == chat_id).first()
        if user:
            # Update the notification time
            user.notification_time = new_notification_time
            db.commit()
            return True
        else:
            logging.error(f"No user found for chat_id {chat_id}")
            return False
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Can't update notification time for chat_id {chat_id}: {str(e)}")
        return False


def update_user_website(db: Session, chat_id: int, website_id: int, website_data):
    try:
        # Encrypt the credentials
        encrypted_login = cipher_suite.encrypt(website_data["login"].encode())
        encrypted_password = cipher_suite.encrypt(website_data["password"].encode())

        # Find the existing user website association or create a new one
        db_user_website = (
            db.query(UserWebsite)
            .filter_by(chat_id=chat_id, website_id=website_id)
            .first()
        )

        if db_user_website:
            # Update the existing user's website data
            db_user_website.login = encrypted_login
            db_user_website.password = encrypted_password
        else:
            # Create a new UserWebsite association
            db_user_website = UserWebsite(
                chat_id=chat_id,
                website_id=website_id,
                login=encrypted_login,
                password=encrypted_password,
            )
            db.add(db_user_website)

        db.commit()
        return db_user_website
    except SQLAlchemyError as e:
        db.rollback()
        # It's good practice to also log the exception message itself
        logging.error(
            f"Can't update user website information for chat_id {chat_id} and website_id {website_id}: {str(e)}"
        )
        return None


def get_user_credentials(db: Session, chat_id: int, website_id: int):
    try:
        user_website = (
            db.query(UserWebsite)
            .filter_by(chat_id=chat_id, website_id=website_id)
            .first()
        )
        if user_website:
            # Decrypt the credentials
            decrypted_login = cipher_suite.decrypt(user_website.login).decode()
            decrypted_password = cipher_suite.decrypt(user_website.password).decode()
            return decrypted_login, decrypted_password
        else:
            return None, None
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"Can't get user credentials from database for chat_id {chat_id} and website_id {website_id}: {str(e)}"
        )
        return None, None


def get_all_user_bookmarks(db: Session, chat_id: int, website_id: int = None):
    try:
        query = (
            db.query(Bookmark)
            .join(UserWebsite, UserWebsite.id == Bookmark.user_website_id)
            .join(User, User.chat_id == UserWebsite.chat_id)
            .filter(User.chat_id == chat_id)
        )

        if website_id is not None:
            query = query.filter(UserWebsite.website_id == website_id)

        bookmarks = query.all()
        return bookmarks
    except SQLAlchemyError as e:
        logging.error(f"Can't get all user's bookmarks for chat_id {chat_id}: {str(e)}")
        return []


def get_recent_bookmarks(db: Session, chat_id: int, hours: int = 24):
    try:
        # Calculate the time 24 hours ago from now
        time_threshold = datetime.utcnow() - timedelta(hours=hours)

        # Retrieve all bookmarks updated within the last 24 hours
        recent_bookmarks = (
            db.query(Bookmark)
            .join(UserWebsite, UserWebsite.id == Bookmark.user_website_id)
            .join(User, User.chat_id == UserWebsite.chat_id)
            .filter(
                User.chat_id == chat_id, Bookmark.time_of_last_update >= time_threshold
            )
            .all()
        )
        return recent_bookmarks
    except SQLAlchemyError as e:
        logging.error(
            f"Can't get user's recent bookmarks for chat_id {chat_id}: {str(e)}"
        )
        return []


def set_user_inactive(db: Session, chat_id: int):
    try:
        # Find the user by chat ID and set them as inactive
        user = db.query(User).filter(User.chat_id == chat_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Can't put user inactive for chat_id {chat_id}: {str(e)}")
        return False


def remove_user(db: Session, chat_id: int):
    try:
        # Delete the user and related records from the database
        # This may involve deleting UserWebsite and Bookmark records first, depending on your cascading settings
        db.query(User).filter(User.chat_id == chat_id).delete()
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"Some problem's with deleting user for chat_id {chat_id}: {str(e)}"
        )
        return False


def get_user_by_chat_id(db: Session, chat_id: int):
    try:
        # Retrieve the user's information by chat ID
        user = db.query(User).filter(User.chat_id == chat_id).first()
        return user
    except SQLAlchemyError as e:
        logging.error(f"Can't get user by id for chat_id {chat_id}: {str(e)}")
        return None


def add_or_update_bookmarks(
    db: Session, chat_id: int, website_id: int, bookmarks_data: list
):
    try:
        # Retrieve the associated UserWebsite entry
        user_website = (
            db.query(UserWebsite)
            .filter_by(chat_id=chat_id, website_id=website_id)
            .first()
        )

        if not user_website:
            # If there isn't an association, it means there's something wrong
            logging.error(
                f"No association found for chat_id {chat_id} and website_id {website_id}"
            )
            return False

        for bookmark_data in bookmarks_data:
            # Check if the bookmark already exists
            bookmark = (
                db.query(Bookmark)
                .filter_by(
                    user_website_id=user_website.id, title=bookmark_data["title"]
                )
                .first()
            )

            if bookmark:
                # Update existing bookmark
                bookmark.image = bookmark_data["image"]
                bookmark.last_chapter_title = bookmark_data["last_chapter_title"]
                bookmark.time_of_last_update = bookmark_data["time_of_last_update"]
                bookmark.link_on_title = bookmark_data["link_on_title"]
                bookmark.link_on_last_chapter = bookmark_data["link_on_last_chapter"]
            else:
                # Add new bookmark
                new_bookmark = Bookmark(
                    user_website_id=user_website.id,
                    title=bookmark_data["title"],
                    image=bookmark_data["image"],
                    last_chapter_title=bookmark_data["last_chapter_title"],
                    time_of_last_update=bookmark_data["time_of_last_update"],
                    link_on_title=bookmark_data["link_on_title"],
                    link_on_last_chapter=bookmark_data["link_on_last_chapter"],
                )
                db.add(new_bookmark)

        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error updating bookmarks for chat_id {chat_id}: {str(e)}")
        return False


# Synchronization script to run at application startup
def synchronize_websites(db_session):
    try:
        for site in AVAILABLE_WEBSITES:
            existing_site = db_session.query(Website).filter_by(name=site["name"]).first()
            if not existing_site:
                # Site not in database, add it
                new_site = Website(name=site["name"], url=site["url"])
                db_session.add(new_site)
            else:
                existing_site.url = site["url"]
            db_session.commit()
            return True
    except SQLAlchemyError as e:
        db_session.rollback()
        logging.error(f"Error synchronizing websites: {str(e)}")
        return False

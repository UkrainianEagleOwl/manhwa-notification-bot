from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    chat_id = Column(Integer, primary_key=True)
    notification_time = Column(String)
    is_active = Column(Boolean)

    # Relationship to UserWebsite
    websites = relationship("UserWebsite", back_populates="user")

    def __repr__(self):
        return f"<User(chat_id={self.chat_id}, is_active={self.is_active})>"


class Website(Base):
    __tablename__ = "websites"

    website_id = Column(Integer, primary_key=True)
    website_link = Column(String, unique=True)

    # Relationship to UserWebsite
    users = relationship("UserWebsite", back_populates="website")

    def __repr__(self):
        return f"<Website(website_link={self.website_link})>"


class UserWebsite(Base):
    __tablename__ = "user_websites"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("users.chat_id"))
    website_id = Column(Integer, ForeignKey("websites.website_id"))
    login = Column(String)
    password = Column(String)

    # Relationships
    user = relationship("User", back_populates="websites")
    website = relationship("Website", back_populates="users")

    def __repr__(self):
        return f"<UserWebsite(chat_id={self.chat_id}, website_id={self.website_id})>"


class Bookmark(Base):
    __tablename__ = "bookmarks"

    bookmark_id = Column(Integer, primary_key=True)
    title = Column(String)
    image = Column(String)
    last_chapter_title = Column(String)
    time_of_last_update = Column(DateTime)
    link_on_title = Column(String)
    link_on_last_chapter = Column(String)
    user_website_id = Column(Integer, ForeignKey("user_websites.id"))

    # Relationship to UserWebsite
    user_website = relationship("UserWebsite")

    def __repr__(self):
        return f"<Bookmark(title={self.title}, last_chapter_title={self.last_chapter_title})>"


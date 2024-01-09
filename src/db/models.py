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
    notification_time = Column(
        String, nullable=True
    )  # Assuming it can be None if the user hasn't set it
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationship to UserWebsite with cascade delete
    websites = relationship(
        "UserWebsite", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(chat_id={self.chat_id}, is_active={self.is_active})>"


class Website(Base):
    __tablename__ = "websites"

    website_id = Column(Integer, primary_key=True)
    website_name = Column(String, unique=True)
    website_link = Column(String, unique=True)

    # Relationship to UserWebsite
    users = relationship("UserWebsite", back_populates="website")

    def __repr__(self):
        return f"<Website(website_link={self.website_link})>"


class UserWebsite(Base):
    __tablename__ = "user_websites"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("users.chat_id"), nullable=False)
    website_id = Column(Integer, ForeignKey("websites.website_id"), nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)

    # Relationships with cascade delete for bookmarks
    user = relationship("User", back_populates="websites")
    website = relationship("Website", back_populates="users")
    bookmarks = relationship("Bookmark", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserWebsite(chat_id={self.chat_id}, website_id={self.website_id})>"


class Bookmark(Base):
    __tablename__ = "bookmarks"

    bookmark_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)  # Must not be None
    image = Column(String, nullable=False)  # Must not be None
    last_chapter_title = Column(String, nullable=False)  # Must not be None
    time_of_last_update = Column(DateTime)  # Can be None
    link_on_title = Column(String, nullable=False)  # Must not be None
    link_on_last_chapter = Column(String, nullable=False)  # Must not be None
    user_website_id = Column(
        Integer, ForeignKey("user_websites.id"), nullable=False
    )  # Must not be None

    # Relationship to UserWebsite
    user_website = relationship("UserWebsite")

    def __repr__(self):
        return f"<Bookmark(title={self.title}, last_chapter_title={self.last_chapter_title})>"

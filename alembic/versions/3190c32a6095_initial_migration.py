"""Initial migration

Revision ID: 3190c32a6095
Revises: 
Create Date: 2024-01-06 18:12:52.316429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3190c32a6095'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('notification_time', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_table('websites',
    sa.Column('website_id', sa.Integer(), nullable=False),
    sa.Column('website_link', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('website_id'),
    sa.UniqueConstraint('website_link')
    )
    op.create_table('user_websites',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=True),
    sa.Column('website_id', sa.Integer(), nullable=True),
    sa.Column('login', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['users.chat_id'], ),
    sa.ForeignKeyConstraint(['website_id'], ['websites.website_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookmarks',
    sa.Column('bookmark_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('last_chapter_title', sa.String(), nullable=True),
    sa.Column('time_of_last_update', sa.DateTime(), nullable=True),
    sa.Column('link_on_title', sa.String(), nullable=True),
    sa.Column('link_on_last_chapter', sa.String(), nullable=True),
    sa.Column('user_website_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_website_id'], ['user_websites.id'], ),
    sa.PrimaryKeyConstraint('bookmark_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bookmarks')
    op.drop_table('user_websites')
    op.drop_table('websites')
    op.drop_table('users')
    # ### end Alembic commands ###

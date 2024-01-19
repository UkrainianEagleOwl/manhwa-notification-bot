"""'Update_user_model_for_save_last_time_data_base_update'

Revision ID: aae49a9e780b
Revises: 0d83a5e1865a
Create Date: 2024-01-19 10:09:41.975112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aae49a9e780b'
down_revision: Union[str, None] = '0d83a5e1865a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bookmarks', 'title',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('bookmarks', 'image',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('bookmarks', 'last_chapter_title',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('bookmarks', 'link_on_title',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('bookmarks', 'link_on_last_chapter',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('bookmarks', 'user_website_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('user_websites', 'chat_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('user_websites', 'website_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('user_websites', 'login',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('user_websites', 'password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.add_column('users', sa.Column('last_update', sa.DateTime(), nullable=True))
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.add_column('websites', sa.Column('website_name', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'websites', ['website_name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'websites', type_='unique')
    op.drop_column('websites', 'website_name')
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.drop_column('users', 'last_update')
    op.alter_column('user_websites', 'password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('user_websites', 'login',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('user_websites', 'website_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('user_websites', 'chat_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('bookmarks', 'user_website_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('bookmarks', 'link_on_last_chapter',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('bookmarks', 'link_on_title',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('bookmarks', 'last_chapter_title',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('bookmarks', 'image',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('bookmarks', 'title',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###

"""Update website tabel

Revision ID: 0d83a5e1865a
Revises: 170da422f56c
Create Date: 2024-01-09 14:12:52.172643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d83a5e1865a'
down_revision: Union[str, None] = '170da422f56c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

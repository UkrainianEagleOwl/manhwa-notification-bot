"""Upgrade models with nullable features and cascade delete

Revision ID: 170da422f56c
Revises: 3190c32a6095
Create Date: 2024-01-06 23:12:15.472196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '170da422f56c'
down_revision: Union[str, None] = '3190c32a6095'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

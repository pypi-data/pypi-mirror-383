"""base schema

Revision ID: 3c3445a58565
Revises:
Create Date: 2025-08-20 14:25:40.121999

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "3c3445a58565"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

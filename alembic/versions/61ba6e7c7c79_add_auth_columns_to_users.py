from alembic import op
import sqlalchemy as sa

revision = '61ba6e7c7c79'
down_revision = '0002_sport_tables'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))
    op.add_column('users', sa.Column('role', sa.String(50), nullable=False, server_default='REFEREE'))


def downgrade():
    op.drop_column('users', 'role')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'is_active')
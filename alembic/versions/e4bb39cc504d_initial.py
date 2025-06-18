"""Initial tables creation

Revision ID: 001
Revises: 
Create Date: 2025-06-17 21:38:32.265166

"""
from alembic import op
import sqlalchemy as sa


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('locations',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('icon', sa.String(), nullable=False),
    sa.Column('tags', sa.String(), nullable=True),
    sa.Column('attrs', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sorters',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('icon', sa.String(), nullable=False),
    sa.Column('tags', sa.String(), nullable=True),
    sa.Column('attrs', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['location'], ['locations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parts',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('sorter', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('image', sa.LargeBinary(), nullable=True),
    sa.Column('image_hash', sa.LargeBinary(), nullable=True),
    sa.Column('tags', sa.String(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('quantity_type', sa.String(), nullable=False),
    sa.Column('enable_quantity', sa.Boolean(), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('attrs', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['location'], ['locations.id'], ),
    sa.ForeignKeyConstraint(['sorter'], ['sorters.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('parts')
    op.drop_table('sorters')
    op.drop_table('locations')
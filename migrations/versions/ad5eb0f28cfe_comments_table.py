"""comments table

Revision ID: ad5eb0f28cfe
Revises: 3c8d5f80ce97
Create Date: 2021-02-21 16:34:13.470496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad5eb0f28cfe'
down_revision = '3c8d5f80ce97'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=64), nullable=True),
    sa.Column('content', sa.String(length=140), nullable=True),
    sa.Column('publication_datetime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_publication_datetime'), 'comments', ['publication_datetime'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comments_publication_datetime'), table_name='comments')
    op.drop_table('comments')
    # ### end Alembic commands ###
"""Simplify model by removing classes

Revision ID: simplify_model
Revises: 
Create Date: 2023-03-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'simplify_model'
down_revision = None  # Replace with the actual previous revision ID
branch_labels = None
depends_on = None


def upgrade():
    # 1. Remove foreign key constraints
    op.drop_constraint('assignments_class_id_fkey', 'assignments', type_='foreignkey')
    
    # 2. Drop column from assignments
    op.drop_column('assignments', 'class_id')
    
    # 3. Drop class_videos table
    op.drop_table('class_videos')
    
    # 4. Drop student_class association table
    op.drop_table('student_class')
    
    # 5. Drop classes table
    op.drop_table('classes')


def downgrade():
    # This is a complex migration to revert, as we're removing tables
    # For a complete downgrade, we would need to:
    # 1. Recreate the classes table
    op.create_table('classes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 2. Recreate the student_class table
    op.create_table('student_class',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('student_id', 'class_id')
    )
    
    # 3. Recreate the class_videos table
    op.create_table('class_videos',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 4. Add class_id back to assignments
    op.add_column('assignments', sa.Column('class_id', sa.Integer(), nullable=True))
    
    # 5. Add foreign key constraint
    op.create_foreign_key('assignments_class_id_fkey', 'assignments', 'classes', ['class_id'], ['id']) 
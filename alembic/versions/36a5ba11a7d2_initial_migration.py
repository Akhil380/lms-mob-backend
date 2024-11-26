"""Initial migration

Revision ID: 36a5ba11a7d2
Revises: 
Create Date: 2024-11-21 23:40:09.938591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '36a5ba11a7d2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_question_set_types_id', table_name='question_set_types')
    op.drop_index('ix_question_set_types_name', table_name='question_set_types')
    op.drop_table('question_set_types')
    op.drop_index('ix_otps_id', table_name='otps')
    op.drop_table('otps')
    op.drop_index('ix_questions_id', table_name='questions')
    op.drop_table('questions')
    op.drop_index('ix_test_results_id', table_name='test_results')
    op.drop_table('test_results')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_mobile', table_name='users')
    op.drop_index('ix_users_name', table_name='users')
    op.drop_table('users')
    op.drop_table('user_question_set_association')
    op.drop_index('ix_exam_masters_id', table_name='exam_masters')
    op.drop_table('exam_masters')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exam_masters',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('exam_masters_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='exam_masters_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_exam_masters_id', 'exam_masters', ['id'], unique=False)
    op.create_table('user_question_set_association',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('question_set_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['question_set_id'], ['question_set_types.id'], name='user_question_set_association_question_set_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_question_set_association_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'question_set_id', name='user_question_set_association_pkey')
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('mobile', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('registered_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_users_name', 'users', ['name'], unique=False)
    op.create_index('ix_users_mobile', 'users', ['mobile'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_table('test_results',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('question_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('test_no', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_selected_answer', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('correct_option', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('is_attended', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('is_user_answer_true', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], name='test_results_question_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='test_results_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='test_results_pkey')
    )
    op.create_index('ix_test_results_id', 'test_results', ['id'], unique=False)
    op.create_table('questions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('option_a', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('option_b', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('option_c', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('option_d', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('correct_option', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('test_no', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('test_time', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('test_availability', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('exam_master_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['exam_master_id'], ['exam_masters.id'], name='questions_exam_master_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='questions_pkey')
    )
    op.create_index('ix_questions_id', 'questions', ['id'], unique=False)
    op.create_table('otps',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('otp_code', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('expires_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('is_verified', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='otps_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='otps_pkey')
    )
    op.create_index('ix_otps_id', 'otps', ['id'], unique=False)
    op.create_table('question_set_types',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='question_set_types_pkey')
    )
    op.create_index('ix_question_set_types_name', 'question_set_types', ['name'], unique=True)
    op.create_index('ix_question_set_types_id', 'question_set_types', ['id'], unique=False)
    # ### end Alembic commands ###

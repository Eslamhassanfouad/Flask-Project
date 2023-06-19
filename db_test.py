from flasktasks import db, app

from flasktasks.models import User, Post
import sys

from sqlalchemy import text

def create_db():
    with app.app_context():
        # you will have instance folder with site.db inside
        db.create_all()

def drop_migration_history_table():
       with app.app_context():
        # execute SQL statement to drop migration history table
        conn = db.engine.connect()
        stmt = text("DROP TABLE alembic_version;")
        conn.execute(stmt)    
        
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'drop_migration_history_table':
        drop_migration_history_table()
        print("Database created successfully!")
    else:
        print("Invalid command. Please use 'python db_test.py create_db' to create the database.")     
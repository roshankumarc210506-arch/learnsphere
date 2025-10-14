"""
Database reset utility for LearnSphere
Drops all tables and recreates them with fresh data
"""

from app import app, db
from init_db import init_database
import sys

def reset_database():
    """Drop all tables and reinitialize database"""
    
    print("\n" + "="*60)
    print("⚠️  WARNING: Database Reset")
    print("="*60)
    print("\nThis will DELETE ALL DATA in the database!")
    print("This action cannot be undone.\n")
    
    confirmation = input("Type 'YES' to confirm: ")
    
    if confirmation != 'YES':
        print("\n❌ Reset cancelled.")
        sys.exit(0)
    
    with app.app_context():
        print("\n🗑️  Dropping all tables...")
        db.drop_all()
        print("✓ All tables dropped")
        
        print("\n🔄 Reinitializing database...")
        init_database()
        
        print("\n✅ Database has been reset successfully!")


if __name__ == '__main__':
    reset_database()
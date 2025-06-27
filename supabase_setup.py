"""
Supabase setup script for Xeinst AI Lead Scraper
"""

import os
import sys
from sqlalchemy import text
from database import create_database_manager, Base
from utils import logger

def setup_supabase_database():
    """Setup Supabase database with required tables"""
    try:
        print("🚀 Setting up Supabase database...")
        
        # Check if Supabase environment variables are set
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_db_password = os.getenv('SUPABASE_DB_PASSWORD')
        
        if not supabase_url or not supabase_db_password:
            print("❌ Supabase environment variables not found!")
            print("Please set the following environment variables:")
            print("  - SUPABASE_URL")
            print("  - SUPABASE_DB_PASSWORD")
            print("\nYou can copy env_example.txt to .env and fill in your values.")
            return False
        
        # Create database manager
        db_manager = create_database_manager()
        
        # Test connection
        print("🔗 Testing database connection...")
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        # Create tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=db_manager.engine)
        print("✅ Tables created successfully!")
        
        # Create indexes for better performance
        print("🔍 Creating database indexes...")
        with db_manager.get_session() as session:
            # These indexes should already be created by SQLAlchemy, but let's verify
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_leads_fit_score ON leads (fit_score);
                CREATE INDEX IF NOT EXISTS idx_leads_industry ON leads (industry);
                CREATE INDEX IF NOT EXISTS idx_leads_status ON leads (status);
                CREATE INDEX IF NOT EXISTS idx_leads_data_source ON leads (data_source);
            """))
            session.commit()
        print("✅ Indexes created successfully!")
        
        # Test basic operations
        print("🧪 Testing basic database operations...")
        
        # Test insert
        test_lead = {
            'name': 'Test Company',
            'industry': 'Technology',
            'website': 'https://test-company.com',
            'fit_score': 8.5,
            'data_source': 'Test',
            'status': 'new'
        }
        
        lead = db_manager.add_lead(test_lead)
        if lead:
            print("✅ Insert test passed")
            
            # Test update
            success = db_manager.update_lead(lead.id, {'status': 'contacted'})
            if success:
                print("✅ Update test passed")
            
            # Test delete
            success = db_manager.delete_lead(lead.id)
            if success:
                print("✅ Delete test passed")
        else:
            print("❌ Insert test failed")
            return False
        
        print("\n🎉 Supabase database setup completed successfully!")
        print("\n📊 You can now:")
        print("  - Run the scraper: python main.py")
        print("  - Manage leads: python database_cli.py")
        print("  - View statistics: python database_cli.py stats")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        logger.error(f"Supabase setup error: {str(e)}")
        return False

def check_supabase_connection():
    """Check if Supabase connection is working"""
    try:
        db_manager = create_database_manager()
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT COUNT(*) FROM leads"))
            count = result.fetchone()[0]
            print(f"✅ Supabase connection working! Current leads: {count}")
            return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🗄️  Xeinst AI Lead Scraper - Supabase Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_supabase_connection()
        return
    
    success = setup_supabase_database()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the scraper: python main.py")
        print("2. Check database: python supabase_setup.py check")
        print("3. Manage leads: python database_cli.py stats")
    else:
        print("\n❌ Setup failed. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
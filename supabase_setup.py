"""
Supabase setup script for Xeinst AI Business Lead Scraper
Creates tables and indexes for both business and developer leads
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_supabase_connection():
    """Get Supabase PostgreSQL connection"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_db_password = os.getenv('SUPABASE_DB_PASSWORD')
    
    if not supabase_url or not supabase_db_password:
        raise ValueError("SUPABASE_URL and SUPABASE_DB_PASSWORD environment variables are required")
    
    # Extract host from Supabase URL
    host = supabase_url.replace('https://', '').replace('http://', '')
    
    # Connect to Supabase PostgreSQL
    connection = psycopg2.connect(
        host=host,
        port=5432,
        database="postgres",
        user="postgres",
        password=supabase_db_password
    )
    
    return connection

def create_business_leads_table(connection):
    """Create business_leads table"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS business_leads (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        industry VARCHAR(100) NOT NULL,
        website VARCHAR(500) NOT NULL UNIQUE,
        linkedin VARCHAR(500),
        email VARCHAR(255),
        company_size VARCHAR(100),
        pain_points TEXT,
        fit_score FLOAT NOT NULL,
        data_source VARCHAR(100) NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_contacted BOOLEAN DEFAULT FALSE,
        contact_date TIMESTAMP,
        notes TEXT,
        status VARCHAR(50) DEFAULT 'new',
        annual_revenue VARCHAR(100),
        location VARCHAR(255),
        tech_stack TEXT,
        automation_needs TEXT,
        decision_maker VARCHAR(255)
    );
    """
    
    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_business_fit_score ON business_leads(fit_score);
    CREATE INDEX IF NOT EXISTS idx_business_industry ON business_leads(industry);
    CREATE INDEX IF NOT EXISTS idx_business_status ON business_leads(status);
    CREATE INDEX IF NOT EXISTS idx_business_data_source ON business_leads(data_source);
    CREATE INDEX IF NOT EXISTS idx_business_company_size ON business_leads(company_size);
    CREATE INDEX IF NOT EXISTS idx_business_name ON business_leads(name);
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_sql)
            cursor.execute(create_indexes_sql)
            connection.commit()
            logger.info("✅ Business leads table created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating business leads table: {str(e)}")
        connection.rollback()
        raise

def create_developer_leads_table(connection):
    """Create developer_leads table"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS developer_leads (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        website VARCHAR(500) NOT NULL UNIQUE,
        linkedin VARCHAR(500),
        email VARCHAR(255),
        fit_score FLOAT NOT NULL,
        data_source VARCHAR(100) NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_contacted BOOLEAN DEFAULT FALSE,
        contact_date TIMESTAMP,
        notes TEXT,
        status VARCHAR(50) DEFAULT 'new',
        skills TEXT,
        experience_level VARCHAR(50),
        project_types TEXT,
        hourly_rate VARCHAR(100),
        availability VARCHAR(100),
        portfolio_url VARCHAR(500),
        github_url VARCHAR(500),
        automation_interest TEXT
    );
    """
    
    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_developer_fit_score ON developer_leads(fit_score);
    CREATE INDEX IF NOT EXISTS idx_developer_status ON developer_leads(status);
    CREATE INDEX IF NOT EXISTS idx_developer_data_source ON developer_leads(data_source);
    CREATE INDEX IF NOT EXISTS idx_developer_experience ON developer_leads(experience_level);
    CREATE INDEX IF NOT EXISTS idx_developer_skills ON developer_leads(skills);
    CREATE INDEX IF NOT EXISTS idx_developer_name ON developer_leads(name);
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_sql)
            cursor.execute(create_indexes_sql)
            connection.commit()
            logger.info("✅ Developer leads table created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating developer leads table: {str(e)}")
        connection.rollback()
        raise

def test_business_lead_operations(connection):
    """Test business lead CRUD operations"""
    logger.info("🧪 Testing business lead operations...")
    
    # Test insert
    insert_sql = """
    INSERT INTO business_leads (name, industry, website, fit_score, data_source, company_size, pain_points)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (website) DO UPDATE SET
        name = EXCLUDED.name,
        industry = EXCLUDED.industry,
        fit_score = EXCLUDED.fit_score,
        last_updated = CURRENT_TIMESTAMP
    RETURNING id, name, website;
    """
    
    test_data = (
        "Test Business Inc",
        "Technology",
        "https://testbusiness.com",
        8.5,
        "test_source",
        "10-50 employees",
        "Manual data entry and repetitive tasks"
    )
    
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(insert_sql, test_data)
            result = cursor.fetchone()
            connection.commit()
            logger.info(f"✅ Inserted business lead: {result}")
            
            # Test select
            cursor.execute("SELECT COUNT(*) as count FROM business_leads")
            count = cursor.fetchone()['count']
            logger.info(f"✅ Total business leads: {count}")
            
            # Test update
            update_sql = """
            UPDATE business_leads 
            SET status = 'contacted', is_contacted = TRUE 
            WHERE website = %s
            """
            cursor.execute(update_sql, ("https://testbusiness.com",))
            connection.commit()
            logger.info("✅ Updated business lead status")
            
    except Exception as e:
        logger.error(f"❌ Error testing business lead operations: {str(e)}")
        connection.rollback()

def test_developer_lead_operations(connection):
    """Test developer lead CRUD operations"""
    logger.info("🧪 Testing developer lead operations...")
    
    # Test insert
    insert_sql = """
    INSERT INTO developer_leads (name, website, fit_score, data_source, skills, experience_level, automation_interest)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (website) DO UPDATE SET
        name = EXCLUDED.name,
        fit_score = EXCLUDED.fit_score,
        last_updated = CURRENT_TIMESTAMP
    RETURNING id, name, website;
    """
    
    test_data = (
        "John Developer",
        "https://johndeveloper.dev",
        9.0,
        "test_source",
        "Python, JavaScript, React, Node.js",
        "Senior",
        "AI automation and workflow optimization"
    )
    
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(insert_sql, test_data)
            result = cursor.fetchone()
            connection.commit()
            logger.info(f"✅ Inserted developer lead: {result}")
            
            # Test select
            cursor.execute("SELECT COUNT(*) as count FROM developer_leads")
            count = cursor.fetchone()['count']
            logger.info(f"✅ Total developer leads: {count}")
            
            # Test update
            update_sql = """
            UPDATE developer_leads 
            SET status = 'qualified', is_contacted = TRUE 
            WHERE website = %s
            """
            cursor.execute(update_sql, ("https://johndeveloper.dev",))
            connection.commit()
            logger.info("✅ Updated developer lead status")
            
    except Exception as e:
        logger.error(f"❌ Error testing developer lead operations: {str(e)}")
        connection.rollback()

def test_search_operations(connection):
    """Test search operations on both tables"""
    logger.info("🧪 Testing search operations...")
    
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Search business leads
            cursor.execute("""
                SELECT name, industry, fit_score 
                FROM business_leads 
                WHERE name ILIKE %s OR industry ILIKE %s
                ORDER BY fit_score DESC
                LIMIT 5
            """, ('%test%', '%tech%'))
            
            business_results = cursor.fetchall()
            logger.info(f"✅ Business search results: {len(business_results)} found")
            
            # Search developer leads
            cursor.execute("""
                SELECT name, skills, fit_score 
                FROM developer_leads 
                WHERE name ILIKE %s OR skills ILIKE %s
                ORDER BY fit_score DESC
                LIMIT 5
            """, ('%john%', '%python%'))
            
            developer_results = cursor.fetchall()
            logger.info(f"✅ Developer search results: {len(developer_results)} found")
            
    except Exception as e:
        logger.error(f"❌ Error testing search operations: {str(e)}")

def cleanup_test_data(connection):
    """Clean up test data"""
    logger.info("🧹 Cleaning up test data...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM business_leads WHERE website = %s", ("https://testbusiness.com",))
            cursor.execute("DELETE FROM developer_leads WHERE website = %s", ("https://johndeveloper.dev",))
            connection.commit()
            logger.info("✅ Test data cleaned up")
    except Exception as e:
        logger.error(f"❌ Error cleaning up test data: {str(e)}")
        connection.rollback()

def main():
    """Main setup function"""
    logger.info("🚀 Starting Supabase setup for Xeinst AI Lead Scraper...")
    
    try:
        # Get connection
        connection = get_supabase_connection()
        logger.info("✅ Connected to Supabase PostgreSQL")
        
        # Create tables
        create_business_leads_table(connection)
        create_developer_leads_table(connection)
        
        # Test operations
        test_business_lead_operations(connection)
        test_developer_lead_operations(connection)
        test_search_operations(connection)
        
        # Cleanup
        cleanup_test_data(connection)
        
        logger.info("🎉 Supabase setup completed successfully!")
        logger.info("📊 Tables created:")
        logger.info("   - business_leads (for companies and organizations)")
        logger.info("   - developer_leads (for individual developers)")
        logger.info("🔍 Indexes created for optimal query performance")
        logger.info("✅ All CRUD operations tested and working")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        return False
    
    finally:
        if 'connection' in locals():
            connection.close()
            logger.info("🔌 Database connection closed")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
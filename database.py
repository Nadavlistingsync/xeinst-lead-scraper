"""
Database module for Xeinst AI Business Lead Scraper
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class Lead(Base):
    """Lead model for storing scraped business leads"""
    
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    website = Column(String(500), nullable=False, unique=True)
    linkedin = Column(String(500))
    email = Column(String(255))
    company_size = Column(String(100))
    pain_points = Column(Text)
    fit_score = Column(Float, nullable=False, index=True)
    data_source = Column(String(100), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_contacted = Column(Boolean, default=False)
    contact_date = Column(DateTime)
    notes = Column(Text)
    status = Column(String(50), default='new')  # new, contacted, qualified, converted, rejected
    
    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_fit_score', 'fit_score'),
        Index('idx_industry', 'industry'),
        Index('idx_status', 'status'),
        Index('idx_data_source', 'data_source'),
    )

class DatabaseManager:
    """Database manager for handling all database operations"""
    
    def __init__(self, database_url: str = None):
        """Initialize database connection"""
        if database_url:
            self.database_url = database_url
        else:
            # Default to SQLite for local development, but prefer Supabase
            self.database_url = self._get_database_url()
        
        self.engine = None
        self.SessionLocal = None
        self.setup_database()
    
    def _get_database_url(self) -> str:
        """Get database URL with Supabase support"""
        # Check for Supabase environment variables first
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        supabase_db_password = os.getenv('SUPABASE_DB_PASSWORD')
        
        if supabase_url and supabase_db_password:
            # Construct Supabase PostgreSQL URL
            # Format: postgresql://postgres:[password]@[host]:[port]/postgres
            host = supabase_url.replace('https://', '').replace('http://', '')
            return f"postgresql://postgres:{supabase_db_password}@{host}:5432/postgres"
        
        # Fallback to direct DATABASE_URL
        return os.getenv('DATABASE_URL', 'sqlite:///xeinst_leads.db')
    
    def setup_database(self):
        """Setup database engine and session"""
        try:
            # Configure engine based on database type
            if 'postgresql' in self.database_url:
                # PostgreSQL/Supabase configuration
                self.engine = create_engine(
                    self.database_url,
                    echo=False,  # Set to True for SQL debugging
                    pool_pre_ping=True,
                    pool_recycle=300,
                    pool_size=10,
                    max_overflow=20
                )
            else:
                # SQLite configuration
                self.engine = create_engine(
                    self.database_url,
                    echo=False,
                    pool_pre_ping=True
                )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"Database setup complete: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def add_lead(self, lead_data: Dict[str, Any]) -> Optional[Lead]:
        """Add a new lead to the database"""
        try:
            with self.get_session() as session:
                # Check if lead already exists by website
                existing_lead = session.query(Lead).filter(
                    Lead.website == lead_data['website']
                ).first()
                
                if existing_lead:
                    # Update existing lead
                    for key, value in lead_data.items():
                        if hasattr(existing_lead, key):
                            setattr(existing_lead, key, value)
                    existing_lead.last_updated = datetime.utcnow()
                    session.commit()
                    logger.info(f"Updated existing lead: {lead_data['name']}")
                    return existing_lead
                
                # Create new lead
                lead = Lead(**lead_data)
                session.add(lead)
                session.commit()
                session.refresh(lead)
                logger.info(f"Added new lead: {lead_data['name']}")
                return lead
                
        except SQLAlchemyError as e:
            logger.error(f"Database error adding lead: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error adding lead: {str(e)}")
            return None
    
    def add_leads_batch(self, leads_data: List[Dict[str, Any]]) -> int:
        """Add multiple leads to the database"""
        added_count = 0
        try:
            with self.get_session() as session:
                for lead_data in leads_data:
                    # Check if lead already exists
                    existing_lead = session.query(Lead).filter(
                        Lead.website == lead_data['website']
                    ).first()
                    
                    if existing_lead:
                        # Update existing lead
                        for key, value in lead_data.items():
                            if hasattr(existing_lead, key):
                                setattr(existing_lead, key, value)
                        existing_lead.last_updated = datetime.utcnow()
                    else:
                        # Create new lead
                        lead = Lead(**lead_data)
                        session.add(lead)
                        added_count += 1
                
                session.commit()
                logger.info(f"Batch operation complete: {added_count} new leads added")
                return added_count
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in batch operation: {str(e)}")
            return 0
        except Exception as e:
            logger.error(f"Error in batch operation: {str(e)}")
            return 0
    
    def get_leads(self, 
                  limit: int = 100, 
                  offset: int = 0,
                  min_score: float = None,
                  industry: str = None,
                  status: str = None,
                  data_source: str = None) -> List[Lead]:
        """Get leads with optional filters"""
        try:
            with self.get_session() as session:
                query = session.query(Lead)
                
                if min_score is not None:
                    query = query.filter(Lead.fit_score >= min_score)
                
                if industry:
                    query = query.filter(Lead.industry.ilike(f'%{industry}%'))
                
                if status:
                    query = query.filter(Lead.status == status)
                
                if data_source:
                    query = query.filter(Lead.data_source == data_source)
                
                leads = query.order_by(Lead.fit_score.desc()).offset(offset).limit(limit).all()
                return leads
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting leads: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting leads: {str(e)}")
            return []
    
    def get_lead_by_id(self, lead_id: int) -> Optional[Lead]:
        """Get lead by ID"""
        try:
            with self.get_session() as session:
                return session.query(Lead).filter(Lead.id == lead_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting lead by ID: {str(e)}")
            return None
    
    def get_lead_by_website(self, website: str) -> Optional[Lead]:
        """Get lead by website"""
        try:
            with self.get_session() as session:
                return session.query(Lead).filter(Lead.website == website).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting lead by website: {str(e)}")
            return None
    
    def update_lead(self, lead_id: int, update_data: Dict[str, Any]) -> bool:
        """Update lead by ID"""
        try:
            with self.get_session() as session:
                lead = session.query(Lead).filter(Lead.id == lead_id).first()
                if not lead:
                    return False
                
                for key, value in update_data.items():
                    if hasattr(lead, key):
                        setattr(lead, key, value)
                
                lead.last_updated = datetime.utcnow()
                session.commit()
                logger.info(f"Updated lead ID {lead_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Database error updating lead: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating lead: {str(e)}")
            return False
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete lead by ID"""
        try:
            with self.get_session() as session:
                lead = session.query(Lead).filter(Lead.id == lead_id).first()
                if not lead:
                    return False
                
                session.delete(lead)
                session.commit()
                logger.info(f"Deleted lead ID {lead_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting lead: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error deleting lead: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_session() as session:
                total_leads = session.query(Lead).count()
                high_score_leads = session.query(Lead).filter(Lead.fit_score >= 8.0).count()
                contacted_leads = session.query(Lead).filter(Lead.is_contacted == True).count()
                
                # Industry distribution
                industry_stats = session.query(
                    Lead.industry,
                    session.query(Lead).filter(Lead.industry == Lead.industry).count().label('count')
                ).group_by(Lead.industry).all()
                
                # Status distribution
                status_stats = session.query(
                    Lead.status,
                    session.query(Lead).filter(Lead.status == Lead.status).count().label('count')
                ).group_by(Lead.status).all()
                
                return {
                    'total_leads': total_leads,
                    'high_score_leads': high_score_leads,
                    'contacted_leads': contacted_leads,
                    'industry_distribution': {row.industry: row.count for row in industry_stats},
                    'status_distribution': {row.status: row.count for row in status_stats}
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting statistics: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def search_leads(self, search_term: str, limit: int = 50) -> List[Lead]:
        """Search leads by name, industry, or pain points"""
        try:
            with self.get_session() as session:
                search_filter = f'%{search_term}%'
                leads = session.query(Lead).filter(
                    (Lead.name.ilike(search_filter)) |
                    (Lead.industry.ilike(search_filter)) |
                    (Lead.pain_points.ilike(search_filter))
                ).order_by(Lead.fit_score.desc()).limit(limit).all()
                
                return leads
                
        except SQLAlchemyError as e:
            logger.error(f"Database error searching leads: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error searching leads: {str(e)}")
            return []
    
    def export_leads_to_dict(self, leads: List[Lead]) -> List[Dict[str, Any]]:
        """Convert Lead objects to dictionaries for export"""
        return [
            {
                'id': lead.id,
                'name': lead.name,
                'industry': lead.industry,
                'website': lead.website,
                'linkedin': lead.linkedin,
                'email': lead.email,
                'company_size': lead.company_size,
                'pain_points': lead.pain_points,
                'fit_score': lead.fit_score,
                'data_source': lead.data_source,
                'last_updated': lead.last_updated.isoformat() if lead.last_updated else None,
                'is_contacted': lead.is_contacted,
                'contact_date': lead.contact_date.isoformat() if lead.contact_date else None,
                'notes': lead.notes,
                'status': lead.status
            }
            for lead in leads
        ]

# Database configuration
def get_database_url() -> str:
    """Get database URL from environment or use default"""
    # Check for Supabase environment variables first
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_db_password = os.getenv('SUPABASE_DB_PASSWORD')
    
    if supabase_url and supabase_db_password:
        # Construct Supabase PostgreSQL URL
        host = supabase_url.replace('https://', '').replace('http://', '')
        return f"postgresql://postgres:{supabase_db_password}@{host}:5432/postgres"
    
    # Fallback to direct DATABASE_URL
    return os.getenv('DATABASE_URL', 'sqlite:///xeinst_leads.db')

def create_database_manager() -> DatabaseManager:
    """Create and return database manager instance"""
    database_url = get_database_url()
    return DatabaseManager(database_url) 
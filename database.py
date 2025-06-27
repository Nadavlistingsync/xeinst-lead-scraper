"""
Database module for Xeinst AI Business Lead Scraper
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging
import enum

logger = logging.getLogger(__name__)

Base = declarative_base()

class LeadType(enum.Enum):
    """Lead type enumeration"""
    BUSINESS = "business"
    DEVELOPER = "developer"

class BusinessLead(Base):
    """Business lead model for companies and organizations"""
    
    __tablename__ = 'business_leads'
    
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
    
    # Business-specific fields
    annual_revenue = Column(String(100))
    location = Column(String(255))
    tech_stack = Column(Text)
    automation_needs = Column(Text)
    decision_maker = Column(String(255))
    
    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_business_fit_score', 'fit_score'),
        Index('idx_business_industry', 'industry'),
        Index('idx_business_status', 'status'),
        Index('idx_business_data_source', 'data_source'),
        Index('idx_business_company_size', 'company_size'),
    )

class DeveloperLead(Base):
    """Developer lead model for individual developers and freelancers"""
    
    __tablename__ = 'developer_leads'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    website = Column(String(500), nullable=False, unique=True)
    linkedin = Column(String(500))
    email = Column(String(255))
    fit_score = Column(Float, nullable=False, index=True)
    data_source = Column(String(100), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_contacted = Column(Boolean, default=False)
    contact_date = Column(DateTime)
    notes = Column(Text)
    status = Column(String(50), default='new')
    
    # Developer-specific fields
    skills = Column(Text)  # Programming languages, frameworks
    experience_level = Column(String(50))  # Junior, Mid, Senior, Expert
    project_types = Column(Text)  # Web apps, mobile, AI, etc.
    hourly_rate = Column(String(100))
    availability = Column(String(100))  # Full-time, part-time, contract
    portfolio_url = Column(String(500))
    github_url = Column(String(500))
    automation_interest = Column(Text)  # Specific automation needs
    
    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_developer_fit_score', 'fit_score'),
        Index('idx_developer_status', 'status'),
        Index('idx_developer_data_source', 'data_source'),
        Index('idx_developer_experience', 'experience_level'),
        Index('idx_developer_skills', 'skills'),
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
    
    def classify_lead_type(self, lead_data: Dict[str, Any]) -> LeadType:
        """Classify lead as business or developer based on data"""
        name = lead_data.get('name', '').lower()
        industry = lead_data.get('industry', '').lower()
        pain_points = lead_data.get('pain_points', '').lower()
        company_size = lead_data.get('company_size', '').lower()
        
        # Developer indicators
        dev_keywords = [
            'developer', 'programmer', 'coder', 'freelancer', 'consultant',
            'full-stack', 'frontend', 'backend', 'react', 'python', 'javascript',
            'node.js', 'vue', 'angular', 'php', 'java', 'c#', 'ruby', 'go',
            'mobile developer', 'ios', 'android', 'flutter', 'react native'
        ]
        
        # Check if lead is likely a developer
        for keyword in dev_keywords:
            if keyword in name or keyword in industry or keyword in pain_points:
                return LeadType.DEVELOPER
        
        # Check company size indicators
        if any(size in company_size for size in ['solo', 'individual', '1', 'freelancer']):
            # Could be either, check for more developer indicators
            if any(keyword in pain_points for keyword in ['code', 'development', 'programming']):
                return LeadType.DEVELOPER
        
        # Default to business
        return LeadType.BUSINESS
    
    def add_lead(self, lead_data: Dict[str, Any]) -> Optional[Any]:
        """Add a new lead to the appropriate table"""
        try:
            lead_type = self.classify_lead_type(lead_data)
            
            with self.get_session() as session:
                if lead_type == LeadType.BUSINESS:
                    return self._add_business_lead(session, lead_data)
                else:
                    return self._add_developer_lead(session, lead_data)
                
        except Exception as e:
            logger.error(f"Error adding lead: {str(e)}")
            return None
    
    def _add_business_lead(self, session: Session, lead_data: Dict[str, Any]) -> Optional[BusinessLead]:
        """Add business lead to database"""
        # Check if lead already exists by website
        existing_lead = session.query(BusinessLead).filter(
            BusinessLead.website == lead_data['website']
        ).first()
        
        if existing_lead:
            # Update existing lead
            for key, value in lead_data.items():
                if hasattr(existing_lead, key):
                    setattr(existing_lead, key, value)
            existing_lead.last_updated = datetime.utcnow()
            session.commit()
            logger.info(f"Updated existing business lead: {lead_data['name']}")
            return existing_lead
        
        # Create new business lead
        business_lead = BusinessLead(**lead_data)
        session.add(business_lead)
        session.commit()
        session.refresh(business_lead)
        logger.info(f"Added new business lead: {lead_data['name']}")
        return business_lead
    
    def _add_developer_lead(self, session: Session, lead_data: Dict[str, Any]) -> Optional[DeveloperLead]:
        """Add developer lead to database"""
        # Check if lead already exists by website
        existing_lead = session.query(DeveloperLead).filter(
            DeveloperLead.website == lead_data['website']
        ).first()
        
        if existing_lead:
            # Update existing lead
            for key, value in lead_data.items():
                if hasattr(existing_lead, key):
                    setattr(existing_lead, key, value)
            existing_lead.last_updated = datetime.utcnow()
            session.commit()
            logger.info(f"Updated existing developer lead: {lead_data['name']}")
            return existing_lead
        
        # Create new developer lead
        developer_lead = DeveloperLead(**lead_data)
        session.add(developer_lead)
        session.commit()
        session.refresh(developer_lead)
        logger.info(f"Added new developer lead: {lead_data['name']}")
        return developer_lead
    
    def add_leads_batch(self, leads_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Add multiple leads to the appropriate tables"""
        business_count = 0
        developer_count = 0
        
        try:
            with self.get_session() as session:
                for lead_data in leads_data:
                    lead_type = self.classify_lead_type(lead_data)
                    
                    if lead_type == LeadType.BUSINESS:
                        if self._add_business_lead(session, lead_data):
                            business_count += 1
                    else:
                        if self._add_developer_lead(session, lead_data):
                            developer_count += 1
                
                session.commit()
                logger.info(f"Batch operation complete: {business_count} business leads, {developer_count} developer leads added")
                return {"business": business_count, "developer": developer_count}
                
        except Exception as e:
            logger.error(f"Error in batch operation: {str(e)}")
            return {"business": 0, "developer": 0}
    
    def get_business_leads(self, 
                          limit: int = 100, 
                          offset: int = 0,
                          min_score: float = None,
                          industry: str = None,
                          status: str = None,
                          data_source: str = None) -> List[BusinessLead]:
        """Get business leads with optional filters"""
        try:
            with self.get_session() as session:
                query = session.query(BusinessLead)
                
                if min_score is not None:
                    query = query.filter(BusinessLead.fit_score >= min_score)
                
                if industry:
                    query = query.filter(BusinessLead.industry.ilike(f'%{industry}%'))
                
                if status:
                    query = query.filter(BusinessLead.status == status)
                
                if data_source:
                    query = query.filter(BusinessLead.data_source == data_source)
                
                leads = query.order_by(BusinessLead.fit_score.desc()).offset(offset).limit(limit).all()
                return leads
                
        except Exception as e:
            logger.error(f"Error getting business leads: {str(e)}")
            return []
    
    def get_developer_leads(self, 
                           limit: int = 100, 
                           offset: int = 0,
                           min_score: float = None,
                           experience_level: str = None,
                           status: str = None,
                           data_source: str = None) -> List[DeveloperLead]:
        """Get developer leads with optional filters"""
        try:
            with self.get_session() as session:
                query = session.query(DeveloperLead)
                
                if min_score is not None:
                    query = query.filter(DeveloperLead.fit_score >= min_score)
                
                if experience_level:
                    query = query.filter(DeveloperLead.experience_level == experience_level)
                
                if status:
                    query = query.filter(DeveloperLead.status == status)
                
                if data_source:
                    query = query.filter(DeveloperLead.data_source == data_source)
                
                leads = query.order_by(DeveloperLead.fit_score.desc()).offset(offset).limit(limit).all()
                return leads
                
        except Exception as e:
            logger.error(f"Error getting developer leads: {str(e)}")
            return []
    
    def get_lead_by_id(self, lead_id: int, lead_type: LeadType) -> Optional[Any]:
        """Get lead by ID and type"""
        try:
            with self.get_session() as session:
                if lead_type == LeadType.BUSINESS:
                    return session.query(BusinessLead).filter(BusinessLead.id == lead_id).first()
                else:
                    return session.query(DeveloperLead).filter(DeveloperLead.id == lead_id).first()
        except Exception as e:
            logger.error(f"Database error getting lead by ID: {str(e)}")
            return None
    
    def update_business_lead(self, lead_id: int, update_data: Dict[str, Any]) -> bool:
        """Update business lead by ID"""
        try:
            with self.get_session() as session:
                lead = session.query(BusinessLead).filter(BusinessLead.id == lead_id).first()
                if not lead:
                    return False
                
                for key, value in update_data.items():
                    if hasattr(lead, key):
                        setattr(lead, key, value)
                
                lead.last_updated = datetime.utcnow()
                session.commit()
                logger.info(f"Updated business lead ID {lead_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating business lead: {str(e)}")
            return False
    
    def update_developer_lead(self, lead_id: int, update_data: Dict[str, Any]) -> bool:
        """Update developer lead by ID"""
        try:
            with self.get_session() as session:
                lead = session.query(DeveloperLead).filter(DeveloperLead.id == lead_id).first()
                if not lead:
                    return False
                
                for key, value in update_data.items():
                    if hasattr(lead, key):
                        setattr(lead, key, value)
                
                lead.last_updated = datetime.utcnow()
                session.commit()
                logger.info(f"Updated developer lead ID {lead_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating developer lead: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics for both lead types"""
        try:
            with self.get_session() as session:
                # Business leads statistics
                business_total = session.query(BusinessLead).count()
                business_high_score = session.query(BusinessLead).filter(BusinessLead.fit_score >= 8.0).count()
                business_contacted = session.query(BusinessLead).filter(BusinessLead.is_contacted == True).count()
                
                # Developer leads statistics
                developer_total = session.query(DeveloperLead).count()
                developer_high_score = session.query(DeveloperLead).filter(DeveloperLead.fit_score >= 8.0).count()
                developer_contacted = session.query(DeveloperLead).filter(DeveloperLead.is_contacted == True).count()
                
                # Industry distribution for businesses
                business_industry_stats = session.query(
                    BusinessLead.industry,
                    session.query(BusinessLead).filter(BusinessLead.industry == BusinessLead.industry).count().label('count')
                ).group_by(BusinessLead.industry).all()
                
                # Experience level distribution for developers
                developer_experience_stats = session.query(
                    DeveloperLead.experience_level,
                    session.query(DeveloperLead).filter(DeveloperLead.experience_level == DeveloperLead.experience_level).count().label('count')
                ).group_by(DeveloperLead.experience_level).all()
                
                return {
                    'business_leads': {
                        'total': business_total,
                        'high_score': business_high_score,
                        'contacted': business_contacted,
                        'industry_distribution': {row.industry: row.count for row in business_industry_stats if row.industry}
                    },
                    'developer_leads': {
                        'total': developer_total,
                        'high_score': developer_high_score,
                        'contacted': developer_contacted,
                        'experience_distribution': {row.experience_level: row.count for row in developer_experience_stats if row.experience_level}
                    },
                    'total_leads': business_total + developer_total
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def search_leads(self, search_term: str, lead_type: LeadType = None, limit: int = 50) -> List[Any]:
        """Search leads by name, industry, or skills"""
        try:
            with self.get_session() as session:
                search_filter = f'%{search_term}%'
                results = []
                
                if lead_type is None or lead_type == LeadType.BUSINESS:
                    business_leads = session.query(BusinessLead).filter(
                        (BusinessLead.name.ilike(search_filter)) |
                        (BusinessLead.industry.ilike(search_filter)) |
                        (BusinessLead.pain_points.ilike(search_filter))
                    ).order_by(BusinessLead.fit_score.desc()).limit(limit).all()
                    results.extend(business_leads)
                
                if lead_type is None or lead_type == LeadType.DEVELOPER:
                    developer_leads = session.query(DeveloperLead).filter(
                        (DeveloperLead.name.ilike(search_filter)) |
                        (DeveloperLead.skills.ilike(search_filter)) |
                        (DeveloperLead.automation_interest.ilike(search_filter))
                    ).order_by(DeveloperLead.fit_score.desc()).limit(limit).all()
                    results.extend(developer_leads)
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching leads: {str(e)}")
            return []
    
    def export_leads_to_dict(self, leads: List[Any]) -> List[Dict[str, Any]]:
        """Convert Lead objects to dictionaries for export"""
        result = []
        for lead in leads:
            lead_dict = {
                'id': lead.id,
                'name': lead.name,
                'website': lead.website,
                'linkedin': lead.linkedin,
                'email': lead.email,
                'fit_score': lead.fit_score,
                'data_source': lead.data_source,
                'last_updated': lead.last_updated.isoformat() if lead.last_updated else None,
                'is_contacted': lead.is_contacted,
                'contact_date': lead.contact_date.isoformat() if lead.contact_date else None,
                'notes': lead.notes,
                'status': lead.status,
            }
            
            # Add type-specific fields
            if isinstance(lead, BusinessLead):
                lead_dict.update({
                    'type': 'business',
                    'industry': lead.industry,
                    'company_size': lead.company_size,
                    'pain_points': lead.pain_points,
                    'annual_revenue': lead.annual_revenue,
                    'location': lead.location,
                    'tech_stack': lead.tech_stack,
                    'automation_needs': lead.automation_needs,
                    'decision_maker': lead.decision_maker,
                })
            elif isinstance(lead, DeveloperLead):
                lead_dict.update({
                    'type': 'developer',
                    'skills': lead.skills,
                    'experience_level': lead.experience_level,
                    'project_types': lead.project_types,
                    'hourly_rate': lead.hourly_rate,
                    'availability': lead.availability,
                    'portfolio_url': lead.portfolio_url,
                    'github_url': lead.github_url,
                    'automation_interest': lead.automation_interest,
                })
            
            result.append(lead_dict)
        
        return result

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
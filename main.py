"""
Main orchestrator for the Xeinst AI Business Lead Scraper
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any
from tqdm import tqdm

from config import (
    SCRAPING_CONFIG, 
    OUTPUT_CONFIG, 
    ERROR_CONFIG, 
    DATA_SOURCES,
    QUALIFICATION_CRITERIA
)
from utils import (
    DataValidator, 
    DataProcessor, 
    FileUtils, 
    logger
)
from scrapers import (
    ClutchScraper,
    ProductHuntScraper,
    ShopifyScraper,
    LinkedInScraper
)
from database import DatabaseManager, LeadType

class LeadScraperOrchestrator:
    """Main orchestrator for lead scraping operations"""
    
    def __init__(self, use_database: bool = True):
        self.scrapers = {}
        self.all_leads = []
        self.qualified_leads = []
        self.business_leads = []
        self.developer_leads = []
        self.db_manager = None
        self.use_database = use_database
        
        self.setup_scrapers()
        if self.use_database:
            self.setup_database()
    
    def setup_scrapers(self):
        """Initialize all scrapers"""
        try:
            self.scrapers = {
                "clutch": ClutchScraper(),
                "product_hunt": ProductHuntScraper(),
                "shopify": ShopifyScraper(),
                "linkedin": LinkedInScraper()
            }
            logger.info("All scrapers initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up scrapers: {str(e)}")
    
    def setup_database(self):
        """Initialize database connection"""
        try:
            self.db_manager = DatabaseManager()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            self.use_database = False
    
    def scrape_all_sources(self, target_leads: int = 20) -> List[Dict[str, Any]]:
        """Scrape leads from all configured sources"""
        logger.info(f"Starting lead scraping process. Target: {target_leads} leads")
        
        # Calculate leads per source
        leads_per_source = max(5, target_leads // len(self.scrapers))
        
        for source_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping from {source_name}...")
                
                if source_name == "clutch":
                    leads = scraper.scrape_agencies(max_results=leads_per_source)
                elif source_name == "product_hunt":
                    leads = scraper.scrape_startups(max_results=leads_per_source)
                elif source_name == "shopify":
                    leads = scraper.scrape_stores(max_results=leads_per_source)
                elif source_name == "linkedin":
                    search_terms = ["digital agency", "web design", "ecommerce", "saas"]
                    leads = scraper.scrape_companies(search_terms, max_results=leads_per_source)
                else:
                    continue
                
                self.all_leads.extend(leads)
                logger.info(f"Scraped {len(leads)} leads from {source_name}")
                
                # Add delay between sources
                time.sleep(SCRAPING_CONFIG["delay_between_requests"] * 2)
                
            except Exception as e:
                logger.error(f"Error scraping from {source_name}: {str(e)}")
                continue
        
        logger.info(f"Total leads scraped: {len(self.all_leads)}")
        return self.all_leads
    
    def qualify_leads(self, min_score: float = 7.0) -> List[Dict[str, Any]]:
        """Qualify leads based on scoring criteria"""
        logger.info(f"Qualifying leads with minimum score: {min_score}")
        
        # Remove duplicates
        unique_leads = DataProcessor.deduplicate_leads(self.all_leads)
        logger.info(f"After deduplication: {len(unique_leads)} leads")
        
        # Filter by minimum score
        qualified = [lead for lead in unique_leads if lead.get("fit_score", 0) >= min_score]
        
        # Sort by score
        qualified = DataProcessor.sort_leads_by_score(qualified)
        
        self.qualified_leads = qualified
        logger.info(f"Qualified leads: {len(qualified)}")
        
        return qualified
    
    def classify_leads(self):
        """Classify leads into business and developer categories"""
        logger.info("Classifying leads into business and developer categories...")
        
        self.business_leads = []
        self.developer_leads = []
        
        for lead in self.qualified_leads:
            # Use the same classification logic as the database
            name = lead.get('name', '').lower()
            industry = lead.get('industry', '').lower()
            pain_points = lead.get('pain_points', '').lower()
            company_size = lead.get('company_size', '').lower()
            
            # Developer indicators
            dev_keywords = [
                'developer', 'programmer', 'coder', 'freelancer', 'consultant',
                'full-stack', 'frontend', 'backend', 'react', 'python', 'javascript',
                'node.js', 'vue', 'angular', 'php', 'java', 'c#', 'ruby', 'go',
                'mobile developer', 'ios', 'android', 'flutter', 'react native'
            ]
            
            # Check if lead is likely a developer
            is_developer = False
            for keyword in dev_keywords:
                if keyword in name or keyword in industry or keyword in pain_points:
                    is_developer = True
                    break
            
            # Check company size indicators
            if any(size in company_size for size in ['solo', 'individual', '1', 'freelancer']):
                if any(keyword in pain_points for keyword in ['code', 'development', 'programming']):
                    is_developer = True
            
            if is_developer:
                self.developer_leads.append(lead)
            else:
                self.business_leads.append(lead)
        
        logger.info(f"Classified leads: {len(self.business_leads)} business, {len(self.developer_leads)} developers")
    
    def save_leads_to_database(self) -> Dict[str, int]:
        """Save qualified leads to database"""
        if not self.use_database or not self.db_manager:
            logger.warning("Database not available, skipping database save")
            return {"business": 0, "developer": 0}
        
        try:
            # Convert leads to database format
            db_leads = []
            for lead in self.qualified_leads:
                db_lead = {
                    'name': lead.get('name', ''),
                    'industry': lead.get('industry', ''),
                    'website': lead.get('website', ''),
                    'linkedin': lead.get('linkedin', ''),
                    'email': lead.get('email', ''),
                    'company_size': lead.get('company_size', ''),
                    'pain_points': lead.get('pain_points', ''),
                    'fit_score': lead.get('fit_score', 0.0),
                    'data_source': lead.get('data_source', ''),
                    'last_updated': datetime.utcnow(),
                    'status': 'new'
                }
                
                # Add type-specific fields
                if lead in self.business_leads:
                    db_lead.update({
                        'annual_revenue': lead.get('annual_revenue', ''),
                        'location': lead.get('location', ''),
                        'tech_stack': lead.get('tech_stack', ''),
                        'automation_needs': lead.get('automation_needs', ''),
                        'decision_maker': lead.get('decision_maker', '')
                    })
                elif lead in self.developer_leads:
                    db_lead.update({
                        'skills': lead.get('skills', ''),
                        'experience_level': lead.get('experience_level', ''),
                        'project_types': lead.get('project_types', ''),
                        'hourly_rate': lead.get('hourly_rate', ''),
                        'availability': lead.get('availability', ''),
                        'portfolio_url': lead.get('portfolio_url', ''),
                        'github_url': lead.get('github_url', ''),
                        'automation_interest': lead.get('automation_interest', '')
                    })
                
                db_leads.append(db_lead)
            
            # Save to database
            result = self.db_manager.add_leads_batch(db_leads)
            logger.info(f"Saved leads to database: {result['business']} business, {result['developer']} developers")
            return result
            
        except Exception as e:
            logger.error(f"Error saving leads to database: {str(e)}")
            return {"business": 0, "developer": 0}
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.use_database or not self.db_manager:
            return {}
        
        try:
            stats = self.db_manager.get_statistics()
            return stats
        except Exception as e:
            logger.error(f"Error getting database statistics: {str(e)}")
            return {}
    
    def get_business_leads_from_database(self, 
                                        limit: int = 100, 
                                        min_score: float = None,
                                        industry: str = None,
                                        status: str = None) -> List[Dict[str, Any]]:
        """Get business leads from database with optional filters"""
        if not self.use_database or not self.db_manager:
            return []
        
        try:
            leads = self.db_manager.get_business_leads(
                limit=limit,
                min_score=min_score,
                industry=industry,
                status=status
            )
            
            # Convert to dictionary format
            return self.db_manager.export_leads_to_dict(leads)
            
        except Exception as e:
            logger.error(f"Error getting business leads from database: {str(e)}")
            return []
    
    def get_developer_leads_from_database(self, 
                                         limit: int = 100, 
                                         min_score: float = None,
                                         experience_level: str = None,
                                         status: str = None) -> List[Dict[str, Any]]:
        """Get developer leads from database with optional filters"""
        if not self.use_database or not self.db_manager:
            return []
        
        try:
            leads = self.db_manager.get_developer_leads(
                limit=limit,
                min_score=min_score,
                experience_level=experience_level,
                status=status
            )
            
            # Convert to dictionary format
            return self.db_manager.export_leads_to_dict(leads)
            
        except Exception as e:
            logger.error(f"Error getting developer leads from database: {str(e)}")
            return []
    
    def search_leads_in_database(self, search_term: str, lead_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search leads in database"""
        if not self.use_database or not self.db_manager:
            return []
        
        try:
            lead_type_enum = None
            if lead_type == 'business':
                lead_type_enum = LeadType.BUSINESS
            elif lead_type == 'developer':
                lead_type_enum = LeadType.DEVELOPER
            
            leads = self.db_manager.search_leads(search_term, lead_type_enum, limit)
            return self.db_manager.export_leads_to_dict(leads)
            
        except Exception as e:
            logger.error(f"Error searching leads in database: {str(e)}")
            return []
    
    def update_lead_status(self, lead_id: int, lead_type: str, status: str, notes: str = None) -> bool:
        """Update lead status in database"""
        if not self.use_database or not self.db_manager:
            return False
        
        try:
            lead_type_enum = LeadType.BUSINESS if lead_type == 'business' else LeadType.DEVELOPER
            
            update_data = {'status': status}
            if notes:
                update_data['notes'] = notes
            
            if lead_type == 'business':
                success = self.db_manager.update_business_lead(lead_id, update_data)
            else:
                success = self.db_manager.update_developer_lead(lead_id, update_data)
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating lead status: {str(e)}")
            return False
    
    def validate_leads(self) -> Dict[str, Any]:
        """Validate scraped leads"""
        logger.info("Validating scraped leads...")
        
        validator = DataValidator()
        validation_results = {
            'total_leads': len(self.all_leads),
            'valid_leads': 0,
            'invalid_leads': 0,
            'validation_errors': []
        }
        
        for lead in self.all_leads:
            is_valid, errors = validator.validate_lead(lead)
            if is_valid:
                validation_results['valid_leads'] += 1
            else:
                validation_results['invalid_leads'] += 1
                validation_results['validation_errors'].extend(errors)
        
        logger.info(f"Validation complete: {validation_results['valid_leads']} valid, {validation_results['invalid_leads']} invalid")
        return validation_results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        logger.info("Generating summary report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'scraping_summary': {
                'total_leads_scraped': len(self.all_leads),
                'qualified_leads': len(self.qualified_leads),
                'business_leads': len(self.business_leads),
                'developer_leads': len(self.developer_leads),
                'qualification_rate': len(self.qualified_leads) / len(self.all_leads) * 100 if self.all_leads else 0
            },
            'score_distribution': self.get_score_distribution(),
            'industry_distribution': self.get_industry_distribution(),
            'data_source_distribution': self.get_data_source_distribution(),
            'database_stats': self.get_database_statistics()
        }
        
        return report
    
    def get_score_distribution(self) -> Dict[str, int]:
        """Get fit score distribution"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for lead in self.qualified_leads:
            score = lead.get('fit_score', 0)
            if score >= 8.0:
                distribution['high'] += 1
            elif score >= 6.0:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution
    
    def get_industry_distribution(self) -> Dict[str, int]:
        """Get industry distribution for business leads"""
        distribution = {}
        
        for lead in self.business_leads:
            industry = lead.get('industry', 'Unknown')
            distribution[industry] = distribution.get(industry, 0) + 1
        
        return distribution
    
    def get_data_source_distribution(self) -> Dict[str, int]:
        """Get data source distribution"""
        distribution = {}
        
        for lead in self.all_leads:
            source = lead.get('data_source', 'Unknown')
            distribution[source] = distribution.get(source, 0) + 1
        
        return distribution
    
    def save_results(self, filename: str = None) -> bool:
        """Save results to files"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save all leads
            if not filename:
                filename = f"xeinst_leads_{timestamp}"
            
            # Save qualified leads
            qualified_filename = f"{filename}_qualified.json"
            with open(qualified_filename, 'w') as f:
                json.dump(self.qualified_leads, f, indent=2, default=str)
            
            # Save business leads
            business_filename = f"{filename}_business.json"
            with open(business_filename, 'w') as f:
                json.dump(self.business_leads, f, indent=2, default=str)
            
            # Save developer leads
            developer_filename = f"{filename}_developers.json"
            with open(developer_filename, 'w') as f:
                json.dump(self.developer_leads, f, indent=2, default=str)
            
            # Save summary report
            report_filename = f"{filename}_report.json"
            report = self.generate_summary_report()
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Results saved to files:")
            logger.info(f"  - Qualified leads: {qualified_filename}")
            logger.info(f"  - Business leads: {business_filename}")
            logger.info(f"  - Developer leads: {developer_filename}")
            logger.info(f"  - Summary report: {report_filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            for scraper in self.scrapers.values():
                if hasattr(scraper, 'cleanup'):
                    scraper.cleanup()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def run_complete_scraping(self, target_leads: int = 20, min_score: float = 7.0) -> Dict[str, Any]:
        """Run complete scraping process"""
        logger.info("🚀 Starting complete lead scraping process...")
        
        try:
            # Step 1: Scrape leads
            self.scrape_all_sources(target_leads)
            
            # Step 2: Qualify leads
            self.qualify_leads(min_score)
            
            # Step 3: Classify leads
            self.classify_leads()
            
            # Step 4: Validate leads
            validation_results = self.validate_leads()
            
            # Step 5: Save to database
            db_results = self.save_leads_to_database()
            
            # Step 6: Generate report
            report = self.generate_summary_report()
            
            # Step 7: Save results to files
            self.save_results()
            
            logger.info("✅ Complete scraping process finished successfully!")
            
            return {
                'success': True,
                'report': report,
                'validation': validation_results,
                'database_results': db_results
            }
            
        except Exception as e:
            logger.error(f"❌ Error in complete scraping process: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.cleanup()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Xeinst AI Business Lead Scraper')
    parser.add_argument('--target', type=int, default=20, help='Target number of leads to scrape')
    parser.add_argument('--min-score', type=float, default=7.0, help='Minimum fit score for qualification')
    parser.add_argument('--no-database', action='store_true', help='Skip database operations')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = LeadScraperOrchestrator(use_database=not args.no_database)
    
    # Run complete scraping process
    result = orchestrator.run_complete_scraping(
        target_leads=args.target,
        min_score=args.min_score
    )
    
    if result['success']:
        print("\n🎉 Scraping completed successfully!")
        print(f"📊 Total leads scraped: {result['report']['scraping_summary']['total_leads_scraped']}")
        print(f"✅ Qualified leads: {result['report']['scraping_summary']['qualified_leads']}")
        print(f"🏢 Business leads: {result['report']['scraping_summary']['business_leads']}")
        print(f"👨‍💻 Developer leads: {result['report']['scraping_summary']['developer_leads']}")
        
        if result['database_results']:
            print(f"💾 Database saves: {result['database_results']['business']} business, {result['database_results']['developer']} developers")
    else:
        print(f"\n❌ Scraping failed: {result['error']}")

if __name__ == "__main__":
    main() 
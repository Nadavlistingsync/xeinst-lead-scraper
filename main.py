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

class LeadScraperOrchestrator:
    """Main orchestrator for lead scraping operations"""
    
    def __init__(self):
        self.scrapers = {}
        self.all_leads = []
        self.qualified_leads = []
        self.setup_scrapers()
    
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
    
    def validate_leads(self) -> Dict[str, Any]:
        """Validate all qualified leads"""
        logger.info("Validating qualified leads...")
        
        validation_results = {
            "total_leads": len(self.qualified_leads),
            "valid_leads": 0,
            "invalid_leads": 0,
            "warnings": [],
            "errors": []
        }
        
        for lead in self.qualified_leads:
            validation = DataValidator.validate_lead_data(lead)
            
            if validation["is_valid"]:
                validation_results["valid_leads"] += 1
            else:
                validation_results["invalid_leads"] += 1
                validation_results["errors"].extend(validation["errors"])
            
            validation_results["warnings"].extend(validation["warnings"])
        
        logger.info(f"Validation complete: {validation_results['valid_leads']} valid, {validation_results['invalid_leads']} invalid")
        return validation_results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of the scraping operation"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_leads_scraped": len(self.all_leads),
            "qualified_leads": len(self.qualified_leads),
            "sources_used": list(self.scrapers.keys()),
            "score_distribution": self.get_score_distribution(),
            "industry_distribution": self.get_industry_distribution(),
            "top_leads": self.qualified_leads[:5] if self.qualified_leads else []
        }
        
        return report
    
    def get_score_distribution(self) -> Dict[str, int]:
        """Get distribution of fit scores"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for lead in self.qualified_leads:
            score = lead.get("fit_score", 0)
            if score >= 8:
                distribution["high"] += 1
            elif score >= 6:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution
    
    def get_industry_distribution(self) -> Dict[str, int]:
        """Get distribution of industries"""
        distribution = {}
        
        for lead in self.qualified_leads:
            industry = lead.get("industry", "Unknown")
            distribution[industry] = distribution.get(industry, 0) + 1
        
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def save_results(self, filename: str = None) -> bool:
        """Save results to files"""
        if not filename:
            filename = OUTPUT_CONFIG["filename"]
        
        success = True
        
        # Save to JSON
        if not FileUtils.save_leads_to_json(self.qualified_leads, filename):
            success = False
        
        # Save backup to Excel
        backup_filename = OUTPUT_CONFIG["backup_filename"]
        if not FileUtils.save_leads_to_excel(self.qualified_leads, backup_filename):
            success = False
        
        # Save summary report
        report = self.generate_summary_report()
        report_filename = f"scraping_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Summary report saved to {report_filename}")
        except Exception as e:
            logger.error(f"Failed to save summary report: {str(e)}")
            success = False
        
        return success
    
    def cleanup(self):
        """Cleanup all scrapers"""
        for scraper in self.scrapers.values():
            try:
                scraper.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up scraper: {str(e)}")
    
    def run_complete_scraping(self, target_leads: int = 20, min_score: float = 7.0) -> Dict[str, Any]:
        """Run complete scraping process"""
        try:
            logger.info("=== Starting Xeinst AI Lead Scraping Process ===")
            
            # Step 1: Scrape from all sources
            self.scrape_all_sources(target_leads)
            
            # Step 2: Qualify leads
            self.qualify_leads(min_score)
            
            # Step 3: Validate leads
            validation_results = self.validate_leads()
            
            # Step 4: Save results
            save_success = self.save_results()
            
            # Step 5: Generate final report
            final_report = self.generate_summary_report()
            final_report["validation_results"] = validation_results
            final_report["save_success"] = save_success
            
            logger.info("=== Scraping Process Complete ===")
            logger.info(f"Final Results: {len(self.qualified_leads)} qualified leads")
            
            return final_report
            
        except Exception as e:
            logger.error(f"Error in complete scraping process: {str(e)}")
            return {"error": str(e)}
        finally:
            self.cleanup()

def main():
    """Main function to run the scraper"""
    print("🚀 Xeinst AI Business Lead Scraper")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = LeadScraperOrchestrator()
    
    try:
        # Run complete scraping process
        results = orchestrator.run_complete_scraping(
            target_leads=20,
            min_score=7.0
        )
        
        # Display results
        print("\n📊 Scraping Results:")
        print(f"Total leads scraped: {results.get('total_leads_scraped', 0)}")
        print(f"Qualified leads: {results.get('qualified_leads', 0)}")
        print(f"Sources used: {', '.join(results.get('sources_used', []))}")
        
        if results.get('top_leads'):
            print("\n🏆 Top 5 Leads:")
            for i, lead in enumerate(results['top_leads'][:5], 1):
                print(f"{i}. {lead.get('name', 'N/A')} - Score: {lead.get('fit_score', 0)}")
                print(f"   Industry: {lead.get('industry', 'N/A')}")
                print(f"   Website: {lead.get('website', 'N/A')}")
                print(f"   Pain Points: {lead.get('pain_points', 'N/A')}")
                print()
        
        print(f"\n✅ Results saved to: {OUTPUT_CONFIG['filename']}")
        print(f"📈 Summary report saved to: scraping_report_*.json")
        
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        orchestrator.cleanup()

if __name__ == "__main__":
    main() 
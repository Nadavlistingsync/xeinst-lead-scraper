"""
Specialized scrapers for different data sources
"""

import time
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from utils import WebUtils, DataProcessor, DataValidator, LeadScorer, logger
from config import SCRAPING_CONFIG

class BaseScraper:
    """Base class for all scrapers"""
    
    def __init__(self):
        self.session = None
        self.driver = None
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session with proper headers"""
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": WebUtils.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
    
    def setup_driver(self):
        """Setup Selenium WebDriver for JavaScript-heavy sites"""
        if self.driver:
            return
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--user-agent={WebUtils.get_random_user_agent()}")
        
        try:
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}")
            self.driver = None
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def delay(self):
        """Add delay between requests"""
        time.sleep(SCRAPING_CONFIG["delay_between_requests"])
    
    def extract_lead_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate lead data"""
        lead_data = {
            "name": DataProcessor.clean_text(raw_data.get("name", "")),
            "industry": DataProcessor.clean_text(raw_data.get("industry", "")),
            "website": raw_data.get("website", ""),
            "linkedin": raw_data.get("linkedin", ""),
            "email": raw_data.get("email", ""),
            "company_size": DataProcessor.clean_text(raw_data.get("company_size", "")),
            "pain_points": DataProcessor.clean_text(raw_data.get("pain_points", "")),
            "data_source": raw_data.get("data_source", ""),
            "last_updated": raw_data.get("last_updated", "")
        }
        
        # Calculate fit score
        lead_data["fit_score"] = LeadScorer.calculate_fit_score(lead_data)
        
        return lead_data

class ClutchScraper(BaseScraper):
    """Scraper for Clutch.co agency directory"""
    
    def scrape_agencies(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Scrape agencies from Clutch.co"""
        leads = []
        base_url = "https://clutch.co"
        
        search_paths = [
            "/agencies/web-designers",
            "/agencies/digital-marketers",
            "/agencies/developers"
        ]
        
        for path in search_paths:
            if len(leads) >= max_results:
                break
            
            url = f"{base_url}{path}"
            logger.info(f"Scraping Clutch: {url}")
            
            try:
                response = self.session.get(url, timeout=SCRAPING_CONFIG["timeout"])
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                agency_cards = soup.find_all('li', class_='provider-row')
                
                for card in agency_cards[:10]:  # Limit per page
                    if len(leads) >= max_results:
                        break
                    
                    lead_data = self.extract_agency_data(card)
                    if lead_data:
                        leads.append(lead_data)
                        self.delay()
                
            except Exception as e:
                logger.error(f"Error scraping Clutch {url}: {str(e)}")
                continue
        
        return leads
    
    def extract_agency_data(self, card) -> Optional[Dict[str, Any]]:
        """Extract agency data from Clutch card"""
        try:
            # Extract name
            name_elem = card.find('h3', class_='company-name')
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            # Extract website
            website_elem = card.find('a', class_='website-link')
            website = website_elem.get('href') if website_elem else ""
            
            # Extract industry/services
            services_elem = card.find('span', class_='services')
            services = services_elem.get_text(strip=True) if services_elem else ""
            
            # Extract company size
            size_elem = card.find('span', class_='company-size')
            company_size = size_elem.get_text(strip=True) if size_elem else ""
            
            # Extract location
            location_elem = card.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Determine pain points based on services
            pain_points = self.analyze_pain_points(services, company_size)
            
            lead_data = {
                "name": name,
                "industry": services or "Digital Agency",
                "website": website,
                "linkedin": "",
                "email": "",
                "company_size": company_size,
                "pain_points": pain_points,
                "data_source": "Clutch.co",
                "last_updated": time.strftime("%Y-%m-%d")
            }
            
            # Validate data
            validation = DataValidator.validate_lead_data(lead_data)
            if validation["is_valid"]:
                return self.extract_lead_data(lead_data)
            
        except Exception as e:
            logger.error(f"Error extracting agency data: {str(e)}")
        
        return None
    
    def analyze_pain_points(self, services: str, company_size: str) -> str:
        """Analyze services and company size to determine pain points"""
        pain_points = []
        
        if "web design" in services.lower():
            pain_points.append("client communication and project management")
        
        if "digital marketing" in services.lower():
            pain_points.append("campaign monitoring and reporting")
        
        if "development" in services.lower():
            pain_points.append("code deployment and testing automation")
        
        if "small" in company_size.lower() or "2-10" in company_size:
            pain_points.append("limited resources for repetitive tasks")
        
        if pain_points:
            return f"Likely needs automation for: {', '.join(pain_points)}"
        
        return "Digital agency with potential for workflow automation"

class ProductHuntScraper(BaseScraper):
    """Scraper for Product Hunt startup directory"""
    
    def scrape_startups(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Scrape startups from Product Hunt"""
        leads = []
        url = "https://www.producthunt.com/topics/business-tools"
        
        logger.info(f"Scraping Product Hunt: {url}")
        
        try:
            self.setup_driver()
            if not self.driver:
                return leads
            
            self.driver.get(url)
            time.sleep(5)  # Wait for page to load
            
            # Scroll to load more content
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find product cards
            product_cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-test="post-item"]')
            
            for card in product_cards[:max_results]:
                lead_data = self.extract_startup_data(card)
                if lead_data:
                    leads.append(lead_data)
                    self.delay()
                
        except Exception as e:
            logger.error(f"Error scraping Product Hunt: {str(e)}")
        
        return leads
    
    def extract_startup_data(self, card) -> Optional[Dict[str, Any]]:
        """Extract startup data from Product Hunt card"""
        try:
            # Extract name
            name_elem = card.find_element(By.CSS_SELECTOR, '[data-test="post-name"]')
            name = name_elem.text if name_elem else ""
            
            # Extract tagline
            tagline_elem = card.find_element(By.CSS_SELECTOR, '[data-test="post-tagline"]')
            tagline = tagline_elem.text if tagline_elem else ""
            
            # Extract website (if available)
            website = ""
            try:
                website_elem = card.find_element(By.CSS_SELECTOR, 'a[href*="http"]')
                website = website_elem.get_attribute('href')
            except:
                pass
            
            # Determine industry and pain points
            industry, pain_points = self.analyze_startup(tagline, name)
            
            lead_data = {
                "name": name,
                "industry": industry,
                "website": website,
                "linkedin": "",
                "email": "",
                "company_size": "Startup (1-10 employees)",
                "pain_points": pain_points,
                "data_source": "Product Hunt",
                "last_updated": time.strftime("%Y-%m-%d")
            }
            
            # Validate data
            validation = DataValidator.validate_lead_data(lead_data)
            if validation["is_valid"]:
                return self.extract_lead_data(lead_data)
            
        except Exception as e:
            logger.error(f"Error extracting startup data: {str(e)}")
        
        return None
    
    def analyze_startup(self, tagline: str, name: str) -> tuple:
        """Analyze startup to determine industry and pain points"""
        content = f"{tagline} {name}".lower()
        
        # Determine industry
        if any(keyword in content for keyword in ["saas", "software", "app", "platform"]):
            industry = "SaaS/Software"
        elif any(keyword in content for keyword in ["ecommerce", "shop", "store", "marketplace"]):
            industry = "E-commerce"
        elif any(keyword in content for keyword in ["agency", "consulting", "service"]):
            industry = "Service Agency"
        else:
            industry = "Business Tools"
        
        # Determine pain points
        pain_points = []
        if "automation" in content:
            pain_points.append("workflow automation")
        if "customer" in content:
            pain_points.append("customer support automation")
        if "marketing" in content:
            pain_points.append("marketing campaign management")
        if "analytics" in content:
            pain_points.append("data analysis and reporting")
        
        if pain_points:
            pain_points_text = f"Startup likely needs automation for: {', '.join(pain_points)}"
        else:
            pain_points_text = "Early-stage startup with potential for operational automation"
        
        return industry, pain_points_text

class ShopifyScraper(BaseScraper):
    """Scraper for Shopify store examples"""
    
    def scrape_stores(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Scrape Shopify stores"""
        leads = []
        url = "https://www.shopify.com/examples"
        
        logger.info(f"Scraping Shopify examples: {url}")
        
        try:
            response = self.session.get(url, timeout=SCRAPING_CONFIG["timeout"])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find store examples (this is a simplified approach)
            store_links = soup.find_all('a', href=re.compile(r'https?://[^/]+'))
            
            for link in store_links[:max_results]:
                website = link.get('href')
                if website and self.is_valid_shopify_store(website):
                    lead_data = self.extract_store_data(website)
                    if lead_data:
                        leads.append(lead_data)
                        self.delay()
                
        except Exception as e:
            logger.error(f"Error scraping Shopify examples: {str(e)}")
        
        return leads
    
    def is_valid_shopify_store(self, url: str) -> bool:
        """Check if URL is a valid Shopify store"""
        try:
            response = self.session.get(url, timeout=10)
            return "shopify" in response.text.lower() or "myshopify.com" in url
        except:
            return False
    
    def extract_store_data(self, website: str) -> Optional[Dict[str, Any]]:
        """Extract store data from Shopify store"""
        try:
            response = self.session.get(website, timeout=SCRAPING_CONFIG["timeout"])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract store name
            name = self.extract_store_name(soup, website)
            
            # Extract industry based on content
            industry = self.determine_store_industry(soup)
            
            # Analyze automation opportunities
            pain_points = self.analyze_store_automation_needs(soup)
            
            lead_data = {
                "name": name,
                "industry": industry,
                "website": website,
                "linkedin": "",
                "email": "",
                "company_size": "E-commerce Store (1-10 employees)",
                "pain_points": pain_points,
                "data_source": "Shopify Examples",
                "last_updated": time.strftime("%Y-%m-%d")
            }
            
            # Validate data
            validation = DataValidator.validate_lead_data(lead_data)
            if validation["is_valid"]:
                return self.extract_lead_data(lead_data)
            
        except Exception as e:
            logger.error(f"Error extracting store data from {website}: {str(e)}")
        
        return None
    
    def extract_store_name(self, soup, website: str) -> str:
        """Extract store name from page"""
        # Try multiple selectors for store name
        selectors = [
            'title',
            'h1',
            '.site-title',
            '.brand',
            '[data-testid="store-name"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                name = elem.get_text(strip=True)
                if name and len(name) < 100:
                    return name
        
        # Fallback to domain name
        from urllib.parse import urlparse
        domain = urlparse(website).netloc
        return domain.replace('.myshopify.com', '').replace('www.', '').title()
    
    def determine_store_industry(self, soup) -> str:
        """Determine store industry based on content"""
        text = soup.get_text().lower()
        
        if any(keyword in text for keyword in ["clothing", "fashion", "apparel"]):
            return "Fashion & Apparel"
        elif any(keyword in text for keyword in ["jewelry", "accessories"]):
            return "Jewelry & Accessories"
        elif any(keyword in text for keyword in ["home", "decor", "furniture"]):
            return "Home & Garden"
        elif any(keyword in text for keyword in ["beauty", "cosmetics", "skincare"]):
            return "Beauty & Personal Care"
        elif any(keyword in text for keyword in ["electronics", "tech", "gadgets"]):
            return "Electronics"
        else:
            return "E-commerce"
    
    def analyze_store_automation_needs(self, soup) -> str:
        """Analyze store for automation opportunities"""
        text = soup.get_text().lower()
        opportunities = []
        
        if "contact" in text or "support" in text:
            opportunities.append("customer support automation")
        
        if "inventory" in text or "stock" in text:
            opportunities.append("inventory management")
        
        if "order" in text or "shipping" in text:
            opportunities.append("order processing and fulfillment")
        
        if "marketing" in text or "email" in text:
            opportunities.append("marketing campaign automation")
        
        if opportunities:
            return f"E-commerce store likely needs automation for: {', '.join(opportunities)}"
        
        return "E-commerce store with potential for order and customer service automation"

class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn company pages (limited functionality)"""
    
    def scrape_companies(self, search_terms: List[str], max_results: int = 20) -> List[Dict[str, Any]]:
        """Scrape companies from LinkedIn search"""
        leads = []
        
        for term in search_terms:
            if len(leads) >= max_results:
                break
            
            logger.info(f"Searching LinkedIn for: {term}")
            
            # Note: LinkedIn scraping is limited due to anti-bot measures
            # This is a simplified approach that would need enhancement
            try:
                search_url = f"https://www.linkedin.com/search/results/companies/?keywords={term}"
                
                # For demonstration, we'll create sample data
                # In practice, you'd need to implement proper LinkedIn scraping
                sample_lead = self.create_sample_linkedin_lead(term)
                if sample_lead:
                    leads.append(sample_lead)
                    self.delay()
                
            except Exception as e:
                logger.error(f"Error searching LinkedIn for {term}: {str(e)}")
                continue
        
        return leads
    
    def create_sample_linkedin_lead(self, search_term: str) -> Optional[Dict[str, Any]]:
        """Create sample lead data for LinkedIn (for demonstration)"""
        # This is a placeholder - real implementation would scrape actual data
        lead_data = {
            "name": f"Sample {search_term.title()} Company",
            "industry": search_term.title(),
            "website": f"https://example-{search_term.lower()}.com",
            "linkedin": f"https://linkedin.com/company/sample-{search_term.lower()}",
            "email": "",
            "company_size": "Small Business (2-10 employees)",
            "pain_points": f"Small {search_term} business likely needs automation for customer management and operations",
            "data_source": "LinkedIn Search",
            "last_updated": time.strftime("%Y-%m-%d")
        }
        
        return self.extract_lead_data(lead_data) 
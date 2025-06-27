"""
Utility functions for the Xeinst AI Business Lead Scraper
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin
import requests
from fake_useragent import UserAgent
from config import VALIDATION_RULES, SCORING_WEIGHTS, INDUSTRY_SCORES, AUTOMATION_INDICATORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataValidator:
    """Handles data validation for scraped leads"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        pattern = VALIDATION_RULES["email_pattern"]
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        pattern = VALIDATION_RULES["url_pattern"]
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate business/person name"""
        if not name:
            return False
        length = len(name.strip())
        return VALIDATION_RULES["min_name_length"] <= length <= VALIDATION_RULES["max_name_length"]
    
    @staticmethod
    def validate_lead_data(lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete lead data and return validation results"""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        for field in VALIDATION_RULES["required_fields"]:
            if field not in lead_data or not lead_data[field]:
                validation_results["is_valid"] = False
                validation_results["errors"].append(f"Missing required field: {field}")
        
        # Validate individual fields
        if "name" in lead_data:
            if not DataValidator.validate_name(lead_data["name"]):
                validation_results["is_valid"] = False
                validation_results["errors"].append("Invalid name format")
        
        if "website" in lead_data:
            if not DataValidator.validate_url(lead_data["website"]):
                validation_results["is_valid"] = False
                validation_results["errors"].append("Invalid website URL")
        
        if "email" in lead_data and lead_data["email"]:
            if not DataValidator.validate_email(lead_data["email"]):
                validation_results["warnings"].append("Invalid email format")
        
        if "linkedin" in lead_data and lead_data["linkedin"]:
            if not DataValidator.validate_url(lead_data["linkedin"]):
                validation_results["warnings"].append("Invalid LinkedIn URL")
        
        return validation_results

class LeadScorer:
    """Handles lead scoring based on qualification criteria"""
    
    @staticmethod
    def calculate_company_size_score(company_size: str) -> float:
        """Score based on company size"""
        if not company_size:
            return 5.0  # Default score
        
        size_lower = company_size.lower()
        
        # Solo entrepreneur or very small team
        if any(keyword in size_lower for keyword in ["solo", "1", "individual", "freelancer"]):
            return 9.0
        # Small team (2-10 employees)
        elif any(keyword in size_lower for keyword in ["2-10", "small", "startup"]):
            return 8.0
        # Medium team (11-50 employees)
        elif any(keyword in size_lower for keyword in ["11-50", "medium"]):
            return 6.0
        # Large team (50+ employees)
        elif any(keyword in size_lower for keyword in ["50+", "large", "enterprise"]):
            return 3.0
        
        return 5.0  # Default score
    
    @staticmethod
    def calculate_industry_score(industry: str) -> float:
        """Score based on industry relevance"""
        if not industry:
            return 5.0
        
        industry_lower = industry.lower()
        
        # Check against predefined industry scores
        for industry_key, score in INDUSTRY_SCORES.items():
            if industry_key.replace("_", " ") in industry_lower:
                return float(score)
        
        # Check for specific keywords
        if any(keyword in industry_lower for keyword in ["agency", "consulting", "freelance"]):
            return 8.0
        elif any(keyword in industry_lower for keyword in ["ecommerce", "online store", "shopify"]):
            return 9.0
        elif any(keyword in industry_lower for keyword in ["saas", "software", "tech"]):
            return 8.0
        
        return 5.0  # Default score
    
    @staticmethod
    def calculate_automation_indicators_score(website_content: str, business_description: str) -> float:
        """Score based on automation opportunity indicators"""
        if not website_content and not business_description:
            return 5.0
        
        content = f"{website_content} {business_description}".lower()
        score = 5.0
        
        # Check for automation indicators
        indicators_found = 0
        for indicator in AUTOMATION_INDICATORS:
            if indicator.replace("_", " ") in content:
                indicators_found += 1
        
        # Score based on number of indicators found
        if indicators_found >= 3:
            score = 9.0
        elif indicators_found == 2:
            score = 7.0
        elif indicators_found == 1:
            score = 6.0
        
        return score
    
    @staticmethod
    def calculate_data_quality_score(lead_data: Dict[str, Any]) -> float:
        """Score based on data quality and completeness"""
        score = 5.0
        
        # Bonus for having email
        if lead_data.get("email"):
            score += 2.0
        
        # Bonus for having LinkedIn
        if lead_data.get("linkedin"):
            score += 1.0
        
        # Bonus for having company size
        if lead_data.get("company_size"):
            score += 1.0
        
        # Bonus for having pain points description
        if lead_data.get("pain_points"):
            score += 1.0
        
        return min(score, 10.0)  # Cap at 10
    
    @staticmethod
    def calculate_fit_score(lead_data: Dict[str, Any]) -> float:
        """Calculate overall fit score for a lead"""
        total_score = 0.0
        
        # Company size score
        company_size_score = LeadScorer.calculate_company_size_score(
            lead_data.get("company_size", "")
        )
        total_score += company_size_score * SCORING_WEIGHTS["company_size"]
        
        # Industry relevance score
        industry_score = LeadScorer.calculate_industry_score(
            lead_data.get("industry", "")
        )
        total_score += industry_score * SCORING_WEIGHTS["industry_relevance"]
        
        # Automation indicators score
        automation_score = LeadScorer.calculate_automation_indicators_score(
            lead_data.get("website_content", ""),
            lead_data.get("pain_points", "")
        )
        total_score += automation_score * SCORING_WEIGHTS["automation_indicators"]
        
        # Data quality score
        data_quality_score = LeadScorer.calculate_data_quality_score(lead_data)
        total_score += data_quality_score * SCORING_WEIGHTS["data_quality"]
        
        # Contact availability score
        contact_score = 5.0
        if lead_data.get("email") or lead_data.get("linkedin"):
            contact_score = 8.0
        total_score += contact_score * SCORING_WEIGHTS["contact_availability"]
        
        return round(total_score, 2)

class WebUtils:
    """Web scraping utilities"""
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Get a random user agent string"""
        try:
            ua = UserAgent()
            return ua.random
        except:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    @staticmethod
    def make_request(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        if not headers:
            headers = {
                "User-Agent": WebUtils.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    @staticmethod
    def is_valid_website(url: str) -> bool:
        """Check if website is accessible"""
        response = WebUtils.make_request(url)
        return response is not None and response.status_code == 200

class DataProcessor:
    """Data processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-\.@]', '', text)
        return text
    
    @staticmethod
    def extract_email_from_text(text: str) -> Optional[str]:
        """Extract email addresses from text"""
        if not text:
            return None
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    @staticmethod
    def deduplicate_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate leads based on website or name"""
        seen_websites = set()
        seen_names = set()
        unique_leads = []
        
        for lead in leads:
            website = lead.get("website", "").lower()
            name = lead.get("name", "").lower()
            
            if website and website not in seen_websites:
                seen_websites.add(website)
                unique_leads.append(lead)
            elif name and name not in seen_names:
                seen_names.add(name)
                unique_leads.append(lead)
        
        return unique_leads
    
    @staticmethod
    def sort_leads_by_score(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort leads by fit score in descending order"""
        return sorted(leads, key=lambda x: x.get("fit_score", 0), reverse=True)

class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def save_leads_to_json(leads: List[Dict[str, Any]], filename: str) -> bool:
        """Save leads to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(leads, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(leads)} leads to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save leads to {filename}: {str(e)}")
            return False
    
    @staticmethod
    def save_leads_to_excel(leads: List[Dict[str, Any]], filename: str) -> bool:
        """Save leads to Excel file"""
        try:
            import pandas as pd
            df = pd.DataFrame(leads)
            df.to_excel(filename, index=False)
            logger.info(f"Saved {len(leads)} leads to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save leads to {filename}: {str(e)}")
            return False 
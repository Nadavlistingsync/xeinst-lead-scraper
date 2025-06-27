"""
Test suite for the Xeinst AI Business Lead Scraper
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from config import SCRAPING_CONFIG, VALIDATION_RULES, SCORING_WEIGHTS
from utils import (
    DataValidator, 
    LeadScorer, 
    DataProcessor, 
    FileUtils, 
    WebUtils
)
from scrapers import BaseScraper, ClutchScraper
from main import LeadScraperOrchestrator

class TestDataValidator(unittest.TestCase):
    """Test data validation functionality"""
    
    def test_validate_email(self):
        """Test email validation"""
        # Valid emails
        self.assertTrue(DataValidator.validate_email("test@example.com"))
        self.assertTrue(DataValidator.validate_email("user.name@domain.co.uk"))
        self.assertTrue(DataValidator.validate_email("test+tag@example.org"))
        
        # Invalid emails
        self.assertFalse(DataValidator.validate_email("invalid-email"))
        self.assertFalse(DataValidator.validate_email("@example.com"))
        self.assertFalse(DataValidator.validate_email("test@"))
        self.assertFalse(DataValidator.validate_email(""))
        self.assertFalse(DataValidator.validate_email(None))
    
    def test_validate_url(self):
        """Test URL validation"""
        # Valid URLs
        self.assertTrue(DataValidator.validate_url("https://example.com"))
        self.assertTrue(DataValidator.validate_url("http://www.example.org"))
        self.assertTrue(DataValidator.validate_url("https://subdomain.example.com/path"))
        
        # Invalid URLs
        self.assertFalse(DataValidator.validate_url("not-a-url"))
        self.assertFalse(DataValidator.validate_url("ftp://example.com"))
        self.assertFalse(DataValidator.validate_url(""))
        self.assertFalse(DataValidator.validate_url(None))
    
    def test_validate_name(self):
        """Test name validation"""
        # Valid names
        self.assertTrue(DataValidator.validate_name("Test Company"))
        self.assertTrue(DataValidator.validate_name("A"))
        self.assertTrue(DataValidator.validate_name("A" * 100))
        
        # Invalid names
        self.assertFalse(DataValidator.validate_name(""))
        self.assertFalse(DataValidator.validate_name("A" * 101))
        self.assertFalse(DataValidator.validate_name(None))
    
    def test_validate_lead_data(self):
        """Test complete lead data validation"""
        # Valid lead data
        valid_lead = {
            "name": "Test Company",
            "industry": "Technology",
            "website": "https://example.com",
            "email": "test@example.com"
        }
        
        validation = DataValidator.validate_lead_data(valid_lead)
        self.assertTrue(validation["is_valid"])
        self.assertEqual(len(validation["errors"]), 0)
        
        # Invalid lead data
        invalid_lead = {
            "name": "",
            "industry": "Technology",
            "website": "not-a-url"
        }
        
        validation = DataValidator.validate_lead_data(invalid_lead)
        self.assertFalse(validation["is_valid"])
        self.assertGreater(len(validation["errors"]), 0)

class TestLeadScorer(unittest.TestCase):
    """Test lead scoring functionality"""
    
    def test_calculate_company_size_score(self):
        """Test company size scoring"""
        # Solo entrepreneurs
        self.assertEqual(LeadScorer.calculate_company_size_score("solo"), 9.0)
        self.assertEqual(LeadScorer.calculate_company_size_score("1 employee"), 9.0)
        
        # Small teams
        self.assertEqual(LeadScorer.calculate_company_size_score("2-10 employees"), 8.0)
        self.assertEqual(LeadScorer.calculate_company_size_score("small team"), 8.0)
        
        # Medium teams
        self.assertEqual(LeadScorer.calculate_company_size_score("11-50 employees"), 6.0)
        
        # Large teams
        self.assertEqual(LeadScorer.calculate_company_size_score("50+ employees"), 3.0)
        
        # Default
        self.assertEqual(LeadScorer.calculate_company_size_score(""), 5.0)
    
    def test_calculate_industry_score(self):
        """Test industry scoring"""
        # High-scoring industries
        self.assertEqual(LeadScorer.calculate_industry_score("web design"), 9.0)
        self.assertEqual(LeadScorer.calculate_industry_score("ecommerce"), 9.0)
        self.assertEqual(LeadScorer.calculate_industry_score("digital marketing"), 8.0)
        self.assertEqual(LeadScorer.calculate_industry_score("saas"), 8.0)
        
        # Medium-scoring industries
        self.assertEqual(LeadScorer.calculate_industry_score("consulting"), 7.0)
        
        # Default
        self.assertEqual(LeadScorer.calculate_industry_score(""), 5.0)
        self.assertEqual(LeadScorer.calculate_industry_score("manufacturing"), 5.0)
    
    def test_calculate_automation_indicators_score(self):
        """Test automation indicators scoring"""
        # High indicators
        content = "multiple customer touchpoints repetitive data entry high customer inquiries"
        score = LeadScorer.calculate_automation_indicators_score(content, "")
        self.assertEqual(score, 9.0)
        
        # Medium indicators
        content = "multiple customer touchpoints repetitive data entry"
        score = LeadScorer.calculate_automation_indicators_score(content, "")
        self.assertEqual(score, 7.0)
        
        # Low indicators
        content = "multiple customer touchpoints"
        score = LeadScorer.calculate_automation_indicators_score(content, "")
        self.assertEqual(score, 6.0)
        
        # No indicators
        score = LeadScorer.calculate_automation_indicators_score("", "")
        self.assertEqual(score, 5.0)
    
    def test_calculate_data_quality_score(self):
        """Test data quality scoring"""
        # Complete data
        complete_lead = {
            "email": "test@example.com",
            "linkedin": "https://linkedin.com/company/test",
            "company_size": "2-10 employees",
            "pain_points": "Needs automation"
        }
        score = LeadScorer.calculate_data_quality_score(complete_lead)
        self.assertEqual(score, 10.0)
        
        # Partial data
        partial_lead = {
            "email": "test@example.com",
            "company_size": "2-10 employees"
        }
        score = LeadScorer.calculate_data_quality_score(partial_lead)
        self.assertEqual(score, 8.0)
        
        # Minimal data
        minimal_lead = {}
        score = LeadScorer.calculate_data_quality_score(minimal_lead)
        self.assertEqual(score, 5.0)
    
    def test_calculate_fit_score(self):
        """Test overall fit score calculation"""
        # High-scoring lead
        high_score_lead = {
            "name": "Test Agency",
            "industry": "web design",
            "website": "https://example.com",
            "email": "test@example.com",
            "company_size": "solo entrepreneur",
            "pain_points": "multiple customer touchpoints repetitive data entry"
        }
        
        score = LeadScorer.calculate_fit_score(high_score_lead)
        self.assertGreaterEqual(score, 8.0)
        
        # Low-scoring lead
        low_score_lead = {
            "name": "Large Corp",
            "industry": "manufacturing",
            "website": "https://example.com",
            "company_size": "500+ employees"
        }
        
        score = LeadScorer.calculate_fit_score(low_score_lead)
        self.assertLessEqual(score, 5.0)

class TestDataProcessor(unittest.TestCase):
    """Test data processing functionality"""
    
    def test_clean_text(self):
        """Test text cleaning"""
        # Normal text
        self.assertEqual(DataProcessor.clean_text("  Test  Company  "), "Test Company")
        
        # Text with special characters
        self.assertEqual(DataProcessor.clean_text("Test@Company#123"), "TestCompany123")
        
        # Empty text
        self.assertEqual(DataProcessor.clean_text(""), "")
        self.assertEqual(DataProcessor.clean_text(None), "")
    
    def test_extract_email_from_text(self):
        """Test email extraction"""
        text = "Contact us at test@example.com or support@company.org"
        emails = DataProcessor.extract_email_from_text(text)
        self.assertEqual(emails, "test@example.com")
        
        # No email
        self.assertIsNone(DataProcessor.extract_email_from_text("No email here"))
        self.assertIsNone(DataProcessor.extract_email_from_text(""))
    
    def test_deduplicate_leads(self):
        """Test lead deduplication"""
        leads = [
            {"name": "Company A", "website": "https://a.com"},
            {"name": "Company B", "website": "https://b.com"},
            {"name": "Company A", "website": "https://a.com"},  # Duplicate
            {"name": "Company C", "website": "https://c.com"}
        ]
        
        unique_leads = DataProcessor.deduplicate_leads(leads)
        self.assertEqual(len(unique_leads), 3)
        
        # Check that duplicates are removed
        websites = [lead["website"] for lead in unique_leads]
        self.assertEqual(len(set(websites)), 3)
    
    def test_sort_leads_by_score(self):
        """Test lead sorting by score"""
        leads = [
            {"name": "Company A", "fit_score": 5.0},
            {"name": "Company B", "fit_score": 9.0},
            {"name": "Company C", "fit_score": 7.0}
        ]
        
        sorted_leads = DataProcessor.sort_leads_by_score(leads)
        self.assertEqual(sorted_leads[0]["fit_score"], 9.0)
        self.assertEqual(sorted_leads[1]["fit_score"], 7.0)
        self.assertEqual(sorted_leads[2]["fit_score"], 5.0)

class TestFileUtils(unittest.TestCase):
    """Test file utilities"""
    
    def test_save_leads_to_json(self):
        """Test JSON file saving"""
        leads = [
            {"name": "Test Company", "website": "https://example.com"},
            {"name": "Another Company", "website": "https://another.com"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name
        
        try:
            success = FileUtils.save_leads_to_json(leads, filename)
            self.assertTrue(success)
            
            # Verify file content
            with open(filename, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(len(saved_data), 2)
            self.assertEqual(saved_data[0]["name"], "Test Company")
            
        finally:
            os.unlink(filename)
    
    def test_save_leads_to_excel(self):
        """Test Excel file saving"""
        leads = [
            {"name": "Test Company", "website": "https://example.com"},
            {"name": "Another Company", "website": "https://another.com"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as f:
            filename = f.name
        
        try:
            success = FileUtils.save_leads_to_excel(leads, filename)
            self.assertTrue(success)
            
            # Verify file exists
            self.assertTrue(os.path.exists(filename))
            
        finally:
            os.unlink(filename)

class TestBaseScraper(unittest.TestCase):
    """Test base scraper functionality"""
    
    def setUp(self):
        self.scraper = BaseScraper()
    
    def test_setup_session(self):
        """Test session setup"""
        self.assertIsNotNone(self.scraper.session)
        self.assertIn("User-Agent", self.scraper.session.headers)
    
    def test_extract_lead_data(self):
        """Test lead data extraction"""
        raw_data = {
            "name": "  Test Company  ",
            "industry": "Technology",
            "website": "https://example.com",
            "email": "test@example.com",
            "company_size": "2-10 employees",
            "pain_points": "Needs automation",
            "data_source": "Test Source",
            "last_updated": "2024-01-01"
        }
        
        lead_data = self.scraper.extract_lead_data(raw_data)
        
        self.assertEqual(lead_data["name"], "Test Company")  # Cleaned
        self.assertEqual(lead_data["website"], "https://example.com")
        self.assertIn("fit_score", lead_data)
        self.assertIsInstance(lead_data["fit_score"], float)
    
    def tearDown(self):
        self.scraper.cleanup()

class TestLeadScraperOrchestrator(unittest.TestCase):
    """Test main orchestrator"""
    
    def setUp(self):
        self.orchestrator = LeadScraperOrchestrator()
    
    def test_setup_scrapers(self):
        """Test scraper initialization"""
        self.assertIn("clutch", self.orchestrator.scrapers)
        self.assertIn("product_hunt", self.orchestrator.scrapers)
        self.assertIn("shopify", self.orchestrator.scrapers)
        self.assertIn("linkedin", self.orchestrator.scrapers)
    
    def test_qualify_leads(self):
        """Test lead qualification"""
        # Add test leads
        self.orchestrator.all_leads = [
            {"name": "High Score", "fit_score": 9.0},
            {"name": "Low Score", "fit_score": 3.0},
            {"name": "Medium Score", "fit_score": 7.0}
        ]
        
        qualified = self.orchestrator.qualify_leads(min_score=7.0)
        
        self.assertEqual(len(qualified), 2)
        self.assertEqual(qualified[0]["name"], "High Score")  # Sorted by score
    
    def test_generate_summary_report(self):
        """Test report generation"""
        self.orchestrator.all_leads = [{"name": "Test", "fit_score": 8.0}]
        self.orchestrator.qualified_leads = [{"name": "Test", "fit_score": 8.0}]
        
        report = self.orchestrator.generate_summary_report()
        
        self.assertIn("timestamp", report)
        self.assertEqual(report["total_leads_scraped"], 1)
        self.assertEqual(report["qualified_leads"], 1)
        self.assertIn("sources_used", report)
    
    def tearDown(self):
        self.orchestrator.cleanup()

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDataValidator,
        TestLeadScorer,
        TestDataProcessor,
        TestFileUtils,
        TestBaseScraper,
        TestLeadScraperOrchestrator
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Running Xeinst AI Lead Scraper Tests")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    print("\n" + "=" * 50) 
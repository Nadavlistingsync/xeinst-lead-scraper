"""
Configuration file for the Xeinst AI Business Lead Scraper
"""

import os
from datetime import datetime

# Scraping Configuration
SCRAPING_CONFIG = {
    "delay_between_requests": 3,  # seconds
    "max_retries": 3,
    "timeout": 30,
    "user_agent_rotation": True,
    "respect_robots_txt": True,
    "max_leads_per_source": 50,
    "target_total_leads": 20
}

# Data Sources Configuration
DATA_SOURCES = {
    "agency_directories": {
        "clutch": {
            "base_url": "https://clutch.co",
            "search_paths": [
                "/agencies/web-designers",
                "/agencies/digital-marketers", 
                "/agencies/developers"
            ],
            "priority": 1
        },
        "upcity": {
            "base_url": "https://upcity.com",
            "search_paths": [
                "/top-web-design-companies",
                "/top-digital-marketing-agencies"
            ],
            "priority": 2
        },
        "goodfirms": {
            "base_url": "https://www.goodfirms.co",
            "search_paths": [
                "/web-design-companies",
                "/digital-marketing-agencies"
            ],
            "priority": 3
        }
    },
    "ecommerce_platforms": {
        "shopify": {
            "base_url": "https://www.shopify.com",
            "search_paths": ["/examples"],
            "priority": 1
        },
        "etsy": {
            "base_url": "https://www.etsy.com",
            "search_paths": ["/featured"],
            "priority": 2
        }
    },
    "startup_ecosystems": {
        "product_hunt": {
            "base_url": "https://www.producthunt.com",
            "search_paths": ["/topics/business-tools"],
            "priority": 1
        },
        "indie_hackers": {
            "base_url": "https://www.indiehackers.com",
            "search_paths": ["/products"],
            "priority": 2
        }
    }
}

# Lead Qualification Criteria
QUALIFICATION_CRITERIA = {
    "high_priority": {
        "score_range": (8, 10),
        "characteristics": [
            "solo_entrepreneur",
            "small_team_1_10",
            "ecommerce_100_plus_products",
            "agency_multiple_clients",
            "saas_customer_support",
            "service_appointment_scheduling"
        ]
    },
    "medium_priority": {
        "score_range": (5, 7),
        "characteristics": [
            "medium_business_11_50",
            "established_basic_automation",
            "local_business_growth_potential"
        ]
    },
    "low_priority": {
        "score_range": (1, 4),
        "characteristics": [
            "large_enterprise_50_plus",
            "advanced_automation_already",
            "non_profit_organization"
        ]
    }
}

# Automation Opportunity Indicators
AUTOMATION_INDICATORS = [
    "multiple_customer_touchpoints",
    "repetitive_data_entry",
    "high_customer_inquiries",
    "manual_appointment_scheduling",
    "basic_website_contact_forms",
    "social_media_regular_updates",
    "ecommerce_inventory_management",
    "service_booking_systems"
]

# Output Configuration
OUTPUT_CONFIG = {
    "format": "json",
    "filename": f"xeinst_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    "backup_format": "excel",
    "backup_filename": f"xeinst_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
}

# Scoring Weights
SCORING_WEIGHTS = {
    "company_size": 0.25,
    "automation_indicators": 0.30,
    "industry_relevance": 0.20,
    "data_quality": 0.15,
    "contact_availability": 0.10
}

# Industry Relevance Scores
INDUSTRY_SCORES = {
    "web_design": 9,
    "digital_marketing": 8,
    "ecommerce": 9,
    "saas": 8,
    "consulting": 7,
    "real_estate": 6,
    "healthcare": 5,
    "education": 6,
    "finance": 7,
    "retail": 8,
    "manufacturing": 6,
    "other": 5
}

# Error Handling
ERROR_CONFIG = {
    "log_errors": True,
    "continue_on_error": True,
    "max_consecutive_errors": 5,
    "error_log_file": "scraper_errors.log"
}

# Validation Rules
VALIDATION_RULES = {
    "required_fields": ["name", "industry", "website"],
    "email_pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "url_pattern": r'^https?://[^\s/$.?#].[^\s]*$',
    "min_name_length": 2,
    "max_name_length": 100
} 
# Xeinst AI Business Lead Scraper

An intelligent business lead generation system designed to identify high-value prospects for the Xeinst AI agent marketplace. This scraper targets businesses and individuals who would benefit from automation solutions to optimize operations, reduce manual tasks, or scale revenue.

## 🎯 Objective

Build an intelligent business lead scraper that identifies prospects likely to purchase automation agents to save time or grow revenue. The system focuses on quality over quantity, ensuring each lead meets specific qualification criteria.

## 🚀 Features

- **Multi-Source Scraping**: Scrapes from agency directories, e-commerce platforms, startup ecosystems, and professional networks
- **Intelligent Scoring**: Advanced lead qualification system with fit scoring (1-10 scale)
- **Data Validation**: Comprehensive validation of scraped data
- **Deduplication**: Automatic removal of duplicate leads
- **Quality Assurance**: Built-in quality checks and error handling
- **Multiple Output Formats**: JSON and Excel export options
- **Detailed Reporting**: Comprehensive scraping reports and analytics

## 📊 Target Profile

**Ideal leads exhibit these characteristics:**
- Small to medium businesses (1-50 employees)
- Solo entrepreneurs or small agencies
- E-commerce businesses with repetitive tasks
- B2B SaaS companies needing customer support automation
- Service-based businesses with high customer interaction
- Startups in growth phase with limited resources
- Local businesses with basic digital presence

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium-based scraping)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd xeinst-lead-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python main.py --help
   ```

## 🎮 Usage

### Basic Usage

Run the scraper with default settings:
```bash
python main.py
```

### Advanced Usage

```python
from main import LeadScraperOrchestrator

# Initialize orchestrator
orchestrator = LeadScraperOrchestrator()

# Run complete scraping process
results = orchestrator.run_complete_scraping(
    target_leads=20,    # Number of leads to scrape
    min_score=7.0       # Minimum fit score (1-10)
)

# Access results
print(f"Qualified leads: {len(orchestrator.qualified_leads)}")
```

### Configuration

Edit `config.py` to customize:
- Scraping delays and timeouts
- Data sources and priorities
- Scoring weights and criteria
- Output formats and filenames

## 📁 Project Structure

```
xeinst-lead-scraper/
├── main.py              # Main orchestrator and entry point
├── config.py            # Configuration settings
├── utils.py             # Utility functions and helpers
├── scrapers.py          # Specialized scrapers for each source
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── outputs/            # Generated files (created automatically)
    ├── xeinst_leads_*.json
    ├── xeinst_leads_*.xlsx
    └── scraping_report_*.json
```

## 🔧 Data Sources

### Agency Directories
- **Clutch.co**: Web design, digital marketing, and development agencies
- **UpCity**: Top web design and digital marketing companies
- **GoodFirms**: Web design and digital marketing agencies

### E-commerce Platforms
- **Shopify Examples**: Featured Shopify stores
- **Etsy**: Featured shops and sellers

### Startup Ecosystems
- **Product Hunt**: Business tools and SaaS products
- **Indie Hackers**: Independent developer products

### Professional Networks
- **LinkedIn**: Company pages and professional profiles

## 📊 Lead Qualification System

### Scoring Criteria (1-10 Scale)

**High Priority (Score 8-10):**
- Solo entrepreneurs or small teams (1-10 employees)
- E-commerce businesses with 100+ products
- Agencies handling multiple clients
- SaaS companies with customer support needs
- Service businesses with appointment scheduling

**Medium Priority (Score 5-7):**
- Medium-sized businesses (11-50 employees)
- Established companies with basic automation
- Local businesses with growth potential

**Low Priority (Score 1-4):**
- Large enterprises (50+ employees)
- Companies with advanced automation already
- Non-profit organizations

### Scoring Weights
- Company Size: 25%
- Automation Indicators: 30%
- Industry Relevance: 20%
- Data Quality: 15%
- Contact Availability: 10%

## 📋 Output Format

Each lead includes:
```json
{
  "name": "Business/Person Name",
  "industry": "Primary industry or niche",
  "website": "Main website URL",
  "linkedin": "LinkedIn profile/company URL (if available)",
  "email": "Contact email (if publicly available)",
  "company_size": "Estimated employee count or business size",
  "pain_points": "Identified automation opportunities (1-2 sentences)",
  "fit_score": "1-10 rating of how well they match Xeinst's ideal customer profile",
  "data_source": "Where this lead was discovered",
  "last_updated": "Date of data collection"
}
```

## 🔍 Automation Opportunity Indicators

The system looks for these signals that suggest automation needs:
- Multiple customer touchpoints
- Repetitive data entry tasks
- High volume of customer inquiries
- Manual appointment scheduling
- Basic website with contact forms
- Social media presence requiring regular updates
- E-commerce with inventory management
- Service delivery with booking systems

## ⚙️ Configuration Options

### Scraping Configuration
```python
SCRAPING_CONFIG = {
    "delay_between_requests": 3,  # seconds
    "max_retries": 3,
    "timeout": 30,
    "user_agent_rotation": True,
    "respect_robots_txt": True,
    "max_leads_per_source": 50,
    "target_total_leads": 20
}
```

### Industry Relevance Scores
```python
INDUSTRY_SCORES = {
    "web_design": 9,
    "digital_marketing": 8,
    "ecommerce": 9,
    "saas": 8,
    "consulting": 7,
    # ... more industries
}
```

## 🛡️ Ethical Considerations

- **Public Data Only**: Only scrapes publicly available information
- **Rate Limiting**: Implements intelligent delays between requests
- **Robots.txt Compliance**: Respects website robots.txt files
- **Terms of Service**: Follows website terms of service
- **Data Privacy**: Does not collect personal information without consent

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   # Reinstall Chrome driver
   pip uninstall webdriver-manager
   pip install webdriver-manager
   ```

2. **Rate Limiting**
   - Increase delay between requests in `config.py`
   - Use proxy rotation (advanced setup required)

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Optimization

### Tips for Better Results

1. **Adjust Scoring Weights**: Modify weights in `config.py` based on your specific needs
2. **Add Custom Sources**: Extend scrapers in `scrapers.py` for additional sources
3. **Fine-tune Delays**: Balance speed vs. reliability with request delays
4. **Use Proxies**: Implement proxy rotation for high-volume scraping

### Monitoring

- Check `scraper.log` for detailed operation logs
- Review `scraping_report_*.json` for performance metrics
- Monitor success rates and error patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Users are responsible for:
- Complying with website terms of service
- Respecting robots.txt files
- Following applicable laws and regulations
- Using scraped data responsibly

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the logs in `scraper.log`
3. Open an issue on GitHub
4. Contact the development team

---

**Built with ❤️ for the Xeinst AI community** 
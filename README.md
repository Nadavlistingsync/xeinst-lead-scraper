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
- **Database Integration**: Full database support with Supabase (PostgreSQL) and SQLite
- **Lead Management**: Complete CRUD operations for lead management
- **Search & Filtering**: Advanced search and filtering capabilities

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
- Supabase account (recommended) or local SQLite

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

3. **Configure database (Supabase recommended)**
   ```bash
   # Copy environment template
   cp env_example.txt .env
   
   # Edit .env with your Supabase credentials
   # Get these from your Supabase project dashboard
   ```

4. **Setup Supabase database**
   ```bash
   python supabase_setup.py
   ```

5. **Verify installation**
   ```bash
   python main.py --help
   ```

## 🗄️ Database Setup

### Supabase (Recommended)

1. **Create a Supabase project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Note your project URL and database password

2. **Configure environment variables**
   ```bash
   # In your .env file
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_DB_PASSWORD=your-database-password-here
   ```

3. **Run setup script**
   ```bash
   python supabase_setup.py
   ```

### SQLite (Local Development)

For local development, the system will automatically use SQLite if no Supabase credentials are provided.

## 🎮 Usage

### Basic Usage

Run the scraper with default settings:
```bash
python main.py
```

### Database Management

**View database statistics:**
```bash
python database_cli.py stats
```

**List leads:**
```bash
python database_cli.py list --limit 20 --min-score 7.0
```

**Search leads:**
```bash
python database_cli.py search "web design" --details
```

**Update lead status:**
```bash
python database_cli.py update 1 contacted --notes "Initial outreach sent"
```

**Export leads:**
```bash
python database_cli.py export --format csv --min-score 8.0
```

### Advanced Usage

```python
from main import LeadScraperOrchestrator

# Initialize orchestrator with database
orchestrator = LeadScraperOrchestrator(use_database=True)

# Run complete scraping process
results = orchestrator.run_complete_scraping(
    target_leads=20,
    min_score=7.0
)

# Get leads from database
leads = orchestrator.get_leads_from_database(
    limit=50,
    min_score=8.0,
    industry="web design"
)

# Search leads
search_results = orchestrator.search_leads_in_database("automation")
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
├── database.py          # Database models and operations
├── database_cli.py      # Database management CLI
├── supabase_setup.py    # Supabase setup script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── env_example.txt     # Environment variables template
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

## 📋 Database Schema

### Leads Table
```sql
CREATE TABLE leads (
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
    last_updated TIMESTAMP DEFAULT NOW(),
    is_contacted BOOLEAN DEFAULT FALSE,
    contact_date TIMESTAMP,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'new'
);
```

### Lead Statuses
- `new`: Freshly scraped lead
- `contacted`: Initial outreach made
- `qualified`: Lead shows interest
- `converted`: Lead became a customer
- `rejected`: Lead not interested

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

### Database Configuration
```python
# Environment variables
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_DB_PASSWORD=your-database-password
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
```

## 🛡️ Ethical Considerations

- **Public Data Only**: Only scrapes publicly available information
- **Rate Limiting**: Implements intelligent delays between requests
- **Robots.txt Compliance**: Respects website robots.txt files
- **Terms of Service**: Follows website terms of service
- **Data Privacy**: Does not collect personal information without consent

## 🐛 Troubleshooting

### Common Issues

1. **Supabase Connection Issues**
   ```bash
   # Check connection
   python supabase_setup.py check
   
   # Verify environment variables
   echo $SUPABASE_URL
   echo $SUPABASE_DB_PASSWORD
   ```

2. **Chrome Driver Issues**
   ```bash
   # Reinstall Chrome driver
   pip uninstall webdriver-manager
   pip install webdriver-manager
   ```

3. **Rate Limiting**
   - Increase delay between requests in `config.py`
   - Use proxy rotation (advanced setup required)

4. **Missing Dependencies**
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
5. **Database Indexing**: Ensure proper database indexes for large datasets

### Monitoring

- Check `scraper.log` for detailed operation logs
- Review `scraping_report_*.json` for performance metrics
- Monitor database statistics: `python database_cli.py stats`
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
3. Check database connection: `python supabase_setup.py check`
4. Open an issue on GitHub
5. Contact the development team

---

**Built with ❤️ for the Xeinst AI community** 
# Xeinst AI Business Lead Scraper

A comprehensive lead generation system for Xeinst AI, targeting businesses and developers who could benefit from AI automation solutions. The system automatically scrapes, qualifies, and manages leads from multiple sources with intelligent classification into business and developer categories.

## 🎯 Objective

Build an intelligent business lead scraper that identifies prospects likely to purchase automation agents to save time or grow revenue. The system focuses on quality over quantity, ensuring each lead meets specific qualification criteria.

## 🚀 Features

### Multi-Source Scraping
- **Clutch.co** - Digital agencies and service providers
- **Product Hunt** - Startups and innovative companies
- **Shopify** - E-commerce businesses
- **LinkedIn** - Professional companies and individuals

### Intelligent Lead Classification
- **Business Leads** - Companies and organizations with automation needs
- **Developer Leads** - Individual developers and freelancers interested in AI tools

### Advanced Lead Scoring
- Industry relevance analysis
- Pain point identification
- Automation opportunity assessment
- Company size and revenue indicators

### Database Management
- **Supabase PostgreSQL** integration (with SQLite fallback)
- Separate tables for business and developer leads
- Advanced filtering and search capabilities
- Lead status tracking and notes
- Export to JSON/CSV formats

## 📋 Requirements

- Python 3.11+
- Supabase account (optional, for cloud database)
- Chrome/Chromium browser (for Selenium scrapers)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Business
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp env_example.txt .env
# Edit .env with your configuration
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Supabase Configuration (Optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_DB_PASSWORD=your-database-password
SUPABASE_ANON_KEY=your-anon-key

# Database Configuration (Fallback)
DATABASE_URL=sqlite:///xeinst_leads.db

# Scraping Configuration
SCRAPING_DELAY=2
MAX_RETRIES=3
TIMEOUT=30

# Output Configuration
OUTPUT_DIR=./output
```

### Supabase Setup

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Note your project URL and database password

2. **Run Database Setup**
```bash
python supabase_setup.py
```

This will create:
- `business_leads` table for companies and organizations
- `developer_leads` table for individual developers
- Optimized indexes for performance
- Test data to verify functionality

## 🚀 Usage

### Basic Scraping

```bash
# Run scraper with default settings
python main.py

# Customize scraping parameters
python main.py --target 50 --min-score 8.0

# Skip database operations
python main.py --no-database
```

### Database Management

The system provides a comprehensive CLI for managing leads:

#### List Leads
```bash
# List business leads
python database_cli.py list-business --limit 20 --min-score 8.0

# List developer leads
python database_cli.py list-developers --limit 20 --experience-level Senior

# Filter by industry
python database_cli.py list-business --industry "Technology"

# Filter by status
python database_cli.py list-business --status "new"
```

#### Search Leads
```bash
# Search across all leads
python database_cli.py search "automation"

# Search specific lead types
python database_cli.py search "python" --type developer
python database_cli.py search "ecommerce" --type business
```

#### Update Leads
```bash
# Update business lead
python database_cli.py update 123 --type business --status contacted --notes "Initial outreach sent"

# Update developer lead
python database_cli.py update 456 --type developer --status qualified --skills "Python, AI, Automation"
```

#### View Statistics
```bash
# Get comprehensive database statistics
python database_cli.py stats
```

#### Export Data
```bash
# Export all leads to JSON
python database_cli.py export --type all --format json

# Export business leads to CSV
python database_cli.py export --type business --format csv

# Export both formats
python database_cli.py export --type developer --format both
```

## 📊 Database Schema

### Business Leads Table
```sql
business_leads (
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
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_contacted BOOLEAN DEFAULT FALSE,
    contact_date TIMESTAMP,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'new',
    annual_revenue VARCHAR(100),
    location VARCHAR(255),
    tech_stack TEXT,
    automation_needs TEXT,
    decision_maker VARCHAR(255)
)
```

### Developer Leads Table
```sql
developer_leads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(500) NOT NULL UNIQUE,
    linkedin VARCHAR(500),
    email VARCHAR(255),
    fit_score FLOAT NOT NULL,
    data_source VARCHAR(100) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_contacted BOOLEAN DEFAULT FALSE,
    contact_date TIMESTAMP,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'new',
    skills TEXT,
    experience_level VARCHAR(50),
    project_types TEXT,
    hourly_rate VARCHAR(100),
    availability VARCHAR(100),
    portfolio_url VARCHAR(500),
    github_url VARCHAR(500),
    automation_interest TEXT
)
```

## 🔍 Lead Classification Logic

The system automatically classifies leads using intelligent keyword analysis:

### Developer Indicators
- Keywords: developer, programmer, coder, freelancer, consultant
- Technologies: react, python, javascript, node.js, vue, angular
- Project types: full-stack, frontend, backend, mobile development
- Company size: solo, individual, freelancer

### Business Indicators
- Company names and organizations
- Industry classifications
- Business pain points
- Revenue and size indicators

## 📈 Output Files

The scraper generates several output files:

- `xeinst_leads_YYYYMMDD_HHMMSS_qualified.json` - All qualified leads
- `xeinst_leads_YYYYMMDD_HHMMSS_business.json` - Business leads only
- `xeinst_leads_YYYYMMDD_HHMMSS_developers.json` - Developer leads only
- `xeinst_leads_YYYYMMDD_HHMMSS_report.json` - Comprehensive summary report

## 🛡️ Error Handling

- Automatic retry mechanisms for failed requests
- Graceful handling of rate limiting
- Comprehensive logging for debugging
- Data validation and deduplication

## 🔧 Customization

### Adding New Data Sources

1. Create a new scraper class in `scrapers.py`
2. Implement the required methods
3. Add to the orchestrator in `main.py`

### Modifying Lead Scoring

Edit the scoring logic in `utils.py` to adjust:
- Industry weights
- Pain point scoring
- Automation opportunity assessment

### Database Schema Changes

1. Update the models in `database.py`
2. Run database migrations
3. Update the CLI commands if needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues:
- Check the logs for detailed error messages
- Review the database setup instructions
- Ensure all environment variables are configured correctly

## 🔄 Changelog

### v2.0.0
- Added separate business and developer lead classification
- Implemented Supabase PostgreSQL integration
- Enhanced CLI with type-specific commands
- Improved lead scoring and validation
- Added comprehensive database management features

### v1.0.0
- Initial release with multi-source scraping
- Basic lead qualification and scoring
- SQLite database integration
- JSON/Excel export functionality

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
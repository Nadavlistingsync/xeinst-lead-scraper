"""
Database CLI for Xeinst AI Business Lead Scraper
Manages both business and developer leads
"""

import argparse
import json
import sys
from datetime import datetime
from typing import List, Dict, Any
from database import DatabaseManager, LeadType, BusinessLead, DeveloperLead
from utils import logger

def print_leads(leads: List[Any], lead_type: str):
    """Print leads in a formatted table"""
    if not leads:
        print(f"No {lead_type} leads found.")
        return
    
    print(f"\n📊 {lead_type.title()} Leads ({len(leads)} found):")
    print("=" * 100)
    
    for lead in leads:
        print(f"ID: {lead.id}")
        print(f"Name: {lead.name}")
        print(f"Website: {lead.website}")
        print(f"Fit Score: {lead.fit_score}")
        print(f"Status: {lead.status}")
        print(f"Data Source: {lead.data_source}")
        
        if isinstance(lead, BusinessLead):
            print(f"Industry: {lead.industry}")
            print(f"Company Size: {lead.company_size}")
            if lead.pain_points:
                print(f"Pain Points: {lead.pain_points[:100]}...")
        elif isinstance(lead, DeveloperLead):
            print(f"Skills: {lead.skills}")
            print(f"Experience: {lead.experience_level}")
            if lead.automation_interest:
                print(f"Automation Interest: {lead.automation_interest[:100]}...")
        
        print(f"Contacted: {'Yes' if lead.is_contacted else 'No'}")
        if lead.notes:
            print(f"Notes: {lead.notes[:100]}...")
        print("-" * 100)

def list_business_leads(db_manager: DatabaseManager, args):
    """List business leads with optional filters"""
    leads = db_manager.get_business_leads(
        limit=args.limit,
        offset=args.offset,
        min_score=args.min_score,
        industry=args.industry,
        status=args.status,
        data_source=args.data_source
    )
    print_leads(leads, "business")

def list_developer_leads(db_manager: DatabaseManager, args):
    """List developer leads with optional filters"""
    leads = db_manager.get_developer_leads(
        limit=args.limit,
        offset=args.offset,
        min_score=args.min_score,
        experience_level=args.experience_level,
        status=args.status,
        data_source=args.data_source
    )
    print_leads(leads, "developer")

def search_leads(db_manager: DatabaseManager, args):
    """Search leads across both tables"""
    lead_type = None
    if args.type == 'business':
        lead_type = LeadType.BUSINESS
    elif args.type == 'developer':
        lead_type = LeadType.DEVELOPER
    
    leads = db_manager.search_leads(
        search_term=args.term,
        lead_type=lead_type,
        limit=args.limit
    )
    
    # Separate business and developer leads for display
    business_leads = [lead for lead in leads if isinstance(lead, BusinessLead)]
    developer_leads = [lead for lead in leads if isinstance(lead, DeveloperLead)]
    
    if business_leads:
        print_leads(business_leads, "business")
    
    if developer_leads:
        print_leads(developer_leads, "developer")
    
    if not business_leads and not developer_leads:
        print(f"No leads found matching '{args.term}'")

def update_lead(db_manager: DatabaseManager, args):
    """Update a lead by ID"""
    lead_type = LeadType.BUSINESS if args.type == 'business' else LeadType.DEVELOPER
    
    # Get current lead data
    lead = db_manager.get_lead_by_id(args.id, lead_type)
    if not lead:
        print(f"❌ Lead with ID {args.id} not found")
        return
    
    # Prepare update data
    update_data = {}
    
    if args.status:
        update_data['status'] = args.status
    if args.notes:
        update_data['notes'] = args.notes
    if args.contacted:
        update_data['is_contacted'] = True
        update_data['contact_date'] = datetime.utcnow()
    
    # Type-specific updates
    if isinstance(lead, BusinessLead):
        if args.industry:
            update_data['industry'] = args.industry
        if args.company_size:
            update_data['company_size'] = args.company_size
        if args.pain_points:
            update_data['pain_points'] = args.pain_points
    elif isinstance(lead, DeveloperLead):
        if args.skills:
            update_data['skills'] = args.skills
        if args.experience_level:
            update_data['experience_level'] = args.experience_level
        if args.automation_interest:
            update_data['automation_interest'] = args.automation_interest
    
    # Perform update
    if isinstance(lead, BusinessLead):
        success = db_manager.update_business_lead(args.id, update_data)
    else:
        success = db_manager.update_developer_lead(args.id, update_data)
    
    if success:
        print(f"✅ Updated {lead_type.value} lead ID {args.id}")
    else:
        print(f"❌ Failed to update {lead_type.value} lead ID {args.id}")

def show_statistics(db_manager: DatabaseManager):
    """Show database statistics"""
    stats = db_manager.get_statistics()
    
    if not stats:
        print("❌ Failed to get statistics")
        return
    
    print("\n📈 Database Statistics")
    print("=" * 50)
    
    # Business leads stats
    business_stats = stats.get('business_leads', {})
    print(f"\n🏢 Business Leads:")
    print(f"   Total: {business_stats.get('total', 0)}")
    print(f"   High Score (8+): {business_stats.get('high_score', 0)}")
    print(f"   Contacted: {business_stats.get('contacted', 0)}")
    
    industry_dist = business_stats.get('industry_distribution', {})
    if industry_dist:
        print(f"   Industry Distribution:")
        for industry, count in sorted(industry_dist.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"     {industry}: {count}")
    
    # Developer leads stats
    developer_stats = stats.get('developer_leads', {})
    print(f"\n👨‍💻 Developer Leads:")
    print(f"   Total: {developer_stats.get('total', 0)}")
    print(f"   High Score (8+): {developer_stats.get('high_score', 0)}")
    print(f"   Contacted: {developer_stats.get('contacted', 0)}")
    
    experience_dist = developer_stats.get('experience_distribution', {})
    if experience_dist:
        print(f"   Experience Distribution:")
        for level, count in sorted(experience_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"     {level}: {count}")
    
    print(f"\n📊 Total Leads: {stats.get('total_leads', 0)}")

def export_leads(db_manager: DatabaseManager, args):
    """Export leads to JSON or CSV"""
    # Get leads based on type
    if args.type == 'business':
        leads = db_manager.get_business_leads(limit=args.limit)
    elif args.type == 'developer':
        leads = db_manager.get_developer_leads(limit=args.limit)
    else:
        # Export both types
        business_leads = db_manager.get_business_leads(limit=args.limit)
        developer_leads = db_manager.get_developer_leads(limit=args.limit)
        leads = business_leads + developer_leads
    
    if not leads:
        print(f"No {args.type} leads to export")
        return
    
    # Convert to dictionary format
    leads_data = db_manager.export_leads_to_dict(leads)
    
    # Export to JSON
    if args.format == 'json' or args.format == 'both':
        filename = f"xeinst_{args.type}_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(leads_data, f, indent=2, default=str)
        print(f"✅ Exported {len(leads_data)} leads to {filename}")
    
    # Export to CSV
    if args.format == 'csv' or args.format == 'both':
        import csv
        filename = f"xeinst_{args.type}_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if leads_data:
            fieldnames = leads_data[0].keys()
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(leads_data)
            print(f"✅ Exported {len(leads_data)} leads to {filename}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Xeinst AI Lead Scraper Database CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List business leads command
    list_business_parser = subparsers.add_parser('list-business', help='List business leads')
    list_business_parser.add_argument('--limit', type=int, default=50, help='Number of leads to show')
    list_business_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    list_business_parser.add_argument('--min-score', type=float, help='Minimum fit score')
    list_business_parser.add_argument('--industry', help='Filter by industry')
    list_business_parser.add_argument('--status', help='Filter by status')
    list_business_parser.add_argument('--data-source', help='Filter by data source')
    
    # List developer leads command
    list_dev_parser = subparsers.add_parser('list-developers', help='List developer leads')
    list_dev_parser.add_argument('--limit', type=int, default=50, help='Number of leads to show')
    list_dev_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    list_dev_parser.add_argument('--min-score', type=float, help='Minimum fit score')
    list_dev_parser.add_argument('--experience-level', help='Filter by experience level')
    list_dev_parser.add_argument('--status', help='Filter by status')
    list_dev_parser.add_argument('--data-source', help='Filter by data source')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search leads')
    search_parser.add_argument('term', help='Search term')
    search_parser.add_argument('--type', choices=['business', 'developer'], help='Search specific type')
    search_parser.add_argument('--limit', type=int, default=50, help='Number of results')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a lead')
    update_parser.add_argument('id', type=int, help='Lead ID')
    update_parser.add_argument('--type', choices=['business', 'developer'], required=True, help='Lead type')
    update_parser.add_argument('--status', help='New status')
    update_parser.add_argument('--notes', help='Notes')
    update_parser.add_argument('--contacted', action='store_true', help='Mark as contacted')
    
    # Business-specific update fields
    update_parser.add_argument('--industry', help='Industry (business only)')
    update_parser.add_argument('--company-size', help='Company size (business only)')
    update_parser.add_argument('--pain-points', help='Pain points (business only)')
    
    # Developer-specific update fields
    update_parser.add_argument('--skills', help='Skills (developer only)')
    update_parser.add_argument('--experience-level', help='Experience level (developer only)')
    update_parser.add_argument('--automation-interest', help='Automation interest (developer only)')
    
    # Statistics command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export leads')
    export_parser.add_argument('--type', choices=['business', 'developer', 'all'], default='all', help='Type to export')
    export_parser.add_argument('--format', choices=['json', 'csv', 'both'], default='json', help='Export format')
    export_parser.add_argument('--limit', type=int, default=1000, help='Number of leads to export')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Execute command
        if args.command == 'list-business':
            list_business_leads(db_manager, args)
        elif args.command == 'list-developers':
            list_developer_leads(db_manager, args)
        elif args.command == 'search':
            search_leads(db_manager, args)
        elif args.command == 'update':
            update_lead(db_manager, args)
        elif args.command == 'stats':
            show_statistics(db_manager)
        elif args.command == 'export':
            export_leads(db_manager, args)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            
    except Exception as e:
        logger.error(f"CLI error: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
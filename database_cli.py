"""
Command-line interface for database operations
"""

import argparse
import json
from datetime import datetime
from typing import List, Dict, Any

from database import create_database_manager
from utils import logger

def display_leads(leads: List[Dict[str, Any]], show_details: bool = False):
    """Display leads in a formatted way"""
    if not leads:
        print("No leads found.")
        return
    
    print(f"\n📋 Found {len(leads)} leads:")
    print("=" * 80)
    
    for i, lead in enumerate(leads, 1):
        print(f"{i}. {lead['name']} - Score: {lead['fit_score']}")
        print(f"   Industry: {lead['industry']}")
        print(f"   Website: {lead['website']}")
        print(f"   Status: {lead['status']}")
        
        if show_details:
            if lead.get('email'):
                print(f"   Email: {lead['email']}")
            if lead.get('linkedin'):
                print(f"   LinkedIn: {lead['linkedin']}")
            if lead.get('company_size'):
                print(f"   Company Size: {lead['company_size']}")
            if lead.get('pain_points'):
                print(f"   Pain Points: {lead['pain_points']}")
            if lead.get('notes'):
                print(f"   Notes: {lead['notes']}")
            if lead.get('contact_date'):
                print(f"   Contact Date: {lead['contact_date']}")
        
        print()

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Xeinst AI Lead Database Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List leads command
    list_parser = subparsers.add_parser('list', help='List leads from database')
    list_parser.add_argument('--limit', type=int, default=20, help='Number of leads to show')
    list_parser.add_argument('--min-score', type=float, help='Minimum fit score')
    list_parser.add_argument('--industry', type=str, help='Filter by industry')
    list_parser.add_argument('--status', type=str, help='Filter by status')
    list_parser.add_argument('--details', action='store_true', help='Show detailed information')
    
    # Search leads command
    search_parser = subparsers.add_parser('search', help='Search leads')
    search_parser.add_argument('term', type=str, help='Search term')
    search_parser.add_argument('--limit', type=int, default=20, help='Number of results to show')
    search_parser.add_argument('--details', action='store_true', help='Show detailed information')
    
    # Get lead by ID command
    get_parser = subparsers.add_parser('get', help='Get lead by ID')
    get_parser.add_argument('id', type=int, help='Lead ID')
    
    # Update lead command
    update_parser = subparsers.add_parser('update', help='Update lead status')
    update_parser.add_argument('id', type=int, help='Lead ID')
    update_parser.add_argument('status', type=str, choices=['new', 'contacted', 'qualified', 'converted', 'rejected'], help='New status')
    update_parser.add_argument('--notes', type=str, help='Add notes')
    
    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export leads to file')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.add_argument('--filename', type=str, help='Output filename')
    export_parser.add_argument('--min-score', type=float, help='Minimum fit score')
    export_parser.add_argument('--industry', type=str, help='Filter by industry')
    export_parser.add_argument('--status', type=str, help='Filter by status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize database manager
        db_manager = create_database_manager()
        
        if args.command == 'list':
            leads = db_manager.get_leads(
                limit=args.limit,
                min_score=args.min_score,
                industry=args.industry,
                status=args.status
            )
            display_leads(db_manager.export_leads_to_dict(leads), args.details)
        
        elif args.command == 'search':
            leads = db_manager.search_leads(args.term, args.limit)
            display_leads(db_manager.export_leads_to_dict(leads), args.details)
        
        elif args.command == 'get':
            lead = db_manager.get_lead_by_id(args.id)
            if lead:
                display_leads([db_manager.export_leads_to_dict([lead])[0]], True)
            else:
                print(f"Lead with ID {args.id} not found.")
        
        elif args.command == 'update':
            success = db_manager.update_lead(args.id, {
                'status': args.status,
                'notes': args.notes
            })
            if success:
                print(f"✅ Lead {args.id} updated successfully")
            else:
                print(f"❌ Failed to update lead {args.id}")
        
        elif args.command == 'stats':
            stats = db_manager.get_statistics()
            print("\n📊 Database Statistics:")
            print("=" * 40)
            print(f"Total leads: {stats.get('total_leads', 0)}")
            print(f"High score leads (8+): {stats.get('high_score_leads', 0)}")
            print(f"Contacted leads: {stats.get('contacted_leads', 0)}")
            
            if stats.get('industry_distribution'):
                print(f"\n🏭 Industry Distribution:")
                for industry, count in stats['industry_distribution'].items():
                    print(f"  {industry}: {count}")
            
            if stats.get('status_distribution'):
                print(f"\n📈 Status Distribution:")
                for status, count in stats['status_distribution'].items():
                    print(f"  {status}: {count}")
        
        elif args.command == 'export':
            leads = db_manager.get_leads(
                limit=1000,  # Export all leads
                min_score=args.min_score,
                industry=args.industry,
                status=args.status
            )
            
            if not leads:
                print("No leads to export.")
                return
            
            lead_data = db_manager.export_leads_to_dict(leads)
            
            if args.format == 'json':
                filename = args.filename or f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(lead_data, f, indent=2)
                print(f"✅ Exported {len(lead_data)} leads to {filename}")
            
            elif args.format == 'csv':
                import csv
                filename = args.filename or f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'w', newline='') as f:
                    if lead_data:
                        writer = csv.DictWriter(f, fieldnames=lead_data[0].keys())
                        writer.writeheader()
                        writer.writerows(lead_data)
                print(f"✅ Exported {len(lead_data)} leads to {filename}")
    
    except Exception as e:
        logger.error(f"Error in CLI: {str(e)}")
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 
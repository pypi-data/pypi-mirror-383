#!/usr/bin/env python3
"""
CLI tool for managing BDD test status overrides and bug tracking
"""
import argparse
import sys
from pathlib import Path
from .status_manager import TestStatusManager


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="BDD Test Status Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Override a failed test as passed with exception
  bdd-status override "Failed Login Test" passed "Known issue - JIRA-123 in progress"
  
  # Assign bug ID to a failed test
  bdd-status bug "Shopping Cart Error" JIRA-456 "Cart calculation bug" --priority High
  
  # List all overrides and bugs
  bdd-status list
  
  # Remove an override
  bdd-status remove-override "Failed Login Test"
  
  # Update bug status
  bdd-status update-bug "Shopping Cart Error" Fixed
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Override command
    override_parser = subparsers.add_parser('override', help='Override test status')
    override_parser.add_argument('test_name', help='Test name to override')
    override_parser.add_argument('new_status', choices=['passed', 'failed', 'skipped'], 
                               help='New status for the test')
    override_parser.add_argument('reason', help='Reason for the override')
    override_parser.add_argument('--user', default='CLI User', help='User making the override')
    
    # Bug assignment command
    bug_parser = subparsers.add_parser('bug', help='Assign bug ID to test')
    bug_parser.add_argument('test_name', help='Test name to assign bug to')
    bug_parser.add_argument('bug_id', help='Bug ID (e.g., JIRA-123)')
    bug_parser.add_argument('description', help='Bug description')
    bug_parser.add_argument('--priority', choices=['Low', 'Medium', 'High', 'Critical'], 
                          default='Medium', help='Bug priority')
    bug_parser.add_argument('--user', default='CLI User', help='User assigning the bug')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all overrides and bugs')
    list_parser.add_argument('--type', choices=['overrides', 'bugs', 'all'], 
                           default='all', help='What to list')
    
    # Remove override command
    remove_override_parser = subparsers.add_parser('remove-override', help='Remove status override')
    remove_override_parser.add_argument('test_name', help='Test name to remove override from')
    
    # Remove bug command
    remove_bug_parser = subparsers.add_parser('remove-bug', help='Remove bug assignment')
    remove_bug_parser.add_argument('test_name', help='Test name to remove bug from')
    
    # Update bug status command
    update_bug_parser = subparsers.add_parser('update-bug', help='Update bug status')
    update_bug_parser.add_argument('test_name', help='Test name')
    update_bug_parser.add_argument('status', choices=['Open', 'In Progress', 'Fixed', 'Closed'], 
                                  help='New bug status')
    
    # Clear all command
    clear_parser = subparsers.add_parser('clear', help='Clear all overrides and bugs')
    clear_parser.add_argument('--confirm', action='store_true', 
                            help='Confirm clearing all data')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize status manager
    status_manager = TestStatusManager()
    
    try:
        if args.command == 'override':
            handle_override(status_manager, args)
        elif args.command == 'bug':
            handle_bug_assignment(status_manager, args)
        elif args.command == 'list':
            handle_list(status_manager, args)
        elif args.command == 'remove-override':
            handle_remove_override(status_manager, args)
        elif args.command == 'remove-bug':
            handle_remove_bug(status_manager, args)
        elif args.command == 'update-bug':
            handle_update_bug(status_manager, args)
        elif args.command == 'clear':
            handle_clear(status_manager, args)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_override(status_manager, args):
    """Handle status override command"""
    # Determine original status (assume failed if overriding to passed)
    original_status = 'failed' if args.new_status == 'passed' else 'passed'
    
    status_manager.override_test_status(
        args.test_name, 
        original_status, 
        args.new_status, 
        args.reason, 
        args.user
    )
    
    print(f"✅ Status override applied:")
    print(f"   Test: {args.test_name}")
    print(f"   Status: {original_status} → {args.new_status}")
    print(f"   Reason: {args.reason}")
    print(f"   User: {args.user}")


def handle_bug_assignment(status_manager, args):
    """Handle bug assignment command"""
    status_manager.assign_bug_id(
        args.test_name,
        args.bug_id,
        args.description,
        args.priority,
        args.user
    )
    
    print(f"🐛 Bug assigned:")
    print(f"   Test: {args.test_name}")
    print(f"   Bug ID: {args.bug_id}")
    print(f"   Priority: {args.priority}")
    print(f"   Description: {args.description}")
    print(f"   User: {args.user}")


def handle_list(status_manager, args):
    """Handle list command"""
    if args.type in ['overrides', 'all']:
        overrides = status_manager.get_all_overrides()
        if overrides:
            print("📋 Status Overrides:")
            print("-" * 60)
            for key, override in overrides.items():
                print(f"Test: {override['test_name']}")
                print(f"  Status: {override['original_status']} → {override['new_status']}")
                print(f"  Reason: {override['reason']}")
                print(f"  User: {override['user']}")
                print(f"  Date: {override['timestamp']}")
                print()
        else:
            print("No status overrides found.")
    
    if args.type in ['bugs', 'all']:
        bugs = status_manager.get_all_bugs()
        if bugs:
            print("🐛 Bug Tracking:")
            print("-" * 60)
            for key, bug in bugs.items():
                print(f"Test: {bug['test_name']}")
                print(f"  Bug ID: {bug['bug_id']}")
                print(f"  Priority: {bug['priority']}")
                print(f"  Status: {bug['status']}")
                print(f"  Description: {bug['description']}")
                print(f"  User: {bug['user']}")
                print(f"  Date: {bug['timestamp']}")
                print()
        else:
            print("No bug assignments found.")


def handle_remove_override(status_manager, args):
    """Handle remove override command"""
    status_manager.remove_override(args.test_name)
    print(f"✅ Status override removed for: {args.test_name}")


def handle_remove_bug(status_manager, args):
    """Handle remove bug command"""
    status_manager.remove_bug(args.test_name)
    print(f"✅ Bug assignment removed for: {args.test_name}")


def handle_update_bug(status_manager, args):
    """Handle update bug status command"""
    status_manager.update_bug_status(args.test_name, args.status)
    print(f"✅ Bug status updated:")
    print(f"   Test: {args.test_name}")
    print(f"   New Status: {args.status}")


def handle_clear(status_manager, args):
    """Handle clear all command"""
    if not args.confirm:
        print("⚠️  This will clear ALL status overrides and bug assignments.")
        print("Use --confirm to proceed.")
        return
    
    # Clear by removing the files
    config_dir = Path(".bdd_status")
    if config_dir.exists():
        for file in config_dir.glob("*.json"):
            file.unlink()
        print("✅ All status overrides and bug assignments cleared.")
    else:
        print("No data to clear.")


if __name__ == "__main__":
    sys.exit(main())
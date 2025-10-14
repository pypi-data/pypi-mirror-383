"""
Command-line interface for YOPmail client.

This module provides a CLI entry point for the YOPmail client,
allowing users to interact with YOPmail services from the command line.
"""

import argparse
import logging
import sys
from typing import List, Optional

from .client import YOPMailClient
from .utils import Message


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_messages(messages: List[Message], show_details: bool = False) -> None:
    """Print messages in a formatted way."""
    if not messages:
        print("No messages found.")
        return
    
    print(f"Found {len(messages)} message(s):")
    print("-" * 50)
    
    for i, msg in enumerate(messages, 1):
        print(f"{i}. Subject: {msg.subject}")
        if show_details:
            print(f"   ID: {msg.id}")
            print(f"   Sender: {msg.sender or 'Unknown'}")
            print(f"   Time: {msg.time or 'Unknown'}")
        print()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="YOPmail Client - Interact with YOPmail disposable email service"
    )
    
    parser.add_argument(
        "mailbox",
        help="Mailbox name (without @yopmail.com)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List messages in inbox"
    )
    
    parser.add_argument(
        "--fetch", "-f",
        type=str,
        metavar="MESSAGE_ID",
        help="Fetch specific message by ID"
    )
    
    parser.add_argument(
        "--details", "-d",
        action="store_true",
        help="Show detailed message information"
    )
    
    parser.add_argument(
        "--page", "-p",
        type=int,
        default=1,
        help="Page number for message listing (default: 1)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize client
        config = {"timeout": args.timeout}
        client = YOPMailClient(args.mailbox, config=config)
        
        with client:
            # Open inbox
            print(f"Opening inbox for {args.mailbox}@yopmail.com...")
            client.open_inbox()
            
            if args.list:
                # List messages
                messages = client.list_messages(page=args.page)
                print_messages(messages, show_details=args.details)
                
            elif args.fetch:
                # Fetch specific message
                print(f"Fetching message {args.fetch}...")
                content = client.fetch_message(args.fetch)
                print(f"Message content ({len(content)} characters):")
                print("-" * 50)
                print(content[:500] + "..." if len(content) > 500 else content)
                
            else:
                # Default: show inbox info
                info = client.get_inbox_info()
                print(f"Inbox for {info['mailbox']}@yopmail.com:")
                print(f"Messages: {info['message_count']}")
                
                if info['has_messages']:
                    print("\nRecent messages:")
                    for msg in info['messages'][:5]:  # Show first 5
                        print(f"  - {msg['subject']} (from: {msg['sender'] or 'Unknown'})")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Command Line Interface for LLM Conversation Parser
"""

import argparse
import sys
import os
from pathlib import Path
from .parser import LLMConversationParser


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Parse LLM conversation JSON files into RAG-optimized format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single conversation file
  %(prog)s parse conversations.json
  
  # Parse multiple files and save to custom directory
  %(prog)s parse file1.json file2.json --output parsed_data/
  
  # Parse with specific LLM type (auto-detection if not specified)
  %(prog)s parse conversations.json --llm-type claude
  
  # Parse and save in CSV format
  %(prog)s parse conversations.json --format csv

Supported LLM Types:
  - claude: Claude conversation exports
  - gpt: ChatGPT conversation exports  
  - grok: Grok conversation exports

The parser automatically detects the LLM type based on the JSON structure,
but you can explicitly specify it using the --llm-type option.
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', 
                                        help='Parse conversation files into RAG-optimized format',
                                        description='Parse LLM conversation JSON files and convert them into a structured format optimized for RAG (Retrieval-Augmented Generation) applications.')
    parse_parser.add_argument('files', nargs='+', 
                             help='JSON files to parse (supports multiple files)')
    parse_parser.add_argument('--output', '-o', default='parsed_data', 
                             help='Output directory for parsed files (default: parsed_data)')
    parse_parser.add_argument('--llm-type', choices=['claude', 'gpt', 'grok'],
                             help='Specify LLM type explicitly (auto-detection if not provided)')
    parse_parser.add_argument('--format', choices=['json', 'csv'], default='json',
                             help='Output format for parsed data (default: json)')
    
    args = parser.parse_args()
    
    if args.command == 'parse':
        parse_files(args)
    else:
        parser.print_help()


def parse_files(args):
    """Parse conversation files"""
    try:
        print("LLM Conversation Parser")
        print("=" * 50)
        
        # Initialize parser
        llm_parser = LLMConversationParser()
        print("Parser initialized successfully")
        
        # Check if files exist
        print(f"Checking {len(args.files)} file(s)...")
        for file_path in args.files:
            if not os.path.exists(file_path):
                print(f"Error: File not found: {file_path}")
                print("Please check the file path and try again.")
                sys.exit(1)
        print("All files found")
        
        # Parse files
        if len(args.files) == 1:
            # Single file
            print(f"\nParsing single file: {args.files[0]}")
            data = llm_parser.parse_file(args.files[0], args.llm_type)
            print(f"Successfully parsed {len(data)} conversations")
            
            # Save single file
            output_path = os.path.join(args.output, "parsed_conversations.json")
            os.makedirs(args.output, exist_ok=True)
            llm_parser.save_parsed_data(data, output_path)
            print(f"Single file saved to: {output_path}")
            
        else:
            # Multiple files
            print(f"\nParsing {len(args.files)} files...")
            data_by_llm = llm_parser.parse_multiple_files(args.files)
            
            total_conversations = sum(len(data) for data in data_by_llm.values())
            print(f"Successfully parsed {total_conversations} conversations total")
            
            # Save by LLM type
            llm_parser.save_parsed_data_by_llm(data_by_llm, args.output)
            print(f"Files saved by LLM type to: {args.output}/")
        
        print(f"\nAll results saved to: {args.output}/")
        print("Parsing completed successfully!")
        
    except Exception as e:
        print(f"\nError occurred during parsing: {str(e)}")
        print("Please check your input files and try again.")
        print("For help, run: llm-conversation-parser --help")
        sys.exit(1)


if __name__ == "__main__":
    main()

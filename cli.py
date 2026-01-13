#!/usr/bin/env python3
"""
Git-to-LLM Toolkit CLI
Unified command-line interface for the entire toolkit
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Git-to-LLM Toolkit: Analyze repositories and integrate LLM responses with Git",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  git-llm convert /path/to/repo                    # Convert repo to LLM format
  git-llm prompt generate --type code-review       # Generate code review prompt
  git-llm process llm_response.json --apply        # Process LLM response
  git-llm workflow /path/to/repo --full            # Run complete workflow
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert repository to LLM format')
    convert_parser.add_argument('repo_path', help='Path to git repository')
    convert_parser.add_argument('-o', '--output', default='llm_analysis', help='Output directory')
    convert_parser.add_argument('--max-size', type=int, default=1, help='Max file size in MB')
    convert_parser.add_argument('--include-docs', action='store_true', help='Include documentation')
    convert_parser.add_argument('--no-sanitize', action='store_true', help='Skip sanitization')
    
    # Prompt command
    prompt_parser = subparsers.add_parser('prompt', help='Generate prompts for LLM')
    prompt_parser.add_argument('action', choices=['generate', 'list', 'view'], help='Prompt action')
    prompt_parser.add_argument('--type', help='Prompt type (code-review, bug-fix, etc.)')
    prompt_parser.add_argument('--output', help='Output file for generated prompt')
    prompt_parser.add_argument('--repo', help='Repository path for context')
    prompt_parser.add_argument('--custom', help='Custom request text')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process LLM response')
    process_parser.add_argument('response_file', help='LLM response file')
    process_parser.add_argument('--repo', default='.', help='Repository path')
    process_parser.add_argument('--apply', action='store_true', help='Apply patches')
    process_parser.add_argument('--dry-run', action='store_true', help='Dry run only')
    process_parser.add_argument('--create-branch', help='Create branch for changes')
    process_parser.add_argument('--validate-only', action='store_true', help='Only validate')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run complete workflow')
    workflow_parser.add_argument('repo_path', help='Repository path')
    workflow_parser.add_argument('--type', default='code-review', help='Workflow type')
    workflow_parser.add_argument('--output', default='llm_workflow', help='Output directory')
    workflow_parser.add_argument('--apply', action='store_true', help='Auto-apply changes')
    workflow_parser.add_argument('--full', action='store_true', help='Full analysis workflow')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure toolkit')
    config_parser.add_argument('--list', action='store_true', help='List configuration')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set config value')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Import modules based on command
    if args.command == 'convert':
        from git2llm.main import convert_repository
        convert_repository(args)
    
    elif args.command == 'prompt':
        from prompts.manager import PromptManager
        manager = PromptManager()
        
        if args.action == 'generate':
            if not args.type:
                print("Error: --type is required for generate action")
                prompt_parser.print_help()
                sys.exit(1)
            manager.generate_prompt(args.type, args.output, args.repo, args.custom)
        
        elif args.action == 'list':
            manager.list_prompts()
        
        elif args.action == 'view':
            if not args.type:
                print("Error: --type is required for view action")
                prompt_parser.print_help()
                sys.exit(1)
            manager.view_prompt(args.type)
    
    elif args.command == 'process':
        from llm2git.main import process_llm_response
        process_llm_response(args)
    
    elif args.command == 'workflow':
        from workflow import run_workflow
        run_workflow(args)
    
    elif args.command == 'config':
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        
        if args.list:
            config.list_config()
        elif args.set:
            config.set_config(args.set[0], args.set[1])
        else:
            config_parser.print_help()

if __name__ == '__main__':
    main()

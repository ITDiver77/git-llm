# Git-to-LLM Toolkit

A comprehensive Python toolkit for converting Git repositories to LLM-optimized formats and integrating LLM responses back into Git workflows.

## Features

- **Git2LLM**: Convert repositories to structured, LLM-friendly formats
- **LLM2Git**: Parse LLM responses and apply changes to repositories
- **Smart Analysis**: Automatic project structure and technology detection
- **Security**: Built-in sanitization for sensitive data
- **Flexible Prompts**: Pre-built templates for common tasks
- **Git Integration**: Full Git workflow support (branches, patches, commits)

## Installation

### From Source
```bash
git clone https://github.com/yourusername/git-llm-toolkit.git
cd git-llm-toolkit
pip install -e .
```
Quick Start
1. Convert Repository to LLM Format
```bash

git-llm convert /path/to/repository --output analysis_output
```
2. Generate a Prompt
```bash

git-llm prompt generate --type code-review --output review_prompt.txt
```
3. Process LLM Response
```bash

git-llm process llm_response.json --apply --create-branch
```
4. Run Complete Workflow
```bash

git-llm workflow /path/to/repository --type code-review --full
```
Architecture
text

git-llm-toolkit/
├── git2llm/          # Repository to LLM conversion
├── llm2git/          # LLM response to Git integration
├── prompts/          # Prompt templates and management
├── utils/            # Shared utilities
└── cli.py           # Command-line interface

Modules
Git2LLM (git2llm/)

    converter.py: Main conversion logic

    analyzer.py: Project structure analysis

    sanitizer.py: Data sanitization

LLM2Git (llm2git/)

    processor.py: LLM response parsing

    git_ops.py: Git operations

    validator.py: Patch validation

Prompts (prompts/)

    generator.py: Prompt generation

    templates/: Pre-built prompt templates

    manager.py: Prompt management

Prompt Templates

The toolkit includes several pre-built prompt templates:

    Code Review: Comprehensive code analysis

    Bug Fix: Bug detection and fixes

    New Feature: Feature implementation

    Security Audit: Security analysis

    Refactoring: Code improvement suggestions

    Git Implementation: Git-ready implementation format

Examples

See the examples/ directory for complete workflow examples:
```python

# examples/simple_workflow.py
from git2llm import convert_repository
from llm2git import process_llm_response

# Convert repository
result = convert_repository("/path/to/repo", output_dir="analysis")

# Generate prompt
with open("analysis/prompts/code_review.txt") as f:
    prompt = f.read()

# (Send to LLM and get response...)

# Process response
process_llm_response("llm_response.json", repo_path="/path/to/repo", apply=True)

Configuration

Configuration can be set via environment variables or a config file:
bash

# Environment variables
export GIT_LLM_MAX_FILE_SIZE=2  # MB
export GIT_LLM_INCLUDE_DOCS=true
export GIT_LLM_SANITIZE=true

# Config file
git-llm config --set max_file_size 2
git-llm config --set include_docs true

Security

    Sensitive Data Protection: Automatic sanitization of API keys, passwords, tokens

    File Size Limits: Configurable limits to prevent large file processing

    Validation: All patches are validated before application

    Dry Run Mode: Test changes before applying

Contributing

    Fork the repository

    Create a feature branch

    Make your changes

    Run tests: pytest

    Submit a pull request

License

MIT License - see LICENSE file for details.
Support

    Issues: https://github.com/yourusername/git-llm-toolkit/issues

    Documentation: https://github.com/yourusername/git-llm-toolkit/wiki

    Discussions: https://github.com/yourusername/git-llm-toolkit/discussions

text


## 10. Example Workflow: `examples/simple_workflow.py`

```python
#!/usr/bin/env python3
"""
Simple workflow example for Git-to-LLM Toolkit
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from git2llm.main import convert_repository
from llm2git.main import process_llm_response
from prompts.manager import PromptManager

def simple_workflow(repo_path: str, output_dir: str = "llm_analysis"):
    """Run a simple analysis and implementation workflow."""
    
    print(f"Starting workflow for: {repo_path}")
    print("=" * 60)
    
    # Step 1: Convert repository
    print("\n1. Converting repository to LLM format...")
    from argparse import Namespace
    
    args = Namespace(
        repo_path=repo_path,
        output=output_dir,
        max_size=1,
        include_docs=True,
        no_sanitize=False
    )
    
    conversion_result = convert_repository(args)
    print(f"✓ Conversion complete: {conversion_result['output_dir']}")
    
    # Step 2: Generate prompt
    print("\n2. Generating code review prompt...")
    prompt_manager = PromptManager()
    prompt_file = prompt_manager.generate_prompt(
        prompt_type='code-review',
        output_file='code_review_prompt.txt',
        repo_path=repo_path
    )
    
    print(f"✓ Prompt generated: {prompt_file}")
    
    # Step 3: Show prompt usage instructions
    print("\n3. Next steps:")
    print("-" * 40)
    print(f"Prompt file: {prompt_file}")
    print(f"Codebase file: {output_dir}/codebase.txt")
    print(f"Documentation: {output_dir}/documentation.txt")
    print("\nUse these files with your LLM to get analysis.")
    print("\nWhen you have the LLM response, run:")
    print(f"  git-llm process llm_response.json --repo {repo_path} --apply")
    
    return {
        'conversion': conversion_result,
        'prompt_file': prompt_file,
        'output_dir': output_dir
    }

def process_response_workflow(response_file: str, repo_path: str):
    """Process an LLM response and apply changes."""
    
    print(f"\nProcessing LLM response: {response_file}")
    print("=" * 60)
    
    from argparse import Namespace
    
    args = Namespace(
        response_file=response_file,
        repo=repo_path,
        apply=True,
        dry_run=False,
        create_branch='auto',
        validate_only=False
    )
    
    process_result = process_llm_response(args)
    
    if process_result['success']:
        print(f"\n✓ Processing complete!")
        print(f"- Applied patches: {process_result['applied_patches']}")
        print(f"- Branch created: {process_result.get('branch', 'N/A')}")
        print(f"- Reports: {len(process_result.get('reports', {}))}")
        
        print("\nNext steps:")
        print("1. Review changes: git diff")
        print("2. Run tests")
        print("3. Commit: ./apply_llm_changes.sh (if generated)")
    else:
        print(f"\n✗ Processing failed: {process_result.get('error')}")
    
    return process_result

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple workflow example")
    parser.add_argument('repo_path', help='Repository path')
    parser.add_argument('--output', default='llm_analysis', help='Output directory')
    parser.add_argument('--process', help='LLM response file to process')
    
    args = parser.parse_args()
    
    if args.process:
        # Process existing LLM response
        process_response_workflow(args.process, args.repo_path)
    else:
        # Run full analysis workflow
        simple_workflow(args.repo_path, args.output)

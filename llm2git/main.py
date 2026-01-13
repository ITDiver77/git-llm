#!/usr/bin/env python3
"""
LLM2Git Module: Process LLM responses and integrate with Git
"""

import json
from pathlib import Path
from .processor import LLMResponseProcessor
from .git_ops import GitOperations
from .validator import PatchValidator
from utils.logger import setup_logger

logger = setup_logger('llm2git')

def process_llm_response(args):
    """Process LLM response and integrate with Git."""
    
    response_file = Path(args.response_file).resolve()
    repo_path = Path(args.repo).resolve()
    
    logger.info(f"Processing LLM response: {response_file}")
    logger.info(f"Repository: {repo_path}")
    
    # Initialize components
    processor = LLMResponseProcessor()
    git_ops = GitOperations(repo_path)
    validator = PatchValidator(repo_path)
    
    try:
        # Step 1: Parse LLM response
        logger.info("Parsing LLM response...")
        parsed_response = processor.parse_response(response_file)
        
        if not parsed_response.get('changes'):
            logger.warning("No changes found in LLM response")
            return {'success': False, 'error': 'No changes found'}
        
        # Step 2: Validate patches
        logger.info("Validating patches...")
        validation_results = validator.validate_patches(parsed_response.get('patches', []))
        
        valid_patches = validation_results.get('valid', [])
        if not valid_patches and not args.validate_only:
            logger.error("No valid patches found")
            return {'success': False, 'error': 'No valid patches'}
        
        # Step 3: Create branch if requested
        branch_name = None
        if args.create_branch:
            branch_name = args.create_branch
            if branch_name == 'auto':
                # Generate branch name from changes
                first_change = parsed_response['changes'][0]
                description = first_change.get('description', 'llm-changes')
                branch_name = f"llm/{description.lower().replace(' ', '-')[:30]}"
            
            logger.info(f"Creating branch: {branch_name}")
            git_ops.create_branch(branch_name)
        
        # Step 4: Apply patches if requested
        applied_patches = []
        if args.apply and valid_patches and not args.dry_run:
            logger.info(f"Applying {len(valid_patches)} patches...")
            for patch in valid_patches:
                try:
                    git_ops.apply_patch(patch['content'])
                    applied_patches.append(patch)
                    logger.info(f"Applied patch for: {patch.get('file', 'unknown')}")
                except Exception as e:
                    logger.error(f"Failed to apply patch: {e}")
        
        elif args.dry_run:
            logger.info(f"Dry run: Would apply {len(valid_patches)} patches")
        
        # Step 5: Generate reports
        logger.info("Generating reports...")
        reports = generate_reports(
            parsed_response, 
            validation_results, 
            applied_patches,
            repo_path
        )
        
        # Step 6: Generate commit script if changes were applied
        if applied_patches and parsed_response.get('commits'):
            commit_script = git_ops.generate_commit_script(
                parsed_response['commits'],
                branch_name
            )
            reports['commit_script'] = commit_script
        
        logger.info("Processing complete!")
        
        return {
            'success': True,
            'valid_patches': len(valid_patches),
            'applied_patches': len(applied_patches),
            'branch': branch_name,
            'reports': reports
        }
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise

def generate_reports(parsed_response, validation_results, applied_patches, repo_path):
    """Generate various reports."""
    reports = {}
    
    # Implementation report
    report_content = [
        "# LLM Implementation Report",
        "",
        "## Summary",
        f"- Changes requested: {len(parsed_response.get('changes', []))}",
        f"- Patches provided: {len(parsed_response.get('patches', []))}",
        f"- Valid patches: {len(validation_results.get('valid', []))}",
        f"- Applied patches: {len(applied_patches)}",
        "",
        "## Changes Requested"
    ]
    
    for change in parsed_response.get('changes', []):
        report_content.extend([
            f"### {change.get('file_path', 'Unknown')}",
            f"- **Type**: {change.get('change_type', 'modify')}",
            f"- **Priority**: {change.get('priority', 'medium')}",
            f"- **Description**: {change.get('description', '')}",
            ""
        ])
    
    if validation_results.get('invalid'):
        report_content.extend([
            "## Validation Issues",
            "The following patches could not be applied:"
        ])
        
        for invalid in validation_results['invalid']:
            report_content.append(f"- {invalid.get('error', 'Unknown error')}")
    
    # Next steps
    report_content.extend([
        "",
        "## Next Steps",
        "```bash",
        "# 1. Review changes",
        "git status",
        "git diff",
        "",
        "# 2. Test the changes",
        "# Run your test suite",
        "",
        "# 3. Commit changes",
        "# Use the generated commit script or commit manually",
        "```"
    ])
    
    report_file = repo_path / 'llm_implementation_report.md'
    report_file.write_text("\n".join(report_content))
    reports['implementation_report'] = report_file
    
    # JSON summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'changes': parsed_response.get('changes', []),
        'validation': validation_results,
        'applied': [p.get('file', 'unknown') for p in applied_patches]
    }
    
    summary_file = repo_path / 'llm_summary.json'
    summary_file.write_text(json.dumps(summary, indent=2))
    reports['summary_json'] = summary_file
    
    return reports

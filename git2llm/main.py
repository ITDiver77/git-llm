#!/usr/bin/env python3
"""
Git2LLM Module: Convert Git repositories to LLM-optimized formats
"""

import json
from pathlib import Path
from .converter import RepositoryConverter
from .analyzer import ProjectAnalyzer
from .sanitizer import ContentSanitizer
from utils.logger import setup_logger

logger = setup_logger('git2llm')

def convert_repository(args):
    """Convert repository to LLM format."""
    
    repo_path = Path(args.repo_path).resolve()
    output_dir = Path(args.output).resolve()
    
    logger.info(f"Converting repository: {repo_path}")
    logger.info(f"Output directory: {output_dir}")
    
    # Initialize components
    converter = RepositoryConverter(repo_path, output_dir)
    analyzer = ProjectAnalyzer(repo_path)
    sanitizer = ContentSanitizer()
    
    # Set configuration
    converter.max_file_size = args.max_size * 1024 * 1024
    converter.include_docs = args.include_docs
    sanitizer.enabled = not args.no_sanitize
    
    try:
        # Step 1: Analyze project structure
        logger.info("Analyzing project structure...")
        analysis = analyzer.analyze()
        
        # Step 2: Extract files
        logger.info("Extracting files...")
        extracted_files = converter.extract_files()
        
        # Step 3: Sanitize content
        if sanitizer.enabled:
            logger.info("Sanitizing sensitive data...")
            extracted_files = sanitizer.process_files(extracted_files)
        
        # Step 4: Generate outputs
        logger.info("Generating output files...")
        outputs = converter.generate_outputs(extracted_files, analysis)
        
        # Step 5: Save metadata
        metadata = {
            'repo_path': str(repo_path),
            'analysis': analysis,
            'file_stats': converter.stats,
            'config': {
                'max_file_size': args.max_size,
                'sanitization_enabled': sanitizer.enabled,
                'docs_included': args.include_docs
            }
        }
        
        metadata_file = output_dir / 'metadata.json'
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        logger.info(f"Conversion complete!")
        logger.info(f"Output files: {outputs}")
        logger.info(f"Metadata: {metadata_file}")
        
        return {
            'success': True,
            'output_dir': str(output_dir),
            'files': outputs,
            'analysis': analysis
        }
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        raise

def analyze_repository(repo_path):
    """Analyze repository structure."""
    analyzer = ProjectAnalyzer(repo_path)
    return analyzer.analyze()

def extract_repository_info(repo_path):
    """Extract basic repository information."""
    from utils.git_utils import get_git_info
    
    return get_git_info(repo_path)

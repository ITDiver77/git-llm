#!/usr/bin/env python3
"""
Repository Converter: Convert repository files to LLM-optimized format
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Tuple
import shutil
from datetime import datetime

class RepositoryConverter:
    """Convert Git repository to LLM-optimized text files."""
    
    def __init__(self, repo_path: Path, output_dir: Path):
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.code_output = output_dir / 'codebase.txt'
        self.docs_output = output_dir / 'documentation.txt'
        self.structure_output = output_dir / 'structure.txt'
        
        # Configuration
        self.max_file_size = 1 * 1024 * 1024  # 1MB
        self.include_docs = True
        
        # File patterns to include/exclude
        self.source_patterns = [
            '*.py', '*.js', '*.ts', '*.jsx', '*.tsx', '*.java', '*.cpp', '*.c', '*.h',
            '*.go', '*.rs', '*.php', '*.rb', '*.swift', '*.kt', '*.scala',
            '*.sh', '*.bash', '*.sql', '*.html', '*.css', '*.scss', '*.sass',
            '*.json', '*.xml', '*.yaml', '*.yml', '*.toml', '*.ini', '*.cfg', '*.conf',
            'Dockerfile', 'docker-compose*.yml', '*.dockerfile',
            'Makefile', 'CMakeLists.txt', '*.mk',
            '*.md', '*.txt', '*.rst', '*.tex'
        ]
        
        self.exclude_patterns = [
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
            '*.class', '*.jar', '*.war', '*.ear', '*.bin', '*.exe',
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.ico', '*.svg',
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx',
            '*.zip', '*.tar', '*.gz', '*.rar', '*.7z', '*.bz2',
            '.git/*', 'node_modules/*', '__pycache__/*', '.pytest_cache/*',
            '*.egg-info/*', '*.dist-info/*', 'build/*', 'dist/*', 'target/*',
            'venv/*', '.env/*', '.venv/*', 'env/*', '.idea/*', '.vscode/*',
            '*.log', '*.tmp', '*.temp', '*.swp', '*.swo'
        ]
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'skipped_size': 0,
            'total_size': 0,
            'start_time': None,
            'end_time': None
        }
    
    def should_include(self, file_path: Path) -> bool:
        """Check if file should be included based on patterns."""
        rel_path = str(file_path.relative_to(self.repo_path))
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return False
        
        # Check size
        try:
            size = file_path.stat().st_size
            self.stats['total_size'] += size
            
            if size > self.max_file_size:
                self.stats['skipped_size'] += size
                self.stats['skipped_files'] += 1
                return False
        except:
            return False
        
        # Check include patterns for source files
        for pattern in self.source_patterns:
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
        
        # Include README and LICENSE files
        if file_path.name.lower() in ['readme', 'readme.md', 'readme.txt', 
                                      'license', 'license.txt', 'license.md',
                                      'contributing.md', 'changelog.md']:
            return True
        
        # Check if it's a text file
        if self._is_text_file(file_path):
            return True
        
        return False
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                # Check for null bytes
                if b'\0' in chunk:
                    return False
                
                # Check if it's valid UTF-8
                try:
                    chunk.decode('utf-8')
                    return True
                except:
                    return False
        except:
            return False
    
    def extract_files(self) -> List[Dict[str, Any]]:
        """Extract files from repository."""
        self.stats['start_time'] = datetime.now()
        
        files = []
        
        for root, dirs, file_names in os.walk(self.repo_path):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(
                fnmatch.fnmatch(d, pattern.strip('*/')) for pattern in self.exclude_patterns
            )]
            
            for file_name in file_names:
                file_path = Path(root) / file_name
                
                if self.should_include(file_path):
                    try:
                        content = self._read_file(file_path)
                        
                        files.append({
                            'path': str(file_path.relative_to(self.repo_path)),
                            'content': content,
                            'size': file_path.stat().st_size,
                            'type': self._get_file_type(file_path),
                            'is_documentation': self._is_documentation(file_path)
                        })
                        
                        self.stats['processed_files'] += 1
                        
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        self.stats['skipped_files'] += 1
        
        self.stats['total_files'] = len(files)
        self.stats['end_time'] = datetime.now()
        
        return files
    
    def _read_file(self, file_path: Path) -> str:
        """Read file content with proper encoding handling."""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, try with errors='replace'
        return file_path.read_text(encoding='utf-8', errors='replace')
    
    def _get_file_type(self, file_path: Path) -> str:
        """Get file type based on extension."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react-jsx',
            '.tsx': 'react-tsx',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'header',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.sh': 'shell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.md': 'markdown',
            '.txt': 'text'
        }
        
        return extension_map.get(file_path.suffix.lower(), 'unknown')
    
    def _is_documentation(self, file_path: Path) -> bool:
        """Check if file is documentation."""
        doc_patterns = ['*.md', '*.txt', '*.rst', '*.tex', '*.adoc']
        doc_names = ['readme*', 'README*', 'license*', 'LICENSE*', 
                    'contributing*', 'CONTRIBUTING*', 'changelog*', 'CHANGELOG*']
        
        for pattern in doc_patterns:
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
        
        for pattern in doc_names:
            if fnmatch.fnmatch(file_path.name.lower(), pattern):
                return True
        
        return False
    
    def generate_outputs(self, files: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Path]:
        """Generate output files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate file tree
        tree_content = self._generate_file_tree(files)
        self.structure_output.write_text(tree_content)
        
        # Separate code and documentation
        code_files = [f for f in files if not f['is_documentation']]
        doc_files = [f for f in files if f['is_documentation']]
        
        # Generate codebase file
        code_content = self._format_codebase(code_files, analysis)
        self.code_output.write_text(code_content)
        
        # Generate documentation file
        doc_content = self._format_documentation(doc_files)
        self.docs_output.write_text(doc_content)
        
        # Generate summary
        summary = self._generate_summary(analysis)
        summary_file = self.output_dir / 'summary.md'
        summary_file.write_text(summary)
        
        return {
            'codebase': self.code_output,
            'documentation': self.docs_output,
            'structure': self.structure_output,
            'summary': summary_file
        }
    
    def _generate_file_tree(self, files: List[Dict[str, Any]]) -> str:
        """Generate file tree structure."""
        lines = [f"Project Structure: {self.repo_path.name}", "=" * 60, ""]
        
        # Group files by directory
        dirs = {}
        for file in files:
            path = Path(file['path'])
            parent = str(path.parent)
            if parent == '.':
                parent = ''
            
            if parent not in dirs:
                dirs[parent] = []
            dirs[parent].append(path.name)
        
        # Sort directories
        sorted_dirs = sorted(dirs.keys())
        
        for directory in sorted_dirs:
            if directory:
                lines.append(f"{directory}/")
            
            files_in_dir = sorted(dirs[directory])
            for file_name in files_in_dir:
                indent = "    " if directory else ""
                lines.append(f"{indent}├── {file_name}")
            
            if directory:
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_codebase(self, files: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Format codebase for LLM consumption."""
        lines = [
            "=" * 80,
            "PROJECT CODEBASE",
            "=" * 80,
            "",
            "ANALYSIS SUMMARY",
            f"Repository: {self.repo_path.name}",
            f"Total files: {len(files)}",
            f"Main language: {analysis.get('primary_language', 'Unknown')}",
            f"Framework: {analysis.get('primary_framework', 'Unknown')}",
            "",
            "=" * 80,
            "FILE CONTENTS",
            "=" * 80,
            ""
        ]
        
        for file in files:
            lines.extend([
                "",
                "-" * 60,
                f"FILE: {file['path']}",
                f"TYPE: {file['type']}",
                f"SIZE: {file['size']} bytes",
                "-" * 60,
                "",
                file['content'],
                ""
            ])
        
        return "\n".join(lines)
    
    def _format_documentation(self, files: List[Dict[str, Any]]) -> str:
        """Format documentation files."""
        lines = [
            "=" * 80,
            "PROJECT DOCUMENTATION",
            "=" * 80,
            ""
        ]
        
        for file in files:
            lines.extend([
                "",
                "-" * 60,
                f"DOCUMENTATION: {file['path']}",
                "-" * 60,
                "",
                file['content'],
                ""
            ])
        
        return "\n".join(lines)
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate summary markdown file."""
        return f"""# Project Analysis Summary

## Repository Information
- **Name**: {self.repo_path.name}
- **Path**: {self.repo_path}
- **Analysis Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistics
- **Total Files Processed**: {self.stats['processed_files']}
- **Total Size**: {self.stats['total_size'] / 1024 / 1024:.2f} MB
- **Files Skipped**: {self.stats['skipped_files']}
- **Size Skipped**: {self.stats['skipped_size'] / 1024 / 1024:.2f} MB

## Technical Analysis
{self._format_analysis(analysis)}

## Generated Files
1. `codebase.txt` - All source code files
2. `documentation.txt` - All documentation files
3. `structure.txt` - File tree structure
4. `metadata.json` - Analysis metadata

## Usage Notes
- Use `codebase.txt` with LLM prompts for code analysis
- Reference `structure.txt` for project architecture
- Check `documentation.txt` for project documentation
"""
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results."""
        lines = []
        
        if 'languages' in analysis:
            lines.append("### Languages Used")
            for lang, count in analysis['languages'].items():
                lines.append(f"- {lang}: {count} files")
            lines.append("")
        
        if 'frameworks' in analysis:
            lines.append("### Frameworks Detected")
            for framework in analysis['frameworks']:
                lines.append(f"- {framework}")
            lines.append("")
        
        if 'file_types' in analysis:
            lines.append("### File Types")
            for file_type, count in analysis['file_types'].items():
                lines.append(f"- {file_type}: {count}")
        
        return "\n".join(lines)

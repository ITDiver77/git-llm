#!/usr/bin/env python3
"""
LLM Response Processor: Parse and extract structured data from LLM responses
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class LLMResponseProcessor:
    """Process LLM responses into structured data for Git integration."""
    
    def __init__(self):
        self.parsers = {
            'json': self._parse_json_response,
            'markdown': self._parse_markdown_response,
            'text': self._parse_text_response,
            'mixed': self._parse_mixed_response
        }
    
    def parse_response(self, response_file: Path) -> Dict[str, Any]:
        """Parse LLM response file."""
        content = response_file.read_text(encoding='utf-8')
        
        # Detect response type
        response_type = self._detect_response_type(content)
        
        # Parse based on type
        parser = self.parsers.get(response_type, self._parse_text_response)
        parsed_data = parser(content)
        
        # Extract patches from any format
        parsed_data['patches'] = self._extract_patches(content)
        
        # Extract commit messages
        parsed_data['commits'] = self._extract_commit_messages(content)
        
        # Add metadata
        parsed_data['metadata'] = {
            'response_file': str(response_file),
            'response_type': response_type,
            'parsed_at': datetime.now().isoformat(),
            'content_length': len(content)
        }
        
        return parsed_data
    
    def _detect_response_type(self, content: str) -> str:
        """Detect the type of response."""
        # Check for JSON
        if content.strip().startswith('{') or content.strip().startswith('['):
            try:
                json.loads(content)
                return 'json'
            except:
                pass
        
        # Check for YAML
        if '---' in content[:100]:
            try:
                yaml.safe_load(content)
                return 'yaml'
            except:
                pass
        
        # Check for structured markdown
        if re.search(r'```(?:json|patch|diff)', content):
            return 'mixed'
        
        # Check for markdown headers
        if re.search(r'^#+\s+', content, re.MULTILINE):
            return 'markdown'
        
        return 'text'
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response."""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Try to find JSON in the content
            json_pattern = r'```json\s*\n(.*?)\n```'
            match = re.search(json_pattern, content, re.DOTALL)
            
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            
            # Try to extract JSON-like structure
            return self._extract_structured_data(content)
    
    def _parse_markdown_response(self, content: str) -> Dict[str, Any]:
        """Parse markdown response."""
        result = {
            'changes': [],
            'summary': '',
            'details': {}
        }
        
        # Extract sections
        sections = re.split(r'\n#+\s+', content)
        
        for section in sections:
            if not section.strip():
                continue
            
            # Get section title
            lines = section.split('\n')
            title = lines[0].strip()
            body = '\n'.join(lines[1:]).strip()
            
            if not title:
                continue
            
            title_lower = title.lower()
            
            if 'change' in title_lower or 'modification' in title_lower:
                result['changes'] = self._extract_changes_from_text(body)
            elif 'summary' in title_lower or 'overview' in title_lower:
                result['summary'] = body
            elif 'implementation' in title_lower or 'plan' in title_lower:
                result['implementation_plan'] = body
            else:
                result['details'][title] = body
        
        return result
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """Parse plain text response."""
        return {
            'raw_content': content,
            'changes': self._extract_changes_from_text(content),
            'summary': content[:500] + '...' if len(content) > 500 else content
        }
    
    def _parse_mixed_response(self, content: str) -> Dict[str, Any]:
        """Parse mixed format response (markdown with code blocks)."""
        result = {
            'changes': [],
            'code_blocks': [],
            'sections': {}
        }
        
        # Extract JSON from code blocks
        json_pattern = r'```json\s*\n(.*?)\n```'
        json_matches = re.findall(json_pattern, content, re.DOTALL)
        
        for json_block in json_matches:
            try:
                data = json.loads(json_block)
                if isinstance(data, list):
                    result['changes'].extend(data)
                elif isinstance(data, dict):
                    if 'changes' in data:
                        result['changes'].extend(data['changes'])
                    else:
                        result.update(data)
            except:
                pass
        
        # Extract other code blocks
        code_pattern = r'```(?!json)(\w+)?\s*\n(.*?)\n```'
        code_matches = re.findall(code_pattern, content, re.DOTALL)
        
        for lang, code in code_matches:
            result['code_blocks'].append({
                'language': lang or 'text',
                'content': code
            })
        
        # Extract markdown sections
        sections = re.split(r'\n#+\s+', content)
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.split('\n')
            title = lines[0].strip()
            body = '\n'.join(lines[1:]).strip()
            
            if title and body:
                result['sections'][title] = body
        
        return result
    
    def _extract_changes_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract changes from unstructured text."""
        changes = []
        
        # Look for file patterns
        file_patterns = [
            r'File:\s*(.+?)(?:\n|$)',
            r'File\s*[#:]?\s*(.+?)(?:\n|$)',
            r'^(?:-|\*|\d+\.)\s*(.+?\.(?:py|js|ts|java|cpp|c|h|go|rs|php|rb|sh|md|txt|json|yaml|yml))',
            r'\b(?:modif|chang|updat|add|remov|delet).*?\s+file\s+["\']?(.+?)["\']?(?:\s|$|\.)'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if match.strip() and '.' in match:
                    changes.append({
                        'file_path': match.strip(),
                        'change_type': 'modify',
                        'description': f'Change detected in {match.strip()}',
                        'source': 'text_extraction'
                    })
        
        return changes
    
    def _extract_structured_data(self, content: str) -> Dict[str, Any]:
        """Extract structured data using various patterns."""
        result = {}
        
        # Look for key-value pairs
        kv_pattern = r'^\s*(.+?)\s*[:=]\s*(.+?)\s*$'
        lines = content.split('\n')
        
        for line in lines:
            match = re.match(kv_pattern, line)
            if match:
                key = match.group(1).strip().lower().replace(' ', '_')
                value = match.group(2).strip()
                
                # Try to parse as JSON if it looks like a list or dict
                if value.startswith('[') or value.startswith('{'):
                    try:
                        value = json.loads(value)
                    except:
                        pass
                
                result[key] = value
        
        return result
    
    def _extract_patches(self, content: str) -> List[Dict[str, Any]]:
        """Extract patches from response content."""
        patches = []
        
        # Look for unified diff patches
        diff_patterns = [
            r'```(?:patch|diff)\s*\n(.*?)\n```',
            r'^--- a/(.+?)\n\+\+\+ b/(.+?)(?:\n@@.*?(?:\n.*?)*?)(?=\n---|\n```|\Z)',
            r'@@ -\d+,\d+ \+\d+,\d+ @@\n(?:.*?\n)*?(?=\n@@|\n---|\n```|\Z)'
        ]
        
        for pattern in diff_patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
            
            for match in matches:
                patch_content = match.group(0)
                
                # Extract file names
                file_match = re.search(r'--- a/(.+?)\n\+\+\+ b/(.+?)\n', patch_content)
                
                patches.append({
                    'content': patch_content,
                    'file': file_match.group(1) if file_match else 'unknown',
                    'format': 'unified_diff'
                })
        
        # Look for simple replacements
        simple_pattern = r'Replace:\s*["\']?(.+?)["\']?\s*→\s*["\']?(.+?)["\']?(?:\s|$)'
        simple_matches = re.findall(simple_pattern, content, re.MULTILINE)
        
        for old, new in simple_matches:
            patches.append({
                'content': f'-{old}\n+{new}',
                'file': 'unknown',
                'format': 'simple_replace'
            })
        
        return patches
    
    def _extract_commit_messages(self, content: str) -> List[str]:
        """Extract commit messages from response."""
        messages = []
        
        # Look for commit message sections
        commit_patterns = [
            r'Commit(?: Message)?:\s*(.+?)(?:\n|$)',
            r'^`(.+?)`\s*$',
            r'feat(?:ure)?:\s*(.+?)(?:\n|$)',
            r'^(?:-|\*|\d+\.)\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in commit_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            messages.extend([m.strip() for m in matches if len(m.strip()) > 10])
        
        # Deduplicate and clean
        messages = list(dict.fromkeys(messages))  # Preserve order
        
        return messages[:5]  # Return top 5 messages

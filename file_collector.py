#!/usr/bin/env python3

import os
import argparse
import re
from pathlib import Path

def detect_language(file_path):
    """Detect language based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    
    # Map file extensions to language names for code block formatting
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'jsx',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.md': 'markdown',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.java': 'java',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.sh': 'bash',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.sql': 'sql',
        '.swift': 'swift',
        '.kt': 'kotlin'
    }
    
    return language_map.get(ext, '')  # Return empty string if extension not found

def should_include_file(file_path):
    """Check if the file should be included in the output."""
    # Skip binary files, hidden files, etc.
    exclusions = [
        r'\.git',
        r'__pycache__',
        r'\.pyc$',
        r'\.png$', r'\.jpg$', r'\.jpeg$', r'\.gif$', r'\.svg$',
        r'\.pdf$', r'\.zip$', r'\.tar$', r'\.gz$',
        r'\.exe$', r'\.dll$', r'\.so$', r'\.class$',
        r'\.o$', r'\.a$', r'\.lib$',
        r'node_modules',
        r'\.env',
        r'\.DS_Store$'
    ]
    
    # Check if file path matches any exclusion pattern
    for pattern in exclusions:
        if re.search(pattern, file_path):
            return False
    
    return True

def process_directory(source_dir, output_file):
    """Process all files in a directory and its subdirectories."""
    source_dir = os.path.abspath(source_dir)
    source_name = os.path.basename(source_dir)
    
    with open(output_file, 'w', encoding='utf-8') as output:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip files that should not be included
                if not should_include_file(file_path):
                    continue
                
                # Get relative path from source directory
                rel_path = os.path.relpath(file_path, os.path.dirname(source_dir))
                language = detect_language(file_path)
                
                try:
                    # Try to read the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Write file path and content to output file
                    output.write(f"```{language}\n")
                    output.write(f"// {rel_path}\n")
                    output.write(content)
                    
                    # Add newline if the file doesn't end with one
                    if content and not content.endswith('\n'):
                        output.write('\n')
                    
                    output.write("```\n\n")
                except UnicodeDecodeError:
                    # Skip binary files that couldn't be decoded as UTF-8
                    print(f"Skipping binary file: {rel_path}")
                except Exception as e:
                    print(f"Error processing {rel_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Collect file contents into a single output file.')
    parser.add_argument('--source', default='src', help='Source directory to scan (default: src)')
    parser.add_argument('--output', default='output.txt', help='Output file path (default: output.txt)')
    
    args = parser.parse_args()
    
    # Ensure source directory exists
    if not os.path.isdir(args.source):
        print(f"Error: Source directory '{args.source}' does not exist.")
        return
    
    # Process the directory
    print(f"Processing directory: {args.source}")
    process_directory(args.source, args.output)
    print(f"Output written to: {args.output}")

if __name__ == "__main__":
    main() 
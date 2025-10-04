#!/usr/bin/env python3
"""
Script to extract and render Mermaid diagrams from PROJECT_OVERVIEW.md
and create enhanced document versions with embedded images.
"""

import re
import os
import subprocess
import tempfile
from pathlib import Path

def extract_mermaid_diagrams(markdown_file):
    """Extract Mermaid diagrams from markdown file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all mermaid code blocks
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    diagrams = re.findall(mermaid_pattern, content, re.DOTALL)
    
    return diagrams, content

def render_mermaid_to_svg(mermaid_code, output_file):
    """Render Mermaid diagram to SVG using mermaid-cli."""
    try:
        # Create temporary mermaid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_file:
            temp_file.write(mermaid_code)
            temp_mmd = temp_file.name
        
        # Run mermaid-cli to generate SVG
        cmd = ['mmdc', '-i', temp_mmd, '-o', output_file, '-t', 'neutral', '-b', 'white']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp file
        os.unlink(temp_mmd)
        
        if result.returncode == 0:
            print(f"✅ Successfully rendered: {output_file}")
            return True
        else:
            print(f"❌ Failed to render {output_file}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error rendering diagram: {e}")
        return False

def create_enhanced_markdown(original_content, diagram_files):
    """Create enhanced markdown with image references."""
    enhanced_content = original_content
    
    # Replace mermaid code blocks with image references
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    diagram_index = 0
    
    def replace_mermaid(match):
        nonlocal diagram_index
        if diagram_index < len(diagram_files):
            img_file = diagram_files[diagram_index]
            diagram_index += 1
            return f'![Diagram {diagram_index}]({img_file})'
        return match.group(0)
    
    enhanced_content = re.sub(mermaid_pattern, replace_mermaid, enhanced_content, flags=re.DOTALL)
    
    return enhanced_content

def main():
    """Main function to process diagrams and create enhanced documents."""
    print("🔄 Starting Mermaid diagram rendering process...")
    
    # Check if mermaid-cli is available
    try:
        result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ mermaid-cli (mmdc) not found. Installing...")
            subprocess.run(['/usr/bin/npm', 'install', '-g', '@mermaid-js/mermaid-cli'], check=True)
    except FileNotFoundError:
        try:
            # Check if Node.js is available with full path
            result = subprocess.run(['/usr/bin/node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Node.js found, installing mermaid-cli...")
                subprocess.run(['/usr/bin/npm', 'install', '-g', '@mermaid-js/mermaid-cli'], check=True)
            else:
                print("❌ Node.js not found. Please install Node.js first.")
                return False
        except FileNotFoundError:
            print("❌ Node.js/npm not found. Please install Node.js first.")
            return False
    
    # Extract diagrams from original markdown
    markdown_file = 'PROJECT_OVERVIEW.md'
    if not os.path.exists(markdown_file):
        print(f"❌ {markdown_file} not found!")
        return False
    
    print(f"📖 Reading {markdown_file}...")
    diagrams, content = extract_mermaid_diagrams(markdown_file)
    print(f"🔍 Found {len(diagrams)} Mermaid diagrams")
    
    if not diagrams:
        print("ℹ️  No Mermaid diagrams found in the document.")
        return True
    
    # Create diagrams directory
    diagrams_dir = Path('diagrams')
    diagrams_dir.mkdir(exist_ok=True)
    
    # Render each diagram
    diagram_files = []
    for i, diagram in enumerate(diagrams, 1):
        output_file = diagrams_dir / f'diagram_{i}.svg'
        print(f"🎨 Rendering diagram {i}/{len(diagrams)}...")
        
        if render_mermaid_to_svg(diagram, str(output_file)):
            diagram_files.append(str(output_file))
        else:
            # Fallback: create placeholder
            diagram_files.append(f'[Diagram {i} - Rendering Failed]')
    
    # Create enhanced markdown with image references
    print("📝 Creating enhanced markdown...")
    enhanced_content = create_enhanced_markdown(content, diagram_files)
    
    # Save enhanced markdown
    enhanced_file = 'PROJECT_OVERVIEW_ENHANCED.md'
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"✅ Enhanced markdown saved as: {enhanced_file}")
    
    # Generate enhanced documents
    print("📄 Generating enhanced DOCX...")
    subprocess.run([
        'pandoc', enhanced_file, '-o', 'PROJECT_OVERVIEW_ENHANCED.docx',
        '--from', 'markdown', '--to', 'docx', '--toc', '--toc-depth=3',
        '--highlight-style=tango'
    ])
    
    print("📄 Generating enhanced PDF...")
    subprocess.run([
        'pandoc', enhanced_file, '-o', 'PROJECT_OVERVIEW_ENHANCED.html',
        '--from', 'markdown', '--to', 'html', '--toc', '--toc-depth=3',
        '--highlight-style=tango', '--standalone'
    ])
    
    subprocess.run(['weasyprint', 'PROJECT_OVERVIEW_ENHANCED.html', 'PROJECT_OVERVIEW_ENHANCED.pdf'])
    
    print("🎉 Document conversion complete!")
    print("\n📋 Generated files:")
    for ext in ['docx', 'html', 'pdf']:
        file_path = f'PROJECT_OVERVIEW_ENHANCED.{ext}'
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size:,} bytes)")
    
    print(f"\n🖼️  Diagram files in '{diagrams_dir}':")
    for diagram_file in diagram_files:
        if os.path.exists(diagram_file):
            size = os.path.getsize(diagram_file)
            print(f"   ✅ {diagram_file} ({size:,} bytes)")
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

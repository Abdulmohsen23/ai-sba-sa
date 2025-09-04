import os
import argparse

def generate_project_structure(start_path, output_file, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = ['__pycache__', '.git', 'venv', 'node_modules']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(start_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            level = root.replace(start_path, '').count(os.sep)
            indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
            
            f.write(f"{indent}{os.path.basename(root)}/\n")
            
            subindent = '│   ' * level + '├── '
            for i, file in enumerate(files):
                if i == len(files) - 1:
                    subindent = '│   ' * level + '└── '
                f.write(f"{subindent}{file}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate project structure')
    parser.add_argument('--path', default='.', help='Project root path')
    parser.add_argument('--output', default='project_structure.txt', help='Output file')
    args = parser.parse_args()
    
    generate_project_structure(args.path, args.output)
    print(f"Project structure saved to {args.output}")
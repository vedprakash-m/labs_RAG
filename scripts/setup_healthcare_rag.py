#!/usr/bin/env python3
"""
Healthcare RAG Project Setup Script
==================================
This script sets up a complete Python environment for a healthcare RAG project.

Features:
- Creates and activates a virtual environment
- Installs essential packages for RAG applications
- Sets up project directory structure
- Creates configuration templates
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step_num, total_steps, message):
    """Print a formatted step message"""
    print(f"\n{Colors.BLUE}[{step_num}/{total_steps}]{Colors.END} {Colors.BOLD}{message}{Colors.END}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    """Print an info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

def run_command(command, description, shell=True):
    """Run a shell command and handle errors"""
    try:
        result = subprocess.run(command, shell=shell, check=True, 
                              capture_output=True, text=True)
        print_success(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    print(f"{Colors.BOLD}Healthcare RAG Project Setup{Colors.END}")
    print("=" * 40)
    print("This script will set up your healthcare RAG project environment.\n")
    
    # Get current directory
    project_dir = Path.cwd()
    venv_name = "healthcare_rag_env"
    venv_path = project_dir / venv_name
    
    print(f"Project directory: {project_dir}")
    print(f"Virtual environment: {venv_path}")
    
    # Confirm with user
    response = input(f"\nProceed with setup? (y/N): ").strip().lower()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    total_steps = 7
    
    # Step 1: Check Python version
    print_step(1, total_steps, "Checking Python version")
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print_error(f"Python 3.8+ required. Current version: {python_version.major}.{python_version.minor}")
        return
    print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Step 2: Create virtual environment
    print_step(2, total_steps, "Creating virtual environment")
    if venv_path.exists():
        print_info(f"Virtual environment already exists at {venv_path}")
        response = input("Remove existing environment and create new one? (y/N): ").strip().lower()
        if response == 'y':
            import shutil
            shutil.rmtree(venv_path)
            print_success("Removed existing virtual environment")
    
    if not venv_path.exists():
        if not run_command(f"python3 -m venv {venv_name}", "Virtual environment creation"):
            return
    else:
        print_success("Using existing virtual environment")
    
    # Step 3: Determine activation command based on OS
    print_step(3, total_steps, "Preparing package installation")
    system = platform.system()
    if system == "Windows":
        pip_cmd = f"{venv_path}\\Scripts\\pip"
        python_cmd = f"{venv_path}\\Scripts\\python"
        activate_cmd = f"{venv_path}\\Scripts\\activate"
    else:  # macOS/Linux
        pip_cmd = f"{venv_path}/bin/pip"
        python_cmd = f"{venv_path}/bin/python"
        activate_cmd = f"source {venv_path}/bin/activate"
    
    print_success("Environment commands prepared")
    
    # Step 4: Upgrade pip
    print_step(4, total_steps, "Upgrading pip")
    if not run_command(f"{pip_cmd} install --upgrade pip", "Pip upgrade"):
        print_error("Failed to upgrade pip, but continuing...")
    
    # Step 5: Install packages
    print_step(5, total_steps, "Installing essential packages")
    packages = [
        "azure-storage-blob",
        "azure-search-documents", 
        "openai",
        "langchain",
        "python-dotenv",
        "requests",
        "pandas",
        "numpy"
    ]
    
    print_info(f"Installing packages: {', '.join(packages)}")
    package_list = " ".join(packages)
    
    if not run_command(f"{pip_cmd} install {package_list}", "Package installation"):
        print_error("Some packages may have failed to install. Check the output above.")
    
    # Step 6: Create project structure
    print_step(6, total_steps, "Creating project directory structure")
    
    directories = [
        "src",
        "src/healthcare_rag",
        "src/healthcare_rag/data",
        "src/healthcare_rag/models", 
        "src/healthcare_rag/utils",
        "tests",
        "config",
        "notebooks"
    ]
    
    # Note: docs/ already exists, so we'll skip creating it
    for directory in directories:
        dir_path = project_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print_success(f"Created directory: {directory}/")
    
    # Step 7: Create configuration files
    print_step(7, total_steps, "Creating configuration files")
    
    # Create .env template
    env_content = """# Healthcare RAG Configuration
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string_here
AZURE_STORAGE_CONTAINER_NAME=healthcare-documents

# Azure Cognitive Search
AZURE_SEARCH_SERVICE_NAME=your_search_service_name
AZURE_SEARCH_API_KEY=your_search_api_key
AZURE_SEARCH_INDEX_NAME=healthcare-index

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_TYPE=azure  # or 'openai' for OpenAI API
OPENAI_API_BASE=https://your-resource.openai.azure.com/
OPENAI_API_VERSION=2024-02-01

# Application Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
"""
    
    with open(project_dir / ".env", "w") as f:
        f.write(env_content)
    print_success("Created .env configuration file")
    
    # Create requirements.txt
    requirements_content = """azure-storage-blob>=12.19.0
azure-search-documents>=11.4.0
openai>=1.0.0
langchain>=0.1.0
python-dotenv>=1.0.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
"""
    
    with open(project_dir / "requirements.txt", "w") as f:
        f.write(requirements_content)
    print_success("Created requirements.txt")
    
    # Create basic Python files
    init_content = '"""Healthcare RAG Package"""\n'
    
    # Create __init__.py files
    init_files = [
        "src/healthcare_rag/__init__.py",
        "src/healthcare_rag/data/__init__.py",
        "src/healthcare_rag/models/__init__.py",
        "src/healthcare_rag/utils/__init__.py"
    ]
    
    for init_file in init_files:
        with open(project_dir / init_file, "w") as f:
            f.write(init_content)
    
    print_success("Created Python package structure")
    
    # Create a simple main.py template
    main_content = '''"""
Healthcare RAG Main Application
==============================
"""

import os
from dotenv import load_dotenv

def main():
    """Main application entry point"""
    # Load environment variables
    load_dotenv()
    
    print("Healthcare RAG Application Starting...")
    print("Environment loaded successfully!")
    
    # TODO: Add your RAG implementation here
    
if __name__ == "__main__":
    main()
'''
    
    with open(project_dir / "src/healthcare_rag/main.py", "w") as f:
        f.write(main_content)
    print_success("Created main.py template")
    
    # Create .gitignore
    gitignore_content = """# Virtual Environment
healthcare_rag_env/
venv/
env/

# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Data files
*.csv
*.json
*.txt
data/
!requirements.txt
"""
    
    with open(project_dir / ".gitignore", "w") as f:
        f.write(gitignore_content)
    print_success("Created .gitignore")
    
    # Final success message
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Setup completed successfully!{Colors.END}")
    print("\nNext steps:")
    print(f"1. Activate virtual environment: {Colors.YELLOW}{activate_cmd}{Colors.END}")
    print(f"2. Configure your .env file with actual API keys")
    print(f"3. Start developing in src/healthcare_rag/")
    print(f"4. Test installation: {Colors.YELLOW}{python_cmd} src/healthcare_rag/main.py{Colors.END}")
    
    print(f"\nProject structure created:")
    print(f"├── {venv_name}/           # Virtual environment")
    print(f"├── docs/                  # Documentation (existing)")
    print(f"├── src/healthcare_rag/    # Main source code")
    print(f"├── tests/                 # Test files")
    print(f"├── config/                # Configuration files")
    print(f"├── notebooks/             # Jupyter notebooks")
    print(f"├── .env                   # Environment variables")
    print(f"├── requirements.txt       # Python dependencies")
    print(f"└── .gitignore             # Git ignore file")
    
    print(f"\n{Colors.BLUE}Happy coding! 🚀{Colors.END}")

if __name__ == "__main__":
    main()
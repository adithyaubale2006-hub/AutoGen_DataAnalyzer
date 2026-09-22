import os
from pathlib import Path
import logging

#Saves The data of any Changes in the folder with Date and Time
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

list_of_files = [
    # Core application
    "app.py",

    # Source package
    "src/__init__.py",
    "src/config.py",
    "src/state.py",
    "src/helper.py",
    "src/prompt.py",

    # Agents
    "src/agents/__init__.py",
    "src/agents/data_loader.py",
    "src/agents/data_cleaner.py",
    "src/agents/feature_engineer.py",
    "src/agents/data_analyzer.py",
    "src/agents/visualizer.py",
    "src/agents/report_generator.py",

    # Agent orchestration
    "src/orchestration/__init__.py",
    "src/orchestration/team.py",

    # Code execution / Docker
    "src/execution/__init__.py",
    "src/execution/code_executor.py",
    "src/execution/docker_manager.py",

    # Prompts
    "prompts/data_loader.txt",
    "prompts/data_cleaner.txt",
    "prompts/feature_engineer.txt",
    "prompts/data_analyzer.txt",
    "prompts/visualizer.txt",
    "prompts/report_generator.txt",

    # Data
    "data/.gitkeep",

    # Generated outputs
    "outputs/.gitkeep",

    # Research
    "research/trials.ipynb",

    # Tests
    "tests/__init__.py",
    "tests/test_cleaner.py",
    "tests/test_analyzer.py",
    "tests/test_executor.py",

    # Configuration
    ".env.example",
    ".gitignore",
    "requirements.txt",
    "README.md",
    "setup.py"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)
    
    if filedir !="":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory; {filedir} for the file: {filename}")
        
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating empty file: {filepath}")
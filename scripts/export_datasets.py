import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from loguru import logger

from src.config import load_config
from src.download import download_deforestation_data, monitor_tasks

if __name__ == "__main__":
    try:
        # Load config
        config = load_config()
        
        # Download data and get tasks
        tasks = download_deforestation_data(config)
        
        # Monitor tasks
        logger.info("Monitoring export tasks...")
        monitor_tasks(tasks)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")

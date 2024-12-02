from pathlib import Path
from typing import Dict, Any
import yaml
from loguru import logger

def load_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Parameters
    ----------
    config_path : str
        Path to configuration file
    
    Returns
    -------
    Dict[str, Any]
        Configuration dictionary
    
    Raises
    ------
    FileNotFoundError
        If config file doesn't exist
    """
    logger.info(f"Loading configuration from {config_path}")
    
    if not Path(config_path).is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Format export filenames with year ranges
    for dataset in ['mapbiomas_deforestation', 'gfw_forest_loss']:
        years = config['processing'][dataset.split('_')[0]]
        config['export']['files'][dataset] = config['export']['files'][dataset].format(
            start_year=years['start_year'],
            end_year=years['end_year']
        )
        
    logger.debug("Configuration loaded successfully")
    return config
    
def get_dataset_params(config: Dict[str, Any], dataset: str) -> Dict[str, Any]:
    """
    Get processing parameters for a dataset.
    
    Parameters
    ----------
    config : Dict[str, Any]
        Configuration dictionary
    dataset : str
        Dataset name ('mapbiomas' or 'gfw')
    
    Returns
    -------
    Dict[str, Any]
        Processing parameters
    """
    return config['processing'][dataset]

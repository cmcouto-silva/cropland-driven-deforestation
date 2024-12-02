import ee
import time
from loguru import logger
from src.config import load_config

def monitor_tasks(tasks: list, check_interval: int = 10) -> None:
    """
    Monitor Earth Engine export tasks until completion.
    
    Parameters
    ----------
    tasks : list
        List of ee.batch.Task objects to monitor
    check_interval : int, optional
        Seconds between status checks, by default 10
    """
    start_time = time.time()
    tasks_completed = [False] * len(tasks)
    
    while not all(tasks_completed):
        for i, task in enumerate(tasks):
            if not tasks_completed[i]:
                status = task.status()
                state = status['state']
                
                if state == 'COMPLETED':
                    elapsed = time.time() - start_time
                    tasks_completed[i] = True
                    logger.success(f"Task {task.id} completed in {elapsed:.1f} seconds")
                elif state == 'FAILED':
                    tasks_completed[i] = True
                    logger.error(f"Task {task.id} failed with error: {status.get('error_message', 'Unknown error')}")
                else:
                    logger.info(f"Task {task.id} state: {state}")
        
        if not all(tasks_completed):
            time.sleep(check_interval)

def download_deforestation_data(config: dict) -> None:
    """
    Download deforestation data from Mapbiomas and GFW.
    
    Parameters
    ----------
    config : dict
        Configuration dictionary containing paths and parameters
    """
    logger.info("Initializing Earth Engine")
    ee.Initialize()
    
    # Load datasets from config
    logger.info("Loading datasets")
    biomes = ee.FeatureCollection(config['earth_engine']['datasets']['biomes'])
    mapbiomas = ee.Image(config['earth_engine']['datasets']['mapbiomas'])
    gfw = ee.Image(config['earth_engine']['datasets']['gfw'])
    
    # Get Mapbiomas deforestation
    logger.info("Processing Mapbiomas deforestation")
    deforestationImgs = []
    for year in range(2010, 2024):
        classification = mapbiomas.select(f'classification_{year}')
        deforestation = classification.gte(400).And(classification.lt(500))
        area = deforestation.multiply(ee.Image.pixelArea().divide(10000))
        deforestationImgs.append(area.rename(f'MB_deforestation_{year}'))
    
    deforestationAll = ee.Image.cat(deforestationImgs)
    
    # Get GFW forest loss
    logger.info("Processing GFW forest loss")
    lossImgs = []
    for year in range(2010, 2024):
        yearOffset = year - 2000
        loss = gfw.select('lossyear').eq(yearOffset)
        area = loss.multiply(ee.Image.pixelArea().divide(10000))
        lossImgs.append(area.rename(f'GFW_forest_loss_{year}'))
    
    lossAll = ee.Image.cat(lossImgs)
    
    # Calculate statistics by biome
    logger.info("Calculating statistics")
    mapbiomasStats = deforestationAll.reduceRegions(
        collection=biomes,
        reducer=ee.Reducer.sum(),
        scale=config['processing']['mapbiomas']['scale'],
        tileScale=config['processing']['mapbiomas']['tile_scale']
    )
    
    gfwStats = lossAll.reduceRegions(
        collection=biomes,
        reducer=ee.Reducer.sum(),
        scale=config['processing']['gfw']['scale'],
        tileScale=config['processing']['gfw']['tile_scale']
    )
    
    # Export results
    logger.info("Starting exports")
    task_mb = ee.batch.Export.table.toDrive(
        collection=mapbiomasStats,
        description=config['export']['files']['mapbiomas_deforestation'],
        folder=config['export']['drive_folder'],
        fileFormat='CSV'
    )
    
    task_gfw = ee.batch.Export.table.toDrive(
        collection=gfwStats,
        description=config['export']['files']['gfw_forest_loss'],
        folder=config['export']['drive_folder'],
        fileFormat='CSV'
    )
    
    # Start exports
    task_mb.start()
    task_gfw.start()
    
    return [task_mb, task_gfw]

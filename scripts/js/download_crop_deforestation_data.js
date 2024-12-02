// Load datasets
var biomes = ee.FeatureCollection('projects/mapbiomas-territories/assets/TERRITORIES/LULC/BRAZIL/COLLECTION9/WORKSPACE/BIOMES');
var mapbiomas = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_deforestation_secondary_vegetation_v1');
var gfw = ee.Image('UMD/hansen/global_forest_change_2023_v1_11');
var mapbiomas_landcover = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1');

// Helper function to get cropland mask
function getCroplandMask(year) {
  var classification = mapbiomas_landcover.select('classification_' + year);
  return classification.eq(18)  // Temporary crop
    .or(classification.eq(19))  // Temporary crop
    .or(classification.eq(39))  // Soybean
    .or(classification.eq(20))  // Sugar cane
    .or(classification.eq(40))  // Sugar cane
    .or(classification.eq(62))  // Cotton
    .or(classification.eq(41)); // Other temporary crops
}

// Get cropland-driven deforestation for Mapbiomas (2010-2018)
var cropDeforestationImgs = [];
for (var year = 2010; year <= 2018; year++) {
  // Get initial deforestation
  var classification = mapbiomas.select('classification_' + year);
  var deforestation = classification.gte(400).and(classification.lt(500));
  
  // Check for cropland conversion in next 5 years
  var croplandConversion = ee.Image(0);
  for (var futureYear = year + 1; futureYear <= year + 5; futureYear++) {
    croplandConversion = croplandConversion.or(getCroplandMask(futureYear));
  }
  
  // Calculate area where deforestation was followed by cropland
  var cropDeforestation = deforestation.and(croplandConversion);
  var area = cropDeforestation.multiply(ee.Image.pixelArea().divide(10000));
  cropDeforestationImgs.push(area.rename('MB_crop_deforestation_' + year));
}

// Get cropland-driven forest loss for GFW (2010-2018)
var cropLossImgs = [];
for (var year = 2010; year <= 2018; year++) {
  // Get initial forest loss with 10% tree cover threshold
  var yearOffset = year - 2000;
  var treecover = gfw.select('treecover2000').gte(10);
  var loss = gfw.select('lossyear').eq(yearOffset).and(treecover);
  
  // Check for cropland conversion in next 5 years
  var croplandConversion = ee.Image(0);
  for (var futureYear = year + 1; futureYear <= year + 5; futureYear++) {
    croplandConversion = croplandConversion.or(getCroplandMask(futureYear));
  }
  
  // Calculate area where forest loss was followed by cropland
  var cropLoss = loss.and(croplandConversion);
  var area = cropLoss.multiply(ee.Image.pixelArea().divide(10000));
  cropLossImgs.push(area.rename('GFW_crop_forest_loss_' + year));
}

// Combine images and calculate statistics
var cropDeforestationAll = ee.Image.cat(cropDeforestationImgs);
var cropLossAll = ee.Image.cat(cropLossImgs);

var mapbiomasCropStats = cropDeforestationAll.reduceRegions({
  collection: biomes,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});

var gfwCropStats = cropLossAll.reduceRegions({
  collection: biomes,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});

// Export results
Export.table.toDrive({
  collection: mapbiomasCropStats,
  description: 'mapbiomas_crop_deforestation_2010_2018',
  fileFormat: 'CSV'
});

Export.table.toDrive({
  collection: gfwCropStats,
  description: 'gfw_crop_forest_loss_2010_2018',
  fileFormat: 'CSV'
});

// Print samples
print('Mapbiomas cropland sample:', mapbiomasCropStats.first());
print('GFW cropland sample:', gfwCropStats.first());

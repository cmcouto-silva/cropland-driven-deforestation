// Load datasets
var biomes = ee.FeatureCollection('projects/mapbiomas-territories/assets/TERRITORIES/LULC/BRAZIL/COLLECTION9/WORKSPACE/BIOMES');
var mapbiomas = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_deforestation_secondary_vegetation_v1');
var gfw = ee.Image('UMD/hansen/global_forest_change_2023_v1_11');

// Get deforestation for Mapbiomas
var deforestationImgs = [];
for (var year = 2010; year <= 2023; year++) {
  var classification = mapbiomas.select('classification_' + year);
  var deforestation = classification.gte(400).and(classification.lt(500));
  var area = deforestation.multiply(ee.Image.pixelArea().divide(10000));
  deforestationImgs.push(area.rename('MB_deforestation_' + year));
}

var deforestationAll = ee.Image.cat(deforestationImgs);

// Get forest loss for GFW
var lossImgs = [];
for (var year = 2010; year <= 2023; year++) {
  var yearOffset = year - 2000;
  var loss = gfw.select('lossyear').eq(yearOffset);
  var area = loss.multiply(ee.Image.pixelArea().divide(10000));
  lossImgs.push(area.rename('GFW_forest_loss_' + year));
}

var lossAll = ee.Image.cat(lossImgs);

// Calculate statistics by biome
var mapbiomasStats = deforestationAll.reduceRegions({
  collection: biomes,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});

var gfwStats = lossAll.reduceRegions({
  collection: biomes,
  reducer: ee.Reducer.sum(),
  scale: 30,
  tileScale: 4
});

// Export results
Export.table.toDrive({
  collection: mapbiomasStats,
  description: 'mapbiomas_deforestation_2010_2023',
  fileFormat: 'CSV'
});

Export.table.toDrive({
  collection: gfwStats,
  description: 'gfw_forest_loss_2010_2023',
  fileFormat: 'CSV'
});

// Print sample and add to map
print('Mapbiomas sample:', mapbiomasStats.first());
print('GFW sample:', gfwStats.first());
Map.addLayer(biomes, {}, 'Biomes');
Map.centerObject(biomes);

import ee 
import geemap

Map = geemap.Map()

# Import roads.
grip4_africa = ee.FeatureCollection(
  'projects/sat-io/open-datasets/GRIP4/Africa')
grip4_europe = ee.FeatureCollection(
  'projects/sat-io/open-datasets/GRIP4/Europe')
grip4_north_america = ee.FeatureCollection(
  'projects/sat-io/open-datasets/GRIP4/North-America')

# Check sizes
print('Grip4 Africa size', grip4_africa.size())
print('Grip4 North America size', grip4_north_america.size())
print('Grip4 Europe size', grip4_europe.size())

Map.setCenter(3.6, 32.5, 11)

# Display roads
Map.addLayer(grip4_africa.style(**{'color': '413B3A', 'width':1}),
             {},
             'Grip4 Africa')
Map.addLayer(grip4_north_america.style(**{'color': '413B3A', 'width':1}),
             {},
             'Grip4 North America')
Map.addLayer(grip4_europe.style(**{'color': '413B3A', 'width':1}),
             {},
             'Grip4 Europe')

# Import simplified countries
countries = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')

# Function to calculate feature's geometry area and adds it as a property
def addArea(feature):
  return feature.set({
    'areaKm': feature.geometry().area().divide(1000 * 1000) # km2 squared
  })


# Map the area getting function over the FeatureCollection.
countriesArea = countries.map(addArea)

# Filter to largest country in Africa
Algeria = countriesArea.filter(ee.Filter.inList('country_na', ['Algeria']))

# Display selected countries
Map.addLayer(Algeria.style(**{'fillColor': 'b5ffb4', 'color': '00909F', 'width': 1.0}),
             {},
             'Algeria')

# Calculate road length per country for the associated GRIP dataset.
def roadLength4Country(country, grip4):

  # Join roads to countries
  interesectsFilter = ee.Filter.intersects({
    'leftField': '.geo',
    'rightField': '.geo',
    'maxError': 10
  })

  grip4Selected = grip4.filterBounds(country)

  countriesWithRds = ee.Join.saveAll('roads').apply({
    'primary': country,
    'secondary': grip4Selected,
    'condition': interesectsFilter
  }).filter(ee.Filter.neq('roads', None))

  # Return country with road length and roads per km square km set

def func_ibq(country):
    roadsList = ee.List(country.get('roads'))
    roadLengths = roadsList.map(function(road) {
      return ee.Feature(road).intersection(country, 10).length(10)
    })
    roadLength = ee.Number(roadLengths.reduce(ee.Reducer.sum()))
    return country.set({
      'roadLength': roadLength.divide(1000), # Convert to km
      'roadsPerArea': roadLength.divide(ee.Number(country.get('areaKm')))
    })

  return countriesWithRds.map(func_ibq
).select(['country_na', 'areaKm','roadLength', 'roadsPerArea'])









).select(['country_na', 'areaKm','roadLength', 'roadsPerArea'])


# Apply road length function to Algeria
roadLengthAlgeria = roadLength4Country(Algeria, grip4_africa)

# Print statics for Algeria for roads per area
print('Roads statistics in Algeria', roadLengthAlgeria)

# Function to add line length in km
def addLength(feature):
  return feature.set({
    'lengthKm': feature.length().divide(1000) # km squared
  })


# Calculate line lengths for all roads in Africa
grip4_africaLength = grip4_africa.map(addLength)

# Compare with other value
print(grip4_africaLength.limit(1))

# Repeat analysis to calculate length of all roads
# Filter the table geographically: only keep roads in Algeria
grip4_Algeria = grip4_africaLength.filterBounds(Algeria)

# Visualize the output
Map.addLayer(grip4_Algeria.style(**{'color': 'green', 'width': 2.0}),
             {},
             'Algeria roads')

# Sum the lengths for roads in Algeria
sumLengthKmAlgeria = ee.Number(
  # Reduce to get the sum
  grip4_Algeria.reduceColumns(ee.Reducer.sum(), ['lengthKm']) \
    .get('sum')
)

# Print the result
print('Length of all roads in Algeria', sumLengthKmAlgeria)

# Repeat analysis again to calculate length of all roads using rasters
# Convert to raster
empty = ee.Image().float()

grip4_africaRaster = empty.paint({
  'featureCollection': grip4_africaLength,
  'color': 'lengthKm'
}).gt(0)

Map.addLayer(grip4_africaRaster,
             {'palette': ['orange'], 'max': 1},
             'Rasterized roads')

# Add reducer output to the Features in the collection.
AlgeriaRoadLength = ee.Image.pixelArea() \
  .addBands(grip4_africaRaster) \
  .reduceRegions({
    'collection': Algeria,
    'reducer': ee.Reducer.sum(),
    'scale': 100,

def func_bks(feature):
    num = ee.Number.parse(feature.get('area'))
    return feature.set('length', num.divide(1000).sqrt().round())

}).map(func_bks)





# Print the first feature, to illustrate the result.
print('Length of all roads in Algeria calculated via rasters',
      ee.Number(AlgeriaRoadLength.first().get('length')))

# Calculate line lengths for all roads in North America and Europe
grip4_north_americaLength = grip4_north_america.map(addLength)
grip4_europeLength = grip4_europe.map(addLength)

# Merge vectors
roadLengthMerge = grip4_africaLength.merge(grip4_north_americaLength) \
                      .merge(grip4_europeLength)

# Convert to raster
empty = ee.Image().float()

roadLengthMergeRaster = empty.paint({
  'featureCollection': roadLengthMerge,
  'color': 'roadsPerArea'
}).gt(0)

# Filter to largest countries in Africa, North America and Europe
countriesSelected = countries \
    .filter(ee.Filter.inList('country_na', ['Algeria', 'Canada', 'France']))

# Clip image to only countries of analysis
roadLengthMergeRasterClipped = roadLengthMergeRaster \
    .clipToCollection(countriesSelected)

# Add reducer output to the Features in the collection.
countriesRoadLength = ee.Image.pixelArea() \
  .addBands(roadLengthMergeRasterClipped) \
  .reduceRegions({
    'collection': countriesSelected,
    'reducer': ee.Reducer.sum(),
    'scale': 100,

def func_fgy(feature):
    num = ee.Number.parse(feature.get('area'))
    return feature.set('length', num.divide(1000).sqrt().round())

}).map(func_fgy)





# Compute totaled road lengths in km, grouped by country
print('Length of all roads in Canada',
    countriesRoadLength.filter(ee.Filter.equals('country_na', 'Canada')) \
        .aggregate_sum('length'))
print('Length of all roads in France',
    countriesRoadLength.filter(ee.Filter.equals('country_na', 'France')) \
        .aggregate_sum('length'))

# Examine effect of scale on raster
Map.addLayer(grip4_africaRaster.reproject({'crs': 'EPSG:4326', 'scale': 100}),
             {'palette': ['orange'], 'max': 1},
             'Rasterized roads 100 m')

# LGTM (nclinton). Reformatted. Added a setCenter.
Map
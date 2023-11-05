import ee 
import geemap

Map = geemap.Map()

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Chapter:      F4.0 Filter, Map, Reduce
#  Checkpoint:   F40a
#  Author:       Jeff Cardille
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

imgCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
# How many Tier 1 Landsat 5 images have ever been collected?
print("All images ever: ", imgCol.size()); # A very large number

# How many images were collected in the 2000s?
startDate = '2000-01-01'
endDate = '2010-01-01'

imgColfilteredByDate = imgCol.filterDate(startDate, endDate)
print("All images 2000-2010: ", imgColfilteredByDate.size())
# A smaller (but still large) number

ShanghaiImage = ee.Image(
    'LANDSAT/LT05/C02/T1_L2/LT05_118038_20000606')
Map.centerObject(ShanghaiImage, 9)

imgColfilteredByDateHere = imgColfilteredByDate.filterBounds(Map \
    .getCenter())
print("All images here, 2000-2010: ", imgColfilteredByDateHere \
.size()); 

L5FilteredLowCloudImages = imgColfilteredByDateHere \
    .filterMetadata('CLOUD_COVER', 'less_than', 50)
print("Less than 50% clouds in this area, 2000-2010",
    L5FilteredLowCloudImages.size()); # A smaller number

chainedFilteredSet = imgCol.filterDate(startDate, endDate) \
    .filterBounds(Map.getCenter()) \
    .filterMetadata('CLOUD_COVER', 'less_than', 50)
print('Chained: Less than 50% clouds in this area, 2000-2010',
    chainedFilteredSet.size())

efficientFilteredSet = imgCol.filterBounds(Map.getCenter()) \
    .filterDate(startDate, endDate) \
    .filterMetadata('CLOUD_COVER', 'less_than', 50)
print('Efficient filtering: Less than 50% clouds in this area, 2000-2010',
    efficientFilteredSet.size())

#  -----------------------------------------------------------------------
#  CHECKPOINT
#  -----------------------------------------------------------------------
Map
import json

import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiLineString
import matplotlib.pyplot as plt


# find the dimensions of the lcp file
#   * find code for this in Fangqi's repo
# draw a line of fire somewhere in it - can be deterministic position for our experiment
#   * would need geopandas - find helpful code in Fangqi's repo


def create_ignition_fire(geojson_file_path, output_path,
                         latitude_size=0.1, longitude_size=0.1, horizontal_offset=0.0, vertical_offset=0.0):
    geojson_file = open(geojson_file_path)
    space = json.loads(geojson_file.read())
    geojson_file.close()
    coordinates = space['features'][0]['geometry']['coordinates'][0]
    longitudes = sorted([coordinate[0] for coordinate in coordinates])
    latitudes = sorted([coordinate[1] for coordinate in coordinates])
    shape_height = (latitudes[-1] - latitudes[0]) * latitude_size
    shape_width = (longitudes[-1] - longitudes[0]) * longitude_size
    mid_long = (longitudes[0] + longitudes[-1]) / 2
    mid_lat = (latitudes[0] + latitudes[-1]) / 2
    shape_long = mid_long + horizontal_offset * shape_width
    shape_lat = mid_lat + vertical_offset * shape_height
    shape_coordinates = [(shape_long, shape_lat), (shape_long, shape_lat + shape_height),
                         (shape_long + shape_width, shape_lat + shape_height),
                         (shape_long + shape_width, shape_lat), (shape_long, shape_lat)]
    new_shape = gpd.GeoDataFrame()
    new_shape['geometry'] = None
    new_shape.loc[0, 'geometry'] = Polygon(shape_coordinates)
    # new_shape = gpd.GeoDataFrame(index=[0], geometry=Polygon(shape_coordinates))
    new_shape.plot()
    plt.show()
    new_shape.to_file(output_path)
    return new_shape

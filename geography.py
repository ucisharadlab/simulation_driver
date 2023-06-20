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
    longitudes = [-1976085.000000, -1968315.000000]  # sorted([coordinate[0] for coordinate in coordinates])
    latitudes = [1409085.000000, 1415115.000000]  # sorted([coordinate[1] for coordinate in coordinates])
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


def create_rxfire(folder_name, dir, UID):
    gap = 10
    offset = 20
    width = 3
    data = gpd.read_file(f"/Users/sriramrao/code/farsite/farsite_simulator/examples/FQ_burn/input/FQ_burn.shp")
    # Get Boundary:
    newdata = gpd.GeoDataFrame()
    newdata['geometry'] = None
    poly = data.loc[UID[0], 'geometry']
    poly = Polygon(poly)
    site = data.loc[UID[0], 'geometry']
    crs = data.crs
    x, y = site.exterior.coords.xy
    mx, my, bx, by = (min(x), min(y), max(x), max(y))
    x = mx + offset
    cout = 0
    while x < bx - offset:
        line = [(int(x), int(my) - 10), (int(x), int(by) + 10)]
        if poly.intersection(LineString(line)).geom_type == 'MultiLineString':
            for linestr in poly.intersection(LineString(line)):
                c = list(linestr.coords)
                y = [i[1] for i in c]
                if y[0] + offset < y[1] - offset:
                    coords = [(x, y[0] + offset), (x, y[1] - offset), (x + width, y[1] - offset),
                              (x + width, y[0] + offset), (x, y[0] + offset)]
                    newdata.loc[cout, 'geometry'] = Polygon(coords)
                    cout = cout + 1
                    # plt.plot([i[0] for i in coords], [i[1] for i in coords])
        else:
            c = list(poly.intersection(LineString(line)).coords)
            y = [i[1] for i in c]
            if y[0] + offset < y[1] - offset:
                coords = [(x, y[0] + offset), (x, y[1] - offset), (x + width, y[1] - offset),
                          (x + width, y[0] + offset), (x, y[0] + offset)]
                newdata.loc[cout, 'geometry'] = Polygon(coords)
                cout = cout + 1
                # plt.plot([i[0] for i in coords], [i[1] for i in coords])
        x = x + gap
    # newdata.to_file(f"{dir}/{folder_name}/input/{folder_name}.shp")
    data.plot()
    # plt.show()

    # newdata.to_file(f"{dir}/{foldername}/input/{foldername}.shp")
    return newdata

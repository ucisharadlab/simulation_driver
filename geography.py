import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiLineString
import matplotlib.pyplot as plt


# find the dimensions of the lcp file
#   * find code for this in Fangqi's repo
# draw a line of fire somewhere in it - can be deterministic position for our experiment
#   * would need geopandas - find helpful code in Fangqi's repo


def create_ignition_fire(space_shape_file, output_path):
    gap = 10
    offset = 20
    width = 3
    new_data = gpd.GeoDataFrame()
    new_data['geometry'] = None
    space = gpd.read_file(space_shape_file)
    poly = space.loc[0, 'geometry']
    poly = Polygon(poly)
    site = space.loc[0, 'geometry']
    x, y = site.exterior.coords.xy
    mx, my, bx, by = (min(x), min(y), max(x), max(y))
    x = mx + offset
    cout = 0

    while x < bx - offset:
        line = [(int(x), int(my) - 10), (int(x), int(by) + 10)]
        if poly.intersection(LineString(line)).geom_type == 'MultiLineString':
            for line in poly.intersection(LineString(line)):
                c = list(line.coords)
                y = [i[1] for i in c]
                if y[0] + offset < y[1] - offset:
                    coords = [(x, y[0] + offset), (x, y[1] - offset), (x + width, y[1] - offset),
                              (x + width, y[0] + offset), (x, y[0] + offset)]
                    new_data.loc[cout, 'geometry'] = Polygon(coords)
                    cout = cout + 1
                    plt.plot([i[0] for i in coords], [i[1] for i in coords])
        else:
            c = list(poly.intersection(LineString(line)).coords)
            y = [i[1] for i in c]
            if y[0] + offset < y[1] - offset:
                coords = [(x, y[0] + offset), (x, y[1] - offset), (x + width, y[1] - offset),
                          (x + width, y[0] + offset), (x, y[0] + offset)]
                new_data.loc[cout, 'geometry'] = Polygon(coords)
                cout = cout + 1
                plt.plot([i[0] for i in coords], [i[1] for i in coords])
        x = x + gap
        # new_data.to_file(output_path)
        new_data.plot()
        plt.show()

        new_data.to_file(output_path)
        return new_data

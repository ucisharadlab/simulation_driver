import geopandas as gpd
import os
import numpy as np
from shapely.geometry import shape, Point, mapping, LineString, Polygon


# This file is to map polygon of each timestep to 0-1 cells


def generate_points_set(x_min, y_min, x_max, y_max, unit):
    points_set = []
    xlen = x_max - x_min
    ylen = y_max - y_min
    x, y = x_min, y_min
    while y <= y_max:
        y += unit
        x = x_min
        while x <= x_max:
            x += unit
            points_set.append(Point(x - unit / 2, y - unit / 2))
    return points_set


def generate_poly_dict(df, TE=None):
    poly_dict = {}
    # if TE == None:
    #     for i in df.values:
    #         # shp = df1.loc[i, 'geometry']
    #         Month, Day, Hour = i[1], i[2], i[3]
    #         # print(Month,Day,Hour)
    #         # calculate the time in unit of minutes from May 4th 00:00 to the simulation time,
    #         # as filename (also integer key of polygon dictionary)
    #         time_instance = int((Day - 4) * 24 * 60 + (Hour // 100) * 60 + (Hour % 100))
    #         if time_instance not in poly_dict:
    #             poly_dict[time_instance] = []  # let same time instance geometry data to be placed in same dict key.
    #         poly = Polygon(i[5])  ## i[5] -> df1['geometry']
    #         poly_dict[time_instance].append(poly)
    #         # print(poly_dict)
    # else:  # TE is specified, and is a list
    # for i in df.values:
        # shp = df1.loc[i, 'geometry']
    Month, Day, Hour = 5, 4, 2  # i[1], i[2], i[3]
    time_instance = int((Day - 4) * 24 * 60 + (Hour // 100) * 60 + (Hour % 100))
    if time_instance not in poly_dict:
        poly_dict[time_instance] = []
    poly = Polygon(df)
    poly_dict[time_instance].append(poly)
    return poly_dict


def get_centroid(poly_dict):
    centroid_dict = {}
    for time_instance in poly_dict:
        polygon_list = poly_dict[time_instance]
        centroid_list = []
        for poly in polygon_list:
            centroid_list.append(poly.centroid)
        if time_instance not in centroid_dict:
            num = len(gpd.GeoSeries(centroid_list))
            centroid_dict[time_instance] = (
                sum(gpd.GeoSeries(centroid_list).x) / num, sum(gpd.GeoSeries(centroid_list).y) / num)
    return centroid_dict


def get_fire_mapping(surface, points_set, xnum, save_path):
    row = ''
    cell_counter = 0
    for cell in points_set:
        if cell_counter >= xnum:
            row += '\n'
            cell_counter = 0
        fire_flag = 0
        for poly in surface:
            dist = cell.distance(poly)
            if dist <= 0.0:
                fire_flag = 1
                break
        row += str(fire_flag) + ','
        cell_counter += 1

    f = open(save_path, 'w')
    f.writelines(row)
    f.close()
    return 0


def generate_cell_mapping(df_file, target_path, x_min, y_min, x_max, y_max, unit=10, TE=None):
    df1 = gpd.read_file(df_file)
    poly_dict = generate_poly_dict(df1, TE)
    ##
    # centroid_dict = get_centroid(poly_dict)
    # print(centroid_dict)
    ##
    points_set = generate_points_set(x_min, y_min, x_max, y_max, unit)
    xlen = x_max - x_min
    xnum = (xlen // unit) + 1
    # print('xlen=',xlen)
    # print('xnum=',xnum)
    for time_instance in poly_dict:
        surface = poly_dict[time_instance]
        save_filename = str(time_instance) + '.csv'
        # print(save_filename)
        # os.system('touch \'' + target_path + '/' + save_filename + '\'')

        save_filepath = os.path.join(target_path, save_filename)
        # get_fire_mapping(surface, points_set, xnum, save_filepath)
    return 0


def read_save_path(read_path, target_path, project_name):
    df_filename = project_name + 'Perimeters.shp'
    df_file_list = []
    savepath_list = []
    for dirname in os.listdir(read_path):
        if dirname == '.DS_Store':
            continue
        df_file_list.append(os.path.join(read_path, dirname, df_filename))
        cmd = 'mkdir ' + target_path + '/' + dirname
        savepath_list.append(os.path.join(target_path, dirname))
        os.system(cmd)
    return df_file_list, savepath_list


def get_coord_bound(map_file):
    # map_file = '/Users/delilah/Documents/Research/Sparx/farsite/examples/FQ_new/input/FQ_burn.shp'
    df = gpd.read_file(map_file)
    geometry1 = [i for i in df.geometry]

    x, y = geometry1[-1].exterior.coords.xy
    coords = np.dstack((x, y)).tolist()
    xlist = [coords[0][i][0] for i in range(len(coords[0]))]
    ylist = [coords[0][i][1] for i in range(len(coords[0]))]

    return min(xlist), min(ylist), max(xlist), max(ylist)


def create_directory(full_path: str) -> None:
    os.system(f"mkdir -p {full_path}")


if __name__ == '_main__':
    # Bursite = (702460.0, 4309700.0, 703540.0, 4310820.0)#x,y: 1080*1120
    x_min, y_min, x_max, y_max = 702200.0, 4309600.0, 702900.0, 4310200.0  # insert the boundary of map on figure
    # map_file = '/Users/delilah/Documents/Research/Sparx/farsite/examples/FQ_new/output0226_origin/outputFQ_new_1_1_1/FQ_new_Ignitions_Perimeters.shp'
    # x_min,y_min,x_max,y_max = get_coord_bound(map_file)
    # print(x_min,y_min,x_max,y_max)
    unit = 10  # indicate the level of resolution interpreting the perimeter to cells, min is 1
    # scale = 20
    # x_min,y_min,x_max,y_max = x_min-unit*scale,y_min-unit*scale,x_max+unit*scale,y_max+unit*scale

    xlen = x_max - x_min
    ylen = y_max - y_min
    project_name = 'Burn'
    root_path = '/Users/sriramrao/code/farsite/farsite_output'
    TE = [10, 20, 30, 60, 90, 120]

    # # target_path = '/Users/delilah/Documents/Research/Sparx/output_comp/cell_mapping_ana1'
    # # read_path = '/Users/delilah/Documents/Research/Sparx/output_comp/FQ_burn_output/output_ana1'
    ground_truth = root_path + '/ground_truth/burn_5_1_1_05_04_0000_05_04_0500'
    read_paths = ['time_extent', 'timestep', "perimeter_res", "perimeter_res_1",
                  "perimeter_res_15", "perimeter_res_30", "perimeter_res_45",
                  "perimeter_res_60", "perimeter_res_75", "perimeter_res_90"]
    # read_path = f'{root_path}time_extent/' #root_path + project_name + 'output0226'
    target_path = root_path + project_name + '_cell_mapping_time_extent'
    for read_path in read_paths:
        search_path = f"{root_path}/{read_path}/"
        target_path = f"{root_path}/{project_name}_cell_mapping_{read_path}"
        create_directory(target_path)
        df_file_list, savepath_list = read_save_path(search_path, target_path, project_name)
        for idx in range(len(df_file_list)):
            df_file = df_file_list[idx]
            print(df_file + "\n")
            if not os.path.isfile(df_file):
                continue
            savepath = savepath_list[idx]
            generate_cell_mapping(df_file, savepath, x_min, y_min, x_max, y_max, unit)

#### back up: plot one point and the surface for each time instance :
# a = Point(702600,4310000)
# for time_instance in poly_dict:
#     surface = poly_dict[time_instance]
#     gpd.GeoSeries(a).plot()
#     print('surface: ',time_instance)
#     for p in surface:
#         x,y = p.exterior.coords.xy
#         print(a.distance(p))
#         plt.plot(x, y, c='red')
#     plt.show()

#### end back up

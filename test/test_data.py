from repo.edb_repo import prepare_test_data_row


def get_data():
    return {(120, 5, 5, 5): (3, 0.7),
            (120, 10, 5, 5): (1.5, 0.6),
            (120, 8, 10, 10): (0.5, 0.55)}


def get_query_load():
    return [{"name": "Fire Query",
             "query": "SELECT cell_id FROM fire_map WHERE fire_presence = 1",
             "output_type": "fire_presence",
             "simulation_id": "ABC123"}]


planner_data = [('{"%start_locations%": ["35.727513, -118.786136"], "%output_grids%": [{"%centre%":"35.727513, '
                 '-118.786136","%spacing%":"0.09 0.09","%span%":"2.0 4.0",'
                 '"%dir%":"./debug/hysplit_out/default/start-1-sample-5/","%file%":"dump_default",'
                 '"%vertical_level%":"1\n50","%sampling%":"00 00 00 00 00\n00 00 00 00 00\n00 00 05"}]}',
                 800, 0.4),
                ('{"%start_locations%": ["35.727513, -118.786136"], "%output_grids%": [{"%centre%":"35.727513, '
                 '-118.786136","%spacing%":"0.09 0.09","%span%":"2.0 4.0",'
                 '"%dir%":"./debug/hysplit_out/default/start-1-sample-5/","%file%":"dump_default",'
                 '"%vertical_level%":"1\n50","%sampling%":"00 00 00 00 00\n00 00 00 00 00\n00 00 05"}]}',
                1000, 0.7),
                ('{"%start_locations%": ["35.727513, -118.786136"], "%output_grids%": [{"%centre%":"35.727513, '
                 '-118.786136","%spacing%":"0.1 0.1","%span%":"2.0 4.0",'
                 '"%dir%":"./debug/hysplit_out/default/start-1-sample-60/","%file%":"dump_default",'
                 '"%vertical_level%":"1\n50","%sampling%":"00 00 00 00 00\n00 00 00 00 00\n00 01 00"}]}',
                120, 0.3),
                ('{"%start_locations%": ["35.727513, -118.786136", "35.726513, -118.788136", "35.728513, '
                 '-118.788136", "35.725513, -118.787136", "35.729513, -118.787136"], "%output_grids%": [{'
                 '"%centre%":"35.727513, -118.786136","%spacing%":"0.05 0.05","%span%":"5.0 10.0",'
                 '"%dir%":"./debug/hysplit_out/default/start-5-sample-15-run-20/","%file%":"dump_default",'
                 '"%vertical_level%":"1\n50","%sampling%":"00 00 00 00 00\n00 00 00 00 00\n00 01 00"}]}',
                2000, 1.0)]

data_queries = [{"id": "1",
                 "query": "SELECT location, name, concentration FROM concentration_data WHERE concentration > 0.3",
                 "output_type": "concentration"}]

slow_params = {"%start_locations%": ["35.727513, -118.786136", "35.726513, -118.788136", "35.728513, -118.788136",
                                     "35.725513, -118.787136", "35.729513, -118.787136"], "%output_grids%": [
    {"%centre%": "35.727513, -118.786136", "%spacing%": "0.05 0.05", "%span%": "5.0 10.0",
     "%dir%": "./debug/hysplit_out/default/slow-start-5-sample-15-run-20/", "%file%": "dump_default",
     "%vertical_level%": "1\n50", "%sampling%": "00 00 00 00 00\n00 00 00 00 00\n00 01 00"}]}


def get_test_planner_data():
    test_data = dict()
    for row in planner_data:
        test_row = prepare_test_data_row(row)
        test_data[test_row[0]] = test_row[1]
    return test_data

# create_rxfire("", "", [2])
# create_ignition_fire("./lcp/LCP_LF2022_FBFM13_220_CONUS.GeoJSON", "./lcp/barrier.shp", latitude_size=0.1,
#                      longitude_size=0.1, horizontal_offset=0.05, vertical_offset=-0.05)
# read_experiment_latencies(
#     "/home/sriram/code/farsite/farsite_simulator/examples/FQ_burn/output/timestep/")

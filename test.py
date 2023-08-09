def get_data():
    return {(120, 5, 5, 5): (3, 0.7),
            (120, 10, 5, 5): (1.5, 0.6),
            (120, 8, 10, 10): (0.5, 0.55)}


def get_query_load():
    return [{"name": "Fire Query",
             "query": "SELECT cell_id FROM fire_map WHERE fire_presence = 1",
             "output_type": "fire_presence",
             "simulation_id": "ABC123"}]


# create_rxfire("", "", [2])
# create_ignition_fire("./lcp/LCP_LF2022_FBFM13_220_CONUS.GeoJSON", "./lcp/barrier.shp", latitude_size=0.1,
#                      longitude_size=0.1, horizontal_offset=0.05, vertical_offset=-0.05)
# read_experiment_latencies(
#     "/home/sriram/code/farsite/farsite_simulator/examples/FQ_burn/output/timestep/")

-- see simulators
select * from simulator;

-- add a new simulator
SELECT create_simulator('hysplit', 'simulator.hysplit.Hysplit', 'concentration', 'plan.planner.GreedyPlanner', '{"%name%":"test_helpers","%start_locations%":["35.727513, -118.786136"],"%total_run_time%":"240","%input_data_grids%":[{"%dir%":"/Users/sriramrao/code/hysplit/hysplit/working/","%file%":"oct1618.BIN"}],"%pollutants%":[{"%id%":"AIR1","%emission_rate%":"50.0","%emission_duration_hours%":"96.0","%release_start%":"00 00 00 00 00"}],"%output_grids%":[{"%centre%":"35.727513, -118.786136","%spacing%":"0.1 0.1","%span%":"10.0 10.0","%dir%":"./","%file%":"cdump_CA","%vertical_level%":"1\n50","%sampling%":"00 00 00 00 00\n00 00 00 00 00\n00 01 00"}],"%deposition%":["0.0 0.0 0.0\n0.0 0.0 0.0 0.0 0.0\n0.0 0.0 0.0\n0.0\n0.0"],"%params%":"%name%_%start_locations_count%_%total_run_time%_%output_grids_count%","%control_file%":[{"%template_path%":"/Users/sriramrao/code/farsite/farsite_driver/examples/hysplit","%template_file%":"CONTROL_template","%name%":"CONTROL","%path%":"./"}],"%keys_with_count%":["%start_locations%","%input_data_grids%","%output_grids%","%pollutants%"]}');

select * from simulator;

-- add a dummy one to demo drop
SELECT create_simulator('remove_me', 'simulator.hysplit.Hysplit', 'concentration', 'plan.planner.GreedyPlanner', '{"%name%":"test_helpers"}');

select * from simulator;

-- remove
SELECT drop_simulator('remove_me');

select * from simulator;

-- configuring table columns
SELECT * FROM simulated_columns;

SELECT add_simulated_column('pollutant concentration', 'concentration_data', 'concentration', 'location', 'concentration');

SELECT * FROM simulated_columns;

-- test data for planner to learn from
SELECT * FROM hysplit_test_data;

SELECT learn('hysplit', 'hysplit_test_data');

-- learn is added as part of the workload
select id, query, status from query_workload;

-- query for data
SELECT insert_query('SELECT location, name, concentration FROM concentration_data WHERE concentration > 0.3');

select id, query, status from query_workload;

-- see if there is data 
SELECT id, location, name, concentration FROM concentration_data WHERE concentration > 0.3 ORDER BY id ASC;
SELECT count(*) FROM concentration_data WHERE concentration > 0.3 

-- there isn't
-- we didn't start the simulator
SELECT * FROM simulator_status;

SELECT start_simulator('hysplit');

SELECT * FROM simulator_status;

-- refresh for data 
SELECT id, location, name, concentration FROM concentration_data WHERE concentration > 0.3 ORDER BY id ASC;

-- stop when done
SELECT stop_simulator('hysplit');

SELECT * FROM simulator_status;

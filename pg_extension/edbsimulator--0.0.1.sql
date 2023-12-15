CREATE OR REPLACE FUNCTION
add_simulator(
	name	TEXT,
	class_name	TEXT,
	output_type	TEXT,
    planner_name    TEXT,
	parameters	TEXT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO simulator (name, class_name, output_type, planner, parameters) VALUES
    (name, class_name, output_type, planner_name, parameters);
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
drop_simulator(
	name	TEXT
)
RETURNS VOID AS $$
BEGIN
    DELETE FROM simulator WHERE name = name
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
update_simulator(
	name	TEXT,
	class_name	TEXT,
	output_type	TEXT,
	parameters	TEXT
)
RETURNS VOID AS $$
BEGIN
    SELECT drop_simulator(name);
    SELECT create_simulator(name, class_name, output_type, parameters);
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
get_simulators(
	type	TEXT
)
RETURNS TABLE (LIKE simulator) AS $$
BEGIN
	RETURN QUERY SELECT id, name, class_name, planner, output_type FROM simulator WHERE output_type = type;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
add_simulated_column(
	name	TEXT,
	table_name	TEXT,
    column_name  TEXT,
	type_key	TEXT,
	data_type	TEXT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO simulated_columns (name, table_name, column_name, type_key, data_type) VALUES
    (name, table_name, column_name, type_key, data_type);
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
drop_simulated_column(
	column_name	TEXT
)
RETURNS VOID AS $$
BEGIN
    DELETE FROM simulated_columns WHERE name = column_name
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
start_simulator(
	name	TEXT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO simulator_status(simulator_name, status, start_time) VALUES
    (name, 0, NOW())
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
stop_simulator(
	name	TEXT
)
RETURNS VOID AS $$
BEGIN
    UPDATE simulator_status SET status = 1, end_time = NOW() WHERE simulator_name = name AND status = 0
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
learn(
	simulator_name	TEXT,
    test_data_table TEXT DEFAULT '%NULL%'
)
RETURNS VOID AS $$
DECLARE
    planner_name TEXT := '';
BEGIN
    SELECT planner FROM simulator WHERE name = simulator_name INTO planner_name;
	PERFORM insert_query(CONCAT('learn:', simulator_name, ':', planner_name, ':', test_data_table), 0, 0);
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION rewrite_simulator_query(
	query    TEXT
)
RETURNS TEXT AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.rewrite_query(query)

$$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION insert_query(
   IN _query    TEXT,
   IN _refresh_interval INTEGER,
   IN _refresh_count    INTEGER,
   OUT _id  INTEGER
) LANGUAGE sql
AS $BODY$
    INSERT INTO query_workload(query, refresh_interval, refresh_count, status)
    VALUES(_query, _refresh_interval, _refresh_count, 0)
    RETURNING id;
$BODY$;

CREATE OR REPLACE PROCEDURE run_simulation_query(
    query   TEXT,
	refresh_interval_minutes    INTEGER,
	refresh_count   INTEGER,
    query_name TEXT
)
LANGUAGE plpgsql
AS
$BODY$
DECLARE
    counter INTEGER := 0 ;
    _id BIGINT := -1;
    view_name TEXT := CONCAT('sim_', query_name);
    view_query TEXT := '';
    refresh_query TEXT := 'SELECT * FROM ' || view_name;
BEGIN
    SELECT insert_query(query, refresh_interval_minutes, refresh_count) INTO _id;
    view_query := rewrite_simulator_query(query);
    RAISE NOTICE 'VIEW QUERY: %', view_query;
    EXECUTE 'CREATE INCREMENTAL MATERIALIZED VIEW $1 AS $2'  view_name, view_query;

	LOOP
	    EXIT WHEN counter = refresh_count;
	    RAISE NOTICE 'Refreshing';
        EXECUTE refresh_query;
        RAISE NOTICE 'Refreshed % time(s)', counter;
        counter := counter + 1;
		PERFORM pg_sleep(delay);
	END LOOP ;
	UPDATE query_workload SET status = 1 WHERE id = _id;

END;
$BODY$;

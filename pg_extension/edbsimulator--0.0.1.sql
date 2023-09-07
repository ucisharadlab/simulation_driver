CREATE OR REPLACE FUNCTION
create_simulator(
	name	TEXT,
	class_name	TEXT,
	output_type	TEXT,
	parameters	TEXT
)
RETURNS VOID AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.create_simulator(name, class_name, output_type, parameters)

$$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION
drop_simulator(
	name	TEXT
)
RETURNS VOID AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.remove_simulator(name)

$$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION
update_simulator(
	name	TEXT,
	class_name	TEXT,
	output_type	TEXT,
	parameters	TEXT
)
RETURNS VOID AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.update_simulator(name, class_name, output_type, parameters)

$$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION
get_simulators(
	type	TEXT
)
RETURNS TABLE (LIKE simulator) AS $$
BEGIN
	RETURN QUERY SELECT * FROM simulator WHERE output_type = type;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION
add_simulated_column(
	name	TEXT,
	table_name	TEXT,
    column_name  TEXT,
	type_key	TEXT[],
	data_type	TEXT
)
RETURNS VOID AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.add_simulated_column(name, table_name, column_name, type_key, data_type)

$$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION
drop_simulated_column(
	name	TEXT
)
RETURNS VOID AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.remove_simulated_column(name)

$$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION
start_simulator(
	name	TEXT
)
RETURNS VOID AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.start_simulator(name)

$$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION
stop_simulator(
	name	TEXT
)
RETURNS VOID AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.stop_simulator(name)

$$ LANGUAGE plpython3u;

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
   IN _query    INTEGER,
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
    SELECT rewrite_simulator_query(query) INTO view_query;
    EXECUTE 'CREATE INCREMENTAL MATERIALIZED VIEW $1 AS $2', view_name, view_query;

	LOOP
	    EXIT WHEN counter = refresh_count;
        EXECUTE '$1' USING refresh_query;
        RAISE NOTICE 'Refreshed % time(s)', counter;
        counter := counter + 1;
		PERFORM pg_sleep(delay);
	END LOOP ;
	UPDATE query_workload SET status = 1 WHERE id = _id;

END;
$BODY$;

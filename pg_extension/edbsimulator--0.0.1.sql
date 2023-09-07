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

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.get_simulators(type)

$$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION
add_simulated_column(
	name	TEXT,
	table_name	TEXT,
	type_key	TEXT[],
	data_type	TEXT
)
RETURNS VOID AS $$

import sys
sys.path.insert(1, "/usr/local/lib/python3.11/site-packages/")
sys.path.insert(1, "/Users/sriramrao/code/farsite/farsite_driver/pg_extension")
import metadata_access

return metadata_access.add_simulated_column(name, table_name, type_key, data_type)

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

CREATE OR REPLACE PROCEDURE check_kill(
	num_epoch INTEGER,
	delay INTEGER
)
LANGUAGE plpgsql
AS
$BODY$
DECLARE
   counter INTEGER := 0 ;
BEGIN
	LOOP
		RAISE NOTICE 'Sleeping';
		PERFORM pg_sleep(delay);
	END LOOP ;

END;
$BODY$;

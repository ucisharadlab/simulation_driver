CREATE TABLE simulator(
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    class_name VARCHAR(250) NOT NULL,
    output_type VARCHAR(250) NOT NULL,
    planner VARCHAR(250) NOT NULL, 
    parameters JSON NOT NULL
);

CREATE TABLE simulated_column (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(250) NOT NULL UNIQUE,
    table_name VARCHAR(250) NOT NULL,
    column_name TEXT NOT NULL,
    type_key TEXT,
    data_type VARCHAR(250) NOT NULL
);

CREATE TABLE simulation_log (
    id SERIAL PRIMARY KEY,
    simulator TEXT NOT NULL,
    params JSON,
    execution_info JSON,
    timestamp TIMESTAMP
);

CREATE TABLE query_workload (
    id SERIAL PRIMARY KEY,
    query TEXT,
    refresh_interval DECIMAL,
    refresh_count INTEGER,
    status INTEGER,
    start_time TIMESTAMP,
);

CREATE TABLE simulator_status (
    id SERIAL PRIMARY KEY,
    simulator_name TEXT,
    status INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

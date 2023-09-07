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
    column VARCHAR(250) NOT NULL,
    data_type VARCHAR(250) NOT NULL
);

CREATE TABLE simulation_log (
    id SERIAL PRIMARY KEY,
    simulator_id int NOT NULL,
    params JSON,
    timestamp date,
    execution_info JSON
);


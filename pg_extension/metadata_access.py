import plpy


def create_simulator(name, class_name, output_type, parameters):
    plpy.execute(f"INSERT INTO simulator (name, class_name, output_type, parameters) VALUES "
                     f"('{name}', '{class_name}', '{output_type}', '{parameters}')")

def remove_simulator(name):
    plpy.notice(f"Entered remove: {name}")
    plpy.execute(f"DELETE FROM simulator WHERE name = '{name}'")


def update_simulator(name: str, new_class_name: str, new_type: str, new_parameters: str):
    plpy.notice(f"Entered update: {name}")
    remove_simulator(name)
    create_simulator(name, new_class_name, new_type, new_parameters)


def get_simulators(output_type):
    plpy.notice(f"Entered get: {output_type}")
    result = plpy.execute(f"SELECT * FROM simulator WHERE output_type = '{output_type}'")
    row_count = result.nrows()
    return result[0:row_count]


def add_simulated_column(name: str, table: str, column: str, type_key: [str], data_type: str):
    plpy.notice(f"Entered add columns: {name}")
    plpy.execute(f"INSERT INTO simulated_columns (name, table_name, column_name type_key, data_type) VALUES "
                 f"('{name}', '{table}', '{column}' '{','.join(type_key)}', '{data_type}')")


def remove_simulated_column(name: str):
    plpy.notice(f"Entered remove columns: {name}")
    plpy.execute(f"DELETE FROM simulated_columns WHERE name = '{name}'")


def start_simulator(name: str):
    plpy.notice(f"Start: {name}")
    plpy.execute(f"INSERT INTO simulator_status(simulator, status, start_time) VALUES "
                 f"('{name}', 0, NOW())")


def stop_simulator(name: str):
    plpy.notice(f"Stop: {name}")
    plpy.execute(f"UPDATE simulator_status SET status = 1 WHERE simulator = {name} AND status = 0")

def rewrite_query(query: str):
    query = (query.replace("SELECT", "%%")
             .replace("FROM", "%%")
             .replace("WHERE", "%%"))
    select_query, from_query, where_query = query.split("%%")
    columns = [column.strip() for column in select_query.split(',')]

    for column in columns:
        result = plpy.execute(f"SELECT column_name, type_key, data_type FROM simulated_column "
                          f"WHERE table_name = {from_query} AND column_name = {column}")
        if not result: continue
        column_name = column
        output_type = result[0]["data_type"]
        join_key = result[0]["type_key"]

    select_query += f", value_timestamp AS time, value AS {column_name}"
    join_clause = f"{from_query} T INNER JOIN {output_type}_data D ON T.{join_key} = D.{join_key}"
    return f"SELECT {select_query} FROM {join_clause} WHERE {where_query}"

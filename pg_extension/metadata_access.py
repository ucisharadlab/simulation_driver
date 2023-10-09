import plpy


def create_simulator(name, class_name, output_type, planner_name, parameters):
    plpy.execute(f"INSERT INTO simulator (name, class_name, output_type, planner, parameters) VALUES "
                     f"('{name}', '{class_name}', '{output_type}', '{planner_name}', '{parameters}');")
    # plpy.execute(f"CREATE TABLE {output_type}_data (row_key TEXT, value_timestamp TIMESTAMP, value JSON);")

def remove_simulator(name):
    plpy.notice(f"Remove: {name}")
    plpy.execute(f"DELETE FROM simulator WHERE name = '{name}'")


def update_simulator(name: str, new_class_name: str, new_type: str, new_parameters: str):
    plpy.notice(f"Update: {name}")
    remove_simulator(name)
    create_simulator(name, new_class_name, new_type, new_parameters)


def get_simulators(output_type):
    plpy.notice(f"Get: {output_type}")
    result = plpy.execute(f"SELECT * FROM simulator WHERE output_type = '{output_type}'")
    row_count = result.nrows()
    return result[0:row_count]


def add_simulated_column(name: str, table: str, column: str, type_key: str, data_type: str):
    plpy.notice(f"Add column: {name}")
    plpy.execute(f"INSERT INTO simulated_columns (name, table_name, column_name, type_key, data_type) VALUES "
                 f"('{name}', '{table}', '{column}', '{type_key}', '{data_type}')")


def remove_simulated_column(name: str):
    plpy.notice(f"Remove column: {name}")
    plpy.execute(f"DELETE FROM simulated_columns WHERE name = '{name}'")


def start_simulator(name: str):
    plpy.notice(f"Start: {name}")
    plpy.execute(f"INSERT INTO simulator_status(simulator_name, status, start_time) VALUES "
                 f"('{name}', 0, NOW())")


def stop_simulator(name: str):
    plpy.notice(f"Stop: {name}")
    plpy.execute(f"UPDATE simulator_status SET status = 1, end_time = NOW() WHERE simulator_name = '{name}' AND status = 0")

def rewrite_query(query: str):
    plpy.notice("Rewriting query")
    query = (query.replace("SELECT", "%%")
             .replace("FROM", "%%")
             .replace("WHERE", "%%"))
    plpy.notice(query.split("%%"))
    _, select_query, from_query, where_query = query.split("%%")
    columns = [column.strip() for column in select_query.split(',')]
    from_query = from_query.strip()

    column_details = dict()
    for column in columns:
        check_query = (f"SELECT column_name, type_key, data_type FROM simulated_columns "
                       f"WHERE table_name = '{from_query}' AND column_name = '{column}'")
        plpy.notice(check_query)
        result = plpy.execute(check_query)
        plpy.notice(result)
        if len(result) == 0: continue
        column_details = result[0]
        break
    column_name = column_details["column_name"]
    output_type = column_details["data_type"]
    join_key = column_details["type_key"]

    select_query = select_query.replace(f", {column_name}", "")
    select_query += f", value_timestamp AS time, value AS {column_name}"
    join_clause = f"{from_query} T INNER JOIN {output_type}_data D ON T.{join_key} = D.row_key"
    new_query = f"SELECT {select_query} FROM {join_clause} WHERE {where_query}"
    new_query = new_query.replace("\"", "'")
    plpy.notice(f"Rewritten query: {new_query}")
    return new_query

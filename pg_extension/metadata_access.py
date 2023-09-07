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


def add_simulated_column(name: str, table: str, type_key: [str], data_type: str):
    plpy.notice(f"Entered add columns: {name}")
    plpy.execute(f"INSERT INTO simulated_columns (name, table_name, type_key, data_type) VALUES "
                 f"('{name}', '{table}', '{','.join(type_key)}', '{data_type}')")


def remove_simulated_column(name: str):
    plpy.notice(f"Entered remove columns: {name}")
    plpy.execute(f"DELETE FROM simulated_columns WHERE name = '{name}'")


def start_simulator(name: str):
    plpy.notice(f"Start: {name}")


def stop_simulator(name: str):
    plpy.notice(f"Stop: {name}")

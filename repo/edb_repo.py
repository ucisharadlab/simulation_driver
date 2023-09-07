from repo.sql_repo import SqlRepo


class EdbRepo(SqlRepo):
    def add_simulator(self, name: str, class_name: str, output_type: str, parameters: str):
        self.execute(f"INSERT INTO simulator (name, class_name, output_type, parameters) VALUES "
                     f"('{name}', '{class_name}', '{output_type}', '{parameters}')")

    def remove_simulator(self, name: str):
        self.execute(f"DELETE FROM simulator WHERE name = '{name}'")

    def update_simulator(self, name: str, new_class_name: str, new_type: str, new_parameters: str):
        self.remove_simulator(name)
        self.add_simulator(name, new_class_name, new_type, new_parameters)

    def get_simulators(self, output_type: str):
        return self.fetch_entities(f"SELECT * FROM simulator WHERE output_type = '{output_type}'")

    def add_simulated_columns(self, name: str, table: str, key_columns: [str], columns: [str], data_type: str):
        self.execute(f"INSERT INTO simulated_columns (name, table_name, key_columns, columns, data_type) VALUES "
                     f"('{name}', '{table}', '{','.join(key_columns)}', '{','.join(columns)}', '{data_type}')")

    def remove_simulated_columns(self, name: str, column: str):
        self.execute(f"DELETE FROM simulated_columns WHERE name = '{name}'")

    def update_simulated_column(self, name: str, table: str, key_columns: [str], column: str, new_type: str):
        self.remove_simulated_columns(name, column)
        self.add_simulated_columns(name, table, key_columns, column, new_type)

    def store_result(self, simulation_name: str, rows: [dict]):
        for row in rows:
            self.execute(f"UPDATE fire_map SET fire_presence = {row['fire_presence']} WHERE cell_id = {row['cell_id']}")

    def get_query_load(self) -> [dict]:
        self.fetch_entity("SELECT * FROM simulator LIMIT 1")  # TODO: change query
        return [{}]

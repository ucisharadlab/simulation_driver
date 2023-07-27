from repo.sql_repo import SqlRepo


class EdbRepo(SqlRepo):
    def add_simulator(self, name: str, class_name: str, output_type: str):
        self.execute(f"INSERT INTO simulator (name, class, output_type) VALUES ('${name}', "
                     f"'${class_name}', '${output_type}')")

    def remove_simulator(self, name: str):
        self.execute(f"DELETE FROM simulator WHERE name = '${name}')")

    def update_simulator(self, name: str, new_class_name: str, new_type: str):
        self.remove_simulator(name)
        self.add_simulator(name, new_class_name, new_type)

    def get_simulators(self, output_type: str):
        return self.fetch_entities(f"SELECT * FROM simulator WHERE output_type = '${output_type}'")

    def add_simulated_columns(self, name: str, table: str, key_columns: [str], columns: [str], data_type: str):
        self.execute(f"INSERT INTO simulated_columns (name, table, key_columns, columns, type) VALUES "
                     f"('${name}' '${table}', '${','.join(key_columns)}', '${','.join(columns)}', '${data_type}')")

    def remove_simulated_columns(self, name: str, column: str):
        # TODO: Change to update
        self.execute(f"DELETE FROM simulated_columns WHERE name = '${name}')")

    def update_simulated_column(self, name: str, table: str, key_columns: [str], column: str, new_type: str):
        self.remove_simulated_columns(name, column)
        self.add_simulated_columns(name, table, key_columns, column, new_type)

    def store_result(self, simulation_name: str, rows: [dict]):
        # fetch table and columns using simulation_name
        # update rows into table - using id?
        pass

    def get_query_load(self) -> [dict]:
        self.fetch_entity("SELECT * FROM simulator LIMIT 1")  # TODO: change placeholder query to remove warning
        return [{}]

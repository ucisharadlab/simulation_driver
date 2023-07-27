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

    def add_simulated_columns(self, name: str, table: str, columns: [str], data_type: str):
        self.execute(f"INSERT INTO simulated_columns (name, table, columns, type) VALUES "
                     f"('${name}' '${table}', '${','.join(columns)}', '${data_type}')")

    def remove_simulated_columns(self, name: str, column: str):
        # TODO: Change to update
        self.execute(f"DELETE FROM simulated_columns WHERE name = '${name}')")

    def update_simulated_column(self, name: str, table: str, column: str, new_type: str):
        self.remove_simulated_columns(name, column)
        self.add_simulated_columns(name, table, column, new_type)

    def store_result(self, simulation_name: str, rows: [dict]):
        pass

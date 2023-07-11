from repo.sql_repo import SqlRepo


class EdbRepo(SqlRepo):
    def add_simulator(self, name: str, class_name: str, output_type: str):
        pass

    def remove_simulator(self, name: str):
        pass

    def update_simulator(self, name: str, new_class_name: str, new_type: str):
        self.remove_simulator(name)
        self.add_simulator(name, new_class_name, new_type)

    def add_simulated_columns(self, columns: [str], data_type: str):
        pass

    def remove_simulated_columns(self, columns: [str]):
        pass

    def update_simulated_column(self, name: str, new_type: str):
        self.remove_simulated_columns(name)
        self.add_simulated_columns(name, new_type)

    def store_result(self, rows: [dict]):
        pass

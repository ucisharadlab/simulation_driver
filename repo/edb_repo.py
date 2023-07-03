from repo.sql_repo import SqlRepo


class EdbRepo(SqlRepo):
    def add_simulator(self):
        pass

    def remove_simulator(self):
        pass

    def update_simulator(self):
        self.remove_simulator()
        self.add_simulator()

    def add_simulated_columns(self):
        pass

    def remove_simulated_columns(self):
        pass

    def update_simulated_columns(self):
        self.remove_simulated_columns()
        self.add_simulated_columns()

    def store_result(self):
        pass

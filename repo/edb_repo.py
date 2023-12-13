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

    def get_simulator_by_type(self, output_type: str):
        row = self.fetch_entity(f"SELECT s.id, name, class_name, output_type, planner, parameters "
                                f"FROM simulator s INNER JOIN simulator_status ss "
                                f"ON s.name = ss.simulator_name "
                                f"WHERE output_type = '{output_type}' AND status = 0 LIMIT 1")
        return dict_from_tuple(["id", "name", "class_name", "output_type", "planner", "parameters"], row)

    def get_simulator_by_name(self, name: str):
        row = self.fetch_entity(f"SELECT id, name, class_name, output_type, planner, parameters "
                                f"FROM simulator s WHERE name = '{name}'")
        return dict_from_tuple(["id", "name", "class_name", "output_type", "planner", "parameters"], row)

    def add_simulated_columns(self, name: str, table: str, key_columns: [str], columns: [str], data_type: str):
        self.execute(f"INSERT INTO simulated_columns (name, table_name, key_columns, columns, data_type) VALUES "
                     f"('{name}', '{table}', '{','.join(key_columns)}', '{','.join(columns)}', '{data_type}')")

    def remove_simulated_columns(self, name: str, column: str):
        self.execute(f"DELETE FROM simulated_columns WHERE name = '{name}'")

    def update_simulated_column(self, name: str, table: str, key_columns: [str], column: str, new_type: str):
        self.remove_simulated_columns(name, column)
        self.add_simulated_columns(name, table, key_columns, column, new_type)

    def store_result(self, data_type: str, rows: [dict]):
        for row in rows:
            self.execute(f"INSERT INTO {data_type}_data (timestamp, location, name, concentration) VALUES "
                         f"(to_timestamp('{row['timestamp'].strftime('%Y-%m-%d %H:%M')}', "
                         f"'YYYY-MM-DD HH24:MI')::timestamp, "
                         f"'{row['location']}', '{row['name']}', '{row['concentration']}')")

    def get_query_load(self) -> [dict]:
        rows = self.fetch_entities(
            "SELECT id, query, start_time FROM query_workload WHERE status = 0")  # TODO: change query
        return [] if not rows \
            else [dict_from_tuple(["id", "query", "start_time"], row) for row in rows]

    def log(self, simulator: str, execution_info: dict):
        self.execute(f"INSERT INTO simulation_log (simulator, execution_info, timestamp) VALUES "
                     f"('{simulator}', '[]', NOW())")  # {json.dumps(execution_info)}

    def get_log(self, simulator: str):
        rows = self.fetch_entities(f"SELECT simulator, params FROM simulation_log WHERE simulator = '{simulator}'")
        return [dict_from_tuple(["simulator", "params"], row) for row in rows]

    def complete_queries(self, query_ids: list):
        if len(query_ids) < 1:
            return
        ids = [str(query_id) for query_id in query_ids]
        self.execute(f"UPDATE query_workload SET status = 1 WHERE id IN ({','.join(ids)})")

    def get_test_data(self, table: str) -> dict:
        if "%NULL%" == table:
            return dict()
        rows = self.fetch_entities(f"SELECT parameters, cost, quality FROM {table}")
        test_data = dict()
        for row in rows:
            test_row = prepare_test_data_row(row)
            test_data[test_row[0]] = test_row[1]
        return test_data


def dict_from_tuple(schema: list, row: tuple) -> dict:
    if not row:
        return dict()
    row_attribute_names = dict()
    for i in range(len(schema)):
        row_attribute_names[schema[i]] = row[i]
    return row_attribute_names


def prepare_test_data_row(row: tuple) -> tuple:
    return row[0], {"cost": row[1], "quality": row[2]}

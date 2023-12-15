import plpy


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

from querymark import q


def test_quick_start_basic():
    # Create a query with one parameter
    query = q("SELECT * FROM users WHERE id = ?", 123)

    # See what to_sql() returns
    print(query.to_sql())


def test_building_dynamic_queries():
    # Start with a base query
    query = q("SELECT * FROM users WHERE active = ?", True)

    # Add conditions dynamically
    query += q("AND role = ?", "admin")

    print(query.to_sql())

    # More complex conditional example
    base = q("SELECT * FROM users WHERE id = ?", 123)

    include_role = True
    if include_role:
        base += q("AND role = ?", "admin")

    print(base.to_sql())


def test_building_dynamic_multiple_params():
    # Multiple parameters in one q object
    query = q("SELECT * FROM article WHERE category = ? AND id = ?", "news", 123)
    print(query.to_sql())

    # Mixing q-objects with plain strings
    query2 = q("SELECT *") + "FROM user" + q("WHERE id = ?", 123)
    print(query2.to_sql())

    query3 = (
        q("SELECT * FROM user")
        + q("WHERE id = ?", 123)
        + "OR"
        + (q("group = ?", 345) + q("AND role = ?", "admin")).wrap()
    )
    print(query3.to_sql())


def test_building_lists():
    ids = [1, 2, 3]
    query = q("SELECT * FROM users WHERE id IN") + q.join(", ", ids).wrap()
    print(query.to_sql())

    table = "users"
    fields = {"name": "John", "email": "john@example.com"}
    returning = ["user_id", "name"]
    columns = ", ".join([f'"{key}"' for key in fields.keys()])
    query2 = q(f'INSERT INTO "{table}" ({columns}) VALUES')
    query2 += q.join(", ", list(fields.values())).wrap()
    if returning:
        query2 += f" RETURNING {', '.join(returning)}"
    print(query2.to_sql())


def test_building_dicts():
    updates = {"name": "Jane", "email": "jane@example.com", "active": True}
    user_id = 123
    query = q("UPDATE users SET") + q.join(", ", updates) + q("WHERE id = ?", user_id)
    print(query.to_sql())

    filters = {"name": "John%", "email": "%@example.com"}
    query2 = q("SELECT * FROM users WHERE") + q.join(
        " AND ", filters, lambda key: f"{key} LIKE ?"
    )
    print(query2.to_sql())


if __name__ == "__main__":
    test_quick_start_basic()
    test_building_dynamic_queries()
    test_building_dynamic_multiple_params()
    test_building_lists()
    test_building_dicts()

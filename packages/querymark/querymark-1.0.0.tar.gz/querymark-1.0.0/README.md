# querymark
Lightweight Python query builder for asyncpg. Use ? placeholders and querymark handles the $1, $2, $3 conversion. Compose queries with + operator while keeping parameters tracked automatically.

## The Problem
When managing indexed parameters in SQL queries to use for asyncpg for example you can easily get into problems when conditionally constructing queries.

For example if the number of conditions needed in the query is based on some logic you could end up with something like this

```Python
if role and extended_role:
    check = "(role <= $1 AND extended_role <= $2)"
    params = [role, extended_role]
elif role:
    check = "role <= $1"
    params = [role]
elif extended_role:
    check = "extended_role <= $1"
    params = [extended_role]
else:
    raise Exception("Must specify either role, extended_role or both")
if project:
    query = f"""
        SELECT 1 FROM user_project_roles
        WHERE user_id = ${len(params) + 1} AND {check}
        AND (project_id = ${len(params) + 2} OR project_id IS NULL)
        LIMIT 1
    """
    result = await db.fetchrow(query, *params, user.id, project.id)
    return result is not None
else:
    query = f"""
        SELECT 1 FROM user_project_roles
        WHERE user_id = ${len(params) + 1} AND {check}
        AND project_id IS NULL
        LIMIT 1
    """
    result = await db.fetchrow(query, *params, user.id)
    return result is not None
```

## The Solution

With querymark, you write queries using `?` placeholders and let the library handle parameter indexing:

```python
from querymark import q

# Build conditions naturally
if role and extended_role:
    check = q("(role <= ? AND extended_role <= ?)", role, extended_role)
elif role:
    check = q("role <= ?", role)
elif extended_role:
    check = q("extended_role <= ?", extended_role)
else:
    raise Exception("Must specify either role, extended_role or both")

# Compose the full query
query = q("SELECT 1 FROM user_project_roles")
query += q("WHERE user_id = ?", user.id) + " AND " + check
if project:
    query += q("AND (project_id = ? OR project_id IS NULL)", project.id)
result = await db.fetchrow(*query.to_sql())
return result is not None
```

## Installation

```bash
pip install querymark
(Note: Package will be available on PyPI soon. For now, install from source.)
```

## Basic Usage
```python
from querymark import q

# Simple query with parameters
query = q("SELECT * FROM users WHERE id = ?", user_id)
result = await db.fetch(*query.to_sql())

# Compose queries dynamically
base = q("SELECT id, name, email FROM users")
if filter_active:
    base += q("WHERE active = ?", True)
if sort_by:
    base += f"ORDER BY {sort_by}"
    
results = await db.fetch(*base.to_sql())

# Functions can return query fragments
def group_filter(self) -> q:
    return q("group_id = ?", self.group_id)

@staticmethod
def to_query() -> q:
    return q("SELECT id, group_id, text, published FROM article")

# And then combined when needed
rows = await db.fetch(
    Article.to_query()
    + q("WHERE") + article.group_filter()
    + "ORDER BY published"
)
```

For more examples and detailed documentation, see [USAGE.md](https://github.com/hlynurj/querymark/blob/main/USAGE.md).
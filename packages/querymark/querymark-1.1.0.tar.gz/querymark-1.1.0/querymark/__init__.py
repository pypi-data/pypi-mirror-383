from __future__ import annotations

from typing import Any, Callable


class q:
    """
    Constructs an SQL statement, or fragment of an SQL statement
    with question marks to be replaced with values when parsed
    by the database.
    Example usage: q("SELECT * FROM ? WHERE id = ?", table_name, id)
    """

    def __init__(self, query: str, *values: Any):
        self.query: list[str] = query.split("?")
        if len(values) != len(self.query) - 1:
            raise ValueError(
                "Value list must have the same number of items as ? characters in the query"
            )
        self.values: list[Any] = list(values)

    @classmethod
    def _from_parts(cls, query: list[str], values: list[Any]):
        instance = object.__new__(cls)
        instance.query = query
        instance.values = values
        return instance

    def to_sql(self) -> tuple[str, ...]:
        """
        Convert the query to asyncpg format with indexed parameters.

        Replaces ? placeholders with $1, $2, $3, etc. and returns the query
        string followed by all parameter values as a tuple.

        Returns:
            Tuple where first element is the parameterized query string,
            followed by all values in order.

        Example:
            >>> query = q("SELECT * FROM users WHERE id = ?", 123)
            >>> query += q(" AND group = ?", "admin")
            >>> query.to_sql()
            ('SELECT * FROM users WHERE id = $1 AND group = $2', 123, 'admin')
            >>> result = await db.fetch(*query.to_sql())
        """
        ret = ""
        for i, _ in enumerate(self.values):
            ret += f"{self.query[i]}${i + 1}"
        ret += self.query[-1]
        return (ret, *self.values)

    def concat(self, x: str | q, separator="") -> q:
        """
        Concatenate another query fragment with an optional separator.

        Args:
            x: String or q object to concatenate
            separator: String to insert between fragments (default: no separator)
                When separator is " ", strips trailing/leading whitespace leaving
                the single space between words.

        Returns:
            New q object with combined query and values
        """
        if isinstance(x, str):
            x = q(x)
        if not isinstance(x, q):
            raise ValueError("Must be a str or q object")
        query = [
            *self.query[:-1],
            separator.join([self.query[-1].rstrip(), x.query[0].lstrip()])
            if separator == " "
            else separator.join([self.query[-1], x.query[0]]),
            *x.query[1:],
        ]
        values = [*self.values, *x.values]
        return q._from_parts(query, values)

    def __add__(self, x: str | q) -> q:
        return self.concat(x, " ")

    @staticmethod
    def join(
        separator: str,
        items: dict[str, Any] | list[Any],
        formatter: Callable[[str | None], str] | None = None,
    ) -> q:
        """
        Formats a dictionary of keys and values or just a list of
        values in a comma-separated list for example but any
        separator can be defined.

        Args:
            separator: String to place between each item (e.g. ", " or " AND ")
            items: Dictionary of key-value pairs or list of values
            formatter: Optional function to format each item's placeholder.
                For lists: receives None, defaults to "?"
                For dicts: receives the key, defaults to f"{key} = ?"
                Must return a string with exactly one question mark.

        Returns:
            A q object with the formatted items and their values

        Example:
            >>> q.join(", ", [1, 2, 3])  # produces: ?, ?, ?
            >>> q.join(", ", {"name": "John", "age": 30})  # produces: name = ?, age = ?
        """

        def default_list_formatter(_):
            return "?"

        def default_dict_formatter(key):
            return f"{key} = ?"

        ret = q("")
        if isinstance(items, list):
            fmt = formatter or default_list_formatter
            for index, value in enumerate(items):
                ret = ret.concat(q(fmt(None), value), separator if index > 0 else "")
        else:
            fmt = formatter or default_dict_formatter
            for index, (key, value) in enumerate(items.items()):
                ret = ret.concat(q(fmt(key), value), separator if index > 0 else "")
        return ret

    def wrap(self, prefix: str = "(", postfix: str = ")") -> q:
        """
        Wraps the query fragment in parentheses or any prefix and postfix you define

        Args:
            prefix: String to place before the fragment
            postfix: String to place after the fragment

        Returns:
            A q object wrapped with pre- and postfix strings

        Example:
            >>> q.join(", ", [1, 2, 3]).wrap()  # produces: (?, ?, ?)
        """
        return q(prefix).concat(self).concat(postfix)

"""
Test core DataStore functionality - converted from pypika test_query.py and test_selects.py
"""

import unittest
from datastore import DataStore, Field, Sum, Count


class TestDataStoreBasics(unittest.TestCase):
    """Test basic DataStore operations."""

    def setUp(self):
        """Set up test DataStore."""
        self.ds = DataStore(table="customers")

    def test_create_datastore(self):
        """Test creating a DataStore."""
        ds = DataStore(table="test_table")
        self.assertEqual("test_table", ds.table_name)

    def test_datastore_repr(self):
        """Test DataStore string representation."""
        ds = DataStore(source_type="file", table="data")
        self.assertIn("file", repr(ds))
        self.assertIn("data", repr(ds))

    def test_empty_datastore_sql(self):
        """Test SQL generation for empty DataStore."""
        ds = DataStore(table="test")
        sql = ds.to_sql()
        self.assertEqual('SELECT * FROM "test"', sql)


class TestSelect(unittest.TestCase):
    """Test SELECT operations."""

    def setUp(self):
        self.ds = DataStore(table="customers")

    def test_select_star(self):
        """Test SELECT *."""
        sql = self.ds.to_sql()
        self.assertEqual('SELECT * FROM "customers"', sql)

    def test_select_single_field(self):
        """Test SELECT single field."""
        sql = self.ds.select("name").to_sql()
        self.assertEqual('SELECT "name" FROM "customers"', sql)

    def test_select_multiple_fields(self):
        """Test SELECT multiple fields."""
        sql = self.ds.select("name", "age", "city").to_sql()
        self.assertEqual('SELECT "name", "age", "city" FROM "customers"', sql)

    def test_select_with_field_objects(self):
        """Test SELECT with Field objects."""
        sql = self.ds.select(Field("name"), Field("age")).to_sql()
        self.assertEqual('SELECT "name", "age" FROM "customers"', sql)

    def test_select_with_alias(self):
        """Test SELECT with field alias."""
        sql = self.ds.select(Field("name", alias="customer_name")).to_sql()
        self.assertEqual('SELECT "name" AS "customer_name" FROM "customers"', sql)


class TestWhere(unittest.TestCase):
    """Test WHERE clause."""

    def setUp(self):
        self.ds = DataStore(table="customers")

    def test_filter_equal(self):
        """Test WHERE with equality."""
        sql = self.ds.filter(Field("age") == 18).to_sql()
        self.assertEqual('SELECT * FROM "customers" WHERE "age" = 18', sql)

    def test_filter_greater_than(self):
        """Test WHERE with greater than."""
        sql = self.ds.filter(Field("age") > 18).to_sql()
        self.assertEqual('SELECT * FROM "customers" WHERE "age" > 18', sql)

    def test_filter_less_than(self):
        """Test WHERE with less than."""
        sql = self.ds.filter(Field("price") < 100).to_sql()
        self.assertEqual('SELECT * FROM "customers" WHERE "price" < 100', sql)

    def test_filter_and(self):
        """Test WHERE with AND condition."""
        sql = self.ds.filter((Field("age") > 18) & (Field("city") == "NYC")).to_sql()
        self.assertEqual('SELECT * FROM "customers" WHERE ("age" > 18 AND "city" = \'NYC\')', sql)

    def test_filter_or(self):
        """Test WHERE with OR condition."""
        sql = self.ds.filter((Field("status") == "active") | (Field("status") == "trial")).to_sql()
        self.assertEqual('SELECT * FROM "customers" WHERE ("status" = \'active\' OR "status" = \'trial\')', sql)

    def test_multiple_filter_calls(self):
        """Test multiple filter() calls (should AND them)."""
        sql = self.ds.filter(Field("age") > 18).filter(Field("city") == "NYC").to_sql()
        self.assertEqual('SELECT * FROM "customers" WHERE ("age" > 18 AND "city" = \'NYC\')', sql)


class TestDynamicFieldAccess(unittest.TestCase):
    """Test dynamic field access (ds.column_name)."""

    def setUp(self):
        self.ds = DataStore(table="customers")

    def test_dynamic_field(self):
        """Test accessing field via ds.field_name."""
        field = self.ds.age
        self.assertIsInstance(field, Field)
        self.assertEqual("age", field.name)

    def test_dynamic_field_in_condition(self):
        """Test using dynamic field in condition."""
        sql = self.ds.filter(self.ds.age > 18).to_sql()
        self.assertEqual('SELECT * FROM "customers" WHERE "age" > 18', sql)

    def test_dynamic_field_in_select(self):
        """Test using dynamic field in select."""
        sql = self.ds.select(self.ds.name, self.ds.age).to_sql()
        self.assertEqual('SELECT "name", "age" FROM "customers"', sql)


class TestGroupBy(unittest.TestCase):
    """Test GROUP BY operations."""

    def setUp(self):
        self.ds = DataStore(table="orders")

    def test_groupby_single_field(self):
        """Test GROUP BY single field."""
        sql = self.ds.groupby("customer_id").to_sql()
        self.assertEqual('SELECT * FROM "orders" GROUP BY "customer_id"', sql)

    def test_groupby_multiple_fields(self):
        """Test GROUP BY multiple fields."""
        sql = self.ds.groupby("customer_id", "status").to_sql()
        self.assertEqual('SELECT * FROM "orders" GROUP BY "customer_id", "status"', sql)

    def test_groupby_with_aggregate(self):
        """Test GROUP BY with aggregate function."""
        sql = self.ds.groupby("customer_id").select(Field("customer_id"), Sum(Field("amount"), alias="total")).to_sql()
        self.assertEqual('SELECT "customer_id", SUM("amount") AS "total" FROM "orders" GROUP BY "customer_id"', sql)


class TestOrderBy(unittest.TestCase):
    """Test ORDER BY operations."""

    def setUp(self):
        self.ds = DataStore(table="customers")

    def test_sort_single_field_asc(self):
        """Test ORDER BY single field ascending."""
        sql = self.ds.sort("name").to_sql()
        self.assertEqual('SELECT * FROM "customers" ORDER BY "name" ASC', sql)

    def test_sort_single_field_desc(self):
        """Test ORDER BY single field descending."""
        sql = self.ds.sort("name", ascending=False).to_sql()
        self.assertEqual('SELECT * FROM "customers" ORDER BY "name" DESC', sql)

    def test_sort_multiple_fields(self):
        """Test ORDER BY multiple fields."""
        sql = self.ds.sort("city", "name").to_sql()
        self.assertEqual('SELECT * FROM "customers" ORDER BY "city" ASC, "name" ASC', sql)


class TestLimitOffset(unittest.TestCase):
    """Test LIMIT and OFFSET."""

    def setUp(self):
        self.ds = DataStore(table="customers")

    def test_limit(self):
        """Test LIMIT clause."""
        sql = self.ds.limit(10).to_sql()
        self.assertEqual('SELECT * FROM "customers" LIMIT 10', sql)

    def test_offset(self):
        """Test OFFSET clause."""
        sql = self.ds.offset(20).to_sql()
        self.assertEqual('SELECT * FROM "customers" OFFSET 20', sql)

    def test_limit_and_offset(self):
        """Test LIMIT and OFFSET together."""
        sql = self.ds.limit(10).offset(20).to_sql()
        self.assertEqual('SELECT * FROM "customers" LIMIT 10 OFFSET 20', sql)


class TestChaining(unittest.TestCase):
    """Test method chaining."""

    def setUp(self):
        self.ds = DataStore(table="orders")

    def test_complex_chain(self):
        """Test complex method chain."""
        sql = (
            self.ds.select("customer_id", Sum(Field("amount"), alias="total"))
            .filter(Field("status") == "completed")
            .groupby("customer_id")
            .sort("total", ascending=False)
            .limit(10)
            .to_sql()
        )

        expected = (
            'SELECT "customer_id", SUM("amount") AS "total" FROM "orders" '
            'WHERE "status" = \'completed\' '
            'GROUP BY "customer_id" '
            'ORDER BY "total" DESC '
            'LIMIT 10'
        )
        self.assertEqual(expected, sql)


class TestImmutability(unittest.TestCase):
    """Test immutability of operations."""

    def test_select_immutable(self):
        """Test that select() doesn't modify original."""
        ds1 = DataStore(table="test")
        ds2 = ds1.select("name")

        self.assertNotEqual(id(ds1), id(ds2))
        self.assertEqual('SELECT * FROM "test"', ds1.to_sql())
        self.assertEqual('SELECT "name" FROM "test"', ds2.to_sql())

    def test_filter_immutable(self):
        """Test that filter() doesn't modify original."""
        ds1 = DataStore(table="test")
        ds2 = ds1.filter(Field("age") > 18)

        self.assertNotEqual(id(ds1), id(ds2))
        self.assertEqual('SELECT * FROM "test"', ds1.to_sql())
        self.assertEqual('SELECT * FROM "test" WHERE "age" > 18', ds2.to_sql())

    def test_chaining_immutable(self):
        """Test that chaining creates new instances."""
        ds1 = DataStore(table="test")
        ds2 = ds1.select("name")
        ds3 = ds2.filter(Field("age") > 18)

        # All three should be different objects
        self.assertNotEqual(id(ds1), id(ds2))
        self.assertNotEqual(id(ds2), id(ds3))
        self.assertNotEqual(id(ds1), id(ds3))

        # Original should be unchanged
        self.assertEqual('SELECT * FROM "test"', ds1.to_sql())


if __name__ == '__main__':
    unittest.main()


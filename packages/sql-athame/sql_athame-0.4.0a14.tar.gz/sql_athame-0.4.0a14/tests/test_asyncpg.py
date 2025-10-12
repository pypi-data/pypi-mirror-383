# ruff: noqa: UP007

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated, Optional

import asyncpg
import pytest
from typing_extensions import TypeAlias

from sql_athame import ColumnInfo, ModelBase, sql


@pytest.fixture(autouse=True)
async def conn():
    port = os.environ.get("PGPORT", 29329)
    conn = await asyncpg.connect(
        f"postgres://postgres:password@localhost:{port}/postgres"
    )
    txn = conn.transaction()
    try:
        await txn.start()
        yield conn
    finally:
        await txn.rollback()
        await conn.close()


@dataclass
class Table1(ModelBase, table_name="table1"):
    a: int
    b: str


@pytest.fixture(autouse=True)
async def tables(conn):
    await conn.execute(*Table1.create_table_sql())


async def test_connection(conn):
    assert await conn.fetchval("SELECT 2 + 2") == 4


async def test_select(conn, tables):
    assert len(await conn.fetch("SELECT * FROM table1")) == 0
    await Table1(42, "foo").insert(conn)
    res = await conn.fetchrow("SELECT * FROM table1")
    assert list(res.keys()) == ["a", "b"]


async def test_replace_multiple(conn):
    @dataclass(order=True)
    class Test(ModelBase, table_name="test", primary_key="id"):
        id: int
        a: int
        b: str

    await conn.execute(*Test.create_table_sql())
    await Test.insert_multiple(conn, [])
    await Test.upsert_multiple(conn, [])

    data = [
        Test(1, 1, "foo"),
        Test(2, 1, "bar"),
        Test(3, 2, "quux"),
    ]
    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple(conn, [], where=[])
    assert not c
    assert not u
    assert len(d) == 3
    assert await Test.select(conn) == []

    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple(conn, [], where=sql("a = 1"))
    assert not c
    assert not u
    assert len(d) == 2
    assert [x.id for x in await Test.select(conn)] == [3]

    await conn.execute("DELETE FROM test")
    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple(
        conn, [Test(1, 5, "apples"), Test(4, 6, "fred")], where=sql("a = 1")
    )
    assert len(c) == 1
    assert len(u) == 1
    assert len(d) == 1
    assert sorted(await Test.select(conn)) == [
        Test(1, 5, "apples"),
        Test(3, 2, "quux"),
        Test(4, 6, "fred"),
    ]


async def test_replace_multiple_ignore_insert_only(conn):
    @dataclass(order=True)
    class Test(ModelBase, table_name="test", primary_key="id"):
        id: int
        a: int
        created: datetime = field(default_factory=datetime.utcnow)
        updated: datetime = field(default_factory=datetime.utcnow)

    await conn.execute(*Test.create_table_sql())

    data = [Test(1, 1), Test(2, 1), Test(3, 2)]
    await Test.insert_multiple(conn, data)

    await asyncio.sleep(0.1)
    new_data = [Test(1, 1), Test(2, 4), Test(3, 2)]
    c, u, d = await Test.replace_multiple(
        conn, new_data, where=[], ignore=["updated"], insert_only=["created"]
    )
    assert not c
    assert not d
    assert len(u) == 1

    db_data = await Test.select(conn, order_by="id")
    assert data[0] == db_data[0]
    assert data[2] == db_data[2]
    orig = data[1]
    new = new_data[1]
    db = db_data[1]
    assert db.created == orig.created
    assert db.updated == new.updated

    # Test force_update - should override insert_only and update created field
    await asyncio.sleep(0.1)
    force_data = [Test(1, 10), Test(2, 40), Test(3, 20)]
    c, u, d = await Test.replace_multiple(
        conn,
        force_data,
        where=[],
        ignore=["updated"],
        insert_only=["created"],
        force_update={"created"},
    )
    assert not c
    assert not d
    # All 3 records should be updated since we're forcing created to update
    assert len(u) == 3

    # Verify created field was updated despite insert_only
    final_data = await Test.select(conn, order_by="id")
    assert final_data[0].created != data[0].created  # Should be updated
    assert final_data[0].a == 10


@pytest.mark.parametrize("insert_multiple_mode", ["array_safe", "executemany"])
async def test_replace_multiple_arrays(conn, insert_multiple_mode):
    @dataclass(order=True)
    class Test(
        ModelBase,
        table_name="test",
        primary_key="id",
        insert_multiple_mode=insert_multiple_mode,
    ):
        id: int
        a: Annotated[list[int], ColumnInfo(type="INT[]")]
        b: str

    await conn.execute(*Test.create_table_sql())
    await Test.insert_multiple(conn, [])
    await Test.upsert_multiple(conn, [])

    data = [
        Test(1, [1], "foo"),
        Test(2, [1, 3, 5], "bar"),
        Test(3, [], "quux"),
    ]
    await Test.insert_multiple(conn, dict(enumerate(data)).values())

    c, u, d = await Test.replace_multiple(conn, [], where=[])
    assert not c
    assert not u
    assert len(d) == 3
    assert await Test.select(conn) == []

    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple(conn, [], where=sql("a @> ARRAY[1]"))
    assert not c
    assert not u
    assert len(d) == 2
    assert [x.id for x in await Test.select(conn)] == [3]

    await conn.execute("DELETE FROM test")
    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple(
        conn, [Test(1, [5], "apples"), Test(4, [6], "fred")], where=sql("a @> ARRAY[1]")
    )
    assert len(c) == 1
    assert len(u) == 1
    assert len(d) == 1
    assert sorted(await Test.select(conn)) == [
        Test(1, [5], "apples"),
        Test(3, [], "quux"),
        Test(4, [6], "fred"),
    ]


async def test_replace_multiple_reporting_differences(conn):
    @dataclass(order=True)
    class Test(ModelBase, table_name="test", primary_key="id"):
        id: int
        a: int
        b: str

    await conn.execute(*Test.create_table_sql())

    data = [
        Test(1, 1, "foo"),
        Test(2, 1, "bar"),
        Test(3, 2, "quux"),
    ]
    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple_reporting_differences(conn, [], where=[])
    assert not c
    assert not u
    assert len(d) == 3
    assert await Test.select(conn) == []

    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple_reporting_differences(
        conn, [], where=sql("a = 1")
    )
    assert not c
    assert not u
    assert len(d) == 2
    assert [x.id for x in await Test.select(conn)] == [3]

    await conn.execute("DELETE FROM test")
    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple_reporting_differences(
        conn, [Test(1, 5, "apples"), Test(4, 6, "fred")], where=sql("a = 1")
    )
    assert len(c) == 1
    assert len(u) == 1
    assert u == [(Test(1, 1, "foo"), Test(1, 5, "apples"), ["a", "b"])]
    assert len(d) == 1
    assert sorted(await Test.select(conn)) == [
        Test(1, 5, "apples"),
        Test(3, 2, "quux"),
        Test(4, 6, "fred"),
    ]


async def test_replace_multiple_multicolumn_pk(conn):
    @dataclass(order=True)
    class Test(ModelBase, table_name="test", primary_key=("id1", "id2")):
        id1: int
        id2: int
        a: int
        b: str

    await conn.execute(*Test.create_table_sql())

    data = [
        Test(1, 1, 1, "foo"),
        Test(1, 2, 1, "bar"),
        Test(1, 3, 2, "quux"),
    ]
    await Test.insert_multiple(conn, data)

    c, u, d = await Test.replace_multiple(
        conn, [Test(1, 1, 5, "apples"), Test(2, 4, 6, "fred")], where=sql("a = 1")
    )
    assert len(c) == 1
    assert len(u) == 1
    assert len(d) == 1
    assert sorted(await Test.select(conn)) == [
        Test(1, 1, 5, "apples"),
        Test(1, 3, 2, "quux"),
        Test(2, 4, 6, "fred"),
    ]


Serial: TypeAlias = Annotated[int, ColumnInfo(type="SERIAL")]


async def test_serial(conn):
    @dataclass
    class Test(ModelBase, table_name="table", primary_key="id"):
        id: Serial
        foo: int
        bar: str

    await conn.execute(*Test.create_table_sql())
    t = await Test.create(conn, foo=42, bar="bar")
    assert t == Test(1, 42, "bar")
    t = await Test.create(conn, foo=42, bar="bar")
    assert t == Test(2, 42, "bar")

    assert list(await Test.select(conn)) == [Test(1, 42, "bar"), Test(2, 42, "bar")]


async def test_unnest_json(conn):
    @dataclass
    class Test(ModelBase, table_name="table", primary_key="id"):
        id: Serial
        json: Annotated[Optional[list], ColumnInfo(type="JSONB", nullable=True)]

    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )

    await conn.execute(*Test.create_table_sql())

    rows = [
        Test(1, ["foo"]),
        Test(2, ["foo", "bar"]),
        Test(3, None),
    ]

    await Test.insert_multiple(conn, rows)

    assert list(await Test.select(conn)) == rows
    assert list(
        await conn.fetchrow('SELECT COUNT(*) FROM "table" WHERE json IS NULL')
    ) == [1]


async def test_unnest_empty(conn):
    @dataclass
    class Test(ModelBase, table_name="table", primary_key="id"):
        id: Serial

    await conn.execute(*Test.create_table_sql())

    await Test.insert_multiple(conn, [])

    assert list(await Test.select(conn)) == []


async def test_upsert_insert_only(conn):
    @dataclass
    class Test(ModelBase, table_name="test_upsert", primary_key="id"):
        id: int
        name: str
        count: int
        created_at: str

    await conn.execute(*Test.create_table_sql())

    # Initial insert
    record = Test(1, "Alice", 5, "2023-01-01")
    was_updated = await record.upsert(conn)
    assert not was_updated  # Should be False for initial insert

    # Verify record was inserted
    result = await Test.select(conn, where=sql("id = {}", 1))
    assert len(result) == 1
    assert result[0] == record

    # Update without insert_only - should update all fields including created_at
    updated_record = Test(1, "Alice Updated", 10, "2023-01-02")
    was_updated = await updated_record.upsert(conn)
    assert was_updated  # Should be True for update

    result = await Test.select(conn, where=sql("id = {}", 1))
    assert len(result) == 1
    assert result[0] == updated_record

    # Update with insert_only - should not update created_at
    final_record = Test(1, "Alice Final", 15, "2023-01-03")
    was_updated = await final_record.upsert(conn, insert_only={"created_at"})
    assert was_updated  # Should be True for update

    # Verify created_at was preserved
    result = await Test.select(conn, where=sql("id = {}", 1))
    assert result[0].created_at == "2023-01-02"  # Should still be the previous value
    assert result[0].name == "Alice Final"
    assert result[0].count == 15

    # Test force_update - should override insert_only and update created_at
    force_record = Test(1, "Alice Force", 20, "2023-01-04")
    was_updated = await force_record.upsert(
        conn, insert_only={"created_at"}, force_update={"created_at"}
    )
    assert was_updated

    # Verify created_at was updated despite insert_only
    result = await Test.select(conn, where=sql("id = {}", 1))
    assert result[0].created_at == "2023-01-04"  # Should be updated
    assert result[0].name == "Alice Force"
    assert result[0].count == 20


async def test_replace_multiple_with_replace_ignore(conn):
    """Test replace_ignore ColumnInfo attribute."""

    @dataclass(order=True)
    class Test(ModelBase, table_name="test", primary_key="id"):
        id: int
        name: str
        count: int
        # metadata field should be ignored during comparison
        metadata: Annotated[str, ColumnInfo(replace_ignore=True)]

    await conn.execute(*Test.create_table_sql())

    # Insert initial data
    data = [
        Test(1, "Alice", 10, "meta1"),
        Test(2, "Bob", 20, "meta2"),
        Test(3, "Charlie", 30, "meta3"),
    ]
    await Test.insert_multiple(conn, data)

    # Replace with same data but different metadata
    # Since metadata is ignored, no updates should happen
    new_data = [
        Test(1, "Alice", 10, "different_meta"),
        Test(2, "Bob", 20, "different_meta"),
        Test(3, "Charlie", 30, "different_meta"),
    ]
    c, u, d = await Test.replace_multiple(conn, new_data, where=[])
    assert not c  # No creates
    assert not u  # No updates because metadata is ignored
    assert not d  # No deletes

    # Verify original metadata is preserved
    result = await Test.select(conn, order_by="id")
    assert result[0].metadata == "meta1"
    assert result[1].metadata == "meta2"
    assert result[2].metadata == "meta3"

    # Now change a non-ignored field - should trigger update
    # The metadata will be updated too (it's only ignored for comparison)
    new_data[0] = Test(1, "Alice Updated", 10, "still_different")
    c, u, d = await Test.replace_multiple(conn, new_data, where=[])
    assert not c
    assert len(u) == 1  # Should update because name changed
    assert not d

    # Verify update happened - metadata gets updated along with other fields
    result = await Test.select(conn, where=sql("id = 1"))
    assert result[0].name == "Alice Updated"
    assert result[0].metadata == "still_different"  # Updated along with name


async def test_replace_multiple_replace_ignore_with_force_update(conn):
    """Test that force_update overrides replace_ignore."""

    @dataclass(order=True)
    class Test(ModelBase, table_name="test", primary_key="id"):
        id: int
        name: str
        metadata: Annotated[str, ColumnInfo(replace_ignore=True)]

    await conn.execute(*Test.create_table_sql())

    # Insert initial data
    data = [Test(1, "Alice", "meta1"), Test(2, "Bob", "meta2")]
    await Test.insert_multiple(conn, data)

    # Replace with different metadata, using force_update
    new_data = [Test(1, "Alice", "new_meta1"), Test(2, "Bob", "new_meta2")]
    c, u, d = await Test.replace_multiple(
        conn, new_data, where=[], force_update={"metadata"}
    )
    assert not c
    assert len(u) == 2  # Should update because force_update overrides replace_ignore
    assert not d

    # Verify metadata was updated
    result = await Test.select(conn, order_by="id")
    assert result[0].metadata == "new_meta1"
    assert result[1].metadata == "new_meta2"


async def test_replace_multiple_replace_ignore_with_insert_only(conn):
    """Test interaction between replace_ignore and insert_only."""

    @dataclass(order=True)
    class Test(ModelBase, table_name="test", primary_key="id"):
        id: int
        name: str
        # Both replace_ignore and insert_only
        created_at: Annotated[str, ColumnInfo(replace_ignore=True, insert_only=True)]
        # Only replace_ignore
        metadata: Annotated[str, ColumnInfo(replace_ignore=True)]

    await conn.execute(*Test.create_table_sql())

    # Insert initial data
    data = [Test(1, "Alice", "2023-01-01", "meta1")]
    await Test.insert_multiple(conn, data)

    # Try to replace with different created_at and metadata
    new_data = [Test(1, "Alice", "2023-01-02", "meta2")]
    c, u, d = await Test.replace_multiple(conn, new_data, where=[])
    assert not c
    assert not u  # No update because both fields are ignored
    assert not d

    # Verify original values preserved
    result = await Test.select(conn)
    assert result[0].created_at == "2023-01-01"
    assert result[0].metadata == "meta1"

    # Change name - should trigger update
    # created_at is preserved (insert_only), metadata is updated (only ignored for comparison)
    new_data = [Test(1, "Alice Updated", "2023-01-03", "meta3")]
    c, u, d = await Test.replace_multiple(conn, new_data, where=[])
    assert not c
    assert len(u) == 1
    assert not d

    # Verify update happened
    result = await Test.select(conn)
    assert result[0].name == "Alice Updated"
    assert result[0].created_at == "2023-01-01"  # Preserved (insert_only)
    assert result[0].metadata == "meta3"  # Updated (only ignored for comparison)


async def test_replace_multiple_replace_ignore_partial_match(conn):
    """Test replace_ignore when only some records match."""

    @dataclass(order=True)
    class Test(ModelBase, table_name="test", primary_key="id"):
        id: int
        category: str
        value: int
        metadata: Annotated[str, ColumnInfo(replace_ignore=True)]

    await conn.execute(*Test.create_table_sql())

    # Insert data with different categories
    data = [
        Test(1, "A", 10, "meta1"),
        Test(2, "A", 20, "meta2"),
        Test(3, "B", 30, "meta3"),
    ]
    await Test.insert_multiple(conn, data)

    # Replace only category A with different metadata
    new_data = [
        Test(1, "A", 10, "new_meta1"),
        Test(2, "A", 25, "new_meta2"),  # value changed
    ]
    c, u, d = await Test.replace_multiple(conn, new_data, where=sql("category = 'A'"))
    assert not c
    assert len(u) == 1  # Only id=2 should update (value changed)
    assert not d  # Category B record not affected by where clause

    # Verify results
    result = await Test.select(conn, order_by="id")
    assert len(result) == 3
    assert result[0].metadata == "meta1"  # Unchanged (no update happened)
    assert result[0].value == 10
    assert result[1].metadata == "new_meta2"  # Updated along with value
    assert result[1].value == 25  # Updated
    assert result[2] == data[2]  # Category B unchanged

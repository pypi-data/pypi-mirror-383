# nosqlpy - Async, NoSQL, MQL-style embedded document store for Python

<p align="center">
  <img src="logo.png" alt="nosqlpy logo" width="250">
</p>

⚠️ Warning: This is the alpha version

**nosqlpy** is a lightweight, async-first, file-backed document database for Python that speaks a **MongoDB-like Query Language (MQL)**.
It’s designed for small-to-medium apps, dev tooling, prototyping, CLI tools, and apps that want a simple embedded DB with **async/await**, durability options, indexes, and a clean API - without running a separate database server.

- ✅ Async-first 
- ✅ Mongo-like queries 
- ✅ Append-only op-log 
- ✅ Secondary equality indexes 
- ✅ Compaction & durability modes

---

# Table of contents

- [nosqlpy - Async, NoSQL, MQL-style embedded document store for Python](#nosqlpy---async-nosql-mql-style-embedded-document-store-for-python)
- [Table of contents](#table-of-contents)
- [Why nosqlpy?](#why-nosqlpy)
- [Key features](#key-features)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Core concepts \& API reference](#core-concepts--api-reference)
  - [Database \& Collection](#database--collection)
  - [Common operations](#common-operations)
    - [List of operations](#list-of-operations)
    - [Examples](#examples)
  - [Query language (MQL subset)](#query-language-mql-subset)
  - [Update operators](#update-operators)
  - [Indexing](#indexing)
  - [Compaction \& durability](#compaction--durability)
- [Performance tips](#performance-tips)
- [License](#license)
- [Keywords](#keywords)

---

# Why nosqlpy?

Many small Python apps need an embedded document store that:

* Is **async-native** (fits FastAPI / aiohttp / asyncio apps)
* Uses a **familiar query language** (MongoDB-style filters)
* Provides **durable writes** and **safe recovery**
* Enables **fast reads** using secondary indexes

Most small DB options are either synchronous (TinyDB), or require wrapping sync code into thread pools. `nosqlpy` is built async-first and offers MQL-style queries, an append-only op-log for safe durability, optional indexes, and compaction for production-ish workloads - all in a single small dependency set.

---

# Key features

* Async API (`async/await`) - designed for asyncio apps
* MongoDB-style query language (subset): `$and`, `$or`, `$not`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$exists`, simple dot-notation for nested fields
* Update operators: `$set`, `$unset`, `$inc`, `$push`, `$pull`
* Append-only operation log (oplog) with replayable history
* Durability modes: `fast`, `safe`, `durable` (fsync)
* Secondary equality indexes (create and use for fast `field == value`)
* Compaction (background-friendly pattern) to shrink logs and produce snapshots
* Bulk ops: `insert_many`, `update_many`, `delete_many`
* find support: `projection`, `sort`, `skip`, `limit`, `find_one`
* TinyDB migration helper / compatibility shim (to ease switching)

---

# Installation

```bash
# install from PyPI (when published)
pip install nosqlpy

# or during development (from repo)
git clone https://github.com/viehoang/nosqlpy.git
cd nosqlpy
pip install -e ".[dev]"
```

Dependencies: `aiofiles` (async file I/O). Dev/test extras include `pytest`, `pytest-asyncio`.

---

# Quickstart

```python
import asyncio
from nosqlpy import Database

async def main():
    db = Database("data_dir", durability="safe")
    users = await db.collection("users")

    # insert
    uid = await users.insert_one({
        "name": "alice", 
        "age": 30})
        
    print("inserted id:", uid)

    # find (Mongo-like query)
    results = await users.find(
        {"age": {"$gte": 25}, 
        "name": "alice"})
    print("found:", results)

    # update operators
    await users.update_many(
        {"name": "alice"}, 
        {"$inc": {"age": 1}, 
        "$push": {"tags": "admin"}})

    # create index on email for fast equality lookups
    await users.create_index("email")

    # compact (shrink the op-log)
    await users.compact()

asyncio.run(main())
```

---

# Core concepts & API reference

> **Collection** - a single named dataset backed by an append-oplog file.
> 
> **Document** - a JSON-like dict with an `_id` field (string) as the primary key.
>
> **Op-log** - append-only lines describing `insert`, `update`, `replace`, `delete` operations.

All calls are `async`.

## Database & Collection

```python
from nosqlpy import Database
db = Database("my_data_dir", durability="safe")
users = await db.collection("users")
```

## Common operations

### List of operations

| Operator | Description |
|----------|-------------|
| `open` | Asynchronously open and load the collection. |
| `insert_one` | Insert a single document into the collection. |
| `insert_many` | Insert multiple documents into the collection. |
| `find` | Find documents matching the query, with options for projection, sort, skip, and limit. |
| `find_one` | Find a single document matching the query. |
| `count` | Count the number of documents matching the query. |
| `delete_one` | Delete a single document matching the query. |
| `delete_many` | Delete multiple documents matching the query. |
| `update_one` | Update a single document matching the query, with optional upsert. |
| `update_many` | Update multiple documents matching the query, with optional upsert (upserts one if no matches). |
| `replace_one` | Replace a single document matching the query, with optional upsert. |
| `create_index` | Create a secondary hash index on a field. |
| `drop_index` | Drop the index on a field. |
| `compact` | Compact the op-log by replacing it with current state as inserts. |

### Examples

```python
# insert one
_id = await users.insert_one({"name": "Bob", "age": 22})

# insert many
ids = await users.insert_many([{"name":"A"},{"name":"B"}])

# find (MQL filter)
docs = await users.find(
    {"age": {"$gte": 18}}, 
    projection=["name","age"], 
    sort=[("age", -1)], 
    skip=0, 
    limit=50)

# find one
doc = await users.find_one({"name": "Bob"})

# count
n = await users.count({"age": {"$gte": 30}})

# update many (supports $set/$inc/$push/$pull)
updated = await users.update_many(
    {"name": "Bob"}, 
    {"$inc": {"age": 1}})

# replace one
ok = await users.replace_one(
    {"name": "Bob"}, 
    {"name": "Robert", "age": 23})

# delete many
deleted = await users.delete_many({"age": {"$lt": 18}})

# compact (rewrite op-log as current-state snapshot)
await users.compact()
```

## Query language (MQL subset)

Supported query operators (subset):

* Comparison: `$eq` (or plain value), `$ne`, `$gt`, `$gte`, `$lt`, `$lte`
* Membership: `$in`, `$nin`
* Existence: `$exists`
* Logical: `$and`, `$or`, `$not`
* Dot-notation: `"user.age"` for nested fields

Examples:

```python
# age >= 30 AND (country == "US" OR country == "JP")
q = {"$and": [{"age": {"$gte": 30}}, {"$or": [{"country": "US"}, {"country": "JP"}]}]}

# membership
q2 = {"status": {"$in": ["active", "pending"]}}

# nested field
q3 = {"profile.email": {"$exists": True}}
```

## Update operators

Supported update operators:

* `$set`: set field(s) to value
* `$unset`: remove field(s)
* `$inc`: increment numeric field
* `$push`: append to array field
* `$pull`: remove value(s) from array field

Example:

```python
await users.update_many(
    {"_id": some_id}, 
    {
        "$set": {"name": "Alice"}, 
        "$inc": {"score": 10}
    })
```

## Indexing

Equality secondary index (hash-based) to accelerate queries like `{ "email": "a@x.com" }`:

```python
await users.create_index("email")
```

Notes:

* Indexes are in-memory by default and rebuilt on create; consider snapshotting indexes for very large DBs (TODO/roadmap).
* Planner currently optimizes single-field equality queries; range indexes are a planned feature.

## Compaction & durability

* **Op-log** (append-only) is crash friendly: each write is a single line append.
* Durability modes:

  * `fast`: minimal overhead, no explicit flush (best throughput, less durable)
  * `safe`: flush after write (`file.flush()`) - good compromise
  * `durable`: `fsync()` after each op (strong durability, slower)

Compaction rewrites the current state as a compact snapshot (series of `insert` ops) and atomically replaces the op-log. For large DBs we recommend:

* Run `compact()` occasionally (or use background segmented compaction; see Roadmap).
* Use `durable` for critical writes, `safe` for normal persistence.

---

# Performance tips

* Use indexes for frequent equality lookups.
* Use `durability="safe"` for most apps; switch to `durable` only if you need fsync-level guarantees on every op.
* For very large data (>100k docs), enable segmented compaction or index snapshots (planned).

---

# License

`nosqlpy` is released under the **MIT License**. See `LICENSE` for details.

---

# Keywords

`nosqlpy`, `nosqlite`, `nosql lite`, `async nosql`, `python async database`, `embedded document store`, `mongo query language python`, `mql python`, `asyncio database`, `append log database`, `python nosql lite`, `tinydb alternative`, `aiosqlite alternative`, `lightweight mongodb`, `file-backed document store`

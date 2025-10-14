# `simple-json-mapped-dict`

A simple `MutableMapping` (dict-like) that transparently persists its contents to a JSON file on disk. Uses only the most reliable file opening modes (`r` and `w`). Maximum compatibility with network filesystems (e.g. NAS, SSHFS, NFS), at the cost of atomicity and data race safety.

## Features

- Behaves just like a Python dict
- Contents always kept in sync with a backing JSON file
- All values must be JSON-serializable (numbers, strings, lists, objects, etc.)
  - If you try to set a value that cannot be serialized, the in-memory state will roll back and an exception will be thrown
- Uses only standard JSON and file IO, no dependencies outside the standard library
- [De]serializes through Python's `OrderedDict` - key order is preserved on disk

## When to Use

- When you need a persistent, human-readable, cross-platform key/value store, but **don't require full ACID transactional reliability, or multiprocess safety**
- When you must use filesystems with flaky support for "advanced" file locking/modes, such as SSHFS, NFS, Samba, or network-attached storage (NAS)
- When "good enough" durability, simplicity, and auditability are your main needs

## When **Not** to Use

- **Do not use for concurrent/multi-user/multiprocess writes:** This class is not race-safe—simultaneous modifications may corrupt or lose data
- Do not use for large data (entire dict is serialized/deserialized each time)
- Do not store non-JSON-serializable objects

## Installation

```bash
pip install simple-json-mapped-dict
```

## Usage

### Basic Example

```python
# coding=utf-8
from simple_json_mapped_dict import SimpleJSONMappedDict

d = SimpleJSONMappedDict('mydata.json')
d[u'foo'] = u'bar'
d.update({u'baz': 123})
print(d[u'foo'])  # 'bar'
del d[u'foo']
```

After running the above, `mydata.json` would look like:
```json
{"baz": 123}
```

## Alternatives

- For heavier-duty persistence with ACID guarantees, see [sqlite3](https://docs.python.org/3/library/sqlite3.html), [ZODB](https://zodb.org/), [shelve](https://docs.python.org/3/library/shelve.html), [TinyDB](https://tinydb.readthedocs.io/), etc.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
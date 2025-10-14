# fort

*The Python database micropackage*

-----

**fort** is a thin database wrapper for programmers who love to write SQL. Use it when SQLAlchemy is too much.

## Usage

Start by initializing an object for your database, providing a connection string:

```python
import fort

db = fort.PostgresDatabase('postgres://user:password@host/database')
```

Each of fort's database classes provides a small set of methods that makes working with SQL simple. You can immediately
begin making queries to the database:

```python
import uuid

db.u('CREATE TABLE widgets (id uuid PRIMARY KEY, name text)')

my_id = uuid.uuid4()
db.u('INSERT INTO widgets (id, name) VALUES (%(id)s, %(name)s)', {'id': my_id, 'name': 'Thingy'})

for row in db.q('SELECT id, name FROM widgets'):
    print(row['id'], row['name'])

my_widget = db.q_one('SELECT id, name FROM widgets WHERE id = %(id)s', {'id': my_id})
print(my_widget['name'])

my_widget_name = db.q_val('SELECT name FROM widgets WHERE id = %(id)s', {'id': my_id})
print(my_id, my_widget_name)
```

Using one of fort's database classes directly is fine, but it is better to consolidate your SQL statements by
subclassing one of fort's classes and adding your own methods:

```python
class MyDatabase(fort.PostgresDatabase):

    def migrate(self):
        self.u('CREATE TABLE widgets (id uuid PRIMARY KEY, name text)')

    def add_widget(self, widget_name: str) -> uuid.UUID:
        new_id = uuid.uuid4()
        sql = 'INSERT INTO widgets (id, name) VALUES (%(id)s, %(name)s)'
        params = {'id': new_id, 'name': widget_name}
        self.u(sql, params)
        return new_id

    def list_widgets(self) -> List[Dict]:
        return self.q('SELECT id, name FROM widgets')

    def get_widget(self, widget_id: uuid.UUID) -> Optional[Dict]:
        sql = 'SELECT id, name FROM widgets WHERE id = %(id)s'
        return self.q_one(sql, {'id': widget_id})

    def get_widget_name(self, widget_id: uuid.UUID) -> Optional[str]:
        sql = 'SELECT name FROM widgets WHERE id = %(id)s'
        return self.q_val(sql, {'id': widget_id})

db = MyDatabase('postgres://user:password@host/database')
db.migrate()

my_id = db.add_widget('Thingy')

for widget in db.list_widgets():
    print(widget['id'], widget['name'])

my_widget = db.get_widget(my_id)
print(my_widget['id'], my_widget['name'])

my_widget_name = db.get_widget_name(my_id)
print(my_id, my_widget_name)
```

## Database class methods

The following methods come with every fort database class:

```python
def u(self, sql: str, params: Dict = None) -> int: ...
    """
    Execute a statement and return the number of rows affected.
    Use this method for CREATE, INSERT, and UPDATE statements.
    """

def q(self, sql: str, params: Dict = None) -> List[Dict]: ...
    """
    Execute a statement and return all results.
    Use this method for SELECT statements.
    """

def q_one(self, sql: str, params: Dict = None) -> Optional[Dict]: ...
    """
    Execute a statement and return the first result.
    If there are no results, return `None`.
    """

def q_val(self, sql: str, params: Dict = None) -> Any: ...
    """
    Execute a statement and return the value in the first column of the first result.
    If there are no results, return `None`.
    """
```

Each fort database class instance also has a logger at `self.log`:

```python
    db = MyDatabase('postgres://user:password@host/database')
    db.log.info('Hello from my database class instance!')
```

## Notes on specific database classes

### PostgresDatabase

Use `PostgresDatabase` to connect to a PostgreSQL database. Use `pyformat` [paramstyle][a] for all your statements.
Your connection string will be passed directly to [`psycopg2.connect()`][b].

You are still responsible for installing `psycopg2`.

### SQLiteDatabase

Use `SQLiteDatabase` to connect to an SQLite database. Use `named` [paramstyle][a] for all your statements. Your
connection string will be passed directly to [`sqlite3.connect()`][c].

[a]: https://www.python.org/dev/peps/pep-0249/#paramstyle
[b]: http://initd.org/psycopg/docs/module.html#psycopg2.connect
[c]: https://docs.python.org/3/library/sqlite3.html#sqlite3.connect

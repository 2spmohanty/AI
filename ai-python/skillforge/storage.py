import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from graph_states import LearnerProfileState
from langgraph.store.sqlite import SqliteStore

# 1. Mount serialization whitelisting
custom_serde = JsonPlusSerializer(allowed_msgpack_modules=[LearnerProfileState])

# 2. Open a pristine file connection pool
db_connection = sqlite3.connect("./skillforge_checkpointer.db", check_same_thread=False)

# 3. Re-instantiate the persistent saver
db_checkpointer = SqliteSaver(conn=db_connection, serde=custom_serde)

# 4. Re-run setup to verify schema state
db_checkpointer.setup()
db_connection.commit()
print("SQLite Checkpointer successfully re-hydrated from disk file!")

# Long term memory enabler
store_connection = sqlite3.connect("./skillforge_store.db", check_same_thread=False)
store = SqliteStore(conn=store_connection)
store.setup()
store_connection.commit()
print("🗄️ SQLite Store successfully initialised!")



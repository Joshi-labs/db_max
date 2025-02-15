import asyncio
import aiosqlite
import os
from quart import Quart, jsonify, request

app = Quart(__name__)

DATABASE_DIR = "databases/"
DATABASE_CRYPTO = "crypto.db"
AUTH_KEY = "123"


async def execute_query(db_name, query):

    """Safely execute a query on the given database."""

    db_path = os.path.join(DATABASE_DIR, db_name)

    # Prevent unsafe queries
    unsafe_keywords = ["DROP", "ALTER"] # , "DELETE"
    if any(keyword in query.upper() for keyword in unsafe_keywords):
        return {"error": "Unsafe query detected"}, 403

    try:
        async with aiosqlite.connect(db_path) as connection:  
            cursor = await connection.execute(query)
            if query.strip().upper().startswith("SELECT") | query.strip().upper().startswith("PRAGMA"):
                rows = await cursor.fetchall()
                return rows  # Return fetched rows
            else:
                await connection.commit()
                return {"status": "Query executed successfully"}
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/crypto", methods=["POST"])
async def execute_crypto_query():

    """Execute a user-provided query on the crypto database."""

    data = await request.get_json()

    # Validate input
    if not data or "auth" not in data or "query" not in data:
        return jsonify({"error": "Invalid request, 'auth' and 'query' required"}), 400

    # Auth check
    if data["auth"] != AUTH_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Execute query on the crypto database
    result = await execute_query(DATABASE_CRYPTO, data["query"])
    return jsonify(result)

if __name__ == "__main__":
    os.makedirs(DATABASE_DIR, exist_ok=True)
    app.run(port=4444)

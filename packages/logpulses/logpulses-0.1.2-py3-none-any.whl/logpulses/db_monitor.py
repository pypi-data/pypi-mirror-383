"""
Universal Database Monitoring Module
Supports: MongoDB, MySQL, PostgreSQL, SQLAlchemy, Redis, Cassandra
Auto-tracks connection time and query execution time
"""

import time
import contextvars
from functools import wraps
from typing import Any, Callable, Optional
import traceback
from datetime import datetime
from decimal import Decimal

# Context variable to store DB operations (shared with logger)
db_operations = contextvars.ContextVar("db_operations", default=[])


# ============================================================================
# SERIALIZATION HELPERS
# ============================================================================


def safe_serialize(obj: Any) -> Any:
    """Safely serialize any object for logging"""
    try:
        # Handle MongoDB ObjectId
        if obj.__class__.__name__ == "ObjectId":
            return str(obj)

        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Handle date objects
        try:
            from datetime import date

            if isinstance(obj, date):
                return obj.isoformat()
        except:
            pass

        # Handle Decimal
        if isinstance(obj, Decimal):
            return float(obj)

        # Handle bytes
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8")
            except:
                return obj.hex()

        # Handle sets
        if isinstance(obj, set):
            return list(obj)

        # Handle dict
        if isinstance(obj, dict):
            return {k: safe_serialize(v) for k, v in obj.items()}

        # Handle list/tuple
        if isinstance(obj, (list, tuple)):
            return [safe_serialize(item) for item in obj]

        # Try converting to dict if object has __dict__
        if hasattr(obj, "__dict__"):
            return safe_serialize(obj.__dict__)

        # Fallback to string
        return str(obj)
    except Exception as e:
        return f"<serialization_error: {type(obj).__name__}>"


def truncate_query(query: str, max_length: int = 500) -> str:
    """Truncate long queries for logging"""
    if len(query) <= max_length:
        return query
    return query[:max_length] + f"... (truncated {len(query) - max_length} chars)"


# ============================================================================
# BASE DATABASE MONITOR
# ============================================================================


class DatabaseMonitor:
    """Base class for database monitoring"""

    @staticmethod
    def log_operation(
        db_type: str,
        operation: str,
        duration_ms: float,
        query: Optional[str] = None,
        params: Optional[Any] = None,
        result_count: Optional[int] = None,
        connection_time_ms: Optional[float] = None,
        status: str = "success",
        error: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """Log a database operation"""
        ops = db_operations.get()

        log_entry = {
            "type": db_type,
            "operation": operation,
            "duration_ms": f"{duration_ms:.2f}",
            "timestamp": datetime.now().isoformat(),
            "status": status,
        }

        if connection_time_ms is not None:
            log_entry["connection_time_ms"] = f"{connection_time_ms:.2f}"

        if query:
            log_entry["query"] = truncate_query(str(query))

        if params:
            log_entry["params"] = safe_serialize(params)

        if result_count is not None:
            log_entry["result_count"] = result_count

        if error:
            log_entry["error"] = str(error)

        if metadata:
            log_entry["metadata"] = safe_serialize(metadata)

        ops.append(log_entry)
        db_operations.set(ops)


# ============================================================================
# MONGODB MONITOR
# ============================================================================


class MongoDBMonitor(DatabaseMonitor):
    """MongoDB monitoring with connection and query tracking"""

    @staticmethod
    def patch_pymongo():
        """Patch PyMongo to track operations automatically"""
        try:
            from pymongo import MongoClient
            from pymongo.collection import Collection

            # Store original methods
            original_find = Collection.find
            original_find_one = Collection.find_one
            original_insert_one = Collection.insert_one
            original_insert_many = Collection.insert_many
            original_update_one = Collection.update_one
            original_update_many = Collection.update_many
            original_delete_one = Collection.delete_one
            original_delete_many = Collection.delete_many
            original_aggregate = Collection.aggregate
            original_count_documents = Collection.count_documents

            # Patched methods
            def patched_find(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_find(self, *args, **kwargs)
                    # Materialize cursor to get count
                    result_list = list(result)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="find",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else kwargs.get("filter", {})),
                        result_count=len(result_list),
                        metadata={"collection": self.name, "database": self.database.name},
                    )
                    return iter(result_list)
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="find",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name, "database": self.database.name},
                    )
                    raise

            def patched_find_one(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_find_one(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="find_one",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else kwargs.get("filter", {})),
                        result_count=1 if result else 0,
                        metadata={"collection": self.name, "database": self.database.name},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="find_one",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_insert_one(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_insert_one(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="insert_one",
                        duration_ms=duration,
                        result_count=1,
                        metadata={"collection": self.name, "inserted_id": str(result.inserted_id)},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="insert_one",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_insert_many(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_insert_many(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="insert_many",
                        duration_ms=duration,
                        result_count=len(result.inserted_ids),
                        metadata={"collection": self.name, "count": len(result.inserted_ids)},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="insert_many",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_update_one(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_update_one(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="update_one",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result.modified_count,
                        metadata={"collection": self.name, "matched": result.matched_count},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="update_one",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_update_many(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_update_many(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="update_many",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result.modified_count,
                        metadata={"collection": self.name, "matched": result.matched_count},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="update_many",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_delete_one(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_delete_one(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="delete_one",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result.deleted_count,
                        metadata={"collection": self.name},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="delete_one",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_delete_many(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_delete_many(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="delete_many",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result.deleted_count,
                        metadata={"collection": self.name},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="delete_many",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_aggregate(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_aggregate(self, *args, **kwargs)
                    result_list = list(result)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="aggregate",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else []),
                        result_count=len(result_list),
                        metadata={"collection": self.name, "database": self.database.name},
                    )
                    return iter(result_list)
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="aggregate",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            def patched_count_documents(self, *args, **kwargs):
                start = time.time()
                try:
                    result = original_count_documents(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="count_documents",
                        duration_ms=duration,
                        query=safe_serialize(args[0] if args else {}),
                        result_count=result,
                        metadata={"collection": self.name},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MongoDBMonitor.log_operation(
                        db_type="MongoDB",
                        operation="count_documents",
                        duration_ms=duration,
                        status="failed",
                        error=str(e),
                        metadata={"collection": self.name},
                    )
                    raise

            # Apply patches
            Collection.find = patched_find
            Collection.find_one = patched_find_one
            Collection.insert_one = patched_insert_one
            Collection.insert_many = patched_insert_many
            Collection.update_one = patched_update_one
            Collection.update_many = patched_update_many
            Collection.delete_one = patched_delete_one
            Collection.delete_many = patched_delete_many
            Collection.aggregate = patched_aggregate
            Collection.count_documents = patched_count_documents

            print("✅ MongoDB monitoring patched successfully")
        except ImportError:
            print("ℹ️  PyMongo not installed, skipping MongoDB monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch MongoDB: {e}")


# ============================================================================
# MYSQL MONITOR
# ============================================================================


class MySQLMonitor(DatabaseMonitor):
    """MySQL monitoring with connection and query tracking"""

    @staticmethod
    def patch_mysql():
        """Patch MySQL connectors to track operations"""
        try:
            # Try mysql-connector-python
            import mysql.connector
            from mysql.connector import cursor as mysql_cursor

            original_execute = mysql_cursor.MySQLCursor.execute
            original_executemany = mysql_cursor.MySQLCursor.executemany
            original_connect = mysql.connector.connect

            def patched_execute(self, operation, params=None, multi=False):
                start = time.time()
                try:
                    result = original_execute(self, operation, params, multi)
                    duration = (time.time() - start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="execute",
                        duration_ms=duration,
                        query=operation,
                        params=params,
                        result_count=self.rowcount if hasattr(self, "rowcount") else None,
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="execute",
                        duration_ms=duration,
                        query=operation,
                        params=params,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_executemany(self, operation, seq_params):
                start = time.time()
                try:
                    result = original_executemany(self, operation, seq_params)
                    duration = (time.time() - start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="executemany",
                        duration_ms=duration,
                        query=operation,
                        result_count=self.rowcount if hasattr(self, "rowcount") else None,
                        metadata={"batch_size": len(list(seq_params)) if seq_params else 0},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="executemany",
                        duration_ms=duration,
                        query=operation,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_connect(*args, **kwargs):
                conn_start = time.time()
                try:
                    connection = original_connect(*args, **kwargs)
                    conn_duration = (time.time() - conn_start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        metadata={
                            "host": kwargs.get("host", args[0] if args else "localhost"),
                            "database": kwargs.get("database", args[3] if len(args) > 3 else None),
                        },
                    )
                    return connection
                except Exception as e:
                    conn_duration = (time.time() - conn_start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        status="failed",
                        error=str(e),
                    )
                    raise

            mysql_cursor.MySQLCursor.execute = patched_execute
            mysql_cursor.MySQLCursor.executemany = patched_executemany
            mysql.connector.connect = patched_connect

            print("✅ MySQL (mysql-connector-python) monitoring patched successfully")
        except ImportError:
            pass

        try:
            # Try PyMySQL
            import pymysql
            import pymysql.cursors

            original_execute = pymysql.cursors.Cursor.execute
            original_executemany = pymysql.cursors.Cursor.executemany
            original_connect = pymysql.connect

            def patched_pymysql_execute(self, query, args=None):
                start = time.time()
                try:
                    result = original_execute(self, query, args)
                    duration = (time.time() - start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="execute",
                        duration_ms=duration,
                        query=query,
                        params=args,
                        result_count=self.rowcount,
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="execute",
                        duration_ms=duration,
                        query=query,
                        params=args,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_pymysql_executemany(self, query, args):
                start = time.time()
                try:
                    result = original_executemany(self, query, args)
                    duration = (time.time() - start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="executemany",
                        duration_ms=duration,
                        query=query,
                        result_count=self.rowcount,
                        metadata={"batch_size": len(args) if args else 0},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="executemany",
                        duration_ms=duration,
                        query=query,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_pymysql_connect(*args, **kwargs):
                conn_start = time.time()
                try:
                    connection = original_connect(*args, **kwargs)
                    conn_duration = (time.time() - conn_start) * 1000

                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        metadata={
                            "host": kwargs.get("host", "localhost"),
                            "database": kwargs.get("database", kwargs.get("db")),
                        },
                    )
                    return connection
                except Exception as e:
                    conn_duration = (time.time() - conn_start) * 1000
                    MySQLMonitor.log_operation(
                        db_type="MySQL (PyMySQL)",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        status="failed",
                        error=str(e),
                    )
                    raise

            pymysql.cursors.Cursor.execute = patched_pymysql_execute
            pymysql.cursors.Cursor.executemany = patched_pymysql_executemany
            pymysql.connect = patched_pymysql_connect

            print("✅ MySQL (PyMySQL) monitoring patched successfully")
        except ImportError:
            pass


# ============================================================================
# POSTGRESQL MONITOR
# ============================================================================


class PostgreSQLMonitor(DatabaseMonitor):
    """PostgreSQL monitoring with connection and query tracking"""

    @staticmethod
    def patch_postgresql():
        """Patch psycopg2 to track operations"""
        try:
            import psycopg2
            import psycopg2.extensions

            original_execute = psycopg2.extensions.cursor.execute
            original_executemany = psycopg2.extensions.cursor.executemany
            original_connect = psycopg2.connect

            def patched_execute(self, query, vars=None):
                start = time.time()
                try:
                    result = original_execute(self, query, vars)
                    duration = (time.time() - start) * 1000

                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="execute",
                        duration_ms=duration,
                        query=query,
                        params=vars,
                        result_count=self.rowcount if self.rowcount >= 0 else None,
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="execute",
                        duration_ms=duration,
                        query=query,
                        params=vars,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_executemany(self, query, vars_list):
                start = time.time()
                try:
                    result = original_executemany(self, query, vars_list)
                    duration = (time.time() - start) * 1000

                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="executemany",
                        duration_ms=duration,
                        query=query,
                        result_count=self.rowcount if self.rowcount >= 0 else None,
                        metadata={"batch_size": len(vars_list) if vars_list else 0},
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="executemany",
                        duration_ms=duration,
                        query=query,
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_connect(*args, **kwargs):
                conn_start = time.time()
                try:
                    connection = original_connect(*args, **kwargs)
                    conn_duration = (time.time() - conn_start) * 1000

                    # Extract database info from connection string or kwargs
                    db_info = {}
                    if "dbname" in kwargs:
                        db_info["database"] = kwargs["dbname"]
                    if "host" in kwargs:
                        db_info["host"] = kwargs["host"]

                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        metadata=db_info,
                    )
                    return connection
                except Exception as e:
                    conn_duration = (time.time() - conn_start) * 1000
                    PostgreSQLMonitor.log_operation(
                        db_type="PostgreSQL",
                        operation="connect",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                        status="failed",
                        error=str(e),
                    )
                    raise

            psycopg2.extensions.cursor.execute = patched_execute
            psycopg2.extensions.cursor.executemany = patched_executemany
            psycopg2.connect = patched_connect

            print("✅ PostgreSQL monitoring patched successfully")
        except ImportError:
            print("ℹ️  psycopg2 not installed, skipping PostgreSQL monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch PostgreSQL: {e}")


# ============================================================================
# SQLALCHEMY MONITOR
# ============================================================================


class SQLAlchemyMonitor(DatabaseMonitor):
    """SQLAlchemy ORM monitoring"""

    @staticmethod
    def patch_sqlalchemy():
        """Patch SQLAlchemy to track operations"""
        try:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine

            @event.listens_for(Engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                context._query_start_time = time.time()

            @event.listens_for(Engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                duration = (time.time() - context._query_start_time) * 1000

                SQLAlchemyMonitor.log_operation(
                    db_type="SQLAlchemy",
                    operation="executemany" if executemany else "execute",
                    duration_ms=duration,
                    query=statement,
                    params=parameters,
                    result_count=cursor.rowcount if hasattr(cursor, "rowcount") else None,
                    metadata={"dialect": conn.dialect.name},
                )

            @event.listens_for(Engine, "connect")
            def connect(dbapi_conn, connection_record):
                connection_record._connected_at = time.time()

            @event.listens_for(Engine, "checkout")
            def checkout(dbapi_conn, connection_record, connection_proxy):
                if hasattr(connection_record, "_connected_at"):
                    conn_duration = (time.time() - connection_record._connected_at) * 1000
                    SQLAlchemyMonitor.log_operation(
                        db_type="SQLAlchemy",
                        operation="connection_checkout",
                        duration_ms=conn_duration,
                        connection_time_ms=conn_duration,
                    )

            print("✅ SQLAlchemy monitoring patched successfully")
        except ImportError:
            print("ℹ️  SQLAlchemy not installed, skipping SQLAlchemy monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch SQLAlchemy: {e}")


# ============================================================================
# REDIS MONITOR
# ============================================================================


class RedisMonitor(DatabaseMonitor):
    """Redis monitoring"""

    @staticmethod
    def patch_redis():
        """Patch Redis to track operations"""
        try:
            import redis
            from redis.client import Redis

            # Store original methods
            original_methods = {}
            redis_commands = [
                "get",
                "set",
                "delete",
                "exists",
                "expire",
                "ttl",
                "hget",
                "hset",
                "hgetall",
                "hdel",
                "hincrby",
                "lpush",
                "rpush",
                "lpop",
                "rpop",
                "lrange",
                "sadd",
                "srem",
                "smembers",
                "sismember",
                "zadd",
                "zrem",
                "zrange",
                "zscore",
                "incr",
                "decr",
                "incrby",
                "decrby",
                "keys",
                "scan",
                "mget",
                "mset",
                "pipeline",
                "execute",
            ]

            def create_patched_method(method_name, original_method):
                def patched_method(self, *args, **kwargs):
                    start = time.time()
                    try:
                        result = original_method(self, *args, **kwargs)
                        duration = (time.time() - start) * 1000

                        RedisMonitor.log_operation(
                            db_type="Redis",
                            operation=method_name,
                            duration_ms=duration,
                            params={
                                "args": safe_serialize(args[:2]),
                                "kwargs": safe_serialize(kwargs),
                            },
                        )
                        return result
                    except Exception as e:
                        duration = (time.time() - start) * 1000
                        RedisMonitor.log_operation(
                            db_type="Redis",
                            operation=method_name,
                            duration_ms=duration,
                            status="failed",
                            error=str(e),
                        )
                        raise

                return patched_method

            # Patch all Redis commands
            for cmd in redis_commands:
                if hasattr(Redis, cmd):
                    original_methods[cmd] = getattr(Redis, cmd)
                    setattr(Redis, cmd, create_patched_method(cmd, original_methods[cmd]))

            print("✅ Redis monitoring patched successfully")
        except ImportError:
            print("ℹ️  Redis not installed, skipping Redis monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch Redis: {e}")


# ============================================================================
# CASSANDRA MONITOR
# ============================================================================


class CassandraMonitor(DatabaseMonitor):
    """Cassandra monitoring"""

    @staticmethod
    def patch_cassandra():
        """Patch Cassandra driver to track operations"""
        try:
            from cassandra.cluster import Session

            original_execute = Session.execute
            original_execute_async = Session.execute_async

            def patched_execute(self, query, parameters=None, *args, **kwargs):
                start = time.time()
                try:
                    result = original_execute(self, query, parameters, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    CassandraMonitor.log_operation(
                        db_type="Cassandra",
                        operation="execute",
                        duration_ms=duration,
                        query=str(query),
                        params=parameters,
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    CassandraMonitor.log_operation(
                        db_type="Cassandra",
                        operation="execute",
                        duration_ms=duration,
                        query=str(query),
                        status="failed",
                        error=str(e),
                    )
                    raise

            def patched_execute_async(self, query, parameters=None, *args, **kwargs):
                start = time.time()
                try:
                    future = original_execute_async(self, query, parameters, *args, **kwargs)

                    # Add callback to track completion
                    def log_completion(result):
                        duration = (time.time() - start) * 1000
                        CassandraMonitor.log_operation(
                            db_type="Cassandra",
                            operation="execute_async",
                            duration_ms=duration,
                            query=str(query),
                            params=parameters,
                        )

                    def log_error(exception):
                        duration = (time.time() - start) * 1000
                        CassandraMonitor.log_operation(
                            db_type="Cassandra",
                            operation="execute_async",
                            duration_ms=duration,
                            query=str(query),
                            status="failed",
                            error=str(exception),
                        )

                    future.add_callback(log_completion)
                    future.add_errback(log_error)

                    return future
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    CassandraMonitor.log_operation(
                        db_type="Cassandra",
                        operation="execute_async",
                        duration_ms=duration,
                        query=str(query),
                        status="failed",
                        error=str(e),
                    )
                    raise

            Session.execute = patched_execute
            Session.execute_async = patched_execute_async

            print("✅ Cassandra monitoring patched successfully")
        except ImportError:
            print("ℹ️  Cassandra driver not installed, skipping Cassandra monitoring")
        except Exception as e:
            print(f"⚠️  Failed to patch Cassandra: {e}")


# ============================================================================
# DECORATOR FOR MANUAL DB MONITORING
# ============================================================================


def monitor_db_operation(db_type: str = "Custom", operation_name: str = None):
    """
    Decorator to manually monitor any database operation

    Usage:
        @monitor_db_operation(db_type="MySQL", operation_name="get_user")
        def get_user_from_db(user_id):
            # your db code
            return user
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            op_name = operation_name or func.__name__

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000

                DatabaseMonitor.log_operation(
                    db_type=db_type,
                    operation=op_name,
                    duration_ms=duration,
                    metadata={"function": func.__name__, "module": func.__module__},
                )
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                DatabaseMonitor.log_operation(
                    db_type=db_type,
                    operation=op_name,
                    duration_ms=duration,
                    status="failed",
                    error=str(e),
                    metadata={"function": func.__name__, "module": func.__module__},
                )
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            op_name = operation_name or func.__name__

            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start) * 1000

                DatabaseMonitor.log_operation(
                    db_type=db_type,
                    operation=op_name,
                    duration_ms=duration,
                    metadata={"function": func.__name__, "module": func.__module__},
                )
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                DatabaseMonitor.log_operation(
                    db_type=db_type,
                    operation=op_name,
                    duration_ms=duration,
                    status="failed",
                    error=str(e),
                    metadata={"function": func.__name__, "module": func.__module__},
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# ============================================================================
# INITIALIZATION FUNCTION
# ============================================================================


def initialize_db_monitoring():
    """
    Initialize all database monitoring patches
    Call this once at application startup
    """
    print("\n" + "=" * 80)
    print("🔧 Initializing Database Monitoring...")
    print("=" * 80)

    MongoDBMonitor.patch_pymongo()
    MySQLMonitor.patch_mysql()
    PostgreSQLMonitor.patch_postgresql()
    SQLAlchemyMonitor.patch_sqlalchemy()
    RedisMonitor.patch_redis()
    CassandraMonitor.patch_cassandra()

    print("=" * 80)
    print("✅ Database Monitoring Initialization Complete!")
    print("=" * 80 + "\n")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "initialize_db_monitoring",
    "monitor_db_operation",
    "db_operations",
    "DatabaseMonitor",
    "MongoDBMonitor",
    "MySQLMonitor",
    "PostgreSQLMonitor",
    "SQLAlchemyMonitor",
    "RedisMonitor",
    "CassandraMonitor",
    "safe_serialize",
]

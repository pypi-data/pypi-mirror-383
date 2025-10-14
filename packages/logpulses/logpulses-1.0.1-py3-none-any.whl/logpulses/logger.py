import json
import time
import psutil
import platform
import uuid
import tracemalloc
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.datastructures import Headers
from typing import Callable
import contextvars
from functools import wraps

# Context variable to store DB operations for current request
db_operations = contextvars.ContextVar("db_operations", default=[])


class DBMonitor:
    """Monkey patches database libraries to track connections and query times"""

    _patched = False

    @classmethod
    def patch_all(cls):
        """Patch all supported database libraries"""
        if cls._patched:
            return

        cls._patch_pymongo()
        cls._patch_mysql()
        cls._patch_postgresql()
        cls._patch_sqlalchemy()
        cls._patch_redis()
        cls._patched = True

    @classmethod
    def _patch_pymongo(cls):
        """Patch PyMongo (MongoDB)"""
        try:
            import pymongo.collection
            import pymongo.cursor

            original_find = pymongo.collection.Collection.find
            original_insert_one = pymongo.collection.Collection.insert_one
            original_insert_many = pymongo.collection.Collection.insert_many
            original_update_one = pymongo.collection.Collection.update_one
            original_update_many = pymongo.collection.Collection.update_many
            original_delete_one = pymongo.collection.Collection.delete_one
            original_delete_many = pymongo.collection.Collection.delete_many
            original_aggregate = pymongo.collection.Collection.aggregate
            original_count = pymongo.collection.Collection.count_documents

            def wrap_mongo_operation(method_name, original_method):
                @wraps(original_method)
                def wrapper(self, *args, **kwargs):
                    start = time.time()
                    try:
                        result = original_method(self, *args, **kwargs)
                        duration = (time.time() - start) * 1000

                        # Extract query info
                        query_info = {
                            "type": "MongoDB",
                            "operation": method_name,
                            "collection": self.name,
                            "database": self.database.name,
                            "duration_ms": f"{duration:.2f}",
                            "query": args[0] if args else kwargs.get("filter", {}),
                        }

                        # Add operation-specific details
                        if method_name in ["insert_one", "insert_many"]:
                            query_info["document_count"] = (
                                len(args[0]) if method_name == "insert_many" else 1
                            )
                        elif method_name in [
                            "update_one",
                            "update_many",
                            "delete_one",
                            "delete_many",
                        ]:
                            if len(args) > 1:
                                query_info["update"] = args[1]

                        ops = db_operations.get()
                        ops.append(query_info)
                        db_operations.set(ops)

                        return result
                    except Exception as e:
                        duration = (time.time() - start) * 1000
                        ops = db_operations.get()
                        ops.append(
                            {
                                "type": "MongoDB",
                                "operation": method_name,
                                "collection": self.name,
                                "database": self.database.name,
                                "duration_ms": f"{duration:.2f}",
                                "error": str(e),
                                "status": "failed",
                            }
                        )
                        db_operations.set(ops)
                        raise

                return wrapper

            pymongo.collection.Collection.find = wrap_mongo_operation("find", original_find)
            pymongo.collection.Collection.insert_one = wrap_mongo_operation(
                "insert_one", original_insert_one
            )
            pymongo.collection.Collection.insert_many = wrap_mongo_operation(
                "insert_many", original_insert_many
            )
            pymongo.collection.Collection.update_one = wrap_mongo_operation(
                "update_one", original_update_one
            )
            pymongo.collection.Collection.update_many = wrap_mongo_operation(
                "update_many", original_update_many
            )
            pymongo.collection.Collection.delete_one = wrap_mongo_operation(
                "delete_one", original_delete_one
            )
            pymongo.collection.Collection.delete_many = wrap_mongo_operation(
                "delete_many", original_delete_many
            )
            pymongo.collection.Collection.aggregate = wrap_mongo_operation(
                "aggregate", original_aggregate
            )
            pymongo.collection.Collection.count_documents = wrap_mongo_operation(
                "count_documents", original_count
            )

        except ImportError:
            pass

    @classmethod
    def _patch_mysql(cls):
        """Patch MySQL connectors (mysql-connector-python and PyMySQL)"""
        # Patch mysql-connector-python
        try:
            import mysql.connector.cursor

            original_execute = mysql.connector.cursor.MySQLCursor.execute
            original_executemany = mysql.connector.cursor.MySQLCursor.executemany

            def wrap_mysql_execute(original_method, method_name):
                @wraps(original_method)
                def wrapper(self, *args, **kwargs):
                    start = time.time()
                    query = args[0] if args else kwargs.get("operation", "")
                    params = args[1] if len(args) > 1 else kwargs.get("params", None)

                    try:
                        result = original_method(self, *args, **kwargs)
                        duration = (time.time() - start) * 1000

                        ops = db_operations.get()
                        ops.append(
                            {
                                "type": "MySQL",
                                "operation": method_name,
                                "query": (
                                    query[:200] if isinstance(query, str) else str(query)[:200]
                                ),
                                "params": params,
                                "duration_ms": f"{duration:.2f}",
                                "rows_affected": self.rowcount if hasattr(self, "rowcount") else 0,
                            }
                        )
                        db_operations.set(ops)

                        return result
                    except Exception as e:
                        duration = (time.time() - start) * 1000
                        ops = db_operations.get()
                        ops.append(
                            {
                                "type": "MySQL",
                                "operation": method_name,
                                "query": (
                                    query[:200] if isinstance(query, str) else str(query)[:200]
                                ),
                                "duration_ms": f"{duration:.2f}",
                                "error": str(e),
                                "status": "failed",
                            }
                        )
                        db_operations.set(ops)
                        raise

                return wrapper

            mysql.connector.cursor.MySQLCursor.execute = wrap_mysql_execute(
                original_execute, "execute"
            )
            mysql.connector.cursor.MySQLCursor.executemany = wrap_mysql_execute(
                original_executemany, "executemany"
            )

        except ImportError:
            pass

        # Patch PyMySQL
        try:
            import pymysql.cursors

            original_execute = pymysql.cursors.Cursor.execute
            original_executemany = pymysql.cursors.Cursor.executemany

            def wrap_pymysql_execute(original_method, method_name):
                @wraps(original_method)
                def wrapper(self, query, args=None):
                    start = time.time()

                    try:
                        result = original_method(self, query, args)
                        duration = (time.time() - start) * 1000

                        ops = db_operations.get()
                        ops.append(
                            {
                                "type": "MySQL (PyMySQL)",
                                "operation": method_name,
                                "query": (
                                    query[:200] if isinstance(query, str) else str(query)[:200]
                                ),
                                "params": args,
                                "duration_ms": f"{duration:.2f}",
                                "rows_affected": self.rowcount if hasattr(self, "rowcount") else 0,
                            }
                        )
                        db_operations.set(ops)

                        return result
                    except Exception as e:
                        duration = (time.time() - start) * 1000
                        ops = db_operations.get()
                        ops.append(
                            {
                                "type": "MySQL (PyMySQL)",
                                "operation": method_name,
                                "query": (
                                    query[:200] if isinstance(query, str) else str(query)[:200]
                                ),
                                "duration_ms": f"{duration:.2f}",
                                "error": str(e),
                                "status": "failed",
                            }
                        )
                        db_operations.set(ops)
                        raise

                return wrapper

            pymysql.cursors.Cursor.execute = wrap_pymysql_execute(original_execute, "execute")
            pymysql.cursors.Cursor.executemany = wrap_pymysql_execute(
                original_executemany, "executemany"
            )

        except ImportError:
            pass

    @classmethod
    def _patch_postgresql(cls):
        """Patch psycopg2 (PostgreSQL)"""
        try:
            import psycopg2.extensions

            original_execute = psycopg2.extensions.cursor.execute
            original_executemany = psycopg2.extensions.cursor.executemany

            def wrap_pg_execute(original_method, method_name):
                @wraps(original_method)
                def wrapper(self, query, vars=None):
                    start = time.time()

                    try:
                        result = original_method(self, query, vars)
                        duration = (time.time() - start) * 1000

                        ops = db_operations.get()
                        ops.append(
                            {
                                "type": "PostgreSQL",
                                "operation": method_name,
                                "query": (
                                    query[:200] if isinstance(query, str) else str(query)[:200]
                                ),
                                "params": vars,
                                "duration_ms": f"{duration:.2f}",
                                "rows_affected": self.rowcount if hasattr(self, "rowcount") else 0,
                            }
                        )
                        db_operations.set(ops)

                        return result
                    except Exception as e:
                        duration = (time.time() - start) * 1000
                        ops = db_operations.get()
                        ops.append(
                            {
                                "type": "PostgreSQL",
                                "operation": method_name,
                                "query": (
                                    query[:200] if isinstance(query, str) else str(query)[:200]
                                ),
                                "duration_ms": f"{duration:.2f}",
                                "error": str(e),
                                "status": "failed",
                            }
                        )
                        db_operations.set(ops)
                        raise

                return wrapper

            psycopg2.extensions.cursor.execute = wrap_pg_execute(original_execute, "execute")
            psycopg2.extensions.cursor.executemany = wrap_pg_execute(
                original_executemany, "executemany"
            )

        except ImportError:
            pass

    @classmethod
    def _patch_sqlalchemy(cls):
        """Patch SQLAlchemy"""
        try:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine

            @event.listens_for(Engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                context._query_start_time = time.time()

            @event.listens_for(Engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                duration = (time.time() - context._query_start_time) * 1000

                ops = db_operations.get()
                ops.append(
                    {
                        "type": "SQLAlchemy",
                        "operation": "executemany" if executemany else "execute",
                        "query": (
                            statement[:200] if isinstance(statement, str) else str(statement)[:200]
                        ),
                        "params": parameters,
                        "duration_ms": f"{duration:.2f}",
                        "dialect": conn.dialect.name,
                    }
                )
                db_operations.set(ops)

        except ImportError:
            pass

    @classmethod
    def _patch_redis(cls):
        """Patch Redis"""
        try:
            import redis

            original_execute_command = redis.Redis.execute_command

            @wraps(original_execute_command)
            def wrapper(self, *args, **kwargs):
                start = time.time()
                command = args[0] if args else "UNKNOWN"

                try:
                    result = original_execute_command(self, *args, **kwargs)
                    duration = (time.time() - start) * 1000

                    ops = db_operations.get()
                    ops.append(
                        {
                            "type": "Redis",
                            "operation": command,
                            "args": args[1:] if len(args) > 1 else [],
                            "duration_ms": f"{duration:.2f}",
                        }
                    )
                    db_operations.set(ops)

                    return result
                except Exception as e:
                    duration = (time.time() - start) * 1000
                    ops = db_operations.get()
                    ops.append(
                        {
                            "type": "Redis",
                            "operation": command,
                            "duration_ms": f"{duration:.2f}",
                            "error": str(e),
                            "status": "failed",
                        }
                    )
                    db_operations.set(ops)
                    raise

            redis.Redis.execute_command = wrapper

        except ImportError:
            pass


def get_device_id():
    """Get unique device identifier"""
    try:
        return str(uuid.UUID(int=uuid.getnode()))
    except Exception:
        return platform.node()


def get_system_metrics():
    """Get current system CPU and memory metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
        mem_info = psutil.virtual_memory()
        return {
            "cpuUsage": f"{cpu_percent:.1f}%",
            "memoryUsage": {
                "total": f"{mem_info.total / (1024 ** 3):.2f} GB",
                "used": f"{mem_info.used / (1024 ** 3):.2f} GB",
                "available": f"{mem_info.available / (1024 ** 3):.2f} GB",
                "percent": f"{mem_info.percent:.1f}%",
            },
        }
    except Exception as e:
        return {"error": str(e)}


def get_active_network_info():
    """Get active network interface (prioritizes WiFi)"""
    try:
        net_io = psutil.net_io_counters(pernic=True)
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        wireless_keywords = ["wlan", "wi-fi", "wifi", "wireless", "802.11"]
        best_interface = None
        best_score = -1

        for iface_name, addrs in net_if_addrs.items():
            if iface_name.lower() == "lo" or iface_name.startswith("Loopback"):
                continue
            if iface_name in net_if_stats and not net_if_stats[iface_name].isup:
                continue

            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    continue
                if addr.family.name == "AF_INET" and addr.address != "127.0.0.1":
                    score = 0
                    if any(kw in iface_name.lower() for kw in wireless_keywords):
                        score += 100
                        interface_type = "WiFi"
                    elif "ethernet" in iface_name.lower() or "eth" in iface_name.lower():
                        score += 50
                        interface_type = "Ethernet"
                    else:
                        interface_type = "Other"

                    if iface_name in net_io:
                        io_stats = net_io[iface_name]
                        if io_stats.bytes_sent > 0 or io_stats.bytes_recv > 0:
                            score += 10

                    if addr.address.startswith(("192.168.", "10.", "172.")):
                        score += 5

                    if score > best_score:
                        best_score = score
                        best_interface = {
                            "interface": iface_name,
                            "type": interface_type,
                            "ip": addr.address,
                            "netmask": addr.netmask,
                            "isActive": True,
                        }
                        if iface_name in net_io:
                            io_stats = net_io[iface_name]
                            best_interface.update(
                                {
                                    "bytesSent": f"{io_stats.bytes_sent / (1024**2):.2f} MB",
                                    "bytesRecv": f"{io_stats.bytes_recv / (1024**2):.2f} MB",
                                }
                            )

        return best_interface or {"error": "No active network interface found"}
    except Exception as e:
        return {"error": str(e)}


def get_memory_usage_delta(start_snapshot):
    """Calculate memory used by the current request"""
    try:
        current = tracemalloc.take_snapshot()
        stats = current.compare_to(start_snapshot, "lineno")
        total_kb = sum(stat.size_diff for stat in stats) / 1024
        return f"{total_kb:.2f} KB" if total_kb > 0 else "< 1 KB"
    except Exception:
        return "N/A"


def print_log(log_data):
    """Pretty print log data"""
    print("\n" + "=" * 80)
    print(json.dumps(log_data, indent=2, ensure_ascii=False))
    print("=" * 80 + "\n")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Universal middleware that logs ALL requests automatically with DB monitoring.

    ✅ NO DECORATORS NEEDED!
    ✅ Automatically detects and tracks DB operations
    ✅ Supports MongoDB, MySQL, PostgreSQL, SQLAlchemy, Redis
    ✅ Tracks connection time and query execution time
    ✅ Works with all HTTP methods
    """

    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        # Patch database libraries on initialization
        DBMonitor.patch_all()

    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Reset DB operations for this request
        db_operations.set([])

        # Start tracking
        tracemalloc.start()
        mem_snapshot = tracemalloc.take_snapshot()
        start_time = time.time()

        # Capture request info
        route_path = request.url.path
        method = request.method
        full_url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Cache request body
        body_bytes = await request.body()
        request_body_for_log = None
        body_size = len(body_bytes)

        # Parse request body for logging
        query_params = dict(request.query_params)
        query_string = str(request.url.query) if request.url.query else ""
        query_size = len(query_string.encode("utf-8")) if query_string else 0

        # Calculate total request size
        request_size = body_size + query_size

        # Build comprehensive request data structure
        request_data = {}

        # Handle request body for methods that typically have bodies
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            if body_bytes:
                try:
                    request_data["body"] = json.loads(body_bytes)
                except json.JSONDecodeError:
                    request_data["body"] = body_bytes.decode("utf-8", errors="replace")[:500]

            if query_params:
                request_data["queryParams"] = query_params

            if not request_data:
                request_body_for_log = "No body or query parameters"
            else:
                request_body_for_log = request_data

        # Handle GET and HEAD methods
        elif method in ("GET", "HEAD"):
            if query_params:
                request_body_for_log = {"queryParams": query_params}
            else:
                request_body_for_log = "No query parameters"

        # Handle other methods
        else:
            if body_bytes:
                try:
                    request_data["body"] = json.loads(body_bytes)
                except json.JSONDecodeError:
                    request_data["body"] = body_bytes.decode("utf-8", errors="replace")[:500]

            if query_params:
                request_data["queryParams"] = query_params

            if request_data:
                request_body_for_log = request_data
            else:
                request_body_for_log = "No data"

        # Response tracking
        status_code = 500
        response_body = None
        response_size = 0
        error_details = None

        try:
            # Call the next middleware/endpoint
            response = await call_next(request)
            status_code = response.status_code

            # Try to capture response body
            response_body_list = []
            async for chunk in response.body_iterator:
                response_body_list.append(chunk)

            response_body_bytes = b"".join(response_body_list)
            response_size = len(response_body_bytes)

            # Parse response body
            try:
                response_body = json.loads(response_body_bytes) if response_body_bytes else None
            except json.JSONDecodeError:
                response_body = response_body_bytes.decode("utf-8", errors="replace")
                if len(response_body) > 1000:
                    response_body = response_body[:1000] + "... (truncated)"

            # If response indicates an error, capture it
            if status_code >= 400:
                error_details = {
                    "statusCode": status_code,
                    "type": "HTTP Error",
                    "message": (
                        response_body
                        if isinstance(response_body, str)
                        else (
                            response_body.get("detail", "Unknown error")
                            if isinstance(response_body, dict)
                            else "Error occurred"
                        )
                    ),
                    "responseBody": response_body,
                }

            # Recreate response with the captured body
            from starlette.responses import Response as StarletteResponse

            response = StarletteResponse(
                content=response_body_bytes,
                status_code=status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as e:
            import traceback

            # Determine status code based on exception type
            if hasattr(e, "status_code"):
                status_code = e.status_code
            elif isinstance(e, ValueError):
                status_code = 400
            elif isinstance(e, KeyError):
                status_code = 400
            elif isinstance(e, TypeError):
                status_code = 400
            elif isinstance(e, PermissionError):
                status_code = 403
            elif isinstance(e, FileNotFoundError):
                status_code = 404
            elif isinstance(e, TimeoutError):
                status_code = 504
            elif isinstance(e, ConnectionError):
                status_code = 503
            else:
                status_code = 500

            error_details = {
                "type": type(e).__name__,
                "message": str(e),
                "statusCode": status_code,
                "traceback": traceback.format_exc(),
                "failurePoint": "Request processing",
                "exceptionModule": type(e).__module__,
                "hasStatusCode": hasattr(e, "status_code"),
            }

            # Create error response
            error_response_body = {
                "error": type(e).__name__,
                "detail": str(e),
                "statusCode": status_code,
            }

            response = Response(
                content=json.dumps(error_response_body),
                status_code=status_code,
                media_type="application/json",
            )

        finally:
            # Calculate metrics
            processing_time = (time.time() - start_time) * 1000
            memory_used = get_memory_usage_delta(mem_snapshot)
            tracemalloc.stop()

            # Get DB operations
            db_ops = db_operations.get()

            # Calculate DB statistics
            db_stats = None
            if db_ops:
                total_db_time = sum(
                    float(op["duration_ms"]) for op in db_ops if "duration_ms" in op
                )
                db_types = list(set(op["type"] for op in db_ops))
                failed_ops = [op for op in db_ops if op.get("status") == "failed"]

                db_stats = {
                    "totalOperations": len(db_ops),
                    "totalDuration": f"{total_db_time:.2f} ms",
                    "databaseTypes": db_types,
                    "operations": db_ops,
                    "failedOperations": len(failed_ops),
                    "percentageOfRequestTime": f"{(total_db_time / processing_time * 100):.1f}%",
                }

            # Build log
            log_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "request": {
                    "route": route_path,
                    "method": method,
                    "fullUrl": full_url,
                    "clientIp": client_ip,
                    "userAgent": user_agent,
                    "size": (
                        {
                            "total": f"{request_size} bytes",
                            "body": f"{body_size} bytes",
                            "queryParams": f"{query_size} bytes",
                        }
                        if query_size > 0
                        else f"{request_size} bytes"
                    ),
                    "body": request_body_for_log,
                },
                "response": {
                    "status": status_code,
                    "success": status_code < 400,
                    "size": f"{response_size} bytes",
                    "body": (response_body if response_size < 5000 else "<response too large>"),
                },
                "performance": {
                    "processingTime": f"{processing_time:.2f} ms",
                    "memoryUsed": memory_used,
                },
                "system": get_system_metrics(),
                "network": get_active_network_info(),
                "server": {
                    "instanceId": get_device_id(),
                    "platform": platform.system(),
                    "hostname": platform.node(),
                },
            }

            # Add database stats if any DB operations occurred
            if db_stats:
                log_data["database"] = db_stats

            # Add error details if request failed
            if error_details:
                log_data["error"] = error_details
                log_data["failureAnalysis"] = {
                    "statusCode": status_code,
                    "category": self._categorize_error(status_code),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

            print_log(log_data)

        return response

    def _categorize_error(self, status_code):
        """Categorize error based on status code"""
        error_categories = {
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Access denied",
            404: "Not Found - Resource doesn't exist",
            405: "Method Not Allowed - HTTP method not supported",
            408: "Request Timeout - Client took too long",
            409: "Conflict - Resource state conflict",
            410: "Gone - Resource permanently deleted",
            413: "Payload Too Large - Request body too big",
            415: "Unsupported Media Type - Invalid content type",
            422: "Unprocessable Entity - Validation error",
            429: "Too Many Requests - Rate limit exceeded",
            500: "Internal Server Error - Application error",
            501: "Not Implemented - Feature not available",
            502: "Bad Gateway - Upstream server error",
            503: "Service Unavailable - Server overloaded",
            504: "Gateway Timeout - Request timeout",
        }

        if status_code in error_categories:
            return error_categories[status_code]

        if 400 <= status_code < 500:
            return "Client Error - Request issue"
        elif 500 <= status_code < 600:
            return "Server Error - Backend issue"
        else:
            return "Unknown Error"


# Decorator is now completely unnecessary - kept only for backward compatibility
def log_request(func: Callable):
    """
    This decorator is NO LONGER NEEDED!
    RequestLoggingMiddleware handles everything automatically.
    """
    return func

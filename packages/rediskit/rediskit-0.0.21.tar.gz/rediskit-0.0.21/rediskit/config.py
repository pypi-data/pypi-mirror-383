import os

from DockerBuildSystem import TerminalTools

from rediskit.utils import base64_json_to_dict

TerminalTools.LoadDefaultEnvironmentVariablesFile("private.env")
TerminalTools.LoadDefaultEnvironmentVariablesFile(".env")

# Redis Settings
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
REDIS_TOP_NODE = os.environ.get("REDIS_TOP_NODE", "redis_kit_node")
REDIS_SCAN_COUNT = int(os.environ.get("REDIS_SCAN_COUNT", "10000"))
REDIS_SKIP_CACHING = os.environ.get("REDIS_SKIP_CACHING", "false").upper() == "TRUE"

# Lock Settings
REDIS_KIT_LOCK_SETTINGS_REDIS_NAMESPACE = os.environ.get("REDIS_KIT_LOCK_SETTINGS_REDIS_NAMESPACE", f"{REDIS_TOP_NODE}:LOCK")
REDIS_KIT_LOCK_ASYNC_SETTINGS_REDIS_NAMESPACE = os.environ.get("REDIS_KIT_LOCK_ASYNC_SETTINGS_REDIS_NAMESPACE", f"{REDIS_TOP_NODE}:LOCK_ASYNC")
REDIS_KIT_LOCK_CACHE_MUTEX = os.environ.get("REDIS_KIT_LOCK_CACHE_MUTEX", "REDIS_KIT_LOCK_CACHE_MUTEX")

# Encryption Settings
REDIS_KIT_ENCRYPTION_SECRET = base64_json_to_dict(os.environ.get("REDIS_KIT_ENCRYPTION_SECRET", ""))

# Semaphore Settings
REDIS_KIT_SEMAPHORE_SETTINGS_REDIS_NAMESPACE = os.environ.get("REDIS_KIT_SEMAPHORE_SETTINGS_REDIS_NAMESPACE", f"{REDIS_TOP_NODE}:Semaphore")
REDIS_KIT_SEMAPHORE_SETTINGS_STALE_TIMEOUT_SECONDS = int(os.environ.get("REDIS_KIT_SEMAPHORE_SETTINGS_STALE_TIMEOUT_SECONDS", "30"))
REDIS_KIT_SEMAPHORE_LOCK_TIME_TO_LIVE = int(os.environ.get("REDIS_KIT_SEMAPHORE_LOCK_TIME_TO_LIVE", "30"))

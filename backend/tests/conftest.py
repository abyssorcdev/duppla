"""Root conftest for backend tests.

Sets up environment variables needed for test collection
before the application modules are imported.
"""

import os

os.environ.setdefault("TESTING", "true")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault(
    "DATABASE_URL",
    f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:{os.environ.get('POSTGRES_PASSWORD', 'postgres')}"  # pragma: allowlist secret
    f"@{os.environ.get('POSTGRES_HOST', 'localhost')}:{os.environ.get('POSTGRES_PORT', '5432')}"
    f"/{os.environ.get('POSTGRES_DB', 'duppla_test')}",
)

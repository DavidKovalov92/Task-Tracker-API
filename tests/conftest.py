import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(autouse=True)
def mock_django_redis():
    with patch("django_redis.get_redis_connection") as mock_conn:
        fake_redis = MagicMock()
        fake_redis.get.return_value = None
        fake_redis.set.return_value = True
        fake_redis.delete.return_value = True
        fake_redis.keys.return_value = []
        mock_conn.return_value = fake_redis
        yield


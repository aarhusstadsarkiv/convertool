# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from convertool.exceptions import LibreError

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestLibreError:
    def test_init(self):
        libre_error = LibreError("test")
        assert str(libre_error) == "test"
        assert libre_error.timeout is False
        libre_error = LibreError("test_timeout", timeout=True)
        assert libre_error.timeout is True

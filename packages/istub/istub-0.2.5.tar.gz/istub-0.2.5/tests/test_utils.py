from pathlib import Path

from istub.utils import cleanup_output, get_python_path_str, get_replace_paths, shorten_path


class TestUtils:
    def test_get_replace_paths(self) -> None:
        paths = get_replace_paths()
        assert paths

    def test_cleanup_output(self) -> None:
        output = [
            "line 1",
            "line 2 # 0x1234567890ab",
        ]
        assert cleanup_output(output) == [
            "line 1",
            "line 2 # HASH",
        ]

    def test_shorten_path(self) -> None:
        assert shorten_path(Path("/test_utils.py")) == "/test_utils.py"
        assert shorten_path(Path("tests/test_utils.py")) == "tests/test_utils.py"
        assert shorten_path(Path.cwd() / "test.py") == "./test.py"
        assert shorten_path(Path.cwd() / "dir" / "test.py") == "dir/test.py"

    def test_get_python_path_str(self) -> None:
        assert get_python_path_str()

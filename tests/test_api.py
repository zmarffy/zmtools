from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import Any, ContextManager, Dict, List

import pytest

import zmtools

FIXTURE_DIR = Path(__file__).parent.resolve() / "test_files"


@pytest.mark.datafiles(FIXTURE_DIR / "working_directory")
@pytest.mark.parametrize(
    "subdir,files_in_dir",
    [
        (Path("subfolder1"), [Path("file1.txt")]),
        (Path("subfolder2"), [Path("file2.txt")]),
    ],
)
def test_working_directory(
    datafiles: Path, subdir: Path, files_in_dir: List[Path]
) -> None:
    with zmtools.working_directory(datafiles / subdir):
        assert list(Path(".").iterdir()) == files_in_dir


@pytest.mark.parametrize(
    "string,delimiter,expected_string",
    [
        ("This is a sentence.", " ", "This Is A Sentence."),
        ("word", "\n", "Word"),
    ],
)
def test_capitalize_each_word(
    string: str, delimiter: str, expected_string: str
) -> None:
    assert zmtools.capitalize_each_word(string, delimiter) == expected_string


@pytest.mark.parametrize(
    "string,expected_string",
    [
        ("This\n  is\n    a\n      sentence.", "This\nis\na\nsentence."),
        ("word", "word"),
    ],
)
def test_strip_each_line(string: str, expected_string: str) -> None:
    assert zmtools.strip_each_line(string) == expected_string


@pytest.mark.parametrize(
    "requires_enter,simulated_input,expected_output",
    [
        (True, "y", True),
        (False, "n", False),
    ],
)
def test_input_multiline(
    monkeypatch: pytest.MonkeyPatch,
    requires_enter: bool,
    simulated_input: str,
    expected_output: bool,
) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": simulated_input)
    monkeypatch.setattr("zmtools.api.getchar", lambda: simulated_input)
    assert zmtools.y_to_continue(requires_enter=requires_enter) == expected_output


@pytest.mark.parametrize(
    "default_string,simulated_input,expected_output",
    [
        ("", "text\n\nmore text ", "text\n\nmore text"),
        ("default", "\n", "default"),
    ],
)
def test_y_to_continue(
    monkeypatch: pytest.MonkeyPatch,
    default_string: str,
    simulated_input: str,
    expected_output: str,
) -> None:
    monkeypatch.setattr("zmtools.api.sys.stdin.read", lambda: simulated_input)
    assert zmtools.input_multiline(default=default_string) == expected_output


@pytest.mark.parametrize(
    "exception,expected_dict",
    [
        (
            ValueError("Whatever"),
            {"type": "ValueError", "message": "Whatever"},
        ),
    ],
)
def test_exception_to_dict(exception: Exception, expected_dict: Dict[str, str]) -> None:
    assert zmtools.exception_to_dict(exception) == expected_dict


@pytest.mark.parametrize(
    "string,length,elipsis,expected_string",
    [
        ("A small string", 25, True, "A small string"),
        ("A decently long string", 10, True, "A decently..."),
        ("no", 1, False, "n"),
    ],
)
def test_truncate(
    string: str, length: int, elipsis: bool, expected_string: str
) -> None:
    assert zmtools.truncate(string, length=length, elipsis=elipsis) == expected_string


@pytest.mark.datafiles(FIXTURE_DIR / "get_dpkg_version")
@pytest.mark.parametrize(
    "package_name,expected_version",
    [
        ("mypackage", "1.0.0-1ubuntu1.10"),
    ],
)
def test_get_dpkg_package_version(
    datafiles: Path,
    monkeypatch: pytest.MonkeyPatch,
    package_name: str,
    expected_version: str,
) -> None:
    def _read_file(file_path: Path):
        with open(file_path, "rb") as f:
            return f.read()

    monkeypatch.setattr(
        "zmtools.api.subprocess.check_output",
        lambda cmd: _read_file(datafiles / cmd[2]),
    )
    assert zmtools.get_dpkg_package_version(package_name) == expected_version


@pytest.mark.parametrize(
    "items,simulated_input,raises_expectation,expected_item",
    [
        ([1, 2, 3, 4], "2", does_not_raise(), 2),
        ([], "2", pytest.raises(IndexError), None),
        ([1, 2], "4", pytest.raises(IndexError), None),
        ([9], None, does_not_raise(), 9),
        ([1, 2], "a", pytest.raises(ValueError), None),
    ],
)
def test_picker(
    monkeypatch: pytest.MonkeyPatch,
    items: list,
    simulated_input: str,
    raises_expectation: ContextManager,
    expected_item: Any,
) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": simulated_input)
    with raises_expectation:
        assert zmtools.picker(items) == expected_item


@pytest.mark.datafiles(FIXTURE_DIR / "read_text_file")
@pytest.mark.parametrize(
    "file_location,not_exists_ok,raises_expectation,expected_text",
    [
        (Path("subfolder1", "file1.txt"), False, does_not_raise(), "content1"),
        (
            Path("subfolder1", "file2.txt"),
            False,
            pytest.raises(FileNotFoundError),
            None,
        ),
        (Path("subfolder2", "file1.txt"), True, does_not_raise(), ""),
    ],
)
def test_read_text_file(
    datafiles: Path,
    file_location: Path,
    not_exists_ok: bool,
    raises_expectation: ContextManager,
    expected_text: str,
) -> None:
    print(datafiles / file_location)
    with raises_expectation:
        assert (
            zmtools.read_text_file(
                datafiles / file_location, not_exists_ok=not_exists_ok
            )
            == expected_text
        )


@pytest.fixture
@pytest.mark.parametrize(
    "content",
    [
        "content",
    ],
)
def test_write_text_file(tmp_path: str, content: str):
    def _read_file(file_path: Path):
        with open(file_path, "r") as f:
            return f.read()

    file_location = Path(tmp_path)
    zmtools.write_text_file(file_location, content)
    assert _read_file(file_location) == content

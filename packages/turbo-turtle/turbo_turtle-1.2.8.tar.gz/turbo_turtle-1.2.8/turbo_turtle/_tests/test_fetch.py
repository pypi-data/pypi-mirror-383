"""Test :mod:`turbo_turtle._fetch`."""

import contextlib
import pathlib
import platform
from unittest.mock import patch

import pytest

from turbo_turtle import _fetch

does_not_raise = contextlib.nullcontext()


def platform_check() -> tuple[bool, str]:
    """Check platform and set platform specific variables.

    :return: tuple (root_fs, testing_windows)
    :rtype: (str, bool)
    """
    if platform.system().lower() == "windows":
        root_fs = "C:\\"
        testing_windows = True
    else:
        root_fs = "/"
        testing_windows = False
    return testing_windows, root_fs


testing_windows, root_fs = platform_check()

if testing_windows:
    root_directory = pathlib.Path("C:/path/to/source")
    destination = pathlib.Path("C:/path/to/destination")
else:
    root_directory = pathlib.Path("/path/to/source")
    destination = pathlib.Path("/path/to/destination")
source_files = [pathlib.Path("dummy.file1"), pathlib.Path("dummy.file2")]

one_file_source_tree = [root_directory / source_files[0]]
one_file_destination_tree = [destination / source_files[0]]
one_file_copy_tuples = ((one_file_source_tree[0], one_file_destination_tree[0]),)

two_file_source_tree = [root_directory / path for path in source_files]
two_file_destination_tree = [destination / path for path in source_files]


def test_fetch() -> None:
    """Test :func:`turbo_turtle._fetch.main`."""
    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with patch("turbo_turtle._fetch.recursive_copy") as mock_recursive_copy, pytest.raises(RuntimeError):
        try:
            _fetch.main(
                "dummy_subcommand",
                pathlib.Path("/directory/assumptions/are/wrong"),
                ["dummy/relative/path"],
                "/dummy/destination",
            )
        finally:
            mock_recursive_copy.assert_not_called()


conditional_copy_input = {
    "one new file": (one_file_copy_tuples, [False], [False], one_file_copy_tuples[0]),  # File does not exist
    "one different file": (  # File does exist, but it's different from the source file
        one_file_copy_tuples,
        [True],
        [False],
        one_file_copy_tuples[0],
    ),
    "one identical file": (one_file_copy_tuples, [True], [True], None),  # File exists and is identical to source file
    "one missing (different) file": (  # File doesn't exist and is identical to source file. Should never actually occur
        one_file_copy_tuples,
        [False],
        [True],
        one_file_copy_tuples[0],
    ),
}


@pytest.mark.parametrize(
    "copy_tuples, exists_side_effect, filecmp_side_effect, copyfile_call",
    conditional_copy_input.values(),
    ids=conditional_copy_input.keys(),
)
def test_conditional_copy(
    copy_tuples: list[tuple[pathlib.Path, pathlib.Path]],
    exists_side_effect: list[bool],
    filecmp_side_effect: list[bool],
    copyfile_call: tuple[pathlib.Path, pathlib.Path],
) -> None:
    """Test :func:`turbo_turtle._fetch.conditional_copy`."""
    with (
        patch("pathlib.Path.exists", side_effect=exists_side_effect),
        patch("filecmp.cmp", side_effect=filecmp_side_effect),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("shutil.copyfile") as mock_copyfile,
    ):
        _fetch.conditional_copy(copy_tuples)
        if copyfile_call:
            mock_mkdir.assert_called_once()
            mock_copyfile.assert_called_once_with(*copyfile_call)
        else:
            mock_copyfile.assert_not_called()


available_files_input = {
    "one file, str": ("/path/to/source", "dummy.file1", [True], [False], [], one_file_source_tree, [], None),
    "one file, list": ("/path/to/source", ["dummy.file1"], [True], [False], [], one_file_source_tree, [], None),
    "one file, not found": (
        "/path/to/source",
        ["dummy.file1"],
        [False],
        [False],
        [[]],
        [],
        ["dummy.file1"],
        "dummy.file1",
    ),
    "two files": (
        "/path/to/source",
        ["dummy.file2", "dummy.file1"],
        [True, True],
        [],
        [],
        two_file_source_tree,
        [],
        None,
    ),
    "one directory, one file": (
        "/path/to",
        "source",
        [False, True],
        [True],
        [one_file_source_tree],
        one_file_source_tree,
        [],
        "*",
    ),
    "one directory, two files": (
        "/path/to",
        "source",
        [False, True, True],
        [True],
        [two_file_source_tree],
        two_file_source_tree,
        [],
        "*",
    ),
    "two files, rglob pattern": (
        "/path/to/source",
        ["dummy.file*"],
        [False, True, True],
        [False],
        [two_file_source_tree],
        two_file_source_tree,
        [],
        "dummy.file*",
    ),
}


@pytest.mark.parametrize(
    (
        "root_directory",
        "relative_paths",
        "is_file_side_effect",
        "is_dir_side_effect",
        "rglob_side_effect",
        "expected_files",
        "expected_missing",
        "mock_rglob_argument",
    ),
    available_files_input.values(),
    ids=available_files_input.keys(),
)
def test_available_files(
    root_directory: str,
    relative_paths: list[str],
    is_file_side_effect: list[bool],
    is_dir_side_effect: list[bool],
    rglob_side_effect: list[list[pathlib.Path]],
    expected_files: list[pathlib.Path],
    expected_missing: list[pathlib.Path],
    mock_rglob_argument: str,
) -> None:
    """Test :func:`turbo_turtle._fetch.available_files`."""
    with (
        patch("pathlib.Path.is_file", side_effect=is_file_side_effect),
        patch("pathlib.Path.is_dir", side_effect=is_dir_side_effect),
        patch("pathlib.Path.rglob", side_effect=rglob_side_effect) as mock_rglob,
    ):
        available_files, not_found = _fetch.available_files(root_directory, relative_paths)
        assert available_files == expected_files
        assert not_found == expected_missing
        if mock_rglob_argument:
            mock_rglob.assert_called_once_with(mock_rglob_argument)
        else:
            mock_rglob.assert_not_called()


build_source_files_input: dict[str, tuple] = {
    "one file not matched": (
        "/path/to/source",
        ["dummy.file1"],
        ["notamatch"],
        (one_file_source_tree, []),
        one_file_source_tree,
    ),
    "one file matched": ("/path/to/source", ["dummy.file1"], ["dummy"], (one_file_source_tree, []), []),
    "two files, one matched": (
        "/path/to/source",
        ["dummy.file1", "matched"],
        ["matched"],
        ([one_file_source_tree[0], pathlib.Path("/path/to/source/matched")], []),
        one_file_source_tree,
    ),
}


@pytest.mark.parametrize(
    ("root_directory", "relative_paths", "exclude_patterns", "available_files_side_effect", "expected_source_files"),
    build_source_files_input.values(),
    ids=build_source_files_input.keys(),
)
def test_build_source_files(
    root_directory: str,
    relative_paths: list[str],
    exclude_patterns: list[str],
    available_files_side_effect: tuple[list[pathlib.Path], list],
    expected_source_files: list[pathlib.Path],
) -> None:
    """Test :func:`turbo_turtle._fetch.build_source_files`."""
    with patch("turbo_turtle._fetch.available_files", return_value=available_files_side_effect):
        source_files, _not_found = _fetch.build_source_files(
            root_directory, relative_paths, exclude_patterns=exclude_patterns
        )
        assert source_files == expected_source_files


expected_path = root_directory
longest_common_path_prefix_input = {
    "no list": ([], expected_path, pytest.raises(RuntimeError)),
    "one file, str": (str(one_file_source_tree[0]), expected_path, pytest.raises(ValueError)),
    "one file, path": (one_file_source_tree[0], expected_path, pytest.raises(TypeError)),
    "one file, list": (one_file_source_tree, expected_path, does_not_raise),
    "two files": (two_file_source_tree, expected_path, does_not_raise),
}


@pytest.mark.parametrize(
    "file_list, expected_path, outcome",
    longest_common_path_prefix_input.values(),
    ids=longest_common_path_prefix_input.keys(),
)
def test_longest_common_path_prefix(
    file_list: str | pathlib.Path | list[pathlib.Path],
    expected_path: pathlib.Path,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Test :func:`turbo_turtle._fetch.longest_common_path_prefix`."""
    with outcome:
        try:
            path_prefix = _fetch.longest_common_path_prefix(file_list)
            assert path_prefix == expected_path
        finally:
            pass


build_destination_files_input = {
    "two files, one exists": (
        "/path/to/destination",
        two_file_source_tree,
        [False, True],
        two_file_destination_tree,
        [two_file_destination_tree[1]],
    )
}


@pytest.mark.parametrize(
    "destination, requested_paths, exists_side_effect, expected_destination_files, expected_existing_files",
    build_destination_files_input.values(),
    ids=build_destination_files_input.keys(),
)
def test_build_destination_files(
    destination: str,
    requested_paths: list[pathlib.Path],
    exists_side_effect: list[bool],
    expected_destination_files: list[pathlib.Path],
    expected_existing_files: list[pathlib.Path],
) -> None:
    """Test :func:`turbo_turtle._fetch.build_destination_files`."""
    with patch("pathlib.Path.exists", side_effect=exists_side_effect):
        destination_files, existing_files = _fetch.build_destination_files(destination, requested_paths)
        assert destination_files == expected_destination_files
        assert existing_files == expected_existing_files


build_copy_tuples_input = {
    "two files, one exists, overwrite": (
        "/path/to/destination",
        two_file_source_tree,
        True,
        (two_file_destination_tree, [two_file_destination_tree[1]]),
        list(zip(two_file_source_tree, two_file_destination_tree, strict=True)),
    ),
    "two files, one exists, no overwrite": (
        "/path/to/destination",
        two_file_source_tree,
        False,
        (two_file_destination_tree, [two_file_destination_tree[1]]),
        list(zip([two_file_source_tree[0]], [two_file_destination_tree[0]], strict=True)),
    ),
}


@pytest.mark.parametrize(
    (
        "destination",
        "requested_paths_resolved",
        "overwrite",
        "build_destination_files_side_effect",
        "expected_copy_tuples",
    ),
    build_copy_tuples_input.values(),
    ids=build_copy_tuples_input.keys(),
)
def test_build_copy_tuples(
    destination: str,
    requested_paths_resolved: list[pathlib.Path],
    overwrite: bool,
    build_destination_files_side_effect: tuple[list[pathlib.Path], list[pathlib.Path]],
    expected_copy_tuples: list,
) -> None:
    """Test :func:`turbo_turtle._fetch.build_copy_tuples`."""
    with patch("turbo_turtle._fetch.build_destination_files", return_value=build_destination_files_side_effect):
        copy_tuples = _fetch.build_copy_tuples(destination, requested_paths_resolved, overwrite=overwrite)
        assert copy_tuples == expected_copy_tuples


def test_print_list() -> None:
    """Test :func:`turbo_turtle._fetch.print_list`."""
    # TODO: implement stdout tests
    pass


@pytest.mark.parametrize(
    "root_directory, source_files, source_tree, destination_tree",
    [
        (root_directory, source_files, two_file_source_tree, two_file_destination_tree),
        (root_directory, source_files, two_file_source_tree, two_file_destination_tree),
    ],
)
def test_recursive_copy(
    root_directory: pathlib.Path,
    source_files: list[pathlib.Path],
    source_tree: list[pathlib.Path],
    destination_tree: list[pathlib.Path],
) -> None:
    """Test :func:`turbo_turtle._fetch.recursive_copy`."""
    # Dummy modsim_template tree
    copy_tuples = list(zip(source_tree, destination_tree, strict=True))
    not_found: list = []
    available_files_output = (source_tree, not_found)
    single_file_requested = ([source_tree[0]], not_found)

    # Files in destination tree do not exist. Copy the modsim_template file tree.
    with (
        patch("turbo_turtle._fetch.available_files", return_value=available_files_output),
        patch("turbo_turtle._fetch.print_list") as mock_print_list,
        patch("turbo_turtle._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise,
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination)
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do not exist. Only want the first file. Copy the first file..
    with (
        patch("turbo_turtle._fetch.available_files", side_effect=[available_files_output, single_file_requested]),
        patch("turbo_turtle._fetch.print_list") as mock_print_list,
        patch("turbo_turtle._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise,
    ):
        _fetch.recursive_copy(
            root_directory.parent, root_directory.name, destination, requested_paths=[source_files[0]]
        )
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with([copy_tuples[0]])

    # Files in destination tree do not exist, but dry-run. Print destination file tree.
    with (
        patch("turbo_turtle._fetch.available_files", return_value=available_files_output),
        patch("turbo_turtle._fetch.print_list") as mock_print_list,
        patch("turbo_turtle._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise,
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, dry_run=True)
        mock_print_list.assert_called_once_with(destination_tree)
        mock_conditional_copy.assert_not_called()

    # Files in destination tree do not exist, but print_available. Print source file tree.
    with (
        patch("turbo_turtle._fetch.available_files", return_value=available_files_output),
        patch("turbo_turtle._fetch.print_list") as mock_print_list,
        patch("turbo_turtle._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise,
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, print_available=True)
        mock_print_list.assert_called_once_with(source_files)
        mock_conditional_copy.assert_not_called()

    # All files in destination tree do exist. Don't copy the modsim_template file tree.
    # Don't error out, just remove destination file from the copy list
    with (
        patch("turbo_turtle._fetch.available_files", return_value=available_files_output),
        patch("turbo_turtle._fetch.print_list") as mock_print_list,
        patch("turbo_turtle._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[True, True]),
        patch("filecmp.cmp", return_value=True),
        does_not_raise,
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination)
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with([])

    # Files in destination tree do exist, we want to overwrite contents, and the files differ. Copy the source file.
    with (
        patch("turbo_turtle._fetch.available_files", return_value=available_files_output),
        patch("turbo_turtle._fetch.print_list") as mock_print_list,
        patch("turbo_turtle._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[True, True]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise,
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True)
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do exist, we want to overwrite contents, but the files are the same. Don't copy the
    # source file.
    with (
        patch("turbo_turtle._fetch.available_files", return_value=available_files_output),
        patch("turbo_turtle._fetch.print_list") as mock_print_list,
        patch("turbo_turtle._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[True, True]),
        patch("filecmp.cmp", return_value=True),
        does_not_raise,
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True)
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do exist, but we want to overwrite contents and dry-run.
    # Print the modsim_template file tree.
    with (
        patch("turbo_turtle._fetch.available_files", return_value=available_files_output),
        patch("turbo_turtle._fetch.print_list") as mock_print_list,
        patch("turbo_turtle._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[True, True]),
        patch("filecmp.cmp", return_value=True),
        does_not_raise,
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True, dry_run=True)
        mock_print_list.assert_called_once_with(destination_tree)
        mock_conditional_copy.assert_not_called()

"""
Dataset files managements Python API module.
"""
from typing import Dict, List, Set
import os
import re
import stat
import shutil
import datetime
import uuid

README_FILENAME = "readme.txt"


class UserMistakeException(Exception):
    """ Exception class for user's errors. """


def init_dataset(
        dataset_root_path: str,
        init_version: str = None):
    """
    Init version tracking for a dataset.

    Args:
        dataset_root_path: root path of a dataset directory
        init_version: optional initial dataset version string (for example, `v1.0`)
    
    Returns:
        Dict: Dictionary with statistics on added, removed, updated and linked files
    """
    # check dataset path
    if not os.path.isdir(dataset_root_path):
        raise UserMistakeException("Dataset does not exist in provided path!")

    if not init_version:
        init_version = "v0.1"

    to_move = []
    for filename in os.listdir(dataset_root_path):
        to_move.append(_format_path(filename, os.path.isdir(
            os.path.join(dataset_root_path, filename))))

    temp_dir = uuid.uuid4().hex
    temp_version_path = os.path.join(dataset_root_path, temp_dir)
    os.mkdir(temp_version_path)

    # move all content to new dir
    for filename in to_move:
        shutil.move(
            os.path.join(dataset_root_path, filename),
            os.path.join(temp_version_path, filename))

    # rename dir to version number
    new_version_path = os.path.join(dataset_root_path, init_version)
    shutil.move(temp_version_path, new_version_path)

    results = {
        "added": to_move, 
        "updated": [], 
        "removed": [], 
        "symlinks": [], 
        "version": init_version}
    _make_version_readme(new_version_path, init_version, None, results, None)
    _make_readonly(new_version_path)
    _make_symlink_for_current_version(dataset_root_path, init_version)

    return results


def make_new_dataset_version(
        dataset_root_path: str,
        changes: dict,
        new_version: str = None,
        increase_major: bool = False,
        copy_files: bool = False,
        message: str = None) -> Dict:
    """
    Make new version of dataset by applying changes.

    Args:
        dataset_root_path: Root path of a dataset directory
        changes: Dictinary with list fields "add", "add_all", "update", 
        "update_all", "remove" representing changes need to be applied to a dataset.
        new_version: Optional new version string (for example, `v2.0`)
        increase_major: Increase major version
        copy_files: Copy new files to add or update dataset instead of move
        message: Optional comment for `readme.txt` file

    Returns:
        Dict: Dictionary with statistics on added, removed, updated and linked files
    """
    # check dataset path
    if not os.path.isdir(dataset_root_path):
        raise UserMistakeException("Dataset does not exist in provided path!")

    # get the latest version
    prev_version = _get_versions_list(dataset_root_path)[-1]
    prev_version_path = os.path.join(os.path.abspath(dataset_root_path), prev_version)
    # obtain new version number
    if new_version is None:
        new_version = _gen_next_version_number(prev_version, increase_major=increase_major)
    if not _validate_next_version_number(prev_version, new_version):
        raise UserMistakeException(
            "New version number must be greater then the latest version number!")
    
    # validate changes before applying
    if "add" in changes and changes["add"] is not None:
        for source_path, target_subpath in changes["add"]:
            _validate_add(source_path, target_subpath)
    if "add_all" in changes and changes["add_all"] is not None:
        for source_path, target_subpath in changes["add_all"]:
            _validate_add_all(source_path, target_subpath)
    if "update" in changes and changes["update"] is not None:
        for source_path, target_subpath in changes["update"]:
            _validate_update(source_path, target_subpath, prev_version_path, prev_version)
    if "update_all" in changes and changes["update_all"] is not None:
        for source_path, target_subpath in changes["update_all"]:
            _validate_update_all(
                source_path, 
                target_subpath, 
                prev_version_path,
                prev_version)
    if "remove" in changes and changes["remove"] is not None:
        for source_path in changes["remove"]:
            _validate_remove(source_path, prev_version_path, prev_version)

    # create new version directory
    new_version_path = os.path.join(os.path.abspath(dataset_root_path), new_version)
    os.mkdir(new_version_path)

    results_stat = {
        "added": [], 
        "updated": [], 
        "removed": [], 
        "symlinks": [], 
        "version": new_version}
    # add new files
    if "add" in changes and changes["add"] is not None:
        for source_path, target_subpath in changes["add"]:
            _apply_add(
                source_path, 
                target_subpath, 
                new_version_path, 
                copy_files, 
                results_stat)
    if "add_all" in changes and changes["add_all"] is not None:
        for source_path, target_subpath in changes["add_all"]:
            _apply_add_all(
                source_path, 
                target_subpath, 
                new_version_path, 
                copy_files, 
                results_stat)
    # update files
    if "update" in changes and changes["update"] is not None:
        for source_path, target_subpath in changes["update"]:
            _apply_update(source_path, target_subpath, new_version_path, copy_files, results_stat)
    if "update_all" in changes and changes["update_all"] is not None:
        for source_path, target_subpath in changes["update_all"]:
            _apply_update_all(
                source_path, 
                target_subpath, 
                new_version_path, 
                copy_files, 
                results_stat)
    # create subdirs for removing files
    exclude_links = [os.path.join(prev_version_path, README_FILENAME)]
    if "remove" in changes and changes["remove"] is not None:
        for source_path in changes["remove"]:
            _apply_remove(
                source_path, 
                prev_version_path, 
                new_version_path, 
                exclude_links, 
                results_stat)

    # create symlinks or remove files
    results_stat["symlinks"] = _make_symlinks(prev_version_path, new_version_path, set(exclude_links))

    _make_version_readme(new_version_path, new_version, prev_version, results_stat, message)
    _make_readonly(new_version_path)
    _make_symlink_for_current_version(dataset_root_path, new_version)

    return results_stat


def _validate_add(source_path: str, target_subpath: str):
    _check_source_file_existence(source_path)
    _validate_subpath(target_subpath)


def _validate_add_all(source_path: str, target_subpath: str):
    _check_source_dir_existence(source_path)
    _validate_subpath(target_subpath)


def _validate_update(
        source_path: str, target_subpath: str, prev_version_path: str, prev_version: str):
    _check_source_file_existence(source_path)
    _validate_subpath(target_subpath)
    prev_file_path = os.path.join(
        prev_version_path, target_subpath, source_path.split(os.path.sep)[-1])
    _check_path_existence(prev_file_path, prev_version)


def _validate_update_all(
        source_path: str, target_subpath: str, prev_version_path: str, prev_version: str):
    _check_source_dir_existence(source_path)
    _validate_subpath(target_subpath)
    for entry in list(os.scandir(source_path)):
        prev_file_path = os.path.join(prev_version_path, target_subpath, entry.name)
        _check_path_existence(prev_file_path, prev_version)


def _validate_remove(source_path: str, prev_version_path: str, prev_version: str):
    _validate_subpath(source_path)
    prev_file_path = os.path.join(prev_version_path, source_path)
    _check_path_existence(prev_file_path, prev_version)


def _apply_add(
        source_path: str, 
        target_subpath: str, 
        new_version_path: str, 
        copy_files: bool, 
        results_stat: Dict):
    _add_file_to_subpath(
        new_version_path, os.path.abspath(source_path), target_subpath, copy_files)
    results_stat["added"].append(
        _format_path(os.path.join(
        target_subpath, os.path.split(source_path)[-1]), os.path.isdir(source_path)))
    

def _apply_add_all(
        source_path: str, 
        target_subpath: str, 
        new_version_path: str, 
        copy_files: bool, 
        results_stat: Dict):
    for entry in list(os.scandir(source_path)):
        entry_source_path = os.path.join(os.path.abspath(source_path), entry.name)
        _add_file_to_subpath(
            new_version_path, entry_source_path, target_subpath, copy_files)
        results_stat["added"].append(
            _format_path(
                os.path.join(target_subpath, entry.name),
                os.path.isdir(entry_source_path)))


def _apply_update(
        source_path: str, 
        target_subpath: str, 
        new_version_path: str, 
        copy_files: bool, 
        results_stat: Dict):
    _add_file_to_subpath(new_version_path, source_path, target_subpath, copy_files)
    results_stat["updated"].append(
        _format_path(
            os.path.join(target_subpath, source_path.split(os.path.sep)[-1]),
            os.path.isdir(source_path)))


def _apply_update_all(
        source_path: str, 
        target_subpath: str, 
        new_version_path: str, 
        copy_files: bool, 
        results_stat: Dict):
    for entry in list(os.scandir(source_path)):
        entry_source_path = os.path.join(source_path, entry.name)
        _add_file_to_subpath(
            new_version_path, entry_source_path, target_subpath, copy_files)
        results_stat["updated"].append(
            _format_path(
                os.path.join(target_subpath, entry.name),
                os.path.isdir(entry_source_path)))


def _apply_remove(
        source_path: str, 
        prev_version_path: str, 
        new_version_path: str, 
        exclude_links: List, 
        results_stat: Dict):
    prev_file_path = os.path.join(prev_version_path, source_path)
    os.makedirs(
        os.path.join(new_version_path, *os.path.split(source_path)[:-1]), exist_ok=True)
    results_stat["removed"].append(_format_path(source_path, os.path.isdir(prev_file_path)))
    exclude_links.append(prev_file_path)


def _check_source_file_existence(file_path: str):
    if not os.path.exists(file_path):
        raise UserMistakeException(
            f"File {file_path} doesn't exist")


def _check_source_dir_existence(file_path: str):
    if not os.path.exists(file_path) or not os.path.isdir(file_path):
        raise UserMistakeException(
            f"Directory {file_path} doesn't exist")


def _check_path_existence(file_path: str, prev_version: str):
    if not os.path.exists(file_path):
        raise UserMistakeException(
            f"File {file_path} doesn't exist in previous version {prev_version}")


def _format_path(file_path: str, is_dir: bool):
    if is_dir and file_path[-1] != os.sep:
        return file_path + os.sep
    return file_path


def _validate_subpath(subpath: str):
    if len(subpath) > 0 and subpath[0] in "./\\":
        raise UserMistakeException(
            f"Relative path {subpath} is invalid. Please, "\
                "don't start relative path with '/' or '.'")


def _get_versions_list(dataset_root_path: str):
    return sorted([item.name for item in os.scandir(dataset_root_path) if item.is_dir() and
                   item.name != "current" and item.name != "readme"])


def _add_file_to_subpath(
        root_path: str, 
        source_path: str, 
        target_subpath: str, 
        copy_files: bool=True):
    if target_subpath and len(target_subpath) > 0:
        os.makedirs(os.path.join(root_path, target_subpath), exist_ok=True)
    if os.path.isdir(source_path):
        # recursively add folder
        if copy_files:
            shutil.copytree(source_path, os.path.join(root_path, target_subpath))
        else:
            shutil.move(source_path, os.path.join(root_path, target_subpath))
    else:
        # add file
        if copy_files:
            shutil.copy2(source_path, os.path.join(root_path, target_subpath))
        else:
            shutil.move(source_path, os.path.join(root_path, target_subpath))


def _make_readonly(path: str):
    def chmod_operation(root_path, name):
        os.chmod(
            os.path.join(root_path, name), stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    def chmod_dir_operation(root_path, name):
        os.chmod(
            os.path.join(root_path, name), (stat.S_IREAD | stat.S_IXUSR | stat.S_IRGRP |
                stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH))
    for root, dirs, files in os.walk(path, topdown=False):
        for filename in files:
            chmod_operation(root, filename)
        for filename in dirs:
            chmod_dir_operation(root, filename)
    chmod_dir_operation(path, "")


def _make_symlinks(source_path: str, target_path: str, exclude: Set):
    symlinks = []
    for filename in os.listdir(source_path):
        source_file_path = os.path.join(source_path, filename)
        if source_file_path in exclude:
            continue
        symlink_path = os.path.join(target_path, filename)
        if os.path.exists(symlink_path):
            if os.path.isdir(symlink_path):
                # create symlinks inside directory recursively
                sublinks = _make_symlinks(
                    os.path.join(source_path, filename),
                    symlink_path,
                    exclude)
                symlinks.extend(sublinks)
        else:
            os.symlink(os.path.relpath(source_file_path, start=target_path), symlink_path)
            symlinks.append(symlink_path)
    return symlinks


def _write_stats(stats, key, out):
    if len(stats[key]) > 0:
        out.write(f"Files {key}:\n")
        for filename in stats[key]:
            out.write(filename)
            out.write("\n")
        out.write("\n")


def _make_version_readme(
        new_version_path: str, 
        new_version: str, 
        old_version: str, 
        stats: Dict, 
        message: str):
    with open(os.path.join(new_version_path, README_FILENAME), "w", encoding="utf-8") as out:
        if old_version:
            out.write(f"Dataset version {new_version} has been created from "\
                      f"previous version {old_version}!\n")
        else:
            out.write(f"Dataset version {new_version} has been created!\n")
        if message:
            out.write(message)
            if len(message) >= 1 and message[-1] != '\n':
                out.write("\n")
        out.write(f"Created timestamp: {str(datetime.datetime.now())}, OS user: {os.getlogin()}\n")
        out.write("Files added: %d, updated: %d, removed: %d, symlinked: %d\n\n" % (
            len(stats["added"]),
            len(stats["updated"]),
            len(stats["removed"]),
            len(stats["symlinks"])))
        _write_stats(stats, "added", out)
        _write_stats(stats, "updated", out)
        _write_stats(stats, "removed", out)


def _make_symlink_for_current_version(dataset_root_path: str, new_version: str):
    symlink_path = os.path.join(dataset_root_path, "current")
    if os.path.exists(symlink_path):
        os.unlink(symlink_path)
    os.symlink(os.path.join(".", new_version), symlink_path)


def _increase_version(version: str) -> str:
    return str(list(map(int, re.findall(r'\d+', version)))[-1] + 1)


def _gen_next_version_number(prev_version: str, increase_major: bool=False):
    version_numbers = prev_version.split('.')
    if increase_major:
        version_numbers[0] = _increase_version(version_numbers[0])
    else:
        version_numbers[-1] = _increase_version(version_numbers[-1])
    return '.'.join(version_numbers)


def _validate_next_version_number(prev_version: str, next_version: str):
    return prev_version < next_version

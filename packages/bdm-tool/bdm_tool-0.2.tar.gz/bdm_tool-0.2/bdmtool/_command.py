"""
Command line parsing module of BDM tool.  
"""
import argparse
from .files_management import init_dataset, make_new_dataset_version


class AppendWithSubpathAction(argparse.Action):
    """
    Argparse action for appending to the list with subpath.
    """
    def __call__(self, parser_name, namespace, values, option_string=None):
        current_paths = getattr(namespace, self.dest) or []
        paths = values.split(':', 1)
        value = (paths[0], paths[1]) if len(paths) > 1 else (paths[0], "")
        current_paths.append(value)
        setattr(namespace, self.dest, current_paths)


parser = argparse.ArgumentParser(
    prog='bdm',
    description='Big Datasets version Management tool')
subparsers = parser.add_subparsers(dest='command', title="Commands")

# create the parser for the "init" command
parser_init = subparsers.add_parser('init', help='start versioning a dataset using BDM tool')
parser_init.add_argument('dataset_path', type=str, action='store', help='path to a dataset root')
parser_init.add_argument('-n', '--number', action='store', metavar='dataset_version_number',
                         help='custom number of initial dataset version')

# create the parser for the "b" command
parser_change = subparsers.add_parser('change', help='make a new version of a dataset')
parser_change.add_argument('dataset_path', type=str, action='store',
                           help='path to a dataset root directory')
parser_change.add_argument('-a', '--add', type=str, action=AppendWithSubpathAction,
                           metavar='file_path[:target_subpath]',
                           help='add file from `file_path` to `target_subpath` or ' \
                           'root of a dataset')
parser_change.add_argument('-al', '--add_all', type=str,
                           action=AppendWithSubpathAction, metavar='dir_path[:target_subpath]',
                           help='add all files from `dir_path` to `target_subpath` or ' \
                           'root of a dataset')
parser_change.add_argument('-u', '--update', type=str, action=AppendWithSubpathAction,
                           metavar='file_path[:target_subpath]',
                           help='update file in `target_subpath` or root of a dataset ' \
                           'by file from `file_path`')
parser_change.add_argument('-ua', '--update_all', '-ua', type=str, action=AppendWithSubpathAction,
                           metavar='dir_path[:target_subpath]',
                           help='update files in `target_subpath` or root of a dataset ' \
                           'by all files from `dir_path`')
parser_change.add_argument('-r', '--remove', type=str, action='append', metavar='file_subpath',
                           help='remove file `file_subpath` from a dataset')
parser_change.add_argument('-m', '--message', action='store', metavar='text',
                           help='optional message for new dataset version README file')
parser_change.add_argument('-c', '--copy_files', action='store_true',
                           help='make copy of files instead of moving when update or ' \
                           'add files to dataset ')
parser_change.add_argument('-n', '--number', action='store', metavar='dataset_version_number',
                           help='custom number of new dataset version')
parser_change.add_argument('-im', '--increase_major_version', action='store_true',
                           help='if custom version is not defined increase major number of version')


def print_results(results):
    """
    Print statistics on dataset version changes.
    """
    print(f"Version {results['version']} of dataset has been created.")
    print(f"Files added: {len(results['added'])}, updated: {len(results['updated'])}, " +
          f"removed: {len(results['removed'])}, symlinked: {len(results['symlinks'])}\n\n")


def run_bdm():
    """
    Entry point function for `bdm` command.
    """
    args = parser.parse_args()
    if args.command == 'init':
        results = init_dataset(args.dataset_path, args.number)
        print_results(results)
    elif args.command == "change":
        try:
            results = make_new_dataset_version(
                dataset_root_path=args.dataset_path,
                changes={
                    'add': args.add,
                    'add_all': args.add_all,
                    'update': args.update,
                    'update_all': args.update_all,
                    'remove': args.remove,
                },
                new_version=args.number,
                increase_major=args.increase_major_version,
                copy_files=args.copy_files,
                message=args.message)
            print_results(results)
        except Exception as e:
            print(e)
    else:
        print("Invalid command! Try `bdm --help` to get help.")


if __name__ == "__main__":
    run_bdm()

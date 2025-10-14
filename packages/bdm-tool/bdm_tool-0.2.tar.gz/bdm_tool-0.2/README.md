# BDM Tool
__BDM__ (Big Dataset Management) Tool is a __simple__ lightweight dataset versioning utility based purely on the file system and symbolic links.

BDM Tool Features:
* __No full downloads required__: Switch to any dataset version without downloading the entire dataset to your local machine.
* __Independent of external VCS__: Does not rely on external version control systems like Git or Mercurial, and does not require integrating with one.
* __Easy dataset sharing__: Supports sharing datasets via remote file systems on a data server.
* __Fast version switching__: Switching between dataset versions does not require long synchronization processes.
* __Transparent version access__: Different dataset versions are accessed through simple and intuitive paths (e.g., dataset/v1.0/, dataset/v2.0/, etc.), making versioning fully transparent to configuration files, MLflow parameters, and other tooling.
* __Storage optimization__: Efficiently stores multiple dataset versions using symbolic links to avoid duplication.
* __Designed for large, complex datasets__: Well-suited for managing big datasets with intricate directory and subdirectory structures.
* __Python API for automation__: Provides a simple Python API to automatically create new dataset versions within MLOps pipelines, workflows, ETL jobs, and other automated processes.

## General Principles
* Each version of a dataset is a path like `dataset/v1.0/`, `dataset/v2.0/`.
* A new dataset version is generated whenever modifications are made
* Each dataset version is immutable and read-only.
* A new version includes only the files that have been added or modified, while unchanged files and directories are stored as symbolic links.
* Each version contains a readme.txt file with a summary of changes.

## Intallation
### Installation from PyPI (Recommended)
Use `pip` to install tool by the following command:
```shell
pip install bdm-tool
```

### Installation from Sources
Use `pip` to install tool by the following command:
```shell
pip install git+https://github.com/aikho/bdm-tool.git
```

## Usage
### Start Versioning Dataset
Let's assume we have a dataset with the following structure:
```shell
tree testdata
testdata
├── annotation
│   ├── part01
│   │   ├── regions01.json
│   │   ├── regions02.json
│   │   ├── regions03.json
│   │   ├── regions04.json
│   │   └── regions05.json
│   ├── part02
│   │   ├── regions01.json
│   │   ├── regions02.json
│   │   ├── regions03.json
│   │   ├── regions04.json
│   │   └── regions05.json
│   └── part03
│       ├── regions01.json
│       ├── regions02.json
│       ├── regions03.json
│       ├── regions04.json
│       └── regions05.json
└── data
    ├── part01
    │   ├── image01.png
    │   ├── image02.png
    │   ├── image03.png
    │   ├── image04.png
    │   └── image05.png
    ├── part02
    │   ├── image01.png
    │   ├── image02.png
    │   ├── image03.png
    │   ├── image04.png
    │   └── image05.png
    └── part03
        ├── image01.png
        ├── image02.png
        ├── image03.png
        ├── image04.png
        └── image05.png

9 directories, 30 files
```
To put it under `bdm-tool` version control use command `bdm init`:
```shell
bdm init testdata
Version v0.1 of dataset has been created.
Files added: 3, updated: 0, removed: 0, symlinked: 0
```
The first version `v0.1` of the dataset has been created. Let’s take a look at the file structure: 
```shell
tree testdata
testdata
├── current -> ./v0.1
└── v0.1
    ├── annotation
    │   ├── part01
    │   │   ├── regions01.json
    │   │   ├── regions02.json
    │   │   ├── regions03.json
    │   │   ├── regions04.json
    │   │   └── regions05.json
    │   ├── part02
    │   │   ├── regions01.json
    │   │   ├── regions02.json
    │   │   ├── regions03.json
    │   │   ├── regions04.json
    │   │   └── regions05.json
    │   └── part03
    │       ├── regions01.json
    │       ├── regions02.json
    │       ├── regions03.json
    │       ├── regions04.json
    │       └── regions05.json
    ├── data
    │   ├── part01
    │   │   ├── image01.png
    │   │   ├── image02.png
    │   │   ├── image03.png
    │   │   ├── image04.png
    │   │   └── image05.png
    │   ├── part02
    │   │   ├── image01.png
    │   │   ├── image02.png
    │   │   ├── image03.png
    │   │   ├── image04.png
    │   │   └── image05.png
    │   └── part03
    │       ├── image01.png
    │       ├── image02.png
    │       ├── image03.png
    │       ├── image04.png
    │       └── image05.png
    └── readme.txt

11 directories, 31 files
```
We can see that version `v0.1` contains all the initial files along with a `readme.txt` file. Let’s take a look inside `readme.txt`:
```shell
cat testdata/v0.1/readme.txt 
Dataset version v0.1 has been created!
Created timestamp: 2023-08-07 19:40:19.498656, OS user: rock-star-ml-engineer
Files added: 2, updated: 0, removed: 0, symlinked: 0

Files added:
annotation/
data/
```
The file shows the creation date, operating system user, relevant statistics, and a summary of performed operations.

### Add New Files
Suppose we have additional data stored in the `new_data` directory:
```shell
tree new_data/
new_data/
├── annotation
│   ├── regions06.json
│   └── regions07.json
└── data
    ├── image06.png
    └── image07.png

2 directories, 4 files
```
New files can be added to a new dataset version using the `dbm change` command. Use the `--add` flag to add individual files, or `--add-all` to add all files from a specified directory:
```shell
bdm change --add_all new_data/annotation/:annotation/part03/ --add_all new_data/data/:data/part03/ -c -m "add new files" testdata
Version v0.2 of dataset has been created.
Files added: 4, updated: 0, removed: 0, symlinked: 14
```
The `:` character is used as a separator between the source path and the target subpath inside the dataset where the files should be added.

The `-c` flag stands for copy. When used, files are copied instead of moved. Moving files can be faster, so you may prefer it for performance reasons.

The `-m` flag allows you to add a message, which is then stored in the `readme.txt` file of the new dataset version.

Let’s take a look inside the `readme.txt` file of the new version:
```shell
cat testdata/current/readme.txt 
Dataset version v0.2 has been created from previous version v0.1!
add new files
Created timestamp: 2023-08-07 19:38:39.758828, OS user: rock-star-ml-engineer
Files added: 4, updated: 0, removed: 0, symlinked: 14

Files added:
annotation/part03/regions06.json
annotation/part03/regions07.json
data/part03/image06.png
data/part03/image07.png
```
Next, let’s examine the updated file structure:
```shell
tree testdata
testdata
├── current -> ./v0.2
├── v0.1
│   ├── annotation
│   │   ├── part01
│   │   │   ├── regions01.json
│   │   │   ├── regions02.json
│   │   │   ├── regions03.json
│   │   │   ├── regions04.json
│   │   │   └── regions05.json
│   │   ├── part02
│   │   │   ├── regions01.json
│   │   │   ├── regions02.json
│   │   │   ├── regions03.json
│   │   │   ├── regions04.json
│   │   │   └── regions05.json
│   │   └── part03
│   │       ├── regions01.json
│   │       ├── regions02.json
│   │       ├── regions03.json
│   │       ├── regions04.json
│   │       └── regions05.json
│   ├── data
│   │   ├── part01
│   │   │   ├── image01.png
│   │   │   ├── image02.png
│   │   │   ├── image03.png
│   │   │   ├── image04.png
│   │   │   └── image05.png
│   │   ├── part02
│   │   │   ├── image01.png
│   │   │   ├── image02.png
│   │   │   ├── image03.png
│   │   │   ├── image04.png
│   │   │   └── image05.png
│   │   └── part03
│   │       ├── image01.png
│   │       ├── image02.png
│   │       ├── image03.png
│   │       ├── image04.png
│   │       └── image05.png
│   └── readme.txt
└── v0.2
    ├── annotation
    │   ├── part01 -> ../../v0.1/annotation/part01
    │   ├── part02 -> ../../v0.1/annotation/part02
    │   └── part03
    │       ├── regions01.json -> ../../../v0.1/annotation/part03/regions01.json
    │       ├── regions02.json -> ../../../v0.1/annotation/part03/regions02.json
    │       ├── regions03.json -> ../../../v0.1/annotation/part03/regions03.json
    │       ├── regions04.json -> ../../../v0.1/annotation/part03/regions04.json
    │       ├── regions05.json -> ../../../v0.1/annotation/part03/regions05.json
    │       ├── regions06.json
    │       └── regions07.json
    ├── data
    │   ├── part01 -> ../../v0.1/data/part01
    │   ├── part02 -> ../../v0.1/data/part02
    │   └── part03
    │       ├── image01.png -> ../../../v0.1/data/part03/image01.png
    │       ├── image02.png -> ../../../v0.1/data/part03/image02.png
    │       ├── image03.png -> ../../../v0.1/data/part03/image03.png
    │       ├── image04.png -> ../../../v0.1/data/part03/image04.png
    │       ├── image05.png -> ../../../v0.1/data/part03/image05.png
    │       ├── image06.png
    │       └── image07.png
    └── readme.txt

20 directories, 46 files
```

### Update Files
Files can be updated in a new dataset version using the `dbm change` command. Use the `--update` flag to update individual files, or `--update-all` to update all files in a given directory:
```shell
bdm change --update data_update/regions05.json:annotation/part03/ -c -m "update" testdata
Version v0.3 of dataset has been created.
Files added: 0, updated: 1, removed: 0, symlinked: 9
```
Let’s take a look inside the `readme.txt` file of the new version:
```shell
cat testdata/current/readme.txt 
Dataset version v0.3 has been created from previous version v0.2!
update
Created timestamp: 2023-08-07 19:40:01.753345, OS user: rock-star-data-scientist
Files added: 0, updated: 1, removed: 0, symlinked: 9

Files updated:
annotation/part03/regions05.json
```
Let’s take a look at the file structure:
```shell
tree testdata
testdata
├── current -> ./v0.3
├── v0.1
│   ├── annotation
│   │   ├── part01
│   │   │   ├── regions01.json
│   │   │   ├── regions02.json
│   │   │   ├── regions03.json
│   │   │   ├── regions04.json
│   │   │   └── regions05.json
│   │   ├── part02
│   │   │   ├── regions01.json
│   │   │   ├── regions02.json
│   │   │   ├── regions03.json
│   │   │   ├── regions04.json
│   │   │   └── regions05.json
│   │   └── part03
│   │       ├── regions01.json
│   │       ├── regions02.json
│   │       ├── regions03.json
│   │       ├── regions04.json
│   │       └── regions05.json
│   ├── data
│   │   ├── part01
│   │   │   ├── image01.png
│   │   │   ├── image02.png
│   │   │   ├── image03.png
│   │   │   ├── image04.png
│   │   │   └── image05.png
│   │   ├── part02
│   │   │   ├── image01.png
│   │   │   ├── image02.png
│   │   │   ├── image03.png
│   │   │   ├── image04.png
│   │   │   └── image05.png
│   │   └── part03
│   │       ├── image01.png
│   │       ├── image02.png
│   │       ├── image03.png
│   │       ├── image04.png
│   │       └── image05.png
│   └── readme.txt
├── v0.2
│   ├── annotation
│   │   ├── part01 -> ../../v0.1/annotation/part01
│   │   ├── part02 -> ../../v0.1/annotation/part02
│   │   └── part03
│   │       ├── regions01.json -> ../../../v0.1/annotation/part03/regions01.json
│   │       ├── regions02.json -> ../../../v0.1/annotation/part03/regions02.json
│   │       ├── regions03.json -> ../../../v0.1/annotation/part03/regions03.json
│   │       ├── regions04.json -> ../../../v0.1/annotation/part03/regions04.json
│   │       ├── regions05.json -> ../../../v0.1/annotation/part03/regions05.json
│   │       ├── regions06.json
│   │       └── regions07.json
│   ├── data
│   │   ├── part01 -> ../../v0.1/data/part01
│   │   ├── part02 -> ../../v0.1/data/part02
│   │   └── part03
│   │       ├── image01.png -> ../../../v0.1/data/part03/image01.png
│   │       ├── image02.png -> ../../../v0.1/data/part03/image02.png
│   │       ├── image03.png -> ../../../v0.1/data/part03/image03.png
│   │       ├── image04.png -> ../../../v0.1/data/part03/image04.png
│   │       ├── image05.png -> ../../../v0.1/data/part03/image05.png
│   │       ├── image06.png
│   │       └── image07.png
│   └── readme.txt
└── v0.3
    ├── annotation
    │   ├── part01 -> ../../v0.2/annotation/part01
    │   ├── part02 -> ../../v0.2/annotation/part02
    │   └── part03
    │       ├── regions01.json -> ../../../v0.2/annotation/part03/regions01.json
    │       ├── regions02.json -> ../../../v0.2/annotation/part03/regions02.json
    │       ├── regions03.json -> ../../../v0.2/annotation/part03/regions03.json
    │       ├── regions04.json -> ../../../v0.2/annotation/part03/regions04.json
    │       ├── regions05.json
    │       ├── regions06.json -> ../../../v0.2/annotation/part03/regions06.json
    │       └── regions07.json -> ../../../v0.2/annotation/part03/regions07.json
    ├── data -> ../v0.2/data
    └── readme.txt

26 directories, 54 file
```

### Remove Files
Files or directories can be removed from the dataset using `dbm change` command with key `--remove`:
```shell
bdm change --remove annotation/part01/regions05.json --remove annotation/part01/regions04.json -c -m "remove obsolete data" testdata 
Version v0.4 of dataset has been created.
Files added: 0, updated: 0, removed: 2, symlinked: 8

```
### Combining Operations
Adding, updating, and removing operations can be freely combined within a single dataset version. Use `bdm change -h` command to get detailed information on available keys and options:
```shell
bdm change -h
```

## License
See `LICENSE` file in the repo.



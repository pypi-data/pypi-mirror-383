import os
from pyfakefs.fake_filesystem_unittest import TestCase
from bdmtool.files_management import make_new_dataset_version, init_dataset, UserMistakeException


class InitDatasetVersionTestCase(TestCase):
    """
    Test class for init operation on a new dataset
    """

    def setUp(self):
        self.setUpPyfakefs()
        # create mock dataset
        self.fs.create_file("/test_dataset/aab1/file1.csv", contents="test")
        self.fs.create_file("/test_dataset/aab1/file2.csv", contents="test")
        self.fs.create_file("/test_dataset/aab1/file3.csv", contents="test")
        self.fs.create_file("/test_dataset/abb2/file1.csv", contents="test")
        self.fs.create_file("/test_dataset/abb2/file2.csv", contents="test")
        self.fs.create_file("/test_dataset/abb2/file3.csv", contents="test")
        self.fs.create_file("/test_dataset/acb3/file1.csv", contents="test")
        self.fs.create_file("/test_dataset/acb3/file2.csv", contents="test")
        self.fs.create_file("/test_dataset/acb3/file3.csv", contents="test")
        self.fs.create_file("/test_dataset/acb3/file4.csv", contents="test")
        self.fs.create_file("/test_dataset/acb3/file5.csv", contents="test")
        self.fs.create_file("/test_dataset/acb3/cbf/file1.csv", contents="test")
        self.fs.create_file("/test_dataset/acb3/cbf/file2.csv", contents="test")

    def test_init_dataset(self):
        init_dataset("/test_dataset")

        self.assertTrue(os.path.exists("/test_dataset/v0.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v0.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v0.1/aab1"))
        self.assertTrue(os.path.exists("/test_dataset/v0.1/abb2/file3.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v0.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v0.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v0.1/acb3/cbf/file2.csv"))


class MakeNewDatasetVersionTestCase(TestCase):
    """
    Test case for updates 
    """

    def setUp(self):
        self.setUpPyfakefs()
        # create mock dataset
        self.fs.create_file("/test_dataset/v1.0/readme.txt", contents="test")
        self.fs.create_symlink("/test_dataset/current", "/test_dataset/v1.0")
        self.fs.create_file("/test_dataset/v1.0/aab1/file1.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/aab1/file2.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/aab1/file3.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/abb2/file1.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/abb2/file2.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/abb2/file3.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/acb3/file1.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/acb3/file2.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/acb3/file3.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/acb3/file4.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/acb3/file5.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/acb3/cbf/file1.csv", contents="test")
        self.fs.create_file("/test_dataset/v1.0/acb3/cbf/file2.csv", contents="test")

    def test_add_file_by_move(self):
        self.fs.create_file("/new_data/file11.csv")
        self.fs.create_file("/new_data/file12.csv")

        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "add": [("/new_data/file11.csv", ""), ("/new_data/file12.csv", "")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/file11.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/file12.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1"))
        self.assertTrue(os.path.exists("/test_dataset/v1.0/abb2/file3.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.0/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.0/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.0/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 2)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 3)
        self.assertFalse(os.path.exists("/new_data/file11.csv"))
        self.assertFalse(os.path.exists("/new_data/file12.csv"))

    def test_add_file_by_copy(self):
        self.fs.create_file("/new_data/file11.csv")
        self.fs.create_file("/new_data/file12.csv")

        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "add": [("/new_data/file11.csv", ""), ("/new_data/file12.csv", "")]},
            copy_files=True)

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/file11.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/file12.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file3.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 2)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 3)
        self.assertTrue(os.path.exists("/new_data/file11.csv"))
        self.assertTrue(os.path.exists("/new_data/file12.csv"))

    def test_add_file_to_subpath_by_move(self):
        self.fs.create_file("/new_data/file11.csv")
        self.fs.create_file("/new_data/file12.csv")

        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "add": [("/new_data/file11.csv", "aab1"), ("/new_data/file12.csv", "acb3/")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1/file11.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file12.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file3.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 2)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 10)
        self.assertFalse(os.path.exists("/new_data/file11.csv"))
        self.assertFalse(os.path.exists("/new_data/file12.csv"))

    def test_add_file_to_subpath_from_relative_path(self):
        self.fs.create_file("../new_data/file11.csv")
        self.fs.create_file("../new_data/file12.csv")

        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "add": [("../new_data/file11.csv", "aab1"), ("../new_data/file12.csv", "acb3/")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1/file11.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file12.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file3.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 2)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 10)
        self.assertFalse(os.path.exists("/new_data/file11.csv"))
        self.assertFalse(os.path.exists("/new_data/file12.csv"))

    def test_add_file_to_subpath_using_dataset_relative_path(self):
        os.chdir("/test_dataset")
        self.fs.create_file("../new_data/file11.csv")
        self.fs.create_file("../new_data/file12.csv")

        stats = make_new_dataset_version(
            "./",
            changes={
                "add": [("../new_data/file11.csv", "aab1"), ("../new_data/file12.csv", "acb3/")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1/file11.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file12.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file3.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 2)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 10)
        self.assertFalse(os.path.exists("/new_data/file11.csv"))
        self.assertFalse(os.path.exists("/new_data/file12.csv"))

    def test_add_file_to_incorrect_subpath(self):
        self.fs.create_file("/new_data/file11.csv")
        self.fs.create_file("/new_data/file12.csv")

        def incorrect_subpath():
            make_new_dataset_version(
                "/test_dataset",
                changes={
                    "add": [("/new_data/file11.csv", "/aab1"), ("/new_data/file12.csv", "acb3/")]})
        self.assertRaises(
            UserMistakeException, incorrect_subpath)
        self.assertFalse(os.path.exists("/test_dataset/v1.1"))

    def test_add_incorrect_path_(self):
        self.fs.create_file("/new_data/file11.csv")
        self.fs.create_file("/new_data/file12.csv")

        def incorrect_source_path():
            make_new_dataset_version(
                "/test_dataset",
                changes={
                    "add": [("/new_data/file1111.csv", "/aab1"), ("/new_data/file12.csv", "acb3/")]})
        self.assertRaises(
            UserMistakeException, incorrect_source_path)
        self.assertFalse(os.path.exists("/test_dataset/v1.1"))

    def test_add_all_files_by_move(self):
        self.fs.create_file("/new_data/file11.csv")
        self.fs.create_file("/new_data/file12.csv")

        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "add_all": [("/new_data/", "")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/file11.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/file12.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file3.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 2)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 3)
        self.assertFalse(os.path.exists("/new_data/file11.csv"))
        self.assertFalse(os.path.exists("/new_data/file12.csv"))

    def test_add_all_files_incorrect_path(self):
        self.fs.create_file("/new_data/file11.csv")
        self.fs.create_file("/new_data/file12.csv")

        def incorrect_source_path():
            stats = make_new_dataset_version(
                "/test_dataset",
                changes={
                    "add_all": [("/new_datawdwdwq/", "")]
                })

        self.assertRaises(
            UserMistakeException, incorrect_source_path)

    def test_add_all_files_using_relative_dataset_path(self):
        os.chdir("/test_dataset")
        self.fs.create_file("../new_data/file11.csv")
        self.fs.create_file("../new_data/file12.csv")

        stats = make_new_dataset_version(
            "./",
            changes={
                "add_all": [("../new_data/", "aab1")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1/file11.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1/file12.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/aab1"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file3.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 2)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 5)
        self.assertFalse(os.path.exists("/new_data/file11.csv"))
        self.assertFalse(os.path.exists("/new_data/file12.csv"))

    def test_update_file_in_subpath_by_move(self):
        self.fs.create_file("/new_data/file1.csv", contents="updated")
        self.fs.create_file("/new_data/file2.csv", contents="updated")

        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "update": [("/new_data/file1.csv", "abb2"), ("/new_data/file2.csv", "acb3/")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file1.csv"))
        with open('/test_dataset/v1.1/abb2/file1.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "updated")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file2.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file1.csv"))
        with open('/test_dataset/v1.1/acb3/file1.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "test")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file2.csv"))
        with open('/test_dataset/v1.1/acb3/file2.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "updated")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 0)
        self.assertEqual(len(stats["updated"]), 2)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 8)
        self.assertFalse(os.path.exists("/new_data/file1.csv"))
        self.assertFalse(os.path.exists("/new_data/file2.csv"))

    def test_update_file_in_subpath_using_dataset_relative_path(self):
        os.chdir("/test_dataset")
        self.fs.create_file("../new_data/file1.csv", contents="updated")
        self.fs.create_file("../new_data/file2.csv", contents="updated")

        stats = make_new_dataset_version(
            "./",
            changes={
                "update": [("../new_data/file1.csv", "abb2"), ("../new_data/file2.csv", "acb3/")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file1.csv"))
        with open('/test_dataset/v1.1/abb2/file1.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "updated")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file2.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file1.csv"))
        with open('/test_dataset/v1.1/acb3/file1.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "test")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file2.csv"))
        with open('/test_dataset/v1.1/acb3/file2.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "updated")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 0)
        self.assertEqual(len(stats["updated"]), 2)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 8)
        self.assertFalse(os.path.exists("/new_data/file1.csv"))
        self.assertFalse(os.path.exists("/new_data/file2.csv"))

    def test_update_file_in_subpath_by_copy(self):
        self.fs.create_file("/new_data/file1.csv", contents="updated")
        self.fs.create_file("/new_data/file2.csv", contents="updated")

        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "update": [("/new_data/file1.csv", "abb2"), ("/new_data/file2.csv", "acb3/")]
            },
            copy_files=True)

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file1.csv"))
        with open('/test_dataset/v1.1/abb2/file1.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "updated")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file2.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file1.csv"))
        with open('/test_dataset/v1.1/acb3/file1.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "test")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file2.csv"))
        with open('/test_dataset/v1.1/acb3/file2.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "updated")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 0)
        self.assertEqual(len(stats["updated"]), 2)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 8)
        self.assertTrue(os.path.exists("/new_data/file1.csv"))
        self.assertTrue(os.path.exists("/new_data/file2.csv"))

    def test_update_all_files_in_subpath_by_move(self):
        self.fs.create_file("/new_data/file1.csv", contents="updated")
        self.fs.create_file("/new_data/file2.csv", contents="updated")

        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "update_all": [("/new_data/", "abb2/")]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file1.csv"))
        with open('/test_dataset/v1.1/abb2/file1.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "updated")
        with open('/test_dataset/v1.1/abb2/file2.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "updated")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file2.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file1.csv"))
        with open('/test_dataset/v1.1/acb3/file1.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "test")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file2.csv"))
        with open('/test_dataset/v1.1/acb3/file2.csv', 'r') as content_file:
            content = content_file.read()
            self.assertEqual(content, "test")
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 0)
        self.assertEqual(len(stats["updated"]), 2)
        self.assertEqual(len(stats["removed"]), 0)
        self.assertEqual(len(stats["symlinks"]), 3)
        self.assertFalse(os.path.exists("/new_data/file1.csv"))
        self.assertFalse(os.path.exists("/new_data/file2.csv"))

    def test_update_all_files_incorrect_path(self):
        self.fs.create_file("/new_data/file1.csv", contents="updated")
        self.fs.create_file("/new_data/file2.csv", contents="updated")

        def incorrect_source_path():
            stats = make_new_dataset_version(
                "/test_dataset",
                changes={
                    "update_all": [("/new_datawewfwefwf/", "abb2/")]
                })

        self.assertRaises(
            UserMistakeException, incorrect_source_path)
        self.assertFalse(os.path.exists("/test_dataset/v1.1"))

    def test_remove_files(self):
        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "remove": ["abb2/file2.csv", "acb3/file4.csv", "acb3/cbf/file2.csv"]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file1.csv"))
        self.assertFalse(os.path.exists("/test_dataset/v1.1/abb2/file2.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/file2.csv"))
        self.assertFalse(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertFalse(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 0)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 3)
        self.assertEqual(len(stats["symlinks"]), 8)

    def test_remove_dir(self):
        stats = make_new_dataset_version(
            "/test_dataset",
            changes={
                "remove": ["acb3"]
            })

        self.assertTrue(os.path.exists("/test_dataset/v1.1"))
        self.assertTrue(os.path.exists("/test_dataset/current"))
        self.assertTrue(os.path.isdir("/test_dataset/current"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/readme.txt"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file1.csv"))
        self.assertTrue(os.path.exists("/test_dataset/v1.1/abb2/file2.csv"))
        self.assertFalse(os.path.exists("/test_dataset/v1.1/acb3/file1.csv"))
        self.assertFalse(os.path.exists("/test_dataset/v1.1/acb3/file2.csv"))
        self.assertFalse(os.path.exists("/test_dataset/v1.1/acb3/file4.csv"))
        self.assertFalse(os.path.exists("/test_dataset/v1.1/acb3/cbf/file1.csv"))
        self.assertFalse(os.path.exists("/test_dataset/v1.1/acb3/cbf/file2.csv"))
        self.assertEqual(len(stats["added"]), 0)
        self.assertEqual(len(stats["updated"]), 0)
        self.assertEqual(len(stats["removed"]), 1)
        self.assertEqual(len(stats["symlinks"]), 2)

    def test_remove_files_incorrect_path(self):
        def incorrect_path():
            stats = make_new_dataset_version(
                "/test_dataset",
                changes={
                    "remove": ["abb2/file2.csv", "acb3/file44545csv", "acb3/cbf/file2.csv"]
                })

        self.assertRaises(
            UserMistakeException, incorrect_path)
        self.assertFalse(os.path.exists("/test_dataset/v1.1"))

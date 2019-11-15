from convertool.utils import get_files


class TestGetFiles:
    def test_with_file(self, list_file):
        result = get_files(list_file)
        assert len(result) == 2

    def test_with_dir(self, data_dir):
        result = get_files(data_dir)
        assert len(result) == 2

    def test_with_nothing(self):
        result = get_files("nothing_here")
        assert len(result) == 0

from unittest.mock import MagicMock, patch


def test_save_header(tmpdir, mocker):
    import yaml

    from csvy.writers import write_header

    dumper = mocker.spy(yaml, "safe_dump")
    header = {"Name": "Ada Lovelace", "Country of origin": "UK"}

    filename = tmpdir / "some_file.cvsy"
    write_header(filename, header)
    dumper.assert_called_with(header, sort_keys=False)

    with filename.open("r") as f:
        lines = [line.strip() for line in f.readlines()]

    assert len(lines) == 4
    assert lines[0] == "---"
    assert lines[-1] == "---"
    for i, (k, v) in enumerate(header.items()):
        assert k in lines[i + 1]
        assert v in lines[i + 1]

    write_header(filename, header, comment="#", sort_keys=True)
    dumper.assert_called_with(header, sort_keys=True)

    with filename.open("r") as f:
        lines = [line.strip() for line in f.readlines()]
    print(lines)
    assert len(lines) == 4
    assert all([line.startswith("#") for line in lines])
    assert lines[0] == "#---"
    assert lines[-1] == "#---"
    for i, (k, v) in enumerate(sorted(header.items())):
        assert k in lines[i + 1]
        assert v in lines[i + 1]


@patch("numpy.savetxt")
def test_write_numpy(mock_save, tmpdir):
    import numpy as np

    from csvy.writers import write_numpy

    filename = tmpdir / "some_file.csv"

    data = []
    assert not write_numpy(filename, data)

    data = np.array([])
    assert write_numpy(filename, data)
    mock_save.assert_called_once()


@patch("pandas.DataFrame.to_csv")
def test_write_pandas(mock_save, tmpdir):
    import pandas as pd

    from csvy.writers import write_pandas

    filename = tmpdir / "some_file.csv"

    data = []
    assert not write_pandas(filename, data)

    data = pd.DataFrame()
    assert write_pandas(filename, data)
    mock_save.assert_called_once()


@patch("csv.writer")
def test_write_csv(mock_save, tmpdir):
    from csvy.writers import write_csv

    class Writer:
        writerow = MagicMock()

    mock_save.return_value = Writer
    filename = tmpdir / "some_file.csv"

    data = [[1, 2], [3, 4]]
    assert write_csv(filename, data)

    mock_save.assert_called_once()
    assert Writer.writerow.call_count == len(data)

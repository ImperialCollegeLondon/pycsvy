import pytest


def test_get_comment():
    from csvy.readers import get_comment

    assert "" == get_comment("--- Something else")
    assert "# " == get_comment("# ---")
    assert "# " == get_comment("# @@", marker="@@")

    with pytest.raises(ValueError):
        get_comment("Wrong marker")


def test_get_header(data_path, data_comment_path):
    from csvy.readers import read_header

    header, nlines, comment = read_header(data_path)
    assert isinstance(header, dict)
    assert "freq" in header.keys()
    assert nlines == 18
    assert comment == ""

    header2, nlines, comment = read_header(data_comment_path)
    assert isinstance(header2, dict)
    assert "freq" in header.keys()
    assert nlines == 18
    assert comment == "# "

    assert header == header2


def test_read_to_array(array_data_path):
    import numpy as np

    from csvy.readers import read_to_array

    data, header = read_to_array(array_data_path, csv_options={"delimiter": ","})
    assert isinstance(data, np.ndarray)
    assert data.shape[1] == 4
    assert isinstance(header, dict)
    assert len(header) > 0

    import csvy.readers as readers

    readers.NDArray = NotImplemented

    with pytest.raises(ModuleNotFoundError):
        read_to_array(array_data_path)


def test_read_to_dataframe(data_path):
    import pandas as pd

    from csvy.readers import read_to_dataframe

    data, header = read_to_dataframe(data_path)
    assert isinstance(data, pd.DataFrame)
    assert tuple(data.columns) == ("Date", "WTI")
    assert isinstance(header, dict)
    assert len(header) > 0

    import csvy.readers as readers

    readers.DataFrame = NotImplemented

    with pytest.raises(ModuleNotFoundError):
        read_to_dataframe(data_path)

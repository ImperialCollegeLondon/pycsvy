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

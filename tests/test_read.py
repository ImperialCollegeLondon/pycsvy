def test_get_header(data_path, data_comment_path):
    from csvy.readers import read_header

    header, nlines = read_header(data_path)
    assert isinstance(header, dict)
    assert "freq" in header.keys()
    assert nlines == 18

    header2, nlines = read_header(data_comment_path, "# ")
    assert isinstance(header2, dict)
    assert "freq" in header.keys()
    assert nlines == 18

    assert header == header2

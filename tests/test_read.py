def test_get_header(data_path, data_comment_path):
    from csvy.readers import load_header

    header = load_header(data_path)
    assert isinstance(header, dict)
    assert len(header) == 16

    header2 = load_header(data_comment_path, "#")
    assert isinstance(header2, dict)
    assert len(header2) == 16

    assert header == header2

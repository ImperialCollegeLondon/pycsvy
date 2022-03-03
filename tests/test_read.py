def test_get_header(data_path, data_comment_path):
    from csvy.read import get_header

    header = get_header(data_path)
    assert isinstance(header, dict)
    assert len(header) == 16

    header2 = get_header(data_comment_path)
    assert isinstance(header2, dict)
    assert len(header2) == 16

    assert header == header2

def test_save_header(tmpdir):
    from pycsvy.writers import write_header

    header = {"Name": "Ada Lovelace", "Country of origin": "UK"}

    filename = tmpdir / "some_file.cvsy"
    write_header(filename, header)

    with filename.open("r") as f:
        lines = [line.strip() for line in f.readlines()]

    assert len(lines) == 4
    assert lines[0] == "---"
    assert lines[-1] == "---"
    for i, (k, v) in enumerate(sorted(header.items())):
        assert k in lines[i + 1]
        assert v in lines[i + 1]

    write_header(filename, header, comment="#")

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

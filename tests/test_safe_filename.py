from papyr.util.fs import safe_filename


def test_safe_filename():
    name = safe_filename("A Study: On/Files?", "10.1/abc")
    assert name.endswith(".pdf")
    assert " " not in name
    assert "/" not in name

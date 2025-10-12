from breadcrumb.storage.value_truncation import truncate_dict, truncate_value, MAX_VALUE_SIZE


def test_truncate_value_respects_default_limit():
    long_string = "X" * (MAX_VALUE_SIZE + 100)
    result = truncate_value(long_string)
    assert "[TRUNCATED" in result
    assert len(result) <= MAX_VALUE_SIZE + 50  # Truncation indicator appended


def test_truncate_dict_recursive():
    data = {
        "outer": {
            "inner": "Y" * (MAX_VALUE_SIZE + 200)
        }
    }
    truncated = truncate_dict(data)
    assert "[TRUNCATED" in truncated["outer"]["inner"]

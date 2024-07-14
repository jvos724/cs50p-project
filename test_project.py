import project as p


# test parse_args() for standard uses of hashtags
def test_parse_tags_hashtags():
    assert p.parse_tags("#one #two #three") == ["one", "two", "three"]
    assert p.parse_tags("#one#two#three") == ["one", "two", "three"]


# test parse_tags() for use of commas
def test_parse_tags_commas():
    assert p.parse_tags("one, two, three") == ["one", "two", "three"]
    assert p.parse_tags("one,two,three") == ["one", "two", "three"]


# test parse_tags() for only spaces
def test_parse_tags_spaces():
    assert p.parse_tags("one two three") == ["one", "two", "three"]


# test parse_tags() for handling excess delimiters
def test_parse_tags_extra_delimiters():
    assert p.parse_tags("##one,   ,#two,, three") == ["one", "two", "three"]

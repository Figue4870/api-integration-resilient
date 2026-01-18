from fixed.pagination import parse_link_header

def test_parse_link_header_next_last():
    link = '<https://api.github.com/resource?page=2>; rel="next", <https://api.github.com/resource?page=5>; rel="last"'
    parsed = parse_link_header(link)
    assert parsed["next"].endswith("page=2")
    assert parsed["last"].endswith("page=5")

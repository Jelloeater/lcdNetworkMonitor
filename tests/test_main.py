import libs

def test_ping_server():
    # Test with a known IP address that should respond
    response = libs.ping_server("8.8.8.8")
    assert isinstance(response, str)

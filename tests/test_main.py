import utils


def test_get_ping():
    # Test with a known IP address that should respond
    response = utils.get_ping("8.8.8.8")
    response = int(response)  # Convert to int to ensure it's a number
    assert response > 0, "Ping should return a positive integer for a reachable IP address"

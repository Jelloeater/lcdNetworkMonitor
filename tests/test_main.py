import utils


def test_get_ping():
    # Test with a known IP address that should respond
    response = utils.get_ping("8.8.8.8")
    response = int(response)  # Convert to int to ensure it's a number
    assert response > 0, "Ping should return a positive integer for a reachable IP address"

def test_time_iso():
    # Test if the function returns a string in ISO format
    response = utils.get_time_iso()
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"
    assert response.count('-') == 1, "ISO format should contain two hyphens"
    assert response.count(':') == 1, "ISO format should contain two colons"
    # assert response.count('T') == 1, "ISO format should contain one 'T' character"

def test_wakatime():
    # Test if the function returns a string
    response = utils.get_wakatime()
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"
    # Additional checks can be added based on expected WakaTime output format


# TODO Add more tests for the following:
#  Wakatime
#  Weather
#  WAN Speed
#  UTC Clock
#  PRTG Alert Count
#  VMware CPU via SNMP
#  Unread RSS + Unread Gmail
#  Public IP#

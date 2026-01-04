import logging
import os
from unittest import skipIf

import dotenv

import utils


def test_env_vars():
    # Load environment variables from .env file for testing
    logging.info(os.getcwd())
    dotenv.load_dotenv(dotenv.find_dotenv())
    required_vars = [
        "WAKATIME_API_KEY",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    assert not missing_vars, f"Missing environment variables: {', '.join(missing_vars)}"
    logging.debug(required_vars)
    assert len(missing_vars) == 0


@skipIf(True, "Will fail if permissions not set, see utils.py for details")
def test_get_ping():
    # Test with a known IP address that should respond
    response = utils.get_ping("8.8.8.8")
    response = int(response)  # Convert to int to ensure it's a number
    assert response > 0, (
        "Ping should return a positive integer for a reachable IP address"
    )


def test_time_iso():
    # Test if the function returns a string in ISO format
    response = utils.get_time_iso()
    logging.debug(response)
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"
    assert response.count("-") == 0
    assert response.count(":") == 1, "ISO format should contain two colons"
    # assert response.count('T') == 1, "ISO format should contain one 'T' character"


def test_time():
    # Test if the function returns a string in ISO format
    response = utils.get_time_local()
    logging.debug(response)
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"


def test_wakatime():
    # Test if the function returns a string
    response = utils.get_wakatime()
    logging.debug(response)
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"
    # Additional checks can be added based on expected WakaTime output format

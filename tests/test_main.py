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
        "PRTG_API_TOKEN",
        "WAKATIME_API_KEY",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    assert not missing_vars, f"Missing environment variables: {', '.join(missing_vars)}"
    logging.debug(required_vars)
    assert required_vars['PRTG_API_TOKEN'] is not None

@skipIf(True, "Will fail if permissions not set, see utils.py for details")
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

def test_weather():
    # Test if the function returns a string
    response = utils.get_weather()
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"
    # Additional checks can be added based on expected weather output format

def test_get_public_ip():
    # Test if the function returns a valid public IP address
    response = utils.get_public_ip()
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"
    assert response.count('.') == 3, "Public IP should contain three dots"
    # Additional checks can be added to validate the format of the IP address

# @skipIf(True, "WIP")
def test_get_prtg_sensor_info():
    # Test if the function returns a dictionary with expected keys
    stat = utils.get_prtg_sensor(sensor_id=(os.getenv("PRTG_WAN_SENSOR_ID"))) #2=Primary Channel
    assert stat is not None #"Response should not be None"


def test_get_prtg_sensor_data_last():
    # Test if the function returns a valid value for the last data point
    stat = utils.get_prtg_sensor_data_value_last(sensor_id=(os.getenv("PRTG_WAN_SENSOR_ID")), channel_id=int((os.getenv("PRTG_WAN_SENSOR_CHANNEL"))),field_name=(os.getenv("PRTG_WAN_SENSOR_FIELD"))) #2=Primary Channel
    assert stat is not None #"Response should not be None"
    assert isinstance(stat, float), "Value should be a number"



# TODO Add more tests for the following:
#  VMware CPU via SNMP
#  PRTG Alert Count
#  Unread RSS + Unread Gmail

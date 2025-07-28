from aiohttp import ClientSession
from .exceptions import InsnrgPoolError
import logging
_LOGGER = logging.getLogger(__name__)
LOGIN_URL = 'https://4rsb9rvte4.execute-api.us-east-2.amazonaws.com/prod/api/login'
CMD_URL = 'https://4rsb9rvte4.execute-api.us-east-2.amazonaws.com/prod/api/cmd'
class InsnrgPool:
    """Main Interface to the Insnrg Pool Device"""
    def __init__(self, session: ClientSession, userName, password):
        self._url_login = LOGIN_URL
        self._userName = userName
        self._password = password
        self._session = session

    async def test_insnrg_pool_credentials(self):
        """Function tests the credentials against the Insnrg Pool Servers"""
        LOGIN_DATA = {
            "userName": self._userName,
            "password": self._password,
        }
        """Login to the system."""
        resp = await self._session.post(self._url_login, json=LOGIN_DATA)
        if resp.status == 200:
            data = await resp.json(content_type=None)
            if data["auth"]["idToken"] is None:
                return False
            else:
                if len(data["devices"]) > 0: #serial = systemId
                    return data["devices"][0]["serial"]
                return "DEMO"
        else:
            return False
    async def get_insnrg_pool_data(self):
        """Function gets all the data for this user account from the Insnrg Pool api"""
        LOGIN_DATA = {
            "userName": self._userName,
            "password": self._password,
        }
        """Login to the system."""
        resp = await self._session.post(self._url_login, json=LOGIN_DATA)
        if resp.status == 200:
            data = await resp.json(content_type=None)
            URL_DATA = CMD_URL
            body = {
                "cmd": "getall",
                "userId": data['user']['userId']
                }
            head = {'Authorization': data["auth"]["idToken"]}
            resp = await self._session.post(URL_DATA, headers=head, json=body)
            result_dict = {}
            if resp.status == 200:
                discoverData = await resp.json(content_type=None)
                _LOGGER.debug(f"getall API response data: {discoverData}")

                for item in discoverData:
                    device_id = item['deviceId']
                    status = item['properties']
                    result_dict[device_id] = {
                                'name': item['name'],
                                'deviceId': item['deviceId'],
                                'type': item['type'][0],
                                'switchStatus': next((prop['value'] for prop in status if prop['namespace'] == 'Alexa.PowerController'), ''),
                                'toggleStatus': next((prop['value'] for prop in status if prop['namespace'] == 'Alexa.ToggleController'), ''),
                                'thermostatStatus': next((prop['value'] for prop in status if prop['namespace'] == 'Alexa.ThermostatController'), {}),
                                'temperatureSensorStatus': next((prop['value'] for prop in status if prop['namespace'] == 'Alexa.TemperatureSensor'), {}),
                                'modeValue': next((prop['value'] for prop in status if prop['namespace'] == 'Alexa.ModeController'), ''),
                            }
                    if item['type'][0] == "LIGHT":
                        result_dict["LIGHT_MODE"] = {
                            'name': "Light Modes",
                            'deviceId': "LIGHT_MODE",
                            'supportCmd': item['deviceId'],
                            'modeValue': next((prop['value'] for prop in status if prop['namespace'] == 'Alexa.ModeController'), ''),
                            "modeList" : item['options']
                            }
                    if "options" in item:
                        result_dict[device_id]["modeList"] = item['options']
                results = result_dict
                _LOGGER.debug(f"Parsed result_dict: {results}")
            else:
                raise InsnrgPoolError(resp.status,"Server error.")
        else:
            raise InsnrgPoolError(resp.status,"Login failed.")
        return results
    async def turn_the_switch(self, mode, deviceId):
        LOGIN_DATA = {
            "userName": self._userName,
            "password": self._password,
        }
        try:
            """Login to the system."""
            resp = await self._session.post(self._url_login, json=LOGIN_DATA)
            if resp.status == 200:
                data = await resp.json(content_type=None)
                URL_DATA = CMD_URL
                mode_to_cmdType = {
                    "ON": "TurnOn",
                    "OFF": "TurnOff",
                    "TIMER": "TimerOn"
                }
                body = {
                    "cmd": "setDeviceStatus",
                    "cmdType": mode_to_cmdType[mode],
                    "deviceId": deviceId,
                    "userId": data['user']['userId']
                    }
                head = {'Authorization': 'Bearer {}'.format(data["auth"]["idToken"])}
                set_state_resp = await self._session.post(URL_DATA, headers=head, json=body)
                if set_state_resp.status == 200:
                    return True
                else: 
                    raise InsnrgPoolError(set_state_resp.status, "Failed to turn the switch")
        except Exception as e:
            _LOGGER.error(f"Error turning the switch: {str(e)}")
            return False

    async def set_thermostat_temp(self, temp_value, deviceId):
        LOGIN_DATA = {
            "userName": self._userName,
            "password": self._password,
        }
        try:
            """Login to the system."""
            resp = await self._session.post(self._url_login, json=LOGIN_DATA)
            if resp.status == 200:
                data = await resp.json(content_type=None)
                URL_DATA = CMD_URL
                body = {
                    "cmd": "setTemperature",
                    "tempValue": temp_value,
                    "deviceId": deviceId,
                    "userId": data['user']['userId']
                    }
                head = {'Authorization': 'Bearer {}'.format(data["auth"]["idToken"])}
                set_state_resp = await self._session.post(URL_DATA, headers=head, json=body)
                if set_state_resp.status == 200:
                    return True
                else: 
                    raise InsnrgPoolError(set_state_resp.status, "Failed to turn the switch")
        except Exception as e:
            _LOGGER.error(f"Error set temperature: {str(e)}")
            return False
    
    async def set_chemistry(self, chem_value, deviceId):
        LOGIN_DATA = {
            "userName": self._userName,
            "password": self._password,
        }
        try:
            """Login to the system."""
            resp = await self._session.post(self._url_login, json=LOGIN_DATA)
            if resp.status == 200:
                data = await resp.json(content_type=None)
                URL_DATA = CMD_URL
                body = {
                    "cmd": "setChemistry",
                    "chemValue": chem_value,
                    "deviceId": deviceId,
                    "userId": data['user']['userId']
                    }
                head = {'Authorization': 'Bearer {}'.format(data["auth"]["idToken"])}
                set_state_resp = await self._session.post(URL_DATA, headers=head, json=body)
                if set_state_resp.status == 200:
                    return True
                else: 
                    raise InsnrgPoolError(set_state_resp.status, "Failed to turn the switch")
        except Exception as e:
            _LOGGER.error(f"Error turning on the switch: {str(e)}")
            return False
    async def change_light_mode(self, mode, deviceId):
        LOGIN_DATA = {
            "userName": self._userName,
            "password": self._password,
        }
        try:
            """Login to the system."""
            resp = await self._session.post(self._url_login, json=LOGIN_DATA)
            if resp.status == 200:
                data = await resp.json(content_type=None)
                URL_DATA = CMD_URL
                body = {
                    "cmd": "setLightMode",
                    "lightValue": mode,
                    "deviceId": deviceId,
                    "userId": data['user']['userId']
                    }
                head = {'Authorization': 'Bearer {}'.format(data["auth"]["idToken"])}
                set_state_resp = await self._session.post(URL_DATA, headers=head, json=body)
                if set_state_resp.status == 200:
                    return True
                else: 
                    raise InsnrgPoolError(set_state_resp.status, "Failed to turn the switch")
        except Exception as e:
            _LOGGER.error(f"Error turning the switch: {str(e)}")
            return False

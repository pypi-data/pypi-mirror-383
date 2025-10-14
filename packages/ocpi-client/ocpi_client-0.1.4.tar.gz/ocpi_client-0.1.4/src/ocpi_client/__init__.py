from base64 import b64encode
from logging import Logger, getLogger
from uuid import uuid4

import httpx
from ocpi_pydantic.v221.base import OcpiBaseResponse
from ocpi_pydantic.v221.enum import OcpiStatusCodeEnum, OcpiModuleIdEnum, OcpiVersionNumberEnum, OcpiInterfaceRoleEnum
from ocpi_pydantic.v221.cdrs import OcpiCdr, OcpiCdrResponse
from ocpi_pydantic.v221.commands import OcpiCommandResult, OcpiReserveNow, OcpiStartSession, OcpiStopSession, OcpiUnlockConnector, OcpiCommandResponseResponse, OcpiCommandResponse
from ocpi_pydantic.v221.credentials import OcpiCredentials, OcpiCredentialsResponse
from ocpi_pydantic.v221.locations.connector import OcpiConnectorResponse
from ocpi_pydantic.v221.locations.evse import OcpiEvse, OcpiEvseResponse
from ocpi_pydantic.v221.locations.location import OcpiLocation, OcpiLocationResponse
from ocpi_pydantic.v221.sessions import OcpiSession, OcpiSessionResponse, OcpiChargingPreferencesResponse
from ocpi_pydantic.v221.tokens import OcpiToken, OcpiLocationReferences, OcpiAuthorizationInfoResponse, OcpiTokenListResponse
from ocpi_pydantic.v221.tariffs import OcpiTariff, OcpiTariffResponse
from ocpi_pydantic.v221.versions import OcpiVersionsResponse, OcpiVersionDetailsResponse
from pydantic import ValidationError

from ocpi_client.models import OcpiParty, OcpiSessionUpdate



class OcpiClient:
    '''
    方法的命名原則 <http_action>_<ocpi_module>
    '''
    def __init__(self, httpx_async_client: httpx.AsyncClient, from_country_code: str, from_party_id: str, to_party: OcpiParty, logger: Logger = getLogger(__name__)):
        if len(from_country_code) != 2: raise ValueError('from_country_code must be ISO 3166-1 alpha-2 format')
        if len(from_party_id) != 3: raise ValueError('from_party_id must be 3 characters')

        self.client = httpx_async_client
        self.from_country_code = from_country_code.upper()
        self.from_party_id = from_party_id.upper()
        self.party = to_party
        self.logger = logger
        self.client.event_hooks = {'request': [self._log_request], 'response': [self._log_response]}


    async def _log_request(self, request: httpx.Request):
        self.logger.info({
            'request_method': request.method,
            'request_url': request.url,
            'request_headers': request.headers,
            'request_content': request.content.decode(),
        })


    async def _log_response(self, response: httpx.Response):
        message = {
            'response_url': response.url,
            'response_status_code': response.status_code,
            'response_headers': response.headers,
            'response_content': (await response.aread()).decode()}
        if response.is_success: self.logger.info(message)
        else: self.logger.error(message)


    async def get_versions(self):
        if not self.party.versions_url:
            raise ValueError({
                'title': 'Party versions URL not available',
                'instance': {'country_code': self.party.country_code, 'party_id': self.party.party_id},
            })
        try:
            auth_token = self.party.credentials_token_for_sending_request_to_party or self.party.credentials_token_for_sending_register_to_party
            versions_response = await self.client.get(
                str(self.party.versions_url),
                headers={
                    'Authorization': f'Token {b64encode(str(auth_token).encode()).decode()}',
                    'OCPI-from-country-code': self.from_country_code,
                    'OCPI-from-party-id': self.from_party_id,
                    'OCPI-to-country-code': self.party.country_code,
                    'OCPI-to-party-id': self.party.party_id,
                    'X-Request-ID': str(uuid4()),
                    'X-Correlation-ID': str(uuid4()),
                },
            )
        except httpx.ConnectError as connect_error:
            self.logger.warning({
                'title': 'HTTP connect error on sending register token to a party',
                'detail': connect_error,
                'instance': {'country_code': self.party.country_code, 'party_id': self.party.party_id, 'versions_url': self.party.versions_url},
            })
            raise connect_error
        except httpx.ConnectTimeout as timeout:
            self.logger.warning({
                'title': 'HTTP timeout error on sending register token to a party',
                'detail': timeout,
                'instance': {'country_code': self.party.country_code, 'party_id': self.party.party_id, 'versions_url': self.party.versions_url},
            })
            raise timeout
        try: versions_response.raise_for_status()
        except httpx.HTTPStatusError as http_error: raise http_error
        party_ocpi_versions_response = OcpiVersionsResponse.model_validate(versions_response.json())
        return party_ocpi_versions_response.data


    async def get_version_details(self, version: OcpiVersionNumberEnum):
        party_version_list = await self.get_versions()
        try: party_version = next(v for v in party_version_list if v.version == version)
        except StopIteration as stop_iteration:
            self.logger.warning({
                'tilte': 'Remote party does not support specified OCPI version',
                'instance': {'remote_party_versions': party_version_list},
            })
            raise ValueError('Remote party does not support specified OCPI version') from stop_iteration
        
        auth_token = self.party.credentials_token_for_sending_request_to_party or self.party.credentials_token_for_sending_register_to_party
        version_details_response = await self.client.get(
            str(party_version.url),
            headers={
                'Authorization': f'Token {b64encode(str(auth_token).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        version_details_response.raise_for_status()
        party_version_details_response = OcpiVersionDetailsResponse.model_validate(version_details_response.json())
        return party_version_details_response.data.endpoints


    async def post_credentials(self, version: OcpiVersionNumberEnum, our_credentials: OcpiCredentials):
        if version != OcpiVersionNumberEnum.v221: raise ValueError('Only OCPI version 2.2.1 is supported')
        if not self.party.v221_endpoints: raise ValueError('Party OCPI V2.2.1 endpoints not available')
        try:
            credentials_endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.credentials and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        except StopIteration as stop_iteration:
            self.logger.error({'title': 'Remote party does not have credentials endpoint', 'instance': {'remote_party_endpoints': self.party.v221_endpoints}})
            raise ValueError('Remote party does not have credentials endpoint') from stop_iteration
        response = await self.client.post(
            str(credentials_endpoint.url),
            json=our_credentials.model_dump(mode='json'),
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_register_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        try:
            party_credentials_response = OcpiCredentialsResponse.model_validate(response.json())
            return party_credentials_response.data
        except ValidationError as e: raise e


    async def put_credentials(self, version: OcpiVersionNumberEnum, new_credentials: OcpiCredentials):
        '''Provides the server with an updated credentials object to access the client’s system.'''
        if version != OcpiVersionNumberEnum.v221: raise ValueError('Only OCPI version 2.2.1 is supported')
        if not self.party.v221_endpoints: raise ValueError('Party OCPI V2.2.1 endpoints not available')
        try:
            credentials_endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.credentials and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        except StopIteration as stop_iteration:
            self.logger.error({'title': 'Remote party does not have credentials endpoint', 'instance': {'remote_party_endpoints': self.party.v221_endpoints}})
            raise ValueError('Remote party does not have credentials endpoint') from stop_iteration
        response = await self.client.put(
            str(credentials_endpoint.url),
            json=new_credentials.model_dump(mode='json'), # Body 應該帶上我們新發行給對方的 credentials token
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        try:
            party_credentials_response = OcpiCredentialsResponse.model_validate(response.json())
            return party_credentials_response.data
        except ValidationError as e: raise e


    async def get_location(self, location_id: str):
        '''
        Retrieve a Location as it is stored in the eMSP system.
        
        If the CPO wants to check the status of a Location, EVSE or Connector object in the eMSP system, it might GET the
        object from the eMSP system for validation purposes. The CPO is the owner of the objects, so it would be illogical if
        the eMSP system had a different status or was missing an object. If a discrepancy is found, the CPO might push an
        update to the eMSP via a PUT or PATCH call.
        '''
        if not self.party.v221_endpoints:
            self.logger.warning({'title': 'No endpoints in this party', 'instance': {'party_id': self.party.party_id, '2.2.1 endpoints': self.party.v221_endpoints}})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.locations and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.get(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{location_id}',
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        ocpi_response = OcpiLocationResponse.model_validate(response.json())
        return ocpi_response.data
    

    async def get_evse(self, location_id: str, evse_uid: str):
        '''
        Retrieve a Location as it is stored in the eMSP system.
        
        If the CPO wants to check the status of a Location, EVSE or Connector object in the eMSP system, it might GET the
        object from the eMSP system for validation purposes. The CPO is the owner of the objects, so it would be illogical if
        the eMSP system had a different status or was missing an object. If a discrepancy is found, the CPO might push an
        update to the eMSP via a PUT or PATCH call.
        '''
        if not self.party.v221_endpoints:
            self.logger.warning({'title': 'No endpoints in this party', 'instance': {'party_id': self.party.party_id, '2.2.1 endpoints': self.party.v221_endpoints}})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.locations and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.get(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{location_id}/{evse_uid}',
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        ocpi_response = OcpiEvseResponse.model_validate(response.json())
        return ocpi_response.data
    

    async def get_connector(self, location_id: str, evse_uid: str, connector_id: str):
        '''
        Retrieve a Location as it is stored in the eMSP system.
        
        If the CPO wants to check the status of a Location, EVSE or Connector object in the eMSP system, it might GET the
        object from the eMSP system for validation purposes. The CPO is the owner of the objects, so it would be illogical if
        the eMSP system had a different status or was missing an object. If a discrepancy is found, the CPO might push an
        update to the eMSP via a PUT or PATCH call.
        '''
        if not self.party.v221_endpoints:
            self.logger.warning({'title': 'No endpoints in this party', 'instance': {'party_id': self.party.party_id, '2.2.1 endpoints': self.party.v221_endpoints}})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.locations and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.get(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{location_id}/{evse_uid}/{connector_id}',
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        ocpi_response = OcpiConnectorResponse.model_validate(response.json())
        return ocpi_response.data


    async def put_location(self, location: OcpiLocation):
        '''
        Push new/updated Location, EVSE and/or Connector to the eMSP.
        '''
        if not self.party.v221_endpoints:
            self.logger.warning({'title': 'No endpoints in this party', 'instance': {'party_id': self.party.party_id, '2.2.1 endpoints': self.party.v221_endpoints}})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.locations and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.put(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{location.id}',
            json=location.model_dump(mode='json'),
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        return True


    async def put_evse(self, ocpi_location_id: str, ocpi_evse: OcpiEvse):
        '''
        Push new/updated EVSE and/or Connector to the eMSP.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.locations and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.put(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{ocpi_location_id}/{ocpi_evse.uid}',
            json=ocpi_evse.model_dump(mode='json'),
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        return True


    async def get_tokens(self):
        '''
        Get the list of known Tokens, last updated between the {date_from} and {date_to} (paginated)
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            raise ValueError({
                'title': 'Party OCPI V2.2.1 endpoints not available',
                'instance': {'country_code': self.party.country_code, 'party_id': self.party.party_id},
            })
        try:
            endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.tokens and item.role == OcpiInterfaceRoleEnum.SENDER)
        except StopIteration as stop_iteration:
            self.logger.error({'title': 'Remote party does not have tokens endpoint', 'instance': {'remote_party_endpoints': self.party.v221_endpoints}})
            raise ValueError('Remote party does not have tokens endpoint') from stop_iteration
        response = await self.client.get(
            str(endpoint.url),
            # params={
            #     'date_from': ..., # Only return Tokens that have last_updated after or equal to this Date/Time (inclusive).
            #     'date_to': ..., # Only return Tokens that have last_updated up to this Date/Time, but not including (exclusive).
            #     'offset': ..., # The offset of the first object returned. Default is 0.
            #     'limit': ..., # Maximum number of objects to GET.
            # },
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        ocpi_response = OcpiTokenListResponse.model_validate(response.json())
        return ocpi_response.data



    async def post_token_authorization(self, token: OcpiToken, location_reference: OcpiLocationReferences):
        '''
        Real-time authorization request
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.tokens and item.role == OcpiInterfaceRoleEnum.SENDER)
        response = await self.client.post(
            f'{endpoint.url}/{token.uid}/authorize',
            params={'type': token.type.value}, # https://ocpi.server.com/2.2/tokens/012345678/authorize?type=RFID
            json=location_reference.model_dump(mode='json'),
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        authorization_info = OcpiAuthorizationInfoResponse.model_validate(response.json())
        return authorization_info.data


    async def post_command_result(self, response_url: str, result: OcpiCommandResult):
        '''
        Receive the asynchronous response from the Charge Point.
        '''
        self.logger.info({'title': 'Response to command', 'instance': {'result': result}})
        response = await self.client.post(response_url, json=result, headers={
            'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
            'OCPI-from-country-code': self.from_country_code,
            'OCPI-from-party-id': self.from_party_id,
            'OCPI-to-country-code': self.party.country_code,
            'OCPI-to-party-id': self.party.party_id,
            'X-Request-ID': str(uuid4()),
            'X-Correlation-ID': str(uuid4()),
        })


    async def put_session(self, session: OcpiSession):
        '''
        Send a new/updated Session object to the eMSP.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.sessions and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.put(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{session.id}',
            json=session.model_dump(mode='json'),
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        ocpi_response = OcpiBaseResponse.model_validate(response.json())
        return ocpi_response


    async def patch_session(self, session: OcpiSessionUpdate):
        '''
        Update the Session object with Session.id equal to `{session_id}`.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.sessions and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.patch(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{session.id}',
            json=session.model_dump(mode='json'),
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        ocpi_response = OcpiBaseResponse.model_validate(response.json())
        if ocpi_response.status_code == OcpiStatusCodeEnum.SUCCESS: return True
        else:
            self.logger.error(ocpi_response)
            return False


    async def get_session(self, session_id: str):
        '''
        Retrieve a Session object from the eMSP’s system with Session.id equal to {session_id}.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.sessions and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.get(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{session_id}',
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        try:
            ocpi_response = OcpiSessionResponse.model_validate(response.json())
            return ocpi_response.data
        except ValidationError as e:
            ocpi_response = OcpiBaseResponse.model_validate(response.json())
            e.add_note(ocpi_response.model_dump_json())
            self.logger.error(e)


    async def post_cdr(self, cdr: OcpiCdr):
        '''
        Send a new CDR.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.cdrs and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.post(
            str(endpoint.url),
            json=cdr.model_dump(mode='json'),
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        cdr_url_in_msp: str = response.headers.get('Location')
        return cdr_url_in_msp


    async def get_cdr(self, url: httpx.URL):
        '''
        Retrieve an existing CDR.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.cdrs and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.get(
            url,
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        ocpi_response =  OcpiCdrResponse.model_validate(response.json())
        return ocpi_response.data


    async def put_tariff(self, tariff: OcpiTariff):
        '''
        Push new/updated Tariff object to the eMSP.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.tariffs and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.put(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{tariff.id}',
            json=tariff.model_dump(mode='json'),
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )


    async def get_tariff(self, tariff_id: str):
        '''
        Retrieve a Tariff as it is stored in the eMSP’s system.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.tariffs and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.get(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{tariff_id}',
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
        ocpi_response = OcpiTariffResponse.model_validate(response.json())
        return ocpi_response.data


    async def delete_tariff(self, tariff_id: str):
        '''
        Remove a Tariff object which is no longer in use and will not be used in future either.

        NOTE: Before deleting a Tariff object, it is RECOMMENDED to ensure that the Tariff object is not referenced by any
        Connector object within the `tariff_ids`.
        '''
        if not self.party.v221_endpoints:
            self.logger.error({'title': 'No endpoints in this party', 'instance': self.party})
            return
        endpoint = next(item for item in self.party.v221_endpoints if item.identifier == OcpiModuleIdEnum.tariffs and item.role == OcpiInterfaceRoleEnum.RECEIVER)
        response = await self.client.delete(
            f'{endpoint.url}/{self.from_country_code}/{self.from_party_id}/{tariff_id}',
            headers={
                'Authorization': f'Token {b64encode(str(self.party.credentials_token_for_sending_request_to_party).encode()).decode()}',
                'OCPI-from-country-code': self.from_country_code,
                'OCPI-from-party-id': self.from_party_id,
                'OCPI-to-country-code': self.party.country_code,
                'OCPI-to-party-id': self.party.party_id,
                'X-Request-ID': str(uuid4()),
                'X-Correlation-ID': str(uuid4()),
            },
        )
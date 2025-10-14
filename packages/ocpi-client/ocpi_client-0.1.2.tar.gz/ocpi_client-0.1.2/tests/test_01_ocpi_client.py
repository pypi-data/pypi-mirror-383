from datetime import UTC, datetime
from decimal import Decimal
import beanie
import httpx

from ocpi_pydantic.v221.cdrs import OcpiCdr
from ocpi_pydantic.v221.locations.connector import OcpiConnector
from ocpi_pydantic.v221.locations.location import OcpiHours, OcpiLocation, OcpiGeoLocation
from ocpi_pydantic.v221.locations.evse import OcpiEvse
from ocpi_pydantic.v221.credentials import OcpiCredentials, OcpiCredentialsResponse
from ocpi_pydantic.v221.enum import OcpiConnectorTypeEnum, OcpiVersionNumberEnum, OcpiPowerTypeEnum, OcpiTariffTypeEnum, OcpiTariffDimensionTypeEnum, OcpiStatusEnum, OcpiStatusCodeEnum, OcpiSessionStatusEnum
from ocpi_pydantic.v221.sessions import OcpiSession
from ocpi_pydantic.v221.tariffs import OcpiTariff, OcpiTariffElement, OcpiPriceComponent
from ocpi_pydantic.v221.tokens import OcpiToken, OcpiLocationReferences, OcpiAuthorizationInfo, OcpiTokenListResponse
from ocpi_pydantic.v221.versions import OcpiEndpoint
from ocpi_client import OcpiClient
from ocpi_client.models import OcpiParty
from pydantic import HttpUrl
from pymongo.asynchronous.database import AsyncDatabase
import pytest
import pytest_asyncio

from app.database.models import Connector, DbOcpiCdr, DbOcpiSession, Pile, Station
from app.logging import logger
from app.ocpi.ocpi_logging import ocpi_logger
from app.settings import get_settings



_SETTINGS = get_settings()



@pytest_asyncio.fixture
async def ocpi_client(party_fixture: OcpiParty):
    return OcpiClient(httpx_async_client=httpx.AsyncClient(), party=party_fixture)



class TestOcpiClient:
    location: OcpiLocation
    evse: OcpiEvse
    connector: OcpiConnector
    tokens: list[OcpiToken]
    tariff: OcpiTariff
    session: OcpiSession
    cdr: OcpiCdr


    @pytest.mark.asyncio
    async def test_get_versions(self, ocpi_client: OcpiClient):
        versions = await ocpi_client.get_versions()
        assert versions
        assert not ocpi_client.client.is_closed


    @pytest.mark.asyncio
    async def test_get_version_details(self, ocpi_client: OcpiClient):
        endpoints = await ocpi_client.get_version_details(version=OcpiVersionNumberEnum.v221)
        # logger.debug(endpoints)
        assert endpoints

    
#     Post credential 給對方後，對方會發行新的 token 給我方，但也因此會使 staging 的 token 失效，所以這不走自動化測試。
#     @pytest.mark.asyncio
#     async def test_post_credentials(self, ocpi_client: OcpiClient):
#         ocpi_client.party.v221_endpoints = [OcpiEndpoint(
#             identifier=OcpiModuleIdEnum.credentials,
#             role=OcpiInterfaceRoleEnum.RECEIVER,
#             url=HttpUrl(...)
#         )]
        
#         response = await ocpi_client.post_credentials(
#             version=OcpiVersionNumberEnum.v221,
#             our_credentials=OcpiCredentials(
#                 token='t',
#                 url=HttpUrl('https://www.wnc.net'),
#                 roles=[],
#             )
#         )
#         assert response == ...
        


    @pytest.mark.asyncio
    async def test_put_location(self, ocpi_client: OcpiClient, location: OcpiLocation) -> None:
        location.coordinates.latitude = '24.878'
        location.coordinates.longitude = '121.211'
        location.postal_code = '325'
        location.city = '桃園市'
        location.address = '龍潭區百年路 1 號'
        location.opening_times = OcpiHours(twentyfourseven=True)
        location.publish = True
        TestOcpiClient.location = location

        response = await ocpi_client.put_location(location=await TestOcpiClient.location)
        assert response


    @pytest.mark.asyncio
    async def test_get_location(self, ocpi_client: OcpiClient):
        location = await ocpi_client.get_location(location_id=TestOcpiClient.location.id)
        assert location
        assert location.id == TestOcpiClient.location.id


    @pytest.mark.asyncio
    async def test_put_evse(self, ocpi_client: OcpiClient, evse: OcpiEvse, connector: OcpiConnector):
        evse.floor_level = '1F'
        TestOcpiClient.evse = evse

        connector.standard = OcpiConnectorTypeEnum.IEC_62196_T2_COMBO
        connector.power_type = OcpiPowerTypeEnum.AC_2_PHASE
        connector.max_voltage = 380
        connector.max_amperage = 100
        TestOcpiClient.connector = connector
        
        response = await ocpi_client.put_evse(ocpi_location_id=TestOcpiClient.location.id, ocpi_evse=await TestOcpiClient.evse)
        assert response


    @pytest.mark.asyncio
    async def test_get_evse(self, ocpi_client: OcpiClient):
        evse = await ocpi_client.get_evse(location_id=TestOcpiClient.location.id, evse_uid=TestOcpiClient.evse.uid)
        assert evse
        
        assert float(evse.coordinates.latitude) == TestOcpiClient.location.coordinates.latitude
        assert float(evse.coordinates.longitude) == TestOcpiClient.location.coordinates.longitude
        assert evse.images == TestOcpiClient.location.images

        assert evse.uid == TestOcpiClient.evse.uid
        assert evse.physical_reference == TestOcpiClient.evse.physical_reference
        assert evse.directions == TestOcpiClient.evse.directions
        assert evse.capabilities == TestOcpiClient.evse.capabilities
        # assert evse.floor_level == TestOcpiClient.pile.floor_level
        assert evse.parking_restrictions == TestOcpiClient.evse.parking_restrictions
        # assert evse.last_updated == TestOcpiClient.pile.heartbeat_timestamp

        ocpi_evse_with_connector = await TestOcpiClient.connector.to_ocpi_evse_with_connector()
        
        assert evse.evse_id == ocpi_evse_with_connector.evse_id
        # assert evse.status == ocpi_evse_with_connector.status
        assert evse.status_schedule == ocpi_evse_with_connector.status_schedule

        assert evse.connectors[0].id == ocpi_evse_with_connector.connectors[0].id
        assert evse.connectors[0].standard == TestOcpiClient.connector.standard
        assert evse.connectors[0].format == ocpi_evse_with_connector.connectors[0].format
        assert evse.connectors[0].tariff_ids == TestOcpiClient.evse.ocpi_tariff_ids
        assert evse.connectors[0].max_voltage == TestOcpiClient.connector.max_voltage
        # assert evse.connectors[0].power_type == TestOcpiClient.connector.power_type
        assert evse.connectors[0].max_amperage == TestOcpiClient.connector.max_amperage
        assert evse.connectors[0].max_electric_power == TestOcpiClient.connector.max_electric_power
        # assert evse.connectors[0].terms_and_conditions == ocpi_evse_with_connector.connectors[0].terms_and_conditions
        # assert evse.connectors[0].last_updated == ocpi_evse_with_connector.connectors[0].last_updated


    @pytest.mark.asyncio
    async def test_get_connector(self, ocpi_client: OcpiClient):
        connector = await ocpi_client.get_connector(
            location_id=TestOcpiClient.location.station_id,
            evse_uid=TestOcpiClient.evse.ocpi_evse_uid,
            connector_id=str(TestOcpiClient.connector.connector_id),
        )
        assert connector
        assert connector.id == str(TestOcpiClient.connector.connector_id)


    @pytest.mark.asyncio
    async def test_get_tokens(self, ocpi_client: OcpiClient):
        TestOcpiClient.tokens = await ocpi_client.get_tokens()
        assert TestOcpiClient.tokens


    @pytest.mark.xfail(reason='TW-EVO does not implement OCPI real-time authorization')
    @pytest.mark.asyncio
    async def test_post_toekn_authorizatiion(self, ocpi_client: OcpiClient):
        ocpi_logger.debug(TestOcpiClient.evse)
        response = await ocpi_client.post_token_authorization(
            token=TestOcpiClient.tokens[0],
            location_reference=OcpiLocationReferences(location_id=TestOcpiClient.location.station_id, evse_uids=[TestOcpiClient.evse.ocpi_evse_uid])
        )
        ocpi_logger.debug(response)
        assert response


    @pytest.mark.asyncio
    async def test_put_tariff(self, ocpi_client: OcpiClient):
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        TestOcpiClient.tariff = OcpiTariff(
            country_code=_SETTINGS.OCPI_COUNTRY_CODE,
            party_id=_SETTINGS.OCPI_PARTY_ID,
            id=f'TEST{now.strftime("%Y%m%d%H%M%S")}', # TEST20241012234343
            currency='TWD',
            type=OcpiTariffTypeEnum.PROFILE_FAST,
            elements=[OcpiTariffElement(price_components=[OcpiPriceComponent(
                type=OcpiTariffDimensionTypeEnum.ENERGY,
                price=Decimal('10'),
                vat=5,
                step_size=1,
            )])],
            last_updated=now,
        )
        response = await ocpi_client.put_tariff(tariff=TestOcpiClient.tariff)


    @pytest.mark.asyncio
    async def test_get_tariff(self, ocpi_client: OcpiClient):
        response = await ocpi_client.get_tariff(tariff_id=TestOcpiClient.tariff.id)
        assert response


    @pytest.mark.asyncio
    async def test_delete_tariff(self, ocpi_client: OcpiClient):
        response = await ocpi_client.delete_tariff(tariff_id=TestOcpiClient.tariff.id)


    @pytest.mark.xfail(reason='TW-EVO MSP does not keep sessions with no command from them')
    @pytest.mark.asyncio
    async def test_put_session(self, ocpi_client: OcpiClient, new_session: DbOcpiSession):
        '''
        此測試於 put 階段會成功，get 階段會失敗，因為 session 並沒有真的來自交易，他們收到 session 表示成功應該只是格式上沒問題，實際上沒有真的存下來。
        '''
        TestOcpiClient.session = new_session
        await TestOcpiClient.session.insert()

        put_response = await ocpi_client.put_session(session=TestOcpiClient.session.to_ocpi_session())
        assert put_response
        assert put_response.status_code == OcpiStatusCodeEnum.SUCCESS

        get_response = await ocpi_client.get_session(session_id=TestOcpiClient.session.id)
        assert get_response
        assert get_response.id == str(TestOcpiClient.session.id)


    @pytest.mark.xfail(reason='MSP does not keep sessions with no command from them')
    @pytest.mark.asyncio
    async def test_patch_session(self, ocpi_client: OcpiClient):
        '''
        同上，patch 應該會失敗，當然 get 也會失敗。
        '''
        TestOcpiClient.session.status = OcpiSessionStatusEnum.COMPLETED
        response = await ocpi_client.patch_session(session=TestOcpiClient.session.to_ocpi_session())
        assert response

        get_response = await ocpi_client.get_session(session_id=TestOcpiClient.session.id)
        assert get_response
        assert get_response.id == str(TestOcpiClient.session.id)
        assert get_response.status == TestOcpiClient.session.status


    # @pytest.mark.skip(reason='WIP')
    @pytest.mark.asyncio
    async def test_post_cdr(self, ocpi_client: OcpiClient, new_cdr: DbOcpiCdr):
        TestOcpiClient.cdr = new_cdr
        await TestOcpiClient.cdr.insert()
        response = await ocpi_client.post_cdr(cdr=TestOcpiClient.cdr.to_ocpi_cdr())
        assert response
        TestOcpiClient.cdr.url_in_msp = response


    @pytest.mark.asyncio
    async def test_get_cdr(self, ocpi_client: OcpiClient):
        response = await ocpi_client.get_cdr(url=TestOcpiClient.cdr.url_in_msp)
        assert response
        assert response.id == str(TestOcpiClient.cdr.id)

        await TestOcpiClient.cdr.delete()


    @pytest.mark.asyncio
    async def test_delete_sesion(self, mongodb: AsyncDatabase):
        await TestOcpiClient.session.delete()

    
    @pytest.mark.asyncio
    async def test_remove_evse(self, ocpi_client: OcpiClient):
        ocpi_evse = await TestOcpiClient.connector.to_ocpi_evse_with_connector()
        ocpi_evse.status = OcpiStatusEnum.REMOVED

        response = await ocpi_client.put_evse(ocpi_location_id=TestOcpiClient.location.station_id, ocpi_evse=ocpi_evse)
        assert response


    @pytest.mark.asyncio
    async def test_delete_fixtures(self, mongodb: AsyncDatabase):
        await TestOcpiClient.location.delete()
        await TestOcpiClient.evse.delete()
        # await TestOcpiClient.connector.delete()

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import beanie
from ocpi_pydantic.v221.base import OcpiPrice, OcpiDisplayText
from ocpi_pydantic.v221.cdrs import OcpiCdrToken, OcpiCdrLocation, OcpiChargingPeriod, OcpiCdrDimension
from ocpi_pydantic.v221.enum import OcpiAuthMethodEnum, OcpiReservationRestrictionTypeEnum, OcpiConnectorTypeEnum, OcpiTokenTypeEnum, OcpiWhitelistTypeEnum, OcpiConnectorFormatEnum, OcpiPowerTypeEnum, OcpiCdrDimensionTypeEnum, OcpiSessionStatusEnum, OcpiTariffDimensionTypeEnum, OcpiTariffTypeEnum, OcpiDayOfWeekEnum, OcpiStatusCodeEnum, OcpiPartyRoleEnum
from ocpi_pydantic.v221.locations import OcpiGeoLocation
from ocpi_client.models import OcpiParty
from pymongo.asynchronous.database import AsyncDatabase
import pytest_asyncio

from app.database.models import Connector, DbOcpiCdr, DbOcpiSession, Pile, Station, Transaction




@pytest_asyncio.fixture
async def party_fixture():
    return OcpiParty(
        country_code='TW',
        party_id=...,
        party_roles=[OcpiPartyRoleEnum.EMSP, OcpiPartyRoleEnum.CPO],
        versions_url=...,
        credentials_token_for_receiving_request_from_party=...,

        credentials_token_for_sending_register_to_party=...,
        credentials_token_for_sending_request_to_party=...,
        
        v221_endpoints=[],
    )



@pytest_asyncio.fixture
async def new_session(random_connector: Connector, new_transaction: Transaction):
    station = await Station.find_one({'station_id': random_connector.station_id})
    assert station
    pile = await Pile.find_one({'evse_id': random_connector.evse_id})
    assert pile

    new_transaction.connector_id = random_connector.connector_id
    new_transaction.station_id = station.station_id
    new_transaction.evse_id = pile.evse_id

    session = DbOcpiSession(
        db_evse_id=pile.evse_id,
        db_transaction_id=new_transaction.transaction_id,
        receiver_country_code='TW',
        receiver_party_id='EVO',

        country_code='TW',
        party_id='WIN',
        start_date_time=new_transaction.start_time,
        end_date_time=new_transaction.end_time,
        kwh=new_transaction.meter_stop - new_transaction.meter_start,
        cdr_token=OcpiCdrToken(
            country_code='TW',
            party_id='EVO',
            uid='UID1',
            type=OcpiTokenTypeEnum.APP_USER,
            contract_id='TW-WIN-CA2B3C4D5-L', # https://evroaming.org/wp-content/uploads/2024/10/20211118-PSA-IDACS-whitepaper-ID-Format-and-syntax-v0.4-clean-version.pdf
        ),
        auth_method=OcpiAuthMethodEnum.COMMAND,
        authorization_reference='AREF1',
        location_id=station.station_id,
        evse_uid=pile.ocpi_evse_uid,
        connector_id=str(random_connector.connector_id),
        meter_id=None,
        currency='TWD',
        charging_periods=[OcpiChargingPeriod(
            start_date_time=new_transaction.start_time,
            dimensions=[
                OcpiCdrDimension(type=OcpiCdrDimensionTypeEnum.ENERGY, volume=10),
                OcpiCdrDimension(type=OcpiCdrDimensionTypeEnum.TIME, volume=1),
            ],
            tariff_id=None,
        )],
        total_cost=OcpiPrice(excl_vat=Decimal(95), incl_vat=Decimal(100)),
        status=OcpiSessionStatusEnum.COMPLETED,
        last_updated=new_transaction.end_time,
    )
    return session



@pytest_asyncio.fixture()
async def new_cdr(random_connector: Connector):
    now = datetime.now(UTC).replace(microsecond=0)
    station = await Station.find_one({'station_id': random_connector.station_id})
    assert station
    pile = await Pile.find_one({'evse_id': random_connector.evse_id})
    assert pile

    return DbOcpiCdr(
        # id=PydanticObjectId(),
        receiver_country_code='TW',
        receiver_party_id=...,
        
        country_code='TW',
        party_id=...,
        start_date_time=now,
        end_date_time=now + timedelta(hours=1),
        session_id=f'SID-TEST-{now.strftime('%Y%m%d%H%M%S')}',
        cdr_token=OcpiCdrToken(
            country_code='TW',
            party_id=...,
            uid='UID1',
            type=OcpiTokenTypeEnum.APP_USER,
            contract_id='DE-8AA-CA2B3C4D5-L', # https://evroaming.org/wp-content/uploads/2024/10/20211118-PSA-IDACS-whitepaper-ID-Format-and-syntax-v0.4-clean-version.pdf
        ),
        auth_method=OcpiAuthMethodEnum.COMMAND,
        authorization_reference='AREF1',
        cdr_location=OcpiCdrLocation(
            id=station.station_id,
            name=station.station_name,
            address=station.address or '龍潭區百年路 1 號',
            city=station.city or '桃園市',
            postal_code=station.postal_code,
            state=station.state,
            country=station.country,
            coordinates=OcpiGeoLocation(latitude=str(station.latitude) or '24', longitude=str(station.longitude) or '121'),
            evse_uid=pile.ocpi_evse_uid,
            evse_id=f'TW*WIN*E{pile.ocpi_evse_uid}*{random_connector.connector_id}', # TW*WIN*A0B7655887B8*1
            connector_id=str(random_connector.connector_id),
            connector_standard=random_connector.standard or OcpiConnectorTypeEnum.IEC_62196_T2_COMBO,
            connector_format=OcpiConnectorFormatEnum.CABLE,
            connector_power_type=random_connector.power_type or OcpiPowerTypeEnum.DC,
        ),
        meter_id=None,
        currency='TWD',
        tariffs=[],
        charging_periods=[OcpiChargingPeriod(
            start_date_time=now,
            dimensions=[
                OcpiCdrDimension(type=OcpiCdrDimensionTypeEnum.ENERGY, volume=10),
                OcpiCdrDimension(type=OcpiCdrDimensionTypeEnum.TIME, volume=1),
            ],
            tariff_id=None,
        )],
        signed_data=None,
        total_cost=OcpiPrice(excl_vat=Decimal(95), incl_vat=Decimal(100)),
        total_fixed_cost=None,
        total_energy=10,
        total_energy_cost=None,
        total_time=1,
        total_time_cost=None,
        total_parking_time=1,
        total_parking_cost=None,
        total_reservation_cost=None,
        remark='R01',
        invoice_reference_id='IID1',
        credit=False,
        credit_reference_id=None,
        home_charging_compensation=None,
        last_updated=now + timedelta(hours=1),
    )
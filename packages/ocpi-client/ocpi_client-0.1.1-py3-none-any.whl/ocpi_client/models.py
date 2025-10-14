from typing import Annotated, ClassVar
from uuid import uuid4

from ocpi_pydantic.v221.base import OcpiPrice
from ocpi_pydantic.v221.enum import OcpiPartyRoleEnum, OcpiSessionStatusEnum, OcpiConnectorTypeEnum, OcpiPowerTypeEnum, OcpiCapabilityEnum, OcpiStatusEnum, OcpiConnectorFormatEnum
from ocpi_pydantic.v221.versions import OcpiEndpoint
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl



class OcpiParty(BaseModel):
    country_code: str = Field(description='ISO 3166 alpha-2', min_length=2, max_length=2)
    party_id: str = Field(min_length=3, max_length=3)
    # party_role: OcpiPartyRoleEnum | None = Field(None, deprecated=True)
    party_roles: list[OcpiPartyRoleEnum] = []
    credentials_token_for_receiving_register_from_party: None | str = None
    credentials_token_for_sending_register_to_party: None | str = None
    credentials_token_for_receiving_request_from_party: None | str = None
    credentials_token_for_sending_request_to_party: None | str = None
    versions_url: None | HttpUrl = None
    v221_endpoints: None | list[OcpiEndpoint] = None

    _example: ClassVar[dict] = {
        'enable': True,
        'party_id': 'WIN',
        'country_code': 'TW',
        'party_roles': [OcpiPartyRoleEnum.CPO, OcpiPartyRoleEnum.EMSP],
        'credentials_token_for_receiving_register_from_party': str(uuid4()),
        'credentials_token_for_sending_register_to_party': str(uuid4()),
        'credentials_token_for_receiving_request_from_party': str(uuid4()),
        'credentials_token_for_sending_request_to_party': str(uuid4()),
        'versions_url': 'https://example2.com/ocip/versions',
        'v221_endpoints': OcpiEndpoint._examples,
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiSessionUpdate(BaseModel):
    id: str = Field(max_length=36, description='The unique id that identifies the charging session in the CPO platform.')
    end_date_time: Annotated[AwareDatetime | None, Field(
        description='''
        The timestamp when the session was completed/finished, charging
        might have finished before the session ends, for example: EV is full,
        but parking cost also has to be paid.
        ''',
    )] = None
    kwh: float = Field(description='How many kWh were charged.')
    total_cost: Annotated[OcpiPrice | None, Field(
        description='''
        The total cost of the session in the specified currency. This is the
        price that the eMSP will have to pay to the CPO. A total_cost of
        0.00 means free of charge. When omitted, i.e. no price information
        is given in the Session object, it does not imply the session is/was
        free of charge.
        ''',
    )] = None
    status: OcpiSessionStatusEnum = Field(description='The status of the session.')
    last_updated: AwareDatetime = Field(description='Timestamp when this Session was last updated (or created).')
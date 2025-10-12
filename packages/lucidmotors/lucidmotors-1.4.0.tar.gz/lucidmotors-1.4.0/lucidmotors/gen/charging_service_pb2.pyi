from . import vehicle_state_service_pb2 as _vehicle_state_service_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMAGE_CATEGORY_UNKNOWN: _ClassVar[ImageCategory]
    IMAGE_CATEGORY_OPERATOR: _ClassVar[ImageCategory]

class Capability(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAPABILITY_UNKNOWN: _ClassVar[Capability]
    CAPABILITY_CHARGING_PROFILE_CAPABLE: _ClassVar[Capability]
    CAPABILITY_CREDIT_CARD_PAYABLE: _ClassVar[Capability]
    CAPABILITY_REMOTE_START_STOP_CAPABLE: _ClassVar[Capability]
    CAPABILITY_RESERVABLE: _ClassVar[Capability]
    CAPABILITY_RFID_READER: _ClassVar[Capability]
    CAPABILITY_UNLOCK_CAPABLE: _ClassVar[Capability]

class ChargingStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHARGING_STATUS_UNKNOWN: _ClassVar[ChargingStatus]
    CHARGING_STATUS_CHARGING: _ClassVar[ChargingStatus]

class ConnectorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONNECTOR_TYPE_UNKNOWN: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_CHADEMO: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_A: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_B: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_C: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_D: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_E: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_F: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_G: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_H: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_I: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_J: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_K: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_DOMESTIC_L: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_60309_2_single_16: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_60309_2_three_16: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_60309_2_three_32: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_60309_2_three_64: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_62196_T1: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_62196_T1_COMBO: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_62196_T2: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_62196_T2_COMBO: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_62196_T3A: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_IEC_62196_T3C: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_TESLA_R: _ClassVar[ConnectorType]
    CONNECTOR_TYPE_TESLA_S: _ClassVar[ConnectorType]

class ConnectorFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONNECTOR_FORMAT_UNKNOWN: _ClassVar[ConnectorFormat]
    CONNECTOR_FORMAT_SOCKET: _ClassVar[ConnectorFormat]
    CONNECTOR_FORMAT_CABLE: _ClassVar[ConnectorFormat]

class PowerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POWER_TYPE_UNKNOWN: _ClassVar[PowerType]
    POWER_TYPE_AC_1_PHASE: _ClassVar[PowerType]
    POWER_TYPE_AC_3_PHASE: _ClassVar[PowerType]
    POWER_TYPE_DC: _ClassVar[PowerType]

class LocationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOCATION_TYPE_ON_STREET: _ClassVar[LocationType]
    LOCATION_TYPE_PARKING_GARAGE: _ClassVar[LocationType]
    LOCATION_TYPE_UNDERGROUND_GARAGE: _ClassVar[LocationType]
    LOCATION_TYPE_PARKING_LOT: _ClassVar[LocationType]
    LOCATION_TYPE_OTHER: _ClassVar[LocationType]
    LOCATION_TYPE_UNKNOWN: _ClassVar[LocationType]

class FeeName(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FEE_NAME_UNKNOWN: _ClassVar[FeeName]
    FEE_NAME_TAX: _ClassVar[FeeName]
    FEE_NAME_PARKING_FEE: _ClassVar[FeeName]

class FeeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FEE_TYPE_UNKNOWN: _ClassVar[FeeType]
    FEE_TYPE_ADD_ON_FEE_FLAT: _ClassVar[FeeType]

class AdditionalFilters(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILTER_UNKNOWN: _ClassVar[AdditionalFilters]
    FILTER_OPEN_24_HOURS: _ClassVar[AdditionalFilters]
    FILTER_CURRENTLY_AVAILABLE: _ClassVar[AdditionalFilters]
    FILTER_GREEN_ENERGY_ONLY: _ClassVar[AdditionalFilters]

class CommandResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMMAND_RESPONSE_TYPE_UNKNOWN: _ClassVar[CommandResponseType]
    COMMAND_RESPONSE_TYPE_NOT_SUPPORTED: _ClassVar[CommandResponseType]
    COMMAND_RESPONSE_TYPE_REJECTED: _ClassVar[CommandResponseType]
    COMMAND_RESPONSE_TYPE_ACCEPTED: _ClassVar[CommandResponseType]
    COMMAND_RESPONSE_TYPE_TIMEOUT: _ClassVar[CommandResponseType]
    COMMAND_RESPONSE_TYPE_UNKNOWN_SESSION: _ClassVar[CommandResponseType]
IMAGE_CATEGORY_UNKNOWN: ImageCategory
IMAGE_CATEGORY_OPERATOR: ImageCategory
CAPABILITY_UNKNOWN: Capability
CAPABILITY_CHARGING_PROFILE_CAPABLE: Capability
CAPABILITY_CREDIT_CARD_PAYABLE: Capability
CAPABILITY_REMOTE_START_STOP_CAPABLE: Capability
CAPABILITY_RESERVABLE: Capability
CAPABILITY_RFID_READER: Capability
CAPABILITY_UNLOCK_CAPABLE: Capability
CHARGING_STATUS_UNKNOWN: ChargingStatus
CHARGING_STATUS_CHARGING: ChargingStatus
CONNECTOR_TYPE_UNKNOWN: ConnectorType
CONNECTOR_TYPE_CHADEMO: ConnectorType
CONNECTOR_TYPE_DOMESTIC_A: ConnectorType
CONNECTOR_TYPE_DOMESTIC_B: ConnectorType
CONNECTOR_TYPE_DOMESTIC_C: ConnectorType
CONNECTOR_TYPE_DOMESTIC_D: ConnectorType
CONNECTOR_TYPE_DOMESTIC_E: ConnectorType
CONNECTOR_TYPE_DOMESTIC_F: ConnectorType
CONNECTOR_TYPE_DOMESTIC_G: ConnectorType
CONNECTOR_TYPE_DOMESTIC_H: ConnectorType
CONNECTOR_TYPE_DOMESTIC_I: ConnectorType
CONNECTOR_TYPE_DOMESTIC_J: ConnectorType
CONNECTOR_TYPE_DOMESTIC_K: ConnectorType
CONNECTOR_TYPE_DOMESTIC_L: ConnectorType
CONNECTOR_TYPE_IEC_60309_2_single_16: ConnectorType
CONNECTOR_TYPE_IEC_60309_2_three_16: ConnectorType
CONNECTOR_TYPE_IEC_60309_2_three_32: ConnectorType
CONNECTOR_TYPE_IEC_60309_2_three_64: ConnectorType
CONNECTOR_TYPE_IEC_62196_T1: ConnectorType
CONNECTOR_TYPE_IEC_62196_T1_COMBO: ConnectorType
CONNECTOR_TYPE_IEC_62196_T2: ConnectorType
CONNECTOR_TYPE_IEC_62196_T2_COMBO: ConnectorType
CONNECTOR_TYPE_IEC_62196_T3A: ConnectorType
CONNECTOR_TYPE_IEC_62196_T3C: ConnectorType
CONNECTOR_TYPE_TESLA_R: ConnectorType
CONNECTOR_TYPE_TESLA_S: ConnectorType
CONNECTOR_FORMAT_UNKNOWN: ConnectorFormat
CONNECTOR_FORMAT_SOCKET: ConnectorFormat
CONNECTOR_FORMAT_CABLE: ConnectorFormat
POWER_TYPE_UNKNOWN: PowerType
POWER_TYPE_AC_1_PHASE: PowerType
POWER_TYPE_AC_3_PHASE: PowerType
POWER_TYPE_DC: PowerType
LOCATION_TYPE_ON_STREET: LocationType
LOCATION_TYPE_PARKING_GARAGE: LocationType
LOCATION_TYPE_UNDERGROUND_GARAGE: LocationType
LOCATION_TYPE_PARKING_LOT: LocationType
LOCATION_TYPE_OTHER: LocationType
LOCATION_TYPE_UNKNOWN: LocationType
FEE_NAME_UNKNOWN: FeeName
FEE_NAME_TAX: FeeName
FEE_NAME_PARKING_FEE: FeeName
FEE_TYPE_UNKNOWN: FeeType
FEE_TYPE_ADD_ON_FEE_FLAT: FeeType
FILTER_UNKNOWN: AdditionalFilters
FILTER_OPEN_24_HOURS: AdditionalFilters
FILTER_CURRENTLY_AVAILABLE: AdditionalFilters
FILTER_GREEN_ENERGY_ONLY: AdditionalFilters
COMMAND_RESPONSE_TYPE_UNKNOWN: CommandResponseType
COMMAND_RESPONSE_TYPE_NOT_SUPPORTED: CommandResponseType
COMMAND_RESPONSE_TYPE_REJECTED: CommandResponseType
COMMAND_RESPONSE_TYPE_ACCEPTED: CommandResponseType
COMMAND_RESPONSE_TYPE_TIMEOUT: CommandResponseType
COMMAND_RESPONSE_TYPE_UNKNOWN_SESSION: CommandResponseType

class DateTime(_message.Message):
    __slots__ = ("seconds",)
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    seconds: int
    def __init__(self, seconds: _Optional[int] = ...) -> None: ...

class Unknown(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Image(_message.Message):
    __slots__ = ("url", "category", "type")
    URL_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    url: str
    category: ImageCategory
    type: str
    def __init__(self, url: _Optional[str] = ..., category: _Optional[_Union[ImageCategory, str]] = ..., type: _Optional[str] = ...) -> None: ...

class Operator(_message.Message):
    __slots__ = ("name", "website", "logo")
    NAME_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    LOGO_FIELD_NUMBER: _ClassVar[int]
    name: str
    website: str
    logo: Image
    def __init__(self, name: _Optional[str] = ..., website: _Optional[str] = ..., logo: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class Connector(_message.Message):
    __slots__ = ("id", "standard", "format", "power_type", "voltage", "amperage", "tariff_id", "terms_and_conditions", "last_updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    STANDARD_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    POWER_TYPE_FIELD_NUMBER: _ClassVar[int]
    VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    AMPERAGE_FIELD_NUMBER: _ClassVar[int]
    TARIFF_ID_FIELD_NUMBER: _ClassVar[int]
    TERMS_AND_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    standard: ConnectorType
    format: ConnectorFormat
    power_type: PowerType
    voltage: int
    amperage: int
    tariff_id: str
    terms_and_conditions: str
    last_updated: DateTime
    def __init__(self, id: _Optional[str] = ..., standard: _Optional[_Union[ConnectorType, str]] = ..., format: _Optional[_Union[ConnectorFormat, str]] = ..., power_type: _Optional[_Union[PowerType, str]] = ..., voltage: _Optional[int] = ..., amperage: _Optional[int] = ..., tariff_id: _Optional[str] = ..., terms_and_conditions: _Optional[str] = ..., last_updated: _Optional[_Union[DateTime, _Mapping]] = ...) -> None: ...

class DisplayText(_message.Message):
    __slots__ = ("language", "text")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    language: str
    text: str
    def __init__(self, language: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class ChargingSession(_message.Message):
    __slots__ = ("uid", "evse_id", "status", "capabilities", "connectors", "floor_level", "coordinates", "physical_reference", "directions", "last_updated")
    UID_FIELD_NUMBER: _ClassVar[int]
    EVSE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    CONNECTORS_FIELD_NUMBER: _ClassVar[int]
    FLOOR_LEVEL_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    PHYSICAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    DIRECTIONS_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    uid: str
    evse_id: str
    status: ChargingStatus
    capabilities: _containers.RepeatedScalarFieldContainer[Capability]
    connectors: _containers.RepeatedCompositeFieldContainer[Connector]
    floor_level: str
    coordinates: _vehicle_state_service_pb2.Location
    physical_reference: str
    directions: DisplayText
    last_updated: DateTime
    def __init__(self, uid: _Optional[str] = ..., evse_id: _Optional[str] = ..., status: _Optional[_Union[ChargingStatus, str]] = ..., capabilities: _Optional[_Iterable[_Union[Capability, str]]] = ..., connectors: _Optional[_Iterable[_Union[Connector, _Mapping]]] = ..., floor_level: _Optional[str] = ..., coordinates: _Optional[_Union[_vehicle_state_service_pb2.Location, _Mapping]] = ..., physical_reference: _Optional[str] = ..., directions: _Optional[_Union[DisplayText, _Mapping]] = ..., last_updated: _Optional[_Union[DateTime, _Mapping]] = ...) -> None: ...

class OpeningTimes(_message.Message):
    __slots__ = ("twentyfourseven",)
    TWENTYFOURSEVEN_FIELD_NUMBER: _ClassVar[int]
    twentyfourseven: bool
    def __init__(self, twentyfourseven: bool = ...) -> None: ...

class AdditionalLocation(_message.Message):
    __slots__ = ("latitude", "longitude", "name")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    name: str
    def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., name: _Optional[str] = ...) -> None: ...

class ChargingLocation(_message.Message):
    __slots__ = ("id", "type", "name", "address", "city", "postal_code", "state", "country", "coordinates", "related_locations", "session", "operator", "suboperator", "owner", "timezone", "opening_times", "charging_when_closed", "images", "last_updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    POSTAL_CODE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    RELATED_LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    SUBOPERATOR_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    OPENING_TIMES_FIELD_NUMBER: _ClassVar[int]
    CHARGING_WHEN_CLOSED_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: LocationType
    name: str
    address: str
    city: str
    postal_code: str
    state: str
    country: str
    coordinates: _vehicle_state_service_pb2.Location
    related_locations: _containers.RepeatedCompositeFieldContainer[AdditionalLocation]
    session: ChargingSession
    operator: Operator
    suboperator: Operator
    owner: Operator
    timezone: str
    opening_times: OpeningTimes
    charging_when_closed: bool
    images: _containers.RepeatedCompositeFieldContainer[Image]
    last_updated: DateTime
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[LocationType, str]] = ..., name: _Optional[str] = ..., address: _Optional[str] = ..., city: _Optional[str] = ..., postal_code: _Optional[str] = ..., state: _Optional[str] = ..., country: _Optional[str] = ..., coordinates: _Optional[_Union[_vehicle_state_service_pb2.Location, _Mapping]] = ..., related_locations: _Optional[_Iterable[_Union[AdditionalLocation, _Mapping]]] = ..., session: _Optional[_Union[ChargingSession, _Mapping]] = ..., operator: _Optional[_Union[Operator, _Mapping]] = ..., suboperator: _Optional[_Union[Operator, _Mapping]] = ..., owner: _Optional[_Union[Operator, _Mapping]] = ..., timezone: _Optional[str] = ..., opening_times: _Optional[_Union[OpeningTimes, _Mapping]] = ..., charging_when_closed: bool = ..., images: _Optional[_Iterable[_Union[Image, _Mapping]]] = ..., last_updated: _Optional[_Union[DateTime, _Mapping]] = ...) -> None: ...

class Fee(_message.Message):
    __slots__ = ("name", "description", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: FeeName
    description: str
    type: FeeType
    def __init__(self, name: _Optional[_Union[FeeName, str]] = ..., description: _Optional[str] = ..., type: _Optional[_Union[FeeType, str]] = ...) -> None: ...

class ChargingDataRecord(_message.Message):
    __slots__ = ("id", "start_datetime", "stop_datetime", "auth_id", "total_energy", "total_parking_time", "location", "total_time", "add_on_fee", "charge_time", "idle_time", "currency")
    ID_FIELD_NUMBER: _ClassVar[int]
    START_DATETIME_FIELD_NUMBER: _ClassVar[int]
    STOP_DATETIME_FIELD_NUMBER: _ClassVar[int]
    AUTH_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ENERGY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PARKING_TIME_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TIME_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_FEE_FIELD_NUMBER: _ClassVar[int]
    CHARGE_TIME_FIELD_NUMBER: _ClassVar[int]
    IDLE_TIME_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    id: str
    start_datetime: DateTime
    stop_datetime: DateTime
    auth_id: str
    total_energy: float
    total_parking_time: float
    location: ChargingLocation
    total_time: float
    add_on_fee: _containers.RepeatedCompositeFieldContainer[Fee]
    charge_time: float
    idle_time: float
    currency: str
    def __init__(self, id: _Optional[str] = ..., start_datetime: _Optional[_Union[DateTime, _Mapping]] = ..., stop_datetime: _Optional[_Union[DateTime, _Mapping]] = ..., auth_id: _Optional[str] = ..., total_energy: _Optional[float] = ..., total_parking_time: _Optional[float] = ..., location: _Optional[_Union[ChargingLocation, _Mapping]] = ..., total_time: _Optional[float] = ..., add_on_fee: _Optional[_Iterable[_Union[Fee, _Mapping]]] = ..., charge_time: _Optional[float] = ..., idle_time: _Optional[float] = ..., currency: _Optional[str] = ...) -> None: ...

class GetCdrRequest(_message.Message):
    __slots__ = ("cdr_id",)
    CDR_ID_FIELD_NUMBER: _ClassVar[int]
    cdr_id: str
    def __init__(self, cdr_id: _Optional[str] = ...) -> None: ...

class GetCdrResponse(_message.Message):
    __slots__ = ("cdr",)
    CDR_FIELD_NUMBER: _ClassVar[int]
    cdr: ChargingDataRecord
    def __init__(self, cdr: _Optional[_Union[ChargingDataRecord, _Mapping]] = ...) -> None: ...

class GetCdrsRequest(_message.Message):
    __slots__ = ("ema_id", "offset", "limit")
    EMA_ID_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    ema_id: str
    offset: int
    limit: int
    def __init__(self, ema_id: _Optional[str] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class GetCdrsResponse(_message.Message):
    __slots__ = ("cdr",)
    CDR_FIELD_NUMBER: _ClassVar[int]
    cdr: _containers.RepeatedCompositeFieldContainer[ChargingDataRecord]
    def __init__(self, cdr: _Optional[_Iterable[_Union[ChargingDataRecord, _Mapping]]] = ...) -> None: ...

class ChargingLocationDistance(_message.Message):
    __slots__ = ("location", "distance")
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    location: ChargingLocation
    distance: int
    def __init__(self, location: _Optional[_Union[ChargingLocation, _Mapping]] = ..., distance: _Optional[int] = ...) -> None: ...

class LocationFilter(_message.Message):
    __slots__ = ("min_kw", "brand_substring", "auth_type", "plug_type", "additional_filters")
    MIN_KW_FIELD_NUMBER: _ClassVar[int]
    BRAND_SUBSTRING_FIELD_NUMBER: _ClassVar[int]
    AUTH_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLUG_TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_FILTERS_FIELD_NUMBER: _ClassVar[int]
    min_kw: int
    brand_substring: _containers.RepeatedScalarFieldContainer[str]
    auth_type: _containers.RepeatedScalarFieldContainer[Capability]
    plug_type: _containers.RepeatedScalarFieldContainer[PowerType]
    additional_filters: _containers.RepeatedScalarFieldContainer[AdditionalFilters]
    def __init__(self, min_kw: _Optional[int] = ..., brand_substring: _Optional[_Iterable[str]] = ..., auth_type: _Optional[_Iterable[_Union[Capability, str]]] = ..., plug_type: _Optional[_Iterable[_Union[PowerType, str]]] = ..., additional_filters: _Optional[_Iterable[_Union[AdditionalFilters, str]]] = ...) -> None: ...

class GetLocationsBoxRequest(_message.Message):
    __slots__ = ("ne_corner", "sw_corner", "origin", "limit", "filters")
    NE_CORNER_FIELD_NUMBER: _ClassVar[int]
    SW_CORNER_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    ne_corner: _vehicle_state_service_pb2.Location
    sw_corner: _vehicle_state_service_pb2.Location
    origin: _vehicle_state_service_pb2.Location
    limit: int
    filters: LocationFilter
    def __init__(self, ne_corner: _Optional[_Union[_vehicle_state_service_pb2.Location, _Mapping]] = ..., sw_corner: _Optional[_Union[_vehicle_state_service_pb2.Location, _Mapping]] = ..., origin: _Optional[_Union[_vehicle_state_service_pb2.Location, _Mapping]] = ..., limit: _Optional[int] = ..., filters: _Optional[_Union[LocationFilter, _Mapping]] = ...) -> None: ...

class GetLocationsBoxResponse(_message.Message):
    __slots__ = ("locations",)
    LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    locations: _containers.RepeatedCompositeFieldContainer[ChargingLocationDistance]
    def __init__(self, locations: _Optional[_Iterable[_Union[ChargingLocationDistance, _Mapping]]] = ...) -> None: ...

class GetLocationsByRadiusRequest(_message.Message):
    __slots__ = ("origin", "radius", "limit", "filters")
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    origin: _vehicle_state_service_pb2.Location
    radius: int
    limit: int
    filters: LocationFilter
    def __init__(self, origin: _Optional[_Union[_vehicle_state_service_pb2.Location, _Mapping]] = ..., radius: _Optional[int] = ..., limit: _Optional[int] = ..., filters: _Optional[_Union[LocationFilter, _Mapping]] = ...) -> None: ...

class GetLocationsByRadiusResponse(_message.Message):
    __slots__ = ("locations",)
    LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    locations: _containers.RepeatedCompositeFieldContainer[ChargingLocationDistance]
    def __init__(self, locations: _Optional[_Iterable[_Union[ChargingLocationDistance, _Mapping]]] = ...) -> None: ...

class Tariff(_message.Message):
    __slots__ = ("id", "currency", "tariff_alt_text", "tariff_alt_url", "last_updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    TARIFF_ALT_TEXT_FIELD_NUMBER: _ClassVar[int]
    TARIFF_ALT_URL_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    currency: str
    tariff_alt_text: DisplayText
    tariff_alt_url: str
    last_updated: DateTime
    def __init__(self, id: _Optional[str] = ..., currency: _Optional[str] = ..., tariff_alt_text: _Optional[_Union[DisplayText, _Mapping]] = ..., tariff_alt_url: _Optional[str] = ..., last_updated: _Optional[_Union[DateTime, _Mapping]] = ...) -> None: ...

class GetTariffRequest(_message.Message):
    __slots__ = ("tariff_id",)
    TARIFF_ID_FIELD_NUMBER: _ClassVar[int]
    tariff_id: str
    def __init__(self, tariff_id: _Optional[str] = ...) -> None: ...

class GetTariffResponse(_message.Message):
    __slots__ = ("tariff",)
    TARIFF_FIELD_NUMBER: _ClassVar[int]
    tariff: Tariff
    def __init__(self, tariff: _Optional[_Union[Tariff, _Mapping]] = ...) -> None: ...

class RegisterRFIDRequest(_message.Message):
    __slots__ = ("ema_id", "rfid_token")
    EMA_ID_FIELD_NUMBER: _ClassVar[int]
    RFID_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ema_id: str
    rfid_token: str
    def __init__(self, ema_id: _Optional[str] = ..., rfid_token: _Optional[str] = ...) -> None: ...

class RegisterRFIDResponse(_message.Message):
    __slots__ = ("status", "status_message", "status_code")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status: int
    status_message: str
    status_code: int
    def __init__(self, status: _Optional[int] = ..., status_message: _Optional[str] = ..., status_code: _Optional[int] = ...) -> None: ...

class DeleteRFIDRequest(_message.Message):
    __slots__ = ("ema_id", "rfid_token")
    EMA_ID_FIELD_NUMBER: _ClassVar[int]
    RFID_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ema_id: str
    rfid_token: str
    def __init__(self, ema_id: _Optional[str] = ..., rfid_token: _Optional[str] = ...) -> None: ...

class DeleteRFIDResponse(_message.Message):
    __slots__ = ("status", "status_message", "status_code")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status: int
    status_message: str
    status_code: int
    def __init__(self, status: _Optional[int] = ..., status_message: _Optional[str] = ..., status_code: _Optional[int] = ...) -> None: ...

class StartSessionRequest(_message.Message):
    __slots__ = ("ema_id", "location_id", "evse_uid", "vendor_name")
    EMA_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    EVSE_UID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_NAME_FIELD_NUMBER: _ClassVar[int]
    ema_id: str
    location_id: str
    evse_uid: str
    vendor_name: _vehicle_state_service_pb2.ChargingVendor
    def __init__(self, ema_id: _Optional[str] = ..., location_id: _Optional[str] = ..., evse_uid: _Optional[str] = ..., vendor_name: _Optional[_Union[_vehicle_state_service_pb2.ChargingVendor, str]] = ...) -> None: ...

class StartSessionResponse(_message.Message):
    __slots__ = ("response_type",)
    RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    response_type: CommandResponseType
    def __init__(self, response_type: _Optional[_Union[CommandResponseType, str]] = ...) -> None: ...

class StopSessionRequest(_message.Message):
    __slots__ = ("ema_id", "vendor_name")
    EMA_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_NAME_FIELD_NUMBER: _ClassVar[int]
    ema_id: str
    vendor_name: _vehicle_state_service_pb2.ChargingVendor
    def __init__(self, ema_id: _Optional[str] = ..., vendor_name: _Optional[_Union[_vehicle_state_service_pb2.ChargingVendor, str]] = ...) -> None: ...

class StopSessionResponse(_message.Message):
    __slots__ = ("response_type",)
    RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    response_type: CommandResponseType
    def __init__(self, response_type: _Optional[_Union[CommandResponseType, str]] = ...) -> None: ...

class GetChargingAccountInfoRequest(_message.Message):
    __slots__ = ("vin",)
    VIN_FIELD_NUMBER: _ClassVar[int]
    vin: str
    def __init__(self, vin: _Optional[str] = ...) -> None: ...

class GetChargingAccountInfoResponse(_message.Message):
    __slots__ = ("charging_account",)
    CHARGING_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    charging_account: _vehicle_state_service_pb2.ChargingAccount
    def __init__(self, charging_account: _Optional[_Union[_vehicle_state_service_pb2.ChargingAccount, _Mapping]] = ...) -> None: ...

class GetChargingAccountInfoV2Response(_message.Message):
    __slots__ = ("charging_account",)
    CHARGING_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    charging_account: _containers.RepeatedCompositeFieldContainer[_vehicle_state_service_pb2.ChargingAccount]
    def __init__(self, charging_account: _Optional[_Iterable[_Union[_vehicle_state_service_pb2.ChargingAccount, _Mapping]]] = ...) -> None: ...

class ListChargingAccountsRequest(_message.Message):
    __slots__ = ("vin",)
    VIN_FIELD_NUMBER: _ClassVar[int]
    vin: str
    def __init__(self, vin: _Optional[str] = ...) -> None: ...

class ListChargingAccountsResponse(_message.Message):
    __slots__ = ("charging_accounts",)
    CHARGING_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    charging_accounts: _containers.RepeatedCompositeFieldContainer[_vehicle_state_service_pb2.ChargingAccount]
    def __init__(self, charging_accounts: _Optional[_Iterable[_Union[_vehicle_state_service_pb2.ChargingAccount, _Mapping]]] = ...) -> None: ...

class GetChargingCustomerInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetChargingCustomerInfoResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

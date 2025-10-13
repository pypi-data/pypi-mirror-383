from pydantic import BaseModel, Field
from typing import Generic, List, Literal, Optional, Type, TypeVar, Union, overload
from uuid import UUID
from maleo.enums.medical import Service as MedicalServiceKey
from maleo.enums.status import (
    DataStatus as DataStatusEnum,
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.general import Order
from maleo.schemas.mixins.identity import (
    DataIdentifier,
    IdentifierTypeValue,
    Ids,
    UUIDs,
    Keys,
    Names,
)
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import LifecycleTimestamp, DataTimestamp
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from maleo.types.integer import OptionalInteger, OptionalListOfIntegers
from maleo.types.string import OptionalListOfStrings, OptionalString
from maleo.types.uuid import OptionalListOfUUIDs
from ..enums.medical_service import IdentifierType
from ..mixins.medical_service import Key, Name
from ..types.medical_service import IdentifierValueType


class CreateData(Name[str], Key, Order[OptionalInteger]):
    pass


class CreateDataMixin(BaseModel):
    data: CreateData = Field(..., description="Create data")


class CreateParameter(
    CreateDataMixin,
):
    pass


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    Names[OptionalListOfStrings],
    Keys[OptionalListOfStrings],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    pass


class ReadSingleParameter(BaseReadSingleParameter[IdentifierType, IdentifierValueType]):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.KEY, IdentifierType.NAME],
        value: str,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            value=value,
            statuses=statuses,
            use_cache=use_cache,
        )


class FullUpdateData(Name[str], Order[OptionalInteger]):
    pass


class PartialUpdateData(Name[OptionalString], Order[OptionalInteger]):
    pass


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    UpdateDataMixin[UpdateDataT],
    IdentifierTypeValue[
        IdentifierType,
        IdentifierValueType,
    ],
    Generic[UpdateDataT],
):
    pass


class StatusUpdateParameter(
    BaseStatusUpdateParameter,
):
    pass


class DeleteSingleParameter(
    BaseDeleteSingleParameter[IdentifierType, IdentifierValueType]
):
    pass


class BaseMedicalServiceSchema(
    Name[str],
    Key,
    Order[OptionalInteger],
):
    pass


class StandardMedicalServiceSchema(
    BaseMedicalServiceSchema,
    DataStatus[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullMedicalServiceSchema(
    BaseMedicalServiceSchema,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


AnyMedicalServiceSchemaType = Union[
    Type[StandardMedicalServiceSchema],
    Type[FullMedicalServiceSchema],
]


AnyMedicalServiceSchema = Union[
    StandardMedicalServiceSchema,
    FullMedicalServiceSchema,
]


MedicalServiceSchemaT = TypeVar("MedicalServiceSchemaT", bound=AnyMedicalServiceSchema)


KeyOrStandardSchema = Union[MedicalServiceKey, StandardMedicalServiceSchema]
KeyOrFullSchema = Union[MedicalServiceKey, FullMedicalServiceSchema]
AnyMedicalService = Union[MedicalServiceKey, AnyMedicalServiceSchema]


MedicalServiceT = TypeVar("MedicalServiceT", bound=AnyMedicalService)


class MedicalServiceMixin(BaseModel, Generic[MedicalServiceT]):
    medical_service: MedicalServiceT = Field(..., description="Medical service")


class OptionalMedicalServiceMixin(BaseModel, Generic[MedicalServiceT]):
    medical_service: Optional[MedicalServiceT] = Field(
        ..., description="Medical service"
    )


class MedicalServicesMixin(BaseModel, Generic[MedicalServiceT]):
    medical_services: List[MedicalServiceT] = Field(..., description="Medical services")


class OptionalMedicalServicesMixin(BaseModel, Generic[MedicalServiceT]):
    medical_services: Optional[List[MedicalServiceT]] = Field(
        ..., description="Medical services"
    )

from pydantic import BaseModel, Field
from typing import Generic, List, Literal, Optional, Type, TypeVar, Union, overload
from uuid import UUID
from maleo.enums.system import Role as SystemRoleKey
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
from ..enums.system_role import IdentifierType
from ..mixins.system_role import Key, Name
from ..types.system_role import IdentifierValueType


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


class BaseSystemRoleSchema(
    Name[str],
    Key,
    Order[OptionalInteger],
):
    pass


class StandardSystemRoleSchema(
    BaseSystemRoleSchema,
    DataStatus[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullSystemRoleSchema(
    BaseSystemRoleSchema,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


AnySystemRoleSchemaType = Union[
    Type[StandardSystemRoleSchema],
    Type[FullSystemRoleSchema],
]


AnySystemRoleSchema = Union[
    StandardSystemRoleSchema,
    FullSystemRoleSchema,
]


SystemRoleSchemaT = TypeVar("SystemRoleSchemaT", bound=AnySystemRoleSchema)


KeyOrStandardSchema = Union[SystemRoleKey, StandardSystemRoleSchema]
KeyOrFullSchema = Union[SystemRoleKey, FullSystemRoleSchema]
AnySystemRole = Union[SystemRoleKey, AnySystemRoleSchema]


SystemRoleT = TypeVar("SystemRoleT", bound=AnySystemRole)


class SystemRoleMixin(BaseModel, Generic[SystemRoleT]):
    system_role: SystemRoleT = Field(..., description="System role")


class OptionalSystemRoleMixin(BaseModel, Generic[SystemRoleT]):
    system_role: Optional[SystemRoleT] = Field(..., description="System role")


class SystemRolesMixin(BaseModel, Generic[SystemRoleT]):
    system_roles: List[SystemRoleT] = Field(..., description="System roles")


class OptionalSystemRolesMixin(BaseModel, Generic[SystemRoleT]):
    system_roles: Optional[List[SystemRoleT]] = Field(..., description="System roles")

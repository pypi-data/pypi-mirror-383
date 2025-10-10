from typing import Literal, overload
from uuid import UUID
from maleo.enums.status import (
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.identity import (
    Ids,
    UUIDs,
    UUIDOrganizationIds,
    UUIDUserIds,
)
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
)
from maleo.types.integer import OptionalListOfIntegers
from maleo.types.uuid import OptionalListOfUUIDs
from ..enums.record_inference import IdentifierType
from ..mixins.record import RecordIds
from ..mixins.inference import InferenceIds
from ..types.record_inference import IdentifierValueType


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    InferenceIds[OptionalListOfUUIDs],
    RecordIds[OptionalListOfUUIDs],
    UUIDUserIds[OptionalListOfUUIDs],
    UUIDOrganizationIds[OptionalListOfUUIDs],
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

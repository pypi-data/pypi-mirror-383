from pydantic import BaseModel, Field
from typing import (
    Annotated,
    Generic,
    Literal,
    Self,
    TypeVar,
    overload,
)
from uuid import UUID, uuid4
from maleo.enums.identity import OptionalGender
from maleo.enums.medical import (
    OptionalService as OptionalMedicalService,
    OptionalListOfServices as OptionalListOfMedicalServices,
)
from maleo.enums.status import (
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.filter import convert as convert_filter
from maleo.schemas.mixins.identity import (
    IdentifierTypeValue,
    Ids,
    UUIDs,
    Name,
    UUIDOrganizationIds,
    UUIDUserIds,
)
from maleo.schemas.mixins.sort import convert as convert_sort
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from maleo.types.datetime import OptionalDate
from maleo.types.dict import StringToAnyDict
from maleo.types.integer import OptionalListOfIntegers
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalListOfUUIDs, OptionalUUID
from ...mixins import MedicalServices
from ..enums.record import IdentifierType
from ..types.record import IdentifierValueType


class CreateParameter(BaseModel):
    record_id: Annotated[UUID, Field(uuid4(), description="Record ID")] = uuid4()
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    medical_service: Annotated[
        OptionalMedicalService, Field(None, description="Medical service")
    ] = None
    name: Annotated[OptionalString, Field(None, description="Name", max_length=200)] = (
        None
    )
    gender: Annotated[OptionalGender, Field(None, description="Gender")] = None
    date_of_birth: Annotated[OptionalDate, Field(None, description="Date of Birth")] = (
        None
    )
    description: Annotated[OptionalString, Field(None, description="Description")] = (
        None
    )
    impression: Annotated[OptionalString, Field(None, description="Impression")] = None
    diagnosis: Annotated[str, Field(..., description="Diagnosis")]
    content_type: Annotated[str, Field(..., description="Content type")]
    image: Annotated[bytes, Field(..., description="Image data")]
    filename: Annotated[str, Field(..., description="File name")]
    inference_ids: Annotated[
        OptionalListOfUUIDs, Field(None, description="Inference's Ids")
    ]

    def to_insert_data(self) -> "InsertData":
        return InsertData.from_create_parameter(self)


class InsertData(BaseModel):
    uuid: Annotated[UUID, Field(uuid4(), description="Record ID")] = uuid4()
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    medical_service: Annotated[
        OptionalMedicalService, Field(None, description="Medical service")
    ] = None
    name: Annotated[OptionalString, Field(None, description="Name", max_length=200)] = (
        None
    )
    gender: Annotated[OptionalGender, Field(None, description="Gender")] = None
    date_of_birth: Annotated[OptionalDate, Field(None, description="Date of Birth")] = (
        None
    )
    description: Annotated[OptionalString, Field(None, description="Description")] = (
        None
    )
    impression: Annotated[OptionalString, Field(None, description="Impression")] = None
    diagnosis: Annotated[str, Field(..., description="Diagnosis")]
    filename: Annotated[str, Field(..., description="File name")]

    @classmethod
    def from_create_parameter(cls, parameters: CreateParameter) -> Self:
        return cls(
            uuid=parameters.record_id,
            organization_id=parameters.organization_id,
            user_id=parameters.user_id,
            name=parameters.name,
            gender=parameters.gender,
            date_of_birth=parameters.date_of_birth,
            description=parameters.description,
            impression=parameters.impression,
            diagnosis=parameters.diagnosis,
            filename=parameters.filename,
        )


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    MedicalServices[OptionalListOfMedicalServices],
    UUIDUserIds[OptionalListOfUUIDs],
    UUIDOrganizationIds[OptionalListOfUUIDs],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "ids",
            "uuids",
            "statuses" "organization_ids",
            "user_ids",
            "medical_services",
            "search",
            "page",
            "limit",
            "use_cache",
        }

    def to_query_params(self) -> StringToAnyDict:
        params = self.model_dump(
            mode="json", include=self._query_param_fields, exclude_none=True
        )
        params["filters"] = convert_filter(self.date_filters)
        params["sorts"] = convert_sort(self.sort_columns)
        params = {k: v for k, v in params.items()}
        return params


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

    def to_query_params(self) -> StringToAnyDict:
        return self.model_dump(
            mode="json", include={"statuses", "use_cache"}, exclude_none=True
        )


class BaseUpdateData(
    Name[OptionalString],
):
    medical_service: Annotated[
        OptionalMedicalService, Field(None, description="Medical service")
    ] = None
    name: Annotated[OptionalString, Field(None, description="Name", max_length=200)] = (
        None
    )
    gender: Annotated[OptionalGender, Field(None, description="Gender")] = None
    date_of_birth: Annotated[OptionalDate, Field(None, description="Date of Birth")] = (
        None
    )
    description: Annotated[OptionalString, Field(None, description="Description")] = (
        None
    )
    impression: Annotated[OptionalString, Field(None, description="Impression")] = None


class FullUpdateData(BaseUpdateData):
    diagnosis: Annotated[str, Field(..., description="Diagnosis")]


class PartialUpdateData(BaseUpdateData):
    diagnosis: Annotated[OptionalString, Field(None, description="Diagnosis")] = None


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

from pydantic import BaseModel, Field
from typing import Annotated, List
from uuid import UUID
from maleo.enums.identity import OptionalGender
from maleo.enums.medical import OptionalService as OptionalMedicalService
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.schemas.mixins.identity import DataIdentifier
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import DataTimestamp
from maleo.types.any import ListOfAny
from maleo.types.datetime import OptionalDate
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalUUID
from .enums.inference import InferenceType


class RecordCoreDTO(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
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
    filename: Annotated[str, Field(..., description="File's name")]


class RecordCoreDTOMixin(BaseModel):
    record: Annotated[RecordCoreDTO, Field(..., description="Record")]


class InferenceCoreDTO(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    type: Annotated[InferenceType, Field(..., description="Inference's type")]
    duration: Annotated[float, Field(0.0, description="Inference's duration")] = 0.0
    output: Annotated[ListOfAny, Field(..., description="Inference's output")]


class InferenceCoreDTOMixin(BaseModel):
    inference: Annotated[InferenceCoreDTO, Field(..., description="Inference")]


class RecordInferenceDTO(
    InferenceCoreDTOMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class RecordInferencesDTOMixin(BaseModel):
    inferences: Annotated[
        List[RecordInferenceDTO],
        Field(list[RecordInferenceDTO](), description="Inferences"),
    ] = list[RecordInferenceDTO]()


class RecordCompleteDTO(RecordInferencesDTOMixin, RecordCoreDTO):
    pass


class InferenceRecordDTO(
    RecordCoreDTOMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class InferenceRecordsDTOMixin(BaseModel):
    records: Annotated[
        List[InferenceRecordDTO],
        Field(list[InferenceRecordDTO](), description="Records"),
    ] = list[InferenceRecordDTO]()


class InferenceCompleteDTO(InferenceRecordsDTOMixin, InferenceCoreDTO):
    pass


class RecordAndInferenceDTO(
    InferenceCoreDTOMixin,
    RecordCoreDTOMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass

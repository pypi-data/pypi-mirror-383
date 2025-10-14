from pydantic import BaseModel, Field, model_validator
from typing import (
    Annotated,
    Generic,
    List,
    Literal,
    Self,
    TypeGuard,
    TypeVar,
    Union,
)
from uuid import UUID
from maleo.enums.identity import OptionalGender
from maleo.enums.medical import OptionalService as OptionalMedicalService
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.schemas.mixins.identity import DataIdentifier
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import DataTimestamp
from maleo.types.datetime import OptionalDate
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalUUID
from ..enums.inference import (
    InferenceType,
    InferenceTypeT,
    MultiFindingClass,
    TuberculosisClass,
)
from .inference import FindingWithoutBox, FindingWithBox, AnyFindingT


class RecordCoreSchema(
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
    url: Annotated[str, Field(..., description="File's URL")]


class RecordCoreSchemaMixin(BaseModel):
    record: Annotated[RecordCoreSchema, Field(..., description="Record")]


class GenericInferenceCoreSchema(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
    Generic[InferenceTypeT, AnyFindingT],
):
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    medical_service: Annotated[
        OptionalMedicalService, Field(None, description="Medical service")
    ] = None
    type: Annotated[InferenceTypeT, Field(..., description="Inference's type")]
    duration: Annotated[float, Field(0.0, description="Inference's duration")] = 0.0
    findings: Annotated[
        List[AnyFindingT],
        Field(default_factory=list[AnyFindingT], description="Findings", min_length=1),
    ] = list[AnyFindingT]()

    @model_validator(mode="after")
    def validate_findings(self) -> Self:
        if self.type is InferenceType.MULTI_FINDING:
            for index, finding in enumerate(self.findings):
                if finding.name not in MultiFindingClass.choices():
                    raise ValueError(
                        f"Invalid finding's name for {InferenceType.MULTI_FINDING} inference",
                        f"Received: {finding.name}",
                        f"Expected: [{MultiFindingClass.choices()}]",
                    )
                if finding.box is None:
                    raise ValueError(
                        f"Attribute 'box' can not be None for {InferenceType.MULTI_FINDING} inference",
                        f"index: {index}, id: {finding.id}, name: {finding.name}",
                    )
        elif self.type is InferenceType.TUBERCULOSIS:
            if len(self.findings) != 1:
                raise ValueError(
                    f"{InferenceType.TUBERCULOSIS} inference can only have one finding"
                )
            for index, finding in enumerate(self.findings):
                if finding.name not in TuberculosisClass.choices():
                    raise ValueError(
                        f"Invalid finding's name for {InferenceType.TUBERCULOSIS} inference",
                        f"Received: {finding.name}",
                        f"Expected: [{TuberculosisClass.choices()}]",
                    )
                if finding.box is not None:
                    raise ValueError(
                        f"Attribute 'box' must be None for {InferenceType.TUBERCULOSIS} inference",
                        f"index: {index}, id: {finding.id}, name: {finding.name}",
                    )
        return self


class MultiFindingInferenceCoreSchema(
    GenericInferenceCoreSchema[Literal[InferenceType.MULTI_FINDING], FindingWithBox]
):
    pass


class TuberculosisInferenceCoreSchema(
    GenericInferenceCoreSchema[Literal[InferenceType.TUBERCULOSIS], FindingWithoutBox]
):
    pass


AnyInferenceCoreSchema = Union[
    MultiFindingInferenceCoreSchema, TuberculosisInferenceCoreSchema
]


def is_multi_finding_core_schema(
    schema: AnyInferenceCoreSchema,
) -> TypeGuard[MultiFindingInferenceCoreSchema]:
    return schema.type is InferenceType.MULTI_FINDING and all(
        [isinstance(finding, FindingWithBox) for finding in schema.findings]
    )


def is_tuberculosis_core_schema(
    schema: AnyInferenceCoreSchema,
) -> TypeGuard[TuberculosisInferenceCoreSchema]:
    return (
        schema.type is InferenceType.TUBERCULOSIS
        and len(schema.findings) == 1
        and all([isinstance(finding, FindingWithBox) for finding in schema.findings])
    )


AnyInferenceCoreSchemaT = TypeVar(
    "AnyInferenceCoreSchemaT", bound=AnyInferenceCoreSchema
)


class InferenceCoreSchemaMixin(BaseModel, Generic[AnyInferenceCoreSchemaT]):
    inference: Annotated[AnyInferenceCoreSchemaT, Field(..., description="Inference")]


class RecordInferenceSchema(
    InferenceCoreSchemaMixin[AnyInferenceCoreSchema],
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class RecordInferencesSchemaMixin(BaseModel):
    inferences: Annotated[
        List[RecordInferenceSchema],
        Field(default_factory=list[RecordInferenceSchema], description="Inferences"),
    ] = list[RecordInferenceSchema]()


class RecordCompleteSchema(RecordInferencesSchemaMixin, RecordCoreSchema):
    pass


class InferenceRecordSchema(
    RecordCoreSchemaMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class InferenceRecordsSchemaMixin(BaseModel):
    records: Annotated[
        List[InferenceRecordSchema],
        Field(default_factory=list[InferenceRecordSchema], description="Records"),
    ] = list[InferenceRecordSchema]()


class GenericInferenceCompleteSchema(
    InferenceRecordsSchemaMixin,
    GenericInferenceCoreSchema[InferenceTypeT, AnyFindingT],
    Generic[InferenceTypeT, AnyFindingT],
):
    pass


class MultiFindingInferenceCompleteSchema(
    GenericInferenceCompleteSchema[Literal[InferenceType.MULTI_FINDING], FindingWithBox]
):
    pass


class TuberculosisInferenceCompleteSchema(
    GenericInferenceCompleteSchema[
        Literal[InferenceType.TUBERCULOSIS], FindingWithoutBox
    ]
):
    pass


AnyInferenceCompleteSchema = Union[
    MultiFindingInferenceCompleteSchema, TuberculosisInferenceCompleteSchema
]


def is_multi_finding_complete_schema(
    schema: AnyInferenceCompleteSchema,
) -> TypeGuard[MultiFindingInferenceCompleteSchema]:
    return schema.type is InferenceType.MULTI_FINDING and all(
        [isinstance(finding, FindingWithBox) for finding in schema.findings]
    )


def is_tuberculosis_complete_schema(
    schema: AnyInferenceCompleteSchema,
) -> TypeGuard[TuberculosisInferenceCompleteSchema]:
    return (
        schema.type is InferenceType.TUBERCULOSIS
        and len(schema.findings) == 1
        and all([isinstance(finding, FindingWithBox) for finding in schema.findings])
    )


class RecordAndInferenceSchema(
    InferenceCoreSchemaMixin[AnyInferenceCoreSchema],
    RecordCoreSchemaMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass

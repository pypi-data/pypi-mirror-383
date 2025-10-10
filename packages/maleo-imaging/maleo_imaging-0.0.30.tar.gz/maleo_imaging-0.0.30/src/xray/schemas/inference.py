from pydantic import BaseModel, Field
from typing import (
    Annotated,
    Any,
    Generic,
    Literal,
    Optional,
    Self,
    TypeVar,
    Union,
    overload,
)
from uuid import UUID, uuid4
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
from maleo.types.any import ListOfAny
from maleo.types.integer import OptionalListOfIntegers
from maleo.types.misc import StringOrStringEnum
from maleo.types.uuid import OptionalListOfUUIDs, OptionalUUID
from ..enums.inference import (
    IdentifierType,
    InferenceType,
    InferenceTypeT,
    OptionalListOfInferenceTypes,
)
from ..mixins.inference import InferenceTypes
from ..types.inference import IdentifierValueType


class BoundingBox(BaseModel):
    x_min: Annotated[float, Field(0.0, description="X Min", ge=0.0)]
    y_min: Annotated[float, Field(0.0, description="Y Min", ge=0.0)]
    x_max: Annotated[float, Field(0.0, description="X Max", ge=0.0)]
    y_max: Annotated[float, Field(0.0, description="Y Max", ge=0.0)]


OptionalBoundingBox = Optional[BoundingBox]
OptionalBoundingBoxT = TypeVar("OptionalBoundingBoxT", bound=OptionalBoundingBox)


class Finding(BaseModel, Generic[OptionalBoundingBoxT]):
    id: Annotated[int, Field(..., description="Finding's ID")]
    name: Annotated[StringOrStringEnum, Field(..., description="Finding's Name")]
    confidence: Annotated[float, Field(..., description="Confidence", ge=0.0, le=1.0)]
    box: Annotated[OptionalBoundingBoxT, Field(..., description="Bounding Box")]


class FindingWithoutBox(Finding[None]):
    pass


class FindingWithBox(Finding[BoundingBox]):
    pass


AnyFinding = Union[FindingWithoutBox, FindingWithBox]
AnyFindingT = TypeVar("AnyFindingT", bound=AnyFinding)
OptionalAnyFinding = Optional[AnyFinding]
OptionalAnyFindingT = TypeVar("OptionalAnyFindingT", bound=OptionalAnyFinding)


class GenericPredictParameter(BaseModel, Generic[InferenceTypeT]):
    inference_id: Annotated[
        UUID, Field(default_factory=uuid4, description="Inference ID")
    ]
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    inference_type: Annotated[
        InferenceTypeT, Field(..., description="Inference's type")
    ]
    content_type: Annotated[str, Field(..., description="Content type")]
    image: Annotated[bytes, Field(..., description="Image data")]
    filename: Annotated[str, Field(..., description="File name")]


class BasePredictParameter(GenericPredictParameter[InferenceType]):
    inference_type: Annotated[InferenceType, Field(..., description="Inference's type")]


class MultiFindingPredictParameter(
    GenericPredictParameter[Literal[InferenceType.MULTI_FINDING]]
):
    inference_type: Annotated[
        Literal[InferenceType.MULTI_FINDING],
        Field(InferenceType.MULTI_FINDING, description="Inference's type"),
    ] = InferenceType.MULTI_FINDING


class TuberculosisPredictParameter(
    GenericPredictParameter[Literal[InferenceType.TUBERCULOSIS]]
):
    inference_type: Annotated[
        Literal[InferenceType.TUBERCULOSIS],
        Field(InferenceType.TUBERCULOSIS, description="Inference's type"),
    ] = InferenceType.TUBERCULOSIS


AnyPredictParameter = Union[
    BasePredictParameter, MultiFindingPredictParameter, TuberculosisPredictParameter
]


class GenericCreateParameter(BaseModel, Generic[InferenceTypeT]):
    uuid: Annotated[UUID, Field(default_factory=uuid4, description="Inference ID")]
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    type: Annotated[InferenceTypeT, Field(..., description="Inference's type")]
    filename: Annotated[str, Field(..., description="File name")]
    duration: Annotated[float, Field(0.0, description="Inference's duration")] = 0.0
    output: Annotated[
        ListOfAny,
        Field(default_factory=list[Any], description="Inference's output"),
    ] = list[Any]()

    @classmethod
    def from_predict_parameter(
        cls,
        parameters: GenericPredictParameter[InferenceTypeT],
        duration: float,
        output: ListOfAny,
    ) -> Self:
        return cls(
            uuid=parameters.inference_id,
            organization_id=parameters.organization_id,
            user_id=parameters.user_id,
            type=parameters.inference_type,
            duration=duration,
            filename=parameters.filename,
            output=output,
        )


class BaseCreateParameter(GenericCreateParameter[InferenceType]):
    type: Annotated[InferenceType, Field(..., description="Inference's type")]


class MultiFindingCreateParameter(
    GenericCreateParameter[Literal[InferenceType.MULTI_FINDING]]
):
    type: Annotated[
        Literal[InferenceType.MULTI_FINDING],
        Field(InferenceType.MULTI_FINDING, description="Inference's type"),
    ] = InferenceType.MULTI_FINDING


class TuberculosisCreateParameter(
    GenericCreateParameter[Literal[InferenceType.TUBERCULOSIS]]
):
    type: Annotated[
        Literal[InferenceType.TUBERCULOSIS],
        Field(InferenceType.TUBERCULOSIS, description="Inference's type"),
    ] = InferenceType.TUBERCULOSIS


AnyCreateParameter = Union[
    BaseCreateParameter, MultiFindingCreateParameter, TuberculosisCreateParameter
]


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    InferenceTypes[OptionalListOfInferenceTypes],
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

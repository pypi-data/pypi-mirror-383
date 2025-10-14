from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import (
    Date,
    Enum,
    Float,
    Integer,
    String,
    Text,
    UUID as SQLAlchemyUUID,
)
from uuid import UUID
from maleo.enums.identity import Gender, OptionalGender
from maleo.enums.medical import (
    Service as MedicalService,
    OptionalService as OptionalMedicalService,
)
from maleo.schemas.model import DataIdentifier, DataStatus, DataTimestamp
from maleo.types.any import ListOfAny
from maleo.types.datetime import OptionalDate
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalUUID
from .enums.inference import InferenceType


class Record(DataTimestamp, DataStatus, DataIdentifier):
    __tablename__ = "xray_records"
    organization_id: Mapped[OptionalUUID] = mapped_column(
        name="organization_id", type_=SQLAlchemyUUID
    )
    user_id: Mapped[UUID] = mapped_column(
        name="user_id", type_=SQLAlchemyUUID, nullable=False
    )
    medical_service: Mapped[OptionalMedicalService] = mapped_column(
        name="medical_service", type_=Enum(MedicalService, name="medical_service")
    )
    name: Mapped[OptionalString] = mapped_column(name="name", type_=String(200))
    gender: Mapped[OptionalGender] = mapped_column(
        name="gender", type_=Enum(Gender, name="gender")
    )
    date_of_birth: Mapped[OptionalDate] = mapped_column(
        name="date_of_birth", type_=Date
    )
    description: Mapped[OptionalString] = mapped_column(name="description", type_=Text)
    impression: Mapped[OptionalString] = mapped_column(name="impression", type_=Text)
    diagnosis: Mapped[str] = mapped_column(name="diagnosis", type_=Text, nullable=False)
    filename: Mapped[str] = mapped_column(name="filename", type_=Text, nullable=False)


class Inference(DataTimestamp, DataStatus, DataIdentifier):
    __tablename__ = "xray_inferences"
    organization_id: Mapped[OptionalUUID] = mapped_column(
        name="organization_id", type_=SQLAlchemyUUID
    )
    user_id: Mapped[UUID] = mapped_column(
        name="user_id", type_=SQLAlchemyUUID, nullable=False
    )
    medical_service: Mapped[OptionalMedicalService] = mapped_column(
        name="medical_service", type_=Enum(MedicalService, name="medical_service")
    )
    type: Mapped[InferenceType] = mapped_column(
        name="type", type_=Enum(InferenceType, name="xray_inference_type")
    )
    filename: Mapped[str] = mapped_column(name="filename", type_=Text, nullable=False)
    duration: Mapped[float] = mapped_column(
        name="duration", type_=Float, nullable=False
    )
    output: Mapped[ListOfAny] = mapped_column(
        name="output", type_=JSONB, nullable=False
    )


class RecordAndInference(DataTimestamp, DataStatus, DataIdentifier):
    __tablename__ = "xray_record_inferences"
    record_id: Mapped[int] = mapped_column(
        "record_id",
        Integer,
        ForeignKey("xray_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    inference_id: Mapped[int] = mapped_column(
        "inference_id",
        Integer,
        ForeignKey("xray_inferences.id", ondelete="CASCADE"),
        nullable=False,
    )

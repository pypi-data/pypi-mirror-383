from pydantic import BaseModel, Field
from typing import Annotated, Generic
from maleo.enums.medical import (
    OptionalListOfServicesT as OptionalListOfMedicalServicesT,
)


class MedicalServices(BaseModel, Generic[OptionalListOfMedicalServicesT]):
    medical_service: Annotated[
        OptionalListOfMedicalServicesT, Field(..., description="Medical service")
    ]

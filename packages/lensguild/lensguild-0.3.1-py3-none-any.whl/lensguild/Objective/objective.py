from enum import Enum
from dataclasses import dataclass,field
from allytools.units.length import Length
from allytools.units.angle import Angle
from Sensor.sensor_type import SensorFormats
from Filter import OpticalFilter
from typing import Optional
from pathlib import Path

class ObjectiveBrand(Enum):
    Sunex = 'Sunex'
    Commonlands = 'Commonlands'

@dataclass(frozen=True)
class ObjectiveID:
    brand: ObjectiveBrand
    model: str
    def __repr__(self):
        return f"{self.brand.value} {self.model}"
    def key(self) -> str:
        return f"{self.brand.value}/{self.model}"

@dataclass(frozen=True)
class Objective:
    objectiveID: ObjectiveID
    EFL: Length
    image_format:SensorFormats
    f_number:float
    max_fov:Angle
    max_image_circle:Length
    max_CRA: Angle
    _zmx_file: Optional[Path] = field(default=None, repr=False)
    filter: OpticalFilter | None = None

    def __post_init__(self):
        if not isinstance(self.EFL, Length):
            raise TypeError("EFL must be a Length instance.")
        if not isinstance(self.max_fov, Angle):
            raise TypeError("max_fov must be an Angle instance.")
        if not isinstance(self.max_image_circle, Length):
            raise TypeError("max_image_circle must be a Length instance.")
        if not isinstance(self.max_CRA, Angle):
            raise TypeError("max_CRA must be an Angle instance.")
        if not isinstance(self.image_format, SensorFormats):
            raise TypeError("image_format must be a SensorType enum member.")
        if not isinstance(self.f_number, (int, float)) or self.f_number <= 0:
            raise ValueError("f_number must be a positive number.")
        if self.filter is not None and not isinstance(self.filter, OpticalFilter):
            raise TypeError("filter must be an OpticalFilter instance or None.")
        if self._zmx_file is not None and not isinstance(self._zmx_file, Path):
            object.__setattr__(self, "_zmx_file", Path(self._zmx_file))

    @property
    def zmx_file(self) -> Path:
        if self._zmx_file is None:
            raise AttributeError(f"{self!r} zmx_file is  None.")
        return self._zmx_file

    def __repr__(self):
        return f"{self.objectiveID.brand.value} {self.objectiveID.model}"

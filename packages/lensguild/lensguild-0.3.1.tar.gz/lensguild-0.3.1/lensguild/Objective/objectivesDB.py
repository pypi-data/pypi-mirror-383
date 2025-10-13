from typing import Final
from pathlib import  Path
from allytools.units.length import LengthUnit, Length
from allytools.units.angle import Angle
from allytools.units.angle_unit import AngleUnit
from allytools.types.FrozenDB import FrozenDB
from Sensor.sensor_type import SensorFormats
from Objective import Objective, ObjectiveID, ObjectiveBrand

class ObjectivesDB (metaclass=FrozenDB):
    __slots__ = ()
    DSL935_F3_0_NIR: Final[Objective] = Objective(
        objectiveID=ObjectiveID(ObjectiveBrand.Sunex, "DSL935"),
        EFL=Length(9.6, LengthUnit.MM),
        image_format=SensorFormats.S_1_1_8,
        f_number=3.0,
        max_fov=Angle.from_value(51.0, AngleUnit.DEG),
        max_image_circle=Length(8.8, LengthUnit.MM),
        max_CRA=Angle.from_value(13.0, AngleUnit.DEG),
        filter=None)

    CIL085_F4_4_M12BNIR: Final[Objective] = Objective(
        objectiveID=ObjectiveID(ObjectiveBrand.Commonlands, "CIL085-F4.4-M12BNIR"),
        EFL=Length(8.2, LengthUnit.MM),
        image_format=SensorFormats.S_1_1_8,
        f_number=4.4,
        max_fov=Angle.from_value(150.0, AngleUnit.DEG),
        max_image_circle=Length(6.4, LengthUnit.MM),
        max_CRA=Angle.from_value(28.0, AngleUnit.DEG),
        _zmx_file=Path(r"Catalog\Commanlands\CIL085_F4.4_reverse.zmx"),
        filter=None)


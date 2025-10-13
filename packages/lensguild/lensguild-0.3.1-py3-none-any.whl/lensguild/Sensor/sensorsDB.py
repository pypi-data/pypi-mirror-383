from typing import  Final
from Sensor.sensor import Sensor
from Sensor.sensor_type import SensorType, SensorFormats
from Sensor.pixel import Pixel
from Sensor.bit_depth import BitDepth, BitDepthOptions
from allytools import FrozenDB, Percentage, Length, LengthUnit


class SensorsDB(metaclass=FrozenDB):
    __slots__ = ()
    SONY_IMX547: Final[Sensor] = Sensor(2448, 2048, Pixel(Length(2.74, LengthUnit.UM),Percentage(100)), BitDepth(BitDepthOptions.BD_12), SensorFormats.S_1_2_3, SensorType.CMOS),
    SONY_IMX174: Final[Sensor] = Sensor(1936, 1216, Pixel(Length(5.86, LengthUnit.UM),Percentage(100)), BitDepth(BitDepthOptions.BD_12), SensorFormats.S_1_2, SensorType.CMOS)
    SONY_IMX900: Final[Sensor] = Sensor(2048, 1536, Pixel(Length(2.25, LengthUnit.UM),Percentage(100)), BitDepth(BitDepthOptions.BD_12), SensorFormats.S_1_3_1, SensorType.CMOS)
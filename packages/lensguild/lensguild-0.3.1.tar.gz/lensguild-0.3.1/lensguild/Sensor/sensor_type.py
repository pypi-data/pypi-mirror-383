from enum import Enum
from dataclasses import dataclass
from allytools.units.length import LengthUnit, Length


class SensorType(Enum):
    CMOS = "CMOS"
    CCD = "CCD"
    EMCCD = "Electron-Multiplying CCD"
    sCMOS = "Scientific CMOS"


@dataclass(frozen=True)
class SensorFormat:
    label: str
    width: Length
    height: Length
    diagonal: Length
    def __str__(self) -> str:
        return (f"{self.label} "
                f"({self.width.value_mm:.2f}×{self.height.value_mm:.2f} mm, "
                f"diagonal {self.diagonal.value_mm:.2f} mm)")
    def __repr__(self) -> str:
        return (f"SensorFormat(label='{self.label}', "
                f"width={self.width}, height={self.height}, "
                f"diagonal={self.diagonal})")

class SensorFormats(Enum):
    S_1_3_1 = SensorFormat("1/3.09\"",  width=Length(4.66, LengthUnit.MM),height=Length(3.5, LengthUnit.MM),    diagonal=Length(5.82, LengthUnit.MM))
    S_1_3   = SensorFormat("1/3\"",     width=Length(4.8, LengthUnit.MM), height=Length(3.6, LengthUnit.MM),    diagonal=Length(6.0, LengthUnit.MM))
    S_1_2_7 = SensorFormat("1/2.7\"",   width=Length(5.3, LengthUnit.MM), height=Length(4.0, LengthUnit.MM),    diagonal=Length(6.6, LengthUnit.MM))
    S_1_2_5 = SensorFormat("1/2.5\"",   width=Length(5.8, LengthUnit.MM), height=Length(4.3, LengthUnit.MM),    diagonal=Length(7.2, LengthUnit.MM))
    S_1_2_3 = SensorFormat("1/2.3\"",   width=Length(6.17, LengthUnit.MM),height=Length(4.55, LengthUnit.MM),   diagonal=Length(7.70, LengthUnit.MM))
    S_1_2   = SensorFormat("1/2\"",     width=Length(6.4, LengthUnit.MM), height=Length(4.8, LengthUnit.MM),    diagonal=Length(8.0, LengthUnit.MM))
    S_1_1_8 = SensorFormat("1/1.8\"",   width=Length(7.18, LengthUnit.MM),height=Length(5.32, LengthUnit.MM),   diagonal=Length(8.93, LengthUnit.MM))
    S_1_1_7 = SensorFormat("1/1.7\"",   width=Length(7.6, LengthUnit.MM), height=Length(5.7, LengthUnit.MM),    diagonal=Length(9.5, LengthUnit.MM))
    S_2_3   = SensorFormat("2/3\"",     width=Length(8.8, LengthUnit.MM), height=Length(6.6, LengthUnit.MM),    diagonal=Length(11.0, LengthUnit.MM))
    S_1     = SensorFormat("1\"",       width=Length(12.8, LengthUnit.MM),height=Length(9.6, LengthUnit.MM),    diagonal=Length(16.0, LengthUnit.MM))
    S_APS_C = SensorFormat("APS-C",     width=Length(23.6, LengthUnit.MM),height=Length(15.7, LengthUnit.MM),   diagonal=Length(28.2, LengthUnit.MM))
    S_4_3   = SensorFormat("4/3\"",     width=Length(17.3, LengthUnit.MM),height=Length(13.0, LengthUnit.MM),   diagonal=Length(21.6, LengthUnit.MM))
    S_FULL  = SensorFormat("Full Frame",width=Length(36.0, LengthUnit.MM),height=Length(24.0, LengthUnit.MM),   diagonal=Length(43.3, LengthUnit.MM))

    def __str__(self):
        return self.value.label

    @property
    def format(self) -> SensorFormat:
        return self.value

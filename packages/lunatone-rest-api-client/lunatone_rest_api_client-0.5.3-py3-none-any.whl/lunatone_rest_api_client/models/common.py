from enum import IntEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat

StatusT = TypeVar("StatusT")
ColorT = TypeVar("ColorT")


class Status(BaseModel, Generic[StatusT]):
    status: StatusT


class FadeTime(BaseModel):
    fade_time: NonNegativeFloat = Field(alias="fadeTime")


class DimmableWithFadeTime(FadeTime):
    """Data model for the ``dimmableWithFade`` feature."""

    dim_value: NonNegativeFloat = Field(alias="dimValue", ge=0.0, le=100.0)


class ColorWithFadeTime(FadeTime, Generic[ColorT]):
    """Data model for color features with fade time."""

    color: ColorT


class ColorRGBData(BaseModel):
    """Data model for the ``colorRGB`` feature."""

    red: float | None = Field(
        None,
        description="Relative red value in the [0, 1] interval.",
        alias="r",
        ge=0.0,
        le=1.0,
    )
    green: float | None = Field(
        None,
        description="Relative green value in the [0, 1] interval.",
        alias="g",
        ge=0.0,
        le=1.0,
    )
    blue: float | None = Field(
        None,
        description="Relative blue value in the [0, 1] interval.",
        alias="b",
        ge=0.0,
        le=1.0,
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"r": 0.0, "g": 0.5, "b": 1.0}]}
    )


class DimmableRGBData(ColorRGBData):
    """Data model for the ``dimmableRGB`` feature."""

    dimmable: float = Field(
        50.0,
        description="Percentage in the [0, 100] interval to dim a device to.",
        ge=0.0,
        le=100.0,
    )


class ColorWAFData(BaseModel):
    """Data model for the ``colorWAF`` feature."""

    white: float | None = Field(
        None,
        description="Relative white value in the [0, 1] interval.",
        alias="w",
        ge=0.0,
        le=1.0,
    )
    amber: float | None = Field(
        None,
        description="Relative amber value in the [0, 1] interval.",
        alias="a",
        ge=0.0,
        le=1.0,
    )
    free_color: float | None = Field(
        None,
        description="Relative free color value in the [0, 1] interval.",
        alias="f",
        ge=0.0,
        le=1.0,
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"w": 0.0, "a": 0.5, "f": 1.0}]}
    )


class DimmableWAFData(ColorWAFData):
    """Data model for the ``dimmableWAF`` feature."""

    dimmable: float = Field(
        50.0,
        description="Percentage in the [0, 100] interval to dim a device to.",
        ge=0.0,
        le=100.0,
    )


class DimmableKelvinData(BaseModel):
    """Data model for the ``dimmableKelvin`` feature."""

    dimmable: float = Field(
        50.0,
        description="Percentage in the [0, 100] interval to dim a device to.",
        ge=0.0,
        le=100.0,
    )
    kelvin: NonNegativeFloat = Field(4000.0, description="Color temperature in Kelvin.")


class ColorXYData(BaseModel):
    """Data model for the ``colorXY`` feature."""

    x: float | None = Field(
        None,
        description="X coordinate in the CIE color chromaticity space.",
    )
    y: float | None = Field(
        None,
        description="Y coordinate in the CIE color chromaticity space.",
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"x": 0.432, "y": 0.150}]}
    )


class DimmableXYData(ColorXYData):
    """Data model for the ``dimmableXY`` feature."""

    dimmable: float = Field(
        50.0,
        description="Percentage in the [0, 100] interval to dim a device to.",
        ge=0.0,
        le=100.0,
    )


class TimeSignature(BaseModel):
    timestamp: float
    counter: int


class FeaturesStatus(BaseModel):
    """Data model for the features status."""

    switchable: Status[bool] | None = None
    dimmable: Status[float] | None = None
    dimmable_with_fade: Status[DimmableWithFadeTime] | None = Field(
        None, alias="dimmableWithFade"
    )
    dim_up: bool | None = Field(None, alias="dimUp")
    dim_down: bool | None = Field(None, alias="dimDown")
    scene: bool | None = None
    scene_with_fade: Status[FadeTime] | None = Field(None, alias="sceneWithFade")
    goto_last_active: dict | None = Field(None, alias="gotoLastActive")
    goto_last_active_with_fade: Status[FadeTime] | None = Field(
        None, alias="gotoLastActiveWithFade"
    )
    dali_cmd16: bool | None = Field(None, alias="daliCmd16")
    fade_time: Status[float] | None = Field(None, alias="fadeTime")
    fade_rate: Status[float] | None = Field(None, alias="fadeRate")
    save_to_scene: bool | None = Field(None, alias="saveToScene")
    color_rgb: Status[ColorRGBData] | None = Field(None, alias="colorRGB")
    dimmable_rgb: Status[DimmableRGBData] | None = Field(None, alias="dimmableRGB")
    color_rgb_with_fade: Status[ColorWithFadeTime[ColorRGBData]] | None = Field(
        None, alias="colorRGBWithFade"
    )
    color_waf: Status[ColorWAFData] | None = Field(None, alias="colorWAF")
    dimmable_waf: Status[DimmableWAFData] | None = Field(None, alias="dimmableWAF")
    color_waf_with_fade: Status[ColorWithFadeTime[ColorWAFData]] | None = Field(
        None, alias="colorWAFWithFade"
    )
    color_kelvin: Status[NonNegativeFloat] | None = Field(None, alias="colorKelvin")
    dimmable_kelvin: Status[DimmableKelvinData] | None = Field(
        None, alias="dimmableKelvin"
    )
    color_kelvin_with_fade: Status[ColorWithFadeTime[NonNegativeFloat]] | None = Field(
        None, alias="colorKelvinWithFade"
    )
    color_xy: Status[ColorXYData] | None = Field(None, alias="colorXY")
    dimmable_xy: Status[DimmableXYData] | None = Field(None, alias="dimmableXY")
    color_xy_with_fade: Status[ColorWithFadeTime[ColorXYData | dict]] | None = Field(
        None, alias="colorXYWithFade"
    )


class DALIType(IntEnum):
    """DALI device types."""

    DT0_FLUORESCENT_LAMPS = 0
    DT1_EMERGENCY_LIGHTING = 1
    DT2_DISCHARGE_LAMPS = 2
    DT3_LOW_VOLTAGE_HALOGEN_LAMPS = 3
    DT4_SUPPLY_VOLTAGE_CONTROLLER = 4
    DT5_CONVERSION_FROM_DIGITAL_SIGNAL_INTO_DC_VOLTAGE = 5
    DT6_LED_MODULES = 6
    DT7_SWITCHING_FUNCTION = 7
    DT8_COLOUR_CONTROL = 8
    DT9_SEQUENCER = 9

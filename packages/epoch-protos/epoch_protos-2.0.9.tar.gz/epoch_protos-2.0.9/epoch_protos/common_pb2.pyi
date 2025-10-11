from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EpochFolioDashboardWidget(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WidgetUnspecified: _ClassVar[EpochFolioDashboardWidget]
    WidgetCard: _ClassVar[EpochFolioDashboardWidget]
    WidgetLines: _ClassVar[EpochFolioDashboardWidget]
    WidgetBar: _ClassVar[EpochFolioDashboardWidget]
    WidgetDataTable: _ClassVar[EpochFolioDashboardWidget]
    WidgetXRange: _ClassVar[EpochFolioDashboardWidget]
    WidgetHistogram: _ClassVar[EpochFolioDashboardWidget]
    WidgetPie: _ClassVar[EpochFolioDashboardWidget]
    WidgetHeatMap: _ClassVar[EpochFolioDashboardWidget]
    WidgetBoxPlot: _ClassVar[EpochFolioDashboardWidget]
    WidgetArea: _ClassVar[EpochFolioDashboardWidget]
    WidgetColumn: _ClassVar[EpochFolioDashboardWidget]

class EpochFolioType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TypeUnspecified: _ClassVar[EpochFolioType]
    TypeString: _ClassVar[EpochFolioType]
    TypeInteger: _ClassVar[EpochFolioType]
    TypeDecimal: _ClassVar[EpochFolioType]
    TypePercent: _ClassVar[EpochFolioType]
    TypeBoolean: _ClassVar[EpochFolioType]
    TypeDateTime: _ClassVar[EpochFolioType]
    TypeDate: _ClassVar[EpochFolioType]
    TypeDayDuration: _ClassVar[EpochFolioType]
    TypeMonetary: _ClassVar[EpochFolioType]
    TypeDuration: _ClassVar[EpochFolioType]

class NullValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NULL_VALUE: _ClassVar[NullValue]

class AxisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AxisUnspecified: _ClassVar[AxisType]
    AxisLinear: _ClassVar[AxisType]
    AxisLogarithmic: _ClassVar[AxisType]
    AxisDateTime: _ClassVar[AxisType]
    AxisCategory: _ClassVar[AxisType]

class DashStyle(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DashStyleUnspecified: _ClassVar[DashStyle]
    Solid: _ClassVar[DashStyle]
    ShortDash: _ClassVar[DashStyle]
    ShortDot: _ClassVar[DashStyle]
    ShortDashDot: _ClassVar[DashStyle]
    ShortDashDotDot: _ClassVar[DashStyle]
    Dot: _ClassVar[DashStyle]
    Dash: _ClassVar[DashStyle]
    LongDash: _ClassVar[DashStyle]
    DashDot: _ClassVar[DashStyle]
    LongDashDot: _ClassVar[DashStyle]
    LongDashDotDot: _ClassVar[DashStyle]
WidgetUnspecified: EpochFolioDashboardWidget
WidgetCard: EpochFolioDashboardWidget
WidgetLines: EpochFolioDashboardWidget
WidgetBar: EpochFolioDashboardWidget
WidgetDataTable: EpochFolioDashboardWidget
WidgetXRange: EpochFolioDashboardWidget
WidgetHistogram: EpochFolioDashboardWidget
WidgetPie: EpochFolioDashboardWidget
WidgetHeatMap: EpochFolioDashboardWidget
WidgetBoxPlot: EpochFolioDashboardWidget
WidgetArea: EpochFolioDashboardWidget
WidgetColumn: EpochFolioDashboardWidget
TypeUnspecified: EpochFolioType
TypeString: EpochFolioType
TypeInteger: EpochFolioType
TypeDecimal: EpochFolioType
TypePercent: EpochFolioType
TypeBoolean: EpochFolioType
TypeDateTime: EpochFolioType
TypeDate: EpochFolioType
TypeDayDuration: EpochFolioType
TypeMonetary: EpochFolioType
TypeDuration: EpochFolioType
NULL_VALUE: NullValue
AxisUnspecified: AxisType
AxisLinear: AxisType
AxisLogarithmic: AxisType
AxisDateTime: AxisType
AxisCategory: AxisType
DashStyleUnspecified: DashStyle
Solid: DashStyle
ShortDash: DashStyle
ShortDot: DashStyle
ShortDashDot: DashStyle
ShortDashDotDot: DashStyle
Dot: DashStyle
Dash: DashStyle
LongDash: DashStyle
DashDot: DashStyle
LongDashDot: DashStyle
LongDashDotDot: DashStyle

class Scalar(_message.Message):
    __slots__ = ("string_value", "integer_value", "decimal_value", "percent_value", "boolean_value", "timestamp_ms", "date_value", "day_duration", "monetary_value", "duration_ms", "null_value")
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    DECIMAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    PERCENT_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOLEAN_VALUE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    DATE_VALUE_FIELD_NUMBER: _ClassVar[int]
    DAY_DURATION_FIELD_NUMBER: _ClassVar[int]
    MONETARY_VALUE_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    integer_value: int
    decimal_value: float
    percent_value: float
    boolean_value: bool
    timestamp_ms: int
    date_value: int
    day_duration: int
    monetary_value: float
    duration_ms: int
    null_value: NullValue
    def __init__(self, string_value: _Optional[str] = ..., integer_value: _Optional[int] = ..., decimal_value: _Optional[float] = ..., percent_value: _Optional[float] = ..., boolean_value: bool = ..., timestamp_ms: _Optional[int] = ..., date_value: _Optional[int] = ..., day_duration: _Optional[int] = ..., monetary_value: _Optional[float] = ..., duration_ms: _Optional[int] = ..., null_value: _Optional[_Union[NullValue, str]] = ...) -> None: ...

class Array(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[Scalar]
    def __init__(self, values: _Optional[_Iterable[_Union[Scalar, _Mapping]]] = ...) -> None: ...

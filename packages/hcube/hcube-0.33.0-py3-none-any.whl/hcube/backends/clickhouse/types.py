from hcube.api.models.dimensions import (
    BooleanDimension,
    DateDimension,
    DateTimeDimension,
    IntDimension,
    IPv4Dimension,
    IPv6Dimension,
    StringDimension,
)
from hcube.api.models.metrics import FloatMetric, IntMetric

DIMENSION_TYPE_MAP = {
    IntDimension: "Int",
    StringDimension: "String",
    DateDimension: "Date",
    DateTimeDimension: "DateTime64",
    FloatMetric: "Float",
    IntMetric: "Int",
    IPv4Dimension: "IPv4",
    IPv6Dimension: "IPv6",
    BooleanDimension: "Bool",
}

TYPE_TO_DIMENSION = {t: d for d, t in DIMENSION_TYPE_MAP.items()}

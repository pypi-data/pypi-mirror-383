import hashlib
import json
from dataclasses import dataclass
from typing import List, Optional, Union

from hcube.api.models.cube import Cube
from hcube.api.models.dimensions import (
    Dimension,
    IntDimension,
    StringDimension,
)
from hcube.backends.clickhouse.data_sources import DataSource
from hcube.backends.clickhouse.types import DIMENSION_TYPE_MAP, TYPE_TO_DIMENSION


@dataclass
class DictionaryAttr:
    name: str
    type: Union[str, Dimension]
    expression: Optional[str] = None
    null_value: str = "NULL"
    injective: bool = False

    def __post_init__(self):
        if isinstance(self.type, str):
            try:
                self.type = TYPE_TO_DIMENSION[self.type]()
            except KeyError:
                raise ValueError(f"Invalid type: {self.type}") from None

    def definition_sql(self):
        expression = f"EXPRESSION {self.expression}" if self.expression else ""
        default = f"DEFAULT {self.null_value}" if self.null_value else ""
        type_part = (
            f"Nullable({self.clickhouse_type})"
            if self.null_value == "NULL"
            else self.clickhouse_type
        )
        return (
            f"{self.name} {type_part} {default} {expression} "
            f"{'INJECTIVE' if self.injective else ''}"
        )

    @property
    def clickhouse_type(self):
        return DIMENSION_TYPE_MAP[self.type.__class__]

    def to_json(self):
        return {
            "kind": "attr",
            "name": self.name,
            "type": self.type.__class__.__name__,
            "expression": self.expression,
            "null_value": self.null_value,
            "injective": self.injective,
        }


class DictionaryDefinition:
    def __init__(
        self,
        name: str,
        source: DataSource,
        key: Union[str, DictionaryAttr, List[Union[str, DictionaryAttr]]],
        layout: str,
        attrs: [DictionaryAttr],
        lifetime_min: int = 600,
        lifetime_max: int = 720,
    ):
        self.name = name
        # Normalize keys to a list
        if isinstance(key, (str, DictionaryAttr)):
            self.keys: List[Union[str, DictionaryAttr]] = [key]
        elif isinstance(key, list):
            self.keys = key
        self.source = source
        self.layout = layout
        self.attrs = attrs
        self.lifetime_min = lifetime_min
        self.lifetime_max = lifetime_max

    def definition_sql(self, database=None):
        db_part = f"{database}." if database else ""
        columns = []
        for k in self.keys:
            if isinstance(k, DictionaryAttr):
                # use the type from the DictionaryAttr
                columns.append(f"{k.name} {k.clickhouse_type}")
            elif isinstance(k, str):
                # when the key is just a string, use UInt64 type for the column
                columns.append(f"{k} UInt64")
            else:
                raise ValueError(f"Invalid key type: {k}")
        for attr in self.attrs:
            columns.append(attr.definition_sql())

        cols_sql = ",\n".join(columns)
        # primary key
        if len(self.keys) == 1:
            pk = self.keys[0]
            pk_sql = f"PRIMARY KEY {pk.name if isinstance(pk, DictionaryAttr) else pk}"
        else:
            joined = ", ".join(k.name if isinstance(k, DictionaryAttr) else k for k in self.keys)
            pk_sql = f"PRIMARY KEY ({joined})"
        return (
            f"CREATE DICTIONARY IF NOT EXISTS {db_part}{self.name} ("
            f"{cols_sql}"
            f") "
            f"{pk_sql} "
            f"{self.source.definition_sql()} "
            f"LAYOUT ({self.layout.upper()}()) "
            f"LIFETIME(MIN {self.lifetime_min} MAX {self.lifetime_max}) "
            f"COMMENT 'blake2:{self.checksum}'"
        )

    @property
    def checksum(self):
        def _serialize_key(k: Union[str, "DictionaryAttr"]):
            if isinstance(k, str):
                return {"kind": "string", "name": k}
            return k.to_json()

        data = {
            "name": self.name,
            "key": [_serialize_key(k) for k in self.keys],
            "source": self.source.definition_sql(),
            "layout": self.layout,
            "attrs": [attr.definition_sql() for attr in self.attrs],
            "lifetime_min": self.lifetime_min,
            "lifetime_max": self.lifetime_max,
        }
        return hashlib.blake2b(json.dumps(data).encode("utf-8"), digest_size=32).hexdigest()

    def drop_sql(self, database=None):
        db_part = f"{database}." if database else ""
        return f"DROP DICTIONARY IF EXISTS {db_part}{self.name} SYNC"

    def create_cube(self) -> Cube:
        class Out(Cube):
            class Clickhouse:
                source = self

        # Key columns: infer dimension from key type
        for k in self.keys:
            if isinstance(k, DictionaryAttr):
                setattr(Out, k.name, k.clickhouse_type)
            elif isinstance(k, str):
                setattr(Out, k, IntDimension())
            else:
                raise ValueError(f"Invalid key type: {k}")
        for attr in self.attrs:
            setattr(Out, attr.name, StringDimension())

        Out._process_attrs()
        return Out

from __future__ import annotations

import warnings

from collections.abc import Callable
from functools import cached_property
from typing import Annotated, Any, Literal, cast

from pydantic import (
    BaseModel,
    Discriminator,
    Field,
    ValidationInfo,
    computed_field,
    model_validator,
)

from .enums import (
    BoundaryOrder,
    ColumnConvertedType,
    ColumnLogicalType,
    Compression,
    ConvertedType,
    Encoding,
    GeospatialType,
    GroupConvertedType,
    GroupLogicalType,
    ListSemantics,
    LogicalType,
    PageType,
    Repetition,
    SchemaElementType,
    TimeUnit,
    Type,
)
from .util.models import get_item_or_attr


class CompressionStats(BaseModel, frozen=True):
    """Compression statistics for data."""

    total_compressed: int
    total_uncompressed: int

    @computed_field
    @cached_property
    def ratio(self) -> float:
        """Compression ratio (compressed/uncompressed)."""
        return (
            self.total_compressed / self.total_uncompressed
            if self.total_uncompressed > 0
            else 0.0
        )

    @computed_field
    @cached_property
    def space_saved_percent(self) -> float:
        """Percentage of space saved by compression."""
        return (1 - self.ratio) * 100 if self.total_uncompressed > 0 else 0.0

    @computed_field
    @cached_property
    def compressed_mb(self) -> float:
        """Compressed size in MB."""
        return self.total_compressed / (1024 * 1024)

    @computed_field
    @cached_property
    def uncompressed_mb(self) -> float:
        """Uncompressed size in MB."""
        return self.total_uncompressed / (1024 * 1024)


class KeyValueMetadata(BaseModel, frozen=True):
    """Key-value metadata pair with byte range information."""

    start_offset: int
    byte_length: int
    key: str
    value: str


class LogicalTypeInfo(BaseModel, frozen=True):
    """Base class for logical type information."""

    logical_type: LogicalType


class StringTypeInfo(LogicalTypeInfo, frozen=True):
    """String logical type."""

    logical_type: Literal[LogicalType.STRING] = LogicalType.STRING


class IntTypeInfo(LogicalTypeInfo, frozen=True):
    """Integer logical type with bit width and signedness."""

    logical_type: Literal[LogicalType.INTEGER] = LogicalType.INTEGER
    bit_width: int = 32
    is_signed: bool = True


class DecimalTypeInfo(LogicalTypeInfo, frozen=True):
    """Decimal logical type with scale and precision."""

    logical_type: Literal[LogicalType.DECIMAL] = LogicalType.DECIMAL
    scale: int = 0
    precision: int = 10


class TimeTypeInfo(LogicalTypeInfo, frozen=True):
    """Time logical type with unit and UTC adjustment."""

    logical_type: Literal[LogicalType.TIME] = LogicalType.TIME
    is_adjusted_to_utc: bool = True
    unit: TimeUnit = TimeUnit.MILLIS


class TimestampTypeInfo(LogicalTypeInfo, frozen=True):
    """Timestamp logical type with unit and UTC adjustment."""

    logical_type: Literal[LogicalType.TIMESTAMP] = LogicalType.TIMESTAMP
    is_adjusted_to_utc: bool = True
    unit: TimeUnit = TimeUnit.MILLIS


class DateTypeInfo(LogicalTypeInfo, frozen=True):
    """Date logical type."""

    logical_type: Literal[LogicalType.DATE] = LogicalType.DATE


class EnumTypeInfo(LogicalTypeInfo, frozen=True):
    """Enum logical type."""

    logical_type: Literal[LogicalType.ENUM] = LogicalType.ENUM


class JsonTypeInfo(LogicalTypeInfo, frozen=True):
    """JSON logical type."""

    logical_type: Literal[LogicalType.JSON] = LogicalType.JSON


class BsonTypeInfo(LogicalTypeInfo, frozen=True):
    """BSON logical type."""

    logical_type: Literal[LogicalType.BSON] = LogicalType.BSON


class UuidTypeInfo(LogicalTypeInfo, frozen=True):
    """UUID logical type."""

    logical_type: Literal[LogicalType.UUID] = LogicalType.UUID


class Float16TypeInfo(LogicalTypeInfo, frozen=True):
    """Float16 logical type."""

    logical_type: Literal[LogicalType.FLOAT16] = LogicalType.FLOAT16


class MapTypeInfo(LogicalTypeInfo, frozen=True):
    """Map logical type."""

    logical_type: Literal[LogicalType.MAP] = LogicalType.MAP


class ListTypeInfo(LogicalTypeInfo, frozen=True):
    """List logical type."""

    logical_type: Literal[LogicalType.LIST] = LogicalType.LIST


class VariantTypeInfo(LogicalTypeInfo, frozen=True):
    """Variant logical type."""

    logical_type: Literal[LogicalType.VARIANT] = LogicalType.VARIANT


class GeometryTypeInfo(LogicalTypeInfo, frozen=True):
    """Geometry logical type."""

    logical_type: Literal[LogicalType.GEOMETRY] = LogicalType.GEOMETRY


class GeographyTypeInfo(LogicalTypeInfo, frozen=True):
    """Geography logical type."""

    logical_type: Literal[LogicalType.GEOGRAPHY] = LogicalType.GEOGRAPHY


class UnknownTypeInfo(LogicalTypeInfo, frozen=True):
    """Unknown logical type."""

    logical_type: Literal[LogicalType.UNKNOWN] = LogicalType.UNKNOWN


LogicalTypeInfoUnion = (
    StringTypeInfo
    | IntTypeInfo
    | DecimalTypeInfo
    | TimeTypeInfo
    | TimestampTypeInfo
    | DateTypeInfo
    | EnumTypeInfo
    | JsonTypeInfo
    | BsonTypeInfo
    | UuidTypeInfo
    | Float16TypeInfo
    | MapTypeInfo
    | ListTypeInfo
    | VariantTypeInfo
    | GeometryTypeInfo
    | GeographyTypeInfo
    | UnknownTypeInfo
)

LogicalTypeInfoDiscriminated = Annotated[
    LogicalTypeInfoUnion,
    Discriminator('logical_type'),
]


CONVERTED_TYPE_TO_LOGICAL_TYPE: dict[ConvertedType, LogicalTypeInfo] = {
    ConvertedType.UTF8: StringTypeInfo(),
    ConvertedType.MAP: MapTypeInfo(),
    ConvertedType.LIST: ListTypeInfo(),
    ConvertedType.ENUM: EnumTypeInfo(),
    ConvertedType.DATE: DateTypeInfo(),
    ConvertedType.JSON: JsonTypeInfo(),
    ConvertedType.BSON: BsonTypeInfo(),
    ConvertedType.TIME_MILLIS: TimeTypeInfo(unit=TimeUnit.MILLIS),
    ConvertedType.TIME_MICROS: TimeTypeInfo(unit=TimeUnit.MICROS),
    ConvertedType.TIMESTAMP_MILLIS: TimestampTypeInfo(unit=TimeUnit.MILLIS),
    ConvertedType.TIMESTAMP_MICROS: TimestampTypeInfo(unit=TimeUnit.MICROS),
    ConvertedType.INT_8: IntTypeInfo(bit_width=8, is_signed=True),
    ConvertedType.INT_16: IntTypeInfo(bit_width=16, is_signed=True),
    ConvertedType.INT_32: IntTypeInfo(bit_width=32, is_signed=True),
    ConvertedType.INT_64: IntTypeInfo(bit_width=64, is_signed=True),
    ConvertedType.UINT_8: IntTypeInfo(bit_width=8, is_signed=False),
    ConvertedType.UINT_16: IntTypeInfo(bit_width=16, is_signed=False),
    ConvertedType.UINT_32: IntTypeInfo(bit_width=32, is_signed=False),
    ConvertedType.UINT_64: IntTypeInfo(bit_width=64, is_signed=False),
}


class SchemaElement(BaseModel, frozen=True):
    element_type: SchemaElementType
    name: str
    start_offset: int
    byte_length: int

    def _repr_extra(self) -> list[str]:
        return []

    def __repr__(self) -> str:
        extra = self._repr_extra()
        extra_str = f': {" ".join(extra)}' if extra else None
        return f'{self.element_type}({self.name}{extra_str})'

    def get_logical_type(self) -> LogicalTypeInfo | None:
        """Get the logical type, prioritizing logical_type field over converted_type."""
        logical_type = getattr(self, 'logical_type', None)

        if logical_type is not None:
            return logical_type

        # Fallback to converting converted_type to logical equivalent
        return self._converted_type_to_logical_type(
            getattr(self, 'converted_type', None),
            getattr(self, 'scale', None),
            getattr(self, 'precision', None),
        )

    @staticmethod
    def _converted_type_to_logical_type(
        converted_type: ConvertedType | None,
        scale: int | None = None,
        precision: int | None = None,
    ) -> LogicalTypeInfo | None:
        """Convert a ConvertedType to a LogicalTypeInfo for backward compatibility."""
        if converted_type is None:
            return None

        # Special handling for DECIMAL which uses scale and precision
        if converted_type == ConvertedType.DECIMAL:
            return DecimalTypeInfo(
                scale=scale or 0,
                precision=precision or 10,
            )

        return CONVERTED_TYPE_TO_LOGICAL_TYPE.get(converted_type)

    @staticmethod
    def new(
        start_offset: int,
        byte_length: int,
        name: str | None = None,
        type: Type | None = None,
        type_length: int | None = None,
        repetition: Repetition | None = None,
        num_children: int | None = None,
        converted_type: ConvertedType | None = None,
        scale: int | None = None,
        precision: int | None = None,
        field_id: int | None = None,
        logical_type: LogicalTypeInfoUnion | None = None,
    ) -> SchemaRoot | SchemaGroup | SchemaLeaf:
        # Check type compatibility for column/leaf element
        is_column_converted_type = (
            converted_type is None or converted_type in ColumnConvertedType
        )
        is_column_logical_type = (
            logical_type is None or logical_type.logical_type in ColumnLogicalType
        )

        if (
            name
            and num_children is None
            and repetition is not None
            and type is not None
            and is_column_converted_type
            and is_column_logical_type
        ):
            return SchemaLeaf(
                name=name,
                type=type,
                type_length=type_length,
                repetition=repetition,
                converted_type=converted_type,
                scale=scale,
                precision=precision,
                field_id=field_id,
                logical_type=logical_type,
                start_offset=start_offset,
                byte_length=byte_length,
                # Levels will be calculated later during schema tree building
                definition_level=0,
                repetition_level=0,
            )

        # Root element could look essentially like any other group,
        # but with no repetition, which is required for other types
        if (
            name
            and converted_type is None
            and num_children is not None
            and type is None
            and logical_type is None
            and repetition is None
        ):
            return SchemaRoot(
                name=name,
                num_children=num_children,
                start_offset=start_offset,
                byte_length=byte_length,
            )

        # Root element check: should have no repetition, but some writers
        # incorrectly set repetition=REQUIRED on root elements, so we also
        # check the name
        if (
            name == 'schema'
            and num_children is not None
            and converted_type is None
            and logical_type is None
            and type is None
            and repetition == Repetition.REQUIRED
        ):
            warnings.warn(
                'Schema element appears to be root, but has invalid '
                'attrs. Warily assuming it is root... Schema element: '
                f"name='{name}', type='{type}', type_length='{type_length}', "
                f"repetition='{repetition}', num_children='{num_children}', "
                f"converted_type='{converted_type}",
                stacklevel=1,
            )
            return SchemaRoot(
                name=name,
                num_children=num_children,
                start_offset=start_offset,
                byte_length=byte_length,
            )

        # Check type compatibility for group element
        is_group_converted_type = (
            converted_type is None or converted_type in GroupConvertedType
        )
        is_group_logical_type = (
            logical_type is None or logical_type.logical_type in GroupLogicalType
        )

        if (
            name
            and is_group_converted_type
            and num_children is not None
            and repetition is not None
            and type is None
            and is_group_logical_type
        ):
            return SchemaGroup(
                name=name,
                repetition=repetition,
                num_children=num_children,
                converted_type=converted_type,
                start_offset=start_offset,
                byte_length=byte_length,
                field_id=field_id,
                logical_type=logical_type,
            )

        raise ValueError(
            'Could not resolve schema element type for args: '
            f"name='{name}', type='{type}', type_length='{type_length}', "
            f"repetition='{repetition}', num_children='{num_children}', "
            f"converted_type='{converted_type}",
        )


class BaseSchemaGroup(SchemaElement, frozen=True):
    element_type: SchemaElementType = SchemaElementType.GROUP
    num_children: int
    children: dict[str, SchemaGroup | SchemaLeaf] = Field(default_factory=dict)

    def count_leaf_columns(self) -> int:
        """Count all columns (leaves) in this schema element and its children."""
        return sum(
            child.count_leaf_columns() if isinstance(child, BaseSchemaGroup) else 1
            for child in self.children.values()
        )

    def find_element(self, path: str | list[str]) -> SchemaElement:
        """Finds a descendant schema element by its dotted path."""
        not_found = ValueError(f"Schema element for path '{path}' not found")

        if isinstance(path, str):
            path = path.split('.')

        child_name = path.pop(0)
        try:
            child = self.children[child_name]
        except KeyError:
            raise not_found from None

        if path and isinstance(child, BaseSchemaGroup):
            return child.find_element(path)

        if path:
            raise not_found

        return child

    def add_element(
        self,
        element: SchemaGroup | SchemaLeaf,
        path: str | list[str] | None = None,
    ) -> None:
        """Add an element to the schema at the specified dotted path."""
        if path is None:
            path = [element.name]
        elif isinstance(path, str):
            path = path.split('.')

        child_name = path.pop(0)

        if len(path) == 0:
            # Direct child
            self.children[child_name] = element
            return

        # Nested path - find parent group
        try:
            group = self.children[child_name]
        except KeyError:
            raise ValueError('Parent group not found') from None

        if not isinstance(group, BaseSchemaGroup):
            raise ValueError(
                'Found parent group, but it is not a group!',
            ) from None

        group.add_element(element, path)

    def __repr__(self) -> str:
        result = super().__repr__()
        for child in self.children.values():
            result += f'  {child}'
        return result


class SchemaRoot(BaseSchemaGroup, frozen=True):
    element_type: SchemaElementType = SchemaElementType.ROOT

    def renest(self, flat_data: dict[str, list]) -> dict[str, Any]:
        """
        Reconstruct nested structures from flattened column paths
        using schema information.

        Uses the actual Parquet schema to determine correct reconstruction for:
        - MAP logical types -> {key: value} dictionaries
        - LIST logical types -> [item, item, ...] arrays
        - STRUCT types -> {field: value, ...} objects

        Args:
            flat_data: Dictionary mapping column paths to values.
                      Keys are dotted paths (e.g., "person.name", "arr.key_value.key").
                      Values should be lists of data.

        Returns:
            Dictionary with schema-aware reconstructed nested structures.
        """
        # If we have no data then we just return!
        if not flat_data:
            return {}

        # Convert flat paths to path segments for tree traversal
        path_segments_data = {
            tuple(path.split('.')): data for path, data in flat_data.items()
        }

        # Recursively reconstruct using schema tree
        result = {}
        for name, child_element in self.children.items():
            result[name] = self._reconstruct_from_schema_tree(
                child_element,
                (name,),
                path_segments_data,
            )

        return result

    def _reconstruct_from_schema_tree(
        self,
        schema_element: SchemaGroup | SchemaLeaf,
        current_path: tuple[str, ...],
        path_data: dict[tuple[str, ...], list],
    ) -> Any:
        """Reconstruct data using pure recursive DFS traversal."""
        # Base case: if this exact path has data, return it
        if isinstance(schema_element, SchemaLeaf):
            return path_data[current_path]

        # If no children, return empty
        if not schema_element.children:
            return []

        # Recursively process all children (DFS)
        children_data = {}
        for child_name, child_element in schema_element.children.items():
            child_path = (*current_path, child_name)
            child_result = self._reconstruct_from_schema_tree(
                child_element,
                child_path,
                path_data,
            )
            if child_result:
                children_data[child_name] = child_result

        # Apply logical type transformations to the recursively built data
        return self._apply_logical_type_transform(
            schema_element,
            children_data,
        )

    def _apply_logical_type_transform(
        self,
        schema_element: SchemaGroup,
        children_data: dict[str, Any],
    ) -> Any:
        """Apply logical type transformations to recursively built child data."""
        from por_que.enums import LogicalType

        if not children_data:
            return []

        # Get logical type and apply appropriate transformation
        logical_type_info = schema_element.get_logical_type()

        if logical_type_info is None:
            if schema_element.repetition.name == 'REPEATED':
                if len(schema_element.children) == 1:
                    # REPEATED group with single child → LIST
                    return self._process_standard_list(children_data)
                # REPEATED group with multiple children → array of structs
                return self._process_repeated_struct(children_data)

            return self._process_struct(children_data)

        match logical_type_info.logical_type:
            case LogicalType.MAP:
                return self._get_map_process_function(schema_element)(children_data)
            case LogicalType.LIST:
                return self._process_standard_list(children_data)
            case _ as unexpected:
                raise ValueError(
                    f'Unexpected logical type for group: {unexpected}',
                )

    def _process_struct(self, children_data: dict[str, Any]) -> Any:
        # STRUCT: zip child arrays into list of objects
        return self._zip_struct_fields(children_data)

    def _process_repeated_struct(self, children_data: dict[str, Any]) -> list[Any]:  # noqa: C901
        """Convert REPEATED group with multiple children to array of structs.

        For REPEATED groups, each child produces an array per record.  We need
        to convert from struct-of-arrays to array-of-structs at each record
        level.

        Input: {
            'number': [None, [], [5, 6]],
            'kind': [None, [], ['home', 'work']],
        }
        Output: [
            None,
            [],
            [
                {'number': 5, 'kind': 'home'},
                {'number': 6, 'kind': 'work'},
            ],
        ]
        """
        if not children_data:
            return []

        # Get number of top-level records from first child
        first_child = next(iter(children_data.values()))
        num_records = len(first_child) if isinstance(first_child, list) else 1

        result: list[Any] = []
        for record_idx in range(num_records):
            # Get all child arrays for this record
            all_none = True
            all_empty = True
            field_arrays = {}

            for field_name, field_data in children_data.items():
                value = (
                    field_data[record_idx]
                    if isinstance(field_data, list) and record_idx < len(field_data)
                    else field_data
                )
                field_arrays[field_name] = value

                if value is not None:
                    all_none = False
                if value != []:
                    all_empty = False

            # If all fields are None, the repeated group is null
            if all_none:
                result.append(None)
            # If all fields are empty arrays, the repeated group is empty
            elif all_empty:
                result.append([])
            else:
                # Zip the field arrays into structs
                max_len = max(
                    len(arr) if isinstance(arr, list) else 0
                    for arr in field_arrays.values()
                )
                structs = []
                for elem_idx in range(max_len):
                    struct = {}
                    for field_name, field_array in field_arrays.items():
                        if isinstance(field_array, list) and elem_idx < len(
                            field_array,
                        ):
                            struct[field_name] = field_array[elem_idx]
                        else:
                            struct[field_name] = None
                    structs.append(struct)
                result.append(structs)

        return result

    def _get_map_process_function(
        self,
        schema_element: SchemaGroup,
    ) -> Callable[[dict[str, Any]], Any]:
        """Check if MAP schema is valid according to Parquet specification."""
        # MAP logical type must have canonical three-level structure:
        # <name> (MAP) { repeated group key_value { required key; <rep> value; } }

        if schema_element.num_children != 1:
            return self._process_struct

        child = next(iter(schema_element.children.values()))

        if not isinstance(child, SchemaGroup):
            return self._process_struct

        if child.repetition != Repetition.REPEATED:
            raise ValueError(f'Unexpected map child repetition: {child.repetition}')

        if child.num_children == 1:
            return self._process_standard_list

        if child.num_children > 2:
            raise ValueError(
                f'Unprocessable map: child has {child.num_children} children',
            )

        if next(iter(child.children.values())).repetition != Repetition.REQUIRED:
            return self._process_standard_list

        return self._build_maps

    def _build_maps(self, children_data: dict[str, Any]) -> list[dict[str, Any]]:  # noqa: C901
        """Build MAP objects from key/value data using canonical
        Parquet MAP structure."""
        # According to Parquet spec, MAP logical types have
        # canonical three-level structure:
        # <name> (MAP) { repeated group key_value { required key; <rep> value; } }

        if not children_data:
            return []

        # Get the repeated group data (canonical name is "key_value")
        if 'key_value' not in children_data:
            raise ValueError(
                "MAP logical type missing required 'key_value' repeated group",
            )

        key_value_records = children_data['key_value']
        if not key_value_records:
            return []

        maps: list[dict[str, Any]] = []
        for record in key_value_records:
            # Handle different record formats from _process_repeated_struct
            if isinstance(record, list):
                if len(record) == 0:
                    # Empty list → empty map
                    maps.append({})
                else:
                    # List of key-value structs → convert to map
                    # Each struct has 'key' and 'value' fields
                    map_dict: dict[str, Any] = {}
                    for kv_struct in record:
                        if isinstance(kv_struct, dict):
                            key = cast(str, kv_struct.get('key'))
                            value = kv_struct.get('value')
                            map_dict[key] = value
                        else:
                            raise ValueError(
                                'Expected dict in MAP key_value list, '
                                f'got {type(kv_struct)}',
                            )
                    maps.append(map_dict)
                continue

            if not isinstance(record, dict):
                raise ValueError(
                    f'MAP key_value record must be dict or list, got {type(record)}',
                )

            fields = list(record.items())
            if not fields:
                # Empty dict means empty map
                maps.append({})
                continue

            _, key_data = fields[0]

            # Second field is the value (if it exists)
            value_data = None
            if len(fields) > 1:
                _, value_data = fields[1]

            maps.append(self._construct_map(key_data, value_data))
        return maps

    def _construct_map(self, key_data: Any, value_data: Any) -> dict[Any, Any]:
        if not isinstance(key_data, list):
            # Single key/value pair
            return dict(*[key_data, value_data])

        # Handle array of keys - pair each key with corresponding value or None
        row_map_as_list = []
        for j, key in enumerate(key_data):
            # Check if corresponding value exists, otherwise use None
            if isinstance(value_data, list) and j < len(value_data):
                value = value_data[j]
            else:
                value = None
            row_map_as_list.append([key, value])
        return dict(row_map_as_list)

    def _process_standard_list(self, children_data: dict[str, Any]) -> list:
        """Process standard LIST logical type with three-level structure."""
        if not children_data:
            return []

        # Get the repeated group (should be the only child for LIST types)
        repeated_group_data = next(iter(children_data.values()))
        if not repeated_group_data:
            return []

        # Handle malformed MAP treated as LIST - extract just the values
        if (
            isinstance(repeated_group_data, list)
            and repeated_group_data
            and isinstance(repeated_group_data[0], dict)
            and len(repeated_group_data[0]) == 1
        ):
            # This looks like a malformed MAP (single field) - extract the field values
            field_name = next(iter(repeated_group_data[0].keys()))
            return [record[field_name] for record in repeated_group_data]

        return repeated_group_data

    def _zip_struct_fields(self, fields: dict[str, Any]) -> list[dict[str, Any] | None]:
        """Zip struct field arrays into list of objects."""
        if not fields:
            return []

        # Get record count from first field
        first_field = next(iter(fields.values()))
        num_records = len(first_field) if isinstance(first_field, list) else 1

        # Build struct objects
        result: list[dict[str, Any] | None] = []
        for i in range(num_records):
            struct_obj = {}
            all_none = True

            for name, values in fields.items():
                value = (
                    values[i]
                    if isinstance(values, list) and i < len(values)
                    else values
                )
                struct_obj[name] = value

                # Check if any field is not None
                # Note: empty arrays [] are valid values, not null!
                if value is not None:
                    all_none = False

            # If all fields are None, the struct itself is None (null parent struct)
            # But if any field has a value (including []), the struct exists
            if all_none:
                result.append(None)
            else:
                result.append(struct_obj)

        return result


class SchemaGroup(BaseSchemaGroup, frozen=True):
    repetition: Repetition
    converted_type: ConvertedType | None
    field_id: int | None = None
    logical_type: LogicalTypeInfoUnion | None = None

    def _repr_extra(self) -> list[str]:
        return [
            self.repetition.name,
            self.converted_type.name if self.converted_type else str(None),
        ]


class SchemaLeaf(SchemaElement, frozen=True):
    element_type: SchemaElementType = SchemaElementType.COLUMN
    type: Type
    repetition: Repetition
    converted_type: ConvertedType | None
    type_length: int | None = None
    scale: int | None = None
    precision: int | None = None
    field_id: int | None = None
    logical_type: LogicalTypeInfoUnion | None = None
    # These levels are calculated during schema parsing based on the full path
    definition_level: int = 0
    repetition_level: int = 0
    # Semantic interpretation for repeated field handling
    # (set during tree reconstruction)
    list_semantics: ListSemantics | None = None

    def _repr_extra(self) -> list[str]:
        return [
            self.repetition.name,
            self.converted_type.name if self.converted_type else str(None),
            self.type.name,
        ]


class ColumnStatistics(
    BaseModel,
    frozen=True,
    ser_json_bytes='base64',
    val_json_bytes='base64',
):
    min_: bytes | None = Field(None, alias='min')
    max_: bytes | None = Field(None, alias='max')
    null_count: int | None = None
    distinct_count: int | None = None
    min_value: bytes | None = None
    max_value: bytes | None = None
    is_min_value_exact: bool | None = None
    is_max_value_exact: bool | None = None


class SizeStatistics(BaseModel, frozen=True):
    """Size statistics for BYTE_ARRAY columns."""

    unencoded_byte_array_data_bytes: int | None = None
    repetition_level_histogram: list[int] | None = None
    definition_level_histogram: list[int] | None = None


class BoundingBox(BaseModel, frozen=True):
    """Bounding box for GEOMETRY or GEOGRAPHY types."""

    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float | None = None
    zmax: float | None = None
    mmin: float | None = None
    mmax: float | None = None


class GeospatialStatistics(BaseModel, frozen=True):
    """Statistics specific to Geometry and Geography logical types."""

    bbox: BoundingBox | None = None
    geospatial_types: list[GeospatialType] | None = None


class PageEncodingStats(BaseModel, frozen=True):
    """Statistics of a given page type and encoding."""

    page_type: PageType
    encoding: Encoding
    count: int


class PageLocation(BaseModel, frozen=True):
    """Location information for a page within a column chunk."""

    offset: int  # File offset of the page
    compressed_page_size: int  # Compressed size of the page
    first_row_index: int  # First row index of the page


class OffsetIndex(BaseModel, frozen=True):
    """Index containing page locations and sizes for efficient seeking."""

    page_locations: list[PageLocation]
    unencoded_byte_array_data_bytes: list[int] | None = None


class ColumnIndex(
    BaseModel,
    frozen=True,
    ser_json_bytes='base64',
    val_json_bytes='base64',
):
    """Index containing min/max statistics and null information for pages."""

    null_pages: list[bool]  # Which pages are all null
    min_values: list[bytes]  # Raw min values for each page
    max_values: list[bytes]  # Raw max values for each page
    boundary_order: BoundaryOrder  # Whether min/max values are ordered
    null_counts: list[int] | None = None  # Null count per page
    repetition_level_histograms: list[int] | None = None
    definition_level_histograms: list[int] | None = None


class ColumnMetadata(BaseModel, frozen=True):
    """Detailed metadata about column chunk content and encoding."""

    start_offset: int
    byte_length: int
    type: Type
    encodings: list[Encoding]
    path_in_schema: str
    schema_element: SchemaLeaf = Field(exclude=True)
    codec: Compression
    num_values: int
    total_uncompressed_size: int
    total_compressed_size: int
    data_page_offset: int
    index_page_offset: int | None = None
    dictionary_page_offset: int | None = None
    statistics: ColumnStatistics | None = None
    encoding_stats: list[PageEncodingStats] | None = None
    bloom_filter_offset: int | None = None
    bloom_filter_length: int | None = None
    size_statistics: SizeStatistics | None = None
    geospatial_statistics: GeospatialStatistics | None = None


class ColumnChunk(BaseModel, frozen=True):
    """File-level organization of column chunk."""

    file_offset: int
    metadata: ColumnMetadata
    file_path: str | None = None
    offset_index_offset: int | None = None
    offset_index_length: int | None = None
    column_index_offset: int | None = None
    column_index_length: int | None = None

    @model_validator(mode='before')
    @classmethod
    def inject_schema_element_from_context(cls, data: Any, info: ValidationInfo):
        """Inject schema element from context if not provided."""
        if not isinstance(data, dict) or not info.context:
            return data

        if 'schema_element' in data or 'schema_root' not in info.context:
            return data

        schema_root = info.context['schema_root']

        try:
            path = data['metadata']['path_in_schema']
        except KeyError:
            return data

        schema_element = schema_root.find_element(path)
        if schema_element and isinstance(schema_element, SchemaLeaf):
            data = {**data, 'schema_element': schema_element}

        return data

    # Property accessors for flattened API access
    # We maintain the nested ColumnMetadata structure to stay consistent with
    # the actual Parquet metadata model, but provide these accessors for a
    # more logical and convenient API experience.
    @property
    def type(self) -> Type:
        return self.metadata.type

    @property
    def encodings(self) -> list[Encoding]:
        return self.metadata.encodings

    @property
    def path_in_schema(self) -> str:
        return self.metadata.path_in_schema

    @property
    def schema_element(self) -> SchemaLeaf:
        return self.metadata.schema_element

    @property
    def codec(self) -> Compression:
        return self.metadata.codec

    @property
    def num_values(self) -> int:
        return self.metadata.num_values

    @property
    def total_uncompressed_size(self) -> int:
        return self.metadata.total_uncompressed_size

    @property
    def total_compressed_size(self) -> int:
        return self.metadata.total_compressed_size

    @property
    def data_page_offset(self) -> int:
        return self.metadata.data_page_offset

    @property
    def index_page_offset(self) -> int | None:
        return self.metadata.index_page_offset

    @property
    def dictionary_page_offset(self) -> int | None:
        return self.metadata.dictionary_page_offset

    @property
    def statistics(self) -> ColumnStatistics | None:
        return self.metadata.statistics

    @property
    def bloom_filter_offset(self) -> int | None:
        return self.metadata.bloom_filter_offset

    @property
    def bloom_filter_length(self) -> int | None:
        return self.metadata.bloom_filter_length

    @property
    def size_statistics(self) -> SizeStatistics | None:
        return self.metadata.size_statistics

    @property
    def geospatial_statistics(self) -> GeospatialStatistics | None:
        return self.metadata.geospatial_statistics


class SortingColumn(BaseModel, frozen=True):
    column_idx: int
    descending: bool
    nulls_first: bool


class RowGroup(BaseModel, frozen=True):
    """Logical representation of row group metadata."""

    start_offset: int
    byte_length: int
    column_chunks: dict[str, ColumnChunk]
    total_byte_size: int
    row_count: int
    sorting_columns: list[SortingColumn] | None = None
    file_offset: int | None = None
    total_compressed_size: int | None = None
    ordinal: int | None = None

    @computed_field
    @cached_property
    def compression_stats(self) -> CompressionStats:
        total_compressed = 0
        total_uncompressed = 0
        for col in self.column_chunks.values():
            total_compressed += col.total_compressed_size
            total_uncompressed += col.total_uncompressed_size

        return CompressionStats(
            total_compressed=total_compressed,
            total_uncompressed=total_uncompressed,
        )

    @cached_property
    def column_names(self) -> list[str]:
        return list(self.column_chunks.keys())

    @cached_property
    def column_count(self) -> int:
        return len(self.column_chunks)


type RowGroups = list[RowGroup]


class FileMetadata(BaseModel, frozen=True):
    """Logical representation of file metadata."""

    version: int
    schema_root: SchemaRoot
    row_groups: RowGroups
    created_by: str | None = None
    key_value_metadata: list[KeyValueMetadata] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def inject_schema_references(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        try:
            schema_root = data['schema_root']
            row_groups: RowGroups | list[dict] = data['row_groups']
        except KeyError:
            return data

        if not isinstance(schema_root, SchemaRoot):
            schema_root = SchemaRoot(**schema_root)
            data['schema_root'] = schema_root

        updated_row_groups: list[RowGroup | dict] = []
        for row_group in row_groups:
            updated = False
            try:
                column_chunks: dict[str, ColumnChunk | dict] = get_item_or_attr(
                    row_group,
                    'column_chunks',
                )
            except ValueError:
                return data

            updated_column_chunks: dict[str, ColumnChunk | dict] = {}
            for column_chunk in column_chunks.values():
                try:
                    metadata: ColumnMetadata | dict[str, Any] = get_item_or_attr(
                        column_chunk,
                        'metadata',
                    )
                    path: str = get_item_or_attr(
                        metadata,
                        'path_in_schema',
                    )
                except ValueError:
                    return data

                # Find and inject the logical metadata reference
                schema_element = schema_root.find_element(path)
                if getattr(metadata, 'schema_element', None) is schema_element:
                    updated_column_chunks[path] = column_chunk
                    continue

                updated = True
                _chunk = (
                    column_chunk
                    if isinstance(column_chunk, dict)
                    else column_chunk.__dict__
                )
                _meta = metadata if isinstance(metadata, dict) else metadata.__dict__
                _meta['schema_element'] = schema_element
                _chunk['metadata'] = _meta
                updated_column_chunks[path] = _chunk

            if not updated:
                updated_row_groups.append(row_group)
                continue

            _rg = row_group if isinstance(row_group, dict) else row_group.__dict__
            _rg['column_chunks'] = updated_column_chunks
            updated_row_groups.append(_rg)

        return {**data, 'row_groups': updated_row_groups}

    @computed_field
    @cached_property
    def compression_stats(self) -> CompressionStats:
        """Calculate overall file statistics."""
        total_compressed = 0
        total_uncompressed = 0
        for rg in self.row_groups:
            total_compressed += rg.compression_stats.total_compressed
            total_uncompressed += rg.compression_stats.total_uncompressed

        return CompressionStats(
            total_compressed=total_compressed,
            total_uncompressed=total_uncompressed,
        )

    @computed_field
    @cached_property
    def column_count(self) -> int:
        return self.schema_root.count_leaf_columns()

    @computed_field
    @cached_property
    def row_count(self) -> int:
        return sum(rg.row_count for rg in self.row_groups)

    @computed_field
    @cached_property
    def row_group_count(self) -> int:
        return len(self.row_groups)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True)

from dataclasses import MISSING, dataclass, make_dataclass, field, fields as dc_fields
from datetime import datetime, date
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Type, Union, get_origin, get_args

from database_wrapper import DBDefaultsDataModel, MetadataDict, SerializeType


def type_to_str(t: Any) -> str:
    """Render annotations like 'str | None' or 'RV4ProductionJobStatus | None'."""
    origin = get_origin(t)
    if origin is Union:
        args = list(get_args(t))
        # Optional[T] -> Union[T, NoneType]
        if type(None) in args and len(args) == 2:
            other = args[0] if args[1] is type(None) else args[1]
            return f"{type_to_str(other)} | None"
        # General Union
        return " | ".join(type_to_str(a) for a in args)
    if hasattr(t, "__name__"):
        return t.__name__
    if getattr(t, "__module__", None) and getattr(t, "__qualname__", None):
        return f"{t.__qualname__}"
    return str(t)


def _make_enum(name: str, labels: list[str]) -> Enum:
    # Normalize labels to valid identifiers
    members = {}
    for raw in labels:
        key = raw.upper().replace(" ", "_")
        # avoid starting with digit
        if key and key[0].isdigit():
            key = f"_{key}"
        members[key] = raw
    return Enum(name, members)


@dataclass(frozen=True)
class ColumnMetaIntrospector:
    col_name: str
    db_type: str
    is_nullable: bool
    has_default: bool
    default_expr: str | None = None
    enum_labels: list[str] | None = None


class DBIntrospector:
    conn: Any

    def __init__(self, dbCursor: Any = None):
        self.conn = dbCursor

    @staticmethod
    def _default_class_name(schema: str, table: str) -> str:
        # Very naive PascalCase maker
        def pascal(s: str) -> str:
            return "".join(p.capitalize() for p in s.replace("-", "_").split("_"))

        return f"{pascal(schema)}{pascal(table)}"

    def get_table_columns(self, schema: str, table: str) -> list[ColumnMetaIntrospector]:
        raise NotImplementedError

    def map_db_type(self, db_type: str) -> str:
        raise NotImplementedError

    def get_schema_table_name(self, full_table: str) -> tuple[str, str]:
        (schema, table) = full_table.split(".") if "." in full_table else ("public", full_table)
        return (schema, table)

    def is_meta_field(self, col_name: str) -> bool:
        """
        Return True if the column is a common meta field we want to skip.

        Args:
            col_name: The name of the column
        """

        return (
            col_name == "id"
            or col_name == "created_at"
            or col_name == "updated_at"
            or col_name == "disabled_at"
            or col_name == "deleted_at"
            or col_name == "enabled"
            or col_name == "deleted"
        )

    def generate_dataclass(
        self,
        table_name: str,
        *,
        class_name: Optional[str] = None,
        base: Type[DBDefaultsDataModel] = DBDefaultsDataModel,
        enum_overrides: dict[str, Type[Enum]] | None = None,
        defaults_for_nullable: bool = True,
        include_id_field: bool = True,
    ) -> Type[DBDefaultsDataModel]:
        (schema, table) = self.get_schema_table_name(table_name)
        cols = self.get_table_columns(schema, table)
        if not cols:
            raise ValueError(f"No columns found for {schema}.{table}")

        class_name = class_name or self._default_class_name(schema, table)
        enum_overrides = enum_overrides or {}

        fields_defs = []

        for c in cols:
            # Skip meta fields
            if self.is_meta_field(c.col_name):
                continue

            # Enums
            enum_class: Optional[Type[Enum]] = None
            if c.enum_labels:
                enum_class = enum_overrides.get(c.col_name)
                if not enum_class:
                    enum_class = _make_enum(f"{class_name}_{c.col_name}_Enum", list(c.enum_labels))
                py_type = enum_class
                serialize = SerializeType.ENUM
            else:
                py_type, serialize = self.map_db_type(c.db_type)

            # Optional typing if nullable
            if c.is_nullable:
                ann = Optional[py_type]  # type: ignore
            else:
                ann = py_type  # type: ignore

            # Default value choice
            default = None
            default_factory = None
            if c.is_nullable:
                default = None
            else:
                # give some sane defaults for common not-nullables that aren't id/serial
                if py_type is bool:
                    default = False
                elif py_type in (int, float, str):
                    default = py_type()  # 0, 0.0, ""
                elif py_type is datetime:
                    default_factory = datetime.now
                elif py_type is datetime.date:
                    default_factory = date.today
                elif enum_class:
                    # pick first enum value as default
                    enum_values = list(enum_class)
                    if enum_values:
                        default = enum_values[0]
                elif py_type is dict:
                    default_factory = dict
                elif py_type is list:
                    default_factory = list
                elif py_type is set:
                    default_factory = set
                elif py_type is bytes:
                    default = bytes()
                else:
                    # Leave unset so dataclass enforces passing it explicitly
                    default = None if defaults_for_nullable else None

            md: MetadataDict = {
                "db_field": (c.col_name, c.db_type),
                "store": True,  # opinion: new rows insert everything unless you override
                "update": True,  # opinion: updates allowed unless you override
            }
            if serialize:
                md["serialize"] = serialize
            if enum_class:
                md["enum_class"] = enum_class

            if default_factory:
                fld = field(default_factory=default_factory, metadata=md)
            else:
                fld = field(default=default, metadata=md)
            fields_defs.append(
                (
                    c.col_name,
                    ann,
                    fld,
                )
            )

        # Build class with properties schemaName/tableName
        # We’ll generate methods dynamically and attach.
        cls = make_dataclass(
            class_name,
            fields_defs,
            bases=(base,),
            namespace={},  # we’ll add properties below
            frozen=False,
            eq=True,
            repr=True,
        )

        # Attach schemaName/tableName as properties
        def _schemaName(self) -> str:
            return schema

        def _tableName(self) -> str:
            return table

        setattr(cls, "schemaName", property(_schemaName))
        setattr(cls, "tableName", property(_tableName))

        return cls

    # TODO: Need to improve handling of imports for external classes, including enums.
    def render_dataclass_source(
        self,
        cls: Type,
        table_name: str,
        *,
        extra_imports: list[str] | None = None,
        emit_ignore_unknown_kwargs: bool = True,
    ) -> str:
        """
        Turn a runtime dataclass into a source file close to user's example.

        - Hardcodes schemaName/tableName.
        - Emits @ignore_unknown_kwargs() above @dataclass (optional).
        - Renders fields as:
            name: T | None = field(
                default=..., or default_factory=...,
                metadata=MetadataDict(
                    db_field=("col", "pg_type"),
                    store=True/False,
                    update=True/False,
                    [serialize=SerializeType.X],
                    [enum_class=SomeEnum],
                ),
            )
        - If an enum_class was dynamically created (module == 'enum'), embeds it into the file.
        Otherwise, adds a "from {module} import {name}" import.
        - Adds a toDict() that enumerates fields and applies .isoformat()
        for fields with serialize=SerializeType.DATETIME.
        """
        # Collect enums: dynamic vs external
        extra_imports = extra_imports or []
        dynamic_enums: list[tuple[str, list[tuple[str, Any]]]] = []
        external_enum_imports: set[tuple[str, str]] = set()
        for f in dc_fields(cls):
            md: MetadataDict = dict(f.metadata) if f.metadata else {}  # type: ignore
            enum_class = md.get("enum_class")
            if enum_class:
                mod = getattr(enum_class, "__module__", "")
                name = getattr(enum_class, "__name__", "UnknownEnum")
                # If it's the built-in Enum module (meaning we made it dynamically),
                # embed it. Otherwise, import from its module.
                if mod == "enum":
                    members = [(m.name, m.value) for m in enum_class]  # type: ignore
                    dynamic_enums.append((name, members))
                else:
                    external_enum_imports.add((mod, name))

        lines: list[str] = []
        # Imports
        lines.append("from typing import Any, Optional")
        lines.append("from datetime import datetime")
        lines.append("from dataclasses import dataclass, field")
        lines.append("")
        lines.append("from database_wrapper import MetadataDict, DBDefaultsDataModel, SerializeType")
        if emit_ignore_unknown_kwargs:
            lines.append("from database_wrapper.utils import ignore_unknown_kwargs")
        if dynamic_enums:
            lines.append("from enum import Enum")
        for mod, name in sorted(external_enum_imports):
            lines.append(f"from {mod} import {name}")
        for imp in extra_imports:
            lines.append(imp)
        lines.append("")

        # Dynamic enums embedded
        for name, members in dynamic_enums:
            lines.append(f"class {name}(Enum):")
            for k, v in members:
                lines.append(f"    {k} = {repr(v)}")
            lines.append("")

        # Class header
        (schema, table) = self.get_schema_table_name(table_name)
        if emit_ignore_unknown_kwargs:
            lines.append("@ignore_unknown_kwargs()")
        lines.append("@dataclass")
        lines.append(f"class {cls.__name__}(DBDefaultsDataModel):")
        lines.append('    """Auto-generated from database schema"""')
        lines.append("")
        lines.append("    @property")
        lines.append("    def schemaName(self) -> str:")
        lines.append(f"        return {schema!r}")
        lines.append("")
        lines.append("    @property")
        lines.append("    def tableName(self) -> str:")
        lines.append(f"        return {table!r}")
        lines.append("")

        # Render fields (skip the inherited ones we know exist on base if they aren't present here)
        for f in dc_fields(cls):
            md: MetadataDict = dict(f.metadata) if f.metadata else {}  # type: ignore
            # We always render all fields that exist in this dataclass (your make_dataclass created them)
            db_field = md.get("db_field", (f.name, "Any"))
            if not (isinstance(db_field, tuple) and len(db_field) == 2):
                col_name, db_type = f.name, "Any"
            else:
                col_name, db_type = db_field

            # Skip meta fields
            if self.is_meta_field(col_name):
                continue

            store = bool(md.get("store", False))
            update = bool(md.get("update", False))
            serialize = md.get("serialize")
            enum_class = md.get("enum_class")

            # Type annotation
            ann_str = type_to_str(f.type)

            # Default
            # dataclasses._MISSING_TYPE shows up for no default; we’ll set explicit default=None
            # if annotation is Optional[...] and no concrete default.
            default_val = getattr(f, "default", None)
            default_factory = getattr(f, "default_factory", None)

            # Build field(...) call
            lines.append(f"    {f.name}: {ann_str} = field(")

            if default_factory is not None and default_factory is not MISSING:
                lines.append(f"        default_factory={getattr(default_factory, '__qualname__', None)},")
            elif default_val is not None and default_val is not MISSING:
                lines.append(f"        default={repr(default_val)},")
            else:
                # be explicit for optionals; otherwise we omit default and let required be required
                if "| None" in ann_str:
                    lines.append("        default=None,")

            # Metadata
            lines.append("        metadata=MetadataDict(")
            lines.append(f"            db_field=({col_name!r}, {db_type!r}),")
            lines.append(f"            store={str(store)},")
            lines.append(f"            update={str(update)},")
            if serialize:
                lines.append(f"            serialize=SerializeType.{serialize.name},")
            if enum_class:
                lines.append(f"            enum_class={enum_class.__name__},")
            lines.append("        ),")
            lines.append("    )")
            lines.append("")

        # toDict() that matches your style and ISO-formats DATETIME fields
        # We enumerate in a stable order and treat DATETIME specially.
        # (jsonEncoder in your base also works, but you asked for "close to example".)
        lines.append("    # Methods")
        lines.append("    def toDict(self) -> dict[str, Any]:")
        lines.append("        out: dict[str, Any] = {}")
        lines.append("        # Explicitly list each field (stable order)")
        for f in dc_fields(cls):
            md: MetadataDict = dict(f.metadata) if f.metadata else {}  # type: ignore
            serialize = md.get("serialize")
            key = f.name
            if serialize == SerializeType.DATETIME:
                lines.append(f"        out[{key!r}] = self.{key}.isoformat() if self.{key} else None")
            else:
                lines.append(f"        out[{key!r}] = self.{key}")
        lines.append("        return out")

        return "\n".join(lines)

    def save_to_file(self, class_model_source: str, filepath: str, overwrite: bool) -> str:
        """
        Render `cls` to a Python source file and save it to `filepath`.

        Args:
            cls: The generated dataclass type to render.
            class_model_source: The source code of the class to write.
            filepath: Path to write the file to.
            overwrite: If False and file exists, raises FileExistsError.

        Returns:
            The absolute path of the written file.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not overwrite:
            raise FileExistsError(f"Refusing to overwrite existing file: {path}")

        # Normalize line endings + ensure trailing newline
        if not class_model_source.endswith("\n"):
            class_model_source += "\n"

        path.write_text(class_model_source, encoding="utf-8", newline="\n")
        return str(path.resolve())

class MixDataset(BaseModel):
    """Base model that can upload external files and can convert itself into a
    simple DuckDB-compatible schema mapping.

    The mapping is a ``dict`` where keys are field names and values are the
    corresponding database column types (e.g. ``VARCHAR``, ``INTEGER``).
    """

    # __id__: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # ---------------------------------------------------------------------
    # Generic helpers – can be overridden by subclasses if they need a custom
    # representation in the database.
    # ---------------------------------------------------------------------

    @classmethod
    def _get_db_type(cls) -> str:  # pragma: no cover – overridable
        """Default database type used when a model of *this* type is stored as
        a column value.  Sub-classes can override.
        """
        return "VARCHAR"

    # ------------------------------------------------------------------
    # Schema generation
    # ------------------------------------------------------------------

    @classmethod
    def to_db_schema(cls) -> Dict[str, str]:
        """Return a ``{field_name: db_type}`` mapping suitable for the
        ``/dataset/create`` endpoint.

        The resolution order is:

        1. If the field annotation is a ``MixDataset`` subclass – use its
           ``_get_db_type``.
        2. Built-in primitives are mapped via *type_map*.
        3. Fallback is ``VARCHAR``.
        """

        type_map: Dict[Any, str] = {
            str: "VARCHAR",
            int: "INTEGER",
            float: "DOUBLE",
            bool: "BOOLEAN",
        }

        schema: Dict[str, str] = {}

        for field_name, field_info in cls.model_fields.items():
            field_type = field_info.annotation

            # Handle Optional[...] annotations → typing.Union[T, NoneType]
            origin = get_origin(field_type)
            if origin is Union:  # Optional / Union
                non_none = [
                    arg for arg in get_args(field_type) if arg is not type(None)
                ]
                field_type = non_none[0] if non_none else field_type

            db_type = "VARCHAR"  # default fallback

            try:
                if isinstance(field_type, type) and issubclass(field_type, MixDataset):
                    db_type = field_type._get_db_type()
                elif field_type in type_map:
                    db_type = type_map[field_type]
            except TypeError:
                # field_type not suitable for issubclass, keep default
                pass

            schema[field_name] = db_type

        return schema

    def upload_files(self):
        """Upload any external files in this dataset"""
        # Simple implementation - can be extended as needed
        pass

    def validate_data(self) -> "MixDataset":
        """Basic data validation for the dataset"""
        # Add any basic validation logic here if needed
        return self

    def run(self, func):
        """Run a function with this dataset instance"""
        func(self)

    def append_data(self, rows: List["MixDataset"]):
        """Append data rows to the dataset"""
        raise NotImplementedError("This method is not implemented yet")

    def overwrite_data(self, rows: List["MixDataset"]):
        """Overwrite dataset with new data"""
        raise NotImplementedError("This method is not implemented yet")


class ExternalFile(MixDataset):
    """Represents a file external to the dataset"""

    path: str
    external_url: Optional[str] = None

    @classmethod
    def _get_db_type(cls):
        """External files are stored as URLs"""
        return "VARCHAR"

    def upload_to_dataset(self, dataset_name: str):
        """Upload this file to a dataset"""
        self.external_url = upload_file(dataset_name, self.path)
        return self.external_url


class ImageFile(ExternalFile):
    """Represents an image file"""

    pass


# Simple type aliases for common data types
VectorEmbedding = List[float]
URI = str

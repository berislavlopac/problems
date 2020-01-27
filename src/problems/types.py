from typing import Mapping, Optional, Union

from box import Box
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validate, validator_for
from rfc3986 import exceptions, URIReference, validators
from rfc3986.builder import URIBuilder


class ProblemType:
    __slots__ = ("identifier", "title", "detail", "extension")
    BANNED_EXTENSION_NAMES = {
        "detail",
        "extension",
        "identifier",
        "instance",
        "status",
        "title",
        "type",
    }

    DEFAULT_SCHEME = "https"
    ALLOWED_SCHEMES = {"about", "http", "https"}
    ALLOWED_HOSTS = {"example.com"}

    DEFAULT_HOST = "example.com"
    DEFAULT_TYPE = "about:blank"

    def __init__(
        self,
        identifier: Optional[str] = None,
        title: str = "",
        detail: str = "",
        *,
        extension: Optional[dict] = None,
    ):
        self.identifier = (
            self.DEFAULT_TYPE if identifier is None else self.validate_identifier(identifier)
        )
        self.title = title
        self.detail = detail
        self.extension = {} if extension is None else self.validate_extension(extension)

    @property
    def __dict__(self):
        return {key: getattr(self, key) for key in self.__slots__}

    def __iter__(self):
        return iter(self.__dict__.items())

    def __str__(self):
        return self.identifier

    @classmethod
    def validate_identifier(cls, identifier: Union[str, URIReference]) -> str:
        """
        Validate an identifier and convert it into an URI string.

        Args:
            identifier: Either a full URI or the identifier part.

        Raises:
            `ValueError` if the identifier is invalid.
        """
        uri = URIBuilder.from_uri(identifier)
        if not uri.host:
            if uri.path and not uri.path.startswith("/"):
                uri = uri.add_path(f"/{uri.path}")
            uri = uri.add_host(cls.DEFAULT_HOST)
        if not uri.scheme:
            uri = uri.add_scheme(cls.DEFAULT_SCHEME)
        uri = uri.finalize()
        validator = validators.Validator().require_presence_of("path")
        validator = validator.allow_schemes(*cls.ALLOWED_SCHEMES)
        validator = validator.allow_hosts(*cls.ALLOWED_HOSTS)
        try:
            validator.validate(uri)
        except exceptions.RFC3986Exception as ex:
            raise ValueError(f"Identifier '{uri.unsplit()}' is invalid: {ex.args[0]}") from ex
        else:
            return uri.unsplit()

    @classmethod
    def validate_extension(cls, extension: Mapping[str, Mapping]) -> Mapping[str, Mapping]:
        """
        Validate the value of a given extension.

        Args:
            extension: A mapping of field names and schema mappings.

        Raises:
            `ValueError` if a field has a name that is not allowed.
            `TypeError` if a schema is invalid.
        """
        if cls.BANNED_EXTENSION_NAMES & set(extension):
            raise ValueError(
                "Extension members can't have any of the"
                f" following names: {cls.BANNED_EXTENSION_NAMES}"
            )
        for field, schema in extension.items():
            validator = validator_for(schema)
            try:
                validator.check_schema(schema)
            except SchemaError as ex:
                raise TypeError(
                    f"Extension for the field '{field}' needs to be a valid JSON schema."
                ) from ex
        return extension

    @classmethod
    def validate_value(cls, value, schema):
        validate(value, schema, cls=validator_for(schema))
        return value

    def validate(self, field: str, value):
        try:
            schema = self.extension[field]
        except KeyError:
            raise ValueError(
                f"'{field}' is not a valid extension member "
                f"for problem type '{type(self).__name__}'."
            )
        return self.validate_value(value, schema)

    def format(self, template: str, data: dict) -> str:
        data = Box(data)
        try:
            return template.format(**data)
        except KeyError as ex:
            raise AttributeError(str(ex)) from ex

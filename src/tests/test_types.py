import pytest

from problems.types import ProblemType


def test_construct_blank_type():
    problem_type = ProblemType()
    assert problem_type.identifier == "about:blank"
    assert problem_type.title == ""
    assert problem_type.detail == ""
    assert problem_type.extension == {}


# identifier validation


def test_convert_blank_type_to_string():
    problem_type = ProblemType()
    assert str(problem_type) == "about:blank"


def test_identifier_must_not_be_empty():
    with pytest.raises(ValueError):
        ProblemType(identifier="")


def test_identifier_inserts_default_scheme():
    problem_type = ProblemType("//example.com/baz")
    assert problem_type.identifier == "https://example.com/baz"


@pytest.mark.parametrize("input", ("foo/bar", "/foo/bar"))
@pytest.mark.parametrize("expected", ("https://example.com/foo/bar",))
def test_identifier_inserts_default_scheme_and_host(input, expected):
    problem_type = ProblemType(input)
    assert problem_type.identifier == expected


def test_rejects_unallowed_hostname():
    with pytest.raises(ValueError) as ex:
        ProblemType("https://foo.bar/baz")
        assert str(ex).endswith(
            "Host was required to be one of ['example.com'] but was 'foo.bar'"
        )


def test_rejects_identifier_without_path():
    with pytest.raises(ValueError) as ex:
        ProblemType("https://example.com")
        assert str(ex).endswith("path was required but missing")


# extensions


@pytest.mark.parametrize("input", ProblemType.BANNED_EXTENSION_NAMES)
def test_extension_is_rejected_if_includes_class_attribute_names(input):
    with pytest.raises(ValueError) as ex:
        ProblemType(extension={input: {}})
        assert str(ex).endswith(f"Extension member name {input} is not allowed.")


def test_extension_is_rejected_if_not_valid_json_schema():
    with pytest.raises(TypeError) as ex:
        ProblemType(extension={"foo": []})
        assert str(ex).endswith("Extension for field 'foo' needs to be a valid JSON schema.")


# serialisation to dict


def test_convert_type_to_dict():
    problem_type = ProblemType(
        "https://example.com/foo",
        "Foo problem",
        "Foo fighters attack",
        extension={"bar": {}, "baz": {}},
    )
    assert dict(problem_type) == {
        "identifier": "https://example.com/foo",
        "title": "Foo problem",
        "detail": "Foo fighters attack",
        "extension": {"bar": {}, "baz": {}},
    }


def test_convert_blank_type_to_dict():
    problem_type = ProblemType()
    assert dict(problem_type) == {
        "identifier": "about:blank",
        "title": "",
        "detail": "",
        "extension": {},
    }


# formatting title and description


def test_format_title_simple():
    problem_type = ProblemType("https://example.com/foo", extension={"bar": {"type": "string"}})
    assert problem_type.format("test {foo}", {"foo": "bar baz bam"}) == "test bar baz bam"


def test_format_title_nested():
    nested_schema = {"foo": {"type": "object", "items": {"bar": {"type": "string"}}}}
    problem_type = ProblemType("https://example.com/foo", extension=nested_schema)
    assert (
        problem_type.format("test {foo.bar}", {"foo": {"bar": "bar baz bam"}})
        == "test bar baz bam"
    )


def test_format_title_raises_error_on_incorrect_nested_key():
    nested_schema = {"foo": {"type": "object", "items": {"bar": {"type": "string"}}}}
    problem_type = ProblemType("https://example.com/foo", extension=nested_schema)
    with pytest.raises(AttributeError) as ex:
        problem_type.format("test {foo.baa}", {"foo": {"bar": "bar baz bam"}})
    assert "object has no attribute 'baa'" in str(ex.value)

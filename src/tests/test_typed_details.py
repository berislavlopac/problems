import pytest
from jsonschema.exceptions import ValidationError

from problems.details import ProblemDetails
from problems.types import ProblemType


@pytest.fixture
def base_type():
    return ProblemType(
        identifier="//example.com/base",
        title="Base example type",
        detail="This is a base example type, imagine that!",
        extension={"foo": {"type": "string"}, "bar": {"type": "integer"}},
    )


def test_construct_details_with_type(base_type):
    details = ProblemDetails(problem_type=base_type, foo="bla bla", bar=123)
    assert details.type.identifier == "https://example.com/base"
    assert details.title == "Base example type"
    assert details.detail == "This is a base example type, imagine that!"
    assert details.data["foo"] == "bla bla"
    assert details.data["bar"] == 123


def test_construct_typed_details_with_data():
    problem_type = ProblemType(
        extension={"foo": {"type": "string"}, "baz": {"type": "integer"}}
    )
    details = ProblemDetails(problem_type=problem_type, foo="bar", baz=123)
    assert hasattr(details, "foo")
    assert details.foo == "bar"
    assert details.baz == 123
    assert not hasattr(details, "bar")


def test_construct_typed_details_with_incorrect_data_wrong_field():
    problem_type = ProblemType(
        extension={"foo": {"type": "string"}, "baz": {"type": "integer"}}
    )
    with pytest.raises(ValueError) as ex:
        ProblemDetails(problem_type=problem_type, foo="bar", baa=123)
    assert "'baa' is not a valid extension member for problem type 'ProblemType'." in str(
        ex.value
    )


def test_construct_typed_details_with_incorrect_data_wrong_value():
    problem_type = ProblemType(
        extension={"foo": {"type": "string"}, "baz": {"type": "integer"}}
    )
    with pytest.raises(ValidationError) as ex:
        ProblemDetails(problem_type=problem_type, foo="bar", baz="123")
    assert "'123' is not of type 'integer'" in str(ex.value)


def test_convert_typed_details_with_data_to_dict():
    problem_type = ProblemType(
        extension={"foo": {"type": "string"}, "baz": {"type": "integer"}}
    )
    details = ProblemDetails(problem_type=problem_type, foo="bar", baz=123)
    result = dict(details)
    assert result == {
        "type": "about:blank",
        "title": "",
        "detail": "",
        "status": None,
        "foo": "bar",
        "baz": 123,
    }

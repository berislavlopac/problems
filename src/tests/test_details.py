from problems.details import ProblemDetails
from http import HTTPStatus


def test_construct_blank_details():
    details = ProblemDetails()
    assert details.type.identifier == "about:blank"
    assert details.title == ""
    assert details.detail == ""
    assert details.status is None


def test_construct_typeless_details_with_title_and_detail():
    details = ProblemDetails(title="Foo", detail="Bar")
    assert details.type.identifier == "about:blank"
    assert details.title == "Foo"
    assert details.detail == "Bar"


def test_construct_typeless_details_with_status():
    details = ProblemDetails(status=HTTPStatus.OK)
    assert details.status == 200


def test_construct_typeless_details_with_integer_status():
    details = ProblemDetails(status=200)
    assert details.status is HTTPStatus.OK


def test_convert_blank_details_to_dict():
    details = ProblemDetails()
    result = dict(details)
    assert result == {
        "type": "about:blank",
        "title": "",
        "detail": "",
        "status": None,
    }

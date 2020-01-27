from http import HTTPStatus
from typing import Optional, Union

from problems.types import ProblemType


class ProblemDetails:
    def __init__(
        self,
        *,
        problem_type: Optional[ProblemType] = None,
        title: Optional[str] = None,
        detail: Optional[str] = None,
        status: Optional[Union[int, HTTPStatus]] = None,
        **kwargs,
    ):
        self.type = ProblemType() if problem_type is None else problem_type
        self.data = self.validate_data(kwargs)
        if title is None:
            title = self.type.title
        self.title = self.type.format(title, self.data)
        if detail is None:
            detail = self.type.detail
        self.detail = self.type.format(detail, self.data)
        self.status = None if status is None else HTTPStatus(status)

    def __iter__(self):
        yield "type", self.type.identifier
        yield "title", self.title
        yield "detail", self.detail
        yield "status", self.status
        yield from self.data.items()

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

    def validate_data(self, data):
        return {field: self.type.validate(field, value) for field, value in data.items()}

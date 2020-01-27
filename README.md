Problem Details
===============

`problems` is a Python implementation of [RFC 7870](https://tools.ietf.org/html/rfc7807) "Problem Details for HTTP APIs". Its purpose is to manage a set of known error types, as well to simplify construction of HTTP response payloads.

Problem Types
-------------

This component manages a database of all know problem types. Each problem type definition includes the following information:

1. `identifier`: A URI-compliant string, uniquely identifying the type. If it does not include a schema it is assumed to be `http(s)`, and if it also does not include the hostname a global default **must** be provided.
2. `title`: A string defining the problem type name. It can be in the form of a template (TODO: define the template format), which can be populated by the values from the instance values.
3. `description`: A string defining the description of the problem. It can be in the form of a template (TODO: define the format), which can be populated by the values from the instance.
4. `extensions`: A structure of any fields that a problem instance could include, in addition to the ones defined by the RFC 7870. This structure is defined in the form of JSON Schema.

The database can be in a number of formats: a JSON file, a relational database etc. There should be a simple mechanism to extend the storage engine.


Problem Details
---------------

This component is a library for creation and management of `ProblemDetails` instances; each instance has a type, title and description, as well as any additional information following the structure defined in the `extensions` element of the type. A `ProblemDetails` instance has the following functionality:

* create an instance of a certain type
* populate the instance with required information
* validate the information against the type definition
* serialise the information into a JSON-compatible structure to use as an API response

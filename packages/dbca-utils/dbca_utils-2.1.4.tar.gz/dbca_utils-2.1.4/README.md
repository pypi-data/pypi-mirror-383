# Overview

DBCA Django utility classes and functions.

## Requirements

- Python 3.10 or later
- Django 4.2 or later

## Development

Dependencies for this project are managed using [uv](https://docs.astral.sh/uv/).
With uv installed, change into the project directory and run:

    uv sync

Activate the virtualenv like so:

    source .venv/bin/activate

Run unit tests using `pytest` (or `tox`, to test against multiple Python versions):

    pytest -sv
    tox -v

## Releases

Tagged releases are built and pushed to PyPI automatically using a GitHub
workflow in the project. Update the project version in `pyproject.toml` and
tag the required commit with the same value to trigger a release. Packages
can also be built and uploaded manually, if desired.

Build the project locally using uv, [publish to the PyPI registry](https://docs.astral.sh/uv/guides/publish/#publishing-your-package)
using the same tool if you require:

    uv build
    uv publish

## Installation

1. Install via uv/pip/etc.: `pip install dbca-utils`

## SSO Login Middleware

This will automatically login and create users using headers from an upstream proxy (REMOTE_USER and some others).
The logout view will redirect to a separate logout page which clears the SSO session.

### Usage

Add `dbca_utils.middleware.SSOLoginMiddleware` to `settings.MIDDLEWARE` (after both of
`django.contrib.sessions.middleware.SessionMiddleware` and
`django.contrib.auth.middleware.AuthenticationMiddleware`.
Ensure that `AUTHENTICATION_BACKENDS` contains `django.contrib.auth.backends.ModelBackend`,
as this middleware depends on it for retrieving the logged in user for a session.
Note that the middleware will still work without it, but will reauthenticate the session
on every request, and `request.user.is_authenticated` won't work properly/will be false.

Example:

```python
MIDDLEWARE = [
    ...,
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dbca_utils.middleware.SSOLoginMiddleware'
    ...,
]
```

## Audit model mixin

`AuditMixin` is an extension of `Django.db.model.Model` that adds a number of additional fields:

- `creator` - FK to `AUTH_USER_MODEL`, used to record the object creator
- `modifier` - FK to `AUTH_USER_MODEL`, used to record who the object was last modified by
- `created` - a timestamp that is set on initial object save
- `modified` - an auto-updating timestamp (on each object save)

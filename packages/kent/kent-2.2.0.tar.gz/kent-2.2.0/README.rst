====
Kent
====

Kent is a service for debugging and integration testing Sentry.

:Code:          https://github.com/mozilla-services/kent/
:Issues:        https://github.com/mozilla-services/kent/issues
:License:       MPL v2


Goals
=====

Goals of Kent:

1. make it possible to debug ``before_send`` and ``before_breadcrumb``
   sanitization code when using sentry-sdk
2. make it possible to debug other Sentry event submission payload issues
3. make it possible to write integration tests against a fake Sentry instance


Quick start
===========

Installing and running on your local machine
--------------------------------------------

1. Install Kent.

   (Recommended) With `uv <https://docs.astral.sh/uv/>`__::

      uv tool install kent

   Install from a git clone::

      uv tool install .

2. Run Kent::

      kent-server run [-h HOST] [-p PORT]
      

Running in a Docker container
-----------------------------

I'm using something like this::

    FROM python:3.13-slim-bookworm

    WORKDIR /app/

    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1

    RUN groupadd -r kent && useradd --no-log-init -r -g kent kent

    RUN pip install -U 'pip>=8' && \
        pip install --no-cache-dir 'kent==<VERSION>'

    USER kent

    ENTRYPOINT ["/usr/local/bin/kent-server"]
    CMD ["run"]


Make sure to replace ``<VERSION>`` with the version of Kent you want to use.
See https://pypi.org/project/kent for releases.

Then::

    $ docker build -t kent:latest .
    $ docker run --init --rm --publish 8000:8000 kent:latest run --host 0.0.0.0 --port 8000


Things to know about Kent
=========================

Kent is the fakest of fake Sentry servers. You can set up a Sentry DSN to point
to Kent and have your application send events to it.

Kent is for testing sentry-sdk things. Kent is not for testing Relay.

Kent is a refined fake Sentry service and doesn't like fast food.

Kent will keep track of the last 100 payloads it received in memory. Nothing is
persisted to disk.

You can access the list of events and event data with your web browser by going
to Kent's index page.

You can also access it with the API. This is most useful for integration tests
that want to assert things about events.

``GET /api/eventlist/``
    List of all events in memory with a unique event id.

``GET /api/event/EVENT_ID``
    Retrieve the payload for a specific event by id.

``POST /api/flush/``
    Flushes the event manager of all events.

You can use multiple project ids. Kent will keep the events separate.

If you run ``kent-server run`` with the defaults, your DSN is::

    http://public@localhost:5000/1    for project id 1
    http://public@localhost:5000/2    for project id 2
    etc.


Kent definitely works with:

* Python sentry-sdk client
* Python raven client (deprecated)

I don't know about anything else. If you use Kent with another Sentry client,
add an issue with details or a pull request to update the README.


Development
===========

Requirements: Python, `uv <https://docs.astral.sh/uv/>`__, `just
<https://just.systems/>`__

Create a development environment::

    just devenv

Then you can use rules listed in the ``justfile``::

    just

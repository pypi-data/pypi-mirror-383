OpenTelemetry Arq Instrumentation
===================================================

This library provides automatic and manual instrumentation of `arq <https://github.com/python-arq/arq>`_

auto-instrumentation using the opentelemetry-instrumentation package is also supported.


Installation
------------

.. code-block:: shell

    pip install opentelemetry-instrumentation-arq

Usage
------

.. code-block:: python

    from opentelemetry.instrumentation.arq import ArqInstrumentor

    ArqInstrumentor.instrument()

Test
------

.. code-block:: shell

    python -m unittest tests/*


References
----------

* `OpenTelemetry Project <https://opentelemetry.io/>`_
* `OpenTelemetry Python Examples <https://github.com/open-telemetry/opentelemetry-python/tree/main/docs/examples>`_
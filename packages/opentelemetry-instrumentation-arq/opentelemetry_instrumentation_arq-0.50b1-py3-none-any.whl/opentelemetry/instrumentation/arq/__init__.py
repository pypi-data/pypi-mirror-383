import os
from typing import Callable, Collection
import functools

from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.propagate import extract, inject
from opentelemetry.propagators import textmap
from wrapt import wrap_function_wrapper, wrap_object_attribute

from arq import ArqRedis
from arq.cron import CronJob
from arq.jobs import Job
from arq.worker import Function

from .package import _instruments
from .version import __version__

__all__ = ["ArqInstrumentor"]

CARRIER_KEYWORD = "_carrier"
# Now only ignore the server-side
EXCLUDE_LIST_ENV = "OTEL_PYTHON_ARQ_EXCLUDED_TASKS"


def get_excluded_tasks() -> tuple[str]:
    excluded_tasks = tuple()
    if EXCLUDE_LIST_ENV in os.environ:
        excluded_tasks = tuple(set(map(lambda x: x.strip(), os.environ[EXCLUDE_LIST_ENV].split(","))))
    return excluded_tasks


class ContextSetter(textmap.Setter[dict]):
    def set(self, carrier: dict, key: str, value: str) -> None:
        if carrier is None or key is None:
            return

        if value:
            if carrier.get(CARRIER_KEYWORD) is not None:
                carrier[CARRIER_KEYWORD][key] = value
            else:
                carrier[CARRIER_KEYWORD] = {key: value}


class ContextGetter(textmap.Getter[dict]):
    def get(self, carrier: dict | None, key: str) -> list[str] | None:
        if carrier is None:
            return None

        if base_value := carrier.pop(CARRIER_KEYWORD, None):
            if value := base_value.get(key):
                return [value]

        return None

    def keys(self, carrier: dict | None) -> list[str]:
        if carrier is None:
            return []
        return list(carrier.keys())


_setter = ContextSetter()
_getter = ContextGetter()


class ArqInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get("tracer_provider")

        tracer = trace.get_tracer(
            __name__,
            __version__,
            tracer_provider=tracer_provider,
            schema_url="https://opentelemetry.io/schemas/1.11.0",
        )

        wrap_function_wrapper(ArqRedis, "enqueue_job", _wrap_client(tracer))
        for m, attr in [("arq.cron", "CronJob.coroutine"), ("arq.worker", "Function.coroutine")]:
            wrap_object_attribute(
                m,
                attr,
                _wrap_coroutine,
                (),
                {"tracer": tracer, "excluded_tasks": get_excluded_tasks()},
            )

    def _uninstrument(self, **kwargs):
        unwrap(ArqRedis, "enqueue_job")
        unwrap(CronJob, "coroutine")
        unwrap(Function, "coroutine")


def _wrap_client(tracer: trace.Tracer):
    async def _traced_client(func, instance: ArqRedis, args, kwargs):
        function_name = args[0]
        with tracer.start_as_current_span(function_name, kind=trace.SpanKind.CLIENT) as span:
            inject(kwargs, setter=_setter)
            span.set_attribute("arq.job.name", function_name)
            result: Job | None = await func(*args, **kwargs)
            if result:
                span.set_attribute("arq.job.id", result.job_id)
                span.set_attribute("arq.job.queue", result._queue_name)
            else:
                span.set_status(trace.StatusCode.ERROR, "Job with this ID already exists")

        return result

    return _traced_client


def _wrap_coroutine(value: Callable, *, tracer: trace.Tracer, excluded_tasks: tuple[str]):
    @functools.wraps(value)
    async def _fake_coroutine(ctx: dict, *args, **kwargs):
        function_name = value.__name__

        if function_name in excluded_tasks:
            return await value(ctx, *args, **kwargs)

        with tracer.start_as_current_span(
            function_name,
            kind=trace.SpanKind.SERVER,
            context=extract(carrier=kwargs, getter=_getter),
        ) as span:
            span.set_attribute("arq.job.name", function_name)
            span.set_attribute("arq.job.id", ctx.get("job_id"))
            span.set_attribute("arq.job.try", ctx.get("job_try"))
            span.set_attribute("arq.job.score", ctx.get("score"))
            result = await value(ctx, *args, **kwargs)
            span.set_status(trace.StatusCode.OK)
            return result

    return _fake_coroutine

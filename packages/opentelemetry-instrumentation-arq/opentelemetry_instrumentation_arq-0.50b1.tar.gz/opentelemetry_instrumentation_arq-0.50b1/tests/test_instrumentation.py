import unittest

from arq import ArqRedis, cron, func
from wrapt import BoundFunctionWrapper, ObjectProxy

from opentelemetry.instrumentation.arq import ArqInstrumentor


async def test(ctx):
    """Test function"""
    return 2


class TestInstrument(unittest.IsolatedAsyncioTestCase):
    async def test_instrument(self) -> None:
        instrumentation = ArqInstrumentor()
        instrumentation.instrument()

        self.assertTrue(isinstance(ArqRedis.enqueue_job, BoundFunctionWrapper))

        test_cases = [cron(test), func(test)]

        for case in test_cases:
            self.assertEqual(await case.coroutine({}, *list(), **dict()), 2)
            self.assertTrue(case.coroutine, ObjectProxy)

        # test uninstrument
        instrumentation.uninstrument()
        test_cases = [cron(test), func(test)]
        self.assertFalse(isinstance(ArqRedis.enqueue_job, BoundFunctionWrapper))
        for case in test_cases:
            self.assertFalse(isinstance(case.coroutine, ObjectProxy))

    async def test_wrap(self):
        instrumentation = ArqInstrumentor()
        instrumentation.instrument()
        test_cases = [cron(test), func(test)]
        for case in test_cases:
            self.assertEqual(case.coroutine.__doc__, test.__doc__)
            self.assertEqual(case.coroutine.__name__, test.__name__)


if __name__ == "__main__":
    unittest.main()

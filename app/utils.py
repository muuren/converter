import asyncio
import logging
from typing import Type, Any, Union, Tuple

logger = logging.getLogger(__name__)


class Retry:
    """Retrying async decorated function on exception.

        Options 'on_exc' and 'exclude_exc' will match exact exception type you pass
        regardless of exception hierarchy. Do not set both.

        Args:
            attempts: how many times to try
            delay: time wait (seconds) between attempts
            on_exc: a collection of exception type to retry only.
            exclude_exc: does not retry on the given exceptions.
            If 'on_exc' and 'exclude_exc' not set then retry always.

        Example:
            >>> @Retry(attempts=3, exclude_exc=(ConnectionError,))
            >>> async def my_function(args):
            >>>    ...

        """
    def __init__(
        self,
        attempts: int = 3,
        delay: int | float = 2,
        on_exc: Union[Tuple, Tuple[Type[Any]]] = (),
        exclude_exc: Union[Tuple, Tuple[Type[Any]]] = (),
    ):
        self.attempts = attempts + 1
        self.delay = delay
        self.include_exc = on_exc
        self.exclude_exc = exclude_exc

    def __call__(self, func):
        async def wrapped_f(*args, **kwargs):
            retry_left = self.attempts

            while retry_left > 0:
                retry_left -= 1
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if retry_left == 0 or self._stop_retry(e):
                        raise
                    logger.debug(
                        f"<{e.__class__.__name__}> raised while running '{func.__name__}': "
                        f"retrying after {self.delay} sec. (attempts={retry_left})"
                    )
                if self.delay:
                    await asyncio.sleep(self.delay)
        return wrapped_f

    def _stop_retry(self, exp) -> bool:
        """Check if exception match given conditions for retry."""

        if not self.include_exc and not self.exclude_exc:
            return False

        if self.include_exc and exp.__class__ not in self.include_exc:
            return True

        if self.exclude_exc and exp.__class__ in self.exclude_exc:
            return True
        return False

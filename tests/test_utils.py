import pytest
import time

from app.utils import Retry


async def unreliable_function(exc, cnt):
    cnt()
    raise exc


async def reliable_function(cnt):
    cnt()
    return 'ok'


@pytest.mark.parametrize('attempts, exc', [(4, TypeError), (0, ConnectionError)])
@pytest.mark.asyncio
async def test_retry_do_retry_on_exception(call_counter, attempts, exc):
    func = Retry(attempts=attempts, delay=0)(unreliable_function)
    with pytest.raises(exc):
        await func(exc, call_counter)
    assert call_counter.calls == attempts + 1


@pytest.mark.asyncio
async def test_do_not_retry_on_success_decorated(call_counter, attempts=3):
    func = Retry(attempts=attempts, delay=0)(reliable_function)
    result = await func(call_counter)
    assert call_counter.calls == 1
    assert result == 'ok'


@pytest.mark.parametrize('attempts, delay', [(2, 0.2), (1, 0.6), (0, 3)])
@pytest.mark.asyncio
async def test_retry_do_delay_before_attempt(call_counter, attempts, delay, exc=TimeoutError):
    func = Retry(attempts=attempts, delay=delay)(unreliable_function)
    start_time = time.time()
    with pytest.raises(exc):
        await func(exc, call_counter)
    run_time = time.time() - start_time
    assert round(run_time, 1) == attempts * delay


exc_match = [
    ((AttributeError,), AttributeError),
    ((TimeoutError, ConnectionError, IndentationError), ConnectionError),
]


@pytest.mark.parametrize('on_exp, func_exp', exc_match)
@pytest.mark.asyncio
async def test_retry_on_included_exc_only(call_counter, on_exp, func_exp, attempts=1):
    func = Retry(attempts=attempts, delay=0, on_exc=on_exp)(unreliable_function)

    with pytest.raises(func_exp):
        await func(func_exp, call_counter)
    assert call_counter.calls == attempts + 1


exc_not_match = [
    ((AttributeError,), MemoryError),
    ((TimeoutError, ConnectionError), OSError),
    ((OSError,), TimeoutError)
]


@pytest.mark.parametrize('on_exp, func_exp', exc_not_match)
@pytest.mark.asyncio
async def test_no_retry_if_not_match_included_exc(call_counter, on_exp, func_exp, attempts=1):
    func = Retry(attempts=attempts, delay=0, on_exc=on_exp)(unreliable_function)

    with pytest.raises(func_exp):
        await func(func_exp, call_counter)
    assert call_counter.calls == 1


@pytest.mark.parametrize('exclude_exc, func_exp', exc_match)
@pytest.mark.asyncio
async def test_no_retry_if_match_excluded_exc(call_counter, exclude_exc, func_exp, attempts=1):
    func = Retry(attempts=attempts, delay=0, exclude_exc=exclude_exc)(unreliable_function)

    with pytest.raises(func_exp):
        await func(func_exp, call_counter)
    assert call_counter.calls == 1


@pytest.mark.parametrize('exclude_exc, func_exp', exc_not_match)
@pytest.mark.asyncio
async def test_retry_if_not_match_excluded_exc(call_counter, exclude_exc, func_exp, attempts=1):
    func = Retry(attempts=attempts, delay=0, exclude_exc=exclude_exc)(unreliable_function)

    with pytest.raises(func_exp):
        await func(func_exp, call_counter)
    assert call_counter.calls == attempts + 1

import asyncio
import time
from dataclasses import asdict
from math import isclose
from unittest.mock import patch

import aiohttp
import pytest
import pytest_asyncio
from pytest import approx, fixture

from aioairq import AirQ
from aioairq.core import ComparisonSummary, identify_warming_up_sensors

TIMEOUT_MAX = 5


@fixture
def ip():
    return "192.168.0.0"


@fixture
def mdns():
    return "a123f_air-q.local"


@fixture
def passw():
    return "password"


@pytest_asyncio.fixture
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@fixture(params=["ip", "mdns"])
def valid_address(request, ip, mdns):
    return {"ip": ip, "mdns": mdns}[request.param]


@pytest.mark.asyncio
async def test_constructor(valid_address, passw, session):
    airq = AirQ(valid_address, passw, session)
    assert airq.anchor == "http://" + valid_address
    assert not airq._session.closed


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "return_original_keys,data,expected",
    [
        (
            True,
            {"co2": [604.0, 68.1], "Status": "OK", "pm1": [0, 10], "pm2_5": [0, 10]},
            {"co2": [604.0, 68.1], "Status": "OK", "pm1": [0, 10], "pm2_5": [0, 10]},
        ),
        (
            False,
            {"co2": [604.0, 68.1], "Status": "OK", "pm1": [0, 10], "pm2_5": [0, 10]},
            {"co2": [604.0, 68.1], "Status": "OK", "pm1": [0, 10], "pm2_5": [0, 10]},
        ),
        (
            True,
            {
                "co2": [604.0, 68.1],
                "Status": "OK",
                "pm1_SPS30": [0, 10],
                "pm2_5_SPS30": [0, 10],
            },
            {
                "co2": [604.0, 68.1],
                "Status": "OK",
                "pm1_SPS30": [0, 10],
                "pm2_5_SPS30": [0, 10],
            },
        ),
        (
            False,
            {
                "co2": [604.0, 68.1],
                "Status": "OK",
                "pm1_SPS30": [0, 10],
                "pm2_5_SPS30": [0, 10],
            },
            {"co2": [604.0, 68.1], "Status": "OK", "pm1": [0, 10], "pm2_5": [0, 10]},
        ),
    ],
)
async def test_data_key_filtering(
    return_original_keys, data, expected, valid_address, passw, session
):
    airq = AirQ(valid_address, passw, session)
    with patch("aioairq.AirQ.get", return_value=data):
        actual = await airq.get_latest_data(
            return_uncertainties=True, return_original_keys=return_original_keys
        )
    assert actual == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {
                "timestamp": 1621223828000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 90 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": [63.0, 4.0],
                "temperature": [18.9, 0.6],
            },
            {"co", "o3"},
        ),
        (
            # The following is a strange looking data set but I have seen it.
            # Expected behaviour: consider co & o3 as warming up
            {
                "timestamp": 16212.084000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 1 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 1 s",
                },
                "humidity": [63.26, 4.27],
                "temperature": [18.92, 0.6],
                "co": [0.916, 0.22],
                "o3": [27.17, 2.32],
            },
            {"co", "o3"},
        ),
        (
            {
                "timestamp": 1621226746000,
                "Status": "OK",
                "humidity": [64.0, 4.0],
                "temperature": [18.8, 0.6],
                "co": [0.92, 0.22],
                "o3": [27.228, 2.31],
            },
            set(),
        ),
    ],
)
def test_warmup_sensor_identification(data, expected):
    actual = identify_warming_up_sensors(data)
    assert actual == expected


@pytest.mark.parametrize(
    "previous,current,expected",
    [
        (
            {
                "timestamp": 1621223828000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 90 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": [63.0, 4.0],
                "temperature": [18.9, 0.6],
            },
            {
                "timestamp": 1621223838000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 90 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": [64.0, 4.0],
                "temperature": [17.9, 0.7],
            },
            ComparisonSummary(
                warming_up={"co", "o3"},
                difference={
                    "timestamp": 10_000,
                    "humidity": [1.0, 0.0],
                    "temperature": [-1.0, 0.1],
                },
            ),
        ),
        # dropped uncertainties
        (
            {
                "timestamp": 1621223828000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 90 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": 63.0,
                "temperature": 18.9,
            },
            {
                "timestamp": 1621223838000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 90 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": 64.0,
                "temperature": 17.9,
            },
            ComparisonSummary(
                warming_up={"co", "o3"},
                difference={"timestamp": 10_000, "humidity": 1.0, "temperature": -1.0},
            ),
        ),
        # emulate a reboot
        (
            {
                "timestamp": 1621226746000,
                "Status": "OK",
                "humidity": [64.0, 4.0],
                "temperature": [18.8, 0.6],
                "co": [0.9, 0.2],
                "o3": [27.3, 2.3],
            },
            {
                "timestamp": 1621226796000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 90 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": [60.0, 4.0],
                "temperature": [10.8, 0.6],
            },
            ComparisonSummary(
                missing_keys={"co", "o3"},
                warming_up={"co", "o3"},
                difference={
                    "timestamp": 50_000,
                    "humidity": [-4.0, 0.0],
                    "temperature": [-8.0, 0.0],
                },
            ),
        ),
        # emulate a disappearance of a sensor
        (
            {
                "timestamp": 1621226746000,
                "Status": "OK",
                "humidity": [64.0, 4.0],
                "temperature": [18.8, 0.6],
                "co": [0.9, 0.2],
                "o3": [27.3, 2.3],
            },
            {
                "timestamp": 1621226796000,
                "Status": {
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": [60.0, 4.0],
                "temperature": [10.8, 0.6],
            },
            ComparisonSummary(
                missing_keys={"co", "o3"},
                warming_up={"o3"},
                unaccountably_missing_keys={"co"},
                difference={
                    "timestamp": 50_000,
                    "humidity": [-4.0, 0.0],
                    "temperature": [-8.0, 0.0],
                },
            ),
        ),
        # emulate a new sensor appearing
        (
            {
                "timestamp": 1621226746000,
                "Status": "OK",
                "humidity": [64.0, 4.0],
                "temperature": [18.8, 0.6],
                "o3": [27.3, 2.3],
            },
            {
                "timestamp": 1621226796000,
                "Status": {
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "co": [0.9, 0.2],
                "humidity": [60.0, 4.0],
                "temperature": [10.8, 0.6],
            },
            ComparisonSummary(
                missing_keys={"o3"},
                warming_up={"o3"},
                new_values={"co": [0.9, 0.2]},
                difference={
                    "timestamp": 50_000,
                    "humidity": [-4.0, 0.0],
                    "temperature": [-8.0, 0.0],
                },
            ),
        ),
        # The following is a strange looking data set but I have seen it.
        # Expected behaviour: consider co & o3 as warming up
        (
            {
                "timestamp": 1621223828000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 90 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": 63.0,
                "temperature": 18.9,
            },
            {
                "timestamp": 1621223838000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 1 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 1 s",
                },
                "humidity": 64.0,
                "temperature": 17.9,
                "co": [0.9, 0.2],
                "o3": [27.3, 2.3],
            },
            ComparisonSummary(
                warming_up={"co", "o3"},
                new_values={"co": [0.9, 0.2], "o3": [27.3, 2.3]},
                difference={"timestamp": 10_000, "humidity": 1.0, "temperature": -1.0},
            ),
        ),
        # Sensors completed their warmup
        (
            {
                "timestamp": 1621223828000,
                "Status": {
                    "co": "co sensor still in warm up phase; waiting time = 90 s",
                    "o3": "o3 sensor still in warm up phase; waiting time = 90 s",
                },
                "humidity": 63.0,
                "temperature": 18.9,
            },
            {
                "timestamp": 1621223928000,
                "Status": "OK",
                "humidity": 64.0,
                "temperature": 17.9,
                "co": [0.9, 0.2],
                "o3": [27.3, 2.3],
            },
            ComparisonSummary(
                new_values={"co": [0.9, 0.2], "o3": [27.3, 2.3]},
                difference={"timestamp": 100_000, "humidity": 1.0, "temperature": -1.0},
            ),
        ),
    ],
)
def test_data_comparison(previous, current, expected):
    actual_dict = asdict(ComparisonSummary.compare(current, previous))
    expected_dict = asdict(expected)
    actual_difference = actual_dict.pop("difference")
    expected_difference = expected_dict.pop("difference")
    assert actual_dict == expected_dict
    for sensor_name, actual_diff in actual_difference.items():
        assert actual_diff == approx(expected_difference[sensor_name])


@pytest_asyncio.fixture
async def hanging_server():
    """
    TCP server that accepts connections but never sends data.
    This makes HTTP clients wait forever for the status line / headers.
    """
    hang_for_seconds = TIMEOUT_MAX * 10

    async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            # Keep the connection open; don't read or write HTTP data.
            await asyncio.sleep(hang_for_seconds)
        finally:
            try:
                # Ask asyncio to close the underlying transport...
                writer.close()
                # ...then wait for it to do so
                await writer.wait_closed()
                # Also, ignore any possible edge case during this teardown
            except Exception:
                pass

    # pick any free ephemeral port on localhost and bind the server to it
    server = await asyncio.start_server(handler, host="127.0.0.1", port=0)
    # get the actual selected port
    port = server.sockets[0].getsockname()[1]
    try:
        yield ("127.0.0.1", port)
    finally:
        server.close()
        server.wait_closed()


@pytest.mark.asyncio
async def test_hanging_response_triggers_total_timeout(hanging_server, session):
    """Test that AirQ respects its timeout when querying a hanging server.

    Hanging server will acknowledge the connection but won't respond to read request.
    This test checks that the airq respects the timeout that was specified to it.
    """

    timeout_expected = TIMEOUT_MAX / 10
    host, port = hanging_server
    airq = AirQ(f"{host}:{port}", "dummy_password", session, timeout=timeout_expected)

    started = time.perf_counter()

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(airq.get("ping"), TIMEOUT_MAX)

    elapsed = time.perf_counter() - started

    assert isclose(
        elapsed, timeout_expected, abs_tol=0.1, rel_tol=0.1
    ), f"Elapsed {elapsed:.3f}s suggests no read/total timeout was enforced"

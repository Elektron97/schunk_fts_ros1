# Run tests locally

Inside the dummy's package, install test-related dependencies with

```bash
pip install --user pytest coverage
```

You can run the tests either directly in this folder with `pytest .` or with more output through

```bash
coverage run -m pytest .
coverage report  # for console output
coverage html    # for web-based output
```

## Run tests with the FTS dummy
By default, the test fixture starts the workspace dummy automatically when no
`FTS_HOST` and `FTS_PORT` environment variables are set. The pytest summary shows
which sensor was used, for example:

```text
=== Sensor Summary ===
Sensor kind: dummy-workspace
Sensor used: 127.0.0.1
Port used: 8082
======================
```

You can also start the dummy manually:

1. Navigate into the `schunk_fts_dummy` repo and start the dummy with
    ```bash
    cargo run
    ```

2. Set environment variables in the terminals in which you test
    ```bash
    export FTS_HOST="127.0.0.1"
    export FTS_PORT=8082
    ```
    The tests will then connect to the FTS dummy.

## Run tests with a real sensor
Use a real sensor only when it is safe for automated tests to open TCP/UDP
connections, start and stop streaming, and call supported commands such as tare.
The tests may also configure the UDP output-rate parameter before streaming.

Set the real sensor endpoint explicitly in every terminal that runs tests:

```bash
export FTS_HOST="10.49.60.117"
export FTS_PORT=82
```

Then run the tests as usual:

```bash
pytest . -rs
```

The pytest summary should report the explicit environment target:

```text
=== Sensor Summary ===
Sensor kind: env
Sensor used: <IP_ADDRESS>
Port used: 82
======================
```

If you want the fixture's automatic real-sensor fallback instead of explicit
`FTS_HOST`/`FTS_PORT`, set the fallback endpoint and leave `FTS_HOST` and
`FTS_PORT` unset:

```bash
export FTS_REAL_HOST="<IP_ADDRESS>"
export FTS_REAL_PORT=82
unset FTS_HOST
unset FTS_PORT
```

The automatic fallback is only used when no dummy is already reachable and the
workspace dummy cannot be started.

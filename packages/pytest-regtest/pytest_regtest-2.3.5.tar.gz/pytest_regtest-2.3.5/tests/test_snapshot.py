def test_snapshot_handler_changed(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            snapshot.check(np.array([1, 2, 3, 4.0]))
        """
    )
    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    testdir.makepyfile(
        """
        import pandas as pd
        import numpy as np

        def test_snapshot(snapshot):
            df = pd.DataFrame(
                dict(a=np.array([1, 2, 3, 4.0]))
            )
            snapshot.check(df)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot not recorded yet:",
            "    > snapshot.check(df)",
            "    snapshot handler could not load recorded object, maybe type changed?",
            "         a",
            "    0  1.0",
            "    1  2.0",
            "    2  3.0",
            "    3  4.0",
        ]
    )

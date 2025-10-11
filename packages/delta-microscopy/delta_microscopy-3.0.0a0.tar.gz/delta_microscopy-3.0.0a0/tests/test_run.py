"""
Created on Mon Nov  8 10:08:21 2021.

@author: jeanbaptiste
"""

from pathlib import Path

import delta
from delta.pipeline import Position

TEST_DIR = Path(__file__).parent / "data"


def test_run_mothermachine_tif():
    path = TEST_DIR / "movie_mothermachine_tif/Position{p}Channel{c}Frames{t}.tif"

    args = delta.cli.parse_args(["run", "-c", "mothermachine", "-i", path.as_posix()])

    delta.cli._run(args)

    actual1 = Position.load_netcdf(path.parent / "delta_results/Position000001.nc")
    expected1 = Position.load_netcdf(path.parent / "expected_results/Position000001.nc")
    assert actual1 == expected1

    actual2 = Position.load_netcdf(path.parent / "delta_results/Position000002.nc")
    expected2 = Position.load_netcdf(path.parent / "expected_results/Position000002.nc")
    assert actual2 == expected2


def test_run_2D_nd2():  # noqa: N802
    path = TEST_DIR / "movie_2D_nd2/test.nd2"

    args = delta.cli.parse_args(["run", "-c", "2D", "-i", path.as_posix()])

    delta.cli._run(args)

    actual = Position.load_netcdf(path.parent / "test_delta_results/Position000000.nc")
    expected = Position.load_netcdf(
        path.parent / "test_expected_results/Position000000.nc"
    )
    assert actual == expected


def test_run_2D_tif():  # noqa: N802
    path = TEST_DIR / "movie_2D_tif/Position{p}Channel{c}Frame{t}.tif"

    args = delta.cli.parse_args(
        ["run", "-c", "2D", "-i", path.as_posix(), "--frames", "1-4"]
    )

    delta.cli._run(args)

    actual = Position.load_netcdf(path.parent / "delta_results/Position000001.nc")
    expected = Position.load_netcdf(path.parent / "expected_results/Position000001.nc")
    assert actual == expected

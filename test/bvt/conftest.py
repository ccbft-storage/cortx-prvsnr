import pytest
import argparse

def pytest_addoption(parser):
    parser.addoption(
        "--bvt-repo-path", action='store',
        default='./eos-test.tgz',
        help="path to eos-test repo tar gzipped file"
    )
    parser.addoption(
        "--bvt-test-targets", action='store',
        default='avocado_test/bvt_test.py',
        help="bvt test targets to run"
    )
    parser.addoption(
        "--bvt-results-path", action='store',
        default='./bvt.job-results.tgz',
        help="path to tar gzipped archive with bvt test job result"
    )


@pytest.fixture(scope="session")
def options_list(options_list):
    return (
        options_list +
        ["bvt-repo-path", "bvt-test-targets", "bvt-results-path"]
    )

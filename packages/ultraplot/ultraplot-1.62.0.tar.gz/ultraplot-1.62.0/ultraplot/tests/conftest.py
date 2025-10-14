import os, shutil, pytest, re, numpy as np, ultraplot as uplt
from pathlib import Path
import warnings, logging

logging.getLogger("matplotlib").setLevel(logging.ERROR)

SEED = 51423


@pytest.fixture
def rng():
    """
    Ensure all tests start with the same rng
    """
    return np.random.default_rng(SEED)


@pytest.fixture(autouse=True)
def close_figures_after_test():
    yield
    uplt.close("all")


# Define command line option
def pytest_addoption(parser):
    parser.addoption(
        "--store-failed-only",
        action="store_true",
        help="Store only failed matplotlib comparison images",
    )


class StoreFailedMplPlugin:
    def __init__(self, config):
        self.config = config

        # Get base directories as Path objects
        self.result_dir = Path(config.getoption("--mpl-results-path", "./results"))
        self.baseline_dir = Path(config.getoption("--mpl-baseline-path", "./baseline"))

        print(f"Store Failed MPL Plugin initialized")
        print(f"Result dir: {self.result_dir}")

    def _has_mpl_marker(self, report: pytest.TestReport):
        """Check if the test has the mpl_image_compare marker."""
        return report.keywords.get("mpl_image_compare", False)

    def _remove_success(self, report: pytest.TestReport):
        """Remove successful test images."""

        pattern = r"(?P<sep>::|/)|\[|\]|\.py"
        name = re.sub(
            pattern,
            lambda m: "." if m.group("sep") else "_" if m.group(0) == "[" else "",
            report.nodeid,
        )
        target = (self.result_dir / name).absolute()
        if target.is_dir():
            shutil.rmtree(target)

    @pytest.hookimpl(trylast=True)
    def pytest_runtest_logreport(self, report):
        """Hook that processes each test report."""
        # Delete successfull tests
        if report.when == "call" and report.failed == False:
            if self._has_mpl_marker(report):
                self._remove_success(report)


def pytest_collection_modifyitems(config, items):
    for item in items:
        for mark in item.own_markers:
            if base_dir := config.getoption("--mpl-baseline-path", default=None):
                if mark.name == "mpl_image_compare":
                    name = item.name
                    if not (Path(base_dir) / f"{name}.png").exists():
                        item.add_marker(
                            pytest.mark.skip(reason="Baseline image does not exist")
                        )


# Register the plugin if the option is used
def pytest_configure(config):
    try:
        if config.getoption("--store-failed-only", False):
            config.pluginmanager.register(StoreFailedMplPlugin(config))
    except Exception as e:
        print(f"Error during plugin configuration: {e}")

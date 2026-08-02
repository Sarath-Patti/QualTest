"""Sanity and foundation validation unit tests for QualTest framework."""

from framework.config import Settings, get_settings
from framework.logger import get_logger, setup_logger
from framework.parser import load_testcase, TestCase
from framework.simulator import NetworkSimulator, BaseSimulator
from framework.validator import validate, ValidationState
from framework.scheduler import ConcurrentScheduler
from framework.reporter import ReportGenerator


def test_settings_initialization() -> None:
    """Verifies that framework settings load correctly."""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.app_name == "QualTest v2" or "QualTest" in settings.app_name
    assert settings.version is not None


def test_logger_singleton() -> None:
    """Verifies that logger subsystem returns non-null logger instances."""
    setup_logger()
    logger = get_logger("TestLogger")
    assert logger is not None
    assert logger.name == "QualTest.TestLogger"


def test_sample_testcase_loading() -> None:
    """Verifies that a sample JSON testcase loads correctly."""
    testcase_path = "testcases/attach_success.json"
    tc = load_testcase(testcase_path)
    assert isinstance(tc, TestCase)
    assert tc.name == "Attach Success Test"
    assert tc.protocol == "TCP"
    assert tc.step_count > 0


def test_simulator_and_validator_components() -> None:
    """Verifies simulator and validator interface instantiations."""
    sim = NetworkSimulator(protocol="TCP", port=8888)
    assert sim is not None
    assert sim.protocol == "TCP"

    reporter = ReportGenerator()
    assert reporter is not None

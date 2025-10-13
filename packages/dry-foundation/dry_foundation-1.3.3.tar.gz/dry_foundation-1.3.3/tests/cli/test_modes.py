"""Tests for the application launch modes."""

import multiprocessing
from abc import ABC, abstractmethod
from unittest.mock import Mock, call, patch

import pytest

from dry_foundation.cli.modes import DevelopmentAppMode, LocalAppMode, ProductionAppMode
from dry_foundation.factory import DryFlask


class _TestAppMode(ABC):
    """Abstract base class for testing launch modes."""

    @property
    @abstractmethod
    def mode_cls(self):
        raise NotImplementedError("Define the application mode in a subclass.")

    @property
    @abstractmethod
    def mode_default_port(self):
        raise NotImplementedError("Define the default port in a subclass.")


@pytest.fixture(scope="module", autouse=True)
def mock_db_interface():
    # Tests of the launch mode do not require a functional database interface
    with patch("dry_foundation.factory.SQLAlchemy.select_interface", new=Mock()):
        yield


class TestLocalAppMode(_TestAppMode):
    """Tests for local mode."""

    mode_cls = LocalAppMode
    mode_default_port = 5001
    mode_debugging = False

    def test_initialization(self, mock_click_context):
        self.mode_cls(mock_click_context, host="test.host", port=1111)

    @patch("dry_foundation.cli.modes.run_command")
    @patch("os.environ")
    def test_run(self, mock_environment, mock_run_command, mock_click_context):
        mode = self.mode_cls(mock_click_context, host="test.host", port=1111)
        mode.run()
        mock_environment.setdefault.assert_called_once_with(
            "FLASK_DEBUG", str(self.mode_debugging)
        )
        mock_click_context.invoke.assert_called_once_with(
            mock_run_command, host="test.host", port=1111
        )

    @patch("dry_foundation.cli.modes.run_command")
    @patch("os.environ")
    def test_run_defaults(
        self, mock_environment, mock_run_command, mock_click_context, instance_path
    ):
        config = self.mode_cls.config_type("test", instance_path)
        mode = self.mode_cls(mock_click_context, config=config)
        mode.run()
        mock_environment.setdefault.assert_called_once_with(
            "FLASK_DEBUG", str(self.mode_debugging)
        )
        mock_click_context.invoke.assert_called_once_with(
            mock_run_command, host=None, port=self.mode_default_port
        )

    @patch("dry_foundation.cli.modes.run_command")
    @patch("os.environ")
    def test_run_from_configuration(
        self, mock_environment, mock_run_command, mock_click_context, instance_path
    ):
        config = self.mode_cls.config_type("test", instance_path)
        config.SERVER_NAME = "test.host:1111"
        mode = self.mode_cls(mock_click_context, config=config)
        mode.run()
        mock_environment.setdefault.assert_called_once_with(
            "FLASK_DEBUG", str(self.mode_debugging)
        )
        mock_click_context.invoke.assert_called_once_with(
            mock_run_command, host="test.host", port=1111
        )


class TestDevelopmentAppMode(TestLocalAppMode):
    """Tests for development mode."""

    mode_cls = DevelopmentAppMode
    mode_default_port = 5000
    mode_debugging = True


class TestProductionAppMode(_TestAppMode):
    """Tests for production mode."""

    mode_cls = ProductionAppMode
    mode_default_port = 8000
    expected_worker_count = (multiprocessing.cpu_count() * 2) + 1

    def test_initialization(self, mock_click_context):
        mode = self.mode_cls(mock_click_context, host="test.host", port=1111)
        assert isinstance(mode.application, DryFlask)
        assert mode.options == {
            "config": None,
            "bind": "test.host:1111",
            "workers": self.expected_worker_count,
            "worker_class": "gthread",
        }

    def test_initialization_via_bind(self, mock_click_context):
        mode = self.mode_cls(mock_click_context, bind="test.host:1111")
        assert isinstance(mode.application, DryFlask)
        assert mode.options == {
            "config": None,
            "bind": "test.host:1111",
            "workers": self.expected_worker_count,
            "worker_class": "gthread",
        }

    def test_initialization_with_config(self, mock_click_context):
        mode = self.mode_cls(mock_click_context, gunicorn_config_path="test/config.py")
        assert isinstance(mode.application, DryFlask)
        assert mode.options == {
            "config": "test/config.py",
            "bind": None,
            "workers": self.expected_worker_count,
            "worker_class": "gthread",
        }

    def test_initialization_with_gunicorn_config(self, mock_click_context):
        mode = self.mode_cls(mock_click_context, gunicorn_config_path="test/config.py")
        assert isinstance(mode.application, DryFlask)
        assert mode.options == {
            "config": "test/config.py",
            "bind": None,
            "workers": self.expected_worker_count,
            "worker_class": "gthread",
        }

    def test_initialization_with_gunicorn_config_from_app(self, mock_click_context):
        mock_app_config = Mock(GUNICORN_CONFIG="test/config.py")
        mode = self.mode_cls(mock_click_context, config=mock_app_config)
        assert isinstance(mode.application, DryFlask)
        assert mode.options == {
            "config": "test/config.py",
            "bind": None,
            "workers": self.expected_worker_count,
            "worker_class": "gthread",
        }

    def test_initialization_with_gunicorn_config_match(self, mock_click_context):
        mock_app_config = Mock(GUNICORN_CONFIG="test/config.py")
        mode = self.mode_cls(mock_click_context, config=mock_app_config)
        mode = self.mode_cls(
            mock_click_context,
            config=mock_app_config,
            gunicorn_config_path="test/config.py",
        )
        assert isinstance(mode.application, DryFlask)
        assert mode.options == {
            "config": "test/config.py",
            "bind": None,
            "workers": self.expected_worker_count,
            "worker_class": "gthread",
        }

    @pytest.mark.parametrize(
        ("invalid_kwargs", "config", "exception"),
        [
            [
                {"host": "test.host", "port": "0000", "bind": "test.alt.host:9999"},
                None,
                ValueError,
            ],
            [{"port": "0000"}, None, ValueError],
            [
                {"gunicorn_config_path": "gunicorn_test_config.py"},
                Mock(GUNICORN_CONFIG="test/config.py"),  # conflicts with direct path
                ValueError,
            ],
        ],
    )
    def test_initialization_invalid(
        self, mock_click_context, invalid_kwargs, config, exception
    ):
        with pytest.raises(exception):
            self.mode_cls(mock_click_context, config=config, **invalid_kwargs)

    @pytest.mark.xfail
    def test_load_config(self):
        pytest.fail("Not yet implemented...")

    def test_load(self, mock_click_context):
        mode = self.mode_cls(mock_click_context, host="test.host", port=1111)
        assert mode.load() is mode.application

    @patch("gunicorn.config.Config.set")
    @patch("gunicorn.app.base.BaseApplication.run")
    def test_run(
        self,
        mock_gunicorn_run_method,
        mock_gunicorn_config_set_method,
        mock_click_context,
    ):
        mode = self.mode_cls(mock_click_context, host="test.host", port=1111)
        mode.run()
        mock_gunicorn_run_method.assert_called_once()
        mock_gunicorn_config_set_method.assert_has_calls(
            [
                call("bind", "test.host:1111"),
                call("workers", self.expected_worker_count),
                call("worker_class", "gthread"),
            ],
            any_order=True,
        )

    @patch("gunicorn.config.Config.set")
    @patch("gunicorn.app.base.BaseApplication.run")
    def test_run_defaults(
        self,
        mock_gunicorn_run_method,
        mock_gunicorn_config_set_method,
        mock_click_context,
    ):
        mode = self.mode_cls(mock_click_context)
        mode.run()
        mock_gunicorn_run_method.assert_called_once()
        mock_gunicorn_config_set_method.assert_has_calls(
            [
                call("workers", self.expected_worker_count),
                call("worker_class", "gthread"),
            ],
            any_order=True,
        )

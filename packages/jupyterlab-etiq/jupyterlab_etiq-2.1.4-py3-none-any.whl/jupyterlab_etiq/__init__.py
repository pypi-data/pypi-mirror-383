"""JupyterLab extension backend for the Etiq Copilot.

This module serves as the server-side component for the Etiq Copilot JupyterLab
extension. It establishes a communication channel (`Comm`) with the frontend
to provide code analysis, testing, and recommendation features directly within
the Jupyter environment.

The core logic is encapsulated in the `EtiqExtension` class, which manages
application state (such as the code scan cache), initializes necessary services
(like recommenders and code scanners), and handles incoming messages from the
client. It uses a dispatcher pattern to route actions from the frontend to the
appropriate handler functions.

The module also implements a custom logging handler (`CommLogHandler`) to forward
backend logs to the frontend for real-time display.

It integrates with IPython through the standard `load_ipython_extension` and
`unload_ipython_extension` functions, which register and unregister the comm
target, respectively.
"""

from __future__ import annotations

import logging
import os
import traceback
import uuid
from typing import TYPE_CHECKING, Any
from etiq_copilot.engine.telemetry import get_anonymous_user_id
from typing_extensions import TypeAlias

from etiq_copilot.engine.daemons.utils import (
    get_all_recommenders,
    send_stored_telemetry_to_dashboard,
)
from etiq_copilot.engine.implementations.rca.etiq_rca_recommender import (
    EtiqRCARecommender,
)
from etiq_copilot.engine.implementations.scanner import DebuggerCodeScanner
from etiq_copilot.engine.implementations.test_recommenders import RecommenderRepository
from etiq_copilot.engine.telemetry import Telemetry
from etiq_copilot.engine.test_pool import ConfigTestPool

from .handlers import (
    MessageMissingDataError,
    NoScanResultsError,
    handle_get_logs,
    handle_get_recommendations,
    handle_run_codescan,
    handle_run_rca,
    handle_run_test,
)

if TYPE_CHECKING:
    from ipykernel.comm import Comm
    from IPython.core.interactiveshell import InteractiveShell

    from etiq_copilot.engine.implementations.scanner.scan_results import (
        CodeScannerResult,
    )

CommMsg: TypeAlias = dict[str, Any]

try:
    from ._version import __version__
except ImportError:
    logging.getLogger(__name__).warning(
        "Importing 'jupyterlab_etiq' outside a proper installation.",
    )
    __version__ = "dev"


# Set up telemetry
telemetry = Telemetry(
    etiq_token=os.getenv("ETIQ_TOKEN") or "",
    user_id=get_anonymous_user_id(),
    session_id=uuid.uuid4(),
)


class CommLogHandler(logging.Handler):
    """A logging handler that sends log messages to a Jupyter Comm channel.

    This handler allows you to capture log messages from your Python code
    and send them to a JupyterLab extension via a Comm channel.
    """

    def __init__(self, comm: Comm) -> None:
        """Initialize a CommLogHandler with the given comm.

        Args:
            comm : The comm to use for sending log messages.

        """
        super().__init__()
        self.comm = comm

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record by sending it to the client via a Comm channel.

        Args:
            record: The log record to emit.

        """
        try:
            log_entry = self.format(record)
            self.comm.send(
                {
                    "type": "logger_log",
                    "level": record.levelname,
                    "message": log_entry,
                },
            )
        except Exception:  # noqa: BLE001
            # Do not let logging failures crash the kernel
            traceback.print_exc()


class EtiqExtension:
    """The EtiqExtension class.

    This class is the entry point for the Etiq extension. It is responsible for
    setting up the logging, creating the CodeScanner, RecommenderRepository,
    and RCARecommender. It also sets up the action handlers and failure names.
    """

    def __init__(self, telemetry: Telemetry, comm: Comm) -> None:
        """Initialize the EtiqExtension class.

        Args:
            telemetry: The telemetry object used for sending telemetry data.
            comm: The Comm object used for sending and receiving messages.

        """
        self.comm = comm
        self.scan_result_cache: dict[str, CodeScannerResult] = {}
        self.telemetry = telemetry
        self.rca_recommender = EtiqRCARecommender()
        self.recommender_repository = RecommenderRepository(
            recommenders=get_all_recommenders(),
            test_pool_config=ConfigTestPool(),
        )
        self.code_scanner = DebuggerCodeScanner()
        self.action_handlers = {
            "run_test": self._handle_run_test,
            "rca": self._handle_run_rca,
            "give_recommendations": self._handle_get_recommendations,
            "run_codescan": self._handle_run_codescan,
            "get_logs": self._handle_get_logs,
        }
        self.action_failure_names = {
            "run_test": "test_result",
            "rca": "rca_failure",
            "give_recommendations": "recommendation_result",
            "run_codescan": "scan_result",
        }
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _setup_logging(self) -> None:
        handler = CommLogHandler(self.comm)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(levelname)s   %(message)s"))

    def handle_message(self, msg: CommMsg) -> None:
        """Handle an incoming message from JupyterLab.

        This method takes the given message and uses the action specified in the
        message to determine which action handler to call. If the action is unknown,
        it is logged as an error.

        Args:
            msg: The message to handle, which must contain the action to take in
                the "action" key of the "data" dictionary.

        """
        try:
            action = msg["content"]["data"].get("action")
        except KeyError as e:
            traceback_str = traceback.format_exc()
            self._send_error_response(
                original_msg=msg,
                error=e,
                traceback_str=traceback_str,
            )
            return
        if not isinstance(action, str):
            self.comm.send(
                {
                    "type": "unknown_action",
                    "data": msg["content"],
                    "error": f"Unknown action: {action}",
                    "action": action,
                },
            )
            return
        handler = self.action_handlers.get(action)
        if handler:
            try:
                handler(msg["content"]["data"])
            except MessageMissingDataError as e:
                traceback_str = traceback.format_exc()
                self._send_error_response(
                    original_msg=msg,
                    error=e,
                    traceback_str=traceback_str,
                )
            except NoScanResultsError as e:
                traceback_str = traceback.format_exc()
                self._send_error_response(
                    original_msg=msg,
                    error=e,
                    traceback_str=traceback_str,
                )
            except Exception as e:  # noqa: BLE001
                # Unknown error but we don't want it to crash the extension
                traceback_str = traceback.format_exc()
                self.comm.send(
                    {
                        "type": "unknown_error",
                        "data": msg["content"],
                        "error": f"Error: {e}",
                        "traceback": traceback_str,
                    },
                )
        else:
            self.comm.send(
                {
                    "type": "unknown_action",
                    "data": msg["content"],
                    "error": f"Unknown action: {action}",
                    "action": action,
                },
            )

    def _send_error_response(
        self,
        original_msg: CommMsg,
        error: Exception,
        traceback_str: str,
    ) -> None:
        action = original_msg["content"]["data"].get("action")
        if not isinstance(action, str):
            self.comm.send(
                {
                    "type": "unknown action",
                    "data": original_msg["content"],
                    "filename": original_msg["content"]["data"].get("filename"),
                    "error": f"Error: {error}",
                    "test_id": original_msg["content"]["data"].get("test_id"),
                    "traceback": traceback_str,
                },
            )
            return

        if failure_type := self.action_failure_names.get(
            action,
        ):
            self.comm.send(
                {
                    "type": failure_type,
                    "data": original_msg["content"],
                    "filename": original_msg["content"]["data"].get("filename"),
                    "error": f"Error: {error}",
                    "test_id": original_msg["content"]["data"].get("test_id"),
                    "traceback": traceback_str,
                },
            )

    # --- Individual action handlers as methods ---
    def _handle_run_test(self, msg_data: dict[str, Any]) -> None:
        handle_run_test(
            scan_result_cache=self.scan_result_cache,
            comm=self.comm,
            msg_data=msg_data,
            rca_recommender=self.rca_recommender,
            telemetry=self.telemetry,
        )

    def _handle_run_rca(self, msg_data: dict[str, Any]) -> None:
        handle_run_rca(
            scan_result_cache=self.scan_result_cache,
            comm=self.comm,
            msg_data=msg_data,
        )

    def _handle_get_recommendations(self, msg_data: dict[str, Any]) -> None:
        handle_get_recommendations(
            scan_result_cache=self.scan_result_cache,
            comm=self.comm,
            msg_data=msg_data,
            recommender_repository=self.recommender_repository,
        )

    def _handle_run_codescan(self, msg_data: dict[str, Any]) -> None:
        handle_run_codescan(
            scan_result_cache=self.scan_result_cache,
            comm=self.comm,
            msg_data=msg_data,
            code_scanner=self.code_scanner,
            logger=self.logger,
        )

    def _handle_get_logs(self, msg_data: dict[str, Any]) -> None:
        handle_get_logs(
            comm=self.comm,
            msg_data=msg_data,
            logger=self.logger,
        )


def comm_target(comm: Comm, _: CommMsg) -> None:
    """Handle comm_open messages from frontend."""
    extension_instance = EtiqExtension(comm=comm, telemetry=telemetry)
    comm.on_msg(extension_instance.handle_message)


# This function is required by jupyter lab and is not unused!
def _jupyter_labextension_paths() -> list[dict[str, str]]:
    return [{"src": "labextension", "dest": "jupyterlab-etiq"}]


def load_ipython_extension(ipython: InteractiveShell) -> None:
    # Register comm for communicating with frontend
    """Load the IPython extension.

    This function registers the comm target "debug_vis_comm" from the IPython kernel's
    comm manager, allowing the frontend to communicate with the backend.

    Args:
        ipython (InteractiveShell): The IPython InteractiveShell instance.

    """
    ipython.kernel.comm_manager.register_target("debug_vis_comm", comm_target)
    send_stored_telemetry_to_dashboard(telemetry=telemetry)
    logging.getLogger(__name__).info("Etiq visualization extension loaded.")


def unload_ipython_extension(ipython: InteractiveShell) -> None:
    """Unload the IPython extension.

    This function unregisters the comm target "debug_vis_comm" from the IPython kernel's
    comm manager.

    Args:
        ipython (InteractiveShell): The IPython InteractiveShell instance.

    """
    ipython.kernel.comm_manager.unregister_target("debug_vis_comm")
    send_stored_telemetry_to_dashboard(telemetry=telemetry)
    logging.getLogger(__name__).info("Etiq visualization extension unloaded.")

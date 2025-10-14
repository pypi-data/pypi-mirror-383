from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING, Any, Callable, TypedDict


from etiq_copilot.engine.daemons.utils import (
    generate_recommendations,
    run_rca,
    run_test,
)
from etiq_copilot.engine.implementations.db.storage_test_logs import (
    SQLiteStorageTestLogs,
)
from etiq_copilot.engine.implementations.scanner.code_scanner import DebuggerCodeScanner
from IPython.core.getipython import get_ipython

if TYPE_CHECKING:
    from etiq_copilot.engine.implementations.rca import (
        EtiqRCARecommender,
    )
    from etiq_copilot.engine.implementations.scanner.scan_results import (
        CodeScannerResult,
    )
    from etiq_copilot.engine.implementations.test_recommenders import (
        RecommenderRepository,
    )
    from etiq_copilot.engine.telemetry.base_telemetry import BaseTelemetry
    from ipykernel.comm import Comm


class CommData(TypedDict):
    data: dict[str, Any]


class MessageMissingDataError(Exception):
    pass


class NoScanResultsError(Exception):
    pass


def get_line_getter(code: str) -> Callable[[str, int], str]:
    """Generate a linecache.getline dropin for the given code.

    Args:
        code: The source code to generate a line getter for.

    Returns:
        A function that takes a filename and line number, and returns the
        corresponding line from the given code.

    """
    sourcelines = code.splitlines()

    def _getline(_filename: str, lineno: int) -> str:
        try:
            return sourcelines[lineno - 1]
        except IndexError:
            return ""

    return _getline


def handle_run_test(
    scan_result_cache: dict[str, CodeScannerResult],
    comm: Comm,
    msg_data:  dict[str, Any],
    rca_recommender: EtiqRCARecommender,
    telemetry: BaseTelemetry,
) -> None:
    """Handle the execution of a test based on the provided JSON.

    Args:
        scan_result_cache: A dictionary mapping file names to their respective scan
            results.
        comm: The Comm object used to send the test result.
        msg_data: The message data, containing the filename, test ID, line number,
            test configuration, and other details about the test to run.
        rca_recommender: An instance of the root cause analysis recommender to
            assist in test execution.
        telemetry: An instance of telemetry for logging and monitoring purposes.

    Returns:
        None

    """

    if (filename := msg_data.get("filename")) is None:
        msg = "filename is required"
        raise MessageMissingDataError(msg)
    scan_filename = str(filename)
    test_id = msg_data.get("test_id")
    if test_id is None:
        msg = "test_id is required"
        raise MessageMissingDataError(msg)

    scan_results = scan_result_cache.get(scan_filename)
    if not scan_results:
        # This should not be possible but it's here for safety
        msg = f"Scan results not found for {scan_filename}"
        raise NoScanResultsError(msg)

    test_config = msg_data.get("test_config")
    if not test_config:
        msg = f"Test config not found for {test_id}"
        raise MessageMissingDataError(msg)

    line_no = msg_data.get("line_no")
    if line_no is not None:
        line_no = int(line_no)
    else:
        msg = "No line number found"
        raise MessageMissingDataError(msg)
    result = run_test(
        scan_results=scan_results,
        line_number=line_no,
        test_config=test_config,
        rca_recommender=rca_recommender,
        telemetry=telemetry,
    )
    result["test_id"] = test_id
    payload = {
        "type": "test_result",
        "data": result,
        "filename": scan_filename,
        "test_id": test_id,
    }
    comm.send(payload)


def handle_run_rca(
    scan_result_cache: dict[str, CodeScannerResult],
    comm: Comm,
    msg_data:  dict[str, Any],
) -> None:
    """Handle the execution of Root Cause Analysis (RCA).

    Args:
        scan_result_cache: A dictionary mapping file names to their respective scan
            results.
        comm: The comm to use for sending RCA results or failure messages.
        msg_data:: A dictionary containing details about the RCA to run, including
            the test ID, file path, test configuration, and RCA configuration.

    Returns:
        None

    """
    scan_filename = str(msg_data["path"])
    active_file_scan_results = scan_result_cache.get(scan_filename)
    if active_file_scan_results is None:
        # This should not be possible but it's here for safety
        msg = f"Scan results not found for {scan_filename}"
        raise MessageMissingDataError(msg)

    test_id = msg_data.get("test_id")
    if test_id is None:
        msg = "test_id is required"
        raise MessageMissingDataError(msg)

    test_config = msg_data.get("test_config")
    if not test_config:
        msg = f"Test config not found for {test_id}"
        raise MessageMissingDataError(msg)

    rca_config = msg_data.get("rca_config")
    if not rca_config:
        msg = f"RCA config not found for {test_id}"
        raise MessageMissingDataError(msg)

    result, interpretation = run_rca(
        scan_results=active_file_scan_results,
        test_config=test_config,
        rca_config=rca_config,
    )
    result["state"] = "completed"
    result["test_id"] = test_id
    result["interpretation"] = interpretation
    comm.send(
        {"type": "rca_result", "result": result, "filename": scan_filename},
    )


def handle_get_recommendations(
    scan_result_cache: dict[str, CodeScannerResult],
    comm: Comm,
    msg_data:  dict[str, Any],
    recommender_repository: RecommenderRepository,
) -> None:
    """Handle a message requesting test recommendations for a given file.

    Args:
        scan_result_cache: A dictionary mapping file names to their respective scan
            results.
        comm: The Comm object used to send the recommendation results.
        msg_data: The message data, containing the filename and optional force scan
            flag.
        recommender_repository: The recommender repository used to generate
            recommendations.

    Raises:
        MessageMissingDataException: If the message is missing required data, such as
            a filename or code.

    """

    if (filename := msg_data.get("filename")) is None:
        msg = "filename is required"
        raise MessageMissingDataError(msg)
    scan_filename = str(filename)

    scan_results = scan_result_cache.get(scan_filename)
    if not scan_results:
        # This should not be possible but it's here for safety
        msg = f"Scan results not found for {scan_filename}"
        raise MessageMissingDataError(msg)

    force_scan = msg_data.get("forceScan", False)
    code = msg_data.get("code")
    if code is None or not isinstance(code, str):
        msg = "Code field is required."
        raise MessageMissingDataError(msg)

    recommendation_result = generate_recommendations(
        recommender_repository=recommender_repository,
        scan_results=scan_results,
    )

    payload = {
        "type": "recommendation_result",
        "data": recommendation_result,
        "filename": scan_filename,
        "forceScan": force_scan,
    }
    comm.send(payload)


def run_codescan(
    code: str,
    all_cells: bool,
    filename: str,
    code_scanner: DebuggerCodeScanner,
    scan_result_cache: dict[str, CodeScannerResult],
    force_scan: bool,
) -> CodeScannerResult | None:
    """Runs a code scan using the provided code scanner.

    Args:
        code: The code to scan.
        all_cells: Whether to scan all cells or a single cell.
        filename: The name of the file being scanned.
        code_scanner: The code scanner to use.
        scan_result_cache: A cache of scan results.
        force_scan: Whether to force a scan, even if the result is cached.

    Returns:
        The result of the code scan, or None if there was an error.
    """
    result = None
    if all_cells:
        # If all cells, scan the code as is, no need to inject notebook context
        result = code_scanner.scan_code(code)
        scan_result_cache[filename] = result
    else:
        # If single cell, inject the notebook context
        ip = get_ipython()
        if ip:
            result = code_scanner.scan_code(code, None, ip.user_ns)

    return result


def handle_run_codescan(
    scan_result_cache: dict[str, CodeScannerResult],
    code_scanner: DebuggerCodeScanner,
    comm: Comm,
    msg_data:  dict[str, Any],
    logger: Logger | None,
):
    code = str(msg_data.get("code"))
    all_cells = bool(msg_data.get("allCells"))
    force_scan = msg_data.get("forceScan", True)
    cell_id = msg_data.get("cellId")
    filename = str(msg_data.get("filename"))
    if logger:
        msg = f"Running scan on {filename}"
        logger.info(msg)
    # If not in cache or single cell scan, run the scan
    result = run_codescan(
        code=code,
        all_cells=all_cells,
        filename=filename,
        code_scanner=code_scanner,
        scan_result_cache=scan_result_cache,
        force_scan=force_scan,
    )
    if result:
        dot_graph = result.create_full_lineage_graph(format="json")
    else:
        dot_graph = ""
    payload = {
        "type": "scan_result",
        "data": {
            "dot_graph": dot_graph,
        },
        "filename": filename,
        "allCells": all_cells,
        "forceScan": force_scan,
    }
    if cell_id:
        payload["cellId"] = cell_id
    comm.send(payload)


def handle_get_logs(comm: Comm, msg_data:  dict[str, Any], logger: Logger | None):
    date = msg_data.get("after_date")
    storage_test_logs = SQLiteStorageTestLogs()
    comm.send(
        {
            "type": "test_logs",
            "result": [
                alog.to_json() for alog in storage_test_logs.get(test_started_gt=date)
            ],
        },
    )

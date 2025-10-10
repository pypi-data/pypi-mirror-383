from __future__ import annotations

import base64
import contextlib
import copy
import datetime
import inspect
import json
import pickle
import re
import tempfile
import threading
from dataclasses import dataclass
from enum import Enum
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal
from zipfile import ZipFile

import commonmark
import narwhals as nw
from great_tables import GT, from_column, google_font, html, loc, md, style, vals
from great_tables.gt import _get_column_of_values
from great_tables.vals import fmt_integer, fmt_number
from importlib_resources import files
from narwhals.typing import FrameT

from pointblank._constants import (
    ASSERTION_TYPE_METHOD_MAP,
    CHECK_MARK_SPAN,
    COMPARISON_OPERATORS,
    COMPARISON_OPERATORS_AR,
    COMPATIBLE_DTYPES,
    CROSS_MARK_SPAN,
    IBIS_BACKENDS,
    LOG_LEVELS_MAP,
    MODEL_PROVIDERS,
    REPORTING_LANGUAGES,
    ROW_BASED_VALIDATION_TYPES,
    RTL_LANGUAGES,
    SEVERITY_LEVEL_COLORS,
    SVG_ICONS_FOR_ASSERTION_TYPES,
    SVG_ICONS_FOR_TBL_STATUS,
    VALIDATION_REPORT_FIELDS,
)
from pointblank._constants_translations import (
    EXPECT_FAIL_TEXT,
    STEP_REPORT_TEXT,
    VALIDATION_REPORT_TEXT,
)
from pointblank._interrogation import (
    NumberOfTestUnits,
    SpeciallyValidation,
    col_count_match,
    col_exists,
    col_schema_match,
    col_vals_expr,
    conjointly_validation,
    interrogate_between,
    interrogate_eq,
    interrogate_ge,
    interrogate_gt,
    interrogate_isin,
    interrogate_le,
    interrogate_lt,
    interrogate_ne,
    interrogate_not_null,
    interrogate_notin,
    interrogate_null,
    interrogate_outside,
    interrogate_regex,
    interrogate_rows_distinct,
    row_count_match,
    rows_complete,
)
from pointblank._typing import SegmentSpec
from pointblank._utils import (
    _check_any_df_lib,
    _check_invalid_fields,
    _column_test_prep,
    _copy_dataframe,
    _count_null_values_in_column,
    _count_true_values_in_column,
    _derive_bounds,
    _format_to_integer_value,
    _get_fn_name,
    _get_tbl_type,
    _is_lazy_frame,
    _is_lib_present,
    _is_narwhals_table,
    _is_value_a_df,
    _select_df_lib,
)
from pointblank._utils_check_args import (
    _check_boolean_input,
    _check_column,
    _check_pre,
    _check_set_types,
    _check_thresholds,
)
from pointblank._utils_html import _create_table_dims_html, _create_table_type_html
from pointblank.column import Column, ColumnLiteral, ColumnSelector, ColumnSelectorNarwhals, col
from pointblank.schema import Schema, _get_schema_validation_info
from pointblank.segments import Segment
from pointblank.thresholds import (
    Actions,
    FinalActions,
    Thresholds,
    _convert_abs_count_to_fraction,
    _normalize_thresholds_creation,
)

if TYPE_CHECKING:
    from collections.abc import Collection

    from pointblank._typing import AbsoluteBounds, Tolerance

__all__ = [
    "Validate",
    "load_dataset",
    "read_file",
    "write_file",
    "config",
    "connect_to_table",
    "preview",
    "missing_vals_tbl",
    "get_action_metadata",
    "get_column_count",
    "get_data_path",
    "get_row_count",
    "get_validation_summary",
]

# Create a thread-local storage for the metadata
_action_context = threading.local()


@contextlib.contextmanager
def _action_context_manager(metadata):
    """Context manager for storing metadata during action execution."""
    _action_context.metadata = metadata
    try:
        yield
    finally:
        # Clean up after execution
        if hasattr(_action_context, "metadata"):
            delattr(_action_context, "metadata")


def get_action_metadata() -> dict | None:
    """Access step-level metadata when authoring custom actions.

    Get the metadata for the validation step where an action was triggered. This can be called by
    user functions to get the metadata for the current action. This function can only be used within
    callables crafted for the [`Actions`](`pointblank.Actions`) class.

    Returns
    -------
    dict | None
        A dictionary containing the metadata for the current step. If called outside of an action
        (i.e., when no action is being executed), this function will return `None`.

    Description of the Metadata Fields
    ----------------------------------
    The metadata dictionary contains the following fields for a given validation step:

    - `step`: The step number.
    - `column`: The column name.
    - `value`: The value being compared (only available in certain validation steps).
    - `type`: The assertion type (e.g., `"col_vals_gt"`, etc.).
    - `time`: The time the validation step was executed (in ISO format).
    - `level`: The severity level (`"warning"`, `"error"`, or `"critical"`).
    - `level_num`: The severity level as a numeric value (`30`, `40`, or `50`).
    - `autobrief`: A localized and brief statement of the expectation for the step.
    - `failure_text`: Localized text that explains how the validation step failed.

    Examples
    --------
    When creating a custom action, you can access the metadata for the current step using the
    `get_action_metadata()` function. Here's an example of a custom action that logs the metadata
    for the current step:

    ```{python}
    import pointblank as pb

    def log_issue():
        metadata = pb.get_action_metadata()
        print(f"Type: {metadata['type']}, Step: {metadata['step']}")

    validation = (
        pb.Validate(
            data=pb.load_dataset(dataset="game_revenue", tbl_type="duckdb"),
            thresholds=pb.Thresholds(warning=0.05, error=0.10, critical=0.15),
            actions=pb.Actions(warning=log_issue),
        )
        .col_vals_regex(columns="player_id", pattern=r"[A-Z]{12}[0-9]{3}")
        .col_vals_gt(columns="item_revenue", value=0.05)
        .col_vals_gt(
            columns="session_duration",
            value=15,
        )
        .interrogate()
    )

    validation
    ```

    Key pieces to note in the above example:

    - `log_issue()` (the custom action) collects `metadata` by calling `get_action_metadata()`
    - the `metadata` is a dictionary that is used to craft the log message
    - the action is passed as a bare function to the `Actions` object within the `Validate` object
    (placing it within `Validate(actions=)` ensures it's set as an action for every validation step)

    See Also
    --------
    Have a look at [`Actions`](`pointblank.Actions`) for more information on how to create custom
    actions for validation steps that exceed a set threshold value.
    """
    if hasattr(_action_context, "metadata"):  # pragma: no cover
        return _action_context.metadata  # pragma: no cover
    else:
        return None  # pragma: no cover


# Create a thread-local storage for the metadata
_final_action_context = threading.local()


@contextlib.contextmanager
def _final_action_context_manager(summary):
    """Context manager for storing validation summary during final action execution."""
    _final_action_context.summary = summary
    try:
        yield
    finally:
        # Clean up after execution
        if hasattr(_final_action_context, "summary"):
            delattr(_final_action_context, "summary")


def get_validation_summary() -> dict | None:
    """Access validation summary information when authoring final actions.

    This function provides a convenient way to access summary information about the validation
    process within a final action. It returns a dictionary with key metrics from the validation
    process. This function can only be used within callables crafted for the
    [`FinalActions`](`pointblank.FinalActions`) class.

    Returns
    -------
    dict | None
        A dictionary containing validation metrics. If called outside of an final action context,
        this function will return `None`.

    Description of the Summary Fields
    --------------------------------
    The summary dictionary contains the following fields:

    - `n_steps` (`int`): The total number of validation steps.
    - `n_passing_steps` (`int`): The number of validation steps where all test units passed.
    - `n_failing_steps` (`int`): The number of validation steps that had some failing test units.
    - `n_warning_steps` (`int`): The number of steps that exceeded a 'warning' threshold.
    - `n_error_steps` (`int`): The number of steps that exceeded an 'error' threshold.
    - `n_critical_steps` (`int`): The number of steps that exceeded a 'critical' threshold.
    - `list_passing_steps` (`list[int]`): List of step numbers where all test units passed.
    - `list_failing_steps` (`list[int]`): List of step numbers for steps having failing test units.
    - `dict_n` (`dict`): The number of test units for each validation step.
    - `dict_n_passed` (`dict`): The number of test units that passed for each validation step.
    - `dict_n_failed` (`dict`): The number of test units that failed for each validation step.
    - `dict_f_passed` (`dict`): The fraction of test units that passed for each validation step.
    - `dict_f_failed` (`dict`): The fraction of test units that failed for each validation step.
    - `dict_warning` (`dict`): The 'warning' level status for each validation step.
    - `dict_error` (`dict`): The 'error' level status for each validation step.
    - `dict_critical` (`dict`): The 'critical' level status for each validation step.
    - `all_passed` (`bool`): Whether or not every validation step had no failing test units.
    - `highest_severity` (`str`): The highest severity level encountered during validation. This can
      be one of the following: `"warning"`, `"error"`, or `"critical"`, `"some failing"`, or
      `"all passed"`.
    - `tbl_row_count` (`int`): The number of rows in the target table.
    - `tbl_column_count` (`int`): The number of columns in the target table.
    - `tbl_name` (`str`): The name of the target table.
    - `validation_duration` (`float`): The duration of the validation in seconds.

    Note that the summary dictionary is only available within the context of a final action. If
    called outside of a final action (i.e., when no final action is being executed), this function
    will return `None`.

    Examples
    --------
    Final actions are executed after the completion of all validation steps. They provide an
    opportunity to take appropriate actions based on the overall validation results. Here's an
    example of a final action function (`send_report()`) that sends an alert when critical
    validation failures are detected:

    ```python
    import pointblank as pb

    def send_report():
        summary = pb.get_validation_summary()
        if summary["highest_severity"] == "critical":
            # Send an alert email
            send_alert_email(
                subject=f"CRITICAL validation failures in {summary['tbl_name']}",
                body=f"{summary['n_critical_steps']} steps failed with critical severity."
            )

    validation = (
        pb.Validate(
            data=my_data,
            final_actions=pb.FinalActions(send_report)
        )
        .col_vals_gt(columns="revenue", value=0)
        .interrogate()
    )
    ```

    Note that `send_alert_email()` in the example above is a placeholder function that would be
    implemented by the user to send email alerts. This function is not provided by the Pointblank
    package.

    The `get_validation_summary()` function can also be used to create custom reporting for
    validation results:

    ```python
    def log_validation_results():
        summary = pb.get_validation_summary()

        print(f"Validation completed with status: {summary['highest_severity'].upper()}")
        print(f"Steps: {summary['n_steps']} total")
        print(f"  - {summary['n_passing_steps']} passing, {summary['n_failing_steps']} failing")
        print(
            f"  - Severity: {summary['n_warning_steps']} warnings, "
            f"{summary['n_error_steps']} errors, "
            f"{summary['n_critical_steps']} critical"
        )

        if summary['highest_severity'] in ["error", "critical"]:
            print("⚠️ Action required: Please review failing validation steps!")
    ```

    Final actions work well with both simple logging and more complex notification systems, allowing
    you to integrate validation results into your broader data quality workflows.

    See Also
    --------
    Have a look at [`FinalActions`](`pointblank.FinalActions`) for more information on how to create
    custom actions that are executed after all validation steps have been completed.
    """
    if hasattr(_final_action_context, "summary"):
        return _final_action_context.summary
    else:
        return None


@dataclass
class PointblankConfig:
    """
    Configuration settings for the Pointblank library.
    """

    report_incl_header: bool = True
    report_incl_footer: bool = True
    preview_incl_header: bool = True

    def __repr__(self):
        return (
            f"PointblankConfig(report_incl_header={self.report_incl_header}, "
            f"report_incl_footer={self.report_incl_footer}, "
            f"preview_incl_header={self.preview_incl_header})"
        )


# Global configuration instance
global_config = PointblankConfig()


def config(
    report_incl_header: bool = True,
    report_incl_footer: bool = True,
    preview_incl_header: bool = True,
) -> PointblankConfig:
    """
    Configuration settings for the Pointblank library.

    Parameters
    ----------
    report_incl_header
        This controls whether the header should be present in the validation table report. The
        header contains the table name, label information, and might contain global failure
        threshold levels (if set).
    report_incl_footer
        Should the footer of the validation table report be displayed? The footer contains the
        starting and ending times of the interrogation.
    preview_incl_header
        Whether the header should be present in any preview table (generated via the
        [`preview()`](`pointblank.preview`) function).

    Returns
    -------
    PointblankConfig
        A `PointblankConfig` object with the specified configuration settings.
    """

    global global_config
    global_config.report_incl_header = report_incl_header  # pragma: no cover
    global_config.report_incl_footer = report_incl_footer  # pragma: no cover
    global_config.preview_incl_header = preview_incl_header  # pragma: no cover


def load_dataset(
    dataset: Literal["small_table", "game_revenue", "nycflights", "global_sales"] = "small_table",
    tbl_type: Literal["polars", "pandas", "duckdb"] = "polars",
) -> FrameT | Any:
    """
    Load a dataset hosted in the library as specified table type.

    The Pointblank library includes several datasets that can be loaded using the `load_dataset()`
    function. The datasets can be loaded as a Polars DataFrame, a Pandas DataFrame, or as a DuckDB
    table (which uses the Ibis library backend). These datasets are used throughout the
    documentation's examples to demonstrate the functionality of the library. They're also useful
    for experimenting with the library and trying out different validation scenarios.

    Parameters
    ----------
    dataset
        The name of the dataset to load. Current options are `"small_table"`, `"game_revenue"`,
        `"nycflights"`, and `"global_sales"`.
    tbl_type
        The type of table to generate from the dataset. The named options are `"polars"`,
        `"pandas"`, and `"duckdb"`.

    Returns
    -------
    FrameT | Any
        The dataset for the `Validate` object. This could be a Polars DataFrame, a Pandas DataFrame,
        or a DuckDB table as an Ibis table.

    Included Datasets
    -----------------
    There are three included datasets that can be loaded using the `load_dataset()` function:

    - `"small_table"`: A small dataset with 13 rows and 8 columns. This dataset is useful for
    testing and demonstration purposes.
    - `"game_revenue"`: A dataset with 2000 rows and 11 columns. Provides revenue data for a game
    development company. For the particular game, there are records of player sessions, the items
    they purchased, ads viewed, and the revenue generated.
    - `"nycflights"`: A dataset with 336,776 rows and 18 columns. This dataset provides information
    about flights departing from New York City airports (JFK, LGA, or EWR) in 2013.
    - `"global_sales"`: A dataset with 50,000 rows and 20 columns. Provides information about
    global sales of products across different regions and countries.

    Supported DataFrame Types
    -------------------------
    The `tbl_type=` parameter can be set to one of the following:

    - `"polars"`: A Polars DataFrame.
    - `"pandas"`: A Pandas DataFrame.
    - `"duckdb"`: An Ibis table for a DuckDB database.

    Examples
    --------
    Load the `"small_table"` dataset as a Polars DataFrame by calling `load_dataset()` with
    `dataset="small_table"` and `tbl_type="polars"`:

    ```{python}
    import pointblank as pb

    small_table = pb.load_dataset(dataset="small_table", tbl_type="polars")

    pb.preview(small_table)
    ```

    Note that the `"small_table"` dataset is a Polars DataFrame and using the
    [`preview()`](`pointblank.preview`) function will display the table in an HTML viewing
    environment.

    The `"game_revenue"` dataset can be loaded as a Pandas DataFrame by specifying the dataset name
    and setting `tbl_type="pandas"`:

    ```{python}
    game_revenue = pb.load_dataset(dataset="game_revenue", tbl_type="pandas")

    pb.preview(game_revenue)
    ```

    The `"game_revenue"` dataset is a more real-world dataset with a mix of data types, and it's
    significantly larger than the `small_table` dataset at 2000 rows and 11 columns.

    The `"nycflights"` dataset can be loaded as a DuckDB table by specifying the dataset name and
    setting `tbl_type="duckdb"`:

    ```{python}
    nycflights = pb.load_dataset(dataset="nycflights", tbl_type="duckdb")

    pb.preview(nycflights)
    ```

    The `"nycflights"` dataset is a large dataset with 336,776 rows and 18 columns. This dataset is
    truly a real-world dataset and provides information about flights originating from New York City
    airports in 2013.

    Finally, the `"global_sales"` dataset can be loaded as a Polars table by specifying the dataset
    name. Since `tbl_type=` is set to `"polars"` by default, we don't need to specify it:

    ```{python}
    global_sales = pb.load_dataset(dataset="global_sales")

    pb.preview(global_sales)
    ```

    The `"global_sales"` dataset is a large dataset with 50,000 rows and 20 columns. Each record
    describes the sales of a particular product to a customer located in one of three global
    regions: North America, Europe, or Asia.
    """

    # Raise an error if the dataset is from the list of provided datasets
    if dataset not in ["small_table", "game_revenue", "nycflights", "global_sales"]:
        raise ValueError(
            f"The dataset name `{dataset}` is not valid. Choose one of the following:\n"
            "- `small_table`\n"
            "- `game_revenue`\n"
            "- `nycflights`\n"
            "- `global_sales`"
        )

    # Raise an error if the `tbl_type=` value is not of the supported types
    if tbl_type not in ["polars", "pandas", "duckdb"]:
        raise ValueError(
            f"The DataFrame type `{tbl_type}` is not valid. Choose one of the following:\n"
            "- `polars`\n"
            "- `pandas`\n"
            "- `duckdb`"
        )

    data_path = files("pointblank.data") / f"{dataset}.zip"

    if tbl_type == "polars":
        if not _is_lib_present(lib_name="polars"):
            raise ImportError(
                "The Polars library is not installed but is required when specifying "
                '`tbl_type="polars".'
            )

        import polars as pl

        dataset = pl.read_csv(ZipFile(data_path).read(f"{dataset}.csv"), try_parse_dates=True)

    if tbl_type == "pandas":
        if not _is_lib_present(lib_name="pandas"):
            raise ImportError(
                "The Pandas library is not installed but is required when specifying "
                '`tbl_type="pandas".'
            )

        import pandas as pd

        parse_date_columns = {
            "small_table": ["date_time", "date"],
            "game_revenue": ["session_start", "time", "start_day"],
            "nycflights": [],
            "global_sales": ["timestamp"],
        }

        dataset = pd.read_csv(data_path, parse_dates=parse_date_columns[dataset])

    if tbl_type == "duckdb":  # pragma: no cover
        if not _is_lib_present(lib_name="ibis"):
            raise ImportError(
                "The Ibis library is not installed but is required when specifying "
                '`tbl_type="duckdb".'
            )

        import ibis

        data_path = files("pointblank.data") / f"{dataset}-duckdb.zip"

        # Unzip the DuckDB dataset to a temporary directory
        with tempfile.TemporaryDirectory() as tmp, ZipFile(data_path, "r") as z:
            z.extractall(path=tmp)

            data_path = f"{tmp}/{dataset}.ddb"

            dataset = ibis.connect(f"duckdb://{data_path}").table(dataset)

    return dataset


def read_file(filepath: str | Path) -> Validate:
    """
    Read a Validate object from disk that was previously saved with `write_file()`.

    This function loads a validation object that was previously serialized to disk using the
    `write_file()` function. The validation object will be restored with all its validation results,
    metadata, and optionally the source data (if it was saved with `keep_tbl=True`).

    :::{.callout-warning}
    The `read_file()` function is currently experimental. Please report any issues you encounter in
    the [Pointblank issue tracker](https://github.com/posit-dev/pointblank/issues).
    :::

    Parameters
    ----------
    filepath
        The path to the saved validation file. Can be a string or Path object.

    Returns
    -------
    Validate
        The restored validation object with all its original state, validation results, and
        metadata.

    Examples
    --------
    Load a validation object that was previously saved:

    ```python
    import pointblank as pb

    # Load a validation object from disk
    validation = pb.read_file("my_validation.pkl")

    # View the validation results
    validation
    ```

    You can also load using just the filename (without extension):

    ```python
    # This will automatically look for "my_validation.pkl"
    validation = pb.read_file("my_validation")
    ```

    The loaded validation object retains all its functionality:

    ```python
    # Get validation summary
    summary = validation.get_json_report()

    # Get sundered data (if original table was saved)
    if validation.data is not None:
        failing_rows = validation.get_sundered_data(type="fail")
    ```

    See Also
    --------
    Use the [`write_file()`](`pointblank.Validate.write_file`) method to save a validation object
    to disk for later retrieval with this function.
    """
    # Handle file path and extension
    file_path = Path(filepath)
    if not file_path.suffix:
        file_path = file_path.with_suffix(".pkl")

    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Validation file not found: {file_path}")

    # Load and deserialize the validation object
    try:
        with open(file_path, "rb") as f:
            loaded_data = pickle.load(f)

        # Expect validation package format with function sources
        if not isinstance(loaded_data, dict) or "validation" not in loaded_data:
            raise RuntimeError(f"Invalid validation file format: {file_path}")

        validation = loaded_data["validation"]
        function_sources = loaded_data["function_sources"]

        # Restore functions from source code
        if function_sources:  # pragma: no cover
            restored_functions = {}  # pragma: no cover
            for func_name, source_code in function_sources.items():  # pragma: no cover
                try:  # pragma: no cover
                    # Create a namespace with common imports that functions might need
                    execution_namespace = {}  # pragma: no cover

                    # Add common imports to the execution namespace
                    try:  # pragma: no cover
                        import polars as pl  # pragma: no cover

                        execution_namespace["pl"] = pl  # pragma: no cover

                    except ImportError:  # pragma: no cover
                        pass  # pragma: no cover

                    try:  # pragma: no cover
                        import pandas as pd  # pragma: no cover

                        execution_namespace["pd"] = pd  # pragma: no cover

                    except ImportError:  # pragma: no cover
                        pass  # pragma: no cover

                    try:  # pragma: no cover
                        import narwhals as nw  # pragma: no cover

                        execution_namespace["nw"] = nw  # pragma: no cover

                    except ImportError:  # pragma: no cover
                        pass  # pragma: no cover

                    # Execute the function source code with the enhanced namespace
                    exec(source_code, execution_namespace, execution_namespace)  # pragma: no cover

                    # The function should now be in the execution namespace
                    if func_name in execution_namespace:  # pragma: no cover
                        restored_functions[func_name] = execution_namespace[
                            func_name
                        ]  # pragma: no cover
                    else:  # pragma: no cover
                        print(
                            f"Warning: Function '{func_name}' not found after executing source code"
                        )

                except Exception as e:  # pragma: no cover
                    print(f"Warning: Could not restore function '{func_name}': {e}")

            # Restore functions to validation steps
            for validation_info in validation.validation_info:  # pragma: no cover
                if (  # pragma: no cover
                    hasattr(validation_info, "_pb_function_name")
                    and validation_info._pb_function_name in restored_functions
                ):
                    func_name = validation_info._pb_function_name  # pragma: no cover
                    validation_info.pre = restored_functions[func_name]  # pragma: no cover
                    # Clean up the temporary attribute
                    delattr(validation_info, "_pb_function_name")  # pragma: no cover

        # Verify that we loaded a Validate object
        if not isinstance(validation, Validate):  # pragma: no cover
            raise RuntimeError(f"File does not contain a valid Validate object: {file_path}")

        return validation

    except Exception as e:
        raise RuntimeError(f"Failed to read validation object from {file_path}: {e}")


def _check_for_unpicklable_objects(validation: Validate) -> tuple[dict[str, str], list[int]]:
    """
    Check for functions and capture source code for preservation across sessions.

    This function examines all preprocessing functions and attempts to capture their source code for
    later restoration. Lambda functions are rejected. Functions that might be picklable in the
    current session but fail across sessions (e.g., interactively defined functions) have their
    source preserved.

    Returns
    -------
    tuple[dict[str, str], list[int]]
        A tuple containing:
        - A dictionary mapping function names to their source code
        - A list of step indices that have unpicklable lambda functions (which should cause errors)
    """
    import inspect
    import pickle

    unpicklable_lambda_steps = []
    function_sources = {}

    for i, validation_info in enumerate(validation.validation_info):
        if hasattr(validation_info, "pre") and validation_info.pre is not None:
            func = validation_info.pre
            func_name = getattr(func, "__name__", "<unknown>")

            # Always reject lambda functions
            if func_name == "<lambda>":
                unpicklable_lambda_steps.append((i, validation_info))
                continue

            # For all non-lambda functions, try to capture source code
            # This helps with functions that might be picklable now but fail across sessions
            source_code = None

            try:
                # Try to get the source code
                source_code = inspect.getsource(func)

                # Test if the function can be pickled and loaded in a clean environment
                # by checking if it's defined in a "real" module vs interactively
                func_module = getattr(func, "__module__", None)

                if func_module == "__main__" or not func_module:
                    # Functions defined in __main__ or without a module are risky
                    # These might pickle now but fail when loaded elsewhere
                    function_sources[func_name] = source_code  # pragma: no cover
                    validation_info._pb_function_name = func_name  # pragma: no cover

            except (OSError, TypeError):  # pragma: no cover
                # If we can't get source, check if it's at least picklable
                try:  # pragma: no cover
                    pickle.dumps(func, protocol=pickle.HIGHEST_PROTOCOL)  # pragma: no cover
                    # It's picklable but no source: this might cause issues across sessions
                    print(  # pragma: no cover
                        f"Warning: Function '{func_name}' is picklable but source code could not be captured. "
                        f"It may not be available when loading in a different session."
                    )
                except (pickle.PicklingError, AttributeError, TypeError):  # pragma: no cover
                    # Not picklable and no source: treat as problematic
                    print(  # pragma: no cover
                        f"Warning: Function '{func_name}' is not picklable and source could not be captured. "
                        f"It will not be available after saving/loading."
                    )
                    unpicklable_lambda_steps.append((i, validation_info))  # pragma: no cover

    # Only raise error for lambda functions now
    if unpicklable_lambda_steps:
        step_descriptions = []
        for i, step in unpicklable_lambda_steps:
            desc = f"Step {i + 1}"
            if hasattr(step, "assertion_type"):
                desc += f" ({step.assertion_type})"
            if hasattr(step, "column") and step.column:
                desc += f" on column '{step.column}'"
            step_descriptions.append(desc)

        raise ValueError(
            f"Cannot serialize validation object: found {len(unpicklable_lambda_steps)} validation step(s) "
            f"with unpicklable preprocessing functions (likely lambda functions defined in interactive "
            f"environments):\n\n"
            + "\n".join(f"  - {desc}" for desc in step_descriptions)
            + "\n\nTo resolve this, define your preprocessing functions at the module level:\n\n"
            "  # Instead of:\n"
            "  .col_vals_gt(columns='a', value=10, pre=lambda df: df.with_columns(...))\n\n"
            "  # Use:\n"
            "  def preprocess_data(df):\n"
            "      return df.with_columns(...)\n\n"
            "  .col_vals_gt(columns='a', value=10, pre=preprocess_data)\n\n"
            "Module-level functions can be pickled and will preserve the complete validation logic."
        )

    return function_sources, []


def _provide_serialization_guidance(validation: Validate) -> None:
    """
    Provide helpful guidance to users about creating serializable validations.

    This function analyzes the validation object and provides tailored advice
    about preprocessing functions, best practices, and potential issues.
    """
    import pickle

    # Find all preprocessing functions in the validation
    preprocessing_functions = []

    for i, validation_info in enumerate(validation.validation_info):
        if hasattr(validation_info, "pre") and validation_info.pre is not None:
            preprocessing_functions.append((i, validation_info))

    if not preprocessing_functions:  # pragma: no cover
        # No preprocessing functions: validation should serialize cleanly
        print("  Serialization Analysis:")  # pragma: no cover
        print("   ✓ No preprocessing functions detected")  # pragma: no cover
        print(
            "   ✓ This validation should serialize and load reliably across sessions"
        )  # pragma: no cover
        return  # pragma: no cover

    print("  Serialization Analysis:")  # pragma: no cover
    print(  # pragma: no cover
        f"   Found {len(preprocessing_functions)} validation step(s) with preprocessing functions"
    )

    # Analyze each function
    functions_analysis = {  # pragma: no cover
        "module_functions": [],
        "interactive_functions": [],
        "lambda_functions": [],
        "unpicklable_functions": [],
    }

    for i, validation_info in preprocessing_functions:  # pragma: no cover
        func = validation_info.pre  # pragma: no cover
        func_name = getattr(func, "__name__", "<unknown>")  # pragma: no cover
        func_module = getattr(func, "__module__", "<unknown>")  # pragma: no cover

        # Categorize the function
        if func_name == "<lambda>":  # pragma: no cover
            functions_analysis["lambda_functions"].append(
                (i, func_name, func_module)
            )  # pragma: no cover
        else:  # pragma: no cover
            # Test if it can be pickled
            try:  # pragma: no cover
                pickle.dumps(func, protocol=pickle.HIGHEST_PROTOCOL)  # pragma: no cover
                can_pickle = True  # pragma: no cover
            except (pickle.PicklingError, AttributeError, TypeError):  # pragma: no cover
                can_pickle = False  # pragma: no cover
                functions_analysis["unpicklable_functions"].append(
                    (i, func_name, func_module)
                )  # pragma: no cover
                continue  # pragma: no cover

            # Check if it's likely to work across sessions
            if (
                func_module == "__main__" or not func_module or func_module == "<unknown>"
            ):  # pragma: no cover
                # Function defined interactively - risky for cross-session use
                functions_analysis["interactive_functions"].append(
                    (i, func_name, func_module)
                )  # pragma: no cover
            else:  # pragma: no cover
                # Function from a proper module - should work reliably
                functions_analysis["module_functions"].append(
                    (i, func_name, func_module)
                )  # pragma: no cover

    # Provide specific guidance based on analysis
    if functions_analysis["module_functions"]:  # pragma: no cover
        print("   ✓ Module-level functions detected:")
        for i, func_name, func_module in functions_analysis["module_functions"]:
            print(f"     • Step {i + 1}: {func_name} (from {func_module})")
        print("     These should work reliably across sessions")

    if functions_analysis["interactive_functions"]:  # pragma: no cover
        print("      Interactive functions detected:")
        for i, func_name, func_module in functions_analysis["interactive_functions"]:
            print(f"     • Step {i + 1}: {func_name} (defined in {func_module})")
        print("     These may not load properly in different sessions")
        print()
        print("     Recommendation: Move these functions to a separate .py module:")
        print("      1. Create a file like 'preprocessing_functions.py'")
        print("      2. Define your functions there with proper imports")
        print("      3. Import them: from preprocessing_functions import your_function")
        print("      4. This ensures reliable serialization across sessions")

    if functions_analysis["lambda_functions"]:  # pragma: no cover
        print("     Lambda functions detected:")
        for i, func_name, func_module in functions_analysis["lambda_functions"]:
            print(f"     • Step {i + 1}: {func_name}")
        print("     Lambda functions cannot be serialized!")
        print()
        print("     Required fix: Replace lambda functions with named functions:")
        print("      # Instead of: pre=lambda df: df.with_columns(...)")
        print("      # Use: ")
        print("      def my_preprocessing_function(df):")
        print("          return df.with_columns(...)")
        print("      # Then: pre=my_preprocessing_function")

    if functions_analysis["unpicklable_functions"]:  # pragma: no cover
        print("     Unpicklable functions detected:")
        for i, func_name, func_module in functions_analysis["unpicklable_functions"]:
            print(f"     • Step {i + 1}: {func_name} (from {func_module})")
        print("     These functions cannot be serialized")

    # Provide overall assessment
    total_problematic = (
        len(functions_analysis["interactive_functions"])
        + len(functions_analysis["lambda_functions"])
        + len(functions_analysis["unpicklable_functions"])
    )

    if total_problematic == 0:  # pragma: no cover
        print("     All preprocessing functions should serialize reliably!")
    else:  # pragma: no cover
        print(
            f"      {total_problematic} function(s) may cause issues when loading in different sessions"
        )
        print()
        print("     Best Practice Guide:")
        print("      • Define all preprocessing functions in separate .py modules")
        print("      • Import functions before creating and loading validations")
        print("      • Avoid lambda functions and interactive definitions")
        print("      • Test your validation by loading it in a fresh Python session")

        # Offer to create a template
        print()
        print("     Example module structure:")
        print("      # preprocessing_functions.py")
        print("      import polars as pl  # or pandas, numpy, etc.")
        print("      ")
        print("      def multiply_by_factor(df, factor=10):")
        print("          return df.with_columns(pl.col('value') * factor)")
        print("      ")
        print("      # your_main_script.py")
        print("      import pointblank as pb")
        print("      from preprocessing_functions import multiply_by_factor")
        print("      ")
        print(
            "      validation = pb.Validate(data).col_vals_gt('value', 100, pre=multiply_by_factor)"
        )


def write_file(
    validation: Validate,
    filename: str,
    path: str | None = None,
    keep_tbl: bool = False,
    keep_extracts: bool = False,
    quiet: bool = False,
) -> None:
    """
    Write a Validate object to disk as a serialized file.

    Writing a validation object to disk with `write_file()` can be useful for keeping data
    validation results close at hand for later retrieval (with `read_file()`). By default, any data
    table that the validation object holds will be removed before writing to disk (not applicable if
    no data table is present). This behavior can be changed by setting `keep_tbl=True`, but this
    only works when the table is not of a database type (e.g., DuckDB, PostgreSQL, etc.), as
    database connections cannot be serialized.

    Extract data from failing validation steps can also be preserved by setting
    `keep_extracts=True`, which is useful for later analysis of data quality issues.

    The serialized file uses Python's pickle format for storage of the validation object state,
    including all validation results, metadata, and optionally the source data.

    **Important note.** If your validation uses custom preprocessing functions (via the `pre=`
    parameter), these functions must be defined at the module level (not interactively or as lambda
    functions) to ensure they can be properly restored when loading the validation in a different
    Python session. Read the *Creating Serializable Validations* section below for more information.

    :::{.callout-warning}
    The `write_file()` function is currently experimental. Please report any issues you encounter in
    the [Pointblank issue tracker](https://github.com/posit-dev/pointblank/issues).
    :::

    Parameters
    ----------
    validation
        The `Validate` object to write to disk.
    filename
        The filename to create on disk for the validation object. Should not include the file
        extension as `.pkl` will be added automatically.
    path
        An optional directory path where the file should be saved. If not provided, the file will be
        saved in the current working directory. The directory will be created if it doesn't exist.
    keep_tbl
        An option to keep the data table that is associated with the validation object. The default
        is `False` where the data table is removed before writing to disk. For database tables
        (e.g., Ibis tables with database backends), the table is always removed even if
        `keep_tbl=True`, as database connections cannot be serialized.
    keep_extracts
        An option to keep any collected extract data for failing rows from validation steps. By
        default, this is `False` (i.e., extract data is removed to save space).
    quiet
        Should the function not inform when the file is written? By default, this is `False`, so a
        message will be printed when the file is successfully written.

    Returns
    -------
    None
        This function doesn't return anything but saves the validation object to disk.

    Creating Serializable Validations
    ---------------------------------
    To ensure your validations work reliably across different Python sessions, the recommended
    approach is to use module-Level functions. So, create a separate Python file for your
    preprocessing functions:

    ```python
    # preprocessing_functions.py
    import polars as pl

    def multiply_by_100(df):
        return df.with_columns(pl.col("value") * 100)

    def add_computed_column(df):
        return df.with_columns(computed=pl.col("value") * 2 + 10)
    ```

    Then import and use them in your validation:

    ```python
    # your_main_script.py
    import pointblank as pb
    from preprocessing_functions import multiply_by_100, add_computed_column

    validation = (
        pb.Validate(data=my_data)
        .col_vals_gt(columns="value", value=500, pre=multiply_by_100)
        .col_vals_between(columns="computed", left=50, right=1000, pre=add_computed_column)
        .interrogate()
    )

    # Save validation and it will work reliably across sessions
    pb.write_file(validation, "my_validation", keep_tbl=True)
    ```

    ### Problematic Patterns to Avoid

    Don't use lambda functions as they will cause immediate errors.

    ```python
    validation = pb.Validate(data).col_vals_gt(
        columns="value", value=100,
        pre=lambda df: df.with_columns(pl.col("value") * 2)
    )
    ```

    Don't use interactive function definitions (as they may fail when loading).

    ```python
    def my_function(df):  # Defined in notebook/REPL
        return df.with_columns(pl.col("value") * 2)

    validation = pb.Validate(data).col_vals_gt(
        columns="value", value=100, pre=my_function
    )
    ```

    ### Automatic Analysis and Guidance

    When you call `write_file()`, it automatically analyzes your validation and provides:

    - confirmation when all functions will work reliably
    - warnings for functions that may cause cross-session issues
    - clear errors for unsupported patterns (lambda functions)
    - specific recommendations and code examples
    - loading instructions tailored to your validation

    ### Loading Your Validation

    To load a saved validation in a new Python session:

    ```python
    # In a new Python session
    import pointblank as pb

    # Import the same preprocessing functions used when creating the validation
    from preprocessing_functions import multiply_by_100, add_computed_column

    # Upon loading the validation, functions will be automatically restored
    validation = pb.read_file("my_validation.pkl")
    ```

    ** Testing Your Validation:**

    To verify your validation works across sessions:

    1. save your validation in one Python session
    2. start a fresh Python session (restart kernel/interpreter)
    3. import required preprocessing functions
    4. load the validation using `read_file()`
    5. test that preprocessing functions work as expected

    ### Performance and Storage

    - use `keep_tbl=False` (default) to reduce file size when you don't need the original data
    - use `keep_extracts=False` (default) to save space by excluding extract data
    - set `quiet=True` to suppress guidance messages in automated scripts
    - files are saved using pickle's highest protocol for optimal performance

    Examples
    --------
    Let's create a simple validation and save it to disk:

    ```{python}
    import pointblank as pb

    # Create a validation
    validation = (
        pb.Validate(data=pb.load_dataset("small_table"), label="My validation")
        .col_vals_gt(columns="d", value=100)
        .col_vals_regex(columns="b", pattern=r"[0-9]-[a-z]{3}-[0-9]{3}")
        .interrogate()
    )

    # Save to disk (without the original table data)
    pb.write_file(validation, "my_validation")
    ```

    To keep the original table data for later analysis:

    ```{python}
    # Save with the original table data included
    pb.write_file(validation, "my_validation_with_data", keep_tbl=True)
    ```

    You can also specify a custom directory and keep extract data:

    ```python
    pb.write_file(
        validation,
        filename="detailed_validation",
        path="/path/to/validations",
        keep_tbl=True,
        keep_extracts=True
    )
    ```

    ### Working with Preprocessing Functions

    For validations that use preprocessing functions to be portable across sessions, define your
    functions in a separate `.py` file:

    ```python
    # In `preprocessing_functions.py`

    import polars as pl

    def multiply_by_100(df):
        return df.with_columns(pl.col("value") * 100)

    def add_computed_column(df):
        return df.with_columns(computed=pl.col("value") * 2 + 10)
    ```

    Then import and use them in your validation:

    ```python
    # In your main script

    import pointblank as pb
    from preprocessing_functions import multiply_by_100, add_computed_column

    validation = (
        pb.Validate(data=my_data)
        .col_vals_gt(columns="value", value=500, pre=multiply_by_100)
        .col_vals_between(columns="computed", left=50, right=1000, pre=add_computed_column)
        .interrogate()
    )

    # This validation can now be saved and loaded reliably
    pb.write_file(validation, "my_validation", keep_tbl=True)
    ```

    When you load this validation in a new session, simply import the preprocessing functions
    again and they will be automatically restored.

    See Also
    --------
    Use the [`read_file()`](`pointblank.read_file`) function to load a validation object that was
    previously saved with `write_file()`.
    """
    # Construct the full file path
    if not filename.endswith(".pkl"):
        filename = f"{filename}.pkl"

    if path is not None:
        file_path = Path(path) / filename
    else:
        file_path = Path(filename)

    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a copy of the validation object to avoid modifying the original
    validation_copy = copy.deepcopy(validation)

    # Handle data table preservation
    if not keep_tbl:
        validation_copy.data = None
    else:
        # Check if the data is a database table that cannot be serialized
        if validation_copy.data is not None:
            tbl_type = _get_tbl_type(validation_copy.data)

            # Database tables cannot be serialized, so remove them regardless of keep_tbl
            if tbl_type in [
                "duckdb",
                "mysql",
                "postgresql",
                "sqlite",
                "mssql",
                "snowflake",
                "databricks",
                "bigquery",
            ]:
                validation_copy.data = None
                if not quiet:  # pragma: no cover
                    print(
                        f"Note: Database table removed from saved validation "
                        f"(table type: {tbl_type})"
                    )

    # Handle extract data preservation
    if not keep_extracts:
        # Remove extract data from validation_info to save space
        for validation_info in validation_copy.validation_info:
            if hasattr(validation_info, "extract"):
                validation_info.extract = None

    # Provide user guidance about serialization if not quiet
    if not quiet:
        _provide_serialization_guidance(validation_copy)

    # Check for unpicklable objects and capture function sources
    function_sources, lambda_steps = _check_for_unpicklable_objects(validation_copy)

    # Create a validation package that includes both the object and function sources
    validation_package = {"validation": validation_copy, "function_sources": function_sources}

    # Serialize to disk using pickle
    try:
        with open(file_path, "wb") as f:
            pickle.dump(validation_package, f, protocol=pickle.HIGHEST_PROTOCOL)

        if not quiet:  # pragma: no cover
            print(f"✅ Validation object written to: {file_path}")

            if function_sources:  # pragma: no cover
                print(
                    f"   🔧 Enhanced preservation: Captured source code for {len(function_sources)} function(s)"
                )
                for func_name in function_sources.keys():
                    print(f"      • {func_name}")
                print("   📥 These functions will be automatically restored when loading")

            # Provide loading instructions
            preprocessing_funcs = [
                info
                for info in validation_copy.validation_info
                if hasattr(info, "pre") and info.pre is not None
            ]
            if preprocessing_funcs:
                print()
                print("   💡 To load this validation in a new session:")
                print("      import pointblank as pb")
                if any(
                    hasattr(info.pre, "__module__")
                    and info.pre.__module__ not in ["__main__", None]
                    for info in preprocessing_funcs
                    if hasattr(info, "pre") and info.pre
                ):
                    print("      # Import any preprocessing functions from their modules")
                    modules_mentioned = set()
                    for info in preprocessing_funcs:
                        if (
                            hasattr(info, "pre")
                            and hasattr(info.pre, "__module__")
                            and info.pre.__module__ not in ["__main__", None]
                        ):
                            if info.pre.__module__ not in modules_mentioned:
                                print(
                                    f"      from {info.pre.__module__} import {info.pre.__name__}"
                                )
                                modules_mentioned.add(info.pre.__module__)
                print(f"      validation = pb.read_file('{file_path.name}')")
            else:
                print("   📖 To load: validation = pb.read_file('{}')".format(file_path.name))

    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            f"Failed to write validation object to {file_path}: {e}"
        )  # pragma: no cover


def get_data_path(
    dataset: Literal["small_table", "game_revenue", "nycflights", "global_sales"] = "small_table",
    file_type: Literal["csv", "parquet", "duckdb"] = "csv",
) -> str:
    """
    Get the file path to a dataset included with the Pointblank package.

    This function provides direct access to the file paths of datasets included with Pointblank.
    These paths can be used in examples and documentation to demonstrate file-based data loading
    without requiring the actual data files. The returned paths can be used with
    `Validate(data=path)` to demonstrate CSV and Parquet file loading capabilities.

    Parameters
    ----------
    dataset
        The name of the dataset to get the path for. Current options are `"small_table"`,
        `"game_revenue"`, `"nycflights"`, and `"global_sales"`.
    file_type
        The file format to get the path for. Options are `"csv"`, `"parquet"`, or `"duckdb"`.

    Returns
    -------
    str
        The file path to the requested dataset file.

    Included Datasets
    -----------------
    The available datasets are the same as those in [`load_dataset()`](`pointblank.load_dataset`):

    - `"small_table"`: A small dataset with 13 rows and 8 columns. Ideal for testing and examples.
    - `"game_revenue"`: A dataset with 2000 rows and 11 columns. Revenue data for a game company.
    - `"nycflights"`: A dataset with 336,776 rows and 18 columns. Flight data from NYC airports.
    - `"global_sales"`: A dataset with 50,000 rows and 20 columns. Global sales data across regions.

    File Types
    ----------
    Each dataset is available in multiple formats:

    - `"csv"`: Comma-separated values file (`.csv`)
    - `"parquet"`: Parquet file (`.parquet`)
    - `"duckdb"`: DuckDB database file (`.ddb`)

    Examples
    --------
    Get the path to a CSV file and use it with `Validate`:

    ```{python}
    import pointblank as pb

    # Get path to the small_table CSV file
    csv_path = pb.get_data_path("small_table", "csv")
    print(csv_path)

    # Use the path directly with Validate
    validation = (
        pb.Validate(data=csv_path)
        .col_exists(["a", "b", "c"])
        .col_vals_gt(columns="d", value=0)
        .interrogate()
    )

    validation
    ```

    Get a Parquet file path for validation examples:

    ```{python}
    # Get path to the game_revenue Parquet file
    parquet_path = pb.get_data_path(dataset="game_revenue", file_type="parquet")

    # Validate the Parquet file directly
    validation = (
        pb.Validate(data=parquet_path, label="Game Revenue Data Validation")
        .col_vals_not_null(columns=["player_id", "session_id"])
        .col_vals_gt(columns="item_revenue", value=0)
        .interrogate()
    )

    validation
    ```

    This is particularly useful for documentation examples where you want to demonstrate
    file-based workflows without requiring users to have specific data files:

    ```{python}
    # Example showing CSV file validation
    sales_csv = pb.get_data_path(dataset="global_sales", file_type="csv")

    validation = (
        pb.Validate(data=sales_csv, label="Sales Data Validation")
        .col_exists(["customer_id", "product_id", "amount"])
        .col_vals_regex(columns="customer_id", pattern=r"CUST_[0-9]{6}")
        .interrogate()
    )
    ```

    See Also
    --------
    [`load_dataset()`](`pointblank.load_dataset`) for loading datasets directly as table objects.
    """

    # Validate inputs
    if dataset not in ["small_table", "game_revenue", "nycflights", "global_sales"]:
        raise ValueError(
            f"The dataset name `{dataset}` is not valid. Choose one of the following:\n"
            "- `small_table`\n"
            "- `game_revenue`\n"
            "- `nycflights`\n"
            "- `global_sales`"
        )

    if file_type not in ["csv", "parquet", "duckdb"]:
        raise ValueError(
            f"The file type `{file_type}` is not valid. Choose one of the following:\n"
            "- `csv`\n"
            "- `parquet`\n"
            "- `duckdb`"
        )

    if file_type == "csv":
        # Return path to CSV file inside the zip
        data_path = files("pointblank.data") / f"{dataset}.zip"

        # For CSV files, we need to extract from zip to a temporary location
        # since most libraries expect actual file paths, not zip contents
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as tmp_file:
            with ZipFile(data_path) as zip_file:
                csv_content = zip_file.read(f"{dataset}.csv")
                tmp_file.write(csv_content)
                return tmp_file.name

    elif file_type == "parquet":
        # Create a temporary parquet file from the CSV data
        data_path = files("pointblank.data") / f"{dataset}.zip"

        # We'll need to convert CSV to Parquet temporarily
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".parquet", delete=False) as tmp_file:
            # Load CSV data and save as Parquet
            if _is_lib_present(lib_name="polars"):
                import polars as pl

                df = pl.read_csv(ZipFile(data_path).read(f"{dataset}.csv"), try_parse_dates=True)
                df.write_parquet(tmp_file.name)
            elif _is_lib_present(lib_name="pandas"):
                import pandas as pd

                df = pd.read_csv(data_path)
                df.to_parquet(tmp_file.name, index=False)
            else:
                raise ImportError(
                    "Either Polars or Pandas is required to create temporary Parquet files."
                )
            return tmp_file.name

    elif file_type == "duckdb":
        # Return path to DuckDB file
        data_path = files("pointblank.data") / f"{dataset}-duckdb.zip"

        # Extract DuckDB file to temporary location
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".ddb", delete=False) as tmp_file:
            with ZipFile(data_path) as zip_file:
                ddb_content = zip_file.read(f"{dataset}.ddb")
                tmp_file.write(ddb_content)
                return tmp_file.name


def _process_data(data: FrameT | Any) -> FrameT | Any:
    """
    Centralized data processing pipeline that handles all supported input types.

    This function consolidates the data processing pipeline used across multiple classes and
    functions in Pointblank. It processes data through a consistent sequence of transformations to
    handle different data source types.

    The processing order is important:

    1. GitHub URLs (must come before connection string processing)
    2. Database connection strings
    3. CSV file paths
    4. Parquet file paths

    Parameters
    ----------
    data : FrameT | Any
        The input data which could be:
        - a DataFrame object (Polars, Pandas, Ibis, etc.)
        - a GitHub URL pointing to a CSV or Parquet file
        - a database connection string (e.g., "duckdb:///path/to/file.ddb::table_name")
        - a CSV file path (string or Path object with .csv extension)
        - a Parquet file path, glob pattern, directory, or partitioned dataset
        - any other data type (returned unchanged)

    Returns
    -------
    FrameT | Any
        Processed data as a DataFrame if input was a supported data source type,
        otherwise the original data unchanged.
    """
    # Handle GitHub URL input (e.g., "https://github.com/user/repo/blob/main/data.csv")
    data = _process_github_url(data)

    # Handle connection string input (e.g., "duckdb:///path/to/file.ddb::table_name")
    data = _process_connection_string(data)

    # Handle CSV file input (e.g., "data.csv" or Path("data.csv"))
    data = _process_csv_input(data)

    # Handle Parquet file input (e.g., "data.parquet", "data/*.parquet", "data/")
    data = _process_parquet_input(data)

    return data


def _process_github_url(data: FrameT | Any) -> FrameT | Any:
    """
    Process data parameter to handle GitHub URLs pointing to CSV or Parquet files.

    Handles both standard GitHub URLs and raw GitHub content URLs, downloading the content
    and processing it as a local file.

    Supports:
    - Standard github.com URLs pointing to CSV or Parquet files (automatically transformed to raw URLs)
    - Raw raw.githubusercontent.com URLs pointing to CSV or Parquet files (processed directly)
    - Both CSV and Parquet file formats
    - Automatic temporary file management and cleanup

    Parameters
    ----------
    data : FrameT | Any
        The data parameter which may be a GitHub URL string or any other data type.

    Returns
    -------
    FrameT | Any
        If the input is a supported GitHub URL, returns a DataFrame loaded from the downloaded file.
        Otherwise, returns the original data unchanged.

    Examples
    --------
    Standard GitHub URL (automatically transformed):
    >>> url = "https://github.com/user/repo/blob/main/data.csv"
    >>> df = _process_github_url(url)

    Raw GitHub URL (used directly):
    >>> raw_url = "https://raw.githubusercontent.com/user/repo/main/data.csv"
    >>> df = _process_github_url(raw_url)
    """
    import re
    import tempfile
    from urllib.parse import urlparse
    from urllib.request import urlopen

    # Check if data is a string that looks like a GitHub URL
    if not isinstance(data, str):
        return data

    # Parse the URL to check if it's a GitHub URL
    try:
        parsed = urlparse(data)
    except ValueError:
        # urlparse can raise ValueError for malformed URLs (e.g., invalid IPv6)
        # Return original data as it's likely not a GitHub URL we can process
        return data

    # Check if it's a GitHub URL (standard or raw)
    is_standard_github = parsed.netloc in ["github.com", "www.github.com"]
    is_raw_github = parsed.netloc == "raw.githubusercontent.com"

    if not (is_standard_github or is_raw_github):
        return data

    # Check if it points to a CSV or Parquet file
    path_lower = parsed.path.lower()
    if not (path_lower.endswith(".csv") or path_lower.endswith(".parquet")):
        return data

    # Determine the raw URL to download from
    if is_raw_github:
        # Already a raw GitHub URL, use it directly
        raw_url = data
    else:
        # Transform GitHub URL to raw content URL
        # Pattern: https://github.com/user/repo/blob/branch/path/file.ext
        # Becomes: https://raw.githubusercontent.com/user/repo/branch/path/file.ext
        github_pattern = r"github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)"
        match = re.search(github_pattern, data)

        if not match:
            # If URL doesn't match expected GitHub blob pattern, return original data
            return data

        user, repo, branch, file_path = match.groups()
        raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"

    # Download the file content to a temporary file
    try:
        with urlopen(raw_url) as response:
            content = response.read()

        # Determine file extension
        file_ext = ".csv" if path_lower.endswith(".csv") else ".parquet"

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="wb", suffix=file_ext, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Process the temporary file using existing CSV or Parquet processing functions
        if file_ext == ".csv":
            return _process_csv_input(tmp_file_path)
        else:  # .parquet
            return _process_parquet_input(tmp_file_path)

    except Exception:  # pragma: no cover
        # If download or processing fails, return original data
        return data


def _process_connection_string(data: FrameT | Any) -> FrameT | Any:
    """
    Process data parameter to handle database connection strings.

    Uses the `connect_to_table()` utility function to handle URI-formatted connection strings with
    table specifications. Returns the original data if it's not a connection string.

    For more details on supported connection string formats, see the documentation
    for `connect_to_table()`.
    """
    # Check if data is a string that looks like a connection string
    if not isinstance(data, str):
        return data

    # Basic connection string patterns
    connection_patterns = [
        "://",  # General URL-like pattern
    ]

    # Check if it looks like a connection string
    if not any(pattern in data for pattern in connection_patterns):
        return data

    # Use the utility function to connect to the table
    return connect_to_table(data)


def _process_csv_input(data: FrameT | Any) -> FrameT | Any:
    """
    Process data parameter to handle CSV file inputs.

    If data is a string or Path with .csv extension, reads the CSV file
    using available libraries (Polars preferred, then Pandas).

    Returns the original data if it's not a CSV file path.
    """
    from pathlib import Path

    # Check if data is a string or Path-like object with .csv extension
    csv_path = None

    if isinstance(data, (str, Path)):
        path_obj = Path(data)
        if path_obj.suffix.lower() == ".csv":
            csv_path = path_obj

    # If it's not a CSV file path, return the original data
    if csv_path is None:
        return data

    # Check if the CSV file exists
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Determine which library to use for reading CSV: prefer Polars but fallback to Pandas
    if _is_lib_present(lib_name="polars"):
        try:
            import polars as pl

            return pl.read_csv(csv_path, try_parse_dates=True)
        except Exception as e:
            # If Polars fails, try Pandas if available
            if _is_lib_present(lib_name="pandas"):
                import pandas as pd

                return pd.read_csv(csv_path)
            else:  # pragma: no cover
                raise RuntimeError(
                    f"Failed to read CSV file with Polars: {e}. "
                    "Pandas is not available as fallback."
                ) from e
    elif _is_lib_present(lib_name="pandas"):
        try:
            import pandas as pd

            return pd.read_csv(csv_path)
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV file with Pandas: {e}") from e
    else:
        raise ImportError(
            "Neither Polars nor Pandas is available for reading CSV files. "
            "Please install either 'polars' or 'pandas' to use CSV file inputs."
        )


def _process_parquet_input(data: FrameT | Any) -> FrameT | Any:
    """
    Process data parameter to handle Parquet file inputs.

    Supports:
    - single .parquet file (string or Path)
    - glob patterns for multiple .parquet files (e.g., "data/*.parquet")
    - directory containing .parquet files
    - partitioned Parquet datasets with automatic partition column inference
    - list/sequence of .parquet file paths

    Returns the original data if it's not a Parquet file input.
    """
    import glob
    from pathlib import Path

    parquet_paths = []

    # Handle different input types
    if isinstance(data, (str, Path)):
        data_str = str(data)
        path_obj = Path(data)

        # Check if it's a glob pattern containing .parquet first; look for glob
        # characters: `*`, `?`, `[`, `]`
        if ".parquet" in data_str.lower() and any(
            char in data_str for char in ["*", "?", "[", "]"]
        ):
            parquet_files = glob.glob(data_str)
            if parquet_files:
                parquet_paths = sorted([Path(f) for f in parquet_files])
            else:
                raise FileNotFoundError(f"No files found matching pattern: {data}")

        # Check if it's a single .parquet file
        elif path_obj.suffix.lower() == ".parquet":
            if path_obj.exists():
                parquet_paths = [path_obj]
            else:
                raise FileNotFoundError(f"Parquet file not found: {path_obj}")

        # Check if it's a directory
        elif path_obj.is_dir():
            # First, try to read as a partitioned parquet dataset; This handles datasets where
            # Parquet files are in subdirectories with partition columns encoded in paths
            try:
                # Both Polars and Pandas can handle partitioned datasets natively
                if _is_lib_present(lib_name="polars"):
                    import polars as pl

                    # Try reading as partitioned dataset first
                    df = pl.read_parquet(str(path_obj))
                    return df
                elif _is_lib_present(lib_name="pandas"):
                    import pandas as pd

                    # Try reading as partitioned dataset first
                    df = pd.read_parquet(str(path_obj))
                    return df
            except Exception:
                # If partitioned read fails, fall back to simple directory scan
                pass

            # Fallback: Look for .parquet files directly in the directory
            parquet_files = list(path_obj.glob("*.parquet"))
            if parquet_files:
                parquet_paths = sorted(parquet_files)
            else:
                raise FileNotFoundError(
                    f"No .parquet files found in directory: {path_obj}. "
                    f"This could be a non-partitioned directory without .parquet files, "
                    f"or a partitioned dataset that couldn't be read."
                )

            # If it's not a parquet file, directory, or glob pattern, return original data
        else:
            return data

    # Handle list/sequence of paths
    elif isinstance(data, (list, tuple)):
        for item in data:
            item_path = Path(item)
            if item_path.suffix.lower() == ".parquet":
                if item_path.exists():
                    parquet_paths.append(item_path)
                else:
                    raise FileNotFoundError(f"Parquet file not found: {item_path}")
            else:
                # If any item is not a parquet file, return original data
                return data

    # If no parquet files found, return original data
    if not parquet_paths:
        return data

    # Read the parquet file(s) using available libraries; prefer Polars, fallback to Pandas
    if _is_lib_present(lib_name="polars"):
        try:
            import polars as pl

            if len(parquet_paths) == 1:
                # Single file
                return pl.read_parquet(parquet_paths[0])
            else:
                # Multiple files: concatenate them
                dfs = [pl.read_parquet(path) for path in parquet_paths]
                return pl.concat(dfs, how="vertical_relaxed")
        except Exception as e:
            # If Polars fails, try Pandas if available
            if _is_lib_present(lib_name="pandas"):
                import pandas as pd

                if len(parquet_paths) == 1:
                    return pd.read_parquet(parquet_paths[0])
                else:
                    # Multiple files: concatenate them
                    dfs = [pd.read_parquet(path) for path in parquet_paths]
                    return pd.concat(dfs, ignore_index=True)
            else:  # pragma: no cover
                raise RuntimeError(
                    f"Failed to read Parquet file(s) with Polars: {e}. "
                    "Pandas is not available as fallback."
                ) from e
    elif _is_lib_present(lib_name="pandas"):
        try:
            import pandas as pd

            if len(parquet_paths) == 1:
                return pd.read_parquet(parquet_paths[0])
            else:
                # Multiple files: concatenate them
                dfs = [pd.read_parquet(path) for path in parquet_paths]
                return pd.concat(dfs, ignore_index=True)
        except Exception as e:
            raise RuntimeError(f"Failed to read Parquet file(s) with Pandas: {e}") from e
    else:
        raise ImportError(
            "Neither Polars nor Pandas is available for reading Parquet files. "
            "Please install either 'polars' or 'pandas' to use Parquet file inputs."
        )


def preview(
    data: FrameT | Any,
    columns_subset: str | list[str] | Column | None = None,
    n_head: int = 5,
    n_tail: int = 5,
    limit: int = 50,
    show_row_numbers: bool = True,
    max_col_width: int = 250,
    min_tbl_width: int = 500,
    incl_header: bool = None,
) -> GT:
    """
    Display a table preview that shows some rows from the top, some from the bottom.

    To get a quick look at the data in a table, we can use the `preview()` function to display a
    preview of the table. The function shows a subset of the rows from the start and end of the
    table, with the number of rows from the start and end determined by the `n_head=` and `n_tail=`
    parameters (set to `5` by default). This function works with any table that is supported by the
    `pointblank` library, including Pandas, Polars, and Ibis backend tables (e.g., DuckDB, MySQL,
    PostgreSQL, SQLite, Parquet, etc.).

    The view is optimized for readability, with column names and data types displayed in a compact
    format. The column widths are sized to fit the column names, dtypes, and column content up to
    a configurable maximum width of `max_col_width=` pixels. The table can be scrolled horizontally
    to view even very large datasets. Since the output is a Great Tables (`GT`) object, it can be
    further customized using the `great_tables` API.

    Parameters
    ----------
    data
        The table to preview, which could be a DataFrame object, an Ibis table object, a CSV
        file path, a Parquet file path, or a database connection string. When providing a CSV or
        Parquet file path (as a string or `pathlib.Path` object), the file will be automatically
        loaded using an available DataFrame library (Polars or Pandas). Parquet input also supports
        glob patterns, directories containing .parquet files, and Spark-style partitioned datasets.
        Connection strings enable direct database access via Ibis with optional table specification
        using the `::table_name` suffix. Read the *Supported Input Table Types* section for details
        on the supported table types.
    columns_subset
        The columns to display in the table, by default `None` (all columns are shown). This can
        be a string, a list of strings, a `Column` object, or a `ColumnSelector` object. The latter
        two options allow for more flexible column selection using column selector functions. Errors
        are raised if the column names provided don't match any columns in the table (when provided
        as a string or list of strings) or if column selector expressions don't resolve to any
        columns.
    n_head
        The number of rows to show from the start of the table. Set to `5` by default.
    n_tail
        The number of rows to show from the end of the table. Set to `5` by default.
    limit
        The limit value for the sum of `n_head=` and `n_tail=` (the total number of rows shown).
        If the sum of `n_head=` and `n_tail=` exceeds the limit, an error is raised. The default
        value is `50`.
    show_row_numbers
        Should row numbers be shown? The numbers shown reflect the row numbers of the head and tail
        in the input `data=` table. By default, this is set to `True`.
    max_col_width
        The maximum width of the columns (in pixels) before the text is truncated. The default value
        is `250` (`"250px"`).
    min_tbl_width
        The minimum width of the table in pixels. If the sum of the column widths is less than this
        value, the all columns are sized up to reach this minimum width value. The default value is
        `500` (`"500px"`).
    incl_header
        Should the table include a header with the table type and table dimensions? Set to `True` by
        default.

    Returns
    -------
    GT
        A GT object that displays the preview of the table.

    Supported Input Table Types
    ---------------------------
    The `data=` parameter can be given any of the following table types:

    - Polars DataFrame (`"polars"`)
    - Pandas DataFrame (`"pandas"`)
    - PySpark table (`"pyspark"`)
    - DuckDB table (`"duckdb"`)*
    - MySQL table (`"mysql"`)*
    - PostgreSQL table (`"postgresql"`)*
    - SQLite table (`"sqlite"`)*
    - Microsoft SQL Server table (`"mssql"`)*
    - Snowflake table (`"snowflake"`)*
    - Databricks table (`"databricks"`)*
    - BigQuery table (`"bigquery"`)*
    - Parquet table (`"parquet"`)*
    - CSV files (string path or `pathlib.Path` object with `.csv` extension)
    - Parquet files (string path, `pathlib.Path` object, glob pattern, directory with `.parquet`
    extension, or partitioned dataset)
    - Database connection strings (URI format with optional table specification)

    The table types marked with an asterisk need to be prepared as Ibis tables (with type of
    `ibis.expr.types.relations.Table`). Furthermore, using `preview()` with these types of tables
    requires the Ibis library (`v9.5.0` or above) to be installed. If the input table is a Polars or
    Pandas DataFrame, the availability of Ibis is not needed.

    To use a CSV file, ensure that a string or `pathlib.Path` object with a `.csv` extension is
    provided. The file will be automatically detected and loaded using the best available DataFrame
    library. The loading preference is Polars first, then Pandas as a fallback.

    Connection strings follow database URL formats and must also specify a table using the
    `::table_name` suffix. Examples include:

    ```
    "duckdb:///path/to/database.ddb::table_name"
    "sqlite:///path/to/database.db::table_name"
    "postgresql://user:password@localhost:5432/database::table_name"
    "mysql://user:password@localhost:3306/database::table_name"
    "bigquery://project/dataset::table_name"
    "snowflake://user:password@account/database/schema::table_name"
    ```

    When using connection strings, the Ibis library with the appropriate backend driver is required.

    Examples
    --------
    It's easy to preview a table using the `preview()` function. Here's an example using the
    `small_table` dataset (itself loaded using the [`load_dataset()`](`pointblank.load_dataset`)
    function):

    ```{python}
    import pointblank as pb

    small_table_polars = pb.load_dataset("small_table")

    pb.preview(small_table_polars)
    ```

    This table is a Polars DataFrame, but the `preview()` function works with any table supported
    by `pointblank`, including Pandas DataFrames and Ibis backend tables. Here's an example using
    a DuckDB table handled by Ibis:

    ```{python}
    small_table_duckdb = pb.load_dataset("small_table", tbl_type="duckdb")

    pb.preview(small_table_duckdb)
    ```

    The blue dividing line marks the end of the first `n_head=` rows and the start of the last
    `n_tail=` rows.

    We can adjust the number of rows shown from the start and end of the table by setting the
    `n_head=` and `n_tail=` parameters. Let's enlarge each of these to `10`:

    ```{python}
    pb.preview(small_table_polars, n_head=10, n_tail=10)
    ```

    In the above case, the entire dataset is shown since the sum of `n_head=` and `n_tail=` is
    greater than the number of rows in the table (which is 13).

    The `columns_subset=` parameter can be used to show only specific columns in the table. You can
    provide a list of column names to make the selection. Let's try that with the `"game_revenue"`
    dataset as a Pandas DataFrame:

    ```{python}
    game_revenue_pandas = pb.load_dataset("game_revenue", tbl_type="pandas")

    pb.preview(game_revenue_pandas, columns_subset=["player_id", "item_name", "item_revenue"])
    ```

    Alternatively, we can use column selector functions like
    [`starts_with()`](`pointblank.starts_with`) and [`matches()`](`pointblank.matches`)` to select
    columns based on text or patterns:

    ```{python}
    pb.preview(game_revenue_pandas, n_head=2, n_tail=2, columns_subset=pb.starts_with("session"))
    ```

    Multiple column selector functions can be combined within [`col()`](`pointblank.col`) using
    operators like `|` and `&`:

    ```{python}
    pb.preview(
      game_revenue_pandas,
      n_head=2,
      n_tail=2,
      columns_subset=pb.col(pb.starts_with("item") | pb.matches("player"))
    )
    ```

    ### Working with CSV Files

    The `preview()` function can directly accept CSV file paths, making it easy to preview data
    stored in CSV files without manual loading:

    ```{python}
    # Get a path to a CSV file from the package data
    csv_path = pb.get_data_path("global_sales", "csv")

    pb.preview(csv_path)
    ```

    You can also use a Path object to specify the CSV file:

    ```{python}
    from pathlib import Path

    csv_file = Path(pb.get_data_path("game_revenue", "csv"))

    pb.preview(csv_file, n_head=3, n_tail=3)
    ```

    ### Working with Parquet Files

    The `preview()` function can directly accept Parquet files and datasets in various formats:

    ```{python}
    # Single Parquet file from package data
    parquet_path = pb.get_data_path("nycflights", "parquet")

    pb.preview(parquet_path)
    ```

    You can also use glob patterns and directories:

    ```python
    # Multiple Parquet files with glob patterns
    pb.preview("data/sales_*.parquet")

    # Directory containing Parquet files
    pb.preview("parquet_data/")

    # Partitioned Parquet dataset
    pb.preview("sales_data/")  # Auto-discovers partition columns
    ```

    ### Working with Database Connection Strings

    The `preview()` function supports database connection strings for direct preview of database
    tables. Connection strings must specify a table using the `::table_name` suffix:

    ```{python}
    # Get path to a DuckDB database file from package data
    duckdb_path = pb.get_data_path("game_revenue", "duckdb")

    pb.preview(f"duckdb:///{duckdb_path}::game_revenue")
    ```

    For comprehensive documentation on supported connection string formats, error handling, and
    installation requirements, see the [`connect_to_table()`](`pointblank.connect_to_table`)
    function.
    """

    # Process input data to handle different data source types
    data = _process_data(data)

    if incl_header is None:
        incl_header = global_config.preview_incl_header

    return _generate_display_table(
        data=data,
        columns_subset=columns_subset,
        n_head=n_head,
        n_tail=n_tail,
        limit=limit,
        show_row_numbers=show_row_numbers,
        max_col_width=max_col_width,
        min_tbl_width=min_tbl_width,
        incl_header=incl_header,
        mark_missing_values=True,
    )


def _generate_display_table(
    data: FrameT | Any,
    columns_subset: str | list[str] | Column | None = None,
    n_head: int = 5,
    n_tail: int = 5,
    limit: int | None = 50,
    show_row_numbers: bool = True,
    max_col_width: int = 250,
    min_tbl_width: int = 500,
    incl_header: bool = None,
    mark_missing_values: bool = True,
    row_number_list: list[int] | None = None,
) -> GT:
    # Make a copy of the data to avoid modifying the original
    # Note: PySpark DataFrames cannot be deep copied due to SparkContext serialization issues
    tbl_type = _get_tbl_type(data=data)
    if "pyspark" not in tbl_type:
        data = copy.deepcopy(data)

    # Does the data table already have a leading row number column?
    if "_row_num_" in data.columns:
        if data.columns[0] == "_row_num_":
            has_leading_row_num_col = True
        else:
            has_leading_row_num_col = False
    else:
        has_leading_row_num_col = False

    # Check that the n_head and n_tail aren't greater than the limit
    if n_head + n_tail > limit:
        raise ValueError(f"The sum of `n_head=` and `n_tail=` cannot exceed the limit ({limit}).")

    # Do we have a DataFrame library to work with? We need at least one to display
    # the table using Great Tables
    _check_any_df_lib(method_used="preview_tbl")

    # Set flag for whether the full dataset is shown, or just the head and tail; if the table
    # is very small, the value likely will be `True`
    full_dataset = False

    # Determine if the table is a DataFrame or an Ibis table
    tbl_type = _get_tbl_type(data=data)
    ibis_tbl = "ibis.expr.types.relations.Table" in str(type(data))
    pl_pb_tbl = "polars" in tbl_type or "pandas" in tbl_type or "pyspark" in tbl_type

    # Select the DataFrame library to use for displaying the Ibis table
    df_lib_gt = _select_df_lib(preference="polars")
    df_lib_name_gt = df_lib_gt.__name__

    # If the table is a DataFrame (Pandas, Polars, or PySpark), set `df_lib_name_gt` to the name of the
    # library (e.g., "polars", "pandas", or "pyspark")
    if pl_pb_tbl:
        if "polars" in tbl_type:
            df_lib_name_gt = "polars"
        elif "pandas" in tbl_type:
            df_lib_name_gt = "pandas"
        elif "pyspark" in tbl_type:
            df_lib_name_gt = "pyspark"

        # Handle imports of Polars, Pandas, or PySpark here
        if df_lib_name_gt == "polars":
            import polars as pl
        elif df_lib_name_gt == "pandas":
            import pandas as pd
        elif df_lib_name_gt == "pyspark":
            # Import pandas for conversion since Great Tables needs pandas DataFrame
            import pandas as pd
        # Note: PySpark import is handled as needed, typically already imported in user's environment

    # Get the initial column count for the table
    n_columns = len(data.columns)

    # If `columns_subset=` is not None, resolve the columns to display
    if columns_subset is not None:
        col_names = _get_column_names(data, ibis_tbl=ibis_tbl, df_lib_name_gt=df_lib_name_gt)

        resolved_columns = _validate_columns_subset(
            columns_subset=columns_subset, col_names=col_names
        )

        if len(resolved_columns) == 0:
            raise ValueError(
                "The `columns_subset=` value doesn't resolve to any columns in the table."
            )

        # Add back the row number column if it was removed
        if has_leading_row_num_col:
            resolved_columns = ["_row_num_"] + resolved_columns

        # Select the columns to display in the table with the `resolved_columns` value
        data = _select_columns(
            data, resolved_columns=resolved_columns, ibis_tbl=ibis_tbl, tbl_type=tbl_type
        )

    # From an Ibis table:
    # - get the row count
    # - subset the table to get the first and last n rows (if small, don't filter the table)
    # - get the row numbers for the table
    # - convert the table to a Polars or Pandas DF
    if ibis_tbl:
        import ibis

        # Get the Schema of the table
        tbl_schema = Schema(tbl=data)

        # Get the row count for the table
        ibis_rows = data.count()
        n_rows = ibis_rows.to_polars() if df_lib_name_gt == "polars" else int(ibis_rows.to_pandas())

        # If n_head + n_tail is greater than the row count, display the entire table
        if n_head + n_tail > n_rows:
            full_dataset = True
            data_subset = data

            if row_number_list is None:
                row_number_list = range(1, n_rows + 1)
        else:
            # Get the first n and last n rows of the table
            data_head = data.head(n_head)
            data_tail = data.filter(
                [ibis.row_number() >= (n_rows - n_tail), ibis.row_number() <= n_rows]
            )
            data_subset = data_head.union(data_tail)

            row_numbers_head = range(1, n_head + 1)
            row_numbers_tail = range(n_rows - n_tail + 1, n_rows + 1)
            if row_number_list is None:
                row_number_list = list(row_numbers_head) + list(row_numbers_tail)

        # Convert either to Polars or Pandas depending on the available library
        if df_lib_name_gt == "polars":
            data = data_subset.to_polars()
        else:
            data = data_subset.to_pandas()

    # From a DataFrame:
    # - get the row count
    # - subset the table to get the first and last n rows (if small, don't filter the table)
    # - get the row numbers for the table
    if pl_pb_tbl:
        # Get the Schema of the table
        tbl_schema = Schema(tbl=data)

        if tbl_type == "polars":
            n_rows = int(data.height)

            # If n_head + n_tail is greater than the row count, display the entire table
            if n_head + n_tail >= n_rows:
                full_dataset = True

                if row_number_list is None:
                    row_number_list = range(1, n_rows + 1)

            else:
                data = pl.concat([data.head(n=n_head), data.tail(n=n_tail)])

                if row_number_list is None:
                    row_number_list = list(range(1, n_head + 1)) + list(
                        range(n_rows - n_tail + 1, n_rows + 1)
                    )

        if tbl_type == "pandas":
            n_rows = data.shape[0]

            # If n_head + n_tail is greater than the row count, display the entire table
            if n_head + n_tail >= n_rows:
                full_dataset = True
                data_subset = data

                row_number_list = range(1, n_rows + 1)
            else:
                data = pd.concat([data.head(n=n_head), data.tail(n=n_tail)])

                row_number_list = list(range(1, n_head + 1)) + list(
                    range(n_rows - n_tail + 1, n_rows + 1)
                )

        if tbl_type == "pyspark":
            n_rows = data.count()

            # If n_head + n_tail is greater than the row count, display the entire table
            if n_head + n_tail >= n_rows:
                full_dataset = True
                # Convert to pandas for Great Tables compatibility
                data = data.toPandas()

                row_number_list = range(1, n_rows + 1)
            else:
                # Get head and tail samples, then convert to pandas
                head_data = data.limit(n_head).toPandas()

                # PySpark tail() returns a list of Row objects, need to convert to DataFrame
                tail_rows = data.tail(n_tail)
                if tail_rows:
                    # Convert list of Row objects back to DataFrame, then to pandas
                    tail_df = data.sparkSession.createDataFrame(tail_rows, data.schema)
                    tail_data = tail_df.toPandas()
                else:
                    # If no tail data, create empty DataFrame with same schema
                    import pandas as pd

                    tail_data = pd.DataFrame(columns=head_data.columns)

                # Suppress the FutureWarning about DataFrame concatenation with empty entries
                import warnings

                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        category=FutureWarning,
                        message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated",
                    )
                    data = pd.concat([head_data, tail_data])

                row_number_list = list(range(1, n_head + 1)) + list(
                    range(n_rows - n_tail + 1, n_rows + 1)
                )

        # For PySpark, update schema after conversion to Pandas
        if tbl_type == "pyspark":
            tbl_schema = Schema(tbl=data)

    # From the table schema, get a list of tuples containing column names and data types
    col_dtype_dict = tbl_schema.columns

    # Extract the column names from the list of tuples (first element of each tuple)
    col_names = [col[0] for col in col_dtype_dict]

    # Iterate over the list of tuples and create a new dictionary with the
    # column names and data types
    col_dtype_dict = {k: v for k, v in col_dtype_dict}

    # Create short versions of the data types by omitting any text in parentheses
    col_dtype_dict_short = {
        k: v.split("(")[0] if "(" in v else v for k, v in col_dtype_dict.items()
    }

    # Create a dictionary of column and row positions where the value is None/NA/Null
    # This is used to highlight these values in the table
    if df_lib_name_gt == "polars":
        none_values = {k: data[k].is_null().to_list() for k in col_names}
    else:
        # PySpark data has been converted to Pandas by this point so the 'isnull()'
        # method can be used
        none_values = {k: data[k].isnull() for k in col_names}

    none_values = [(k, i) for k, v in none_values.items() for i, val in enumerate(v) if val]

    # Import Great Tables to get preliminary renders of the columns
    import great_tables as gt

    # For each of the columns get the average number of characters printed for each of the values
    max_length_col_vals = []

    for column in col_dtype_dict.keys():
        # Select a single column of values
        if df_lib_name_gt == "pandas":
            data_col = data[[column]]
        elif df_lib_name_gt == "pyspark":
            # PySpark data should have been converted to pandas by now
            data_col = data[[column]]
        else:
            data_col = data.select([column])

        # Using Great Tables, render the columns and get the list of values as formatted strings
        built_gt = GT(data=data_col).fmt_markdown(columns=column)._build_data(context="html")
        column_values = gt.gt._get_column_of_values(built_gt, column_name=column, context="html")

        # Get the maximum number of characters in the column
        if column_values:  # Check if column_values is not empty
            max_length_col_vals.append(max([len(str(val)) for val in column_values]))
        else:
            max_length_col_vals.append(0)  # Use 0 for empty columns

    length_col_names = [len(column) for column in col_dtype_dict.keys()]
    length_data_types = [len(dtype) for dtype in col_dtype_dict_short.values()]

    # Comparing the length of the column names, the data types, and the max length of the
    # column values, prefer the largest of these for the column widths (by column);
    # the `7.8` factor is an approximation of the average width of a character in the
    # monospace font chosen for the table
    col_widths = [
        round(
            min(
                max(
                    7.8 * max_length_col_vals[i] + 10,  # 1. largest column value
                    7.8 * length_col_names[i] + 10,  # 2. characters in column name
                    7.8 * length_data_types[i] + 10,  # 3. characters in data type
                ),
                max_col_width,
            )
        )
        for i in range(len(col_dtype_dict.keys()))
    ]

    sum_col_widths = sum(col_widths)

    # In situations where the sum of the column widths is less than the minimum width,
    # divide up the remaining space between the columns
    if sum_col_widths < min_tbl_width:
        remaining_width = min_tbl_width - sum_col_widths
        n_remaining_cols = len(col_widths)
        col_widths = [width + remaining_width // n_remaining_cols for width in col_widths]

    # Add the `px` suffix to each of the column widths, stringifying them
    col_widths = [f"{width}px" for width in col_widths]

    # Create a dictionary of column names and their corresponding widths
    col_width_dict = {k: v for k, v in zip(col_names, col_widths)}

    # For each of the values in the dictionary, prepend the column name to the data type
    col_dtype_labels_dict = {
        k: html(
            f"<div><div style='white-space: nowrap; text-overflow: ellipsis; overflow: hidden; "
            f"padding-bottom: 2px; margin-bottom: 2px;'>{k}</div><div style='white-space: nowrap; "
            f"text-overflow: ellipsis; overflow: hidden; padding-top: 2px; margin-top: 2px;'>"
            f"<em>{v}</em></div></div>"
        )
        for k, v in col_dtype_dict_short.items()
    }

    if has_leading_row_num_col:
        # Remove the first entry col_width_dict and col_dtype_labels_dict dictionaries
        col_width_dict.pop("_row_num_")
        col_dtype_labels_dict.pop("_row_num_")

    # Prepend a column that contains the row numbers if `show_row_numbers=True`
    if show_row_numbers or has_leading_row_num_col:
        if has_leading_row_num_col:
            row_number_list = data["_row_num_"].to_list()

        else:
            if df_lib_name_gt == "polars":
                import polars as pl

                row_number_series = pl.Series("_row_num_", row_number_list)
                data = data.insert_column(0, row_number_series)

            if df_lib_name_gt == "pandas":
                data.insert(0, "_row_num_", row_number_list)

            if df_lib_name_gt == "pyspark":
                # For PySpark converted to pandas, use pandas method
                data.insert(0, "_row_num_", row_number_list)

        # Get the highest number in the `row_number_list` and calculate a width that will
        # safely fit a number of that magnitude
        if row_number_list:  # Check if list is not empty
            max_row_num = max(row_number_list)
            max_row_num_width = len(str(max_row_num)) * 7.8 + 10
        else:
            # If row_number_list is empty, use a default width
            max_row_num_width = 7.8 * 2 + 10  # Width for 2-digit numbers

        # Update the col_width_dict to include the row number column
        col_width_dict = {"_row_num_": f"{max_row_num_width}px"} | col_width_dict

        # Update the `col_dtype_labels_dict` to include the row number column (use empty string)
        col_dtype_labels_dict = {"_row_num_": ""} | col_dtype_labels_dict

    # Create the label, table type, and thresholds HTML fragments
    table_type_html = _create_table_type_html(tbl_type=tbl_type, tbl_name=None, font_size="10px")

    tbl_dims_html = _create_table_dims_html(columns=n_columns, rows=n_rows, font_size="10px")

    # Compose the subtitle HTML fragment
    combined_subtitle = (
        "<div>"
        '<div style="padding-top: 0; padding-bottom: 7px;">'
        f"{table_type_html}"
        f"{tbl_dims_html}"
        "</div>"
        "</div>"
    )

    gt_tbl = (
        GT(data=data, id="pb_preview_tbl")
        .opt_table_font(font=google_font(name="IBM Plex Sans"))
        .opt_align_table_header(align="left")
        .fmt_markdown(columns=col_names)
        .tab_style(
            style=style.css(
                "height: 14px; padding: 4px; white-space: nowrap; text-overflow: "
                "ellipsis; overflow: hidden;"
            ),
            locations=loc.body(),
        )
        .tab_style(
            style=style.text(color="black", font=google_font(name="IBM Plex Mono"), size="12px"),
            locations=loc.body(),
        )
        .tab_style(
            style=style.text(color="gray20", font=google_font(name="IBM Plex Mono"), size="12px"),
            locations=loc.column_labels(),
        )
        .tab_style(
            style=style.borders(
                sides=["top", "bottom"], color="#E9E9E", style="solid", weight="1px"
            ),
            locations=loc.body(),
        )
        .tab_options(
            table_body_vlines_style="solid",
            table_body_vlines_width="1px",
            table_body_vlines_color="#E9E9E9",
            column_labels_vlines_style="solid",
            column_labels_vlines_width="1px",
            column_labels_vlines_color="#F2F2F2",
        )
        .cols_label(cases=col_dtype_labels_dict)
        .cols_width(cases=col_width_dict)
    )

    if incl_header:
        gt_tbl = gt_tbl.tab_header(title=html(combined_subtitle))
        gt_tbl = gt_tbl.tab_options(heading_subtitle_font_size="12px")

    if none_values and mark_missing_values:
        for column, none_index in none_values:
            gt_tbl = gt_tbl.tab_style(
                style=[style.text(color="#B22222"), style.fill(color="#FFC1C159")],
                locations=loc.body(rows=none_index, columns=column),
            )

        if tbl_type == "pandas":
            gt_tbl = gt_tbl.sub_missing(missing_text="NA")

        if ibis_tbl:
            gt_tbl = gt_tbl.sub_missing(missing_text="NULL")

    if not full_dataset:
        gt_tbl = gt_tbl.tab_style(
            style=style.borders(sides="bottom", color="#6699CC80", style="solid", weight="2px"),
            locations=loc.body(rows=n_head - 1),
        )

    if show_row_numbers:
        gt_tbl = gt_tbl.tab_style(
            style=[
                style.text(color="gray", font=google_font(name="IBM Plex Mono"), size="10px"),
                style.borders(sides="right", color="#6699CC80", style="solid", weight="2px"),
            ],
            locations=loc.body(columns="_row_num_"),
        )

    # If the version of `great_tables` is `>=0.17.0` then disable Quarto table processing
    if version("great_tables") >= "0.17.0":
        gt_tbl = gt_tbl.tab_options(quarto_disable_processing=True)

    return gt_tbl


def missing_vals_tbl(data: FrameT | Any) -> GT:
    """
    Display a table that shows the missing values in the input table.

    The `missing_vals_tbl()` function generates a table that shows the missing values in the input
    table. The table is displayed using the Great Tables API, which allows for further customization
    of the table's appearance if so desired.

    Parameters
    ----------
    data
        The table for which to display the missing values. This could be a DataFrame object, an
        Ibis table object, a CSV file path, a Parquet file path, or a database connection string.
        Read the *Supported Input Table Types* section for details on the supported table types.

    Returns
    -------
    GT
        A GT object that displays the table of missing values in the input table.

    Supported Input Table Types
    ---------------------------
    The `data=` parameter can be given any of the following table types:

    - Polars DataFrame (`"polars"`)
    - Pandas DataFrame (`"pandas"`)
    - PySpark table (`"pyspark"`)
    - DuckDB table (`"duckdb"`)*
    - MySQL table (`"mysql"`)*
    - PostgreSQL table (`"postgresql"`)*
    - SQLite table (`"sqlite"`)*
    - Microsoft SQL Server table (`"mssql"`)*
    - Snowflake table (`"snowflake"`)*
    - Databricks table (`"databricks"`)*
    - BigQuery table (`"bigquery"`)*
    - Parquet table (`"parquet"`)*
    - CSV files (string path or `pathlib.Path` object with `.csv` extension)
    - Parquet files (string path, `pathlib.Path` object, glob pattern, directory with `.parquet`
    extension, or partitioned dataset)
    - Database connection strings (URI format with optional table specification)

    The table types marked with an asterisk need to be prepared as Ibis tables (with type of
    `ibis.expr.types.relations.Table`). Furthermore, using `missing_vals_tbl()` with these types of
    tables requires the Ibis library (`v9.5.0` or above) to be installed. If the input table is a
    Polars or Pandas DataFrame, the availability of Ibis is not needed.

    The Missing Values Table
    ------------------------
    The missing values table shows the proportion of missing values in each column of the input
    table. The table is divided into sectors, with each sector representing a range of rows in the
    table. The proportion of missing values in each sector is calculated for each column. The table
    is displayed using the Great Tables API, which allows for further customization of the table's
    appearance.

    To ensure that the table can scale to tables with many columns, each row in the reporting table
    represents a column in the input table. There are 10 sectors shown in the table, where the first
    sector represents the first 10% of the rows, the second sector represents the next 10% of the
    rows, and so on. Any sectors that are light blue indicate that there are no missing values in
    that sector. If there are missing values, the proportion of missing values is shown by a gray
    color (light gray for low proportions, dark gray to black for very high proportions).

    Examples
    --------
    The `missing_vals_tbl()` function is useful for quickly identifying columns with missing values
    in a table. Here's an example using the `nycflights` dataset (loaded as a Polars DataFrame using
    the [`load_dataset()`](`pointblank.load_dataset`) function):

    ```{python}
    import pointblank as pb

    nycflights = pb.load_dataset("nycflights", tbl_type="polars")

    pb.missing_vals_tbl(nycflights)
    ```

    The table shows the proportion of missing values in each column of the `nycflights` dataset. The
    table is divided into sectors, with each sector representing a range of rows in the table (with
    around 34,000 rows per sector). The proportion of missing values in each sector is calculated
    for each column. The various shades of gray indicate the proportion of missing values in each
    sector. Many columns have no missing values at all, and those sectors are colored light blue.
    """

    # Process input data to handle different data source types
    data = _process_data(data)

    # Make a copy of the data to avoid modifying the original
    # Note: PySpark DataFrames cannot be deep copied due to SparkContext serialization issues
    tbl_type = _get_tbl_type(data=data)
    if "pyspark" not in tbl_type:
        data = copy.deepcopy(data)

    # Get the number of rows in the table
    n_rows = get_row_count(data)

    # Define the number of cut points for the missing values table
    n_cut_points = 9

    # Get the cut points for the table preview
    cut_points = _get_cut_points(n_rows=n_rows, n_cuts=n_cut_points)

    # Get the row ranges for the table
    row_ranges = _get_row_ranges(cut_points=cut_points, n_rows=n_rows)

    # Determine if the table is a DataFrame or an Ibis table
    tbl_type = _get_tbl_type(data=data)
    ibis_tbl = "ibis.expr.types.relations.Table" in str(type(data))
    pl_pb_tbl = "polars" in tbl_type or "pandas" in tbl_type or "pyspark" in tbl_type

    # Select the DataFrame library to use for displaying the Ibis table
    df_lib_gt = _select_df_lib(preference="polars")
    df_lib_name_gt = df_lib_gt.__name__

    # If the table is a DataFrame (Pandas, Polars, or PySpark), set `df_lib_name_gt` to the name of the
    # library (e.g., "polars", "pandas", or "pyspark")
    if pl_pb_tbl:
        if "polars" in tbl_type:
            df_lib_name_gt = "polars"
        elif "pandas" in tbl_type:
            df_lib_name_gt = "pandas"
        elif "pyspark" in tbl_type:
            df_lib_name_gt = "pyspark"

        # Handle imports of Polars, Pandas, or PySpark here
        if df_lib_name_gt == "polars":
            import polars as pl
        elif df_lib_name_gt == "pandas":
            import pandas as pd
        # Note: PySpark import is handled as needed, typically already imported in user's environment

    # From an Ibis table:
    # - get the row count
    # - get 10 cut points for table preview, these are row numbers used as buckets for determining
    #   the proportion of missing values in each 'sector' in each column
    if ibis_tbl:
        # Get the column names from the table
        col_names = list(data.columns)

        # Use the `row_ranges` list of lists to query, for each column, the proportion of missing
        # values in each 'sector' of the table (a sector is a range of rows)
        def _calculate_missing_proportions(use_polars_conversion: bool = False):
            """
            Calculate missing value proportions for each column and sector.

            Parameters
            ----------
            use_polars_conversion
                If True, use `.to_polars()` for conversions, otherwise use `.to_pandas()`
            """
            missing_vals = {}
            for col in data.columns:
                col_missing_props = []

                # Calculate missing value proportions for each sector
                for i in range(len(cut_points)):
                    start_row = cut_points[i - 1] if i > 0 else 0
                    end_row = cut_points[i]
                    sector_size = end_row - start_row

                    if sector_size > 0:
                        sector_data = data[start_row:end_row][col]
                        null_sum = sector_data.isnull().sum()

                        # Apply the appropriate conversion method
                        if use_polars_conversion:
                            null_sum_converted = null_sum.to_polars()  # pragma: no cover
                        else:
                            null_sum_converted = null_sum.to_pandas()  # pragma: no cover

                        missing_prop = (null_sum_converted / sector_size) * 100
                        col_missing_props.append(missing_prop)
                    else:
                        col_missing_props.append(0)

                # Handle the final sector (after last cut point)
                if n_rows > cut_points[-1]:
                    start_row = cut_points[-1]
                    sector_size = n_rows - start_row

                    sector_data = data[start_row:n_rows][col]
                    null_sum = sector_data.isnull().sum()

                    # Apply the appropriate conversion method
                    if use_polars_conversion:
                        null_sum_converted = null_sum.to_polars()  # pragma: no cover
                    else:
                        null_sum_converted = null_sum.to_pandas()  # pragma: no cover

                    missing_prop = (null_sum_converted / sector_size) * 100
                    col_missing_props.append(missing_prop)
                else:
                    col_missing_props.append(0)  # pragma: no cover

                missing_vals[col] = col_missing_props

            return missing_vals

        # Use the helper function based on the DataFrame library
        if df_lib_name_gt == "polars":
            missing_vals = _calculate_missing_proportions(
                use_polars_conversion=True
            )  # pragma: no cover
        else:
            missing_vals = _calculate_missing_proportions(
                use_polars_conversion=False
            )  # pragma: no cover

        # Pivot the `missing_vals` dictionary to create a table with the missing value proportions
        missing_vals = {
            "columns": list(missing_vals.keys()),
            **{
                str(i + 1): [missing_vals[col][i] for col in missing_vals.keys()]
                for i in range(len(cut_points) + 1)
            },
        }

        # Get a dictionary of counts of missing values in each column
        if df_lib_name_gt == "polars":
            missing_val_counts = {
                col: data[col].isnull().sum().to_polars() for col in data.columns
            }  # pragma: no cover
        else:
            missing_val_counts = {
                col: data[col].isnull().sum().to_pandas() for col in data.columns
            }  # pragma: no cover

    if pl_pb_tbl:
        # Get the column names from the table
        col_names = list(data.columns)

        # Helper function for DataFrame missing value calculation (Polars/Pandas)
        def _calculate_missing_proportions_dataframe(is_polars=False):
            null_method = "is_null" if is_polars else "isnull"

            missing_vals = {
                col: [
                    (
                        getattr(
                            data[(cut_points[i - 1] if i > 0 else 0) : cut_points[i]][col],
                            null_method,
                        )().sum()
                        / (cut_points[i] - (cut_points[i - 1] if i > 0 else 0))
                        * 100
                        if cut_points[i] > (cut_points[i - 1] if i > 0 else 0)
                        else 0
                    )
                    for i in range(len(cut_points))
                ]
                + [
                    (
                        getattr(data[cut_points[-1] : n_rows][col], null_method)().sum()
                        / (n_rows - cut_points[-1])
                        * 100
                        if n_rows > cut_points[-1]
                        else 0
                    )
                ]
                for col in data.columns
            }

            # Transform to the expected format
            formatted_missing_vals = {
                "columns": list(missing_vals.keys()),
                **{
                    str(i + 1): [missing_vals[col][i] for col in missing_vals.keys()]
                    for i in range(len(cut_points) + 1)
                },
            }

            # Get a dictionary of counts of missing values in each column
            missing_val_counts = {
                col: getattr(data[col], null_method)().sum() for col in data.columns
            }

            return formatted_missing_vals, missing_val_counts

        # Iterate over the cut points and get the proportion of missing values in each 'sector'
        # for each column
        if "polars" in tbl_type:
            missing_vals, missing_val_counts = _calculate_missing_proportions_dataframe(
                is_polars=True
            )

        elif "pandas" in tbl_type:
            missing_vals, missing_val_counts = _calculate_missing_proportions_dataframe(
                is_polars=False
            )

        elif "pyspark" in tbl_type:
            from pyspark.sql.functions import col as pyspark_col

            # PySpark implementation for missing values calculation
            missing_vals = {}
            for col_name in data.columns:
                col_missing_props = []

                # Calculate missing value proportions for each sector
                for i in range(len(cut_points)):
                    start_row = cut_points[i - 1] if i > 0 else 0
                    end_row = cut_points[i]
                    sector_size = end_row - start_row

                    if sector_size > 0:
                        # Use row_number() to filter rows by range
                        from pyspark.sql.functions import row_number
                        from pyspark.sql.window import Window

                        window = Window.orderBy(
                            pyspark_col(data.columns[0])
                        )  # Order by first column
                        sector_data = data.withColumn("row_num", row_number().over(window)).filter(
                            (pyspark_col("row_num") > start_row)
                            & (pyspark_col("row_num") <= end_row)
                        )

                        # Count nulls in this sector
                        null_count = sector_data.filter(pyspark_col(col_name).isNull()).count()
                        missing_prop = (null_count / sector_size) * 100
                        col_missing_props.append(missing_prop)
                    else:
                        col_missing_props.append(0)  # pragma: no cover

                # Handle the final sector (after last cut point)
                if n_rows > cut_points[-1]:
                    start_row = cut_points[-1]
                    end_row = n_rows
                    sector_size = end_row - start_row

                    from pyspark.sql.functions import row_number
                    from pyspark.sql.window import Window

                    window = Window.orderBy(pyspark_col(data.columns[0]))
                    sector_data = data.withColumn("row_num", row_number().over(window)).filter(
                        pyspark_col("row_num") > start_row
                    )

                    null_count = sector_data.filter(pyspark_col(col_name).isNull()).count()
                    missing_prop = (null_count / sector_size) * 100
                    col_missing_props.append(missing_prop)
                else:
                    col_missing_props.append(0)  # pragma: no cover

                missing_vals[col_name] = col_missing_props

            # Pivot the `missing_vals` dictionary to create a table with the missing value proportions
            missing_vals = {
                "columns": list(missing_vals.keys()),
                **{
                    str(i + 1): [missing_vals[col][i] for col in missing_vals.keys()]
                    for i in range(len(cut_points) + 1)
                },
            }

            # Get a dictionary of counts of missing values in each column
            missing_val_counts = {}
            for col_name in data.columns:
                null_count = data.filter(pyspark_col(col_name).isNull()).count()
                missing_val_counts[col_name] = null_count

    # From `missing_vals`, create the DataFrame with the missing value proportions
    if df_lib_name_gt == "polars":
        import polars as pl

        # Create a Polars DataFrame from the `missing_vals` dictionary
        missing_vals_df = pl.DataFrame(missing_vals)

    else:
        import pandas as pd

        # Create a Pandas DataFrame from the `missing_vals` dictionary
        missing_vals_df = pd.DataFrame(missing_vals)

    # Get a count of total missing values
    n_missing_total = int(sum(missing_val_counts.values()))

    # Format `n_missing_total` for HTML display
    n_missing_total_fmt = _format_to_integer_value(n_missing_total)

    # Create the label, table type, and thresholds HTML fragments
    table_type_html = _create_table_type_html(tbl_type=tbl_type, tbl_name=None, font_size="10px")

    tbl_dims_html = _create_table_dims_html(columns=len(col_names), rows=n_rows, font_size="10px")

    check_mark = '<span style="color:#4CA64C;">&check;</span>'

    # Compose the title HTML fragment
    if n_missing_total == 0:
        combined_title = f"Missing Values {check_mark}"
    else:
        combined_title = (
            "Missing Values&nbsp;&nbsp;&nbsp;<span style='font-size: 14px; "
            f"text-transform: uppercase; color: #333333'>{n_missing_total_fmt} in total</span>"
        )

    # Compose the subtitle HTML fragment
    combined_subtitle = (
        "<div>"
        '<div style="padding-top: 0; padding-bottom: 7px;">'
        f"{table_type_html}"
        f"{tbl_dims_html}"
        "</div>"
        "</div>"
    )

    # Get the row ranges for the table
    row_ranges = _get_row_ranges(cut_points=cut_points, n_rows=n_rows)

    row_ranges_html = (
        "<div style='font-size: 8px;'><ol style='margin-top: 2px; margin-left: -15px;'>"
        + "".join(
            [f"<li>{row_range[0]} &ndash; {row_range[1]}</li>" for row_range in zip(*row_ranges)]
        )
        + "</ol></div>"
    )

    details_html = (
        "<details style='cursor: pointer; font-size: 12px;'><summary style='font-size: 10px; color: #333333;'>ROW SECTORS</summary>"
        f"{row_ranges_html}"
        "</details>"
    )

    # Compose the footer HTML fragment
    combined_footer = (
        "<div style='display: flex; align-items: center; padding-bottom: 10px;'><div style='width: 20px; height: 20px; "
        "background-color: lightblue; border: 1px solid #E0E0E0; margin-right: 3px;'></div>"
        "<span style='font-size: 10px;'>NO MISSING VALUES</span><span style='font-size: 10px;'>"
        "&nbsp;&nbsp;&nbsp;&nbsp; PROPORTION MISSING:&nbsp;&nbsp;</span>"
        "<div style='font-size: 10px; color: #333333;'>0%</div><div style='width: 80px; "
        "height: 20px; background: linear-gradient(to right, #F5F5F5, #000000); "
        "border: 1px solid #E0E0E0; margin-right: 2px; margin-left: 2px'></div>"
        "<div style='font-size: 10px; color: #333333;'>100%</div></div>"
        f"{details_html}"
    )

    sector_list = [str(i) for i in range(1, n_cut_points + 2)]

    missing_vals_tbl = (
        GT(missing_vals_df)
        .tab_header(title=html(combined_title), subtitle=html(combined_subtitle))
        .opt_table_font(font=google_font(name="IBM Plex Sans"))
        .opt_align_table_header(align="left")
        .cols_label(columns="Column")
        .cols_width(
            cases={
                "columns": "200px",
                "1": "30px",
                "2": "30px",
                "3": "30px",
                "4": "30px",
                "5": "30px",
                "6": "30px",
                "7": "30px",
                "8": "30px",
                "9": "30px",
                "10": "30px",
            }
        )
        .tab_spanner(label="Row Sector", columns=sector_list)
        .cols_align(align="center", columns=sector_list)
        .data_color(
            columns=sector_list,
            palette=["#F5F5F5", "#000000"],
            domain=[0, 1],
        )
        .tab_style(
            style=style.borders(
                sides=["left", "right"], color="#F0F0F0", style="solid", weight="1px"
            ),
            locations=loc.body(columns=sector_list),
        )
        .tab_style(
            style=style.css(
                "height: 20px; padding: 4px; white-space: nowrap; text-overflow: "
                "ellipsis; overflow: hidden;"
            ),
            locations=loc.body(),
        )
        .tab_style(
            style=style.text(color="black", font=google_font(name="IBM Plex Mono"), size="12px"),
            locations=loc.body(),
        )
        .tab_style(
            style=style.text(color="black", size="16px"),
            locations=loc.column_labels(),
        )
        .fmt(fns=lambda x: "", columns=sector_list)
        .tab_source_note(source_note=html(combined_footer))
    )

    #
    # Highlight sectors of the table where there are no missing values
    #

    if df_lib_name_gt == "polars":
        import polars.selectors as cs

        missing_vals_tbl = missing_vals_tbl.tab_style(
            style=style.fill(color="lightblue"), locations=loc.body(mask=cs.numeric().eq(0))
        )

    if df_lib_name_gt == "pandas":
        # For every column in the DataFrame, determine the indices of the rows where the value is 0
        # and use tab_style to fill the cell with a light blue color
        for col in missing_vals_df.columns:
            row_indices = list(missing_vals_df[missing_vals_df[col] == 0].index)

            missing_vals_tbl = missing_vals_tbl.tab_style(
                style=style.fill(color="lightblue"),
                locations=loc.body(columns=col, rows=row_indices),
            )

    # If the version of `great_tables` is `>=0.17.0` then disable Quarto table processing
    if version("great_tables") >= "0.17.0":
        missing_vals_tbl = missing_vals_tbl.tab_options(quarto_disable_processing=True)

    return missing_vals_tbl


def _get_cut_points(n_rows: int, n_cuts: int) -> list[int]:
    """
    Get the cut points for a table.

    For a given number of rows and cuts, get the cut points for the table. The cut points are
    evenly spaced in the range from 1 to n_rows, excluding the first and last points.

    Parameters
    ----------
    n_rows
        The total number of rows in the table.
    n_cuts
        The number of cuts to divide the table into.

    Returns
    -------
    list[int]
        A list of integer values that represent the cut points for the table.
    """

    # Calculate the step size
    step_size = n_rows // (n_cuts + 1)

    # Get the cut points
    cut_points = [step_size * i for i in range(1, n_cuts + 1)]

    return cut_points


def _get_row_ranges(cut_points: list[int], n_rows: int) -> list[list[int]]:
    """
    Get the row ranges for a missing values table.

    For a list of cut points, get the row ranges for a missing values table. The row ranges are
    formatted as lists of integers like [1, 10], [11, 20], etc.

    Parameters
    ----------
    cut_points
        A list of integer values that represent the cut points for the table.

    Returns
    -------
    list[list[int]]
        A list of lists that represent the row ranges for the table.
    """
    row_ranges = []

    for i in range(len(cut_points)):
        if i == 0:
            row_ranges.append([1, cut_points[i]])
        else:
            row_ranges.append([cut_points[i - 1] + 1, cut_points[i]])

    # Add the final range to incorporate n_rows
    if cut_points[-1] < n_rows:
        row_ranges.append([cut_points[-1] + 1, n_rows])

    # Split the row ranges into two lists: LHS and RHS
    lhs_values = [pair[0] for pair in row_ranges]
    rhs_values = [pair[1] for pair in row_ranges]

    return [lhs_values, rhs_values]


def _get_column_names_safe(data: Any) -> list[str]:
    """
    Safely get column names from a DataFrame, optimized for LazyFrames.
    This function avoids the Narwhals PerformanceWarning for LazyFrames.
    """
    try:
        import narwhals as nw

        df_nw = nw.from_native(data)
        # Use `collect_schema()` for LazyFrames to avoid performance warnings
        if hasattr(df_nw, "collect_schema"):
            return list(df_nw.collect_schema().keys())
        else:
            return list(df_nw.columns)  # pragma: no cover
    except Exception:  # pragma: no cover
        # Fallback to direct column access
        return list(data.columns)  # pragma: no cover


def _get_column_names(data: FrameT | Any, ibis_tbl: bool, df_lib_name_gt: str) -> list[str]:
    if ibis_tbl:
        return data.columns if df_lib_name_gt == "polars" else list(data.columns)

    # Use the optimized helper function
    return _get_column_names_safe(data)


def _validate_columns_subset(
    columns_subset: str | list[str] | Column, col_names: list[str]
) -> list[str]:
    if isinstance(columns_subset, str):
        if columns_subset not in col_names:
            raise ValueError("The `columns_subset=` value doesn't match any columns in the table.")
        return [columns_subset]

    if isinstance(columns_subset, list):
        if all(isinstance(col, str) for col in columns_subset):
            if not all(col in col_names for col in columns_subset):
                raise ValueError(
                    "Not all columns provided as `columns_subset=` match the table's columns."
                )
            return columns_subset

    return columns_subset.resolve(columns=col_names)


def _select_columns(
    data: FrameT | Any, resolved_columns: list[str], ibis_tbl: bool, tbl_type: str
) -> FrameT | Any:
    if ibis_tbl:
        return data[resolved_columns]
    if tbl_type == "polars":
        return data.select(resolved_columns)
    return data[resolved_columns]


def get_column_count(data: FrameT | Any) -> int:
    """
    Get the number of columns in a table.

    The `get_column_count()` function returns the number of columns in a table. The function works
    with any table that is supported by the `pointblank` library, including Pandas, Polars, and Ibis
    backend tables (e.g., DuckDB, MySQL, PostgreSQL, SQLite, Parquet, etc.). It also supports
    direct input of CSV files, Parquet files, and database connection strings.

    Parameters
    ----------
    data
        The table for which to get the column count, which could be a DataFrame object, an Ibis
        table object, a CSV file path, a Parquet file path, or a database connection string.
        Read the *Supported Input Table Types* section for details on the supported table types.

    Returns
    -------
    int
        The number of columns in the table.

    Supported Input Table Types
    ---------------------------
    The `data=` parameter can be given any of the following table types:

    - Polars DataFrame (`"polars"`)
    - Pandas DataFrame (`"pandas"`)
    - PySpark table (`"pyspark"`)
    - DuckDB table (`"duckdb"`)*
    - MySQL table (`"mysql"`)*
    - PostgreSQL table (`"postgresql"`)*
    - SQLite table (`"sqlite"`)*
    - Microsoft SQL Server table (`"mssql"`)*
    - Snowflake table (`"snowflake"`)*
    - Databricks table (`"databricks"`)*
    - BigQuery table (`"bigquery"`)*
    - Parquet table (`"parquet"`)*
    - CSV files (string path or `pathlib.Path` object with `.csv` extension)
    - Parquet files (string path, `pathlib.Path` object, glob pattern, directory with `.parquet`
    extension, or partitioned dataset)
    - Database connection strings (URI format with optional table specification)

    The table types marked with an asterisk need to be prepared as Ibis tables (with type of
    `ibis.expr.types.relations.Table`). Furthermore, using `get_column_count()` with these types of
    tables requires the Ibis library (`v9.5.0` or above) to be installed. If the input table is a
    Polars or Pandas DataFrame, the availability of Ibis is not needed.

    To use a CSV file, ensure that a string or `pathlib.Path` object with a `.csv` extension is
    provided. The file will be automatically detected and loaded using the best available DataFrame
    library. The loading preference is Polars first, then Pandas as a fallback.

    GitHub URLs pointing to CSV or Parquet files are automatically detected and converted to raw
    content URLs for downloading. The URL format should be:
    `https://github.com/user/repo/blob/branch/path/file.csv` or
    `https://github.com/user/repo/blob/branch/path/file.parquet`

    Connection strings follow database URL formats and must also specify a table using the
    `::table_name` suffix. Examples include:

    ```
    "duckdb:///path/to/database.ddb::table_name"
    "sqlite:///path/to/database.db::table_name"
    "postgresql://user:password@localhost:5432/database::table_name"
    "mysql://user:password@localhost:3306/database::table_name"
    "bigquery://project/dataset::table_name"
    "snowflake://user:password@account/database/schema::table_name"
    ```

    When using connection strings, the Ibis library with the appropriate backend driver is required.

    Examples
    --------
    To get the number of columns in a table, we can use the `get_column_count()` function. Here's an
    example using the `small_table` dataset (itself loaded using the
    [`load_dataset()`](`pointblank.load_dataset`) function):

    ```{python}
    import pointblank as pb

    small_table_polars = pb.load_dataset("small_table")

    pb.get_column_count(small_table_polars)
    ```

    This table is a Polars DataFrame, but the `get_column_count()` function works with any table
    supported by `pointblank`, including Pandas DataFrames and Ibis backend tables. Here's an
    example using a DuckDB table handled by Ibis:

    ```{python}
    small_table_duckdb = pb.load_dataset("small_table", tbl_type="duckdb")

    pb.get_column_count(small_table_duckdb)
    ```

    #### Working with CSV Files

    The `get_column_count()` function can directly accept CSV file paths:

    ```{python}
    # Get a path to a CSV file from the package data
    csv_path = pb.get_data_path("global_sales", "csv")

    pb.get_column_count(csv_path)
    ```

    #### Working with Parquet Files

    The function supports various Parquet input formats:

    ```{python}
    # Single Parquet file from package data
    parquet_path = pb.get_data_path("nycflights", "parquet")

    pb.get_column_count(parquet_path)
    ```

    You can also use glob patterns and directories:

    ```python
    # Multiple Parquet files with glob patterns
    pb.get_column_count("data/sales_*.parquet")

    # Directory containing Parquet files
    pb.get_column_count("parquet_data/")

    # Partitioned Parquet dataset
    pb.get_column_count("sales_data/")  # Auto-discovers partition columns
    ```

    #### Working with Database Connection Strings

    The function supports database connection strings for direct access to database tables:

    ```{python}
    # Get path to a DuckDB database file from package data
    duckdb_path = pb.get_data_path("game_revenue", "duckdb")

    pb.get_column_count(f"duckdb:///{duckdb_path}::game_revenue")
    ```

    The function always returns the number of columns in the table as an integer value, which is
    `8` for the `small_table` dataset.
    """
    from pathlib import Path

    # Process different input types
    if isinstance(data, str) or isinstance(data, Path):
        data = _process_data(data)
    elif isinstance(data, list):
        # Handle list of file paths (likely Parquet files)
        data = _process_parquet_input(data)

    # Use Narwhals to handle all DataFrame types (including Ibis) uniformly
    try:
        import narwhals as nw

        df_nw = nw.from_native(data)
        # Use `collect_schema()` for LazyFrames to avoid performance warnings
        if hasattr(df_nw, "collect_schema"):
            return len(df_nw.collect_schema())
        else:
            return len(df_nw.columns)  # pragma: no cover
    except Exception:
        # Fallback for unsupported types
        if "pandas" in str(type(data)):
            return data.shape[1]  # pragma: no cover
        else:
            raise ValueError("The input table type supplied in `data=` is not supported.")


def _extract_enum_values(set_values: Any) -> list[Any]:
    """
    Extract values from Enum classes or collections containing Enum instances.

    This helper function handles:
    1. Enum classes: extracts all enum values
    2. Collections containing Enum instances: extracts their values
    3. Regular collections: returns as-is

    Parameters
    ----------
    set_values
        The input collection that may contain Enum class or Enum instances.

    Returns
    -------
    list[Any]
        A list of extracted values
    """
    from collections.abc import Collection

    # Check if set_values is an Enum class (not an instance)
    if inspect.isclass(set_values) and issubclass(set_values, Enum):
        # Extract all values from the Enum class
        return [enum_member.value for enum_member in set_values]

    # Check if set_values is a collection
    if isinstance(set_values, Collection) and not isinstance(set_values, (str, bytes)):
        extracted_values = []
        for item in set_values:
            if isinstance(item, Enum):
                # If item is an Enum instance, extract its value
                extracted_values.append(item.value)
            else:
                # If item is not an Enum instance, keep as-is
                extracted_values.append(item)
        return extracted_values

    # If set_values is neither an Enum class nor a collection, return as list
    return [set_values]


def get_row_count(data: FrameT | Any) -> int:
    """
    Get the number of rows in a table.

    The `get_row_count()` function returns the number of rows in a table. The function works with
    any table that is supported by the `pointblank` library, including Pandas, Polars, and Ibis
    backend tables (e.g., DuckDB, MySQL, PostgreSQL, SQLite, Parquet, etc.). It also supports
    direct input of CSV files, Parquet files, and database connection strings.

    Parameters
    ----------
    data
        The table for which to get the row count, which could be a DataFrame object, an Ibis table
        object, a CSV file path, a Parquet file path, or a database connection string.
        Read the *Supported Input Table Types* section for details on the supported table types.

    Returns
    -------
    int
        The number of rows in the table.

    Supported Input Table Types
    ---------------------------
    The `data=` parameter can be given any of the following table types:

    - Polars DataFrame (`"polars"`)
    - Pandas DataFrame (`"pandas"`)
    - PySpark table (`"pyspark"`)
    - DuckDB table (`"duckdb"`)*
    - MySQL table (`"mysql"`)*
    - PostgreSQL table (`"postgresql"`)*
    - SQLite table (`"sqlite"`)*
    - Microsoft SQL Server table (`"mssql"`)*
    - Snowflake table (`"snowflake"`)*
    - Databricks table (`"databricks"`)*
    - BigQuery table (`"bigquery"`)*
    - Parquet table (`"parquet"`)*
    - CSV files (string path or `pathlib.Path` object with `.csv` extension)
    - Parquet files (string path, `pathlib.Path` object, glob pattern, directory with `.parquet`
    extension, or partitioned dataset)
    - GitHub URLs (direct links to CSV or Parquet files on GitHub)
    - Database connection strings (URI format with optional table specification)

    The table types marked with an asterisk need to be prepared as Ibis tables (with type of
    `ibis.expr.types.relations.Table`). Furthermore, using `get_row_count()` with these types of
    tables requires the Ibis library (`v9.5.0` or above) to be installed. If the input table is a
    Polars or Pandas DataFrame, the availability of Ibis is not needed.

    To use a CSV file, ensure that a string or `pathlib.Path` object with a `.csv` extension is
    provided. The file will be automatically detected and loaded using the best available DataFrame
    library. The loading preference is Polars first, then Pandas as a fallback.

    GitHub URLs pointing to CSV or Parquet files are automatically detected and converted to raw
    content URLs for downloading. The URL format should be:
    `https://github.com/user/repo/blob/branch/path/file.csv` or
    `https://github.com/user/repo/blob/branch/path/file.parquet`

    Connection strings follow database URL formats and must also specify a table using the
    `::table_name` suffix. Examples include:

    ```
    "duckdb:///path/to/database.ddb::table_name"
    "sqlite:///path/to/database.db::table_name"
    "postgresql://user:password@localhost:5432/database::table_name"
    "mysql://user:password@localhost:3306/database::table_name"
    "bigquery://project/dataset::table_name"
    "snowflake://user:password@account/database/schema::table_name"
    ```

    When using connection strings, the Ibis library with the appropriate backend driver is required.

    Examples
    --------
    Getting the number of rows in a table is easily done by using the `get_row_count()` function.
    Here's an example using the `game_revenue` dataset (itself loaded using the
    [`load_dataset()`](`pointblank.load_dataset`) function):

    ```{python}
    import pointblank as pb

    game_revenue_polars = pb.load_dataset("game_revenue")

    pb.get_row_count(game_revenue_polars)
    ```

    This table is a Polars DataFrame, but the `get_row_count()` function works with any table
    supported by `pointblank`, including Pandas DataFrames and Ibis backend tables. Here's an
    example using a DuckDB table handled by Ibis:

    ```{python}
    game_revenue_duckdb = pb.load_dataset("game_revenue", tbl_type="duckdb")

    pb.get_row_count(game_revenue_duckdb)
    ```

    #### Working with CSV Files

    The `get_row_count()` function can directly accept CSV file paths:

    ```{python}
    # Get a path to a CSV file from the package data
    csv_path = pb.get_data_path("global_sales", "csv")

    pb.get_row_count(csv_path)
    ```

    #### Working with Parquet Files

    The function supports various Parquet input formats:

    ```{python}
    # Single Parquet file from package data
    parquet_path = pb.get_data_path("nycflights", "parquet")

    pb.get_row_count(parquet_path)
    ```

    You can also use glob patterns and directories:

    ```python
    # Multiple Parquet files with glob patterns
    pb.get_row_count("data/sales_*.parquet")

    # Directory containing Parquet files
    pb.get_row_count("parquet_data/")

    # Partitioned Parquet dataset
    pb.get_row_count("sales_data/")  # Auto-discovers partition columns
    ```

    #### Working with Database Connection Strings

    The function supports database connection strings for direct access to database tables:

    ```{python}
    # Get path to a DuckDB database file from package data
    duckdb_path = pb.get_data_path("game_revenue", "duckdb")

    pb.get_row_count(f"duckdb:///{duckdb_path}::game_revenue")
    ```

    The function always returns the number of rows in the table as an integer value, which is `2000`
    for the `game_revenue` dataset.
    """
    from pathlib import Path

    # Process different input types
    if isinstance(data, str) or isinstance(data, Path):
        data = _process_data(data)
    elif isinstance(data, list):
        # Handle list of file paths (likely Parquet files)
        data = _process_parquet_input(data)

    # Use Narwhals to handle all DataFrame types (including Ibis) uniformly
    try:
        import narwhals as nw

        df_nw = nw.from_native(data)
        # Handle LazyFrames by collecting them first
        if hasattr(df_nw, "collect"):
            df_nw = df_nw.collect()
        # Try different ways to get row count
        if hasattr(df_nw, "shape"):
            return df_nw.shape[0]
        elif hasattr(df_nw, "height"):  # pragma: no cover
            return df_nw.height  # pragma: no cover
        else:  # pragma: no cover
            raise ValueError("Unable to determine row count from Narwhals DataFrame")
    except Exception:  # pragma: no cover
        # Fallback for types that don't work with Narwhals
        if "pandas" in str(type(data)):  # pragma: no cover
            return data.shape[0]
        elif "pyspark" in str(type(data)):  # pragma: no cover
            return data.count()
        else:
            raise ValueError("The input table type supplied in `data=` is not supported.")


@dataclass
class _ValidationInfo:
    """
    Information about a validation to be performed on a table and the results of the interrogation.

    Attributes
    ----------
    i
        The validation step number.
    i_o
        The original validation step number (if a step creates multiple steps).
    step_id
        The ID of the step (if a step creates multiple steps). Unused.
    sha1
        The SHA-1 hash of the step. Unused.
    assertion_type
        The type of assertion. This is the method name of the validation (e.g., `"col_vals_gt"`).
    column
        The column(s) to validate.
    values
        The value or values to compare against.
    na_pass
        Whether to pass test units that hold missing values.
    pre
        A preprocessing function or lambda to apply to the data table for the validation step.
    segments
        The segments to use for the validation step.
    thresholds
        The threshold values for the validation.
    actions
        The actions to take if the validation fails.
    label
        A label for the validation step. Unused.
    brief
        A brief description of the validation step.
    autobrief
        An automatically-generated brief for the validation step.
    active
        Whether the validation step is active.
    all_passed
        Upon interrogation, this describes whether all test units passed for a validation step.
    n
        The number of test units for the validation step.
    n_passed
        The number of test units that passed (i.e., passing test units).
    n_failed
        The number of test units that failed (i.e., failing test units).
    f_passed
        The fraction of test units that passed. The calculation is `n_passed / n`.
    f_failed
        The fraction of test units that failed. The calculation is `n_failed / n`.
    warning
        Whether the number of failing test units is beyond the 'warning' threshold level.
    error
        Whether the number of failing test units is beyond the 'error' threshold level.
    critical
        Whether the number of failing test units is beyond the 'critical' threshold level.
    failure_text
        Localized text explaining the failure. Only set if any threshold is exceeded.
    tbl_checked
        The data table in its native format that has been checked for the validation step. It wil
        include a new column called `pb_is_good_` that is a boolean column that indicates whether
        the row passed the validation or not.
    extract
        The extracted rows from the table that failed the validation step.
    time_processed
        The time the validation step was processed. This is in the ISO 8601 format in UTC time.
    proc_duration_s
        The duration of processing for the validation step in seconds.
    """

    # Validation plan
    i: int | None = None
    i_o: int | None = None
    step_id: str | None = None
    sha1: str | None = None
    assertion_type: str | None = None
    column: any | None = None
    values: any | list[any] | tuple | None = None
    inclusive: tuple[bool, bool] | None = None
    na_pass: bool | None = None
    pre: Callable | None = None
    segments: any | None = None
    thresholds: Thresholds | None = None
    actions: Actions | None = None
    label: str | None = None
    brief: str | None = None
    autobrief: str | None = None
    active: bool | None = None
    # Interrogation results
    eval_error: bool | None = None
    all_passed: bool | None = None
    n: int | None = None
    n_passed: int | None = None
    n_failed: int | None = None
    f_passed: int | None = None
    f_failed: int | None = None
    warning: bool | None = None
    error: bool | None = None
    critical: bool | None = None
    failure_text: str | None = None
    tbl_checked: FrameT | None = None
    extract: FrameT | None = None
    val_info: dict[str, any] | None = None
    time_processed: str | None = None
    proc_duration_s: float | None = None

    def get_val_info(self) -> dict[str, any]:
        return self.val_info


def connect_to_table(connection_string: str) -> Any:
    """
    Connect to a database table using a connection string.

    This utility function tests whether a connection string leads to a valid table and returns
    the table object if successful. It provides helpful error messages when no table is specified
    or when backend dependencies are missing.

    Parameters
    ----------
    connection_string
        A database connection string with a required table specification using the `::table_name`
        suffix. Supported formats are outlined in the *Supported Connection String Formats* section.

    Returns
    -------
    Any
        An Ibis table object for the specified database table.

    Supported Connection String Formats
    -----------------------------------
    The `connection_string` parameter must include a valid connection string with a table name
    specified using the `::` syntax. Here are some examples on how to format connection strings
    for various backends:

    ```
    DuckDB:     "duckdb:///path/to/database.ddb::table_name"
    SQLite:     "sqlite:///path/to/database.db::table_name"
    PostgreSQL: "postgresql://user:password@localhost:5432/database::table_name"
    MySQL:      "mysql://user:password@localhost:3306/database::table_name"
    BigQuery:   "bigquery://project/dataset::table_name"
    Snowflake:  "snowflake://user:password@account/database/schema::table_name"
    ```

    If the connection string does not include a table name, the function will attempt to connect to
    the database and list available tables, providing guidance on how to specify a table.

    Examples
    --------
    Connect to a DuckDB table:

    ```{python}
    import pointblank as pb

    # Get path to a DuckDB database file from package data
    duckdb_path = pb.get_data_path("game_revenue", "duckdb")

    # Connect to the `game_revenue` table in the DuckDB database
    game_revenue = pb.connect_to_table(f"duckdb:///{duckdb_path}::game_revenue")

    # Use with the `preview()` function
    pb.preview(game_revenue)
    ```

    Here are some backend-specific connection examples:

    ```python
    # PostgreSQL
    pg_table = pb.connect_to_table(
        "postgresql://user:password@localhost:5432/warehouse::customer_data"
    )

    # SQLite
    sqlite_table = pb.connect_to_table("sqlite:///local_data.db::products")

    # BigQuery
    bq_table = pb.connect_to_table("bigquery://my-project/analytics::daily_metrics")
    ```

    This function requires the Ibis library with appropriate backend drivers:

    ```bash
    # You can install a set of common backends:
    pip install 'ibis-framework[duckdb,postgres,mysql,sqlite]'

    # ...or specific backends as needed:
    pip install 'ibis-framework[duckdb]'    # for DuckDB
    pip install 'ibis-framework[postgres]'  # for PostgreSQL
    ```
    """
    # Check if Ibis is available
    if not _is_lib_present(lib_name="ibis"):
        raise ImportError(
            "The Ibis library is not installed but is required for database connection strings.\n"
            "Install it with: pip install 'ibis-framework[duckdb]' (or other backend as needed)"
        )

    import ibis

    # Check if connection string includes table specification
    if "::" not in connection_string:
        # Try to connect to get available tables for helpful error message
        try:
            # Extract the base connection string (without table name)
            base_connection = connection_string

            # Connect to the database
            conn = ibis.connect(base_connection)

            # Get list of available tables
            try:
                available_tables = conn.list_tables()
            except Exception:  # pragma: no cover
                available_tables = []

            conn.disconnect()

            # Create helpful error message
            if available_tables:
                table_list = "\n".join(f"  - {table}" for table in available_tables)
                error_msg = (
                    f"No table specified in connection string: {connection_string}\n\n"
                    f"Available tables in the database:\n{table_list}\n\n"
                    f"To access a specific table, use the format:\n"
                    f"  {connection_string}::TABLE_NAME\n\n"
                    f"Examples:\n"
                )
                # Add examples with first few table names
                for table in available_tables[:3]:
                    error_msg += f"  {connection_string}::{table}\n"
            else:
                error_msg = (
                    f"No table specified in connection string: {connection_string}\n\n"
                    f"No tables found in the database or unable to list tables.\n\n"
                    f"To access a specific table, use the format:\n"
                    f"  {connection_string}::TABLE_NAME"
                )

            raise ValueError(error_msg)

        except Exception as e:
            if isinstance(e, ValueError):
                raise  # Re-raise our custom ValueError

            # Check for backend-specific errors and provide installation guidance
            error_str = str(e).lower()
            backend_install_map = {
                "duckdb": "pip install 'ibis-framework[duckdb]'",
                "postgresql": "pip install 'ibis-framework[postgres]'",
                "postgres": "pip install 'ibis-framework[postgres]'",
                "mysql": "pip install 'ibis-framework[mysql]'",
                "sqlite": "pip install 'ibis-framework[sqlite]'",
                "bigquery": "pip install 'ibis-framework[bigquery]'",
                "snowflake": "pip install 'ibis-framework[snowflake]'",
            }

            # Check if this is a missing backend dependency
            for backend, install_cmd in backend_install_map.items():  # pragma: no cover
                if backend in error_str and ("not found" in error_str or "no module" in error_str):
                    raise ConnectionError(
                        f"Missing {backend.upper()} backend for Ibis. Install it with:\n"
                        f"  {install_cmd}\n\n"
                        f"Original error: {e}\n\n"
                        f"Supported connection string formats:\n"
                        f"- DuckDB: 'duckdb:///path/to/file.ddb::table_name'\n"
                        f"- SQLite: 'sqlite:///path/to/file.db::table_name'\n"
                        f"- PostgreSQL: 'postgresql://user:pass@host:port/db::table_name'\n"
                        f"- MySQL: 'mysql://user:pass@host:port/db::table_name'\n"
                        f"- BigQuery: 'bigquery://project/dataset::table_name'\n"
                        f"- Snowflake: 'snowflake://user:pass@account/db/schema::table_name'\n"
                        f"\nNote: Use '::table_name' to specify the table within the database."
                    ) from e

            # Generic connection error
            raise ConnectionError(  # pragma: no cover
                f"Failed to connect to database using connection string: {connection_string}\n"
                f"Error: {e}\n\n"
                f"No table specified. Use the format: {connection_string}::TABLE_NAME"
            ) from e

    # Split connection string and table name
    try:
        base_connection, table_name = connection_string.rsplit("::", 1)
    except ValueError:  # pragma: no cover
        raise ValueError(f"Invalid connection string format: {connection_string}")

    # Connect to database and get table
    try:
        conn = ibis.connect(base_connection)
        table = conn.table(table_name)
        return table

    except Exception as e:
        # Check for backend-specific errors and provide installation guidance
        error_str = str(e).lower()
        backend_install_map = {
            "duckdb": "pip install 'ibis-framework[duckdb]'",
            "postgresql": "pip install 'ibis-framework[postgres]'",
            "postgres": "pip install 'ibis-framework[postgres]'",
            "mysql": "pip install 'ibis-framework[mysql]'",
            "sqlite": "pip install 'ibis-framework[sqlite]'",
            "bigquery": "pip install 'ibis-framework[bigquery]'",
            "snowflake": "pip install 'ibis-framework[snowflake]'",
        }

        # Check if this is a missing backend dependency
        for backend, install_cmd in backend_install_map.items():
            if backend in error_str and ("not found" in error_str or "no module" in error_str):
                raise ConnectionError(
                    f"Missing {backend.upper()} backend for Ibis. Install it with:\n"
                    f"  {install_cmd}\n\n"
                    f"Original error: {e}"
                ) from e

        # Check if table doesn't exist
        if "table" in error_str and ("not found" in error_str or "does not exist" in error_str):
            # Try to get available tables for helpful message
            try:  # pragma: no cover
                available_tables = conn.list_tables()
                if available_tables:
                    table_list = "\n".join(f"  - {table}" for table in available_tables)
                    raise ValueError(
                        f"Table '{table_name}' not found in database.\n\n"
                        f"Available tables:\n{table_list}\n\n"
                        f"Check the table name and try again with:\n"
                        f"  {base_connection}::CORRECT_TABLE_NAME"
                    ) from e
                else:
                    raise ValueError(
                        f"Table '{table_name}' not found and no tables available in database."
                    ) from e
            except Exception:
                raise ValueError(
                    f"Table '{table_name}' not found in database. "
                    f"Check the table name and connection string."
                ) from e

        # Generic connection error
        raise ConnectionError(
            f"Failed to connect to table '{table_name}' using: {base_connection}\nError: {e}"
        ) from e


@dataclass
class Validate:
    """
    Workflow for defining a set of validations on a table and interrogating for results.

    The `Validate` class is used for defining a set of validation steps on a table and interrogating
    the table with the *validation plan*. This class is the main entry point for the *data quality
    reporting* workflow. The overall aim of this workflow is to generate comprehensive reporting
    information to assess the level of data quality for a target table.

    We can supply as many validation steps as needed, and having a large number of them should
    increase the validation coverage for a given table. The validation methods (e.g.,
    [`col_vals_gt()`](`pointblank.Validate.col_vals_gt`),
    [`col_vals_between()`](`pointblank.Validate.col_vals_between`), etc.) translate to discrete
    validation steps, where each step will be sequentially numbered (useful when viewing the
    reporting data). This process of calling validation methods is known as developing a
    *validation plan*.

    The validation methods, when called, are merely instructions up to the point the concluding
    [`interrogate()`](`pointblank.Validate.interrogate`) method is called. That kicks off the
    process of acting on the *validation plan* by querying the target table getting reporting
    results for each step. Once the interrogation process is complete, we can say that the workflow
    now has reporting information. We can then extract useful information from the reporting data
    to understand the quality of the table. Printing the `Validate` object (or using the
    [`get_tabular_report()`](`pointblank.Validate.get_tabular_report`) method) will return a table
    with the results of the interrogation and
    [`get_sundered_data()`](`pointblank.Validate.get_sundered_data`) allows for the splitting of the
    table based on passing and failing rows.

    Parameters
    ----------
    data
        The table to validate, which could be a DataFrame object, an Ibis table object, a CSV
        file path, a Parquet file path, a GitHub URL pointing to a CSV or Parquet file, or a
        database connection string. When providing a CSV or Parquet file path (as a string or
        `pathlib.Path` object), the file will be automatically loaded using an available DataFrame
        library (Polars or Pandas). Parquet input also supports glob patterns, directories
        containing .parquet files, and Spark-style partitioned datasets. GitHub URLs are
        automatically transformed to raw content URLs and downloaded. Connection strings enable
        direct database access via Ibis with optional table specification using the `::table_name`
        suffix. Read the *Supported Input Table Types* section for details on the supported table
        types.
    tbl_name
        An optional name to assign to the input table object. If no value is provided, a name will
        be generated based on whatever information is available. This table name will be displayed
        in the header area of the tabular report.
    label
        An optional label for the validation plan. If no value is provided, a label will be
        generated based on the current system date and time. Markdown can be used here to make the
        label more visually appealing (it will appear in the header area of the tabular report).
    thresholds
        Generate threshold failure levels so that all validation steps can report and react
        accordingly when exceeding the set levels. The thresholds are set at the global level and
        can be overridden at the validation step level (each validation step has its own
        `thresholds=` parameter). The default is `None`, which means that no thresholds will be set.
        Look at the *Thresholds* section for information on how to set threshold levels.
    actions
        The actions to take when validation steps meet or exceed any set threshold levels. These
        actions are paired with the threshold levels and are executed during the interrogation
        process when there are exceedances. The actions are executed right after each step is
        evaluated. Such actions should be provided in the form of an `Actions` object. If `None`
        then no global actions will be set. View the *Actions* section for information on how to set
        actions.
    final_actions
        The actions to take when the validation process is complete and the final results are
        available. This is useful for sending notifications or reporting the overall status of the
        validation process. The final actions are executed after all validation steps have been
        processed and the results have been collected. The final actions are not tied to any
        threshold levels, they are executed regardless of the validation results. Such actions
        should be provided in the form of a `FinalActions` object. If `None` then no finalizing
        actions will be set. Please see the *Actions* section for information on how to set final
        actions.
    brief
        A global setting for briefs, which are optional brief descriptions for validation steps
        (they be displayed in the reporting table). For such a global setting, templating elements
        like `"{step}"` (to insert the step number) or `"{auto}"` (to include an automatically
        generated brief) are useful. If `True` then each brief will be automatically generated. If
        `None` (the default) then briefs aren't globally set.
    lang
        The language to use for various reporting elements. By default, `None` will select English
        (`"en"`) as the but other options include French (`"fr"`), German (`"de"`), Italian
        (`"it"`), Spanish (`"es"`), and several more. Have a look at the *Reporting Languages*
        section for the full list of supported languages and information on how the language setting
        is utilized.
    locale
        An optional locale ID to use for formatting values in the reporting table according the
        locale's rules. Examples include `"en-US"` for English (United States) and `"fr-FR"` for
        French (France). More simply, this can be a language identifier without a designation of
        territory, like `"es"` for Spanish.

    Returns
    -------
    Validate
        A `Validate` object with the table and validations to be performed.

    Supported Input Table Types
    ---------------------------
    The `data=` parameter can be given any of the following table types:

    - Polars DataFrame (`"polars"`)
    - Pandas DataFrame (`"pandas"`)
    - PySpark table (`"pyspark"`)
    - DuckDB table (`"duckdb"`)*
    - MySQL table (`"mysql"`)*
    - PostgreSQL table (`"postgresql"`)*
    - SQLite table (`"sqlite"`)*
    - Microsoft SQL Server table (`"mssql"`)*
    - Snowflake table (`"snowflake"`)*
    - Databricks table (`"databricks"`)*
    - BigQuery table (`"bigquery"`)*
    - Parquet table (`"parquet"`)*
    - CSV files (string path or `pathlib.Path` object with `.csv` extension)
    - Parquet files (string path, `pathlib.Path` object, glob pattern, directory with `.parquet`
    extension, or partitioned dataset)
    - Database connection strings (URI format with optional table specification)

    The table types marked with an asterisk need to be prepared as Ibis tables (with type of
    `ibis.expr.types.relations.Table`). Furthermore, the use of `Validate` with such tables requires
    the Ibis library v9.5.0 and above to be installed. If the input table is a Polars or Pandas
    DataFrame, the Ibis library is not required.

    To use a CSV file, ensure that a string or `pathlib.Path` object with a `.csv` extension is
    provided. The file will be automatically detected and loaded using the best available DataFrame
    library. The loading preference is Polars first, then Pandas as a fallback.

    Connection strings follow database URL formats and must also specify a table using the
    `::table_name` suffix. Examples include:

    ```
    "duckdb:///path/to/database.ddb::table_name"
    "sqlite:///path/to/database.db::table_name"
    "postgresql://user:password@localhost:5432/database::table_name"
    "mysql://user:password@localhost:3306/database::table_name"
    "bigquery://project/dataset::table_name"
    "snowflake://user:password@account/database/schema::table_name"
    ```

    When using connection strings, the Ibis library with the appropriate backend driver is required.

    Thresholds
    ----------
    The `thresholds=` parameter is used to set the failure-condition levels for all validation
    steps. They are set here at the global level but can be overridden at the validation step level
    (each validation step has its own local `thresholds=` parameter).

    There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values can
    either be set as a proportion failing of all test units (a value between `0` to `1`), or, the
    absolute number of failing test units (as integer that's `1` or greater).

    Thresholds can be defined using one of these input schemes:

    1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
    thresholds)
    2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is the
    'error' level, and position `2` is the 'critical' level
    3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
    'critical'
    4. a single integer/float value denoting absolute number or fraction of failing test units for
    the 'warning' level only

    If the number of failing test units for a validation step exceeds set thresholds, the validation
    step will be marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need
    to be set, you're free to set any combination of them.

    Aside from reporting failure conditions, thresholds can be used to determine the actions to take
    for each level of failure (using the `actions=` parameter).

    Actions
    -------
    The `actions=` and `final_actions=` parameters provide mechanisms to respond to validation
    results. These actions can be used to notify users of validation failures, log issues, or
    trigger other processes when problems are detected.

    *Step Actions*

    The `actions=` parameter allows you to define actions that are triggered when validation steps
    exceed specific threshold levels (warning, error, or critical). These actions are executed
    during the interrogation process, right after each step is evaluated.

    Step actions should be provided using the [`Actions`](`pointblank.Actions`) class, which lets
    you specify different actions for different severity levels:

    ```python
    # Define an action that logs a message when warning threshold is exceeded
    def log_warning():
        metadata = pb.get_action_metadata()
        print(f"WARNING: Step {metadata['step']} failed with type {metadata['type']}")

    # Define actions for different threshold levels
    actions = pb.Actions(
        warning = log_warning,
        error = lambda: send_email("Error in validation"),
        critical = "CRITICAL FAILURE DETECTED"
    )

    # Use in Validate
    validation = pb.Validate(
        data=my_data,
        actions=actions  # Global actions for all steps
    )
    ```

    You can also provide step-specific actions in individual validation methods:

    ```python
    validation.col_vals_gt(
        columns="revenue",
        value=0,
        actions=pb.Actions(warning=log_warning)  # Only applies to this step
    )
    ```

    Step actions have access to step-specific context through the
    [`get_action_metadata()`](`pointblank.get_action_metadata`) function, which provides details
    about the current validation step that triggered the action.

    *Final Actions*

    The `final_actions=` parameter lets you define actions that execute after all validation steps
    have completed. These are useful for providing summaries, sending notifications based on
    overall validation status, or performing cleanup operations.

    Final actions should be provided using the [`FinalActions`](`pointblank.FinalActions`) class:

    ```python
    def send_report():
        summary = pb.get_validation_summary()
        if summary["status"] == "CRITICAL":
            send_alert_email(
                subject=f"CRITICAL validation failures in {summary['tbl_name']}",
                body=f"{summary['critical_steps']} steps failed with critical severity."
            )

    validation = pb.Validate(
        data=my_data,
        final_actions=pb.FinalActions(send_report)
    )
    ```

    Final actions have access to validation-wide summary information through the
    [`get_validation_summary()`](`pointblank.get_validation_summary`) function, which provides a
    comprehensive overview of the entire validation process.

    The combination of step actions and final actions provides a flexible system for responding to
    data quality issues at both the individual step level and the overall validation level.

    Reporting Languages
    -------------------
    Various pieces of reporting in Pointblank can be localized to a specific language. This is done
    by setting the `lang=` parameter in `Validate`. Any of the following languages can be used (just
    provide the language code):

    - English (`"en"`)
    - French (`"fr"`)
    - German (`"de"`)
    - Italian (`"it"`)
    - Spanish (`"es"`)
    - Portuguese (`"pt"`)
    - Dutch (`"nl"`)
    - Swedish (`"sv"`)
    - Danish (`"da"`)
    - Norwegian Bokmål (`"nb"`)
    - Icelandic (`"is"`)
    - Finnish (`"fi"`)
    - Polish (`"pl"`)
    - Czech (`"cs"`)
    - Romanian (`"ro"`)
    - Greek (`"el"`)
    - Russian (`"ru"`)
    - Turkish (`"tr"`)
    - Arabic (`"ar"`)
    - Hindi (`"hi"`)
    - Simplified Chinese (`"zh-Hans"`)
    - Traditional Chinese (`"zh-Hant"`)
    - Japanese (`"ja"`)
    - Korean (`"ko"`)
    - Vietnamese (`"vi"`)
    - Indonesian (`"id"`)
    - Ukrainian (`"uk"`)
    - Hebrew (`"he"`)
    - Thai (`"th"`)
    - Persian (`"fa"`)

    Automatically generated briefs (produced by using `brief=True` or `brief="...{auto}..."`) will
    be written in the selected language. The language setting will also used when generating the
    validation report table through
    [`get_tabular_report()`](`pointblank.Validate.get_tabular_report`) (or printing the `Validate`
    object in a notebook environment).

    Examples
    --------
    ### Creating a validation plan and interrogating

    Let's walk through a data quality analysis of an extremely small table. It's actually called
    `"small_table"` and it's accessible through the [`load_dataset()`](`pointblank.load_dataset`)
    function.

    ```{python}
    import pointblank as pb

    # Load the `small_table` dataset
    small_table = pb.load_dataset(dataset="small_table", tbl_type="polars")

    # Preview the table
    pb.preview(small_table)
    ```

    We ought to think about what's tolerable in terms of data quality so let's designate
    proportional failure thresholds to the 'warning', 'error', and 'critical' states. This can be
    done by using the [`Thresholds`](`pointblank.Thresholds`) class.

    ```{python}
    thresholds = pb.Thresholds(warning=0.10, error=0.25, critical=0.35)
    ```

    Now, we use the `Validate` class and give it the `thresholds` object (which serves as a default
    for all validation steps but can be overridden). The static thresholds provided in `thresholds=`
    will make the reporting a bit more useful. We also need to provide a target table and we'll use
    `small_table` for this.

    ```{python}
    validation = (
        pb.Validate(
            data=small_table,
            tbl_name="small_table",
            label="`Validate` example.",
            thresholds=thresholds
        )
    )
    ```

    Then, as with any `Validate` object, we can add steps to the validation plan by using as many
    validation methods as we want. To conclude the process (and actually query the data table), we
    use the [`interrogate()`](`pointblank.Validate.interrogate`) method.

    ```{python}
    validation = (
        validation
        .col_vals_gt(columns="d", value=100)
        .col_vals_le(columns="c", value=5)
        .col_vals_between(columns="c", left=3, right=10, na_pass=True)
        .col_vals_regex(columns="b", pattern=r"[0-9]-[a-z]{3}-[0-9]{3}")
        .col_exists(columns=["date", "date_time"])
        .interrogate()
    )
    ```

    The `validation` object can be printed as a reporting table.

    ```{python}
    validation
    ```

    The report could be further customized by using the
    [`get_tabular_report()`](`pointblank.Validate.get_tabular_report`) method, which contains
    options for modifying the display of the table.

    ### Adding briefs

    Briefs are short descriptions of the validation steps. While they can be set for each step
    individually, they can also be set globally. The global setting is done by using the
    `brief=` argument in `Validate`. The global setting can be as simple as `True` to have
    automatically-generated briefs for each step. Alternatively, we can use templating elements
    like `"{step}"` (to insert the step number) or `"{auto}"` (to include an automatically generated
    brief). Here's an example of a global setting for briefs:

    ```{python}
    validation_2 = (
        pb.Validate(
            data=pb.load_dataset(),
            tbl_name="small_table",
            label="Validation example with briefs",
            brief="Step {step}: {auto}",
        )
        .col_vals_gt(columns="d", value=100)
        .col_vals_between(columns="c", left=3, right=10, na_pass=True)
        .col_vals_regex(
            columns="b",
            pattern=r"[0-9]-[a-z]{3}-[0-9]{3}",
            brief="Regex check for column {col}"
        )
        .interrogate()
    )

    validation_2
    ```

    We see the text of the briefs appear in the `STEP` column of the reporting table. Furthermore,
    the global brief's template (`"Step {step}: {auto}"`) is applied to all steps except for the
    final step, where the step-level `brief=` argument provided an override.

    If you should want to cancel the globally-defined brief for one or more validation steps, you
    can set `brief=False` in those particular steps.

    ### Post-interrogation methods

    The `Validate` class has a number of post-interrogation methods that can be used to extract
    useful information from the validation results. For example, the
    [`get_data_extracts()`](`pointblank.Validate.get_data_extracts`) method can be used to get
    the data extracts for each validation step.

    ```{python}
    validation_2.get_data_extracts()
    ```

    We can also view step reports for each validation step using the
    [`get_step_report()`](`pointblank.Validate.get_step_report`) method. This method adapts to the
    type of validation step and shows the relevant information for a step's validation.

    ```{python}
    validation_2.get_step_report(i=2)
    ```

    The `Validate` class also has a method for getting the sundered data, which is the data that
    passed or failed the validation steps. This can be done using the
    [`get_sundered_data()`](`pointblank.Validate.get_sundered_data`) method.

    ```{python}
    pb.preview(validation_2.get_sundered_data())
    ```

    The sundered data is a DataFrame that contains the rows that passed or failed the validation.
    The default behavior is to return the rows that failed the validation, as shown above.

    ### Working with CSV Files

    The `Validate` class can directly accept CSV file paths, making it easy to validate data stored
    in CSV files without manual loading:

    ```{python}
    # Get a path to a CSV file from the package data
    csv_path = pb.get_data_path("global_sales", "csv")

    validation_3 = (
        pb.Validate(
            data=csv_path,
            label="CSV validation example"
        )
        .col_exists(["customer_id", "product_id", "revenue"])
        .col_vals_not_null(["customer_id", "product_id"])
        .col_vals_gt(columns="revenue", value=0)
        .interrogate()
    )

    validation_3
    ```

    You can also use a Path object to specify the CSV file. Here's an example of how to do that:

    ```{python}
    from pathlib import Path

    csv_file = Path(pb.get_data_path("game_revenue", "csv"))

    validation_4 = (
        pb.Validate(data=csv_file, label="Game Revenue Validation")
        .col_exists(["player_id", "session_id", "item_name"])
        .col_vals_regex(
            columns="session_id",
            pattern=r"[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}"
        )
        .col_vals_gt(columns="item_revenue", value=0, na_pass=True)
        .interrogate()
    )

    validation_4
    ```

    The CSV loading is automatic, so when a string or Path with a `.csv` extension is provided,
    Pointblank will automatically load the file using the best available DataFrame library (Polars
    preferred, Pandas as fallback). The loaded data can then be used with all validation methods
    just like any other supported table type.

    ### Working with Parquet Files

    The `Validate` class can directly accept Parquet files and datasets in various formats. The
    following examples illustrate how to validate Parquet files:

    ```{python}
    # Single Parquet file from package data
    parquet_path = pb.get_data_path("nycflights", "parquet")

    validation_5 = (
        pb.Validate(
            data=parquet_path,
            tbl_name="NYC Flights Data"
        )
        .col_vals_not_null(["carrier", "origin", "dest"])
        .col_vals_gt(columns="distance", value=0)
        .interrogate()
    )

    validation_5
    ```

    You can also use glob patterns and directories. Here are some examples for how to:

    1. load multiple Parquet files
    2. load a Parquet-containing directory
    3. load a partitioned Parquet dataset

    ```python
    # Multiple Parquet files with glob patterns
    validation_6 = pb.Validate(data="data/sales_*.parquet")

    # Directory containing Parquet files
    validation_7 = pb.Validate(data="parquet_data/")

    # Partitioned Parquet dataset
    validation_8 = (
        pb.Validate(data="sales_data/")  # Contains year=2023/quarter=Q1/region=US/sales.parquet
        .col_exists(["transaction_id", "amount", "year", "quarter", "region"])
        .interrogate()
    )
    ```

    When you point to a directory that contains a partitioned Parquet dataset (with subdirectories
    like `year=2023/quarter=Q1/region=US/`), Pointblank will automatically:

    - discover all Parquet files recursively
    - extract partition column values from directory paths
    - add partition columns to the final DataFrame
    - combine all partitions into a single table for validation

    Both Polars and Pandas handle partitioned datasets natively, so this works seamlessly with
    either DataFrame library. The loading preference is Polars first, then Pandas as a fallback.

    ### Working with Database Connection Strings

    The `Validate` class supports database connection strings for direct validation of database
    tables. Connection strings must specify a table using the `::table_name` suffix:

    ```{python}
    # Get path to a DuckDB database file from package data
    duckdb_path = pb.get_data_path("game_revenue", "duckdb")

    validation_9 = (
        pb.Validate(
            data=f"duckdb:///{duckdb_path}::game_revenue",
            label="DuckDB Game Revenue Validation"
        )
        .col_exists(["player_id", "session_id", "item_revenue"])
        .col_vals_gt(columns="item_revenue", value=0)
        .interrogate()
    )

    validation_9
    ```

    For comprehensive documentation on supported connection string formats, error handling, and
    installation requirements, see the [`connect_to_table()`](`pointblank.connect_to_table`)
    function. This function handles all the connection logic and provides helpful error messages
    when table specifications are missing or backend dependencies are not installed.
    """

    data: FrameT | Any
    tbl_name: str | None = None
    label: str | None = None
    thresholds: int | float | bool | tuple | dict | Thresholds | None = None
    actions: Actions | None = None
    final_actions: FinalActions | None = None
    brief: str | bool | None = None
    lang: str | None = None
    locale: str | None = None

    def __post_init__(self):
        # Process data through the centralized data processing pipeline
        self.data = _process_data(self.data)

        # Check input of the `thresholds=` argument
        _check_thresholds(thresholds=self.thresholds)

        # Normalize the thresholds value (if any) to a Thresholds object
        self.thresholds = _normalize_thresholds_creation(self.thresholds)

        # Check that `actions` is an Actions object if provided
        # TODO: allow string, callable, of list of either and upgrade to Actions object
        if self.actions is not None and not isinstance(self.actions, Actions):  # pragma: no cover
            raise TypeError(
                "The `actions=` parameter must be an `Actions` object. "
                "Please use `Actions()` to wrap your actions."
            )

        # Check that `final_actions` is a FinalActions object if provided
        # TODO: allow string, callable, of list of either and upgrade to FinalActions object
        if self.final_actions is not None and not isinstance(
            self.final_actions, FinalActions
        ):  # pragma: no cover
            raise TypeError(
                "The `final_actions=` parameter must be a `FinalActions` object. "
                "Please use `FinalActions()` to wrap your finalizing actions."
            )

        # Normalize the reporting language identifier and error if invalid
        if self.lang not in ["zh-Hans", "zh-Hant"]:
            self.lang = _normalize_reporting_language(lang=self.lang)

        # Set the `locale` to the `lang` value if `locale` isn't set
        if self.locale is None:
            self.locale = self.lang

        # Transform any shorthands of `brief` to string representations
        self.brief = _transform_auto_brief(brief=self.brief)

        # TODO: Add functionality to obtain the column names and types from the table
        self.col_names = None
        self.col_types = None

        self.time_start = None
        self.time_end = None

        self.validation_info = []

    def set_tbl(
        self,
        tbl: FrameT | Any,
        tbl_name: str | None = None,
        label: str | None = None,
    ) -> Validate:
        """
        Set or replace the table associated with the Validate object.

        This method allows you to replace the table associated with a Validate object with a
        different (but presumably similar) table. This is useful when you want to apply the same
        validation plan to multiple tables or when you have a validation workflow defined but want
        to swap in a different data source.

        Parameters
        ----------
        tbl
            The table to replace the existing table with. This can be any supported table type
            including DataFrame objects, Ibis table objects, CSV file paths, Parquet file paths,
            GitHub URLs, or database connection strings. The same table type constraints apply as in
            the `Validate` constructor.
        tbl_name
            An optional name to assign to the new input table object. If no value is provided, the
            existing table name will be retained.
        label
            An optional label for the validation plan. If no value is provided, the existing label
            will be retained.

        Returns
        -------
        Validate
            A new `Validate` object with the replacement table.

        When to Use
        -----------
        The `set_tbl()` method is particularly useful in scenarios where you have:

        - multiple similar tables that need the same validation checks
        - a template validation workflow that should be applied to different data sources
        - YAML-defined validations where you want to override the table specified in the YAML

        The `set_tbl()` method creates a copy of the validation object with the new table, so the
        original validation object remains unchanged. This allows you to reuse validation plans
        across multiple tables without interference.

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        We will first create two similar tables for our future validation plans.

        ```{python}
        import pointblank as pb
        import polars as pl

        # Create two similar tables
        table_1 = pl.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [5, 4, 3, 2, 1],
            "z": ["a", "b", "c", "d", "e"]
        })

        table_2 = pl.DataFrame({
            "x": [2, 4, 6, 8, 10],
            "y": [10, 8, 6, 4, 2],
            "z": ["f", "g", "h", "i", "j"]
        })
        ```

        Create a validation plan with the first table.

        ```{python}
        validation_table_1 = (
            pb.Validate(
                data=table_1,
                tbl_name="Table 1",
                label="Validation applied to the first table"
            )
            .col_vals_gt(columns="x", value=0)
            .col_vals_lt(columns="y", value=10)
        )
        ```

        Now apply the same validation plan to the second table.

        ```{python}
        validation_table_2 = (
            validation_table_1
            .set_tbl(
                tbl=table_2,
                tbl_name="Table 2",
                label="Validation applied to the second table"
            )
        )
        ```

        Here is the interrogation of the first table:

        ```{python}
        validation_table_1.interrogate()
        ```

        And the second table:

        ```{python}
        validation_table_2.interrogate()
        ```
        """
        from copy import deepcopy

        # Create a deep copy of the current Validate object
        new_validate = deepcopy(self)

        # Process the new table through the centralized data processing pipeline
        new_validate.data = _process_data(tbl)

        # Update table name if provided, otherwise keep existing
        if tbl_name is not None:
            new_validate.tbl_name = tbl_name

        # Update label if provided, otherwise keep existing
        if label is not None:
            new_validate.label = label

        # Reset interrogation state since we have a new table, but preserve validation steps
        new_validate.time_start = None
        new_validate.time_end = None
        # Note: We keep validation_info as it contains the defined validation steps

        return new_validate

    def _repr_html_(self) -> str:
        return self.get_tabular_report()._repr_html_()  # pragma: no cover

    def col_vals_gt(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        value: float | int | Column,
        na_pass: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Are column data greater than a fixed value or data in another column?

        The `col_vals_gt()` validation method checks whether column values in a table are
        *greater than* a specified `value=` (the exact comparison used in this function is
        `col_val > value`). The `value=` can be specified as a single, literal value or as a column
        name given in [`col()`](`pointblank.col`). This validation will operate over the number of
        test units that is equal to the number of rows in the table (determined after any `pre=`
        mutation has been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        value
            The value to compare against. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison. For more information on which types of values are allowed, see the
            *What Can Be Used in `value=`?* section.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        What Can Be Used in `value=`?
        -----------------------------
        The `value=` argument allows for a variety of input types. The most common are:

        - a single numeric value
        - a single date or datetime value
        - A [`col()`](`pointblank.col`) object that represents a column name

        When supplying a number as the basis of comparison, keep in mind that all resolved columns
        must also be numeric. Should you have columns that are of the date or datetime types, you
        can supply a date or datetime value as the `value=` argument. There is flexibility in how
        you provide the date or datetime value, as it can be:

        - a string-based date or datetime (e.g., `"2023-10-01"`, `"2023-10-01 13:45:30"`, etc.)
        - a date or datetime object using the `datetime` module (e.g., `datetime.date(2023, 10, 1)`,
          `datetime.datetime(2023, 10, 1, 13, 45, 30)`, etc.)

        Finally, when supplying a column name in the `value=` argument, it must be specified within
        [`col()`](`pointblank.col`). This is a column-to-column comparison and, crucially, the
        columns being compared must be of the same type (e.g., both numeric, both date, etc.).

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns=` and `value=col(...)` that are expected to be present in the
        transformed table, but may not exist in the table before preprocessing. Regarding the
        lifetime of the transformed table, it only exists during the validation step and is not
        stored in the `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three numeric columns (`a`,
        `b`, and `c`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 6, 5, 7, 6, 5],
                "b": [1, 2, 1, 2, 2, 2],
                "c": [2, 1, 2, 2, 3, 4],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all greater than the value of `4`. We'll
        determine if this validation had any failing test units (there are six test units, one for
        each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=4)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_gt()`. All test units passed, and there are no failing test units.

        Aside from checking a column against a literal value, we can also use a column name in the
        `value=` argument (with the helper function [`col()`](`pointblank.col`) to perform a
        column-to-column comparison. For the next example, we'll use `col_vals_gt()` to check
        whether the values in column `c` are greater than values in column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="c", value=pb.col("b"))
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are:

        - Row 1: `c` is `1` and `b` is `2`.
        - Row 3: `c` is `2` and `b` is `2`.
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        # _check_value_float_int(value=value)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=active, param_name="active")

        # If value is a string-based date or datetime, convert it to the appropriate type
        value = _string_date_dttm_conversion(value=value)

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=value,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_lt(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        value: float | int | Column,
        na_pass: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Are column data less than a fixed value or data in another column?

        The `col_vals_lt()` validation method checks whether column values in a table are
        *less than* a specified `value=` (the exact comparison used in this function is
        `col_val < value`). The `value=` can be specified as a single, literal value or as a column
        name given in [`col()`](`pointblank.col`). This validation will operate over the number of
        test units that is equal to the number of rows in the table (determined after any `pre=`
        mutation has been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        value
            The value to compare against. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison. For more information on which types of values are allowed, see the
            *What Can Be Used in `value=`?* section.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        What Can Be Used in `value=`?
        -----------------------------
        The `value=` argument allows for a variety of input types. The most common are:

        - a single numeric value
        - a single date or datetime value
        - A [`col()`](`pointblank.col`) object that represents a column name

        When supplying a number as the basis of comparison, keep in mind that all resolved columns
        must also be numeric. Should you have columns that are of the date or datetime types, you
        can supply a date or datetime value as the `value=` argument. There is flexibility in how
        you provide the date or datetime value, as it can be:

        - a string-based date or datetime (e.g., `"2023-10-01"`, `"2023-10-01 13:45:30"`, etc.)
        - a date or datetime object using the `datetime` module (e.g., `datetime.date(2023, 10, 1)`,
          `datetime.datetime(2023, 10, 1, 13, 45, 30)`, etc.)

        Finally, when supplying a column name in the `value=` argument, it must be specified within
        [`col()`](`pointblank.col`). This is a column-to-column comparison and, crucially, the
        columns being compared must be of the same type (e.g., both numeric, both date, etc.).

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns=` and `value=col(...)` that are expected to be present in the
        transformed table, but may not exist in the table before preprocessing. Regarding the
        lifetime of the transformed table, it only exists during the validation step and is not
        stored in the `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three numeric columns (`a`,
        `b`, and `c`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 6, 5, 9, 7, 5],
                "b": [1, 2, 1, 2, 2, 2],
                "c": [2, 1, 1, 4, 3, 4],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all less than the value of `10`. We'll
        determine if this validation had any failing test units (there are six test units, one for
        each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_lt(columns="a", value=10)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_lt()`. All test units passed, and there are no failing test units.

        Aside from checking a column against a literal value, we can also use a column name in the
        `value=` argument (with the helper function [`col()`](`pointblank.col`) to perform a
        column-to-column comparison. For the next example, we'll use `col_vals_lt()` to check
        whether the values in column `b` are less than values in column `c`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_lt(columns="b", value=pb.col("c"))
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are:

        - Row 1: `b` is `2` and `c` is `1`.
        - Row 2: `b` is `1` and `c` is `1`.
        """
        assertion_type = _get_fn_name()

        _check_column(column=columns)
        # _check_value_float_int(value=value)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=active, param_name="active")

        # If value is a string-based date or datetime, convert it to the appropriate type
        value = _string_date_dttm_conversion(value=value)

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=value,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_eq(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        value: float | int | Column,
        na_pass: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Are column data equal to a fixed value or data in another column?

        The `col_vals_eq()` validation method checks whether column values in a table are
        *equal to* a specified `value=` (the exact comparison used in this function is
        `col_val == value`). The `value=` can be specified as a single, literal value or as a column
        name given in [`col()`](`pointblank.col`). This validation will operate over the number of
        test units that is equal to the number of rows in the table (determined after any `pre=`
        mutation has been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        value
            The value to compare against. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison. For more information on which types of values are allowed, see the
            *What Can Be Used in `value=`?* section.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        What Can Be Used in `value=`?
        -----------------------------
        The `value=` argument allows for a variety of input types. The most common are:

        - a single numeric value
        - a single date or datetime value
        - A [`col()`](`pointblank.col`) object that represents a column name

        When supplying a number as the basis of comparison, keep in mind that all resolved columns
        must also be numeric. Should you have columns that are of the date or datetime types, you
        can supply a date or datetime value as the `value=` argument. There is flexibility in how
        you provide the date or datetime value, as it can be:

        - a string-based date or datetime (e.g., `"2023-10-01"`, `"2023-10-01 13:45:30"`, etc.)
        - a date or datetime object using the `datetime` module (e.g., `datetime.date(2023, 10, 1)`,
          `datetime.datetime(2023, 10, 1, 13, 45, 30)`, etc.)

        Finally, when supplying a column name in the `value=` argument, it must be specified within
        [`col()`](`pointblank.col`). This is a column-to-column comparison and, crucially, the
        columns being compared must be of the same type (e.g., both numeric, both date, etc.).

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns=` and `value=col(...)` that are expected to be present in the
        transformed table, but may not exist in the table before preprocessing. Regarding the
        lifetime of the transformed table, it only exists during the validation step and is not
        stored in the `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with two numeric columns (`a` and
        `b`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 5, 5, 5, 5, 5],
                "b": [5, 5, 5, 6, 5, 4],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all equal to the value of `5`. We'll determine
        if this validation had any failing test units (there are six test units, one for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_eq(columns="a", value=5)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_eq()`. All test units passed, and there are no failing test units.

        Aside from checking a column against a literal value, we can also use a column name in the
        `value=` argument (with the helper function [`col()`](`pointblank.col`) to perform a
        column-to-column comparison. For the next example, we'll use `col_vals_eq()` to check
        whether the values in column `a` are equal to the values in column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_eq(columns="a", value=pb.col("b"))
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are:

        - Row 3: `a` is `5` and `b` is `6`.
        - Row 5: `a` is `5` and `b` is `4`.
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        # _check_value_float_int(value=value)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=active, param_name="active")

        # If value is a string-based date or datetime, convert it to the appropriate type
        # Allow regular strings to pass through for string comparisons
        value = _conditional_string_date_dttm_conversion(value=value, allow_regular_strings=True)

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=value,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_ne(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        value: float | int | Column,
        na_pass: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Are column data not equal to a fixed value or data in another column?

        The `col_vals_ne()` validation method checks whether column values in a table are
        *not equal to* a specified `value=` (the exact comparison used in this function is
        `col_val != value`). The `value=` can be specified as a single, literal value or as a column
        name given in [`col()`](`pointblank.col`). This validation will operate over the number of
        test units that is equal to the number of rows in the table (determined after any `pre=`
        mutation has been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        value
            The value to compare against. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison. For more information on which types of values are allowed, see the
            *What Can Be Used in `value=`?* section.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        What Can Be Used in `value=`?
        -----------------------------
        The `value=` argument allows for a variety of input types. The most common are:

        - a single numeric value
        - a single date or datetime value
        - A [`col()`](`pointblank.col`) object that represents a column name

        When supplying a number as the basis of comparison, keep in mind that all resolved columns
        must also be numeric. Should you have columns that are of the date or datetime types, you
        can supply a date or datetime value as the `value=` argument. There is flexibility in how
        you provide the date or datetime value, as it can be:

        - a string-based date or datetime (e.g., `"2023-10-01"`, `"2023-10-01 13:45:30"`, etc.)
        - a date or datetime object using the `datetime` module (e.g., `datetime.date(2023, 10, 1)`,
          `datetime.datetime(2023, 10, 1, 13, 45, 30)`, etc.)

        Finally, when supplying a column name in the `value=` argument, it must be specified within
        [`col()`](`pointblank.col`). This is a column-to-column comparison and, crucially, the
        columns being compared must be of the same type (e.g., both numeric, both date, etc.).

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns=` and `value=col(...)` that are expected to be present in the
        transformed table, but may not exist in the table before preprocessing. Regarding the
        lifetime of the transformed table, it only exists during the validation step and is not
        stored in the `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with two numeric columns (`a` and
        `b`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 5, 5, 5, 5, 5],
                "b": [5, 6, 3, 6, 5, 8],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are not equal to the value of `3`. We'll determine
        if this validation had any failing test units (there are six test units, one for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_ne(columns="a", value=3)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_ne()`. All test units passed, and there are no failing test units.

        Aside from checking a column against a literal value, we can also use a column name in the
        `value=` argument (with the helper function [`col()`](`pointblank.col`) to perform a
        column-to-column comparison. For the next example, we'll use `col_vals_ne()` to check
        whether the values in column `a` aren't equal to the values in column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_ne(columns="a", value=pb.col("b"))
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are in rows
        0 and 4, where `a` is `5` and `b` is `5` in both cases (i.e., they are equal to each other).
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        # _check_value_float_int(value=value)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=active, param_name="active")

        # If value is a string-based date or datetime, convert it to the appropriate type
        # Allow regular strings to pass through for string comparisons
        value = _conditional_string_date_dttm_conversion(value=value, allow_regular_strings=True)

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=value,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_ge(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        value: float | int | Column,
        na_pass: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Are column data greater than or equal to a fixed value or data in another column?

        The `col_vals_ge()` validation method checks whether column values in a table are
        *greater than or equal to* a specified `value=` (the exact comparison used in this function
        is `col_val >= value`). The `value=` can be specified as a single, literal value or as a
        column name given in [`col()`](`pointblank.col`). This validation will operate over the
        number of test units that is equal to the number of rows in the table (determined after any
        `pre=` mutation has been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        value
            The value to compare against. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison. For more information on which types of values are allowed, see the
            *What Can Be Used in `value=`?* section.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        What Can Be Used in `value=`?
        -----------------------------
        The `value=` argument allows for a variety of input types. The most common are:

        - a single numeric value
        - a single date or datetime value
        - A [`col()`](`pointblank.col`) object that represents a column name

        When supplying a number as the basis of comparison, keep in mind that all resolved columns
        must also be numeric. Should you have columns that are of the date or datetime types, you
        can supply a date or datetime value as the `value=` argument. There is flexibility in how
        you provide the date or datetime value, as it can be:

        - a string-based date or datetime (e.g., `"2023-10-01"`, `"2023-10-01 13:45:30"`, etc.)
        - a date or datetime object using the `datetime` module (e.g., `datetime.date(2023, 10, 1)`,
          `datetime.datetime(2023, 10, 1, 13, 45, 30)`, etc.)

        Finally, when supplying a column name in the `value=` argument, it must be specified within
        [`col()`](`pointblank.col`). This is a column-to-column comparison and, crucially, the
        columns being compared must be of the same type (e.g., both numeric, both date, etc.).

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns=` and `value=col(...)` that are expected to be present in the
        transformed table, but may not exist in the table before preprocessing. Regarding the
        lifetime of the transformed table, it only exists during the validation step and is not
        stored in the `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three numeric columns (`a`,
        `b`, and `c`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 6, 5, 9, 7, 5],
                "b": [5, 3, 1, 8, 2, 3],
                "c": [2, 3, 1, 4, 3, 4],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all greater than or equal to the value of `5`.
        We'll determine if this validation had any failing test units (there are six test units, one
        for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_ge(columns="a", value=5)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_ge()`. All test units passed, and there are no failing test units.

        Aside from checking a column against a literal value, we can also use a column name in the
        `value=` argument (with the helper function [`col()`](`pointblank.col`) to perform a
        column-to-column comparison. For the next example, we'll use `col_vals_ge()` to check
        whether the values in column `b` are greater than values in column `c`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_ge(columns="b", value=pb.col("c"))
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are:

        - Row 0: `b` is `2` and `c` is `3`.
        - Row 4: `b` is `3` and `c` is `4`.
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        # _check_value_float_int(value=value)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=active, param_name="active")

        # If value is a string-based date or datetime, convert it to the appropriate type
        value = _string_date_dttm_conversion(value=value)

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=value,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_le(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        value: float | int | Column,
        na_pass: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Are column data less than or equal to a fixed value or data in another column?

        The `col_vals_le()` validation method checks whether column values in a table are
        *less than or equal to* a specified `value=` (the exact comparison used in this function is
        `col_val <= value`). The `value=` can be specified as a single, literal value or as a column
        name given in [`col()`](`pointblank.col`). This validation will operate over the number of
        test units that is equal to the number of rows in the table (determined after any `pre=`
        mutation has been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        value
            The value to compare against. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison. For more information on which types of values are allowed, see the
            *What Can Be Used in `value=`?* section.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        What Can Be Used in `value=`?
        -----------------------------
        The `value=` argument allows for a variety of input types. The most common are:

        - a single numeric value
        - a single date or datetime value
        - A [`col()`](`pointblank.col`) object that represents a column name

        When supplying a number as the basis of comparison, keep in mind that all resolved columns
        must also be numeric. Should you have columns that are of the date or datetime types, you
        can supply a date or datetime value as the `value=` argument. There is flexibility in how
        you provide the date or datetime value, as it can be:

        - a string-based date or datetime (e.g., `"2023-10-01"`, `"2023-10-01 13:45:30"`, etc.)
        - a date or datetime object using the `datetime` module (e.g., `datetime.date(2023, 10, 1)`,
          `datetime.datetime(2023, 10, 1, 13, 45, 30)`, etc.)

        Finally, when supplying a column name in the `value=` argument, it must be specified within
        [`col()`](`pointblank.col`). This is a column-to-column comparison and, crucially, the
        columns being compared must be of the same type (e.g., both numeric, both date, etc.).

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns=` and `value=col(...)` that are expected to be present in the
        transformed table, but may not exist in the table before preprocessing. Regarding the
        lifetime of the transformed table, it only exists during the validation step and is not
        stored in the `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three numeric columns (`a`,
        `b`, and `c`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 6, 5, 9, 7, 5],
                "b": [1, 3, 1, 5, 2, 5],
                "c": [2, 1, 1, 4, 3, 4],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all less than or equal to the value of `9`.
        We'll determine if this validation had any failing test units (there are six test units, one
        for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_le(columns="a", value=9)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_le()`. All test units passed, and there are no failing test units.

        Aside from checking a column against a literal value, we can also use a column name in the
        `value=` argument (with the helper function [`col()`](`pointblank.col`) to perform a
        column-to-column comparison. For the next example, we'll use `col_vals_le()` to check
        whether the values in column `c` are less than values in column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_le(columns="c", value=pb.col("b"))
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are:

        - Row 0: `c` is `2` and `b` is `1`.
        - Row 4: `c` is `3` and `b` is `2`.
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        # _check_value_float_int(value=value)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=active, param_name="active")

        # If value is a string-based date or datetime, convert it to the appropriate type
        value = _string_date_dttm_conversion(value=value)

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=value,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_between(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        left: float | int | Column,
        right: float | int | Column,
        inclusive: tuple[bool, bool] = (True, True),
        na_pass: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Do column data lie between two specified values or data in other columns?

        The `col_vals_between()` validation method checks whether column values in a table fall
        within a range. The range is specified with three arguments: `left=`, `right=`, and
        `inclusive=`. The `left=` and `right=` values specify the lower and upper bounds. These
        bounds can be specified as literal values or as column names provided within
        [`col()`](`pointblank.col`). The validation will operate over the number of test units that
        is equal to the number of rows in the table (determined after any `pre=` mutation has been
        applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        left
            The lower bound of the range. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison for this bound. See the *What Can Be Used in `left=` and `right=`?* section
            for details on this.
        right
            The upper bound of the range. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison for this bound. See the *What Can Be Used in `left=` and `right=`?* section
            for details on this.
        inclusive
            A tuple of two boolean values indicating whether the comparison should be inclusive. The
            position of the boolean values correspond to the `left=` and `right=` values,
            respectively. By default, both values are `True`.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        What Can Be Used in `left=` and `right=`?
        -----------------------------------------
        The `left=` and `right=` arguments both allow for a variety of input types. The most common
        are:

        - a single numeric value
        - a single date or datetime value
        - A [`col()`](`pointblank.col`) object that represents a column in the target table

        When supplying a number as the basis of comparison, keep in mind that all resolved columns
        must also be numeric. Should you have columns that are of the date or datetime types, you
        can supply a date or datetime value within `left=` and `right=`. There is flexibility in how
        you provide the date or datetime values for the bounds; they can be:

        - string-based dates or datetimes (e.g., `"2023-10-01"`, `"2023-10-01 13:45:30"`, etc.)
        - date or datetime objects using the `datetime` module (e.g., `datetime.date(2023, 10, 1)`,
        `datetime.datetime(2023, 10, 1, 13, 45, 30)`, etc.)

        Finally, when supplying a column name in either `left=` or `right=` (or both), it must be
        specified within [`col()`](`pointblank.col`). This facilitates column-to-column comparisons
        and, crucially, the columns being compared to either/both of the bounds must be of the same
        type as the column data (e.g., all numeric, all dates, etc.).

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns=` and `left=col(...)`/`right=col(...)` that are expected to be present
        in the transformed table, but may not exist in the table before preprocessing. Regarding the
        lifetime of the transformed table, it only exists during the validation step and is not
        stored in the `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three numeric columns (`a`,
        `b`, and `c`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [2, 3, 2, 4, 3, 4],
                "b": [5, 6, 1, 6, 8, 5],
                "c": [9, 8, 8, 7, 7, 8],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all between the fixed boundary values of `1`
        and `5`. We'll determine if this validation had any failing test units (there are six test
        units, one for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_between(columns="a", left=1, right=5)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_between()`. All test units passed, and there are no failing test units.

        Aside from checking a column against two literal values representing the lower and upper
        bounds, we can also provide column names to the `left=` and/or `right=` arguments (by using
        the helper function [`col()`](`pointblank.col`). In this way, we can perform three
        additional comparison types:

        1. `left=column`, `right=column`
        2. `left=literal`, `right=column`
        3. `left=column`, `right=literal`

        For the next example, we'll use `col_vals_between()` to check whether the values in column
        `b` are between than corresponding values in columns `a` (lower bound) and `c` (upper
        bound).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_between(columns="b", left=pb.col("a"), right=pb.col("c"))
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are:

        - Row 2: `b` is `1` but the bounds are `2` (`a`) and `8` (`c`).
        - Row 4: `b` is `8` but the bounds are `3` (`a`) and `7` (`c`).
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        # _check_value_float_int(value=left)
        # _check_value_float_int(value=right)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=active, param_name="active")

        # If `left=` or `right=` is a string-based date or datetime, convert to the appropriate type
        left = _string_date_dttm_conversion(value=left)
        right = _string_date_dttm_conversion(value=right)

        # Place the `left=` and `right=` values in a tuple for inclusion in the validation info
        value = (left, right)

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=value,
                inclusive=inclusive,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_outside(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        left: float | int | Column,
        right: float | int | Column,
        inclusive: tuple[bool, bool] = (True, True),
        na_pass: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Do column data lie outside of two specified values or data in other columns?

        The `col_vals_between()` validation method checks whether column values in a table *do not*
        fall within a certain range. The range is specified with three arguments: `left=`, `right=`,
        and `inclusive=`. The `left=` and `right=` values specify the lower and upper bounds. These
        bounds can be specified as literal values or as column names provided within
        [`col()`](`pointblank.col`). The validation will operate over the number of test units that
        is equal to the number of rows in the table (determined after any `pre=` mutation has been
        applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        left
            The lower bound of the range. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison for this bound. See the *What Can Be Used in `left=` and `right=`?* section
            for details on this.
        right
            The upper bound of the range. This can be a single value or a single column name given
            in [`col()`](`pointblank.col`). The latter option allows for a column-to-column
            comparison for this bound. See the *What Can Be Used in `left=` and `right=`?* section
            for details on this.
        inclusive
            A tuple of two boolean values indicating whether the comparison should be inclusive. The
            position of the boolean values correspond to the `left=` and `right=` values,
            respectively. By default, both values are `True`.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        What Can Be Used in `left=` and `right=`?
        -----------------------------------------
        The `left=` and `right=` arguments both allow for a variety of input types. The most common
        are:

        - a single numeric value
        - a single date or datetime value
        - A [`col()`](`pointblank.col`) object that represents a column in the target table

        When supplying a number as the basis of comparison, keep in mind that all resolved columns
        must also be numeric. Should you have columns that are of the date or datetime types, you
        can supply a date or datetime value within `left=` and `right=`. There is flexibility in how
        you provide the date or datetime values for the bounds; they can be:

        - string-based dates or datetimes (e.g., `"2023-10-01"`, `"2023-10-01 13:45:30"`, etc.)
        - date or datetime objects using the `datetime` module (e.g., `datetime.date(2023, 10, 1)`,
        `datetime.datetime(2023, 10, 1, 13, 45, 30)`, etc.)

        Finally, when supplying a column name in either `left=` or `right=` (or both), it must be
        specified within [`col()`](`pointblank.col`). This facilitates column-to-column comparisons
        and, crucially, the columns being compared to either/both of the bounds must be of the same
        type as the column data (e.g., all numeric, all dates, etc.).

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns=` and `left=col(...)`/`right=col(...)` that are expected to be present
        in the transformed table, but may not exist in the table before preprocessing. Regarding the
        lifetime of the transformed table, it only exists during the validation step and is not
        stored in the `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three numeric columns (`a`,
        `b`, and `c`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 6, 5, 7, 5, 5],
                "b": [2, 3, 6, 4, 3, 6],
                "c": [9, 8, 8, 9, 9, 7],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all outside the fixed boundary values of `1`
        and `4`. We'll determine if this validation had any failing test units (there are six test
        units, one for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_outside(columns="a", left=1, right=4)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_outside()`. All test units passed, and there are no failing test units.

        Aside from checking a column against two literal values representing the lower and upper
        bounds, we can also provide column names to the `left=` and/or `right=` arguments (by using
        the helper function [`col()`](`pointblank.col`). In this way, we can perform three
        additional comparison types:

        1. `left=column`, `right=column`
        2. `left=literal`, `right=column`
        3. `left=column`, `right=literal`

        For the next example, we'll use `col_vals_outside()` to check whether the values in column
        `b` are outside of the range formed by the corresponding values in columns `a` (lower bound)
        and `c` (upper bound).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_outside(columns="b", left=pb.col("a"), right=pb.col("c"))
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are:

        - Row 2: `b` is `6` and the bounds are `5` (`a`) and `8` (`c`).
        - Row 5: `b` is `6` and the bounds are `5` (`a`) and `7` (`c`).
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        # _check_value_float_int(value=left)
        # _check_value_float_int(value=right)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=active, param_name="active")

        # If `left=` or `right=` is a string-based date or datetime, convert to the appropriate type
        left = _string_date_dttm_conversion(value=left)
        right = _string_date_dttm_conversion(value=right)

        # Place the `left=` and `right=` values in a tuple for inclusion in the validation info
        value = (left, right)

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=value,
                inclusive=inclusive,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_in_set(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        set: Collection[Any],
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether column values are in a set of values.

        The `col_vals_in_set()` validation method checks whether column values in a table are part
        of a specified `set=` of values. This validation will operate over the number of test units
        that is equal to the number of rows in the table (determined after any `pre=` mutation has
        been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        set
            A collection of values to compare against. Can be a list of values, a Python Enum class,
            or a collection containing Enum instances. When an Enum class is provided, all enum
            values will be used. When a collection contains Enum instances, their values will be
            extracted automatically.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        a column via `columns=` that is expected to be present in the transformed table, but may not
        exist in the table before preprocessing. Regarding the lifetime of the transformed table, it
        only exists during the validation step and is not stored in the `Validate` object or used in
        subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with two numeric columns (`a` and
        `b`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 2, 4, 6, 2, 5],
                "b": [5, 8, 2, 6, 5, 1],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all in the set of `[2, 3, 4, 5, 6]`. We'll
        determine if this validation had any failing test units (there are six test units, one for
        each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_in_set(columns="a", set=[2, 3, 4, 5, 6])
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_in_set()`. All test units passed, and there are no failing test units.

        Now, let's use that same set of values for a validation on column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_in_set(columns="b", set=[2, 3, 4, 5, 6])
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are for the
        column `b` values of `8` and `1`, which are not in the set of `[2, 3, 4, 5, 6]`.

        **Using Python Enums**

        The `col_vals_in_set()` method also supports Python Enum classes and instances, which can
        make validations more readable and maintainable:

        ```{python}
        from enum import Enum

        class Color(Enum):
            RED = "red"
            GREEN = "green"
            BLUE = "blue"

        # Create a table with color data
        tbl_colors = pl.DataFrame({
            "product": ["shirt", "pants", "hat", "shoes"],
            "color": ["red", "blue", "green", "yellow"]
        })

        # Validate using an Enum class (all enum values are allowed)
        validation = (
            pb.Validate(data=tbl_colors)
            .col_vals_in_set(columns="color", set=Color)
            .interrogate()
        )

        validation
        ```

        This validation will fail for the `"yellow"` value since it's not in the `Color` enum.

        You can also use specific Enum instances or mix them with regular values:

        ```{python}
        # Validate using specific Enum instances
        validation = (
            pb.Validate(data=tbl_colors)
            .col_vals_in_set(columns="color", set=[Color.RED, Color.BLUE])
            .interrogate()
        )

        # Mix Enum instances with regular values
        validation = (
            pb.Validate(data=tbl_colors)
            .col_vals_in_set(columns="color", set=[Color.RED, Color.BLUE, "yellow"])
            .interrogate()
        )

        validation
        ```

        In this case, the `"green"` value will cause a failing test unit since it's not part of the
        specified set.
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)

        # Extract values from Enum classes or Enum instances if present
        set = _extract_enum_values(set)

        for val in set:
            if val is None:
                continue
            if not isinstance(val, (float, int, str)):
                raise ValueError("`set=` must be a list of floats, integers, or strings.")

        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=set,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_not_in_set(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        set: Collection[Any],
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether column values are not in a set of values.

        The `col_vals_not_in_set()` validation method checks whether column values in a table are
        *not* part of a specified `set=` of values. This validation will operate over the number of
        test units that is equal to the number of rows in the table (determined after any `pre=`
        mutation has been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        set
            A collection of values to compare against. Can be a list of values, a Python Enum class,
            or a collection containing Enum instances. When an Enum class is provided, all enum
            values will be used. When a collection contains Enum instances, their values will be
            extracted automatically.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        a column via `columns=` that is expected to be present in the transformed table, but may not
        exist in the table before preprocessing. Regarding the lifetime of the transformed table, it
        only exists during the validation step and is not stored in the `Validate` object or used in
        subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with two numeric columns (`a` and
        `b`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [7, 8, 1, 9, 1, 7],
                "b": [1, 8, 2, 6, 9, 1],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that none of the values in column `a` are in the set of `[2, 3, 4, 5, 6]`.
        We'll determine if this validation had any failing test units (there are six test units, one
        for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_not_in_set(columns="a", set=[2, 3, 4, 5, 6])
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_not_in_set()`. All test units passed, and there are no failing test
        units.

        Now, let's use that same set of values for a validation on column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_not_in_set(columns="b", set=[2, 3, 4, 5, 6])
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are for the
        column `b` values of `2` and `6`, both of which are in the set of `[2, 3, 4, 5, 6]`.

        **Using Python Enums**

        Like `col_vals_in_set()`, this method also supports Python Enum classes and instances:

        ```{python}
        from enum import Enum

        class InvalidStatus(Enum):
            DELETED = "deleted"
            ARCHIVED = "archived"

        # Create a table with status data
        status_table = pl.DataFrame({
            "product": ["widget", "gadget", "tool", "device"],
            "status": ["active", "pending", "deleted", "active"]
        })

        # Validate that no values are in the invalid status set
        validation = (
            pb.Validate(data=status_table)
            .col_vals_not_in_set(columns="status", set=InvalidStatus)
            .interrogate()
        )

        validation
        ```

        This `"deleted"` value in the `status` column will fail since it matches one of the invalid
        statuses in the `InvalidStatus` enum.
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)

        # Extract values from Enum classes or Enum instances if present
        set = _extract_enum_values(set)

        _check_set_types(set=set)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=set,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_null(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether values in a column are Null.

        The `col_vals_null()` validation method checks whether column values in a table are Null.
        This validation will operate over the number of test units that is equal to the number
        of rows in the table.

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        a column via `columns=` that is expected to be present in the transformed table, but may not
        exist in the table before preprocessing. Regarding the lifetime of the transformed table, it
        only exists during the validation step and is not stored in the `Validate` object or used in
        subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with two numeric columns (`a` and
        `b`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [None, None, None, None],
                "b": [None, 2, None, 9],
            }
        ).with_columns(pl.col("a").cast(pl.Int64))

        pb.preview(tbl)
        ```

        Let's validate that values in column `a` are all Null values. We'll determine if this
        validation had any failing test units (there are four test units, one for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_null(columns="a")
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_null()`. All test units passed, and there are no failing test units.

        Now, let's use that same set of values for a validation on column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_null(columns="b")
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are for the
        two non-Null values in column `b`.
        """
        assertion_type = _get_fn_name()

        _check_column(column=columns)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_not_null(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether values in a column are not Null.

        The `col_vals_not_null()` validation method checks whether column values in a table are not
        Null. This validation will operate over the number of test units that is equal to the number
        of rows in the table.

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        a column via `columns=` that is expected to be present in the transformed table, but may not
        exist in the table before preprocessing. Regarding the lifetime of the transformed table, it
        only exists during the validation step and is not stored in the `Validate` object or used in
        subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with two numeric columns (`a` and
        `b`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [4, 7, 2, 8],
                "b": [5, None, 1, None],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that none of the values in column `a` are Null values. We'll determine if
        this validation had any failing test units (there are four test units, one for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_not_null(columns="a")
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_not_null()`. All test units passed, and there are no failing test units.

        Now, let's use that same set of values for a validation on column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_not_null(columns="b")
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are for the
        two Null values in column `b`.
        """
        assertion_type = _get_fn_name()

        _check_column(column=columns)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_regex(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        pattern: str,
        na_pass: bool = False,
        inverse: bool = False,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether column values match a regular expression pattern.

        The `col_vals_regex()` validation method checks whether column values in a table
        correspond to a `pattern=` matching expression. This validation will operate over the number
        of test units that is equal to the number of rows in the table (determined after any `pre=`
        mutation has been applied).

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        pattern
            A regular expression pattern to compare against.
        na_pass
            Should any encountered None, NA, or Null values be considered as passing test units? By
            default, this is `False`. Set to `True` to pass test units with missing values.
        inverse
            Should the validation step be inverted? If `True`, then the expectation is that column
            values should *not* match the specified `pattern=` regex.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        a column via `columns=` that is expected to be present in the transformed table, but may not
        exist in the table before preprocessing. Regarding the lifetime of the transformed table, it
        only exists during the validation step and is not stored in the `Validate` object or used in
        subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with two string columns (`a` and
        `b`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": ["rb-0343", "ra-0232", "ry-0954", "rc-1343"],
                "b": ["ra-0628", "ra-583", "rya-0826", "rb-0735"],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that all of the values in column `a` match a particular regex pattern. We'll
        determine if this validation had any failing test units (there are four test units, one for
        each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_regex(columns="a", pattern=r"r[a-z]-[0-9]{4}")
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_regex()`. All test units passed, and there are no failing test units.

        Now, let's use the same regex for a validation on column `b`.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_regex(columns="b", pattern=r"r[a-z]-[0-9]{4}")
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The specific failing cases are for the
        string values of rows 1 and 2 in column `b`.
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=na_pass, param_name="na_pass")
        _check_boolean_input(param=inverse, param_name="inverse")
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Package up the `pattern=` and boolean params into a dictionary for later interrogation
        values = {"pattern": pattern, "inverse": inverse}

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=values,
                na_pass=na_pass,
                pre=pre,
                segments=segments,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def col_vals_expr(
        self,
        expr: any,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate column values using a custom expression.

        The `col_vals_expr()` validation method checks whether column values in a table satisfy a
        custom `expr=` expression. This validation will operate over the number of test units that
        is equal to the number of rows in the table (determined after any `pre=` mutation has been
        applied).

        Parameters
        ----------
        expr
            A column expression that will evaluate each row in the table, returning a boolean value
            per table row. If the target table is a Polars DataFrame, the expression should either
            be a Polars column expression or a Narwhals one. For a Pandas DataFrame, the expression
            should either be a lambda expression or a Narwhals column expression.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Regarding the lifetime of the
        transformed table, it only exists during the validation step and is not stored in the
        `Validate` object or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [1, 2, 1, 7, 8, 6],
                "b": [0, 0, 0, 1, 1, 1],
                "c": [0.5, 0.3, 0.8, 1.4, 1.9, 1.2],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that the values in column `a` are all integers. We'll determine if this
        validation had any failing test units (there are six test units, one for each row).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_vals_expr(expr=pl.col("a") % 1 == 0)
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows the single entry that corresponds to the validation step created
        by using `col_vals_expr()`. All test units passed, with no failing test units.
        """

        assertion_type = _get_fn_name()

        # TODO: Add a check for the expression to ensure it's a valid expression object
        # _check_expr(expr=expr)
        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            column=None,
            values=expr,
            pre=pre,
            segments=segments,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def col_exists(
        self,
        columns: str | list[str] | Column | ColumnSelector | ColumnSelectorNarwhals,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether one or more columns exist in the table.

        The `col_exists()` method checks whether one or more columns exist in the target table. The
        only requirement is specification of the column names. Each validation step or expectation
        will operate over a single test unit, which is whether the column exists or not.

        Parameters
        ----------
        columns
            A single column or a list of columns to validate. Can also use
            [`col()`](`pointblank.col`) with column selectors to specify one or more columns. If
            multiple columns are supplied or resolved, there will be a separate validation step
            generated for each column.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step(s) meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with a string columns (`a`) and a
        numeric column (`b`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": ["apple", "banana", "cherry", "date"],
                "b": [1, 6, 3, 5],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that the columns `a` and `b` actually exist in the table. We'll determine if
        this validation had any failing test units (each validation will have a single test unit).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_exists(columns=["a", "b"])
            .interrogate()
        )

        validation
        ```

        Printing the `validation` object shows the validation table in an HTML viewing environment.
        The validation table shows two entries (one check per column) generated by the
        `col_exists()` validation step. Both steps passed since both columns provided in `columns=`
        are present in the table.

        Now, let's check for the existence of a different set of columns.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_exists(columns=["b", "c"])
            .interrogate()
        )

        validation
        ```

        The validation table reports one passing validation step (the check for column `b`) and one
        failing validation step (the check for column `c`, which doesn't exist).
        """

        assertion_type = _get_fn_name()

        _check_column(column=columns)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `columns` is a ColumnSelector or Narwhals selector, call `col()` on it to later
        # resolve the columns
        if isinstance(columns, (ColumnSelector, nw.selectors.Selector)):
            columns = col(columns)

        # If `columns` is Column value or a string, place it in a list for iteration
        if isinstance(columns, (Column, str)):
            columns = [columns]

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Iterate over the columns and create a validation step for each
        for column in columns:
            val_info = _ValidationInfo(
                assertion_type=assertion_type,
                column=column,
                values=None,
                thresholds=thresholds,
                actions=actions,
                brief=brief,
                active=active,
            )

            self._add_validation(validation_info=val_info)

        return self

    def rows_distinct(
        self,
        columns_subset: str | list[str] | None = None,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether rows in the table are distinct.

        The `rows_distinct()` method checks whether rows in the table are distinct. This validation
        will operate over the number of test units that is equal to the number of rows in the table
        (determined after any `pre=` mutation has been applied).

        Parameters
        ----------
        columns_subset
            A single column or a list of columns to use as a subset for the distinct comparison.
            If `None`, then all columns in the table will be used for the comparison. If multiple
            columns are supplied, the distinct comparison will be made over the combination of
            values in those columns.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns_subset=` that are expected to be present in the transformed table, but
        may not exist in the table before preprocessing. Regarding the lifetime of the transformed
        table, it only exists during the validation step and is not stored in the `Validate` object
        or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three string columns
        (`col_1`, `col_2`, and `col_3`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "col_1": ["a", "b", "c", "d"],
                "col_2": ["a", "a", "c", "d"],
                "col_3": ["a", "a", "d", "e"],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that the rows in the table are distinct with `rows_distinct()`. We'll
        determine if this validation had any failing test units (there are four test units, one for
        each row). A failing test units means that a given row is not distinct from every other row.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .rows_distinct()
            .interrogate()
        )

        validation
        ```

        From this validation table we see that there are no failing test units. All rows in the
        table are distinct from one another.

        We can also use a subset of columns to determine distinctness. Let's specify the subset
        using columns `col_2` and `col_3` for the next validation.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .rows_distinct(columns_subset=["col_2", "col_3"])
            .interrogate()
        )

        validation
        ```

        The validation table reports two failing test units. The first and second rows are
        duplicated when considering only the values in columns `col_2` and `col_3`. There's only
        one set of duplicates but there are two failing test units since each row is compared to all
        others.
        """

        assertion_type = _get_fn_name()

        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        if columns_subset is not None and isinstance(columns_subset, str):
            columns_subset = [columns_subset]

        # TODO: incorporate Column object

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            column=columns_subset,
            pre=pre,
            segments=segments,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def rows_complete(
        self,
        columns_subset: str | list[str] | None = None,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether row data are complete by having no missing values.

        The `rows_complete()` method checks whether rows in the table are complete. Completeness
        of a row means that there are no missing values within the row. This validation will operate
        over the number of test units that is equal to the number of rows in the table (determined
        after any `pre=` mutation has been applied). A subset of columns can be specified for the
        completeness check. If no subset is provided, all columns in the table will be used.

        Parameters
        ----------
        columns_subset
            A single column or a list of columns to use as a subset for the completeness check. If
            `None` (the default), then all columns in the table will be used.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list). Read the *Segmentation* section for usage information.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Note that you can refer to
        columns via `columns_subset=` that are expected to be present in the transformed table, but
        may not exist in the table before preprocessing. Regarding the lifetime of the transformed
        table, it only exists during the validation step and is not stored in the `Validate` object
        or used in subsequent validation steps.

        Segmentation
        ------------
        The `segments=` argument allows for the segmentation of a validation step into multiple
        segments. This is useful for applying the same validation step to different subsets of the
        data. The segmentation can be done based on a single column or specific fields within a
        column.

        Providing a single column name will result in a separate validation step for each unique
        value in that column. For example, if you have a column called `"region"` with values
        `"North"`, `"South"`, and `"East"`, the validation step will be applied separately to each
        region.

        Alternatively, you can provide a tuple that specifies a column name and its corresponding
        values to segment on. For example, if you have a column called `"date"` and you want to
        segment on only specific dates, you can provide a tuple like
        `("date", ["2023-01-01", "2023-01-02"])`. Any other values in the column will be disregarded
        (i.e., no validation steps will be created for them).

        A list with a combination of column names and tuples can be provided as well. This allows
        for more complex segmentation scenarios. The following inputs are both valid:

        ```
        # Segments from all unique values in the `region` column
        # and specific dates in the `date` column
        segments=["region", ("date", ["2023-01-01", "2023-01-02"])]

        # Segments from all unique values in the `region` and `date` columns
        segments=["region", "date"]
        ```

        The segmentation is performed during interrogation, and the resulting validation steps will
        be numbered sequentially. Each segment will have its own validation step, and the results
        will be reported separately. This allows for a more granular analysis of the data and helps
        identify issues within specific segments.

        Importantly, the segmentation process will be performed after any preprocessing of the data
        table. Because of this, one can conceivably use the `pre=` argument to generate a column
        that can be used for segmentation. For example, you could create a new column called
        `"segment"` through use of `pre=` and then use that column for segmentation.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three string columns
        (`col_1`, `col_2`, and `col_3`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "col_1": ["a", None, "c", "d"],
                "col_2": ["a", "a", "c", None],
                "col_3": ["a", "a", "d", None],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that the rows in the table are complete with `rows_complete()`. We'll
        determine if this validation had any failing test units (there are four test units, one for
        each row). A failing test units means that a given row is not complete (i.e., has at least
        one missing value).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .rows_complete()
            .interrogate()
        )

        validation
        ```

        From this validation table we see that there are two failing test units. This is because
        two rows in the table have at least one missing value (the second row and the last row).

        We can also use a subset of columns to determine completeness. Let's specify the subset
        using columns `col_2` and `col_3` for the next validation.

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .rows_complete(columns_subset=["col_2", "col_3"])
            .interrogate()
        )

        validation
        ```

        The validation table reports a single failing test units. The last row contains missing
        values in both the `col_2` and `col_3` columns.
        others.
        """

        assertion_type = _get_fn_name()

        _check_pre(pre=pre)
        # TODO: add check for segments
        # _check_segments(segments=segments)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        if columns_subset is not None and isinstance(columns_subset, str):  # pragma: no cover
            columns_subset = [columns_subset]  # pragma: no cover

        # TODO: incorporate Column object

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            column=columns_subset,
            pre=pre,
            segments=segments,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def prompt(
        self,
        prompt: str,
        model: str,
        columns_subset: str | list[str] | None = None,
        batch_size: int = 1000,
        max_concurrent: int = 3,
        pre: Callable | None = None,
        segments: SegmentSpec | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate rows using AI/LLM-powered analysis.

        The `prompt()` validation method uses Large Language Models (LLMs) to validate rows of data
        based on natural language criteria. Similar to other Pointblank validation methods, this
        generates binary test results (pass/fail) that integrate seamlessly with the standard
        reporting framework.

        Like `col_vals_*()` methods, `prompt()` evaluates data against specific criteria, but
        instead of using programmatic rules, it uses natural language prompts interpreted by an LLM.
        Like `rows_distinct()` and `rows_complete()`, it operates at the row level and allows you to
        specify a subset of columns for evaluation using `columns_subset=`.

        The system automatically combines your validation criteria from the `prompt=` parameter with
        the necessary technical context, data formatting instructions, and response structure
        requirements. This is all so you only need to focus on describing your validation logic in
        plain language.

        Each row becomes a test unit that either passes or fails the validation criteria, producing
        the familiar True/False results that appear in Pointblank validation reports. This method
        is particularly useful for complex validation rules that are difficult to express with
        traditional validation methods, such as semantic checks, context-dependent validation, or
        subjective quality assessments.

        Parameters
        ----------
        prompt
            A natural language description of the validation criteria. This prompt should clearly
            describe what constitutes valid vs invalid rows. Some examples:
            `"Each row should contain a valid email address and a realistic person name"`,
            `"Values should indicate positive sentiment"`,
            `"The description should mention a country name"`.
        columns_subset
            A single column or list of columns to include in the validation. If `None`, all columns
            will be included. Specifying fewer columns can improve performance and reduce API costs
            so try to include only the columns necessary for the validation.
        model
            The model to be used. This should be in the form of `provider:model` (e.g.,
            `"anthropic:claude-3-5-sonnet-latest"`). Supported providers are `"anthropic"`,
            `"openai"`, `"ollama"`, and `"bedrock"`. The model name should be the specific model to
            be used from the provider. Model names are subject to change so consult the provider's
            documentation for the most up-to-date model names.
        batch_size
            Number of rows to process in each batch. Larger batches are more efficient but may hit
            API limits. Default is `1000`.
        max_concurrent
            Maximum number of concurrent API requests. Higher values speed up processing but may
            hit rate limits. Default is `3`.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
        segments
            An optional directive on segmentation, which serves to split a validation step into
            multiple (one step per segment). Can be a single column name, a tuple that specifies a
            column name and its corresponding values to segment on, or a combination of both
            (provided as a list).
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Constructing the `model` Argument
        ---------------------------------
        The `model=` argument should be constructed using the provider and model name separated by a
        colon (`provider:model`). The provider text can any of:

        - `"anthropic"` (Anthropic)
        - `"openai"` (OpenAI)
        - `"ollama"` (Ollama)
        - `"bedrock"` (Amazon Bedrock)

        The model name should be the specific model to be used from the provider. Model names are
        subject to change so consult the provider's documentation for the most up-to-date model
        names.

        Notes on Authentication
        -----------------------
        API keys are automatically loaded from environment variables or `.env` files and are **not**
        stored in the validation object for security reasons. You should consider using a secure
        method for handling API keys.

        One way to do this is to load the API key from an environment variable and retrieve it using
        the `os` module (specifically the `os.getenv()` function). Places to store the API key might
        include `.bashrc`, `.bash_profile`, `.zshrc`, or `.zsh_profile`.

        Another solution is to store one or more model provider API keys in an `.env` file (in the
        root of your project). If the API keys have correct names (e.g., `ANTHROPIC_API_KEY` or
        `OPENAI_API_KEY`) then the AI validation will automatically load the API key from the `.env`
        file. An `.env` file might look like this:

        ```plaintext
        ANTHROPIC_API_KEY="your_anthropic_api_key_here"
        OPENAI_API_KEY="your_openai_api_key_here"
        ```

        There's no need to have the `python-dotenv` package installed when using `.env` files in
        this way.

        **Provider-specific setup**:

        - **OpenAI**: set `OPENAI_API_KEY` environment variable or create `.env` file
        - **Anthropic**: set `ANTHROPIC_API_KEY` environment variable or create `.env` file
        - **Ollama**: no API key required, just ensure Ollama is running locally
        - **Bedrock**: configure AWS credentials through standard AWS methods

        AI Validation Process
        ---------------------
        The AI validation process works as follows:

        1. data batching: the data is split into batches of the specified size
        2. row deduplication: duplicate rows (based on selected columns) are identified and only
        unique combinations are sent to the LLM for analysis
        3. json conversion: each batch of unique rows is converted to JSON format for the LLM
        4. prompt construction: the user prompt is embedded in a structured system prompt
        5. llm processing: each batch is sent to the LLM for analysis
        6. response parsing: LLM responses are parsed to extract validation results
        7. result projection: results are mapped back to all original rows using row signatures
        8. result aggregation: results from all batches are combined

        **Performance Optimization**: the process uses row signature memoization to avoid redundant
        LLM calls. When multiple rows have identical values in the selected columns, only one
        representative row is validated, and the result is applied to all matching rows. This can
        dramatically reduce API costs and processing time for datasets with repetitive patterns.

        The LLM receives data in this JSON format:

        ```json
        {
          "columns": ["col1", "col2", "col3"],
          "rows": [
            {"col1": "value1", "col2": "value2", "col3": "value3", "_pb_row_index": 0},
            {"col1": "value4", "col2": "value5", "col3": "value6", "_pb_row_index": 1}
          ]
        }
        ```

        The LLM returns validation results in this format:
        ```json
        [
          {"index": 0, "result": true},
          {"index": 1, "result": false}
        ]
        ```

        Prompt Design Tips
        ------------------
        For best results, design prompts that are:

        - boolean-oriented: frame validation criteria to elicit clear valid/invalid responses
        - specific: clearly define what makes a row valid/invalid
        - unambiguous: avoid subjective language that could be interpreted differently
        - context-aware: include relevant business rules or domain knowledge
        - example-driven: consider providing examples in the prompt when helpful

        **Critical**: Prompts must be designed so the LLM can determine whether each row passes or
        fails the validation criteria. The system expects binary validation responses, so avoid
        open-ended questions or prompts that might generate explanatory text instead of clear
        pass/fail judgments.

        Good prompt examples:

        - "Each row should contain a valid email address in the 'email' column and a non-empty name
        in the 'name' column"
        - "The 'sentiment' column should contain positive sentiment words (happy, good, excellent,
        etc.)"
        - "Product descriptions should mention at least one technical specification"

        Poor prompt examples (avoid these):

        - "What do you think about this data?" (too open-ended)
        - "Describe the quality of each row" (asks for description, not validation)
        - "How would you improve this data?" (asks for suggestions, not pass/fail)

        Provider Setup
        --------------
        **OpenAI**: Set `OPENAI_API_KEY` environment variable or create `.env` file.
        **Anthropic**: Set `ANTHROPIC_API_KEY` environment variable or create `.env` file.
        **Ollama**: Ensure Ollama is running locally (default: http://localhost:11434).
        **Bedrock**: Configure AWS credentials and region.

        Performance Considerations
        --------------------------
        AI validation is significantly slower than traditional validation methods due to API calls
        to LLM providers. However, performance varies dramatically based on data characteristics:

        **High Memoization Scenarios** (seconds to minutes):

        - data with many duplicate rows in the selected columns
        - low cardinality data (repeated patterns)
        - small number of unique row combinations

        **Low Memoization Scenarios** (minutes to hours):

        - high cardinality data with mostly unique rows
        - large datasets with few repeated patterns
        - all or most rows requiring individual LLM evaluation

        The row signature memoization optimization can reduce processing time significantly when
        data has repetitive patterns. For datasets where every row is unique, expect longer
        processing times similar to validating each row individually.

        **Strategies to Reduce Processing Time**:

        - test on data slices: define a sampling function like `def sample_1000(df): return df.head(1000)`
        and use `pre=sample_1000` to validate on smaller samples
        - filter relevant data: define filter functions like `def active_only(df): return df.filter(df["status"] == "active")`
        and use `pre=active_only` to focus on a specific subset
        - optimize column selection: use `columns_subset=` to include only the columns necessary
        for validation
        - start with smaller batches: begin with `batch_size=100` for testing, then increase
        gradually
        - reduce concurrency: lower `max_concurrent=1` if hitting rate limits
        - use faster/cheaper models: consider using smaller or more efficient models for initial
        testing before switching to more capable models

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        The following examples demonstrate how to use AI validation for different types of data
        quality checks. These examples show both basic usage and more advanced configurations with
        custom thresholds and actions.

        **Basic AI validation example:**

        This first example shows a simple validation scenario where we want to check that customer
        records have both valid email addresses and non-empty names. Notice how we use
        `columns_subset=` to focus only on the relevant columns, which improves both performance
        and cost-effectiveness.

        ```python
        import pointblank as pb
        import polars as pl

        # Sample data with email and name columns
        tbl = pl.DataFrame({
            "email": ["john@example.com", "invalid-email", "jane@test.org"],
            "name": ["John Doe", "", "Jane Smith"],
            "age": [25, 30, 35]
        })

        # Validate using AI
        validation = (
            pb.Validate(data=tbl)
            .prompt(
                prompt="Each row should have a valid email address and a non-empty name",
                columns_subset=["email", "name"],  # Only check these columns
                model="openai:gpt-4o-mini",
            )
            .interrogate()
        )

        validation
        ```

        In this example, the AI will identify that the second row fails validation because it has
        an invalid email format (`"invalid-email"`) and the third row also fails because it has an
        empty name field. The validation results will show 2 out of 3 rows failing the criteria.

        **Advanced example with custom thresholds:**

        This more sophisticated example demonstrates how to use AI validation with custom thresholds
        and actions. Here we're validating phone number formats to ensure they include area codes,
        which is a common data quality requirement for customer contact information.

        ```python
        customer_data = pl.DataFrame({
            "customer_id": [1, 2, 3, 4, 5],
            "name": ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Davis"],
            "phone_number": [
                "(555) 123-4567",  # Valid with area code
                "555-987-6543",    # Valid with area code
                "123-4567",        # Missing area code
                "(800) 555-1234",  # Valid with area code
                "987-6543"         # Missing area code
            ]
        })

        validation = (
            pb.Validate(data=customer_data)
            .prompt(
                prompt="Do all the phone numbers include an area code?",
                columns_subset="phone_number",  # Only check the `phone_number` column
                model="openai:gpt-4o",
                batch_size=500,
                max_concurrent=5,
                thresholds=pb.Thresholds(warning=0.1, error=0.2, critical=0.3),
                actions=pb.Actions(error="Too many phone numbers missing area codes.")
            )
            .interrogate()
        )
        ```

        This validation will identify that 2 out of 5 phone numbers (40%) are missing area codes,
        which exceeds all threshold levels. The validation will trigger the specified error action
        since the failure rate (40%) is above the error threshold (20%). The AI can recognize
        various phone number formats and determine whether they include area codes.
        """

        assertion_type = _get_fn_name()

        # Validation of inputs
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        # Parse the provider and model name from the `model=` argument
        try:
            provider, model_name = model.split(sep=":", maxsplit=1)
        except ValueError:
            raise ValueError(f"Model must be in format 'provider:model_name', got: {model}")

        # Error if an unsupported provider is used
        if provider not in MODEL_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. Supported providers are {MODEL_PROVIDERS}."
            )

        # Ensure that `batch_size` and `max_concurrent` are positive integers
        if not isinstance(batch_size, int) or batch_size < 1:
            raise ValueError("batch_size must be a positive integer")
        if not isinstance(max_concurrent, int) or max_concurrent < 1:
            raise ValueError("max_concurrent must be a positive integer")

        _check_pre(pre=pre)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Promote a single column given as a string to a list
        if columns_subset is not None and isinstance(columns_subset, str):
            columns_subset = [columns_subset]

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Package up the AI-specific parameters as a dictionary for later use
        ai_config = {
            "prompt": prompt,
            "llm_provider": provider,
            "llm_model": model_name,
            "batch_size": batch_size,
            "max_concurrent": max_concurrent,
        }

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            column=columns_subset,
            values=ai_config,
            pre=pre,
            segments=segments,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def col_schema_match(
        self,
        schema: Schema,
        complete: bool = True,
        in_order: bool = True,
        case_sensitive_colnames: bool = True,
        case_sensitive_dtypes: bool = True,
        full_match_dtypes: bool = True,
        pre: Callable | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Do columns in the table (and their types) match a predefined schema?

        The `col_schema_match()` method works in conjunction with an object generated by the
        [`Schema`](`pointblank.Schema`) class. That class object is the expectation for the actual
        schema of the target table. The validation step operates over a single test unit, which is
        whether the schema matches that of the table (within the constraints enforced by the
        `complete=`, and `in_order=` options).

        Parameters
        ----------
        schema
            A `Schema` object that represents the expected schema of the table. This object is
            generated by the [`Schema`](`pointblank.Schema`) class.
        complete
            Should the schema match be complete? If `True`, then the target table must have all
            columns specified in the schema. If `False`, then the table can have additional columns
            not in the schema (i.e., the schema is a subset of the target table's columns).
        in_order
            Should the schema match be in order? If `True`, then the columns in the schema must
            appear in the same order as they do in the target table. If `False`, then the order of
            columns in the schema and the target table can differ.
        case_sensitive_colnames
            Should the schema match be case-sensitive with regard to column names? If `True`, then
            the column names in the schema and the target table must match exactly. If `False`, then
            the column names are compared in a case-insensitive manner.
        case_sensitive_dtypes
            Should the schema match be case-sensitive with regard to column data types? If `True`,
            then the column data types in the schema and the target table must match exactly. If
            `False`, then the column data types are compared in a case-insensitive manner.
        full_match_dtypes
            Should the schema match require a full match of data types? If `True`, then the column
            data types in the schema and the target table must match exactly. If `False` then
            substring matches are allowed, so a schema data type of `Int` would match a target table
            data type of `Int64`.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. Regarding the lifetime of the transformed table, it only exists during the
        validation step and is not stored in the `Validate` object or used in subsequent validation
        steps.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```

        For the examples here, we'll use a simple Polars DataFrame with three columns (string,
        integer, and float). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": ["apple", "banana", "cherry", "date"],
                "b": [1, 6, 3, 5],
                "c": [1.1, 2.2, 3.3, 4.4],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that the columns in the table match a predefined schema. A schema can be
        defined using the [`Schema`](`pointblank.Schema`) class.

        ```{python}
        schema = pb.Schema(
            columns=[("a", "String"), ("b", "Int64"), ("c", "Float64")]
        )
        ```

        You can print the schema object to verify that the expected schema is as intended.

        ```{python}
        print(schema)
        ```

        Now, we'll use the `col_schema_match()` method to validate the table against the expected
        `schema` object. There is a single test unit for this validation step (whether the schema
        matches the table or not).

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .col_schema_match(schema=schema)
            .interrogate()
        )

        validation
        ```

        The validation table shows that the schema matches the table. The single test unit passed
        since the table columns and their types match the schema.
        """

        assertion_type = _get_fn_name()

        _check_pre(pre=pre)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")
        _check_boolean_input(param=complete, param_name="complete")
        _check_boolean_input(param=in_order, param_name="in_order")
        _check_boolean_input(param=case_sensitive_colnames, param_name="case_sensitive_colnames")
        _check_boolean_input(param=case_sensitive_dtypes, param_name="case_sensitive_dtypes")
        _check_boolean_input(param=full_match_dtypes, param_name="full_match_dtypes")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # Package up the `schema=` and boolean params into a dictionary for later interrogation
        values = {
            "schema": schema,
            "complete": complete,
            "in_order": in_order,
            "case_sensitive_colnames": case_sensitive_colnames,
            "case_sensitive_dtypes": case_sensitive_dtypes,
            "full_match_dtypes": full_match_dtypes,
        }

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            values=values,
            pre=pre,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def row_count_match(
        self,
        count: int | FrameT | Any,
        tol: Tolerance = 0,
        inverse: bool = False,
        pre: Callable | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether the row count of the table matches a specified count.

        The `row_count_match()` method checks whether the row count of the target table matches a
        specified count. This validation will operate over a single test unit, which is whether the
        row count matches the specified count.

        We also have the option to invert the validation step by setting `inverse=True`. This will
        make the expectation that the row count of the target table *does not* match the specified
        count.

        Parameters
        ----------
        count
            The expected row count of the table. This can be an integer value, a Polars or Pandas
            DataFrame object, or an Ibis backend table. If a DataFrame/table is provided, the row
            count of that object will be used as the expected count.
        tol
            The tolerance allowable for the row count match. This can be specified as a single
            numeric value (integer or float) or as a tuple of two integers representing the lower
            and upper bounds of the tolerance range. If a single integer value (greater than 1) is
            provided, it represents the absolute bounds of the tolerance, ie. plus or minus the value.
            If a float value (between 0-1) is provided, it represents the relative tolerance, ie.
            plus or minus the relative percentage of the target. If a tuple is provided, it represents
            the lower and upper absolute bounds of the tolerance range. See the examples for more.
        inverse
            Should the validation step be inverted? If `True`, then the expectation is that the row
            count of the target table should not match the specified `count=` value.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Regarding the lifetime of the
        transformed table, it only exists during the validation step and is not stored in the
        `Validate` object or used in subsequent validation steps.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False)
        ```

        For the examples here, we'll use the built in dataset `"small_table"`. The table can be
        obtained by calling `load_dataset("small_table")`.

        ```{python}
        import pointblank as pb

        small_table = pb.load_dataset("small_table")

        pb.preview(small_table)
        ```

        Let's validate that the number of rows in the table matches a fixed value. In this case, we
        will use the value `13` as the expected row count.

        ```{python}
        validation = (
            pb.Validate(data=small_table)
            .row_count_match(count=13)
            .interrogate()
        )

        validation
        ```

        The validation table shows that the expectation value of `13` matches the actual count of
        rows in the target table. So, the single test unit passed.


        Let's modify our example to show the different ways we can allow some tolerance to our validation
        by using the `tol` argument.

        ```{python}
        smaller_small_table = small_table.sample(n = 12) # within the lower bound
        validation = (
            pb.Validate(data=smaller_small_table)
            .row_count_match(count=13,tol=(2, 0)) # minus 2 but plus 0, ie. 11-13
            .interrogate()
        )

        validation

        validation = (
            pb.Validate(data=smaller_small_table)
            .row_count_match(count=13,tol=.05) # .05% tolerance of 13
            .interrogate()
        )

        even_smaller_table = small_table.sample(n = 2)
        validation = (
            pb.Validate(data=even_smaller_table)
            .row_count_match(count=13,tol=5) # plus or minus 5; this test will fail
            .interrogate()
        )

        validation
        ```

        """

        assertion_type = _get_fn_name()

        _check_pre(pre=pre)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")
        _check_boolean_input(param=inverse, param_name="inverse")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `count` is a DataFrame or table then use the row count of the DataFrame as
        # the expected count
        if _is_value_a_df(count) or "ibis.expr.types.relations.Table" in str(type(count)):
            count = get_row_count(count)

        # Check the integrity of tolerance
        bounds: AbsoluteBounds = _derive_bounds(ref=int(count), tol=tol)

        # Package up the `count=` and boolean params into a dictionary for later interrogation
        values = {"count": count, "inverse": inverse, "abs_tol_bounds": bounds}

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            values=values,
            pre=pre,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def col_count_match(
        self,
        count: int | FrameT | Any,
        inverse: bool = False,
        pre: Callable | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Validate whether the column count of the table matches a specified count.

        The `col_count_match()` method checks whether the column count of the target table matches a
        specified count. This validation will operate over a single test unit, which is whether the
        column count matches the specified count.

        We also have the option to invert the validation step by setting `inverse=True`. This will
        make the expectation that column row count of the target table *does not* match the
        specified count.

        Parameters
        ----------
        count
            The expected column count of the table. This can be an integer value, a Polars or Pandas
            DataFrame object, or an Ibis backend table. If a DataFrame/table is provided, the column
            count of that object will be used as the expected count.
        inverse
            Should the validation step be inverted? If `True`, then the expectation is that the
            column count of the target table should not match the specified `count=` value.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Regarding the lifetime of the
        transformed table, it only exists during the validation step and is not stored in the
        `Validate` object or used in subsequent validation steps.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False)
        ```

        For the examples here, we'll use the built in dataset `"game_revenue"`. The table can be
        obtained by calling `load_dataset("game_revenue")`.

        ```{python}
        import pointblank as pb

        game_revenue = pb.load_dataset("game_revenue")

        pb.preview(game_revenue)
        ```

        Let's validate that the number of columns in the table matches a fixed value. In this case,
        we will use the value `11` as the expected column count.

        ```{python}
        validation = (
            pb.Validate(data=game_revenue)
            .col_count_match(count=11)
            .interrogate()
        )

        validation
        ```

        The validation table shows that the expectation value of `11` matches the actual count of
        columns in the target table. So, the single test unit passed.
        """

        assertion_type = _get_fn_name()

        _check_pre(pre=pre)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")
        _check_boolean_input(param=inverse, param_name="inverse")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # If `count` is a DataFrame or table then use the column count of the DataFrame as
        # the expected count
        if _is_value_a_df(count) or "ibis.expr.types.relations.Table" in str(type(count)):
            count = get_column_count(count)

        # Package up the `count=` and boolean params into a dictionary for later interrogation
        values = {"count": count, "inverse": inverse}

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            values=values,
            pre=pre,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def conjointly(
        self,
        *exprs: Callable,
        pre: Callable | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Perform multiple row-wise validations for joint validity.

        The `conjointly()` validation method checks whether each row in the table passes multiple
        validation conditions simultaneously. This enables compound validation logic where a test
        unit (typically a row) must satisfy all specified conditions to pass the validation.

        This method accepts multiple validation expressions as callables, which should return
        boolean expressions when applied to the data. You can use lambdas that incorporate
        Polars/Pandas/Ibis expressions (based on the target table type) or create more complex
        validation functions. The validation will operate over the number of test units that is
        equal to the number of rows in the table (determined after any `pre=` mutation has been
        applied).

        Parameters
        ----------
        *exprs
            Multiple validation expressions provided as callable functions. Each callable should
            accept a table as its single argument and return a boolean expression or Series/Column
            that evaluates to boolean values for each row.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Regarding the lifetime of the
        transformed table, it only exists during the validation step and is not stored in the
        `Validate` object or used in subsequent validation steps.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        For the examples here, we'll use a simple Polars DataFrame with three numeric columns (`a`,
        `b`, and `c`). The table is shown below:

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 7, 1, 3, 9, 4],
                "b": [6, 3, 0, 5, 8, 2],
                "c": [10, 4, 8, 9, 10, 5],
            }
        )

        pb.preview(tbl)
        ```

        Let's validate that the values in each row satisfy multiple conditions simultaneously:

        1. Column `a` should be greater than 2
        2. Column `b` should be less than 7
        3. The sum of `a` and `b` should be less than the value in column `c`

        We'll use `conjointly()` to check all these conditions together:

        ```{python}
        validation = (
            pb.Validate(data=tbl)
            .conjointly(
                lambda df: pl.col("a") > 2,
                lambda df: pl.col("b") < 7,
                lambda df: pl.col("a") + pl.col("b") < pl.col("c")
            )
            .interrogate()
        )

        validation
        ```

        The validation table shows that not all rows satisfy all three conditions together. For a
        row to pass the conjoint validation, all three conditions must be true for that row.

        We can also use preprocessing to filter the data before applying the conjoint validation:

        ```{python}
        # Define preprocessing function for serialization compatibility
        def filter_by_c_gt_5(df):
            return df.filter(pl.col("c") > 5)

        validation = (
            pb.Validate(data=tbl)
            .conjointly(
                lambda df: pl.col("a") > 2,
                lambda df: pl.col("b") < 7,
                lambda df: pl.col("a") + pl.col("b") < pl.col("c"),
                pre=filter_by_c_gt_5
            )
            .interrogate()
        )

        validation
        ```

        This allows for more complex validation scenarios where the data is first prepared and then
        validated against multiple conditions simultaneously.

        Or, you can use the backend-agnostic column expression helper
        [`expr_col()`](`pointblank.expr_col`) to write expressions that work across different table
        backends:

        ```{python}
        tbl = pl.DataFrame(
            {
                "a": [5, 7, 1, 3, 9, 4],
                "b": [6, 3, 0, 5, 8, 2],
                "c": [10, 4, 8, 9, 10, 5],
            }
        )

        # Using backend-agnostic syntax with expr_col()
        validation = (
            pb.Validate(data=tbl)
            .conjointly(
                lambda df: pb.expr_col("a") > 2,
                lambda df: pb.expr_col("b") < 7,
                lambda df: pb.expr_col("a") + pb.expr_col("b") < pb.expr_col("c")
            )
            .interrogate()
        )

        validation
        ```

        Using [`expr_col()`](`pointblank.expr_col`) allows your validation code to work consistently
        across Pandas, Polars, and Ibis table backends without changes, making your validation
        pipelines more portable.

        See Also
        --------
        Look at the documentation of the [`expr_col()`](`pointblank.expr_col`) function for more
        information on how to use it with different table backends.
        """

        assertion_type = _get_fn_name()

        if len(exprs) == 0:
            raise ValueError("At least one validation expression must be provided")

        _check_pre(pre=pre)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        # Package the validation expressions for later evaluation
        values = {"expressions": exprs}

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            column=None,  # This validation is not specific to any column(s)
            values=values,
            pre=pre,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def specially(
        self,
        expr: Callable,
        pre: Callable | None = None,
        thresholds: int | float | bool | tuple | dict | Thresholds = None,
        actions: Actions | None = None,
        brief: str | bool | None = None,
        active: bool = True,
    ) -> Validate:
        """
        Perform a specialized validation with customized logic.

        The `specially()` validation method allows for the creation of specialized validation
        expressions that can be used to validate specific conditions or logic in the data. This
        method provides maximum flexibility by accepting a custom callable that encapsulates
        your validation logic.

        The callable function can have one of two signatures:

        - a function accepting a single parameter (the data table): `def validate(data): ...`
        - a function with no parameters: `def validate(): ...`

        The second form is particularly useful for environment validations that don't need to
        inspect the data table.

        The callable function must ultimately return one of:

        1. a single boolean value or boolean list
        2. a table where the final column contains boolean values (column name is unimportant)

        The validation will operate over the number of test units that is equal to the number of
        rows in the data table (if returning a table with boolean values). If returning a scalar
        boolean value, the validation will operate over a single test unit. For a return of a list
        of boolean values, the length of the list constitutes the number of test units.

        Parameters
        ----------
        expr
            A callable function that defines the specialized validation logic. This function should:
            (1) accept the target data table as its single argument (though it may ignore it), or
            (2) take no parameters at all (for environment validations). The function must
            ultimately return boolean values representing validation results. Design your function
            to incorporate any custom parameters directly within the function itself using closure
            variables or default parameters.
        pre
            An optional preprocessing function or lambda to apply to the data table during
            interrogation. This function should take a table as input and return a modified table.
            Have a look at the *Preprocessing* section for more information on how to use this
            argument.
        thresholds
            Set threshold failure levels for reporting and reacting to exceedences of the levels.
            The thresholds are set at the step level and will override any global thresholds set in
            `Validate(thresholds=...)`. The default is `None`, which means that no thresholds will
            be set locally and global thresholds (if any) will take effect. Look at the *Thresholds*
            section for information on how to set threshold levels.
        actions
            Optional actions to take when the validation step meets or exceeds any set threshold
            levels. If provided, the [`Actions`](`pointblank.Actions`) class should be used to
            define the actions.
        brief
            An optional brief description of the validation step that will be displayed in the
            reporting table. You can use the templating elements like `"{step}"` to insert
            the step number, or `"{auto}"` to include an automatically generated brief. If `True`
            the entire brief will be automatically generated. If `None` (the default) then there
            won't be a brief.
        active
            A boolean value indicating whether the validation step should be active. Using `False`
            will make the validation step inactive (still reporting its presence and keeping indexes
            for the steps unchanged).

        Returns
        -------
        Validate
            The `Validate` object with the added validation step.

        Preprocessing
        -------------
        The `pre=` argument allows for a preprocessing function or lambda to be applied to the data
        table during interrogation. This function should take a table as input and return a modified
        table. This is useful for performing any necessary transformations or filtering on the data
        before the validation step is applied.

        The preprocessing function can be any callable that takes a table as input and returns a
        modified table. For example, you could use a lambda function to filter the table based on
        certain criteria or to apply a transformation to the data. Regarding the lifetime of the
        transformed table, it only exists during the validation step and is not stored in the
        `Validate` object or used in subsequent validation steps.

        Thresholds
        ----------
        The `thresholds=` parameter is used to set the failure-condition levels for the validation
        step. If they are set here at the step level, these thresholds will override any thresholds
        set at the global level in `Validate(thresholds=...)`.

        There are three threshold levels: 'warning', 'error', and 'critical'. The threshold values
        can either be set as a proportion failing of all test units (a value between `0` to `1`),
        or, the absolute number of failing test units (as integer that's `1` or greater).

        Thresholds can be defined using one of these input schemes:

        1. use the [`Thresholds`](`pointblank.Thresholds`) class (the most direct way to create
        thresholds)
        2. provide a tuple of 1-3 values, where position `0` is the 'warning' level, position `1` is
        the 'error' level, and position `2` is the 'critical' level
        3. create a dictionary of 1-3 value entries; the valid keys: are 'warning', 'error', and
        'critical'
        4. a single integer/float value denoting absolute number or fraction of failing test units
        for the 'warning' level only

        If the number of failing test units exceeds set thresholds, the validation step will be
        marked as 'warning', 'error', or 'critical'. All of the threshold levels don't need to be
        set, you're free to set any combination of them.

        Aside from reporting failure conditions, thresholds can be used to determine the actions to
        take for each level of failure (using the `actions=` parameter).

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        The `specially()` method offers maximum flexibility for validation, allowing you to create
        custom validation logic that fits your specific needs. The following examples demonstrate
        different patterns and use cases for this powerful validation approach.

        ### Simple validation with direct table access

        This example shows the most straightforward use case where we create a function that
        directly checks if the sum of two columns is positive.

        ```{python}
        import pointblank as pb
        import polars as pl

        simple_tbl = pl.DataFrame({
            "a": [5, 7, 1, 3, 9, 4],
            "b": [6, 3, 0, 5, 8, 2]
        })

        # Simple function that validates directly on the table
        def validate_sum_positive(data):
            return data.select(pl.col("a") + pl.col("b") > 0)

        (
            pb.Validate(data=simple_tbl)
            .specially(expr=validate_sum_positive)
            .interrogate()
        )
        ```

        The function returns a Polars DataFrame with a single boolean column indicating whether
        the sum of columns `a` and `b` is positive for each row. Each row in the resulting DataFrame
        is a distinct test unit. This pattern works well for simple validations where you don't need
        configurable parameters.

        ### Advanced validation with closure variables for parameters

        When you need to make your validation configurable, you can use the function factory pattern
        (also known as closures) to create parameterized validations:

        ```{python}
        # Create a parameterized validation function using closures
        def make_column_ratio_validator(col1, col2, min_ratio):
            def validate_column_ratio(data):
                return data.select((pl.col(col1) / pl.col(col2)) > min_ratio)
            return validate_column_ratio

        (
            pb.Validate(data=simple_tbl)
            .specially(
                expr=make_column_ratio_validator(col1="a", col2="b", min_ratio=0.5)
            )
            .interrogate()
        )
        ```

        This approach allows you to create reusable validation functions that can be configured with
        different parameters without modifying the function itself.

        ### Validation function returning a list of booleans

        This example demonstrates how to create a validation function that returns a list of boolean
        values, where each element represents a separate test unit:

        ```{python}
        import pointblank as pb
        import polars as pl
        import random

        # Create sample data
        transaction_tbl = pl.DataFrame({
            "transaction_id": [f"TX{i:04d}" for i in range(1, 11)],
            "amount": [120.50, 85.25, 50.00, 240.75, 35.20, 150.00, 85.25, 65.00, 210.75, 90.50],
            "category": ["food", "shopping", "entertainment", "travel", "utilities",
                        "food", "shopping", "entertainment", "travel", "utilities"]
        })

        # Define a validation function that returns a list of booleans
        def validate_transaction_rules(data):
            # Create a list to store individual test results
            test_results = []

            # Check each row individually against multiple business rules
            for row in data.iter_rows(named=True):
                # Rule: transaction IDs must start with "TX" and be 6 chars long
                valid_id = row["transaction_id"].startswith("TX") and len(row["transaction_id"]) == 6

                # Rule: Amounts must be appropriate for their category
                valid_amount = True
                if row["category"] == "food" and (row["amount"] < 10 or row["amount"] > 200):
                    valid_amount = False
                elif row["category"] == "utilities" and (row["amount"] < 20 or row["amount"] > 300):
                    valid_amount = False
                elif row["category"] == "entertainment" and row["amount"] > 100:
                    valid_amount = False

                # A transaction passes if it satisfies both rules
                test_results.append(valid_id and valid_amount)

            return test_results

        (
            pb.Validate(data=transaction_tbl)
            .specially(
                expr=validate_transaction_rules,
                brief="Validate transaction IDs and amounts by category."
            )
            .interrogate()
        )
        ```

        This example shows how to create a validation function that applies multiple business rules
        to each row and returns a list of boolean results. Each boolean in the list represents a
        separate test unit, and a test unit passes only if all rules are satisfied for a given row.

        The function iterates through each row in the data table, checking:

        1. if transaction IDs follow the required format
        2. if transaction amounts are appropriate for their respective categories

        This approach is powerful when you need to apply complex, conditional logic that can't be
        easily expressed using the built-in validation functions.

        ### Table-level validation returning a single boolean

        Sometimes you need to validate properties of the entire table rather than row-by-row. In
        these cases, your function can return a single boolean value:

        ```{python}
        def validate_table_properties(data):
            # Check if table has at least one row with column 'a' > 10
            has_large_values = data.filter(pl.col("a") > 10).height > 0

            # Check if mean of column 'b' is positive
            has_positive_mean = data.select(pl.mean("b")).item() > 0

            # Return a single boolean for the entire table
            return has_large_values and has_positive_mean

        (
            pb.Validate(data=simple_tbl)
            .specially(expr=validate_table_properties)
            .interrogate()
        )
        ```

        This example demonstrates how to perform multiple checks on the table as a whole and combine
        them into a single validation result.

        ### Environment validation that doesn't use the data table

        The `specially()` validation method can even be used to validate aspects of your environment
        that are completely independent of the data:

        ```{python}
        def validate_pointblank_version():
            try:
                import importlib.metadata
                version = importlib.metadata.version("pointblank")
                version_parts = version.split(".")

                # Get major and minor components regardless of how many parts there are
                major = int(version_parts[0])
                minor = int(version_parts[1])

                # Check both major and minor components for version `0.9+`
                return (major > 0) or (major == 0 and minor >= 9)

            except Exception as e:
                # More specific error handling could be added here
                print(f"Version check failed: {e}")
                return False

        (
            pb.Validate(data=simple_tbl)
            .specially(
                expr=validate_pointblank_version,
                brief="Check Pointblank version `>=0.9.0`."
            )
            .interrogate()
        )
        ```

        This pattern shows how to validate external dependencies or environment conditions as part
        of your validation workflow. Notice that the function doesn't take any parameters at all,
        which makes it cleaner when the validation doesn't need to access the data table.

        By combining these patterns, you can create sophisticated validation workflows that address
        virtually any data quality requirement in your organization.
        """

        assertion_type = _get_fn_name()

        # TODO: add a check for the expression to be a callable
        # _check_expr_specially(expr=expr)
        _check_pre(pre=pre)
        _check_thresholds(thresholds=thresholds)
        _check_boolean_input(param=active, param_name="active")

        # Determine threshold to use (global or local) and normalize a local `thresholds=` value
        thresholds = (
            self.thresholds if thresholds is None else _normalize_thresholds_creation(thresholds)
        )

        # Determine brief to use (global or local) and transform any shorthands of `brief=`
        brief = self.brief if brief is None else _transform_auto_brief(brief=brief)

        val_info = _ValidationInfo(
            assertion_type=assertion_type,
            column=None,  # This validation is not specific to any column(s)
            values=expr,
            pre=pre,
            thresholds=thresholds,
            actions=actions,
            brief=brief,
            active=active,
        )

        self._add_validation(validation_info=val_info)

        return self

    def interrogate(
        self,
        collect_extracts: bool = True,
        collect_tbl_checked: bool = True,
        get_first_n: int | None = None,
        sample_n: int | None = None,
        sample_frac: int | float | None = None,
        extract_limit: int = 500,
    ) -> Validate:
        """
        Execute each validation step against the table and store the results.

        When a validation plan has been set with a series of validation steps, the interrogation
        process through `interrogate()` should then be invoked. Interrogation will evaluate each
        validation step against the table and store the results.

        The interrogation process will collect extracts of failing rows if the `collect_extracts=`
        option is set to `True` (the default). We can control the number of rows collected using the
        `get_first_n=`, `sample_n=`, and `sample_frac=` options. The `extract_limit=` option will
        enforce a hard limit on the number of rows collected when `collect_extracts=True`.

        After interrogation is complete, the `Validate` object will have gathered information, and
        we can use methods like [`n_passed()`](`pointblank.Validate.n_passed`),
        [`f_failed()`](`pointblank.Validate.f_failed`), etc., to understand how the table performed
        against the validation plan. A visual representation of the validation results can be viewed
        by printing the `Validate` object; this will display the validation table in an HTML viewing
        environment.

        Parameters
        ----------
        collect_extracts
            An option to collect rows of the input table that didn't pass a particular validation
            step. The default is `True` and further options (i.e., `get_first_n=`, `sample_*=`)
            allow for fine control of how these rows are collected.
        collect_tbl_checked
            The processed data frames produced by executing the validation steps is collected and
            stored in the `Validate` object if `collect_tbl_checked=True`. This information is
            necessary for some methods (e.g.,
            [`get_sundered_data()`](`pointblank.Validate.get_sundered_data`)), but it can
            potentially make the object grow to a large size. To opt out of attaching this data, set
            this to `False`.
        get_first_n
            If the option to collect rows where test units is chosen, there is the option here to
            collect the first `n` rows. Supply an integer number of rows to extract from the top of
            subset table containing non-passing rows (the ordering of data from the original table
            is retained).
        sample_n
            If the option to collect non-passing rows is chosen, this option allows for the
            sampling of `n` rows. Supply an integer number of rows to sample from the subset table.
            If `n` happens to be greater than the number of non-passing rows, then all such rows
            will be returned.
        sample_frac
            If the option to collect non-passing rows is chosen, this option allows for the sampling
            of a fraction of those rows. Provide a number in the range of `0` and `1`. The number of
            rows to return could be very large, however, the `extract_limit=` option will apply a
            hard limit to the returned rows.
        extract_limit
            A value that limits the possible number of rows returned when extracting non-passing
            rows. The default is `500` rows. This limit is applied after any sampling or limiting
            options are applied. If the number of rows to be returned is greater than this limit,
            then the number of rows returned will be limited to this value. This is useful for
            preventing the collection of too many rows when the number of non-passing rows is very
            large.

        Returns
        -------
        Validate
            The `Validate` object with the results of the interrogation.

        Examples
        --------
        Let's use a built-in dataset (`"game_revenue"`) to demonstrate some of the options of the
        interrogation process. A series of validation steps will populate our validation plan. After
        setting up the plan, the next step is to interrogate the table and see how well it aligns
        with our expectations. We'll use the `get_first_n=` option so that any extracts of failing
        rows are limited to the first `n` rows.

        ```{python}
        import pointblank as pb
        import polars as pl

        validation = (
            pb.Validate(data=pb.load_dataset(dataset="game_revenue"))
            .col_vals_lt(columns="item_revenue", value=200)
            .col_vals_gt(columns="item_revenue", value=0)
            .col_vals_gt(columns="session_duration", value=5)
            .col_vals_in_set(columns="item_type", set=["iap", "ad"])
            .col_vals_regex(columns="player_id", pattern=r"[A-Z]{12}[0-9]{3}")
        )

        validation.interrogate(get_first_n=10)
        ```

        The validation table shows that step 3 (checking for `session_duration` greater than `5`)
        has 18 failing test units. This means that 18 rows in the table are problematic. We'd like
        to see the rows that failed this validation step and we can do that with the
        [`get_data_extracts()`](`pointblank.Validate.get_data_extracts`) method.

        ```{python}
        pb.preview(validation.get_data_extracts(i=3, frame=True))
        ```

        The [`get_data_extracts()`](`pointblank.Validate.get_data_extracts`) method will return a
        Polars DataFrame here with the first 10 rows that failed the validation step (we passed that
        into the [`preview()`](`pointblank.preview`) function for a better display). There are
        actually 18 rows that failed but we limited the collection of extracts with
        `get_first_n=10`.
        """

        # Raise if `get_first_n` and either or `sample_n` or `sample_frac` arguments are provided
        if get_first_n is not None and (sample_n is not None or sample_frac is not None):
            raise ValueError(
                "The `get_first_n=` argument cannot be provided with the `sample_n=` or "
                "`sample_frac=` arguments."
            )

        # Raise if the `sample_n` and `sample_frac` arguments are both provided
        if sample_n is not None and sample_frac is not None:
            raise ValueError(
                "The `sample_n=` and `sample_frac=` arguments cannot both be provided."
            )

        data_tbl = self.data

        # Determine if the table is a DataFrame or a DB table
        tbl_type = _get_tbl_type(data=data_tbl)

        self.time_start = datetime.datetime.now(datetime.timezone.utc)

        # Expand `validation_info` by evaluating any column expressions in `columns=`
        # (the `_evaluate_column_exprs()` method will eval and expand as needed)
        self._evaluate_column_exprs(validation_info=self.validation_info)

        # Expand `validation_info` by evaluating for any segmentation directives
        # provided in `segments=` (the `_evaluate_segments()` method will eval and expand as needed)
        self._evaluate_segments(validation_info=self.validation_info)

        for validation in self.validation_info:
            # Set the `i` value for the validation step (this is 1-indexed)
            index_value = self.validation_info.index(validation) + 1
            validation.i = index_value

            start_time = datetime.datetime.now(datetime.timezone.utc)

            assertion_type = validation.assertion_type
            column = validation.column
            value = validation.values
            inclusive = validation.inclusive
            na_pass = validation.na_pass
            threshold = validation.thresholds
            segment = validation.segments

            # Get compatible data types for this assertion type
            assertion_method = ASSERTION_TYPE_METHOD_MAP[assertion_type]
            compatible_dtypes = COMPATIBLE_DTYPES.get(assertion_method, [])

            # Process the `brief` text for the validation step by including template variables to
            # the user-supplied text
            validation.brief = _process_brief(
                brief=validation.brief,
                step=validation.i,
                col=column,
                values=value,
                thresholds=threshold,
                segment=segment,
            )

            # Generate the autobrief description for the validation step; it's important to perform
            # that here since text components like the column and the value(s) have been resolved
            # at this point
            autobrief = _create_autobrief_or_failure_text(
                assertion_type=assertion_type,
                lang=self.lang,
                column=column,
                values=value,
                for_failure=False,
            )

            validation.autobrief = autobrief

            # ------------------------------------------------
            # Bypassing the validation step if conditions met
            # ------------------------------------------------

            # Skip the validation step if it is not active but still record the time of processing
            if not validation.active:
                end_time = datetime.datetime.now(datetime.timezone.utc)
                validation.proc_duration_s = (end_time - start_time).total_seconds()
                validation.time_processed = end_time.isoformat(timespec="milliseconds")
                continue

            # Skip the validation step if `eval_error` is `True` and record the time of processing
            if validation.eval_error:
                end_time = datetime.datetime.now(datetime.timezone.utc)
                validation.proc_duration_s = (end_time - start_time).total_seconds()
                validation.time_processed = end_time.isoformat(timespec="milliseconds")
                validation.active = False
                continue

            # Make a deep copy of the table for this step to ensure proper isolation
            # This prevents modifications from one validation step affecting others
            data_tbl_step = _copy_dataframe(data_tbl)

            # ------------------------------------------------
            # Preprocessing stage
            # ------------------------------------------------

            # Determine whether any preprocessing functions are to be applied to the table
            if validation.pre is not None:
                try:
                    # Read the text of the preprocessing function
                    pre_text = _pre_processing_funcs_to_str(validation.pre)

                    # Determine if the preprocessing function is a lambda function; return a boolean
                    is_lambda = re.match(r"^lambda", pre_text) is not None

                    # If the preprocessing function is a lambda function, then check if there is
                    # a keyword argument called `dfn` in the lamda signature; if so, that's a cue
                    # to use a Narwhalified version of the table
                    if is_lambda:
                        # Get the signature of the lambda function
                        sig = inspect.signature(validation.pre)

                        # Check if the lambda function has a keyword argument called `dfn`
                        if "dfn" in sig.parameters:
                            # Convert the table to a Narwhals DataFrame
                            data_tbl_step = nw.from_native(data_tbl_step)

                            # Apply the preprocessing function to the table
                            data_tbl_step = validation.pre(dfn=data_tbl_step)

                            # Convert the table back to its original format
                            data_tbl_step = nw.to_native(data_tbl_step)

                        else:
                            # Apply the preprocessing function to the table
                            data_tbl_step = validation.pre(data_tbl_step)

                    # If the preprocessing function is a function, apply it to the table
                    elif isinstance(validation.pre, Callable):
                        data_tbl_step = validation.pre(data_tbl_step)

                except Exception:
                    # If preprocessing fails, mark the validation as having an eval_error
                    validation.eval_error = True
                    end_time = datetime.datetime.now(datetime.timezone.utc)
                    validation.proc_duration_s = (end_time - start_time).total_seconds()
                    validation.time_processed = end_time.isoformat(timespec="milliseconds")
                    validation.active = False
                    continue

            # ------------------------------------------------
            # Segmentation stage
            # ------------------------------------------------

            # Determine whether any segmentation directives are to be applied to the table

            if validation.segments is not None:
                data_tbl_step = _apply_segments(
                    data_tbl=data_tbl_step, segments_expr=validation.segments
                )

            # ------------------------------------------------
            # Determine table type and `collect()` if needed
            # ------------------------------------------------

            if tbl_type not in IBIS_BACKENDS:
                tbl_type = "local"

            # If the table is a lazy frame, we need to collect it
            if _is_lazy_frame(data_tbl_step):
                data_tbl_step = data_tbl_step.collect()

            # ------------------------------------------------
            # Set the number of test units
            # ------------------------------------------------

            validation.n = NumberOfTestUnits(df=data_tbl_step, column=column).get_test_units(
                tbl_type=tbl_type
            )

            # Check if preprocessing or segmentation resulted in zero rows
            # Only apply this check to row-based validations, not table-level validations
            # (table-level validations like row_count_match(), col_count_match(), etc.,
            # operate on the table as a whole, so zero rows is a valid input)
            table_level_assertions = [
                "col_exists",
                "col_schema_match",
                "row_count_match",
                "col_count_match",
            ]

            if validation.n == 0 and assertion_type not in table_level_assertions:
                # Mark the validation as having an eval_error
                validation.eval_error = True
                end_time = datetime.datetime.now(datetime.timezone.utc)
                validation.proc_duration_s = (end_time - start_time).total_seconds()
                validation.time_processed = end_time.isoformat(timespec="milliseconds")
                validation.active = False
                continue

            # ------------------------------------------------
            # Validation stage
            # ------------------------------------------------

            # Apply error handling only to data quality validations, not programming error validations
            if assertion_type != "specially":
                try:
                    # validations requiring `_column_test_prep()`
                    if assertion_type in [
                        "col_vals_gt",
                        "col_vals_lt",
                        "col_vals_eq",
                        "col_vals_ne",
                        "col_vals_ge",
                        "col_vals_le",
                        "col_vals_null",
                        "col_vals_not_null",
                        "col_vals_between",
                        "col_vals_outside",
                        "col_vals_in_set",
                        "col_vals_not_in_set",
                        "col_vals_regex",
                    ]:
                        # Process table for column validation
                        tbl = _column_test_prep(
                            df=data_tbl_step, column=column, allowed_types=compatible_dtypes
                        )

                        if assertion_method == "gt":
                            results_tbl = interrogate_gt(
                                tbl=tbl, column=column, compare=value, na_pass=na_pass
                            )
                        elif assertion_method == "lt":
                            results_tbl = interrogate_lt(
                                tbl=tbl, column=column, compare=value, na_pass=na_pass
                            )
                        elif assertion_method == "eq":
                            results_tbl = interrogate_eq(
                                tbl=tbl, column=column, compare=value, na_pass=na_pass
                            )
                        elif assertion_method == "ne":
                            results_tbl = interrogate_ne(
                                tbl=tbl, column=column, compare=value, na_pass=na_pass
                            )
                        elif assertion_method == "ge":
                            results_tbl = interrogate_ge(
                                tbl=tbl, column=column, compare=value, na_pass=na_pass
                            )
                        elif assertion_method == "le":
                            results_tbl = interrogate_le(
                                tbl=tbl, column=column, compare=value, na_pass=na_pass
                            )
                        elif assertion_method == "null":
                            results_tbl = interrogate_null(tbl=tbl, column=column)
                        elif assertion_method == "not_null":
                            results_tbl = interrogate_not_null(tbl=tbl, column=column)

                        elif assertion_type == "col_vals_between":
                            results_tbl = interrogate_between(
                                tbl=tbl,
                                column=column,
                                low=value[0],
                                high=value[1],
                                inclusive=inclusive,
                                na_pass=na_pass,
                            )

                        elif assertion_type == "col_vals_outside":
                            results_tbl = interrogate_outside(
                                tbl=tbl,
                                column=column,
                                low=value[0],
                                high=value[1],
                                inclusive=inclusive,
                                na_pass=na_pass,
                            )

                        elif assertion_type == "col_vals_in_set":
                            results_tbl = interrogate_isin(tbl=tbl, column=column, set_values=value)

                        elif assertion_type == "col_vals_not_in_set":
                            results_tbl = interrogate_notin(
                                tbl=tbl, column=column, set_values=value
                            )

                        elif assertion_type == "col_vals_regex":
                            results_tbl = interrogate_regex(
                                tbl=tbl, column=column, values=value, na_pass=na_pass
                            )

                    elif assertion_type == "col_vals_expr":
                        results_tbl = col_vals_expr(
                            data_tbl=data_tbl_step, expr=value, tbl_type=tbl_type
                        )

                    elif assertion_type == "rows_distinct":
                        results_tbl = interrogate_rows_distinct(
                            data_tbl=data_tbl_step, columns_subset=column
                        )

                    elif assertion_type == "rows_complete":
                        results_tbl = rows_complete(data_tbl=data_tbl_step, columns_subset=column)

                    elif assertion_type == "prompt":
                        from pointblank._interrogation import interrogate_prompt

                        results_tbl = interrogate_prompt(
                            tbl=data_tbl_step, columns_subset=column, ai_config=value
                        )

                    elif assertion_type == "col_exists":
                        result_bool = col_exists(
                            data_tbl=data_tbl_step,
                            column=column,
                        )

                        validation.all_passed = result_bool
                        validation.n = 1
                        validation.n_passed = int(result_bool)
                        validation.n_failed = 1 - int(result_bool)

                        results_tbl = None

                    elif assertion_type == "col_schema_match":
                        result_bool = col_schema_match(
                            data_tbl=data_tbl_step,
                            schema=value["schema"],
                            complete=value["complete"],
                            in_order=value["in_order"],
                            case_sensitive_colnames=value["case_sensitive_colnames"],
                            case_sensitive_dtypes=value["case_sensitive_dtypes"],
                            full_match_dtypes=value["full_match_dtypes"],
                            threshold=threshold,
                        )

                        schema_validation_info = _get_schema_validation_info(
                            data_tbl=data_tbl,
                            schema=value["schema"],
                            passed=result_bool,
                            complete=value["complete"],
                            in_order=value["in_order"],
                            case_sensitive_colnames=value["case_sensitive_colnames"],
                            case_sensitive_dtypes=value["case_sensitive_dtypes"],
                            full_match_dtypes=value["full_match_dtypes"],
                        )

                        # Add the schema validation info to the validation object
                        validation.val_info = schema_validation_info

                        validation.all_passed = result_bool
                        validation.n = 1
                        validation.n_passed = int(result_bool)
                        validation.n_failed = 1 - result_bool

                        results_tbl = None

                    elif assertion_type == "row_count_match":
                        result_bool = row_count_match(
                            data_tbl=data_tbl_step,
                            count=value["count"],
                            inverse=value["inverse"],
                            abs_tol_bounds=value["abs_tol_bounds"],
                        )

                        validation.all_passed = result_bool
                        validation.n = 1
                        validation.n_passed = int(result_bool)
                        validation.n_failed = 1 - result_bool

                        results_tbl = None

                    elif assertion_type == "col_count_match":
                        result_bool = col_count_match(
                            data_tbl=data_tbl_step, count=value["count"], inverse=value["inverse"]
                        )

                        validation.all_passed = result_bool
                        validation.n = 1
                        validation.n_passed = int(result_bool)
                        validation.n_failed = 1 - result_bool

                        results_tbl = None

                    elif assertion_type == "conjointly":
                        results_tbl = conjointly_validation(
                            data_tbl=data_tbl_step,
                            expressions=value["expressions"],
                            threshold=threshold,
                            tbl_type=tbl_type,
                        )

                    else:
                        raise ValueError(
                            f"Unknown assertion type: {assertion_type}"
                        )  # pragma: no cover

                except Exception as e:
                    # Only catch specific data quality comparison errors, not programming errors
                    error_msg = str(e).lower()
                    is_comparison_error = (
                        "boolean value of na is ambiguous" in error_msg
                        or "cannot compare" in error_msg
                        or (
                            "type" in error_msg
                            and ("mismatch" in error_msg or "incompatible" in error_msg)
                        )
                        or ("dtype" in error_msg and "compare" in error_msg)
                    )

                    if is_comparison_error:  # pragma: no cover
                        # If data quality comparison fails, mark the validation as having an eval_error
                        validation.eval_error = True  # pragma: no cover
                        end_time = datetime.datetime.now(datetime.timezone.utc)  # pragma: no cover
                        validation.proc_duration_s = (
                            end_time - start_time
                        ).total_seconds()  # pragma: no cover
                        validation.time_processed = end_time.isoformat(
                            timespec="milliseconds"
                        )  # pragma: no cover
                        validation.active = False  # pragma: no cover
                        continue  # pragma: no cover
                    else:
                        # For other errors (like missing columns), let them propagate
                        raise

            else:
                # For "specially" validations, let programming errors propagate as exceptions
                if assertion_type == "specially":
                    results_tbl_list = SpeciallyValidation(
                        data_tbl=data_tbl_step,
                        expression=value,
                        threshold=threshold,
                        tbl_type=tbl_type,
                    ).get_test_results()

                    #
                    # The result from this could either be a table in the conventional form, or,
                    # a list of boolean values; handle both cases
                    #

                    if isinstance(results_tbl_list, list):
                        # If the result is a list of boolean values, then we need to convert it to a
                        # set the validation results from the list
                        validation.all_passed = all(results_tbl_list)
                        validation.n = len(results_tbl_list)
                        validation.n_passed = results_tbl_list.count(True)
                        validation.n_failed = results_tbl_list.count(False)

                        results_tbl = None

                    else:
                        # If the result is not a list, then we assume it's a table in the conventional
                        # form (where the column is `pb_is_good_` exists, with boolean values
                        results_tbl = results_tbl_list

            # If the results table is not `None`, then we assume there is a table with a column
            # called `pb_is_good_` that contains boolean values; we can then use this table to
            # determine the number of test units that passed and failed
            if results_tbl is not None:
                # Count the number of passing and failing test units
                validation.n_passed = _count_true_values_in_column(
                    tbl=results_tbl, column="pb_is_good_"
                )
                validation.n_failed = _count_true_values_in_column(
                    tbl=results_tbl, column="pb_is_good_", inverse=True
                )

                # Solely for the col_vals_in_set assertion type, any Null values in the
                # `pb_is_good_` column are counted as failing test units
                if assertion_type == "col_vals_in_set":
                    null_count = _count_null_values_in_column(tbl=results_tbl, column="pb_is_good_")
                    validation.n_failed += null_count

                # For column-value validations, the number of test units is the number of rows
                validation.n = get_row_count(data=results_tbl)

                # Set the `all_passed` attribute based on whether there are any failing test units
                validation.all_passed = validation.n_failed == 0

            # Calculate fractions of passing and failing test units
            # - `f_passed` is the fraction of test units that passed
            # - `f_failed` is the fraction of test units that failed
            for attr in ["passed", "failed"]:
                setattr(
                    validation,
                    f"f_{attr}",
                    _convert_abs_count_to_fraction(
                        value=getattr(validation, f"n_{attr}"), test_units=validation.n
                    ),
                )

            # Determine if the number of failing test units is beyond the threshold value
            # for each of the severity levels
            # - `warning` is the threshold for the 'warning' severity level
            # - `error` is the threshold for 'error' severity level
            # - `critical` is the threshold for the 'critical' severity level
            for level in ["warning", "error", "critical"]:
                setattr(
                    validation,
                    level,
                    threshold._threshold_result(
                        fraction_failing=validation.f_failed, test_units=validation.n, level=level
                    ),
                )

            # If there is any threshold level that has been exceeded, then produce and
            # set the general failure text for the validation step
            if validation.warning or validation.error or validation.critical:
                # Generate failure text for the validation step
                failure_text = _create_autobrief_or_failure_text(
                    assertion_type=assertion_type,
                    lang=self.lang,
                    column=column,
                    values=value,
                    for_failure=True,
                )

                # Set the failure text in the validation step
                validation.failure_text = failure_text

            # Include the results table that has a new column called `pb_is_good_`; that
            # is a boolean column that indicates whether the row passed the validation or not
            if collect_tbl_checked and results_tbl is not None:
                validation.tbl_checked = results_tbl

            # Perform any necessary actions if threshold levels are exceeded for each of
            # the severity levels (in descending order of 'critical', 'error', and 'warning')
            for level in ["critical", "error", "warning"]:
                if getattr(validation, level) and (
                    self.actions is not None or validation.actions is not None
                ):
                    # Translate the severity level to a number
                    level_num = LOG_LEVELS_MAP[level]

                    #
                    # If step-level actions are set, prefer those over actions set globally
                    #

                    if validation.actions is not None:
                        # Action execution on the step level
                        action = validation.actions._get_action(level=level)

                        # If there is no action set for this level, then continue to the next level
                        if action is None:
                            continue

                        # A list of actions is expected here, so iterate over them
                        if isinstance(action, list):
                            for act in action:
                                if isinstance(act, str):
                                    # Process the action string as it may contain template variables
                                    act = _process_action_str(
                                        action_str=act,
                                        step=validation.i,
                                        col=column,
                                        value=value,
                                        type=assertion_type,
                                        time=str(start_time),
                                        level=level,
                                    )

                                    print(act)
                                elif callable(act):
                                    # Expose dictionary of values to the action function
                                    metadata = {
                                        "step": validation.i,
                                        "column": column,
                                        "value": value,
                                        "type": assertion_type,
                                        "time": str(start_time),
                                        "level": level,
                                        "level_num": level_num,
                                        "autobrief": autobrief,
                                        "failure_text": failure_text,
                                    }

                                    # Execute the action within the context manager
                                    with _action_context_manager(metadata):
                                        act()

                        if validation.actions.highest_only:
                            break

                    elif self.actions is not None:
                        # Action execution on the global level
                        action = self.actions._get_action(level=level)
                        if action is None:
                            continue

                        # A list of actions is expected here, so iterate over them
                        if isinstance(action, list):
                            for act in action:
                                if isinstance(act, str):
                                    # Process the action string as it may contain template variables
                                    act = _process_action_str(
                                        action_str=act,
                                        step=validation.i,
                                        col=column,
                                        value=value,
                                        type=assertion_type,
                                        time=str(start_time),
                                        level=level,
                                    )

                                    print(act)
                                elif callable(act):
                                    # Expose dictionary of values to the action function
                                    metadata = {
                                        "step": validation.i,
                                        "column": column,
                                        "value": value,
                                        "type": assertion_type,
                                        "time": str(start_time),
                                        "level": level,
                                        "level_num": level_num,
                                        "autobrief": autobrief,
                                        "failure_text": failure_text,
                                    }

                                    # Execute the action within the context manager
                                    with _action_context_manager(metadata):
                                        act()

                        if self.actions.highest_only:
                            break

            # If this is a row-based validation step, then extract the rows that failed
            # TODO: Add support for extraction of rows for Ibis backends
            if (
                collect_extracts
                and assertion_type
                in ROW_BASED_VALIDATION_TYPES + ["rows_distinct", "rows_complete"]
                and tbl_type not in IBIS_BACKENDS
            ):
                # Add row numbers to the results table
                validation_extract_nw = nw.from_native(results_tbl)

                # Handle LazyFrame row indexing which requires order_by parameter
                try:
                    # Try without order_by first (for DataFrames)
                    validation_extract_nw = validation_extract_nw.with_row_index(name="_row_num_")
                except TypeError:
                    # LazyFrames require order_by parameter: use first column for ordering
                    first_col = validation_extract_nw.columns[0]
                    validation_extract_nw = validation_extract_nw.with_row_index(
                        name="_row_num_", order_by=first_col
                    )

                validation_extract_nw = validation_extract_nw.filter(~nw.col("pb_is_good_")).drop(
                    "pb_is_good_"
                )  # noqa

                # Add 1 to the row numbers to make them 1-indexed
                validation_extract_nw = validation_extract_nw.with_columns(nw.col("_row_num_") + 1)

                # Apply any sampling or limiting to the number of rows to extract
                if get_first_n is not None:
                    validation_extract_nw = validation_extract_nw.head(get_first_n)
                elif sample_n is not None:
                    # Narwhals LazyFrame doesn't have sample method, use head after shuffling
                    try:
                        validation_extract_nw = validation_extract_nw.sample(n=sample_n)
                    except AttributeError:
                        # For LazyFrames without sample method, collect first then sample
                        validation_extract_native = validation_extract_nw.collect().to_native()
                        if hasattr(validation_extract_native, "sample"):  # pragma: no cover
                            # PySpark DataFrame has sample method
                            validation_extract_native = (
                                validation_extract_native.sample(  # pragma: no cover
                                    fraction=min(
                                        1.0, sample_n / validation_extract_native.count()
                                    )  # pragma: no cover
                                ).limit(sample_n)
                            )  # pragma: no cover
                            validation_extract_nw = nw.from_native(
                                validation_extract_native
                            )  # pragma: no cover
                        else:
                            # Fallback: just take first n rows after collecting
                            validation_extract_nw = validation_extract_nw.collect().head(
                                sample_n
                            )  # pragma: no cover
                elif sample_frac is not None:
                    try:
                        validation_extract_nw = validation_extract_nw.sample(fraction=sample_frac)
                    except AttributeError:  # pragma: no cover
                        # For LazyFrames without sample method, collect first then sample
                        validation_extract_native = (
                            validation_extract_nw.collect().to_native()
                        )  # pragma: no cover
                        if hasattr(validation_extract_native, "sample"):  # pragma: no cover
                            # PySpark DataFrame has sample method
                            validation_extract_native = validation_extract_native.sample(
                                fraction=sample_frac
                            )  # pragma: no cover
                            validation_extract_nw = nw.from_native(
                                validation_extract_native
                            )  # pragma: no cover
                        else:
                            # Fallback: use fraction to calculate head size
                            collected = validation_extract_nw.collect()  # pragma: no cover
                            sample_size = max(
                                1, int(len(collected) * sample_frac)
                            )  # pragma: no cover
                            validation_extract_nw = collected.head(sample_size)  # pragma: no cover

                # Ensure a limit is set on the number of rows to extract
                try:
                    # For DataFrames, use len()
                    extract_length = len(validation_extract_nw)
                except TypeError:
                    # For LazyFrames, collect to get length (or use a reasonable default)
                    try:
                        extract_length = len(validation_extract_nw.collect())
                    except Exception:  # pragma: no cover
                        # If collection fails, apply limit anyway as a safety measure
                        extract_length = extract_limit + 1  # pragma: no cover

                if extract_length > extract_limit:
                    validation_extract_nw = validation_extract_nw.head(extract_limit)

                # If a 'rows_distinct' validation step, then the extract should have the
                # duplicate rows arranged together
                if assertion_type == "rows_distinct":
                    # Get the list of column names in the extract, excluding the `_row_num_` column
                    column_names = validation_extract_nw.columns
                    column_names.remove("_row_num_")

                    # Only include the columns that were defined in `rows_distinct(columns_subset=)`
                    # (stored here in `column`), if supplied
                    if column is not None:
                        column_names = column
                        column_names_subset = ["_row_num_"] + column
                        validation_extract_nw = validation_extract_nw.select(column_names_subset)

                    validation_extract_nw = (
                        validation_extract_nw.with_columns(
                            group_min_row=nw.min("_row_num_").over(*column_names)
                        )
                        # First sort by the columns to group duplicates and by row numbers
                        # within groups; this type of sorting will preserve the original order in a
                        # single operation
                        .sort(by=["group_min_row"] + column_names + ["_row_num_"])
                        .drop("group_min_row")
                    )

                # Ensure that the extract is collected and set to its native format
                # For LazyFrames (like PySpark), we need to collect before converting to native
                if hasattr(validation_extract_nw, "collect"):
                    validation_extract_nw = validation_extract_nw.collect()
                validation.extract = nw.to_native(validation_extract_nw)

            # Get the end time for this step
            end_time = datetime.datetime.now(datetime.timezone.utc)

            # Calculate the duration of processing for this step
            validation.proc_duration_s = (end_time - start_time).total_seconds()

            # Set the time of processing for this step, this should be UTC time is ISO 8601 format
            validation.time_processed = end_time.isoformat(timespec="milliseconds")

        self.time_end = datetime.datetime.now(datetime.timezone.utc)

        # Perform any final actions
        self._execute_final_actions()

        return self

    def all_passed(self) -> bool:
        """
        Determine if every validation step passed perfectly, with no failing test units.

        The `all_passed()` method determines if every validation step passed perfectly, with no
        failing test units. This method is useful for quickly checking if the table passed all
        validation steps with flying colors. If there's even a single failing test unit in any
        validation step, this method will return `False`.

        This validation metric might be overly stringent for some validation plans where failing
        test units are generally expected (and the strategy is to monitor data quality over time).
        However, the value of `all_passed()` could be suitable for validation plans designed to
        ensure that every test unit passes perfectly (e.g., checks for column presence,
        null-checking tests, etc.).

        Returns
        -------
        bool
            `True` if all validation steps had no failing test units, `False` otherwise.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps, and the second step will have a failing test
        unit (the value `10` isn't less than `9`). After interrogation, the `all_passed()` method is
        used to determine if all validation steps passed perfectly.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [1, 2, 9, 5],
                "b": [5, 6, 10, 3],
                "c": ["a", "b", "a", "a"],
            }
        )

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=0)
            .col_vals_lt(columns="b", value=9)
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation.all_passed()
        ```

        The returned value is `False` since the second validation step had a failing test unit. If
        it weren't for that one failing test unit, the return value would have been `True`.
        """
        return all(validation.all_passed for validation in self.validation_info)

    def assert_passing(self) -> None:
        """
        Raise an `AssertionError` if all tests are not passing.

        The `assert_passing()` method will raise an `AssertionError` if a test does not pass. This
        method simply wraps `all_passed` for more ready use in test suites. The step number and
        assertion made is printed in the `AssertionError` message if a failure occurs, ensuring
        some details are preserved.

        If the validation has not yet been interrogated, this method will automatically call
        [`interrogate()`](`pointblank.Validate.interrogate`) with default parameters before checking
        for passing tests.

        Raises
        -------
        AssertionError
            If any validation step has failing test units.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps, and the second step will have a failing test
        unit (the value `10` isn't less than `9`). The `assert_passing()` method is used to assert
        that all validation steps passed perfectly, automatically performing the interrogation if
        needed.

        ```{python}
        #| error: True

        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
            "a": [1, 2, 9, 5],
            "b": [5, 6, 10, 3],
            "c": ["a", "b", "a", "a"],
            }
        )

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=0)
            .col_vals_lt(columns="b", value=9) # this assertion is false
            .col_vals_in_set(columns="c", set=["a", "b"])
        )

        # No need to call [`interrogate()`](`pointblank.Validate.interrogate`) explicitly
        validation.assert_passing()
        ```
        """
        # Check if validation has been interrogated
        if not hasattr(self, "time_start") or self.time_start is None:
            # Auto-interrogate with default parameters
            self.interrogate()

        if not self.all_passed():
            failed_steps = [
                (i, str(step.autobrief))
                for i, step in enumerate(self.validation_info)
                if step.n_failed > 0
            ]
            msg = "The following assertions failed:\n" + "\n".join(
                [f"- Step {i + 1}: {autobrief}" for i, autobrief in failed_steps]
            )
            raise AssertionError(msg)

    def assert_below_threshold(
        self, level: str = "warning", i: int | None = None, message: str | None = None
    ) -> None:
        """
        Raise an `AssertionError` if validation steps exceed a specified threshold level.

        The `assert_below_threshold()` method checks whether validation steps' failure rates are
        below a given threshold level (`"warning"`, `"error"`, or `"critical"`). This is
        particularly useful in automated testing environments where you want to ensure your data
        quality meets minimum standards before proceeding.

        If any validation step exceeds the specified threshold level, an `AssertionError` will be
        raised with details about which steps failed. If the validation has not yet been
        interrogated, this method will automatically call
        [`interrogate()`](`pointblank.Validate.interrogate`) with default parameters.

        Parameters
        ----------
        level
            The threshold level to check against, which could be any of `"warning"` (the default),
            `"error"`, or `"critical"`. An `AssertionError` will be raised if any validation step
            exceeds this level.
        i
            Specific validation step number(s) to check. Can be provided as a single integer or a
            list of integers. If `None` (the default), all steps are checked.
        message
            Custom error message to use if assertion fails. If `None`, a default message will be
            generated that lists the specific steps that exceeded the threshold.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If any specified validation step exceeds the given threshold level.
        ValueError
            If an invalid threshold level is provided.

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        Below are some examples of how to use the `assert_below_threshold()` method. First, we'll
        create a simple Polars DataFrame with two columns (`a` and `b`).

        ```{python}
        import polars as pl

        tbl = pl.DataFrame({
            "a": [7, 4, 9, 7, 12],
            "b": [9, 8, 10, 5, 10]
        })
        ```

        Then a validation plan will be created with thresholds (`warning=0.1`, `error=0.2`,
        `critical=0.3`). After interrogating, we display the validation report table:

        ```{python}
        import pointblank as pb

        validation = (
            pb.Validate(data=tbl, thresholds=(0.1, 0.2, 0.3))
            .col_vals_gt(columns="a", value=5)   # 1 failing test unit
            .col_vals_lt(columns="b", value=10)  # 2 failing test units
            .interrogate()
        )

        validation
        ```

        Using `assert_below_threshold(level="warning")` will raise an `AssertionError` if any step
        exceeds the 'warning' threshold:

        ```{python}
        try:
            validation.assert_below_threshold(level="warning")
        except AssertionError as e:
            print(f"Assertion failed: {e}")
        ```

        Check a specific step against the 'critical' threshold using the `i=` parameter:

        ```{python}
        validation.assert_below_threshold(level="critical", i=1)  # Won't raise an error
        ```

        As the first step is below the 'critical' threshold (it exceeds the 'warning' and 'error'
        thresholds), no error is raised and nothing is printed.

        We can also provide a custom error message with the `message=` parameter. Let's try that
        here:

        ```{python}
        try:
            validation.assert_below_threshold(
                level="error",
                message="Data quality too low for processing!"
            )
        except AssertionError as e:
            print(f"Custom error: {e}")
        ```

        See Also
        --------
        - [`warning()`](`pointblank.Validate.warning`): get the 'warning' status for each validation
        step
        - [`error()`](`pointblank.Validate.error`): get the 'error' status for each validation step
        - [`critical()`](`pointblank.Validate.critical`): get the 'critical' status for each
        validation step
        - [`assert_passing()`](`pointblank.Validate.assert_passing`): assert all validations pass
        completely
        """
        # Check if validation has been interrogated
        if not hasattr(self, "time_start") or self.time_start is None:
            # Auto-interrogate with default parameters
            self.interrogate()

        # Validate the level parameter
        level = level.lower()
        if level not in ["warning", "error", "critical"]:
            raise ValueError(
                f"Invalid threshold level: {level}. Must be one of 'warning', 'error', or 'critical'."
            )

        # Get the threshold status using the appropriate method
        if level == "warning":
            status = self.warning(i=i)
        elif level == "error":
            status = self.error(i=i)
        elif level == "critical":
            status = self.critical(i=i)

        # Find any steps that exceeded the threshold
        failures = []
        for step_num, exceeded in status.items():
            if exceeded:
                # Get the step's description
                validation_step = self.validation_info[step_num - 1]
                step_descriptor = (
                    validation_step.autobrief
                    if hasattr(validation_step, "autobrief") and validation_step.autobrief
                    else f"Validation step {step_num}"
                )
                failures.append(f"Step {step_num}: {step_descriptor}")

        # If any failures were found, raise an AssertionError
        if failures:
            if message:
                msg = message
            else:
                msg = f"The following steps exceeded the {level} threshold level:\n" + "\n".join(
                    failures
                )
            raise AssertionError(msg)

    def above_threshold(self, level: str = "warning", i: int | None = None) -> bool:
        """
        Check if any validation steps exceed a specified threshold level.

        The `above_threshold()` method checks whether validation steps exceed a given threshold
        level. This provides a non-exception-based alternative to
        [`assert_below_threshold()`](`pointblank.Validate.assert_below_threshold`) for conditional
        workflow control based on validation results.

        This method is useful in scenarios where you want to check if any validation steps failed
        beyond a certain threshold without raising an exception, allowing for more flexible
        programmatic responses to validation issues.

        Parameters
        ----------
        level
            The threshold level to check against. Valid options are: `"warning"` (the least severe
            threshold level), `"error"` (the middle severity threshold level), and `"critical"` (the
            most severe threshold level). The default is `"warning"`.
        i
            Specific validation step number(s) to check. If a single integer, checks only that step.
            If a list of integers, checks all specified steps. If `None` (the default), checks all
            validation steps. Step numbers are 1-based (first step is `1`, not `0`).

        Returns
        -------
        bool
            `True` if any of the specified validation steps exceed the given threshold level,
            `False` otherwise.

        Raises
        ------
        ValueError
            If an invalid threshold level is provided.

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        Below are some examples of how to use the `above_threshold()` method. First, we'll create a
        simple Polars DataFrame with a single column (`values`).

        ```{python}
        import polars as pl

        tbl = pl.DataFrame({
            "values": [1, 2, 3, 4, 5, 0, -1]
        })
        ```

        Then a validation plan will be created with thresholds (`warning=0.1`, `error=0.2`,
        `critical=0.3`). After interrogating, we display the validation report table:

        ```{python}
        import pointblank as pb

        validation = (
            pb.Validate(data=tbl, thresholds=(0.1, 0.2, 0.3))
            .col_vals_gt(columns="values", value=0)
            .col_vals_lt(columns="values", value=10)
            .col_vals_between(columns="values", left=0, right=5)
            .interrogate()
        )

        validation
        ```

        Let's check if any steps exceed the 'warning' threshold with the `above_threshold()` method.
        A message will be printed if that's the case:

        ```{python}
        if validation.above_threshold(level="warning"):
            print("Some steps have exceeded the warning threshold")
        ```

        Check if only steps 2 and 3 exceed the 'error' threshold through use of the `i=` argument:

        ```{python}
        if validation.above_threshold(level="error", i=[2, 3]):
            print("Steps 2 and/or 3 have exceeded the error threshold")
        ```

        You can use this in a workflow to conditionally trigger processes. Here's a snippet of how
        you might use this in a function:

        ```python
        def process_data(validation_obj):
            # Only continue processing if validation passes critical thresholds
            if not validation_obj.above_threshold(level="critical"):
                # Continue with processing
                print("Data meets critical quality thresholds, proceeding...")
                return True
            else:
                # Log failure and stop processing
                print("Data fails critical quality checks, aborting...")
                return False
        ```

        Note that this is just a suggestion for how to implement conditional workflow processes. You
        should adapt this pattern to your specific requirements, which might include  different
        threshold levels, custom logging mechanisms, or integration with your organization's data
        pipelines and notification systems.

        See Also
        --------
        - [`assert_below_threshold()`](`pointblank.Validate.assert_below_threshold`): a similar
        method that raises an exception if thresholds are exceeded
        - [`warning()`](`pointblank.Validate.warning`): get the 'warning' status for each validation
        step
        - [`error()`](`pointblank.Validate.error`): get the 'error' status for each validation step
        - [`critical()`](`pointblank.Validate.critical`): get the 'critical' status for each
        validation step
        """
        # Ensure validation has been run
        if not hasattr(self, "time_start") or self.time_start is None:
            return False

        # Validate the level parameter
        level = level.lower()
        if level not in ["warning", "error", "critical"]:
            raise ValueError(
                f"Invalid threshold level: {level}. Must be one of 'warning', 'error', or 'critical'."
            )

        # Get the threshold status using the appropriate method
        if level == "warning":
            status = self.warning(i=i)
        elif level == "error":
            status = self.error(i=i)
        elif level == "critical":
            status = self.critical(i=i)

        # Return True if any steps exceeded the threshold
        return any(status.values())

    def n(self, i: int | list[int] | None = None, scalar: bool = False) -> dict[int, int] | int:
        """
        Provides a dictionary of the number of test units for each validation step.

        The `n()` method provides the number of test units for each validation step. This is the
        total number of test units that were evaluated in the validation step. It is always an
        integer value.

        Test units are the atomic units of the validation process. Different validations can have
        different numbers of test units. For example, a validation that checks for the presence of
        a column in a table will have a single test unit. A validation that checks for the presence
        of a value in a column will have as many test units as there are rows in the table.

        The method provides a dictionary of the number of test units for each validation step. If
        the `scalar=True` argument is provided and `i=` is a scalar, the value is returned as a
        scalar instead of a dictionary. The total number of test units for a validation step is the
        sum of the number of passing and failing test units (i.e., `n = n_passed + n_failed`).

        Parameters
        ----------
        i
            The validation step number(s) from which the number of test units is obtained.
            Can be provided as a list of integers or a single integer. If `None`, all steps are
            included.
        scalar
            If `True` and `i=` is a scalar, return the value as a scalar instead of a dictionary.

        Returns
        -------
        dict[int, int] | int
            A dictionary of the number of test units for each validation step or a scalar value.

        Examples
        --------
        Different types of validation steps can have different numbers of test units. In the example
        below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and `c`). There
        will be three validation steps, and the number of test units for each step will be a little
        bit different.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [1, 2, 9, 5],
                "b": [5, 6, 10, 3],
                "c": ["a", "b", "a", "a"],
            }
        )

        # Define a preprocessing function
        def filter_by_a_gt_1(df):
            return df.filter(pl.col("a") > 1)

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=0)
            .col_exists(columns="b")
            .col_vals_lt(columns="b", value=9, pre=filter_by_a_gt_1)
            .interrogate()
        )
        ```

        The first validation step checks that all values in column `a` are greater than `0`. Let's
        use the `n()` method to determine the number of test units this validation step.

        ```{python}
        validation.n(i=1, scalar=True)
        ```

        The returned value of `4` is the number of test units for the first validation step. This
        value is the same as the number of rows in the table.

        The second validation step checks for the existence of column `b`. Using the `n()` method
        we can get the number of test units for this the second step.

        ```{python}
        validation.n(i=2, scalar=True)
        ```

        There's a single test unit here because the validation step is checking for the presence of
        a single column.

        The third validation step checks that all values in column `b` are less than `9` after
        filtering the table to only include rows where the value in column `a` is greater than `1`.
        Because the table is filtered, the number of test units will be less than the total number
        of rows in the input table. Let's prove this by using the `n()` method.

        ```{python}
        validation.n(i=3, scalar=True)
        ```

        The returned value of `3` is the number of test units for the third validation step. When
        using the `pre=` argument, the input table can be mutated before performing the validation.
        The `n()` method is a good way to determine whether the mutation performed as expected.

        In all of these examples, the `scalar=True` argument was used to return the value as a
        scalar integer value. If `scalar=False`, the method will return a dictionary with an entry
        for the validation step number (from the `i=` argument) and the number of test units.
        Futhermore, leaving out the `i=` argument altogether will return a dictionary with filled
        with the number of test units for each validation step. Here's what that looks like:

        ```{python}
        validation.n()
        ```
        """
        result = self._get_validation_dict(i, "n")
        if scalar and isinstance(i, int):
            return result[i]
        return result

    def n_passed(
        self, i: int | list[int] | None = None, scalar: bool = False
    ) -> dict[int, int] | int:
        """
        Provides a dictionary of the number of test units that passed for each validation step.

        The `n_passed()` method provides the number of test units that passed for each validation
        step. This is the number of test units that passed in the the validation step. It is always
        some integer value between `0` and the total number of test units.

        Test units are the atomic units of the validation process. Different validations can have
        different numbers of test units. For example, a validation that checks for the presence of
        a column in a table will have a single test unit. A validation that checks for the presence
        of a value in a column will have as many test units as there are rows in the table.

        The method provides a dictionary of the number of passing test units for each validation
        step. If the `scalar=True` argument is provided and `i=` is a scalar, the value is returned
        as a scalar instead of a dictionary. Furthermore, a value obtained here will be the
        complement to the analogous value returned by the
        [`n_passed()`](`pointblank.Validate.n_passed`) method (i.e., `n - n_failed`).

        Parameters
        ----------
        i
            The validation step number(s) from which the number of passing test units is obtained.
            Can be provided as a list of integers or a single integer. If `None`, all steps are
            included.
        scalar
            If `True` and `i=` is a scalar, return the value as a scalar instead of a dictionary.

        Returns
        -------
        dict[int, int] | int
            A dictionary of the number of passing test units for each validation step or a scalar
            value.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps and, as it turns out, all of them will have
        failing test units. After interrogation, the `n_passed()` method is used to determine the
        number of passing test units for each validation step.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [7, 4, 9, 7, 12],
                "b": [9, 8, 10, 5, 10],
                "c": ["a", "b", "c", "a", "b"]
            }
        )

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=5)
            .col_vals_gt(columns="b", value=pb.col("a"))
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation.n_passed()
        ```

        The returned dictionary shows that all validation steps had no passing test units (each
        value was less than `5`, which is the total number of test units for each step).

        If we wanted to check the number of passing test units for a single validation step, we can
        provide the step number. Also, we could forego the dictionary and get a scalar value by
        setting `scalar=True` (ensuring that `i=` is a scalar).

        ```{python}
        validation.n_passed(i=1)
        ```

        The returned value of `4` is the number of passing test units for the first validation step.
        """
        result = self._get_validation_dict(i, "n_passed")
        if scalar and isinstance(i, int):
            return result[i]
        return result

    def n_failed(
        self, i: int | list[int] | None = None, scalar: bool = False
    ) -> dict[int, int] | int:
        """
        Provides a dictionary of the number of test units that failed for each validation step.

        The `n_failed()` method provides the number of test units that failed for each validation
        step. This is the number of test units that did not pass in the the validation step. It is
        always some integer value between `0` and the total number of test units.

        Test units are the atomic units of the validation process. Different validations can have
        different numbers of test units. For example, a validation that checks for the presence of
        a column in a table will have a single test unit. A validation that checks for the presence
        of a value in a column will have as many test units as there are rows in the table.

        The method provides a dictionary of the number of failing test units for each validation
        step. If the `scalar=True` argument is provided and `i=` is a scalar, the value is returned
        as a scalar instead of a dictionary. Furthermore, a value obtained here will be the
        complement to the analogous value returned by the
        [`n_passed()`](`pointblank.Validate.n_passed`) method (i.e., `n - n_passed`).

        Parameters
        ----------
        i
            The validation step number(s) from which the number of failing test units is obtained.
            Can be provided as a list of integers or a single integer. If `None`, all steps are
            included.
        scalar
            If `True` and `i=` is a scalar, return the value as a scalar instead of a dictionary.

        Returns
        -------
        dict[int, int] | int
            A dictionary of the number of failing test units for each validation step or a scalar
            value.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps and, as it turns out, all of them will have
        failing test units. After interrogation, the `n_failed()` method is used to determine the
        number of failing test units for each validation step.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [7, 4, 9, 7, 12],
                "b": [9, 8, 10, 5, 10],
                "c": ["a", "b", "c", "a", "b"]
            }
        )

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=5)
            .col_vals_gt(columns="b", value=pb.col("a"))
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation.n_failed()
        ```

        The returned dictionary shows that all validation steps had failing test units.

        If we wanted to check the number of failing test units for a single validation step, we can
        provide the step number. Also, we could forego the dictionary and get a scalar value by
        setting `scalar=True` (ensuring that `i=` is a scalar).

        ```{python}
        validation.n_failed(i=1)
        ```

        The returned value of `1` is the number of failing test units for the first validation step.
        """
        result = self._get_validation_dict(i, "n_failed")
        if scalar and isinstance(i, int):
            return result[i]
        return result

    def f_passed(
        self, i: int | list[int] | None = None, scalar: bool = False
    ) -> dict[int, float] | float:
        """
        Provides a dictionary of the fraction of test units that passed for each validation step.

        A measure of the fraction of test units that passed is provided by the `f_passed` attribute.
        This is the fraction of test units that passed the validation step over the total number of
        test units. Given this is a fractional value, it will always be in the range of `0` to `1`.

        Test units are the atomic units of the validation process. Different validations can have
        different numbers of test units. For example, a validation that checks for the presence of
        a column in a table will have a single test unit. A validation that checks for the presence
        of a value in a column will have as many test units as there are rows in the table.

        This method provides a dictionary of the fraction of passing test units for each validation
        step. If the `scalar=True` argument is provided and `i=` is a scalar, the value is returned
        as a scalar instead of a dictionary. Furthermore, a value obtained here will be the
        complement to the analogous value returned by the
        [`f_failed()`](`pointblank.Validate.f_failed`) method (i.e., `1 - f_failed()`).

        Parameters
        ----------
        i
            The validation step number(s) from which the fraction of passing test units is obtained.
            Can be provided as a list of integers or a single integer. If `None`, all steps are
            included.
        scalar
            If `True` and `i=` is a scalar, return the value as a scalar instead of a dictionary.

        Returns
        -------
        dict[int, float] | float
            A dictionary of the fraction of passing test units for each validation step or a scalar
            value.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps, all having some failing test units. After
        interrogation, the `f_passed()` method is used to determine the fraction of passing test
        units for each validation step.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [7, 4, 9, 7, 12, 3, 10],
                "b": [9, 8, 10, 5, 10, 6, 2],
                "c": ["a", "b", "c", "a", "b", "d", "c"]
            }
        )

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=5)
            .col_vals_gt(columns="b", value=pb.col("a"))
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation.f_passed()
        ```

        The returned dictionary shows the fraction of passing test units for each validation step.
        The values are all less than `1` since there were failing test units in each step.

        If we wanted to check the fraction of passing test units for a single validation step, we
        can provide the step number. Also, we could have the value returned as a scalar by setting
        `scalar=True` (ensuring that `i=` is a scalar).

        ```{python}
        validation.f_passed(i=1)
        ```

        The returned value is the proportion of passing test units for the first validation step
        (5 passing test units out of 7 total test units).
        """
        result = self._get_validation_dict(i, "f_passed")
        if scalar and isinstance(i, int):
            return result[i]
        return result

    def f_failed(
        self, i: int | list[int] | None = None, scalar: bool = False
    ) -> dict[int, float] | float:
        """
        Provides a dictionary of the fraction of test units that failed for each validation step.

        A measure of the fraction of test units that failed is provided by the `f_failed` attribute.
        This is the fraction of test units that failed the validation step over the total number of
        test units. Given this is a fractional value, it will always be in the range of `0` to `1`.

        Test units are the atomic units of the validation process. Different validations can have
        different numbers of test units. For example, a validation that checks for the presence of
        a column in a table will have a single test unit. A validation that checks for the presence
        of a value in a column will have as many test units as there are rows in the table.

        This method provides a dictionary of the fraction of failing test units for each validation
        step. If the `scalar=True` argument is provided and `i=` is a scalar, the value is returned
        as a scalar instead of a dictionary. Furthermore, a value obtained here will be the
        complement to the analogous value returned by the
        [`f_passed()`](`pointblank.Validate.f_passed`) method (i.e., `1 - f_passed()`).

        Parameters
        ----------
        i
            The validation step number(s) from which the fraction of failing test units is obtained.
            Can be provided as a list of integers or a single integer. If `None`, all steps are
            included.
        scalar
            If `True` and `i=` is a scalar, return the value as a scalar instead of a dictionary.

        Returns
        -------
        dict[int, float] | float
            A dictionary of the fraction of failing test units for each validation step or a scalar
            value.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps, all having some failing test units. After
        interrogation, the `f_failed()` method is used to determine the fraction of failing test
        units for each validation step.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [7, 4, 9, 7, 12, 3, 10],
                "b": [9, 8, 10, 5, 10, 6, 2],
                "c": ["a", "b", "c", "a", "b", "d", "c"]
            }
        )

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=5)
            .col_vals_gt(columns="b", value=pb.col("a"))
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation.f_failed()
        ```

        The returned dictionary shows the fraction of failing test units for each validation step.
        The values are all greater than `0` since there were failing test units in each step.

        If we wanted to check the fraction of failing test units for a single validation step, we
        can provide the step number. Also, we could have the value returned as a scalar by setting
        `scalar=True` (ensuring that `i=` is a scalar).

        ```{python}
        validation.f_failed(i=1)
        ```

        The returned value is the proportion of failing test units for the first validation step
        (2 failing test units out of 7 total test units).
        """
        result = self._get_validation_dict(i, "f_failed")
        if scalar and isinstance(i, int):
            return result[i]
        return result

    def warning(
        self, i: int | list[int] | None = None, scalar: bool = False
    ) -> dict[int, bool] | bool:
        """
        Get the 'warning' level status for each validation step.

        The 'warning' status for a validation step is `True` if the fraction of failing test units
        meets or exceeds the threshold for the 'warning' level. Otherwise, the status is `False`.

        The ascribed name of 'warning' is semantic and does not imply that a warning message is
        generated, it is simply a status indicator that could be used to trigger some action to be
        taken. Here's how it fits in with other status indicators:

        - 'warning': the status obtained by calling 'warning()', least severe
        - 'error': the status obtained by calling [`error()`](`pointblank.Validate.error`), middle
        severity
        - 'critical': the status obtained by calling [`critical()`](`pointblank.Validate.critical`),
        most severe

        This method provides a dictionary of the 'warning' status for each validation step. If the
        `scalar=True` argument is provided and `i=` is a scalar, the value is returned as a scalar
        instead of a dictionary.

        Parameters
        ----------
        i
            The validation step number(s) from which the 'warning' status is obtained. Can be
            provided as a list of integers or a single integer. If `None`, all steps are included.
        scalar
            If `True` and `i=` is a scalar, return the value as a scalar instead of a dictionary.

        Returns
        -------
        dict[int, bool] | bool
            A dictionary of the 'warning' status for each validation step or a scalar value.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps, and the first step will have some failing test
        units, the rest will be completely passing. We've set thresholds here for each of the steps
        by using `thresholds=(2, 4, 5)`, which means:

        - the 'warning' threshold is `2` failing test units
        - the 'error' threshold is `4` failing test units
        - the 'critical' threshold is `5` failing test units

        After interrogation, the `warning()` method is used to determine the 'warning' status for
        each validation step.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [7, 4, 9, 7, 12, 3, 10],
                "b": [9, 8, 10, 5, 10, 6, 2],
                "c": ["a", "b", "a", "a", "b", "b", "a"]
            }
        )

        validation = (
            pb.Validate(data=tbl, thresholds=(2, 4, 5))
            .col_vals_gt(columns="a", value=5)
            .col_vals_lt(columns="b", value=15)
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation.warning()
        ```

        The returned dictionary provides the 'warning' status for each validation step. The first
        step has a `True` value since the number of failing test units meets the threshold for the
        'warning' level. The second and third steps have `False` values since the number of failing
        test units was `0`, which is below the threshold for the 'warning' level.

        We can also visually inspect the 'warning' status across all steps by viewing the validation
        table:

        ```{python}
        validation
        ```

        We can see that there's a filled gray circle in the first step (look to the far right side,
        in the `W` column) indicating that the 'warning' threshold was met. The other steps have
        empty gray circles. This means that thresholds were 'set but not met' in those steps.

        If we wanted to check the 'warning' status for a single validation step, we can provide the
        step number. Also, we could have the value returned as a scalar by setting `scalar=True`
        (ensuring that `i=` is a scalar).

        ```{python}
        validation.warning(i=1)
        ```

        The returned value is `True`, indicating that the first validation step had met the
        'warning' threshold.
        """
        result = self._get_validation_dict(i, "warning")
        if scalar and isinstance(i, int):
            return result[i]
        return result

    def error(
        self, i: int | list[int] | None = None, scalar: bool = False
    ) -> dict[int, bool] | bool:
        """
        Get the 'error' level status for each validation step.

        The 'error' status for a validation step is `True` if the fraction of failing test units
        meets or exceeds the threshold for the 'error' level. Otherwise, the status is `False`.

        The ascribed name of 'error' is semantic and does not imply that the validation process
        is halted, it is simply a status indicator that could be used to trigger some action to be
        taken. Here's how it fits in with other status indicators:

        - 'warning': the status obtained by calling [`warning()`](`pointblank.Validate.warning`),
        least severe
        - 'error': the status obtained by calling `error()`, middle severity
        - 'critical': the status obtained by calling [`critical()`](`pointblank.Validate.critical`),
        most severe

        This method provides a dictionary of the 'error' status for each validation step. If the
        `scalar=True` argument is provided and `i=` is a scalar, the value is returned as a scalar
        instead of a dictionary.

        Parameters
        ----------
        i
            The validation step number(s) from which the 'error' status is obtained. Can be
            provided as a list of integers or a single integer. If `None`, all steps are included.
        scalar
            If `True` and `i=` is a scalar, return the value as a scalar instead of a dictionary.

        Returns
        -------
        dict[int, bool] | bool
            A dictionary of the 'error' status for each validation step or a scalar value.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps, and the first step will have some failing test
        units, the rest will be completely passing. We've set thresholds here for each of the steps
        by using `thresholds=(2, 4, 5)`, which means:

        - the 'warning' threshold is `2` failing test units
        - the 'error' threshold is `4` failing test units
        - the 'critical' threshold is `5` failing test units

        After interrogation, the `error()` method is used to determine the 'error' status for each
        validation step.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [3, 4, 9, 7, 2, 3, 8],
                "b": [9, 8, 10, 5, 10, 6, 2],
                "c": ["a", "b", "a", "a", "b", "b", "a"]
            }
        )

        validation = (
            pb.Validate(data=tbl, thresholds=(2, 4, 5))
            .col_vals_gt(columns="a", value=5)
            .col_vals_lt(columns="b", value=15)
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation.error()
        ```

        The returned dictionary provides the 'error' status for each validation step. The first step
        has a `True` value since the number of failing test units meets the threshold for the
        'error' level. The second and third steps have `False` values since the number of failing
        test units was `0`, which is below the threshold for the 'error' level.

        We can also visually inspect the 'error' status across all steps by viewing the validation
        table:

        ```{python}
        validation
        ```

        We can see that there are filled gray and yellow circles in the first step (far right side,
        in the `W` and `E` columns) indicating that the 'warning' and 'error' thresholds were met.
        The other steps have empty gray and yellow circles. This means that thresholds were 'set but
        not met' in those steps.

        If we wanted to check the 'error' status for a single validation step, we can provide the
        step number. Also, we could have the value returned as a scalar by setting `scalar=True`
        (ensuring that `i=` is a scalar).

        ```{python}
        validation.error(i=1)
        ```

        The returned value is `True`, indicating that the first validation step had the 'error'
        threshold met.
        """
        result = self._get_validation_dict(i, "error")
        if scalar and isinstance(i, int):
            return result[i]
        return result

    def critical(
        self, i: int | list[int] | None = None, scalar: bool = False
    ) -> dict[int, bool] | bool:
        """
        Get the 'critical' level status for each validation step.

        The 'critical' status for a validation step is `True` if the fraction of failing test units
        meets or exceeds the threshold for the 'critical' level. Otherwise, the status is `False`.

        The ascribed name of 'critical' is semantic and is thus simply a status indicator that could
        be used to trigger some action to be take. Here's how it fits in with other status
        indicators:

        - 'warning': the status obtained by calling [`warning()`](`pointblank.Validate.warning`),
        least severe
        - 'error': the status obtained by calling [`error()`](`pointblank.Validate.error`), middle
        severity
        - 'critical': the status obtained by calling `critical()`, most severe

        This method provides a dictionary of the 'critical' status for each validation step. If the
        `scalar=True` argument is provided and `i=` is a scalar, the value is returned as a scalar
        instead of a dictionary.

        Parameters
        ----------
        i
            The validation step number(s) from which the 'critical' status is obtained. Can be
            provided as a list of integers or a single integer. If `None`, all steps are included.
        scalar
            If `True` and `i=` is a scalar, return the value as a scalar instead of a dictionary.

        Returns
        -------
        dict[int, bool] | bool
            A dictionary of the 'critical' status for each validation step or a scalar value.

        Examples
        --------
        In the example below, we'll use a simple Polars DataFrame with three columns (`a`, `b`, and
        `c`). There will be three validation steps, and the first step will have many failing test
        units, the rest will be completely passing. We've set thresholds here for each of the steps
        by using `thresholds=(2, 4, 5)`, which means:

        - the 'warning' threshold is `2` failing test units
        - the 'error' threshold is `4` failing test units
        - the 'critical' threshold is `5` failing test units

        After interrogation, the `critical()` method is used to determine the 'critical' status for
        each validation step.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [2, 4, 4, 7, 2, 3, 8],
                "b": [9, 8, 10, 5, 10, 6, 2],
                "c": ["a", "b", "a", "a", "b", "b", "a"]
            }
        )

        validation = (
            pb.Validate(data=tbl, thresholds=(2, 4, 5))
            .col_vals_gt(columns="a", value=5)
            .col_vals_lt(columns="b", value=15)
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation.critical()
        ```

        The returned dictionary provides the 'critical' status for each validation step. The first
        step has a `True` value since the number of failing test units meets the threshold for the
        'critical' level. The second and third steps have `False` values since the number of failing
        test units was `0`, which is below the threshold for the 'critical' level.

        We can also visually inspect the 'critical' status across all steps by viewing the
        validation table:

        ```{python}
        validation
        ```

        We can see that there are filled gray, yellow, and red circles in the first step (far right
        side, in the `W`, `E`, and `C` columns) indicating that the 'warning', 'error', and
        'critical' thresholds were met. The other steps have empty gray, yellow, and red circles.
        This means that thresholds were 'set but not met' in those steps.

        If we wanted to check the 'critical' status for a single validation step, we can provide the
        step number. Also, we could have the value returned as a scalar by setting `scalar=True`
        (ensuring that `i=` is a scalar).

        ```{python}
        validation.critical(i=1)
        ```

        The returned value is `True`, indicating that the first validation step had the 'critical'
        threshold met.
        """
        result = self._get_validation_dict(i, "critical")
        if scalar and isinstance(i, int):
            return result[i]
        return result

    def get_data_extracts(
        self, i: int | list[int] | None = None, frame: bool = False
    ) -> dict[int, FrameT | None] | FrameT | None:
        """
        Get the rows that failed for each validation step.

        After the [`interrogate()`](`pointblank.Validate.interrogate`) method has been called, the
        `get_data_extracts()` method can be used to extract the rows that failed in each
        column-value or row-based validation step (e.g.,
        [`col_vals_gt()`](`pointblank.Validate.col_vals_gt`),
        [`rows_distinct()`](`pointblank.Validate.rows_distinct`), etc.). The method returns a
        dictionary of tables containing the rows that failed in every validation step. If
        `frame=True` and `i=` is a scalar, the value is conveniently returned as a table (forgoing
        the dictionary structure).

        Parameters
        ----------
        i
            The validation step number(s) from which the failed rows are obtained. Can be provided
            as a list of integers or a single integer. If `None`, all steps are included.
        frame
            If `True` and `i=` is a scalar, return the value as a DataFrame instead of a dictionary.

        Returns
        -------
        dict[int, FrameT | None] | FrameT | None
            A dictionary of tables containing the rows that failed in every compatible validation
            step. Alternatively, it can be a DataFrame if `frame=True` and `i=` is a scalar.

        Compatible Validation Methods for Yielding Extracted Rows
        ---------------------------------------------------------
        The following validation methods operate on column values and will have rows extracted when
        there are failing test units.

        - [`col_vals_gt()`](`pointblank.Validate.col_vals_gt`)
        - [`col_vals_ge()`](`pointblank.Validate.col_vals_ge`)
        - [`col_vals_lt()`](`pointblank.Validate.col_vals_lt`)
        - [`col_vals_le()`](`pointblank.Validate.col_vals_le`)
        - [`col_vals_eq()`](`pointblank.Validate.col_vals_eq`)
        - [`col_vals_ne()`](`pointblank.Validate.col_vals_ne`)
        - [`col_vals_between()`](`pointblank.Validate.col_vals_between`)
        - [`col_vals_outside()`](`pointblank.Validate.col_vals_outside`)
        - [`col_vals_in_set()`](`pointblank.Validate.col_vals_in_set`)
        - [`col_vals_not_in_set()`](`pointblank.Validate.col_vals_not_in_set`)
        - [`col_vals_null()`](`pointblank.Validate.col_vals_null`)
        - [`col_vals_not_null()`](`pointblank.Validate.col_vals_not_null`)
        - [`col_vals_regex()`](`pointblank.Validate.col_vals_regex`)
        - [`col_vals_expr()`](`pointblank.Validate.col_vals_expr`)
        - [`conjointly()`](`pointblank.Validate.conjointly`)

        An extracted row for these validation methods means that a test unit failed for that row in
        the validation step.

        These row-based validation methods will also have rows extracted should there be failing
        rows:

        - [`rows_distinct()`](`pointblank.Validate.rows_distinct`)
        - [`rows_complete()`](`pointblank.Validate.rows_complete`)

        The extracted rows are a subset of the original table and are useful for further analysis
        or for understanding the nature of the failing test units.

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(preview_incl_header=False)
        ```
        Let's perform a series of validation steps on a Polars DataFrame. We'll use the
        [`col_vals_gt()`](`pointblank.Validate.col_vals_gt`) in the first step,
        [`col_vals_lt()`](`pointblank.Validate.col_vals_lt`) in the second step, and
        [`col_vals_ge()`](`pointblank.Validate.col_vals_ge`) in the third step. The
        [`interrogate()`](`pointblank.Validate.interrogate`) method executes the validation; then,
        we can extract the rows that failed for each validation step.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [5, 6, 5, 3, 6, 1],
                "b": [1, 2, 1, 5, 2, 6],
                "c": [3, 7, 2, 6, 3, 1],
            }
        )

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=4)
            .col_vals_lt(columns="c", value=5)
            .col_vals_ge(columns="b", value=1)
            .interrogate()
        )

        validation.get_data_extracts()
        ```

        The `get_data_extracts()` method returns a dictionary of tables, where each table contains
        a subset of rows from the table. These are the rows that failed for each validation step.

        In the first step, the[`col_vals_gt()`](`pointblank.Validate.col_vals_gt`) method was used
        to check if the values in column `a` were greater than `4`. The extracted table shows the
        rows where this condition was not met; look at the `a` column: all values are less than `4`.

        In the second step, the [`col_vals_lt()`](`pointblank.Validate.col_vals_lt`) method was
        used to check if the values in column `c` were less than `5`. In the extracted two-row
        table, we see that the values in column `c` are greater than `5`.

        The third step ([`col_vals_ge()`](`pointblank.Validate.col_vals_ge`)) checked if the values
        in column `b` were greater than or equal to `1`. There were no failing test units, so the
        extracted table is empty (i.e., has columns but no rows).

        The `i=` argument can be used to narrow down the extraction to one or more steps. For
        example, to extract the rows that failed in the first step only:

        ```{python}
        validation.get_data_extracts(i=1)
        ```

        Note that the first validation step is indexed at `1` (not `0`). This 1-based indexing is
        in place here to match the step numbers reported in the validation table. What we get back
        is still a dictionary, but it only contains one table (the one for the first step).

        If you want to get the extracted table as a DataFrame, set `frame=True` and provide a scalar
        value for `i`. For example, to get the extracted table for the second step as a DataFrame:

        ```{python}
        pb.preview(validation.get_data_extracts(i=2, frame=True))
        ```

        The extracted table is now a DataFrame, which can serve as a more convenient format for
        further analysis or visualization. We further used the [`preview()`](`pointblank.preview`)
        function to show the DataFrame in an HTML view.
        """
        result = self._get_validation_dict(i, "extract")
        if frame and isinstance(i, int):
            return result[i]
        return result

    def get_json_report(
        self, use_fields: list[str] | None = None, exclude_fields: list[str] | None = None
    ) -> str:
        """
        Get a report of the validation results as a JSON-formatted string.

        The `get_json_report()` method provides a machine-readable report of validation results in
        JSON format. This is particularly useful for programmatic processing, storing validation
        results, or integrating with other systems. The report includes detailed information about
        each validation step, such as assertion type, columns validated, threshold values, test
        results, and more.

        By default, all available validation information fields are included in the report. However,
        you can customize the fields to include or exclude using the `use_fields=` and
        `exclude_fields=` parameters.

        Parameters
        ----------
        use_fields
            An optional list of specific fields to include in the report. If provided, only these
            fields will be included in the JSON output. If `None` (the default), all standard
            validation report fields are included. Have a look at the *Available Report Fields*
            section below for a list of fields that can be included in the report.
        exclude_fields
            An optional list of fields to exclude from the report. If provided, these fields will
            be omitted from the JSON output. If `None` (the default), no fields are excluded.
            This parameter cannot be used together with `use_fields=`. The *Available Report Fields*
            provides a listing of fields that can be excluded from the report.

        Returns
        -------
        str
            A JSON-formatted string representing the validation report, with each validation step
            as an object in the report array.

        Available Report Fields
        -----------------------
        The JSON report can include any of the standard validation report fields, including:

        - `i`: the step number (1-indexed)
        - `i_o`: the original step index from the validation plan (pre-expansion)
        - `assertion_type`: the type of validation assertion (e.g., `"col_vals_gt"`, etc.)
        - `column`: the column being validated (or columns used in certain validations)
        - `values`: the comparison values or parameters used in the validation
        - `inclusive`: whether the comparison is inclusive (for range-based validations)
        - `na_pass`: whether `NA`/`Null` values are considered passing (for certain validations)
        - `pre`: preprocessing function applied before validation
        - `segments`: data segments to which the validation was applied
        - `thresholds`: threshold level statement that was used for the validation step
        - `label`: custom label for the validation step
        - `brief`: a brief description of the validation step
        - `active`: whether the validation step is active
        - `all_passed`: whether all test units passed in the step
        - `n`: total number of test units
        - `n_passed`, `n_failed`: number of test units that passed and failed
        - `f_passed`, `f_failed`: Fraction of test units that passed and failed
        - `warning`, `error`, `critical`: whether the namesake threshold level was exceeded (is
        `null` if threshold not set)
        - `time_processed`: when the validation step was processed (ISO 8601 format)
        - `proc_duration_s`: the processing duration in seconds

        Examples
        --------
        Let's create a validation plan with a few validation steps and generate a JSON report of the
        results:

        ```{python}
        import pointblank as pb
        import polars as pl

        # Create a sample DataFrame
        tbl = pl.DataFrame({
            "a": [5, 7, 8, 9],
            "b": [3, 4, 2, 1]
        })

        # Create and execute a validation plan
        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=6)
            .col_vals_lt(columns="b", value=4)
            .interrogate()
        )

        # Get the full JSON report
        json_report = validation.get_json_report()

        print(json_report)
        ```

        You can also customize which fields to include:

        ```{python}
        json_report = validation.get_json_report(
            use_fields=["i", "assertion_type", "column", "n_passed", "n_failed"]
        )

        print(json_report)
        ```

        Or which fields to exclude:

        ```{python}
        json_report = validation.get_json_report(
            exclude_fields=[
                "i_o", "thresholds", "pre", "segments", "values",
                "na_pass", "inclusive", "label", "brief", "active",
                "time_processed", "proc_duration_s"
            ]
        )

        print(json_report)
        ```

        The JSON output can be further processed or analyzed programmatically:

        ```{python}
        import json

        # Parse the JSON report
        report_data = json.loads(validation.get_json_report())

        # Extract and analyze validation results
        failing_steps = [step for step in report_data if step["n_failed"] > 0]
        print(f"Number of failing validation steps: {len(failing_steps)}")
        ```

        See Also
        --------
        - [`get_tabular_report()`](`pointblank.Validate.get_tabular_report`): Get a formatted HTML
        report as a GT table
        - [`get_data_extracts()`](`pointblank.Validate.get_data_extracts`): Get rows that
        failed validation
        """
        if use_fields is not None and exclude_fields is not None:
            raise ValueError("Cannot specify both `use_fields=` and `exclude_fields=`.")

        if use_fields is None:
            fields = VALIDATION_REPORT_FIELDS
        else:
            # Ensure that the fields to use are valid
            _check_invalid_fields(use_fields, VALIDATION_REPORT_FIELDS)

            fields = use_fields

        if exclude_fields is not None:
            # Ensure that the fields to exclude are valid
            _check_invalid_fields(exclude_fields, VALIDATION_REPORT_FIELDS)

            fields = [field for field in fields if field not in exclude_fields]

        report = []

        for validation_info in self.validation_info:
            report_entry = {
                field: getattr(validation_info, field) for field in VALIDATION_REPORT_FIELDS
            }

            # If preprocessing functions are included in the report, convert them to strings
            if "pre" in fields:
                report_entry["pre"] = _pre_processing_funcs_to_str(report_entry["pre"])

            # Filter the report entry based on the fields to include
            report_entry = {field: report_entry[field] for field in fields}

            report.append(report_entry)

        return json.dumps(report, indent=4, default=str)

    def get_sundered_data(self, type="pass") -> FrameT:
        """
        Get the data that passed or failed the validation steps.

        Validation of the data is one thing but, sometimes, you want to use the best part of the
        input dataset for something else. The `get_sundered_data()` method works with a `Validate`
        object that has been interrogated (i.e., the
        [`interrogate()`](`pointblank.Validate.interrogate`) method was used). We can get either the
        'pass' data piece (rows with no failing test units across all column-value based validation
        functions), or, the 'fail' data piece (rows with at least one failing test unit across the
        same series of validations).

        Details
        -------
        There are some caveats to sundering. The validation steps considered for this splitting will
        only involve steps where:

        - of certain check types, where test units are cells checked down a column (e.g., the
        `col_vals_*()` methods)
        - `active=` is not set to `False`
        - `pre=` has not been given an expression for modifying the input table

        So long as these conditions are met, the data will be split into two constituent tables: one
        with the rows that passed all validation steps and another with the rows that failed at
        least one validation step.

        Parameters
        ----------
        type
            The type of data to return. Options are `"pass"` or `"fail"`, where the former returns
            a table only containing rows where test units always passed validation steps, and the
            latter returns a table only containing rows had test units that failed in at least one
            validation step.

        Returns
        -------
        FrameT
            A table containing the data that passed or failed the validation steps.

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(preview_incl_header=False)
        ```
        Let's create a `Validate` object with three validation steps and then interrogate the data.

        ```{python}
        import pointblank as pb
        import polars as pl

        tbl = pl.DataFrame(
            {
                "a": [7, 6, 9, 7, 3, 2],
                "b": [9, 8, 10, 5, 10, 6],
                "c": ["c", "d", "a", "b", "a", "b"]
            }
        )

        validation = (
            pb.Validate(data=tbl)
            .col_vals_gt(columns="a", value=5)
            .col_vals_in_set(columns="c", set=["a", "b"])
            .interrogate()
        )

        validation
        ```

        From the validation table, we can see that the first and second steps each had 4 passing
        test units. A failing test unit will mark the entire row as failing in the context of the
        `get_sundered_data()` method. We can use this method to get the rows of data that passed the
        during interrogation.

        ```{python}
        pb.preview(validation.get_sundered_data())
        ```

        The returned DataFrame contains the rows that passed all validation steps (we passed this
        object to [`preview()`](`pointblank.preview`) to show it in an HTML view). From the six-row
        input DataFrame, the first two rows and the last two rows had test units that failed
        validation. Thus the middle two rows are the only ones that passed all validation steps and
        that's what we see in the returned DataFrame.
        """

        # Keep only the validation steps that:
        # - are row-based (included in `ROW_BASED_VALIDATION_TYPES`)
        # - are `active`
        validation_info = [
            validation
            for validation in self.validation_info
            if validation.assertion_type in ROW_BASED_VALIDATION_TYPES and validation.active
        ]

        # TODO: ensure that the stored evaluation tables across all steps have not been mutated
        # from the original table (via any `pre=` functions)

        # Obtain the validation steps that are to be used for sundering
        validation_steps_i = [validation.assertion_type for validation in validation_info]

        if len(validation_steps_i) == 0:
            if type == "pass":
                return self.data
            if type == "fail":
                return self.data[0:0]

        # Get an indexed version of the data
        # TODO: add argument for user to specify the index column name
        index_name = "pb_index_"

        data_nw = nw.from_native(self.data)

        # Handle LazyFrame row indexing which requires order_by parameter
        try:
            # Try without order_by first (for DataFrames)
            data_nw = data_nw.with_row_index(name=index_name)
        except TypeError:  # pragma: no cover
            # LazyFrames require order_by parameter: use first column for ordering
            first_col = data_nw.columns[0]  # pragma: no cover
            data_nw = data_nw.with_row_index(
                name=index_name, order_by=first_col
            )  # pragma: no cover

        # Get all validation step result tables and join together the `pb_is_good_` columns
        # ensuring that the columns are named uniquely (e.g., `pb_is_good_1`, `pb_is_good_2`, ...)
        # and that the index is reset
        for i, validation in enumerate(validation_info):
            results_tbl = nw.from_native(validation.tbl_checked)

            # Add row numbers to the results table
            try:
                # Try without order_by first (for DataFrames)
                results_tbl = results_tbl.with_row_index(name=index_name)
            except TypeError:  # pragma: no cover
                # LazyFrames require order_by parameter: use first column for ordering
                first_col = results_tbl.columns[0]  # pragma: no cover
                results_tbl = results_tbl.with_row_index(
                    name=index_name, order_by=first_col
                )  # pragma: no cover

            # Add numerical suffix to the `pb_is_good_` column to make it unique
            results_tbl = results_tbl.select([index_name, "pb_is_good_"]).rename(
                {"pb_is_good_": f"pb_is_good_{i}"}
            )

            # Add the results table to the list of tables
            if i == 0:
                labeled_tbl_nw = results_tbl
            else:
                labeled_tbl_nw = labeled_tbl_nw.join(results_tbl, on=index_name, how="left")

        # Get list of columns that are the `pb_is_good_` columns
        pb_is_good_cols = [f"pb_is_good_{i}" for i in range(len(validation_steps_i))]

        # Determine the rows that passed all validation steps by checking if all `pb_is_good_`
        # columns are `True`
        labeled_tbl_nw = (
            labeled_tbl_nw.with_columns(
                pb_is_good_all=nw.all_horizontal(pb_is_good_cols, ignore_nulls=True)
            )
            .join(data_nw, on=index_name, how="left")
            .drop(index_name)
        )

        bool_val = True if type == "pass" else False

        sundered_tbl = (
            labeled_tbl_nw.filter(nw.col("pb_is_good_all") == bool_val)
            .drop(pb_is_good_cols + ["pb_is_good_all"])
            .to_native()
        )

        return sundered_tbl

    def get_tabular_report(
        self, title: str | None = ":default:", incl_header: bool = None, incl_footer: bool = None
    ) -> GT:
        """
        Validation report as a GT table.

        The `get_tabular_report()` method returns a GT table object that represents the validation
        report. This validation table provides a summary of the validation results, including the
        validation steps, the number of test units, the number of failing test units, and the
        fraction of failing test units. The table also includes status indicators for the 'warning',
        'error', and 'critical' levels.

        You could simply display the validation table without the use of the `get_tabular_report()`
        method. However, the method provides a way to customize the title of the report. In the
        future this method may provide additional options for customizing the report.

        Parameters
        ----------
        title
            Options for customizing the title of the report. The default is the `":default:"` value
            which produces a generic title. Another option is `":tbl_name:"`, and that presents the
            name of the table as the title for the report. If no title is wanted, then `":none:"`
            can be used. Aside from keyword options, text can be provided for the title. This will
            be interpreted as Markdown text and transformed internally to HTML.

        Returns
        -------
        GT
            A GT table object that represents the validation report.

        Examples
        --------
        Let's create a `Validate` object with a few validation steps and then interrogate the data
        table to see how it performs against the validation plan. We can then generate a tabular
        report to get a summary of the results.

        ```{python}
        import pointblank as pb
        import polars as pl

        # Create a Polars DataFrame
        tbl_pl = pl.DataFrame({"x": [1, 2, 3, 4], "y": [4, 5, 6, 7]})

        # Validate data using Polars DataFrame
        validation = (
            pb.Validate(data=tbl_pl, tbl_name="tbl_xy", thresholds=(2, 3, 4))
            .col_vals_gt(columns="x", value=1)
            .col_vals_lt(columns="x", value=3)
            .col_vals_le(columns="y", value=7)
            .interrogate()
        )

        # Look at the validation table
        validation
        ```

        The validation table is displayed with a default title ('Validation Report'). We can use the
        `get_tabular_report()` method to customize the title of the report. For example, we can set
        the title to the name of the table by using the `title=":tbl_name:"` option. This will use
        the string provided in the `tbl_name=` argument of the `Validate` object.

        ```{python}
        validation.get_tabular_report(title=":tbl_name:")
        ```

        The title of the report is now set to the name of the table, which is 'tbl_xy'. This can be
        useful if you have multiple tables and want to keep track of which table the validation
        report is for.

        Alternatively, you can provide your own title for the report.

        ```{python}
        validation.get_tabular_report(title="Report for Table XY")
        ```

        The title of the report is now set to 'Report for Table XY'. This can be useful if you want
        to provide a more descriptive title for the report.
        """

        if incl_header is None:
            incl_header = global_config.report_incl_header
        if incl_footer is None:
            incl_footer = global_config.report_incl_footer

        # Do we have a DataFrame library to work with?
        _check_any_df_lib(method_used="get_tabular_report")

        # Select the DataFrame library
        df_lib = _select_df_lib(preference="polars")

        # Get information on the input data table
        tbl_info = _get_tbl_type(data=self.data)

        # If the table is a Polars one, determine if it's a LazyFrame
        if tbl_info == "polars":
            if _is_lazy_frame(self.data):
                tbl_info = "polars-lazy"  # pragma: no cover

        # Determine if the input table is a Narwhals DF
        if _is_narwhals_table(self.data):
            # Determine if the Narwhals table is a LazyFrame
            if _is_lazy_frame(self.data):  # pragma: no cover
                tbl_info = "narwhals-lazy"  # pragma: no cover
            else:
                tbl_info = "narwhals"  # pragma: no cover

        # Get the thresholds object
        thresholds = self.thresholds

        # Get the language for the report
        lang = self.lang

        # Get the locale for the report
        locale = self.locale

        # Define the order of columns
        column_order = [
            "status_color",
            "i",
            "type_upd",
            "columns_upd",
            "values_upd",
            "tbl",
            "eval",
            "test_units",
            "pass",
            "fail",
            "w_upd",
            "e_upd",
            "c_upd",
            "extract_upd",
        ]

        if lang in RTL_LANGUAGES:
            # Reverse the order of the columns for RTL languages
            column_order.reverse()

        # Set up before/after to left/right mapping depending on the language (LTR or RTL)
        before = "left" if lang not in RTL_LANGUAGES else "right"
        after = "right" if lang not in RTL_LANGUAGES else "left"

        # Determine if there are any validation steps
        no_validation_steps = len(self.validation_info) == 0

        # If there are no steps, prepare a fairly empty table with a message indicating that there
        # are no validation steps
        if no_validation_steps:
            # Create the title text
            title_text = _get_title_text(
                title=title,
                tbl_name=self.tbl_name,
                interrogation_performed=False,
                lang=lang,
            )

            # Create the label, table type, and thresholds HTML fragments
            label_html = _create_label_html(label=self.label, start_time="")
            table_type_html = _create_table_type_html(tbl_type=tbl_info, tbl_name=self.tbl_name)
            thresholds_html = _create_thresholds_html(
                thresholds=thresholds, locale=locale, df_lib=df_lib
            )

            # Compose the subtitle HTML fragment
            combined_subtitle = (
                "<div>"
                f"{label_html}"
                '<div style="padding-top: 10px; padding-bottom: 5px;">'
                f"{table_type_html}"
                f"{thresholds_html}"
                "</div>"
                "</div>"
            )

            df = df_lib.DataFrame(
                {
                    "status_color": "",
                    "i": "",
                    "type_upd": VALIDATION_REPORT_TEXT["no_validation_steps_text"][lang],
                    "columns_upd": "",
                    "values_upd": "",
                    "tbl": "",
                    "eval": "",
                    "test_units": "",
                    "pass": "",
                    "fail": "",
                    "w_upd": "",
                    "e_upd": "",
                    "c_upd": "",
                    "extract_upd": "",
                }
            )

            gt_tbl = (
                GT(df, id="pb_tbl")
                .fmt_markdown(columns=["pass", "fail", "extract_upd"])
                .opt_table_font(font=google_font(name="IBM Plex Sans"))
                .opt_align_table_header(align=before)
                .tab_style(style=style.css("height: 20px;"), locations=loc.body())
                .tab_style(
                    style=style.text(weight="bold", color="#666666"), locations=loc.column_labels()
                )
                .tab_style(
                    style=style.text(size="28px", weight="bold", align=before, color="#444444"),
                    locations=loc.title(),
                )
                .tab_style(
                    style=[
                        style.fill(color="#FED8B1"),
                        style.text(weight="bold", size="14px"),
                        style.css("overflow-x: visible; white-space: nowrap;"),
                    ],
                    locations=loc.body(),
                )
                .tab_style(
                    style=style.text(align=before),
                    locations=[loc.title(), loc.subtitle(), loc.footer()],
                )
                .cols_label(
                    cases={
                        "status_color": "",
                        "i": "",
                        "type_upd": VALIDATION_REPORT_TEXT["report_col_step"][lang],
                        "columns_upd": VALIDATION_REPORT_TEXT["report_col_columns"][lang],
                        "values_upd": VALIDATION_REPORT_TEXT["report_col_values"][lang],
                        "tbl": "TBL",
                        "eval": "EVAL",
                        "test_units": VALIDATION_REPORT_TEXT["report_col_units"][lang],
                        "pass": VALIDATION_REPORT_TEXT["report_col_pass"][lang],
                        "fail": VALIDATION_REPORT_TEXT["report_col_fail"][lang],
                        "w_upd": "W",
                        "e_upd": "E",
                        "c_upd": "C",
                        "extract_upd": "EXT",
                    }
                )
                .cols_width(
                    cases={
                        "status_color": "4px",
                        "i": "35px",
                        "type_upd": "190px",
                        "columns_upd": "120px",
                        "values_upd": "120px",
                        "tbl": "50px",
                        "eval": "50px",
                        "test_units": "60px",
                        "pass": "60px",
                        "fail": "60px",
                        "w_upd": "30px",
                        "e_upd": "30px",
                        "c_upd": "30px",
                        "extract_upd": "65px",
                    }
                )
                .cols_align(
                    align="center",
                    columns=["tbl", "eval", "w_upd", "e_upd", "c_upd", "extract_upd"],
                )
                .cols_align(align="right", columns=["test_units", "pass", "fail"])
                .cols_align(align=before, columns=["type_upd", "columns_upd", "values_upd"])
                .cols_move_to_start(columns=column_order)
                .tab_options(table_font_size="90%")
                .tab_source_note(
                    source_note=VALIDATION_REPORT_TEXT["use_validation_methods_text"][lang]
                )
            )

            if lang in RTL_LANGUAGES:
                gt_tbl = gt_tbl.tab_style(
                    style=style.css("direction: rtl;"), locations=loc.source_notes()
                )  # pragma: no cover

            if incl_header:
                gt_tbl = gt_tbl.tab_header(title=html(title_text), subtitle=html(combined_subtitle))

            # If the version of `great_tables` is `>=0.17.0` then disable Quarto table processing
            if version("great_tables") >= "0.17.0":
                gt_tbl = gt_tbl.tab_options(quarto_disable_processing=True)

            return gt_tbl

        # Convert the `validation_info` object to a dictionary
        validation_info_dict = _validation_info_as_dict(validation_info=self.validation_info)

        # Has the validation been performed? We can check the first `time_processed` entry in the
        # dictionary to see if it is `None` or not; The output of many cells in the reporting table
        # will be made blank if the validation has not been performed
        interrogation_performed = validation_info_dict.get("proc_duration_s", [None])[0] is not None

        # Determine which steps are those using segmented data
        segmented_steps = [
            i + 1
            for i, segment in enumerate(validation_info_dict["segments"])
            if segment is not None
        ]

        # ------------------------------------------------
        # Process the `type_upd` entry
        # ------------------------------------------------

        # Add the `type_upd` entry to the dictionary
        validation_info_dict["type_upd"] = _transform_assertion_str(
            assertion_str=validation_info_dict["assertion_type"],
            brief_str=validation_info_dict["brief"],
            autobrief_str=validation_info_dict["autobrief"],
            segmentation_str=validation_info_dict["segments"],
            lang=lang,
        )

        # Remove the `brief` entry from the dictionary
        validation_info_dict.pop("brief")

        # Remove the `autobrief` entry from the dictionary
        validation_info_dict.pop("autobrief")

        # ------------------------------------------------
        # Process the `columns_upd` entry
        # ------------------------------------------------

        columns_upd = []

        columns = validation_info_dict["column"]

        assertion_type = validation_info_dict["assertion_type"]

        # Iterate over the values in the `column` entry
        for i, column in enumerate(columns):
            if assertion_type[i] in [
                "col_schema_match",
                "row_count_match",
                "col_count_match",
                "col_vals_expr",
            ]:
                columns_upd.append("&mdash;")
            elif assertion_type[i] in ["rows_distinct", "rows_complete", "prompt"]:
                if not column:
                    # If there is no column subset, then all columns are used
                    columns_upd.append("ALL COLUMNS")
                else:
                    # With a column subset list, format with commas between the column names
                    columns_upd.append(", ".join(column))

            elif assertion_type[i] in ["conjointly", "specially"]:
                columns_upd.append("")
            else:
                columns_upd.append(str(column))

        # Add the `columns_upd` entry to the dictionary
        validation_info_dict["columns_upd"] = columns_upd

        # ------------------------------------------------
        # Process the `values_upd` entry
        # ------------------------------------------------

        # Here, `values` will be transformed in ways particular to the assertion type (e.g.,
        # single values, ranges, sets, etc.)

        # Create a list to store the transformed values
        values_upd = []

        values = validation_info_dict["values"]
        assertion_type = validation_info_dict["assertion_type"]
        inclusive = validation_info_dict["inclusive"]
        active = validation_info_dict["active"]
        eval_error = validation_info_dict["eval_error"]

        # Iterate over the values in the `values` entry
        for i, value in enumerate(values):
            # If the assertion type is a comparison of one value then add the value as a string
            if assertion_type[i] in [
                "col_vals_gt",
                "col_vals_lt",
                "col_vals_eq",
                "col_vals_ne",
                "col_vals_ge",
                "col_vals_le",
            ]:
                values_upd.append(str(value))

            # If the assertion type is a comparison of values within or outside of a range, add
            # the appropriate brackets (inclusive or exclusive) to the values
            elif assertion_type[i] in ["col_vals_between", "col_vals_outside"]:
                left_bracket = "[" if inclusive[i][0] else "("
                right_bracket = "]" if inclusive[i][1] else ")"
                values_upd.append(f"{left_bracket}{value[0]}, {value[1]}{right_bracket}")

            # If the assertion type is a comparison of a set of values; strip the leading and
            # trailing square brackets and single quotes
            elif assertion_type[i] in ["col_vals_in_set", "col_vals_not_in_set"]:
                values_upd.append(str(value)[1:-1].replace("'", ""))

            # Certain assertion types don't have an associated value, so use an em dash for those
            elif assertion_type[i] in [
                "col_vals_null",
                "col_vals_not_null",
                "col_exists",
                "rows_distinct",
                "rows_complete",
            ]:
                values_upd.append("&mdash;")

            elif assertion_type[i] in ["col_schema_match"]:
                values_upd.append("SCHEMA")

            elif assertion_type[i] in ["col_vals_expr", "conjointly"]:
                values_upd.append("COLUMN EXPR")

            elif assertion_type[i] in ["row_count_match", "col_count_match"]:
                count = values[i]["count"]
                inverse = values[i]["inverse"]

                if inverse:
                    count = f"&ne; {count}"

                values_upd.append(str(count))

            elif assertion_type[i] in ["specially"]:
                values_upd.append("EXPR")

            elif assertion_type[i] in ["col_vals_regex"]:
                pattern = value["pattern"]

                values_upd.append(str(pattern))

            elif assertion_type[i] in ["prompt"]:  # pragma: no cover
                # For AI validation, show only the prompt, not the full config
                if isinstance(value, dict) and "prompt" in value:  # pragma: no cover
                    values_upd.append(value["prompt"])  # pragma: no cover
                else:  # pragma: no cover
                    values_upd.append(str(value))  # pragma: no cover

            # If the assertion type is not recognized, add the value as a string
            else:  # pragma: no cover
                values_upd.append(str(value))  # pragma: no cover

        # Remove the `inclusive` entry from the dictionary
        validation_info_dict.pop("inclusive")

        # Add the `values_upd` entry to the dictionary
        validation_info_dict["values_upd"] = values_upd

        ## ------------------------------------------------
        ## The following entries rely on an interrogation
        ## to have been performed
        ## ------------------------------------------------

        # ------------------------------------------------
        # Add the `tbl` entry
        # ------------------------------------------------

        # Depending on if there was some preprocessing done, get the appropriate icon for
        # the table processing status to be displayed in the report under the `tbl` column
        # TODO: add the icon for the segmented data option when the step is segmented

        validation_info_dict["tbl"] = _transform_tbl_preprocessed(
            pre=validation_info_dict["pre"],
            seg=validation_info_dict["segments"],
            interrogation_performed=interrogation_performed,
        )

        # ------------------------------------------------
        # Add the `eval` entry
        # ------------------------------------------------

        # Add the `eval` entry to the dictionary

        validation_info_dict["eval"] = _transform_eval(
            n=validation_info_dict["n"],
            interrogation_performed=interrogation_performed,
            eval_error=eval_error,
            active=active,
        )

        # Remove the `eval_error` entry from the dictionary
        validation_info_dict.pop("eval_error")

        # ------------------------------------------------
        # Process the `test_units` entry
        # ------------------------------------------------

        # Add the `test_units` entry to the dictionary
        validation_info_dict["test_units"] = _transform_test_units(
            test_units=validation_info_dict["n"],
            interrogation_performed=interrogation_performed,
            active=active,
            locale=locale,
            df_lib=df_lib,
        )

        # ------------------------------------------------
        # Process `pass` and `fail` entries
        # ------------------------------------------------

        # Create a `pass` entry that concatenates the `n_passed` and `n_failed` entries
        # (the length of the `pass` entry should be equal to the length of the
        # `n_passed` and `n_failed` entries)

        validation_info_dict["pass"] = _transform_passed_failed(
            n_passed_failed=validation_info_dict["n_passed"],
            f_passed_failed=validation_info_dict["f_passed"],
            interrogation_performed=interrogation_performed,
            active=active,
            locale=locale,
            df_lib=df_lib,
        )

        validation_info_dict["fail"] = _transform_passed_failed(
            n_passed_failed=validation_info_dict["n_failed"],
            f_passed_failed=validation_info_dict["f_failed"],
            interrogation_performed=interrogation_performed,
            active=active,
            locale=locale,
            df_lib=df_lib,
        )

        # ------------------------------------------------
        # Process `w_upd`, `e_upd`, `c_upd` entries
        # ------------------------------------------------

        # Transform 'warning', 'error', and 'critical' to `w_upd`, `e_upd`, and `c_upd` entries
        validation_info_dict["w_upd"] = _transform_w_e_c(
            values=validation_info_dict["warning"],
            color=SEVERITY_LEVEL_COLORS["warning"],
            interrogation_performed=interrogation_performed,
        )
        validation_info_dict["e_upd"] = _transform_w_e_c(
            values=validation_info_dict["error"],
            color=SEVERITY_LEVEL_COLORS["error"],
            interrogation_performed=interrogation_performed,
        )
        validation_info_dict["c_upd"] = _transform_w_e_c(
            values=validation_info_dict["critical"],
            color=SEVERITY_LEVEL_COLORS["critical"],
            interrogation_performed=interrogation_performed,
        )

        # ------------------------------------------------
        # Process `status_color` entry
        # ------------------------------------------------

        # For the `status_color` entry, we will add a string based on the status of the validation:
        #
        # CASE 1: if `all_passed` is `True`, then the status color will be green
        # CASE 2: If `critical` is `True`, then the status color will be red (#FF3300)
        # CASE 3: If `error` is `True`, then the status color will be yellow (#EBBC14)
        # CASE 4: If `warning` is `True`, then the status color will be gray (#AAAAAA)
        # CASE 5: If none of `warning`, `error`, or `critical` are `True`, then the status color
        #   will be light green (includes alpha of `0.5`)

        # Create a list to store the status colors
        status_color_list = []

        # Iterate over the validation steps in priority order
        for i in range(len(validation_info_dict["type_upd"])):
            if validation_info_dict["all_passed"][i]:
                status_color_list.append(SEVERITY_LEVEL_COLORS["green"])  # CASE 1
            elif validation_info_dict["critical"][i]:
                status_color_list.append(SEVERITY_LEVEL_COLORS["critical"])  # CASE 2
            elif validation_info_dict["error"][i]:
                status_color_list.append(SEVERITY_LEVEL_COLORS["error"])  # CASE 3
            elif validation_info_dict["warning"][i]:
                status_color_list.append(SEVERITY_LEVEL_COLORS["warning"])  # CASE 4
            else:
                # No threshold exceeded for {W, E, C} and NOT `all_passed`
                status_color_list.append(SEVERITY_LEVEL_COLORS["green"] + "66")  # CASE 5

        # Add the `status_color` entry to the dictionary
        validation_info_dict["status_color"] = status_color_list

        # ------------------------------------------------
        # Process the extract entry
        # ------------------------------------------------

        # Create a list to store the extract colors
        extract_upd = []

        # Iterate over the validation steps
        for i in range(len(validation_info_dict["type_upd"])):
            # If the extract for this step is `None`, then produce an em dash then go to the next
            # iteration
            if validation_info_dict["extract"][i] is None:
                extract_upd.append("&mdash;")
                continue

            # If the extract for this step is not `None`, then produce a button that allows the
            # user to download the extract as a CSV file

            # Get the step number
            step_num = i + 1

            # Get the extract for this step
            extract = validation_info_dict["extract"][i]

            # Transform to Narwhals DataFrame
            extract_nw = nw.from_native(extract)

            # Get the number of rows in the extract (safe for LazyFrames)
            try:
                n_rows = len(extract_nw)
            except TypeError:  # pragma: no cover
                # For LazyFrames, collect() first to get length
                n_rows = (
                    len(extract_nw.collect()) if hasattr(extract_nw, "collect") else 0
                )  # pragma: no cover

            # If the number of rows is zero, then produce an em dash then go to the next iteration
            if n_rows == 0:
                extract_upd.append("&mdash;")
                continue

            # Write the CSV text (ensure LazyFrames are collected first)
            if hasattr(extract_nw, "collect"):  # pragma: no cover
                extract_nw = extract_nw.collect()
            csv_text = extract_nw.write_csv()

            # Use Base64 encoding to encode the CSV text
            csv_text_encoded = base64.b64encode(csv_text.encode("utf-8")).decode("utf-8")

            output_file_name = f"extract_{format(step_num, '04d')}.csv"

            # Create the download button
            button = (
                f'<a href="data:text/csv;base64,{csv_text_encoded}" download="{output_file_name}">'
                "<button "
                # TODO: Add a tooltip for the button
                #'aria-label="Download Extract" data-balloon-pos="left" '
                'style="background-color: #67C2DC; color: #FFFFFF; border: none; padding: 5px; '
                'font-weight: bold; cursor: pointer; border-radius: 4px;">CSV</button>'
                "</a>"
            )

            extract_upd.append(button)

        # Add the `extract_upd` entry to the dictionary
        validation_info_dict["extract_upd"] = extract_upd

        # Remove the `extract` entry from the dictionary
        validation_info_dict.pop("extract")

        # ------------------------------------------------
        # Removals from the dictionary
        # ------------------------------------------------

        # Remove the `assertion_type` entry from the dictionary
        validation_info_dict.pop("assertion_type")

        # Remove the `column` entry from the dictionary
        validation_info_dict.pop("column")

        # Remove the `values` entry from the dictionary
        validation_info_dict.pop("values")

        # Remove the `n` entry from the dictionary
        validation_info_dict.pop("n")

        # Remove the `pre` entry from the dictionary
        validation_info_dict.pop("pre")

        # Remove the `segments` entry from the dictionary
        validation_info_dict.pop("segments")

        # Remove the `proc_duration_s` entry from the dictionary
        validation_info_dict.pop("proc_duration_s")

        # Remove `n_passed`, `n_failed`, `f_passed`, and `f_failed` entries from the dictionary
        validation_info_dict.pop("n_passed")
        validation_info_dict.pop("n_failed")
        validation_info_dict.pop("f_passed")
        validation_info_dict.pop("f_failed")

        # Remove the `warning`, `error`, and `critical` entries from the dictionary
        validation_info_dict.pop("warning")
        validation_info_dict.pop("error")
        validation_info_dict.pop("critical")

        # Drop other keys from the dictionary
        validation_info_dict.pop("na_pass")
        validation_info_dict.pop("label")
        validation_info_dict.pop("active")
        validation_info_dict.pop("all_passed")

        # If no interrogation performed, populate the `i` entry with a sequence of integers
        # from `1` to the number of validation steps
        if not interrogation_performed:
            validation_info_dict["i"] = list(range(1, len(validation_info_dict["type_upd"]) + 1))

        # Create a table time string
        table_time = _create_table_time_html(time_start=self.time_start, time_end=self.time_end)

        # Create the title text
        title_text = _get_title_text(
            title=title,
            tbl_name=self.tbl_name,
            interrogation_performed=interrogation_performed,
            lang=lang,
        )

        # Create the label, table type, and thresholds HTML fragments
        label_html = _create_label_html(label=self.label, start_time=self.time_start)
        table_type_html = _create_table_type_html(tbl_type=tbl_info, tbl_name=self.tbl_name)
        thresholds_html = _create_thresholds_html(
            thresholds=thresholds, locale=locale, df_lib=df_lib
        )

        # Compose the subtitle HTML fragment
        combined_subtitle = (
            "<div>"
            f"{label_html}"
            '<div style="padding-top: 10px; padding-bottom: 5px;">'
            f"{table_type_html}"
            f"{thresholds_html}"
            "</div>"
            "</div>"
        )

        # Create a DataFrame from the validation information using whatever the `df_lib` library is;
        # (it is either Polars or Pandas)
        df = df_lib.DataFrame(validation_info_dict)

        # Return the DataFrame as a Great Tables table
        gt_tbl = (
            GT(df, id="pb_tbl")
            .fmt_markdown(columns=["pass", "fail", "extract_upd"])
            .opt_table_font(font=google_font(name="IBM Plex Sans"))
            .opt_align_table_header(align=before)
            .tab_style(style=style.css("height: 40px;"), locations=loc.body())
            .tab_style(
                style=style.text(weight="bold", color="#666666", size="13px"),
                locations=loc.body(columns="i"),
            )
            .tab_style(
                style=style.text(weight="bold", color="#666666"), locations=loc.column_labels()
            )
            .tab_style(
                style=style.text(size="28px", weight="bold", align=before, color="#444444"),
                locations=loc.title(),
            )
            .tab_style(
                style=style.text(
                    color="black", font=google_font(name="IBM Plex Mono"), size="11px"
                ),
                locations=loc.body(
                    columns=["type_upd", "columns_upd", "values_upd", "test_units", "pass", "fail"]
                ),
            )
            .tab_style(
                style=style.css("overflow-x: visible; white-space: nowrap;"),
                locations=loc.body(columns="type_upd", rows=segmented_steps),
            )
            .tab_style(
                style=style.fill(color="#FCFCFC" if interrogation_performed else "white"),
                locations=loc.body(columns=["w_upd", "e_upd", "c_upd"]),
            )
            .tab_style(
                style=style.fill(color="#FCFCFC" if interrogation_performed else "white"),
                locations=loc.body(columns=["tbl", "eval"]),
            )
            .tab_style(
                style=style.borders(sides=before, color="#E5E5E5", style="dashed"),
                locations=loc.body(columns=["columns_upd", "values_upd"]),
            )
            .tab_style(
                style=style.text(align=before),
                locations=[loc.title(), loc.subtitle(), loc.footer()],
            )
            .tab_style(
                style=style.borders(
                    sides=before,
                    color="#E5E5E5",
                    style="dashed" if interrogation_performed else "none",
                ),
                locations=loc.body(columns=["pass", "fail"]),
            )
            .tab_style(
                style=style.borders(
                    sides=after,
                    color="#D3D3D3",
                    style="solid" if interrogation_performed else "none",
                ),
                locations=loc.body(columns="c_upd"),
            )
            .tab_style(
                style=style.borders(
                    sides=before,
                    color="#D3D3D3",
                    style="solid" if interrogation_performed else "none",
                ),
                locations=loc.body(columns="w_upd"),
            )
            .tab_style(
                style=style.borders(
                    sides=after,
                    color="#D3D3D3",
                    style="solid" if interrogation_performed else "none",
                ),
                locations=loc.body(columns="eval"),
            )
            .tab_style(
                style=style.borders(sides=before, color="#D3D3D3", style="solid"),
                locations=loc.body(columns="tbl"),
            )
            .tab_style(
                style=style.fill(
                    color=from_column(column="status_color") if interrogation_performed else "white"
                ),
                locations=loc.body(columns="status_color"),
            )
            .tab_style(
                style=style.text(color="transparent", size="0px"),
                locations=loc.body(columns="status_color"),
            )
            .tab_style(
                style=style.css("white-space: nowrap; text-overflow: ellipsis; overflow: hidden;"),
                locations=loc.body(columns=["columns_upd", "values_upd"]),
            )
            .cols_label(
                cases={
                    "status_color": "",
                    "i": "",
                    "type_upd": VALIDATION_REPORT_TEXT["report_col_step"][lang],
                    "columns_upd": VALIDATION_REPORT_TEXT["report_col_columns"][lang],
                    "values_upd": VALIDATION_REPORT_TEXT["report_col_values"][lang],
                    "tbl": "TBL",
                    "eval": "EVAL",
                    "test_units": VALIDATION_REPORT_TEXT["report_col_units"][lang],
                    "pass": VALIDATION_REPORT_TEXT["report_col_pass"][lang],
                    "fail": VALIDATION_REPORT_TEXT["report_col_fail"][lang],
                    "w_upd": "W",
                    "e_upd": "E",
                    "c_upd": "C",
                    "extract_upd": "EXT",
                }
            )
            .cols_width(
                cases={
                    "status_color": "4px",
                    "i": "35px",
                    "type_upd": "190px",
                    "columns_upd": "120px",
                    "values_upd": "120px",
                    "tbl": "50px",
                    "eval": "50px",
                    "test_units": "60px",
                    "pass": "60px",
                    "fail": "60px",
                    "w_upd": "30px",
                    "e_upd": "30px",
                    "c_upd": "30px",
                    "extract_upd": "65px",
                }
            )
            .cols_align(
                align="center", columns=["tbl", "eval", "w_upd", "e_upd", "c_upd", "extract_upd"]
            )
            .cols_align(align="right", columns=["test_units", "pass", "fail"])
            .cols_align(align=before, columns=["type_upd", "columns_upd", "values_upd"])
            .cols_move_to_start(columns=column_order)
            .tab_options(table_font_size="90%")
        )

        if incl_header:
            gt_tbl = gt_tbl.tab_header(title=html(title_text), subtitle=html(combined_subtitle))

        if incl_footer:
            gt_tbl = gt_tbl.tab_source_note(source_note=html(table_time))

        # If the interrogation has not been performed, then style the table columns dealing with
        # interrogation data as grayed out
        if not interrogation_performed:
            gt_tbl = gt_tbl.tab_style(
                style=style.fill(color="#F2F2F2"),
                locations=loc.body(
                    columns=["tbl", "eval", "test_units", "pass", "fail", "w_upd", "e_upd", "c_upd"]
                ),
            )

        # Transform `active` to a list of indices of inactive validations
        inactive_steps = [i for i, active in enumerate(active) if not active]

        # If there are inactive steps, then style those rows to be grayed out
        if inactive_steps:
            gt_tbl = gt_tbl.tab_style(
                style=style.fill(color="#F2F2F2"),
                locations=loc.body(rows=inactive_steps),
            )

        # Transform `eval_error` to a list of indices of validations with evaluation errors

        # If there are evaluation errors, then style those rows to be red
        if eval_error:
            gt_tbl = gt_tbl.tab_style(
                style=style.fill(color="#FFC1C159"),
                locations=loc.body(rows=[i for i, error in enumerate(eval_error) if error]),
            )
            gt_tbl = gt_tbl.tab_style(
                style=style.text(color="#B22222"),
                locations=loc.body(
                    columns="columns_upd", rows=[i for i, error in enumerate(eval_error) if error]
                ),
            )

        # If the version of `great_tables` is `>=0.17.0` then disable Quarto table processing
        if version("great_tables") >= "0.17.0":
            gt_tbl = gt_tbl.tab_options(quarto_disable_processing=True)

        return gt_tbl

    def get_step_report(
        self,
        i: int,
        columns_subset: str | list[str] | Column | None = None,
        header: str = ":default:",
        limit: int | None = 10,
    ) -> GT:
        """
        Get a detailed report for a single validation step.

        The `get_step_report()` method returns a report of what went well---or what failed
        spectacularly---for a given validation step. The report includes a summary of the validation
        step and a detailed breakdown of the interrogation results. The report is presented as a GT
        table object, which can be displayed in a notebook or exported to an HTML file.

        :::{.callout-warning}
        The `get_step_report()` method is still experimental. Please report any issues you encounter
        in the [Pointblank issue tracker](https://github.com/posit-dev/pointblank/issues).
        :::

        Parameters
        ----------
        i
            The step number for which to get the report.
        columns_subset
            The columns to display in a step report that shows errors in the input table. By default
            all columns are shown (`None`). If a subset of columns is desired, we can provide a list
            of column names, a string with a single column name, a `Column` object, or a
            `ColumnSelector` object. The last two options allow for more flexible column selection
            using column selector functions. Errors are raised if the column names provided don't
            match any columns in the table (when provided as a string or list of strings) or if
            column selector expressions don't resolve to any columns.
        header
            Options for customizing the header of the step report. The default is the `":default:"`
            value which produces a header with a standard title and set of details underneath. Aside
            from this default, free text can be provided for the header. This will be interpreted as
            Markdown text and transformed internally to HTML. You can provide one of two templating
            elements: `{title}` and `{details}`. The default header has the template
            `"{title}{details}"` so you can easily start from that and modify as you see fit. If you
            don't want a header at all, you can set `header=None` to remove it entirely.
        limit
            The number of rows to display for those validation steps that check values in rows (the
            `col_vals_*()` validation steps). The default is `10` rows and the limit can be removed
            entirely by setting `limit=None`.

        Returns
        -------
        GT
            A GT table object that represents the detailed report for the validation step.

        Types of Step Reports
        ---------------------
        The `get_step_report()` method produces a report based on the *type* of validation step.
        The following column-value or row-based validation step validation methods will produce a
        report that shows the rows of the data that failed:

        - [`col_vals_gt()`](`pointblank.Validate.col_vals_gt`)
        - [`col_vals_ge()`](`pointblank.Validate.col_vals_ge`)
        - [`col_vals_lt()`](`pointblank.Validate.col_vals_lt`)
        - [`col_vals_le()`](`pointblank.Validate.col_vals_le`)
        - [`col_vals_eq()`](`pointblank.Validate.col_vals_eq`)
        - [`col_vals_ne()`](`pointblank.Validate.col_vals_ne`)
        - [`col_vals_between()`](`pointblank.Validate.col_vals_between`)
        - [`col_vals_outside()`](`pointblank.Validate.col_vals_outside`)
        - [`col_vals_in_set()`](`pointblank.Validate.col_vals_in_set`)
        - [`col_vals_not_in_set()`](`pointblank.Validate.col_vals_not_in_set`)
        - [`col_vals_null()`](`pointblank.Validate.col_vals_null`)
        - [`col_vals_not_null()`](`pointblank.Validate.col_vals_not_null`)
        - [`col_vals_regex()`](`pointblank.Validate.col_vals_regex`)
        - [`col_vals_expr()`](`pointblank.Validate.col_vals_expr`)
        - [`conjointly()`](`pointblank.Validate.conjointly`)
        - [`rows_complete()`](`pointblank.Validate.rows_complete`)

        The [`rows_distinct()`](`pointblank.Validate.rows_distinct`) validation step will produce a
        report that shows duplicate rows (or duplicate values in one or a set of columns as defined
        in that method's `columns_subset=` parameter.

        The [`col_schema_match()`](`pointblank.Validate.col_schema_match`) validation step will
        produce a report that shows the schema of the data table and the schema of the validation
        step. The report will indicate whether the schemas match or not.

        Examples
        --------
        ```{python}
        #| echo: false
        #| output: false
        import pointblank as pb
        pb.config(report_incl_header=False, report_incl_footer=False, preview_incl_header=False)
        ```
        Let's create a validation plan with a few validation steps and interrogate the data. With
        that, we'll have a look at the validation reporting table for the entire collection of
        steps and what went well or what failed.

        ```{python}
        import pointblank as pb

        validation = (
            pb.Validate(
                data=pb.load_dataset(dataset="small_table", tbl_type="pandas"),
                tbl_name="small_table",
                label="Example for the get_step_report() method",
                thresholds=(1, 0.20, 0.40)
            )
            .col_vals_lt(columns="d", value=3500)
            .col_vals_between(columns="c", left=1, right=8)
            .col_vals_gt(columns="a", value=3)
            .col_vals_regex(columns="b", pattern=r"[0-9]-[a-z]{3}-[0-9]{3}")
            .interrogate()
        )

        validation
        ```

        There were four validation steps performed, where the first three steps had failing test
        units and the last step had no failures. Let's get a detailed report for the first step by
        using the `get_step_report()` method.

        ```{python}
        validation.get_step_report(i=1)
        ```

        The report for the first step is displayed. The report includes a summary of the validation
        step and a detailed breakdown of the interrogation results. The report provides details on
        what the validation step was checking, the extent to which the test units failed, and a
        table that shows the failing rows of the data with the column of interest highlighted.

        The second and third steps also had failing test units. Reports for those steps can be
        viewed by using `get_step_report(i=2)` and `get_step_report(i=3)` respectively.

        The final step did not have any failing test units. A report for the final step can still be
        viewed by using `get_step_report(i=4)`. The report will indicate that every test unit passed
        and a prview of the target table will be provided.

        ```{python}
        validation.get_step_report(i=4)
        ```

        If you'd like to trim down the number of columns shown in the report, you can provide a
        subset of columns to display. For example, if you only want to see the columns `a`, `b`, and
        `c`, you can provide those column names as a list.

        ```{python}
        validation.get_step_report(i=1, columns_subset=["a", "b", "c"])
        ```

        If you'd like to increase or reduce the maximum number of rows shown in the report, you can
        provide a different value for the `limit` parameter. For example, if you'd like to see only
        up to 5 rows, you can set `limit=5`.

        ```{python}
        validation.get_step_report(i=3, limit=5)
        ```

        Step 3 actually had 7 failing test units, but only the first 5 rows are shown in the step
        report because of the `limit=5` parameter.
        """

        # If the step number is `-99` then enter the debug mode
        debug_return_df = True if i == -99 else False
        i = 1 if debug_return_df else i

        # If the step number is not valid, raise an error
        if i <= 0 and not debug_return_df:
            raise ValueError("Step number must be an integer value greater than 0.")

        # If the step number is not valid, raise an error
        if i not in self._get_validation_dict(i=None, attr="i") and not debug_return_df:
            raise ValueError(f"Step {i} does not exist in the validation plan.")

        # If limit is `0` or less, raise an error
        if limit is not None and limit <= 0:
            raise ValueError("The limit must be an integer value greater than 0.")

        # Convert the `validation_info` object to a dictionary
        validation_info_dict = _validation_info_as_dict(validation_info=self.validation_info)

        # Obtain the language and locale
        lang = self.lang
        locale = self.locale

        # Filter the dictionary to include only the information for the selected step
        validation_step = {
            key: value[i - 1] for key, value in validation_info_dict.items() if key != "i"
        }

        # From `validation_step` pull out key values for the report
        assertion_type = validation_step["assertion_type"]
        column = validation_step["column"]
        values = validation_step["values"]
        inclusive = validation_step["inclusive"]
        all_passed = validation_step["all_passed"]
        n = validation_step["n"]
        n_failed = validation_step["n_failed"]
        active = validation_step["active"]

        # Get the `val_info` dictionary for the step
        val_info = self.validation_info[i - 1].val_info

        # Get the column position in the table
        if column is not None:
            if isinstance(column, str):
                column_list = list(self.data.columns)
                column_position = column_list.index(column) + 1
            elif isinstance(column, list):
                column_position = [list(self.data.columns).index(col) + 1 for col in column]
            else:
                column_position = None  # pragma: no cover
        else:
            column_position = None

        # TODO: Show a report with the validation plan but state that the step is inactive
        # If the step is not active then return a message indicating that the step is inactive
        if not active:
            return "This validation step is inactive."

        # Create a table with a sample of ten rows, highlighting the column of interest
        tbl_preview = preview(
            data=self.data,
            columns_subset=columns_subset,
            n_head=5,
            n_tail=5,
            limit=10,
            min_tbl_width=600,
            incl_header=False,
        )

        # If no rows were extracted, create a message to indicate that no rows were extracted
        # if get_row_count(extract) == 0:
        #    return "No rows were extracted."

        if assertion_type in ROW_BASED_VALIDATION_TYPES + ["rows_complete"]:
            # Get the extracted data for the step
            extract = self.get_data_extracts(i=i, frame=True)

            step_report = _step_report_row_based(
                assertion_type=assertion_type,
                i=i,
                column=column,
                column_position=column_position,
                columns_subset=columns_subset,
                values=values,
                inclusive=inclusive,
                n=n,
                n_failed=n_failed,
                all_passed=all_passed,
                extract=extract,
                tbl_preview=tbl_preview,
                header=header,
                limit=limit,
                lang=lang,
            )

        elif assertion_type == "rows_distinct":
            extract = self.get_data_extracts(i=i, frame=True)

            step_report = _step_report_rows_distinct(
                i=i,
                column=column,
                column_position=column_position,
                columns_subset=columns_subset,
                n=n,
                n_failed=n_failed,
                all_passed=all_passed,
                extract=extract,
                tbl_preview=tbl_preview,
                header=header,
                limit=limit,
                lang=lang,
            )

        elif assertion_type == "col_schema_match":
            # Get the parameters for column-schema matching
            values_dict = validation_step["values"]

            # complete = values_dict["complete"]
            in_order = values_dict["in_order"]

            # CASE I: where ordering of columns is required (`in_order=True`)
            if in_order:
                step_report = _step_report_schema_in_order(
                    step=i,
                    schema_info=val_info,
                    header=header,
                    lang=lang,
                    debug_return_df=debug_return_df,
                )

            # CASE II: where ordering of columns is not required (`in_order=False`)
            if not in_order:
                step_report = _step_report_schema_any_order(
                    step=i,
                    schema_info=val_info,
                    header=header,
                    lang=lang,
                    debug_return_df=debug_return_df,
                )

        else:
            step_report = None  # pragma: no cover

        return step_report

    def _add_validation(self, validation_info):
        """
        Add a validation to the list of validations.

        Parameters
        ----------
        validation_info
            Information about the validation to add.
        """

        # Get the largest value of `i_o` in the `validation_info`
        max_i_o = max([validation.i_o for validation in self.validation_info], default=0)

        # Set the `i_o` attribute to the largest value of `i_o` plus 1
        validation_info.i_o = max_i_o + 1

        self.validation_info.append(validation_info)

        return self

    def _evaluate_column_exprs(self, validation_info):
        """
        Evaluate any column expressions stored in the `column` attribute and expand those validation
        steps into multiple. Errors in evaluation (such as no columns matched) will be caught and
        recorded in the `eval_error` attribute.

        Parameters
        ----------
        validation_info
            Information about the validation to evaluate and expand.
        """

        # Create a list to store the expanded validation steps
        expanded_validation_info = []

        # Iterate over the validation steps
        for i, validation in enumerate(validation_info):
            # Get the column expression
            column_expr = validation.column

            # If the value is not a Column object, then skip the evaluation and append
            # the validation step to the list of expanded validation steps
            if not isinstance(column_expr, Column):
                expanded_validation_info.append(validation)
                continue

            # Evaluate the column expression
            try:
                # Get the table for this step, it can either be:
                # 1. the target table itself
                # 2. the target table modified by a `pre` attribute

                if validation.pre is None:
                    table = self.data
                else:
                    table = validation.pre(self.data)

                # Get the columns from the table as a list
                columns = list(table.columns)

                # Evaluate the column expression
                if isinstance(column_expr, ColumnSelectorNarwhals):
                    columns_resolved = ColumnSelectorNarwhals(column_expr).resolve(table=table)
                else:
                    columns_resolved = column_expr.resolve(columns=columns, table=table)

            except Exception:  # pragma: no cover
                validation.eval_error = True

            # If no columns were resolved, then create a patched validation step with the
            # `eval_error` and `column` attributes set
            if not columns_resolved:
                validation.eval_error = True
                validation.column = str(column_expr)

                expanded_validation_info.append(validation)
                continue

            # For each column resolved, create a new validation step and add it to the list of
            # expanded validation steps
            for column in columns_resolved:
                new_validation = copy.deepcopy(validation)

                new_validation.column = column

                expanded_validation_info.append(new_validation)

        # Replace the `validation_info` attribute with the expanded version
        self.validation_info = expanded_validation_info

        return self

    def _evaluate_segments(self, validation_info):
        """
        Evaluate any segmentation expressions stored in the `segments` attribute and expand each
        validation step with such directives into multiple. This is done by evaluating the
        segmentation expression and creating a new validation step for each segment. Errors in
        evaluation (such as no segments matched) will be caught and recorded in the `eval_error`
        attribute.

        Parameters
        ----------
        validation_info
            Information about the validation to evaluate and expand.
        """

        # Create a list to store the expanded validation steps
        expanded_validation_info = []

        # Iterate over the validation steps
        for i, validation in enumerate(validation_info):
            # Get the segments expression
            segments_expr = validation.segments

            # If the value is None, then skip the evaluation and append the validation step to the
            # list of expanded validation steps
            if segments_expr is None:
                expanded_validation_info.append(validation)
                continue

            # Evaluate the segments expression
            try:
                # Get the table for this step, it can either be:
                # 1. the target table itself
                # 2. the target table modified by a `pre` attribute

                if validation.pre is None:
                    table = self.data
                else:
                    table = validation.pre(self.data)

                # If the `segments` expression is a string, that string is taken as a column name
                # for which segmentation should occur across unique values in the column
                if isinstance(segments_expr, str):
                    seg_tuples = _seg_expr_from_string(data_tbl=table, segments_expr=segments_expr)

                # If the 'segments' expression is a tuple, then normalize it to a list of tuples
                # - ("col", "value") -> [("col", "value")]
                # - ("col", ["value1", "value2"]) -> [("col", "value1"), ("col", "value2")]
                elif isinstance(segments_expr, tuple):
                    seg_tuples = _seg_expr_from_tuple(segments_expr=segments_expr)

                # If the 'segments' expression is a list of strings or tuples (can be mixed) then
                # normalize it to a list of tuples following the rules above
                elif isinstance(segments_expr, list):
                    seg_tuples = []
                    for seg in segments_expr:
                        if isinstance(seg, str):
                            # Use the utility function for string items
                            str_seg_tuples = _seg_expr_from_string(
                                data_tbl=table, segments_expr=seg
                            )
                            seg_tuples.extend(str_seg_tuples)
                        elif isinstance(seg, tuple):
                            # Use the utility function for tuple items
                            tuple_seg_tuples = _seg_expr_from_tuple(segments_expr=seg)
                            seg_tuples.extend(tuple_seg_tuples)
                        else:  # pragma: no cover
                            # Handle invalid segment type
                            raise ValueError(
                                f"Invalid segment expression item type: {type(seg)}. "
                                "Must be either string or tuple."
                            )

            except Exception:  # pragma: no cover
                validation.eval_error = True

            # For each segmentation resolved, create a new validation step and add it to the list of
            # expanded validation steps
            for seg in seg_tuples:
                new_validation = copy.deepcopy(validation)

                new_validation.segments = seg

                expanded_validation_info.append(new_validation)

        # Replace the `validation_info` attribute with the expanded version
        self.validation_info = expanded_validation_info

        return self

    def _get_validation_dict(self, i: int | list[int] | None, attr: str) -> dict[int, int]:
        """
        Utility function to get a dictionary of validation attributes for each validation step.

        Parameters
        ----------
        i
            The validation step number(s) from which the attribute values are obtained.
            If `None`, all steps are included.
        attr
            The attribute name to retrieve from each validation step.

        Returns
        -------
        dict[int, int]
            A dictionary of the attribute values for each validation step.
        """
        if isinstance(i, int):
            i = [i]

        if i is None:
            return {validation.i: getattr(validation, attr) for validation in self.validation_info}

        return {
            validation.i: getattr(validation, attr)
            for validation in self.validation_info
            if validation.i in i
        }

    def _execute_final_actions(self):
        """Execute any final actions after interrogation is complete."""
        if self.final_actions is None:
            return

        # Get the highest severity level based on the validation results
        highest_severity = self._get_highest_severity_level()

        # Get row count using the dedicated function that handles all table types correctly
        row_count = get_row_count(self.data)

        # Get column count using the dedicated function that handles all table types correctly
        column_count = get_column_count(self.data)

        # Get the validation duration
        validation_duration = self.validation_duration = (
            self.time_end - self.time_start
        ).total_seconds()

        # Create a summary of validation results as a dictionary
        summary = {
            "n_steps": len(self.validation_info),
            "n_passing_steps": sum(1 for step in self.validation_info if step.all_passed),
            "n_failing_steps": sum(1 for step in self.validation_info if not step.all_passed),
            "n_warning_steps": sum(1 for step in self.validation_info if step.warning),
            "n_error_steps": sum(1 for step in self.validation_info if step.error),
            "n_critical_steps": sum(1 for step in self.validation_info if step.critical),
            "list_passing_steps": [step.i for step in self.validation_info if step.all_passed],
            "list_failing_steps": [step.i for step in self.validation_info if not step.all_passed],
            "dict_n": {step.i: step.n for step in self.validation_info},
            "dict_n_passed": {step.i: step.n_passed for step in self.validation_info},
            "dict_n_failed": {step.i: step.n_failed for step in self.validation_info},
            "dict_f_passed": {step.i: step.f_passed for step in self.validation_info},
            "dict_f_failed": {step.i: step.f_failed for step in self.validation_info},
            "dict_warning": {step.i: step.warning for step in self.validation_info},
            "dict_error": {step.i: step.error for step in self.validation_info},
            "dict_critical": {step.i: step.critical for step in self.validation_info},
            "all_passed": all(step.all_passed for step in self.validation_info),
            "highest_severity": highest_severity,
            "tbl_row_count": row_count,
            "tbl_column_count": column_count,
            "tbl_name": self.tbl_name or "Unknown",
            "validation_duration": validation_duration,
        }

        # Extract the actions from FinalActions object and execute
        action = self.final_actions.actions

        # Execute the action within the context manager
        with _final_action_context_manager(summary):
            if isinstance(action, str):
                print(action)
            elif callable(action):
                action()
            elif isinstance(action, list):
                for single_action in action:
                    if isinstance(single_action, str):
                        print(single_action)
                    elif callable(single_action):
                        single_action()

    def _get_highest_severity_level(self):
        """Get the highest severity level reached across all validation steps."""
        if any(step.critical for step in self.validation_info):
            return "critical"
        elif any(step.error for step in self.validation_info):
            return "error"
        elif any(step.warning for step in self.validation_info):
            return "warning"
        elif any(not step.all_passed for step in self.validation_info):
            return "some failing"
        else:
            return "all passed"


def _normalize_reporting_language(lang: str | None) -> str:
    if lang is None:
        return "en"

    if lang.lower() not in REPORTING_LANGUAGES:
        raise ValueError(
            f"The text '{lang}' doesn't correspond to a Pointblank reporting language."
        )

    return lang.lower()


def _is_string_date(value: str) -> bool:
    """
    Check if a string represents a date in ISO format (YYYY-MM-DD).

    Parameters
    ----------
    value
        The string value to check.

    Returns
    -------
    bool
        True if the string is in date format, False otherwise.
    """
    if not isinstance(value, str):
        return False

    import re

    # Match ISO date format YYYY-MM-DD
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, value):
        return False

    return True


def _is_string_datetime(value: str) -> bool:
    """
    Check if a string represents a datetime in ISO format (YYYY-MM-DD HH:MM:SS).

    Parameters
    ----------
    value
        The string value to check.

    Returns
    -------
    bool
        True if the string is in datetime format, False otherwise.
    """
    if not isinstance(value, str):
        return False

    import re

    # Match ISO datetime format YYYY-MM-DD HH:MM:SS with optional milliseconds
    pattern = r"^\d{4}-\d{2}-\d{2}(\s|T)\d{2}:\d{2}:\d{2}(\.\d+)?$"
    if not re.match(pattern, value):
        return False

    return True


def _convert_string_to_date(value: str) -> datetime.date:
    """
    Convert a string to a datetime.date object.

    Parameters
    ----------
    value
        The string value to convert.

    Returns
    -------
    datetime.date
        The converted date object.

    Raises
    ------
    ValueError
        If the string cannot be converted to a date.
    """
    if not _is_string_date(value):
        raise ValueError(f"Cannot convert '{value}' to a date.")

    import datetime

    return datetime.datetime.strptime(value, "%Y-%m-%d").date()


def _convert_string_to_datetime(value: str) -> datetime.datetime:
    """
    Convert a string to a datetime.datetime object.

    Parameters
    ----------
    value
        The string value to convert.

    Returns
    -------
    datetime.datetime
        The converted datetime object.

    Raises
    ------
    ValueError
        If the string cannot be converted to a datetime.
    """
    if not _is_string_datetime(value):
        raise ValueError(f"Cannot convert '{value}' to a datetime.")

    import datetime

    if "T" in value:
        if "." in value:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    else:
        if "." in value:
            return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
        else:
            return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _string_date_dttm_conversion(value: any) -> any:
    """
    Convert a string to a date or datetime object if it is in the correct format.
    If the value is not a string, it is returned as is.

    Parameters
    ----------
    value
        The value to convert. It can be a string, date, or datetime object.

    Returns
    -------
    any
        The converted date or datetime object, or the original value if it is not a string.

    Raises
    ------
    ValueError
        If the string cannot be converted to a date or datetime.
    """

    if isinstance(value, str):
        if _is_string_date(value):
            value = _convert_string_to_date(value)
        elif _is_string_datetime(value):
            value = _convert_string_to_datetime(value)
        else:
            raise ValueError(
                "If `value=` is provided as a string it must be a date or datetime string."
            )

    return value


def _conditional_string_date_dttm_conversion(
    value: any, allow_regular_strings: bool = False
) -> any:
    """
    Conditionally convert a string to a date or datetime object if it is in the correct format. If
    `allow_regular_strings=` is `True`, regular strings are allowed to pass through unchanged. If
    the value is not a string, it is returned as is.

    Parameters
    ----------
    value
        The value to convert. It can be a string, date, or datetime object.
    allow_regular_strings
        If `True`, regular strings (non-date/datetime) are allowed to pass through unchanged. If
        `False`, behaves like `_string_date_dttm_conversion()` and raises `ValueError` for regular
        strings.

    Returns
    -------
    any
        The converted date or datetime object, or the original value.

    Raises
    ------
    ValueError
        If allow_regular_strings is False and the string cannot be converted to a date or datetime.
    """

    if isinstance(value, str):
        if _is_string_date(value):
            value = _convert_string_to_date(value)
        elif _is_string_datetime(value):
            value = _convert_string_to_datetime(value)
        elif not allow_regular_strings:
            raise ValueError(
                "If `value=` is provided as a string it must be a date or datetime string."
            )  # pragma: no cover
        # If allow_regular_strings is True, regular strings pass through unchanged

    return value


def _process_brief(
    brief: str | None,
    step: int,
    col: str | list[str] | None,
    values: any | None,
    thresholds: any | None,
    segment: any | None,
) -> str:
    # If there is no brief, return `None`
    if brief is None:
        return None

    # If the brief contains a placeholder for the step number then replace with `step`;
    # placeholders are: {step} and {i}
    brief = brief.replace("{step}", str(step))
    brief = brief.replace("{i}", str(step))

    # If a `col` value is available for the validation step *and* the brief contains a placeholder
    # for the column name then replace with `col`; placeholders are: {col} and {column}
    if col is not None:
        # If a list of columns is provided, then join the columns into a comma-separated string
        if isinstance(col, list):
            col = ", ".join(col)

        brief = brief.replace("{col}", col)
        brief = brief.replace("{column}", col)

    if values is not None:
        # If the value is a list, then join the values into a comma-separated string
        if isinstance(values, list):
            values = ", ".join([str(v) for v in values])

        brief = brief.replace("{value}", str(values))

    if thresholds is not None:
        # Get the string representation of thresholds in the form of:
        # "W: 0.20 / C: 0.40 / E: 1.00"

        warning_val = thresholds._get_threshold_value(level="warning")
        error_val = thresholds._get_threshold_value(level="error")
        critical_val = thresholds._get_threshold_value(level="critical")

        thresholds_fmt = f"W: {warning_val} / E: {error_val} / C: {critical_val}"

        brief = brief.replace("{thresholds}", thresholds_fmt)

    if segment is not None:
        # The segment is always a tuple of the form ("{column}", "{value}")
        # Handle both regular lists and Segment objects (from seg_group())

        segment_column = segment[0]
        segment_value = segment[1]

        # If segment_value is a Segment object (from seg_group()), format it appropriately
        if isinstance(segment_value, Segment):
            # For Segment objects, format the segments as a readable string
            segments = segment_value.segments
            if len(segments) == 1:
                # Single segment: join the values with commas
                segment_value_str = ", ".join(str(v) for v in segments[0])
            else:
                # Multiple segments: join each segment with commas, separate segments with " | "
                segment_value_str = " | ".join([", ".join(str(v) for v in seg) for seg in segments])
        else:
            # For regular lists or other types, convert to string
            if isinstance(segment_value, list):
                segment_value_str = ", ".join(str(v) for v in segment_value)
            else:
                segment_value_str = str(segment_value)

        segment_fmt = f"{segment_column} / {segment_value_str}"

        brief = brief.replace("{segment}", segment_fmt)
        brief = brief.replace("{segment_column}", segment_column)
        brief = brief.replace("{segment_value}", segment_value_str)

    return brief


def _transform_auto_brief(brief: str | bool | None) -> str | None:
    if isinstance(brief, bool):
        if brief:
            return "{auto}"
        else:
            return None
    else:
        return brief


def _process_action_str(
    action_str: str,
    step: int,
    col: str | None,
    value: any,
    type: str,
    level: str,
    time: str,
) -> str:
    # If the action string contains a placeholder for the step number then replace with `step`;
    # placeholders are: {step} and {i}
    action_str = action_str.replace("{step}", str(step))
    action_str = action_str.replace("{i}", str(step))

    # If a `col` value is available for the validation step *and* the action string contains a
    # placeholder for the column name then replace with `col`; placeholders are: {col} and {column}
    if col is not None:
        # If a list of columns is provided, then join the columns into a comma-separated string
        if isinstance(col, list):
            col = ", ".join(col)  # pragma: no cover

        action_str = action_str.replace("{col}", col)
        action_str = action_str.replace("{column}", col)

    # If a `value` value is available for the validation step *and* the action string contains a
    # placeholder for the value then replace with `value`; placeholders are: {value} and {val}
    if value is not None:
        action_str = action_str.replace("{value}", str(value))
        action_str = action_str.replace("{val}", str(value))

    # If the action string contains a `type` placeholder then replace with `type` either in
    # lowercase or uppercase; placeholders for the lowercase form are {type} and {assertion}
    # and for the uppercase form are {TYPE} and {ASSERTION}
    action_str = action_str.replace("{type}", type)
    action_str = action_str.replace("{assertion}", type)
    action_str = action_str.replace("{TYPE}", type.upper())
    action_str = action_str.replace("{ASSERTION}", type.upper())

    # If the action string contains a `level` placeholder then replace with `level` either in
    # lowercase or uppercase; placeholders for the lowercase form are {level} and {severity}
    # and for the uppercase form are {LEVEL} and {SEVERITY}
    action_str = action_str.replace("{level}", level)
    action_str = action_str.replace("{severity}", level)
    action_str = action_str.replace("{LEVEL}", level.upper())
    action_str = action_str.replace("{SEVERITY}", level.upper())

    # If the action string contains a `time` placeholder then replace with `time`;
    # placeholder for this is {time}
    action_str = action_str.replace("{time}", time)

    return action_str


def _create_autobrief_or_failure_text(
    assertion_type: str, lang: str, column: str | None, values: str | None, for_failure: bool
) -> str:
    if assertion_type in [
        "col_vals_gt",
        "col_vals_ge",
        "col_vals_lt",
        "col_vals_le",
        "col_vals_eq",
        "col_vals_ne",
    ]:
        return _create_text_comparison(
            assertion_type=assertion_type,
            lang=lang,
            column=column,
            values=values,
            for_failure=for_failure,
        )

    if assertion_type == "col_vals_between":
        return _create_text_between(
            lang=lang,
            column=column,
            value_1=values[0],
            value_2=values[1],
            for_failure=for_failure,
        )

    if assertion_type == "col_vals_outside":
        return _create_text_between(
            lang=lang,
            column=column,
            value_1=values[0],
            value_2=values[1],
            not_=True,
            for_failure=for_failure,
        )

    if assertion_type == "col_vals_in_set":
        return _create_text_set(
            lang=lang,
            column=column,
            values=values,
            for_failure=for_failure,
        )

    if assertion_type == "col_vals_not_in_set":
        return _create_text_set(
            lang=lang,
            column=column,
            values=values,
            not_=True,
            for_failure=for_failure,
        )

    if assertion_type == "col_vals_null":
        return _create_text_null(
            lang=lang,
            column=column,
            for_failure=for_failure,
        )

    if assertion_type == "col_vals_not_null":
        return _create_text_null(
            lang=lang,
            column=column,
            not_=True,
            for_failure=for_failure,
        )

    if assertion_type == "col_vals_regex":
        return _create_text_regex(
            lang=lang,
            column=column,
            pattern=values,
            for_failure=for_failure,
        )

    if assertion_type == "col_vals_expr":
        return _create_text_expr(
            lang=lang,
            for_failure=for_failure,
        )

    if assertion_type == "col_exists":
        return _create_text_col_exists(
            lang=lang,
            column=column,
            for_failure=for_failure,
        )

    if assertion_type == "col_schema_match":
        return _create_text_col_schema_match(
            lang=lang,
            for_failure=for_failure,
        )

    if assertion_type == "rows_distinct":
        return _create_text_rows_distinct(
            lang=lang,
            columns_subset=column,
            for_failure=for_failure,
        )

    if assertion_type == "rows_complete":
        return _create_text_rows_complete(
            lang=lang,
            columns_subset=column,
            for_failure=for_failure,
        )

    if assertion_type == "row_count_match":
        return _create_text_row_count_match(
            lang=lang,
            value=values,
            for_failure=for_failure,
        )

    if assertion_type == "col_count_match":
        return _create_text_col_count_match(
            lang=lang,
            value=values,
            for_failure=for_failure,
        )

    if assertion_type == "conjointly":
        return _create_text_conjointly(lang=lang, for_failure=for_failure)

    if assertion_type == "specially":
        return _create_text_specially(lang=lang, for_failure=for_failure)

    if assertion_type == "prompt":
        return _create_text_prompt(
            lang=lang,
            prompt=values["prompt"]
            if isinstance(values, dict) and "prompt" in values
            else str(values),
            for_failure=for_failure,
        )

    return None  # pragma: no cover


def _expect_failure_type(for_failure: bool) -> str:
    return "failure" if for_failure else "expectation"


def _create_text_comparison(
    assertion_type: str,
    lang: str,
    column: str | list[str] | None,
    values: str | None,
    for_failure: bool = False,
) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    if lang == "ar":  # pragma: no cover
        operator = COMPARISON_OPERATORS_AR[assertion_type]
    else:
        operator = COMPARISON_OPERATORS[assertion_type]

    column_text = _prep_column_text(column=column)

    values_text = _prep_values_text(values=values, lang=lang, limit=3)

    compare_expectation_text = EXPECT_FAIL_TEXT[f"compare_{type_}_text"][lang]

    return compare_expectation_text.format(
        column_text=column_text,
        operator=operator,
        values_text=values_text,
    )


def _create_text_between(
    lang: str,
    column: str | None,
    value_1: str,
    value_2: str,
    not_: bool = False,
    for_failure: bool = False,
) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    column_text = _prep_column_text(column=column)

    value_1_text = _prep_values_text(values=value_1, lang=lang, limit=3)
    value_2_text = _prep_values_text(values=value_2, lang=lang, limit=3)

    if not not_:
        text = EXPECT_FAIL_TEXT[f"between_{type_}_text"][lang].format(
            column_text=column_text,
            value_1=value_1_text,
            value_2=value_2_text,
        )
    else:
        text = EXPECT_FAIL_TEXT[f"not_between_{type_}_text"][lang].format(
            column_text=column_text,
            value_1=value_1_text,
            value_2=value_2_text,
        )

    return text


def _create_text_set(
    lang: str, column: str | None, values: list[any], not_: bool = False, for_failure: bool = False
) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    values_text = _prep_values_text(values=values, lang=lang, limit=3)

    column_text = _prep_column_text(column=column)

    if not not_:
        text = EXPECT_FAIL_TEXT[f"in_set_{type_}_text"][lang].format(
            column_text=column_text,
            values_text=values_text,
        )
    else:
        text = EXPECT_FAIL_TEXT[f"not_in_set_{type_}_text"][lang].format(
            column_text=column_text,
            values_text=values_text,
        )

    return text


def _create_text_null(
    lang: str, column: str | None, not_: bool = False, for_failure: bool = False
) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    column_text = _prep_column_text(column=column)

    if not not_:
        text = EXPECT_FAIL_TEXT[f"null_{type_}_text"][lang].format(
            column_text=column_text,
        )
    else:
        text = EXPECT_FAIL_TEXT[f"not_null_{type_}_text"][lang].format(
            column_text=column_text,
        )

    return text


def _create_text_regex(
    lang: str, column: str | None, pattern: str | dict, for_failure: bool = False
) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    column_text = _prep_column_text(column=column)

    # Handle case where pattern is a dictionary containing `pattern` and `inverse`
    if isinstance(pattern, dict):
        pattern_str = pattern["pattern"]
        inverse = pattern.get("inverse", False)
    else:  # pragma: no cover
        # For backward compatibility, assume it's just the pattern string
        pattern_str = pattern  # pragma: no cover
        inverse = False  # pragma: no cover

    # Use inverse-specific translations if inverse=True
    if inverse:
        text_key = f"regex_inverse_{type_}_text"
    else:
        text_key = f"regex_{type_}_text"

    return EXPECT_FAIL_TEXT[text_key][lang].format(
        column_text=column_text,
        values_text=pattern_str,
    )


def _create_text_expr(lang: str, for_failure: bool) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    return EXPECT_FAIL_TEXT[f"col_vals_expr_{type_}_text"][lang]


def _create_text_col_exists(lang: str, column: str | None, for_failure: bool = False) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    column_text = _prep_column_text(column=column)

    return EXPECT_FAIL_TEXT[f"col_exists_{type_}_text"][lang].format(column_text=column_text)


def _create_text_col_schema_match(lang: str, for_failure: bool) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    return EXPECT_FAIL_TEXT[f"col_schema_match_{type_}_text"][lang]


def _create_text_rows_distinct(
    lang: str, columns_subset: list[str] | None, for_failure: bool = False
) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    if columns_subset is None:
        text = EXPECT_FAIL_TEXT[f"all_row_distinct_{type_}_text"][lang]

    else:
        column_text = _prep_values_text(values=columns_subset, lang=lang, limit=3)

        text = EXPECT_FAIL_TEXT[f"across_row_distinct_{type_}_text"][lang].format(
            column_text=column_text
        )

    return text


def _create_text_rows_complete(
    lang: str, columns_subset: list[str] | None, for_failure: bool = False
) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    if columns_subset is None:
        text = EXPECT_FAIL_TEXT[f"all_row_complete_{type_}_text"][lang]

    else:
        column_text = _prep_values_text(values=columns_subset, lang=lang, limit=3)

        text = EXPECT_FAIL_TEXT[f"across_row_complete_{type_}_text"][lang].format(
            column_text=column_text
        )

    return text


def _create_text_row_count_match(lang: str, value: int, for_failure: bool = False) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    values_text = _prep_values_text(value["count"], lang=lang)

    return EXPECT_FAIL_TEXT[f"row_count_match_n_{type_}_text"][lang].format(values_text=values_text)


def _create_text_col_count_match(lang: str, value: int, for_failure: bool = False) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    values_text = _prep_values_text(value["count"], lang=lang)

    return EXPECT_FAIL_TEXT[f"col_count_match_n_{type_}_text"][lang].format(values_text=values_text)


def _create_text_conjointly(lang: str, for_failure: bool = False) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    return EXPECT_FAIL_TEXT[f"conjointly_{type_}_text"][lang]


def _create_text_specially(lang: str, for_failure: bool = False) -> str:
    type_ = _expect_failure_type(for_failure=for_failure)

    return EXPECT_FAIL_TEXT[f"specially_{type_}_text"][lang]


def _create_text_prompt(lang: str, prompt: str, for_failure: bool = False) -> str:
    """Create text for prompt validation: just return the prompt."""
    return prompt


def _prep_column_text(column: str | list[str]) -> str:
    if isinstance(column, list):
        return "`" + str(column[0]) + "`"
    elif isinstance(column, str):
        return "`" + column + "`"
    else:
        return ""


def _prep_values_text(
    values: str
    | int
    | float
    | datetime.datetime
    | datetime.date
    | list[str | int | float | datetime.datetime | datetime.date],
    lang: str,
    limit: int = 3,
) -> str:
    if isinstance(values, ColumnLiteral):
        return f"`{values}`"

    if isinstance(values, (str, int, float, datetime.datetime, datetime.date)):
        values = [values]

    length_values = len(values)

    if length_values == 0:
        return ""  # pragma: no cover

    if length_values > limit:
        num_omitted = length_values - limit

        # Format datetime objects as strings if present
        formatted_values = []
        for value in values[:limit]:
            if isinstance(value, (datetime.datetime, datetime.date)):
                formatted_values.append(f"`{value.isoformat()}`")  # pragma: no cover
            else:
                formatted_values.append(f"`{value}`")

        values_str = ", ".join([f"`{value}`" for value in values[:limit]])

        additional_text = EXPECT_FAIL_TEXT["values_text"][lang]

        additional_str = additional_text.format(num_omitted=num_omitted)

        values_str = f"{values_str}, {additional_str}"

    else:
        # Format datetime objects as strings if present
        formatted_values = []
        for value in values:
            if isinstance(value, (datetime.datetime, datetime.date)):
                formatted_values.append(f"`{value.isoformat()}`")
            else:
                formatted_values.append(f"`{value}`")

        values_str = ", ".join([f"`{value}`" for value in values])

    return values_str


def _seg_expr_from_string(data_tbl: any, segments_expr: str) -> list[tuple[str, str]]:
    """
    Obtain the segmentation categories from a table column.

    The `segments_expr` value will have been checked to be a string, so there's no need to check for
    that here. The function will return a list of tuples representing pairings of a column name and
    a value. The task is to obtain the unique values in the column (handling different table types)
    and produce a normalized list of tuples of the form: `(column, value)`.

    This function is used to create a list of segments for the validation step. And since there will
    usually be more than one segment, the validation step will be expanded into multiple during
    interrogation (where this function is called).

    Parameters
    ----------
    data_tbl
        The table from which to obtain the segmentation categories.
    segments_expr
        The column name for which segmentation should occur across unique values in the column.

    Returns
    -------
    list[tuple[str, str]]
        A list of tuples representing pairings of a column name and a value in the column.
    """
    import narwhals as nw

    # Determine if the table is a DataFrame or a DB table
    tbl_type = _get_tbl_type(data=data_tbl)

    # Obtain the segmentation categories from the table column given as `segments_expr`
    if tbl_type in ["polars", "pandas", "pyspark"]:
        # Use Narwhals for supported DataFrame types
        data_nw = nw.from_native(data_tbl)
        unique_vals = data_nw.select(nw.col(segments_expr)).unique()

        # Convert to list of values
        seg_categories = unique_vals[segments_expr].to_list()
    elif tbl_type in IBIS_BACKENDS:
        distinct_col_vals = data_tbl.select(segments_expr).distinct()
        seg_categories = distinct_col_vals[segments_expr].to_list()
    else:  # pragma: no cover
        raise ValueError(f"Unsupported table type: {tbl_type}")

    # Ensure that the categories are sorted, and allow for None values
    seg_categories.sort(key=lambda x: (x is None, x))

    # Place each category and each value in a list of tuples as: `(column, value)`
    seg_tuples = [(segments_expr, category) for category in seg_categories]

    return seg_tuples


def _seg_expr_from_tuple(segments_expr: tuple) -> list[tuple[str, Any]]:
    """
    Normalize the segments expression to a list of tuples, given a single tuple.

    The `segments_expr` value will have been checked to be a tuple, so there's no need to check for
    that here. The function will return a list of tuples representing pairings of a column name and
    a value. The task is to normalize the tuple into a list of tuples of the form:
    `(column, value)`.

    The following examples show how this normalzation works:
    - `("col", "value")` -> `[("col", "value")]` (single tuple, upgraded to a list of tuples)
    - `("col", ["value1", "value2"])` -> `[("col", "value1"), ("col", "value2")]` (tuple with a list
      of values, expanded into multiple tuples within a list)

    This function is used to create a list of segments for the validation step. And since there will
    usually be more than one segment, the validation step will be expanded into multiple during
    interrogation (where this function is called).

    Parameters
    ----------
    segments_expr
        The segments expression to normalize. It can be a tuple of the form
        `(column, value)` or `(column, [value1, value2])`.

    Returns
    -------
    list[tuple[str, Any]]
        A list of tuples representing pairings of a column name and a value in the column.
        Values can be any type, including None.
    """
    # Unpack the segments expression tuple for more convenient and explicit variable names
    column, segment = segments_expr

    # Check if the first element is a string
    if isinstance(column, str):
        if isinstance(segment, Segment):
            seg_tuples = [(column, seg) for seg in segment.segments]
        # If the second element is a collection, expand into a list of tuples
        elif isinstance(segment, (list, set, tuple)):
            seg_tuples = [(column, seg) for seg in segment]
        # If the second element is not a list, create a single tuple
        else:
            seg_tuples = [(column, segment)]
    # If the first element is not a string, raise an error
    else:  # pragma: no cover
        raise ValueError("The first element of the segments expression must be a string.")

    return seg_tuples


def _apply_segments(data_tbl: any, segments_expr: tuple[str, Any]) -> any:
    """
    Apply the segments expression to the data table.

    Filter the data table based on the `segments_expr=` value, where the first element is the
    column name and the second element is the value to filter by.

    Parameters
    ----------
    data_tbl
        The data table to filter. It can be a Pandas DataFrame, Polars DataFrame, or an Ibis
        backend table.
    segments_expr
        The segments expression to apply. It is a tuple of the form `(column, value)`.

    Returns
    -------
    any
        The filtered data table. It will be of the same type as the input table.
    """
    # Get the table type
    tbl_type = _get_tbl_type(data=data_tbl)

    # Unpack the segments expression tuple for more convenient and explicit variable names
    column, segment = segments_expr

    if tbl_type in ["pandas", "polars", "pyspark"]:
        # If the table is a Pandas, Polars, or PySpark DataFrame, transform to a Narwhals table
        # and perform the filtering operation

        # Transform to Narwhals table if a DataFrame
        data_tbl_nw = nw.from_native(data_tbl)

        # Handle Polars expressions by attempting to extract literal values
        # This is a compatibility measure for cases where `pl.datetime()`, `pl.lit()`, etc.,
        # are accidentally used instead of native Python types
        if (
            hasattr(segment, "__class__")
            and "polars" in segment.__class__.__module__
            and segment.__class__.__name__ == "Expr"
        ):
            # This is a Polars expression so we should warn about this and suggest native types
            import warnings
            from datetime import date, datetime

            warnings.warn(
                "Polars expressions in segments are deprecated. Please use native Python types instead. "
                "For example, use datetime.date(2016, 1, 4) instead of pl.datetime(2016, 1, 4).",
                DeprecationWarning,
                stacklevel=3,
            )

            # Try to extract the literal value from various Polars expression patterns
            segment_str = str(segment)
            parsed_value = None

            # Handle different Polars expression string formats
            # Format 1: Direct date strings like "2016-01-04"
            if len(segment_str) == 10 and segment_str.count("-") == 2:
                try:
                    parsed_value = date.fromisoformat(segment_str)
                except ValueError:  # pragma: no cover
                    pass  # pragma: no cover

            # Format 2: Datetime strings with UTC timezone like
            # "2016-01-04 00:00:01 UTC.strict_cast(...)"
            elif " UTC" in segment_str:
                try:
                    # Extract just the datetime part before "UTC"
                    datetime_part = segment_str.split(" UTC")[0]
                    if len(datetime_part) >= 10:
                        parsed_dt = datetime.fromisoformat(datetime_part)
                        # Convert midnight datetimes to dates for consistency
                        if parsed_dt.time() == datetime.min.time():
                            parsed_value = parsed_dt.date()  # pragma: no cover
                        else:
                            parsed_value = parsed_dt
                except (ValueError, IndexError):  # pragma: no cover
                    pass  # pragma: no cover

            # Format 3: Bracketed expressions like ['2016-01-04']
            elif segment_str.startswith("[") and segment_str.endswith("]"):
                try:  # pragma: no cover
                    # Remove [' and ']
                    content = segment_str[2:-2]  # pragma: no cover

                    # Try parsing as date first
                    if len(content) == 10 and content.count("-") == 2:  # pragma: no cover
                        try:  # pragma: no cover
                            parsed_value = date.fromisoformat(content)  # pragma: no cover
                        except ValueError:  # pragma: no cover
                            pass  # pragma: no cover

                    # Try parsing as datetime
                    if parsed_value is None:  # pragma: no cover
                        try:  # pragma: no cover
                            parsed_dt = datetime.fromisoformat(content.replace(" UTC", ""))
                            if parsed_dt.time() == datetime.min.time():
                                parsed_value = parsed_dt.date()
                            else:
                                parsed_value = parsed_dt
                        except ValueError:
                            pass

                except (ValueError, IndexError):  # pragma: no cover
                    pass  # pragma: no cover

            # Handle `pl.datetime()` expressions with .alias("datetime")
            elif "datetime" in segment_str and '.alias("datetime")' in segment_str:
                try:
                    datetime_part = segment_str.split('.alias("datetime")')[0]
                    parsed_dt = datetime.fromisoformat(datetime_part)

                    if parsed_dt.time() == datetime.min.time():
                        parsed_value = parsed_dt.date()
                    else:
                        parsed_value = parsed_dt  # pragma: no cover

                except (ValueError, AttributeError):  # pragma: no cover
                    pass  # pragma: no cover

            # If we successfully parsed a value, use it; otherwise leave segment as is
            if parsed_value is not None:
                segment = parsed_value

        # Filter the data table based on the column name and segment
        if segment is None:
            data_tbl_nw = data_tbl_nw.filter(nw.col(column).is_null())
        elif isinstance(segment, list):
            # Check if the segment is a segment group
            data_tbl_nw = data_tbl_nw.filter(nw.col(column).is_in(segment))
        else:
            data_tbl_nw = data_tbl_nw.filter(nw.col(column) == segment)

        # Transform back to the original table type
        data_tbl = data_tbl_nw.to_native()

    elif tbl_type in IBIS_BACKENDS:
        # If the table is an Ibis backend table, perform the filtering operation directly

        # Filter the data table based on the column name and segment
        # Use the new Ibis API methods to avoid deprecation warnings
        if segment is None:
            data_tbl = data_tbl.filter(data_tbl[column].isnull())  # pragma: no cover
        elif isinstance(segment, list):
            data_tbl = data_tbl.filter(data_tbl[column].isin(segment))  # pragma: no cover
        else:
            data_tbl = data_tbl.filter(data_tbl[column] == segment)

    return data_tbl


def _validation_info_as_dict(validation_info: _ValidationInfo) -> dict:
    """
    Convert a `_ValidationInfo` object to a dictionary.

    Parameters
    ----------
    validation_info
        The `_ValidationInfo` object to convert to a dictionary.

    Returns
    -------
    dict
        A dictionary representing the `_ValidationInfo` object.
    """

    # Define the fields to include in the validation information
    validation_info_fields = [
        "i",
        "assertion_type",
        "column",
        "values",
        "inclusive",
        "na_pass",
        "pre",
        "segments",
        "label",
        "brief",
        "autobrief",
        "active",
        "eval_error",
        "all_passed",
        "n",
        "n_passed",
        "n_failed",
        "f_passed",
        "f_failed",
        "warning",
        "error",
        "critical",
        "extract",
        "proc_duration_s",
    ]

    # Filter the validation information to include only the selected fields
    validation_info_filtered = [
        {field: getattr(validation, field) for field in validation_info_fields}
        for validation in validation_info
    ]

    # Transform the validation information into a dictionary of lists so that it
    # can be used to create a DataFrame
    validation_info_dict = {field: [] for field in validation_info_fields}

    for validation in validation_info_filtered:
        for field in validation_info_fields:
            validation_info_dict[field].append(validation[field])

    return validation_info_dict


def _get_assertion_icon(icon: list[str], length_val: int = 30) -> list[str]:
    # For each icon, get the assertion icon SVG test from SVG_ICONS_FOR_ASSERTION_TYPES dictionary
    icon_svg = [SVG_ICONS_FOR_ASSERTION_TYPES.get(icon) for icon in icon]

    # Replace the width and height in the SVG string
    for i in range(len(icon_svg)):
        icon_svg[i] = _replace_svg_dimensions(icon_svg[i], height_width=length_val)

    return icon_svg


def _replace_svg_dimensions(svg: list[str], height_width: int | float) -> list[str]:
    svg = re.sub(r'width="[0-9]*?px', f'width="{height_width}px', svg)
    svg = re.sub(r'height="[0-9]*?px', f'height="{height_width}px', svg)

    return svg


def _get_title_text(
    title: str | None, tbl_name: str | None, interrogation_performed: bool, lang: str
) -> str:
    title = _process_title_text(title=title, tbl_name=tbl_name, lang=lang)

    if interrogation_performed:
        return title

    no_interrogation_text = VALIDATION_REPORT_TEXT["no_interrogation_performed_text"][lang]

    # If no interrogation was performed, return title text indicating that
    if lang not in RTL_LANGUAGES:
        html_str = (
            "<div>"
            f'<span style="float: left;">'
            f"{title}"
            "</span>"
            f'<span style="float: right; text-decoration-line: underline; '
            "text-underline-position: under;"
            "font-size: 16px; text-decoration-color: #9C2E83;"
            'padding-top: 0.1em; padding-right: 0.4em;">'
            f"{no_interrogation_text}"
            "</span>"
            "</div>"
        )
    else:
        html_str = (
            "<div>"
            f'<span style="float: left; text-decoration-line: underline; '
            "text-underline-position: under;"
            "font-size: 16px; text-decoration-color: #9C2E83;"
            'padding-top: 0.1em; padding-left: 0.4em;">'
            f"{no_interrogation_text}"
            "</span>"
            f'<span style="float: right;">{title}</span>'
            "</div>"
        )  # pragma: no cover

    return html_str


def _process_title_text(title: str | None, tbl_name: str | None, lang: str) -> str:
    default_title_text = VALIDATION_REPORT_TEXT["pointblank_validation_title_text"][lang]

    if title is None:
        title_text = ""
    elif title == ":default:":
        title_text = default_title_text
    elif title == ":none:":
        title_text = ""
    elif title == ":tbl_name:":
        if tbl_name is not None:
            title_text = f"<code>{tbl_name}</code>"
        else:
            title_text = ""
    else:
        title_text = commonmark.commonmark(title)

    return title_text


def _transform_tbl_preprocessed(pre: any, seg: any, interrogation_performed: bool) -> list[str]:
    # If no interrogation was performed, return a list of empty strings
    if not interrogation_performed:
        return ["" for _ in range(len(pre))]

    # Iterate over the pre-processed table status and return the appropriate SVG icon name
    # (either 'unchanged' (None) or 'modified' (not None))
    status_list = []

    for i in range(len(pre)):
        if seg[i] is not None:
            status_list.append("segmented")
        elif pre[i] is not None:
            status_list.append("modified")
        else:
            status_list.append("unchanged")

    return _get_preprocessed_table_icon(icon=status_list)


def _get_preprocessed_table_icon(icon: list[str]) -> list[str]:
    # For each icon, get the SVG icon from the SVG_ICONS_FOR_TBL_STATUS dictionary
    icon_svg = [SVG_ICONS_FOR_TBL_STATUS.get(icon) for icon in icon]

    return icon_svg


def _transform_eval(
    n: list[int], interrogation_performed: bool, eval_error: list[bool], active: list[bool]
) -> list[str]:
    # If no interrogation was performed, return a list of empty strings
    if not interrogation_performed:
        return ["" for _ in range(len(n))]

    symbol_list = []

    for i in range(len(n)):
        # If there was an evaluation error, then add a collision mark
        if eval_error[i]:
            symbol_list.append('<span style="color:#CF142B;">&#128165;</span>')
            continue

        # If the validation step is inactive, then add an em dash
        if not active[i]:
            symbol_list.append("&mdash;")
            continue

        # Otherwise, add a green check mark
        symbol_list.append('<span style="color:#4CA64C;">&check;</span>')

    return symbol_list


def _format_single_number_with_gt(
    value: int, n_sigfig: int = 3, compact: bool = True, locale: str = "en", df_lib=None
) -> str:
    """Format a single number using Great Tables GT object to avoid pandas dependency."""
    if df_lib is None:
        # Use library detection to select appropriate DataFrame library
        if _is_lib_present("polars"):
            import polars as pl

            df_lib = pl
        elif _is_lib_present("pandas"):  # pragma: no cover
            import pandas as pd  # pragma: no cover

            df_lib = pd  # pragma: no cover
        else:  # pragma: no cover
            raise ImportError(
                "Neither Polars nor Pandas is available for formatting"
            )  # pragma: no cover

    # Create a single-row, single-column DataFrame using the specified library
    df = df_lib.DataFrame({"value": [value]})

    # Create GT object and format the column
    gt_obj = GT(df).fmt_number(columns="value", n_sigfig=n_sigfig, compact=compact, locale=locale)

    # Extract the formatted value using _get_column_of_values
    formatted_values = _get_column_of_values(gt_obj, column_name="value", context="html")

    return formatted_values[0]  # Return the single formatted value


def _transform_test_units(
    test_units: list[int],
    interrogation_performed: bool,
    active: list[bool],
    locale: str,
    df_lib=None,
) -> list[str]:
    # If no interrogation was performed, return a list of empty strings
    if not interrogation_performed:
        return ["" for _ in range(len(test_units))]

    # Define the helper function that'll format numbers safely with Great Tables
    def _format_number_safe(value: int) -> str:
        if df_lib is not None:
            # Use GT-based formatting to avoid Pandas dependency completely
            return _format_single_number_with_gt(
                value, n_sigfig=3, compact=True, locale=locale, df_lib=df_lib
            )
        else:
            # Fallback to the original behavior
            return str(vals.fmt_number(value, n_sigfig=3, compact=True, locale=locale)[0])

    return [
        (
            (str(test_units[i]) if test_units[i] < 10000 else _format_number_safe(test_units[i]))
            if active[i]
            else "&mdash;"
        )
        for i in range(len(test_units))
    ]


def _fmt_lg(value: int, locale: str, df_lib=None) -> str:
    if df_lib is not None:
        # Use GT-based formatting if a DataFrame library is provided
        return _format_single_number_with_gt(
            value, n_sigfig=3, compact=True, locale=locale, df_lib=df_lib
        )
    else:
        # Fallback to the original behavior
        return vals.fmt_number(value, n_sigfig=3, compact=True, locale=locale)[0]


def _format_single_float_with_gt(
    value: float, decimals: int = 2, locale: str = "en", df_lib=None
) -> str:
    if df_lib is None:
        # Use library detection to select appropriate DataFrame library
        if _is_lib_present("polars"):
            import polars as pl

            df_lib = pl
        elif _is_lib_present("pandas"):  # pragma: no cover
            import pandas as pd  # pragma: no cover

            df_lib = pd  # pragma: no cover
        else:  # pragma: no cover
            raise ImportError(
                "Neither Polars nor Pandas is available for formatting"
            )  # pragma: no cover

    # Create a single-row, single-column DataFrame using the specified library
    df = df_lib.DataFrame({"value": [value]})

    # Create GT object and format the column
    gt_obj = GT(df).fmt_number(columns="value", decimals=decimals, locale=locale)

    # Extract the formatted value using _get_column_of_values
    formatted_values = _get_column_of_values(gt_obj, column_name="value", context="html")

    return formatted_values[0]  # Return the single formatted value


def _transform_passed_failed(
    n_passed_failed: list[int],
    f_passed_failed: list[float],
    interrogation_performed: bool,
    active: list[bool],
    locale: str,
    df_lib=None,
) -> list[str]:
    if not interrogation_performed:
        return ["" for _ in range(len(n_passed_failed))]

    # Helper function to format numbers safely
    def _format_float_safe(value: float) -> str:
        if df_lib is not None:
            # Use GT-based formatting to avoid Pandas dependency completely
            return _format_single_float_with_gt(value, decimals=2, locale=locale, df_lib=df_lib)
        else:
            # Fallback to the original behavior
            return vals.fmt_number(value, decimals=2, locale=locale)[0]  # pragma: no cover

    passed_failed = [
        (
            f"{n_passed_failed[i] if n_passed_failed[i] < 10000 else _fmt_lg(n_passed_failed[i], locale=locale, df_lib=df_lib)}"
            f"<br />{_format_float_safe(f_passed_failed[i])}"
            if active[i]
            else "&mdash;"
        )
        for i in range(len(n_passed_failed))
    ]

    return passed_failed


def _transform_w_e_c(values, color, interrogation_performed):
    # If no interrogation was performed, return a list of empty strings
    if not interrogation_performed:
        return ["" for _ in range(len(values))]

    return [
        (
            "&mdash;"
            if value is None
            else (
                f'<span style="color: {color};">&#9679;</span>'
                if value is True
                else f'<span style="color: {color};">&cir;</span>'
                if value is False
                else value
            )
        )
        for value in values
    ]


def _transform_assertion_str(
    assertion_str: list[str],
    brief_str: list[str | None],
    autobrief_str: list[str],
    segmentation_str: list[tuple | None],
    lang: str,
) -> list[str]:
    # Get the SVG icons for the assertion types
    svg_icon = _get_assertion_icon(icon=assertion_str)

    # Append `()` to the `assertion_str`
    assertion_str = [x + "()" for x in assertion_str]

    # Make every None value in `brief_str` an empty string
    brief_str = ["" if x is None else x for x in brief_str]

    # If the `autobrief_str` list contains only None values, then set `brief_str` to a
    # list of empty strings (this is the case when `interrogate()` hasn't be called)`
    if all(x is None for x in autobrief_str):
        autobrief_str = [""] * len(brief_str)

    else:
        # If the template text `{auto}` is in the `brief_str` then replace it with
        # the corresponding `autobrief_str` entry
        brief_str = [
            brief_str[i].replace("{auto}", autobrief_str[i])
            if "{auto}" in brief_str[i]
            else brief_str[i]
            for i in range(len(brief_str))
        ]

        # Use Markdown-to-HTML conversion to format the `brief_str` text
        brief_str = [commonmark.commonmark(x) for x in brief_str]

    # Obtain the number of characters contained in the assertion
    # string; this is important for sizing components appropriately
    assertion_type_nchar = [len(x) for x in assertion_str]

    # Declare the text size based on the length of `assertion_str`
    text_size = [10 if nchar + 2 >= 20 else 11 for nchar in assertion_type_nchar]

    # Prepare the CSS style for right-to-left languages
    rtl_css_style = " direction: rtl;" if lang in RTL_LANGUAGES else ""

    # Define the brief's HTML div tag for each row
    brief_divs = [
        f"<div style=\"font-size: 9px; font-family: 'IBM Plex Sans'; text-wrap: balance; margin-top: 3px;{rtl_css_style}\">{brief}</div>"
        if brief.strip()
        else ""
        for brief in brief_str
    ]

    # Create the assertion `type_upd` strings
    type_upd = [
        f"""
        <div style="margin: 0; padding: 0; display: inline-block; height: 30px; vertical-align: middle; width: 16%;">
            <!--?xml version="1.0" encoding="UTF-8"?-->{svg}
        </div>
        <div style="font-family: 'IBM Plex Mono', monospace, courier; color: black; font-size: {size}px; display: inline-block; vertical-align: middle;">
            <div>{assertion}</div>
        </div>
        {brief_div}
        """
        for assertion, svg, size, brief_div in zip(assertion_str, svg_icon, text_size, brief_divs)
    ]

    # If the `segments` list is not empty, prepend a segmentation div to the `type_upd` strings
    if segmentation_str:
        for i in range(len(type_upd)):
            if segmentation_str[i] is not None:
                # Get the column name and value from the segmentation expression
                column_name = segmentation_str[i][0]
                column_value = segmentation_str[i][1]
                # Create the segmentation div
                segmentation_div = (
                    "<div style='margin-top: 0px; margin-bottom: 0px; "
                    "white-space: pre; font-size: 8px; color: darkblue; padding-bottom: 4px; "
                    "'>"
                    "<strong><span style='font-family: Helvetica, arial, sans-serif;'>"
                    f"SEGMENT&nbsp;&nbsp;</span></strong><span>{column_name} / {column_value}"
                    "</span>"
                    "</div>"
                )
                # Prepend the segmentation div to the type_upd string
                type_upd[i] = f"{segmentation_div} {type_upd[i]}"

    return type_upd


def _pre_processing_funcs_to_str(pre: Callable) -> str | list[str]:
    if isinstance(pre, Callable):
        return _get_callable_source(fn=pre)


def _get_callable_source(fn: Callable) -> str:
    if isinstance(fn, Callable):
        try:
            source_lines, _ = inspect.getsourcelines(fn)
            source = "".join(source_lines).strip()
            # Extract the `pre` argument from the source code
            pre_arg = _extract_pre_argument(source)
            return pre_arg
        except (OSError, TypeError):  # pragma: no cover
            return fn.__name__
    return fn  # pragma: no cover


def _extract_pre_argument(source: str) -> str:
    # Find the start of the `pre` argument
    pre_start = source.find("pre=")
    if pre_start == -1:
        return source

    # Find the end of the `pre` argument
    pre_end = source.find(",", pre_start)
    if pre_end == -1:
        pre_end = len(source)

    # Extract the `pre` argument and remove the leading `pre=`
    pre_arg = source[pre_start + len("pre=") : pre_end].strip()

    return pre_arg


def _create_table_time_html(
    time_start: datetime.datetime | None, time_end: datetime.datetime | None
) -> str:
    if time_start is None:
        return ""

    # Get the time duration (difference between `time_end` and `time_start`) in seconds
    time_duration = (time_end - time_start).total_seconds()

    # If the time duration is less than 1 second, use a simplified string, otherwise
    # format the time duration to four decimal places
    if time_duration < 1:
        time_duration_fmt = "< 1 s"
    else:
        time_duration_fmt = f"{time_duration:.4f} s"

    # Format the start time and end time in the format: "%Y-%m-%d %H:%M:%S %Z"
    time_start_fmt = time_start.strftime("%Y-%m-%d %H:%M:%S %Z")
    time_end_fmt = time_end.strftime("%Y-%m-%d %H:%M:%S %Z")

    # Generate an HTML string that displays the start time, duration, and end time
    return (
        f"<div style='margin-top: 5px; margin-bottom: 5px;'>"
        f"<span style='background-color: #FFF; color: #444; padding: 0.5em 0.5em; position: "
        f"inherit; text-transform: uppercase; margin-left: 10px; margin-right: 5px; border: "
        f"solid 1px #999999; font-variant-numeric: tabular-nums; border-radius: 0; padding: "
        f"2px 10px 2px 10px;'>{time_start_fmt}</span>"
        f"<span style='background-color: #FFF; color: #444; padding: 0.5em 0.5em; position: "
        f"inherit; margin-right: 5px; border: solid 1px #999999; font-variant-numeric: "
        f"tabular-nums; border-radius: 0; padding: 2px 10px 2px 10px;'>{time_duration_fmt}</span>"
        f"<span style='background-color: #FFF; color: #444; padding: 0.5em 0.5em; position: "
        f"inherit; text-transform: uppercase; margin: 5px 1px 5px -1px; border: solid 1px #999999; "
        f"font-variant-numeric: tabular-nums; border-radius: 0; padding: 2px 10px 2px 10px;'>"
        f"{time_end_fmt}</span>"
        f"</div>"
    )


def _create_label_html(label: str | None, start_time: str) -> str:
    if label is None:
        # Remove the decimal and everything beyond that
        start_time = str(start_time).split(".")[0]

        # Replace the space character with a pipe character
        start_time = start_time.replace(" ", "|")

        label = start_time

    return (
        f"<span style='text-decoration-style: solid; text-decoration-color: #ADD8E6; "
        f"text-decoration-line: underline; text-underline-position: under; color: #333333; "
        f"font-variant-numeric: tabular-nums; padding-left: 4px; margin-right: 5px; "
        f"padding-right: 2px;'>{label}</span>"
    )


def _format_single_integer_with_gt(value: int, locale: str = "en", df_lib=None) -> str:
    """Format a single integer using Great Tables GT object to avoid pandas dependency."""
    if df_lib is None:
        # Use library detection to select appropriate DataFrame library
        if _is_lib_present("polars"):
            import polars as pl

            df_lib = pl
        elif _is_lib_present("pandas"):  # pragma: no cover
            import pandas as pd  # pragma: no cover

            df_lib = pd  # pragma: no cover
        else:  # pragma: no cover
            raise ImportError(
                "Neither Polars nor Pandas is available for formatting"
            )  # pragma: no cover

    # Create a single-row, single-column DataFrame using the specified library
    df = df_lib.DataFrame({"value": [value]})

    # Create GT object and format the column
    gt_obj = GT(df).fmt_integer(columns="value", locale=locale)

    # Extract the formatted value using _get_column_of_values
    formatted_values = _get_column_of_values(gt_obj, column_name="value", context="html")

    return formatted_values[0]  # Return the single formatted value


def _format_single_float_with_gt_custom(
    value: float,
    decimals: int = 2,
    drop_trailing_zeros: bool = False,
    locale: str = "en",
    df_lib=None,
) -> str:
    """Format a single float with custom options using Great Tables GT object to avoid pandas dependency."""
    if df_lib is None:
        # Use library detection to select appropriate DataFrame library
        if _is_lib_present("polars"):
            import polars as pl

            df_lib = pl
        elif _is_lib_present("pandas"):  # pragma: no cover
            import pandas as pd  # pragma: no cover

            df_lib = pd  # pragma: no cover
        else:  # pragma: no cover
            raise ImportError(
                "Neither Polars nor Pandas is available for formatting"
            )  # pragma: no cover

    # Create a single-row, single-column DataFrame using the specified library
    df = df_lib.DataFrame({"value": [value]})

    # Create GT object and format the column
    gt_obj = GT(df).fmt_number(
        columns="value", decimals=decimals, drop_trailing_zeros=drop_trailing_zeros, locale=locale
    )

    # Extract the formatted value using _get_column_of_values
    formatted_values = _get_column_of_values(gt_obj, column_name="value", context="html")

    return formatted_values[0]  # Return the single formatted value


def _create_thresholds_html(thresholds: Thresholds, locale: str, df_lib=None) -> str:
    if thresholds == Thresholds():
        return ""

    # Helper functions to format numbers safely
    def _format_number_safe(value: float, decimals: int, drop_trailing_zeros: bool = False) -> str:
        if df_lib is not None and value is not None:
            # Use GT-based formatting to avoid Pandas dependency completely
            return _format_single_float_with_gt_custom(
                value,
                decimals=decimals,
                drop_trailing_zeros=drop_trailing_zeros,
                locale=locale,
                df_lib=df_lib,
            )
        else:
            # Fallback to the original behavior
            return fmt_number(
                value, decimals=decimals, drop_trailing_zeros=drop_trailing_zeros, locale=locale
            )[0]  # pragma: no cover

    def _format_integer_safe(value: int) -> str:
        if df_lib is not None and value is not None:
            # Use GT-based formatting to avoid Pandas dependency completely
            return _format_single_integer_with_gt(value, locale=locale, df_lib=df_lib)
        else:
            # Fallback to the original behavior
            return fmt_integer(value, locale=locale)[0]

    warning = (
        _format_number_safe(thresholds.warning_fraction, decimals=3, drop_trailing_zeros=True)
        if thresholds.warning_fraction is not None
        else (
            _format_integer_safe(thresholds.warning_count)
            if thresholds.warning_count is not None
            else "&mdash;"
        )
    )

    error = (
        _format_number_safe(thresholds.error_fraction, decimals=3, drop_trailing_zeros=True)
        if thresholds.error_fraction is not None
        else (
            _format_integer_safe(thresholds.error_count)
            if thresholds.error_count is not None
            else "&mdash;"
        )
    )

    critical = (
        _format_number_safe(thresholds.critical_fraction, decimals=3, drop_trailing_zeros=True)
        if thresholds.critical_fraction is not None
        else (
            _format_integer_safe(thresholds.critical_count)
            if thresholds.critical_count is not None
            else "&mdash;"
        )
    )

    warning_color = SEVERITY_LEVEL_COLORS["warning"]
    error_color = SEVERITY_LEVEL_COLORS["error"]
    critical_color = SEVERITY_LEVEL_COLORS["critical"]

    return (
        "<span>"
        f'<span style="background-color: {warning_color}; color: white; '
        "padding: 0.5em 0.5em; position: inherit; text-transform: uppercase; "
        f"margin: 5px 0px 5px 5px; border: solid 1px {warning_color}; "
        'font-weight: bold; padding: 2px 15px 2px 15px; font-size: smaller;">WARNING</span>'
        '<span style="background-color: none; color: #333333; padding: 0.5em 0.5em; '
        "position: inherit; margin: 5px 0px 5px -4px; font-weight: bold; "
        f"border: solid 1px {warning_color}; padding: 2px 15px 2px 15px; "
        'font-size: smaller; margin-right: 5px;">'
        f"{warning}"
        "</span>"
        f'<span style="background-color: {error_color}; color: white; '
        "padding: 0.5em 0.5em; position: inherit; text-transform: uppercase; "
        f"margin: 5px 0px 5px 1px; border: solid 1px {error_color}; "
        'font-weight: bold; padding: 2px 15px 2px 15px; font-size: smaller;">ERROR</span>'
        '<span style="background-color: none; color: #333333; padding: 0.5em 0.5em; '
        "position: inherit; margin: 5px 0px 5px -4px; font-weight: bold; "
        f"border: solid 1px {error_color}; padding: 2px 15px 2px 15px; "
        'font-size: smaller; margin-right: 5px;">'
        f"{error}"
        "</span>"
        f'<span style="background-color: {critical_color}; color: white; '
        "padding: 0.5em 0.5em; position: inherit; text-transform: uppercase; "
        f"margin: 5px 0px 5px 1px; border: solid 1px {critical_color}; "
        'font-weight: bold; padding: 2px 15px 2px 15px; font-size: smaller;">CRITICAL</span>'
        '<span style="background-color: none; color: #333333; padding: 0.5em 0.5em; '
        "position: inherit; margin: 5px 0px 5px -4px; font-weight: bold; "
        f"border: solid 1px {critical_color}; padding: 2px 15px 2px 15px; "
        'font-size: smaller;">'
        f"{critical}"
        "</span>"
        "</span>"
    )


def _step_report_row_based(
    assertion_type: str,
    i: int,
    column: str,
    column_position: int,
    columns_subset: list[str] | None,
    values: any,
    inclusive: tuple[bool, bool] | None,
    n: int,
    n_failed: int,
    all_passed: bool,
    extract: any,
    tbl_preview: GT,
    header: str,
    limit: int | None,
    lang: str,
) -> GT:
    # Get the length of the extracted data for the step
    extract_length = get_row_count(extract)

    # Determine whether the `lang` value represents a right-to-left language
    is_rtl_lang = lang in RTL_LANGUAGES
    direction_rtl = " direction: rtl;" if is_rtl_lang else ""

    # Generate text that indicates the assertion for the validation step
    if assertion_type == "col_vals_gt":
        text = f"{column} > {values}"
    elif assertion_type == "col_vals_lt":
        text = f"{column} < {values}"
    elif assertion_type == "col_vals_eq":
        text = f"{column} = {values}"
    elif assertion_type == "col_vals_ne":
        text = f"{column} &ne; {values}"
    elif assertion_type == "col_vals_ge":
        text = f"{column} &ge; {values}"
    elif assertion_type == "col_vals_le":
        text = f"{column} &le; {values}"
    elif assertion_type == "col_vals_between":
        symbol_left = "&le;" if inclusive[0] else "&lt;"
        symbol_right = "&le;" if inclusive[1] else "&lt;"
        text = f"{values[0]} {symbol_left} {column} {symbol_right} {values[1]}"
    elif assertion_type == "col_vals_outside":
        symbol_left = "&lt;" if inclusive[0] else "&le;"
        symbol_right = "&gt;" if inclusive[1] else "&ge;"
        text = f"{column} {symbol_left} {values[0]}, {column} {symbol_right} {values[1]}"
    elif assertion_type == "col_vals_in_set":
        elements = ", ".join(map(str, values))
        text = f"{column} &isinv; {{{elements}}}"
    elif assertion_type == "col_vals_not_in_set":
        elements = ", ".join(values)
        text = f"{column} &NotElement; {{{elements}}}"
    elif assertion_type == "col_vals_regex":
        pattern = values["pattern"]
        text = STEP_REPORT_TEXT["column_matches_regex"][lang].format(column=column, values=pattern)
    elif assertion_type == "col_vals_null":
        text = STEP_REPORT_TEXT["column_is_null"][lang].format(column=column)
    elif assertion_type == "col_vals_not_null":
        text = STEP_REPORT_TEXT["column_is_not_null"][lang].format(column=column)
    elif assertion_type == "col_vals_expr":
        text = STEP_REPORT_TEXT["column_expr"][lang].format(values=values)
    elif assertion_type == "rows_complete":
        if column is None:
            text = STEP_REPORT_TEXT["rows_complete_all"][lang]
        else:
            text = STEP_REPORT_TEXT["rows_complete_subset"][lang]

    # Wrap assertion text in a <code> tag
    text = (
        f"<code style='color: #303030; font-family: monospace; font-size: smaller;'>{text}</code>"
    )

    if all_passed:
        # Style the target column in green and add borders but only if that column is present
        # in the `tbl_preview` (i.e., it may not be present if `columns_subset=` didn't include it)
        preview_tbl_columns = tbl_preview._boxhead._get_columns()
        preview_tbl_has_target_column = column in preview_tbl_columns

        if preview_tbl_has_target_column:
            step_report = tbl_preview.tab_style(
                style=[
                    style.text(color="#006400"),
                    style.fill(color="#4CA64C33"),
                    style.borders(
                        sides=["left", "right"],
                        color="#1B4D3E80",
                        style="solid",
                        weight="2px",
                    ),
                ],
                locations=loc.body(columns=column),
            ).tab_style(
                style=style.borders(
                    sides=["left", "right"], color="#1B4D3E80", style="solid", weight="2px"
                ),
                locations=loc.column_labels(columns=column),
            )

        else:
            step_report = tbl_preview

        if header is None:
            return step_report

        title = STEP_REPORT_TEXT["report_for_step_i"][lang].format(i=i) + " " + CHECK_MARK_SPAN
        assertion_header_text = STEP_REPORT_TEXT["assertion_header_text"][lang]

        # Use 'success_statement_no_column' for col_vals_expr() since it doesn't target
        # a specific column
        if assertion_type == "col_vals_expr":
            success_stmt = STEP_REPORT_TEXT["success_statement_no_column"][lang].format(
                n=n
            )  # pragma: no cover
        else:
            success_stmt = STEP_REPORT_TEXT["success_statement"][lang].format(
                n=n,
                column_position=column_position,
            )
        preview_stmt = STEP_REPORT_TEXT["preview_statement"][lang]

        details = (
            f"<div style='font-size: 13.6px; {direction_rtl}'>"
            "<div style='padding-top: 7px;'>"
            f"{assertion_header_text} <span style='border-style: solid; border-width: thin; "
            "border-color: lightblue; padding-left: 2px; padding-right: 2px;'>"
            "<code style='color: #303030; background-color: transparent; "
            f"position: relative; bottom: 1px;'>{text}</code></span>"
            "</div>"
            "<div style='padding-top: 7px;'>"
            f"{success_stmt}"
            "</div>"
            f"{preview_stmt}"
            "</div>"
        )

        # Generate the default template text for the header when `":default:"` is used
        if header == ":default:":
            header = "{title}{details}"

        # Use commonmark to convert the header text to HTML
        header = commonmark.commonmark(header)

        # Place any templated text in the header
        header = header.format(title=title, details=details)

        # Create the header with `header` string
        step_report = step_report.tab_header(title=md(header))

    else:
        if limit is None:
            limit = extract_length

        # Create a preview of the extracted data
        extract_tbl = _generate_display_table(
            data=extract,
            columns_subset=columns_subset,
            n_head=limit,
            n_tail=0,
            limit=limit,
            min_tbl_width=600,
            incl_header=False,
            mark_missing_values=False,
        )

        # Style the target column in green and add borders but only if that column is present
        # in the `extract_tbl` (i.e., it may not be present if `columns_subset=` didn't include it)
        extract_tbl_columns = extract_tbl._boxhead._get_columns()
        extract_tbl_has_target_column = column in extract_tbl_columns

        if extract_tbl_has_target_column:
            step_report = extract_tbl.tab_style(
                style=[
                    style.text(color="#B22222"),
                    style.fill(color="#FFC1C159"),
                    style.borders(
                        sides=["left", "right"], color="black", style="solid", weight="2px"
                    ),
                ],
                locations=loc.body(columns=column),
            ).tab_style(
                style=style.borders(
                    sides=["left", "right"], color="black", style="solid", weight="2px"
                ),
                locations=loc.column_labels(columns=column),
            )

            not_shown = ""
            shown_failures = STEP_REPORT_TEXT["shown_failures"][lang]
        else:
            step_report = extract_tbl
            not_shown = STEP_REPORT_TEXT["not_shown"][lang]
            shown_failures = ""

        title = STEP_REPORT_TEXT["report_for_step_i"][lang].format(i=i)
        assertion_header_text = STEP_REPORT_TEXT["assertion_header_text"][lang]
        failure_rate_metrics = f"<strong>{n_failed}</strong> / <strong>{n}</strong>"

        # Use failure_rate_summary_no_column for col_vals_expr since it doesn't target a specific column
        if assertion_type == "col_vals_expr":
            failure_rate_stmt = STEP_REPORT_TEXT["failure_rate_summary_no_column"][lang].format(
                failure_rate=failure_rate_metrics
            )
        else:
            failure_rate_stmt = STEP_REPORT_TEXT["failure_rate_summary"][lang].format(
                failure_rate=failure_rate_metrics,
                column_position=column_position,
            )

        if limit < extract_length:
            extract_length_resolved = limit
            extract_text = STEP_REPORT_TEXT["extract_text_first"][lang].format(
                extract_length_resolved=extract_length_resolved, shown_failures=shown_failures
            )

        else:
            extract_length_resolved = extract_length
            extract_text = STEP_REPORT_TEXT["extract_text_all"][lang].format(
                extract_length_resolved=extract_length_resolved, shown_failures=shown_failures
            )

        details = (
            f"<div style='font-size: 13.6px; {direction_rtl}'>"
            "<div style='padding-top: 7px;'>"
            f"{assertion_header_text} <span style='border-style: solid; border-width: thin; "
            "border-color: lightblue; padding-left: 2px; padding-right: 2px;'>"
            "<code style='color: #303030; background-color: transparent; "
            f"position: relative; bottom: 1px;'>{text}</code></span>"
            "</div>"
            "<div style='padding-top: 7px;'>"
            f"{failure_rate_stmt} {not_shown}"
            "</div>"
            f"{extract_text}"
            "</div>"
        )

        # If `header` is None then don't add a header and just return the step report
        if header is None:
            return step_report

        # Generate the default template text for the header when `":default:"` is used
        if header == ":default:":
            header = "{title}{details}"

        # Use commonmark to convert the header text to HTML
        header = commonmark.commonmark(header)

        # Place any templated text in the header
        header = header.format(title=title, details=details)

        # Create the header with `header` string
        step_report = step_report.tab_header(title=md(header))

    return step_report


def _step_report_rows_distinct(
    i: int,
    column: list[str],
    column_position: list[int],
    columns_subset: list[str] | None,
    n: int,
    n_failed: int,
    all_passed: bool,
    extract: any,
    tbl_preview: GT,
    header: str,
    limit: int | None,
    lang: str,
) -> GT:
    # Get the length of the extracted data for the step
    extract_length = get_row_count(extract)

    # Determine whether the `lang` value represents a right-to-left language
    is_rtl_lang = lang in RTL_LANGUAGES
    direction_rtl = " direction: rtl;" if is_rtl_lang else ""

    if column is None:
        text = STEP_REPORT_TEXT["rows_distinct_all"][lang].format(column=column)
    else:
        columns_list = ", ".join(column)
        text = STEP_REPORT_TEXT["rows_distinct_subset"][lang].format(columns_subset=columns_list)

    if all_passed:
        step_report = tbl_preview

        if header is None:
            return step_report

        title = STEP_REPORT_TEXT["report_for_step_i"][lang].format(i=i) + " " + CHECK_MARK_SPAN

        success_stmt = STEP_REPORT_TEXT["success_statement_no_column"][lang].format(
            n=n,
            column_position=column_position,
        )
        preview_stmt = STEP_REPORT_TEXT["preview_statement"][lang]

        details = (
            f"<div style='font-size: 13.6px; {direction_rtl}'>"
            "<div style='padding-top: 7px;'>"
            f"{text}"
            "</div>"
            "<div style='padding-top: 7px;'>"
            f"{success_stmt}"
            "</div>"
            f"{preview_stmt}"
            "</div>"
        )

        # Generate the default template text for the header when `":default:"` is used
        if header == ":default:":
            header = "{title}{details}"

        # Use commonmark to convert the header text to HTML
        header = commonmark.commonmark(header)

        # Place any templated text in the header
        header = header.format(title=title, details=details)

        # Create the header with `header` string
        step_report = step_report.tab_header(title=md(header))

    else:
        if limit is None:
            limit = extract_length

        # Create a preview of the extracted data
        step_report = _generate_display_table(
            data=extract,
            columns_subset=columns_subset,
            n_head=limit,
            n_tail=0,
            limit=limit,
            min_tbl_width=600,
            incl_header=False,
            mark_missing_values=False,
        )

        title = STEP_REPORT_TEXT["report_for_step_i"][lang].format(i=i)
        failure_rate_metrics = f"<strong>{n_failed}</strong> / <strong>{n}</strong>"

        failure_rate_stmt = STEP_REPORT_TEXT["failure_rate_summary_rows_distinct"][lang].format(
            failure_rate=failure_rate_metrics,
            column_position=column_position,
        )

        if limit < extract_length:  # pragma: no cover
            extract_length_resolved = limit
            extract_text = STEP_REPORT_TEXT["extract_text_first_rows_distinct"][lang].format(
                extract_length_resolved=extract_length_resolved
            )

        else:
            extract_length_resolved = extract_length
            extract_text = STEP_REPORT_TEXT["extract_text_all_rows_distinct"][lang].format(
                extract_length_resolved=extract_length_resolved
            )

        details = (
            f"<div style='font-size: 13.6px; {direction_rtl}'>"
            "<div style='padding-top: 7px;'>"
            f"{text}"
            "</div>"
            "<div style='padding-top: 7px;'>"
            f"{failure_rate_stmt}"
            "</div>"
            f"{extract_text}"
            "</div>"
        )

        # If `header` is None then don't add a header and just return the step report
        if header is None:
            return step_report

        # Generate the default template text for the header when `":default:"` is used
        if header == ":default:":
            header = "{title}{details}"

        # Use commonmark to convert the header text to HTML
        header = commonmark.commonmark(header)

        # Place any templated text in the header
        header = header.format(title=title, details=details)

        # Create the header with `header` string
        step_report = step_report.tab_header(title=md(header))

    return step_report


def _step_report_schema_in_order(
    step: int, schema_info: dict, header: str, lang: str, debug_return_df: bool = False
) -> GT | any:
    """
    This is the case for schema validation where the schema is supposed to have the same column
    order as the target table.
    """

    # Determine whether the `lang` value represents a right-to-left language
    is_rtl_lang = lang in RTL_LANGUAGES
    direction_rtl = " direction: rtl;" if is_rtl_lang else ""

    all_passed = schema_info["passed"]
    complete = schema_info["params"]["complete"]

    expect_schema = schema_info["expect_schema"]
    target_schema = schema_info["target_schema"]

    # Get the expected column names from the expected and target schemas
    colnames_exp = [x[0] for x in expect_schema]
    colnames_tgt = [x[0] for x in target_schema]
    dtypes_tgt = [str(x[1]) for x in target_schema]

    # Extract the dictionary of expected columns, their data types, whether the column matched
    # a target column, and whether the data type matched the target data type
    exp_columns_dict = schema_info["columns"]

    # Create a Polars DF with the target table columns and dtypes
    import polars as pl

    # Create a DataFrame for the LHS of the table
    schema_tbl = pl.DataFrame(
        {
            "index_target": range(1, len(colnames_tgt) + 1),
            "col_name_target": colnames_tgt,
            "dtype_target": dtypes_tgt,
        }
    )

    # Is the number of column names supplied equal to the number of columns in the
    # target table?
    if len(expect_schema) > len(target_schema):
        schema_length = "longer"
        # Get indices of the extra rows in the schema table
        extra_rows_i = list(range(len(target_schema), len(expect_schema)))
    elif len(expect_schema) < len(target_schema):
        schema_length = "shorter"
        # Get indices of the extra rows (on the target side) in the schema table
        extra_rows_i = list(range(len(expect_schema), len(target_schema)))
    else:
        schema_length = "equal"
        extra_rows_i = []

    # For the right-hand side of the table, we need to find out if the expected column names matched
    col_name_exp = []
    col_exp_correct = []
    dtype_exp = []
    dtype_exp_correct = []

    for i in range(len(exp_columns_dict)):
        #
        # `col_name_exp` values
        #

        # The column name is the key in the dictionary, get the column name and
        # append it to the `col_name_exp` list
        col_name_exp.append(list(exp_columns_dict.keys())[i])

        column_name_exp_i = col_name_exp[i]

        #
        # `col_exp_correct` values
        #

        if (
            exp_columns_dict[column_name_exp_i]["colname_matched"]
            and exp_columns_dict[column_name_exp_i]["index_matched"]
        ):
            col_exp_correct.append(CHECK_MARK_SPAN)
        else:
            col_exp_correct.append(CROSS_MARK_SPAN)

        #
        # `dtype_exp` values
        #

        if not exp_columns_dict[column_name_exp_i]["dtype_present"]:
            dtype_exp.append("&mdash;")

        elif len(exp_columns_dict[column_name_exp_i]["dtype_input"]) > 1:
            # Case where there are multiple dtypes provided for the column in the schema (i.e.,
            # there are multiple attempts to match the dtype)

            # Get the dtypes for the column, this is a list of at least two dtypes
            dtype = exp_columns_dict[column_name_exp_i]["dtype_input"]

            if (
                exp_columns_dict[column_name_exp_i]["dtype_matched_pos"] is not None
                and exp_columns_dict[column_name_exp_i]["colname_matched"]
                and exp_columns_dict[column_name_exp_i]["index_matched"]
            ):
                # Only underline the matched dtype under the conditions that the column name is
                # matched correctly (name and index)

                pos = exp_columns_dict[column_name_exp_i]["dtype_matched_pos"]

                # Combine the dtypes together with pipes but underline the matched dtype in
                # green with an HTML span tag and style attribute
                dtype = [
                    (
                        '<span style="text-decoration: underline; text-decoration-color: #4CA64C; '
                        f'text-underline-offset: 3px;">{dtype[i]}</span>'
                        if i == pos
                        else dtype[i]
                    )
                    for i in range(len(dtype))
                ]
                dtype = " | ".join(dtype)
                dtype_exp.append(dtype)

            else:
                # If the column name or index did not match (or if it did and none of the dtypes
                # matched), then join the dtypes together with pipes with further decoration

                dtype = " | ".join(dtype)
                dtype_exp.append(dtype)

        else:
            dtype = exp_columns_dict[column_name_exp_i]["dtype_input"][0]
            dtype_exp.append(dtype)

        #
        # `dtype_exp_correct` values
        #

        if (
            not exp_columns_dict[column_name_exp_i]["colname_matched"]
            or not exp_columns_dict[column_name_exp_i]["index_matched"]
        ):
            dtype_exp_correct.append("&mdash;")
        elif not exp_columns_dict[column_name_exp_i]["dtype_present"]:
            dtype_exp_correct.append("")
        elif exp_columns_dict[column_name_exp_i]["dtype_matched"]:
            dtype_exp_correct.append(CHECK_MARK_SPAN)
        else:
            dtype_exp_correct.append(CROSS_MARK_SPAN)

    schema_exp = pl.DataFrame(
        {
            "index_exp": range(1, len(colnames_exp) + 1),
            "col_name_exp": colnames_exp,
            "col_name_exp_correct": col_exp_correct,
            "dtype_exp": dtype_exp,
            "dtype_exp_correct": dtype_exp_correct,
        }
    )

    # Concatenate the tables horizontally
    schema_combined = pl.concat([schema_tbl, schema_exp], how="horizontal")

    # Return the DataFrame if the `debug_return_df` parameter is set to True
    if debug_return_df:
        return schema_combined

    target_str = STEP_REPORT_TEXT["schema_target"][lang]
    expected_str = STEP_REPORT_TEXT["schema_expected"][lang]
    column_str = STEP_REPORT_TEXT["schema_column"][lang]
    data_type_str = STEP_REPORT_TEXT["schema_data_type"][lang]
    supplied_column_schema_str = STEP_REPORT_TEXT["supplied_column_schema"][lang]

    step_report = (
        GT(schema_combined, id="pb_step_tbl")
        .fmt_markdown(columns=None)
        .opt_table_font(font=google_font(name="IBM Plex Sans"))
        .opt_align_table_header(align="left")
        .cols_label(
            cases={
                "index_target": "",
                "col_name_target": column_str,
                "dtype_target": data_type_str,
                "index_exp": "",
                "col_name_exp": column_str,
                "col_name_exp_correct": "",
                "dtype_exp": data_type_str,
                "dtype_exp_correct": "",
            }
        )
        .cols_width(
            cases={
                "index_target": "40px",
                "col_name_target": "190px",
                "dtype_target": "190px",
                "index_exp": "40px",
                "col_name_exp": "190px",
                "col_name_exp_correct": "30px",
                "dtype_exp": "190px",
                "dtype_exp_correct": "30px",
            }
        )
        .tab_style(
            style=style.text(color="black", font=google_font(name="IBM Plex Mono"), size="13px"),
            locations=loc.body(
                columns=["col_name_target", "dtype_target", "col_name_exp", "dtype_exp"]
            ),
        )
        .tab_style(
            style=style.text(size="13px"),
            locations=loc.body(columns=["index_target", "index_exp"]),
        )
        .tab_style(
            style=style.borders(sides="left", color="#E5E5E5", style="double", weight="3px"),
            locations=loc.body(columns="index_exp"),
        )
        .tab_style(
            style=style.css("white-space: nowrap; text-overflow: ellipsis; overflow: hidden;"),
            locations=loc.body(
                columns=["col_name_target", "dtype_target", "col_name_exp", "dtype_exp"]
            ),
        )
        .tab_spanner(
            label=target_str,
            columns=["index_target", "col_name_target", "dtype_target"],
        )
        .tab_spanner(
            label=expected_str,
            columns=[
                "index_exp",
                "col_name_exp",
                "col_name_exp_correct",
                "dtype_exp",
                "dtype_exp_correct",
            ],
        )
        .sub_missing(
            columns=[
                "index_target",
                "col_name_target",
                "dtype_target",
                "index_exp",
                "col_name_exp",
                "col_name_exp_correct",
                "dtype_exp",
                "dtype_exp_correct",
            ],
            missing_text="",
        )
        .tab_source_note(
            source_note=html(
                f"<div style='padding-bottom: 2px;'>{supplied_column_schema_str}</div>"
                "<div style='border-style: solid; border-width: thin; border-color: lightblue; "
                "padding-left: 2px; padding-right: 2px; padding-bottom: 3px;'><code "
                "style='color: #303030; font-family: monospace; font-size: 8px;'>"
                f"{expect_schema}</code></div>"
            )
        )
        .tab_options(source_notes_font_size="12px")
    )

    if schema_length == "shorter":
        # Add background color to the missing column on the exp side
        step_report = step_report.tab_style(
            style=style.fill(color="#FFC1C159"),
            locations=loc.body(
                columns=[
                    "index_exp",
                    "col_name_exp",
                    "col_name_exp_correct",
                    "dtype_exp",
                    "dtype_exp_correct",
                ],
                rows=extra_rows_i,
            ),
        )

    if schema_length == "longer":
        # Add background color to the missing column on the target side
        step_report = step_report.tab_style(
            style=style.fill(color="#F3F3F3"),
            locations=loc.body(
                columns=[
                    "index_target",
                    "col_name_target",
                    "dtype_target",
                ],
                rows=extra_rows_i,
            ),
        )

        # Add a border below the row that terminates the target table schema
        step_report = step_report.tab_style(
            style=style.borders(sides="bottom", color="#6699CC80", style="solid", weight="1px"),
            locations=loc.body(rows=len(colnames_tgt) - 1),
        )

    # If the version of `great_tables` is `>=0.17.0` then disable Quarto table processing
    if version("great_tables") >= "0.17.0":
        step_report = step_report.tab_options(quarto_disable_processing=True)

    # If `header` is None then don't add a header and just return the step report
    if header is None:
        return step_report

    # Get the other parameters for the `col_schema_match()` function
    case_sensitive_colnames = schema_info["params"]["case_sensitive_colnames"]
    case_sensitive_dtypes = schema_info["params"]["case_sensitive_dtypes"]
    full_match_dtypes = schema_info["params"]["full_match_dtypes"]

    # Get the passing symbol for the step
    passing_symbol = CHECK_MARK_SPAN if all_passed else CROSS_MARK_SPAN

    # Generate the title for the step report
    title = STEP_REPORT_TEXT["report_for_step_i"][lang].format(i=step) + " " + passing_symbol

    # Generate the details for the step report
    details = _create_col_schema_match_params_html(
        lang=lang,
        complete=complete,
        in_order=True,
        case_sensitive_colnames=case_sensitive_colnames,
        case_sensitive_dtypes=case_sensitive_dtypes,
        full_match_dtypes=full_match_dtypes,
    )

    # Generate the default template text for the header when `":default:"` is used
    if header == ":default:":
        header = "{title}{details}"

    # Use commonmark to convert the header text to HTML
    header = commonmark.commonmark(header)

    # Place any templated text in the header
    header = header.format(title=title, details=details)

    # Create the header with `header` string
    step_report = step_report.tab_header(title=md(header))

    return step_report


def _step_report_schema_any_order(
    step: int, schema_info: dict, header: str, lang: str, debug_return_df: bool = False
) -> GT | any:
    """
    This is the case for schema validation where the schema is permitted to not have to be in the
    same column order as the target table.
    """

    # Determine whether the `lang` value represents a right-to-left language
    is_rtl_lang = lang in RTL_LANGUAGES
    direction_rtl = " direction: rtl;" if is_rtl_lang else ""

    all_passed = schema_info["passed"]
    complete = schema_info["params"]["complete"]

    expect_schema = schema_info["expect_schema"]
    target_schema = schema_info["target_schema"]

    columns_found = schema_info["columns_found"]
    columns_not_found = schema_info["columns_not_found"]
    colnames_exp_unmatched = schema_info["columns_unmatched"]

    # Get the expected column names from the expected and target schemas
    colnames_exp = [x[0] for x in expect_schema]
    colnames_tgt = [x[0] for x in target_schema]
    dtypes_tgt = [str(x[1]) for x in target_schema]

    # Extract the dictionary of expected columns, their data types, whether the column matched
    # a target column, and whether the data type matched the target data type
    exp_columns_dict = schema_info["columns"]

    index_target = range(1, len(colnames_tgt) + 1)

    # Create a Polars DF with the target table columns and dtypes
    import polars as pl

    # Create a DataFrame for the LHS of the table
    schema_tbl = pl.DataFrame(
        {
            "index_target": index_target,
            "col_name_target": colnames_tgt,
            "dtype_target": dtypes_tgt,
        }
    )

    # For the right-hand side of the table, we need to find out if the expected column names matched
    # in any order, this involves iterating over the target colnames first, seeing if there is a
    # match in the expected colnames, and then checking if the dtype matches
    index_exp = []
    col_name_exp = []
    col_exp_correct = []
    dtype_exp = []
    dtype_exp_correct = []

    # Get keys of the `exp_columns_dict` dictionary (remove the unmatched columns
    # of `colnames_exp_unmatched`)
    exp_columns_dict_keys = list(exp_columns_dict.keys())

    for colname_unmatched in colnames_exp_unmatched:
        exp_columns_dict_keys.remove(colname_unmatched)

    for i in range(len(colnames_tgt)):
        # If there is no match in the expected column names, then the column name is not present
        # and we need to fill in the values with empty strings

        match_index = None

        for key in exp_columns_dict_keys:
            if colnames_tgt[i] in exp_columns_dict[key]["matched_to"]:
                # Get the index of the key in the dictionary
                match_index = exp_columns_dict_keys.index(key)
                break

        if match_index is not None:
            # Get the column name which is the key of the dictionary at match_index
            column_name_exp_i = list(exp_columns_dict.keys())[match_index]
            col_name_exp.append(column_name_exp_i)

            # Get the index number of the column name in the expected schema (1-indexed)
            index_exp_i = colnames_exp.index(column_name_exp_i) + 1
            index_exp.append(str(index_exp_i))

        else:
            index_exp.append("")
            col_name_exp.append("")
            col_exp_correct.append("")
            dtype_exp.append("")
            dtype_exp_correct.append("")
            continue

        #
        # `col_exp_correct` values
        #

        if exp_columns_dict[column_name_exp_i]["colname_matched"]:
            col_exp_correct.append(CHECK_MARK_SPAN)
        else:
            col_exp_correct.append(CROSS_MARK_SPAN)  # pragma: no cover

        #
        # `dtype_exp` values
        #

        if not exp_columns_dict[column_name_exp_i]["dtype_present"]:
            dtype_exp.append("")  # pragma: no cover

        elif len(exp_columns_dict[column_name_exp_i]["dtype_input"]) > 1:
            dtype = exp_columns_dict[column_name_exp_i]["dtype_input"]

            if exp_columns_dict[column_name_exp_i]["dtype_matched_pos"] is not None:
                pos = exp_columns_dict[column_name_exp_i]["dtype_matched_pos"]

                # Combine the dtypes together with pipes but underline the matched dtype in
                # green with an HTML span tag and style attribute
                dtype = [
                    (
                        '<span style="text-decoration: underline; text-decoration-color: #4CA64C; '
                        f'text-underline-offset: 3px;">{dtype[i]}</span>'
                        if i == pos
                        else dtype[i]
                    )
                    for i in range(len(dtype))
                ]
                dtype = " | ".join(dtype)
                dtype_exp.append(dtype)

            else:
                dtype = " | ".join(dtype)
                dtype_exp.append(dtype)

        else:
            dtype = exp_columns_dict[column_name_exp_i]["dtype_input"][0]
            dtype_exp.append(dtype)

        #
        # `dtype_exp_correct` values
        #

        if not exp_columns_dict[column_name_exp_i]["colname_matched"]:
            dtype_exp_correct.append("&mdash;")  # pragma: no cover
        elif not exp_columns_dict[column_name_exp_i]["dtype_present"]:
            dtype_exp_correct.append("")  # pragma: no cover
        elif exp_columns_dict[column_name_exp_i]["dtype_matched"]:
            dtype_exp_correct.append(CHECK_MARK_SPAN)
        else:
            dtype_exp_correct.append(CROSS_MARK_SPAN)

    # Create a DataFrame with the expected column names and dtypes
    schema_exp = pl.DataFrame(
        {
            "index_exp": index_exp,
            "col_name_exp": col_name_exp,
            "col_name_exp_correct": col_exp_correct,
            "dtype_exp": dtype_exp,
            "dtype_exp_correct": dtype_exp_correct,
        }
    )

    # If there are unmatched columns in the expected schema, then create a separate DataFrame
    # for those entries and concatenate it with the `schema_combined` DataFrame
    if len(colnames_exp_unmatched) > 0:
        # Get the indices of the unmatched columns by comparing the `colnames_exp_unmatched`
        # against the schema order
        col_name_exp = []
        col_exp_correct = []
        dtype_exp = []
        dtype_exp_correct = []

        for i in range(len(colnames_exp_unmatched)):
            #
            # `col_name_exp` values
            #

            column_name_exp_i = colnames_exp_unmatched[i]
            col_name_exp.append(column_name_exp_i)

            #
            # `col_exp_correct` values
            #

            col_exp_correct.append(CROSS_MARK_SPAN)

            #
            # `dtype_exp` values
            #

            if not exp_columns_dict[column_name_exp_i]["dtype_present"]:
                dtype_exp.append("")  # pragma: no cover

            elif len(exp_columns_dict[column_name_exp_i]["dtype_input"]) > 1:
                dtype = exp_columns_dict[column_name_exp_i]["dtype_input"]  # pragma: no cover

                if (
                    exp_columns_dict[column_name_exp_i]["dtype_matched_pos"] is not None
                ):  # pragma: no cover
                    pos = exp_columns_dict[column_name_exp_i][
                        "dtype_matched_pos"
                    ]  # pragma: no cover

                    # Combine the dtypes together with pipes but underline the matched dtype in
                    # green with an HTML span tag and style attribute
                    dtype = [
                        (
                            '<span style="text-decoration: underline; text-decoration-color: #4CA64C; '
                            f'text-underline-offset: 3px;">{dtype[i]}</span>'
                            if i == pos
                            else dtype[i]
                        )
                        for i in range(len(dtype))
                    ]  # pragma: no cover
                    dtype = " | ".join(dtype)  # pragma: no cover
                    dtype_exp.append(dtype)  # pragma: no cover

                else:
                    dtype = " | ".join(dtype)  # pragma: no cover
                    dtype_exp.append(dtype)  # pragma: no cover

            else:
                dtype = exp_columns_dict[column_name_exp_i]["dtype_input"][0]
                dtype_exp.append(dtype)

            #
            # `dtype_exp_correct` values
            #

            if not exp_columns_dict[column_name_exp_i]["colname_matched"]:
                dtype_exp_correct.append("&mdash;")
            elif not exp_columns_dict[column_name_exp_i]["dtype_present"]:  # pragma: no cover
                dtype_exp_correct.append("")  # pragma: no cover
            elif exp_columns_dict[column_name_exp_i]["dtype_matched"]:  # pragma: no cover
                dtype_exp_correct.append(CHECK_MARK_SPAN)  # pragma: no cover
            else:  # pragma: no cover
                dtype_exp_correct.append(CROSS_MARK_SPAN)  # pragma: no cover

        if len(columns_found) > 0:
            # Get the last index of the columns found
            last_index = columns_found[-1]

            # Get the integer index of the last column found in the target schema
            last_index_int = colnames_tgt.index(last_index)

            # Generate the range and convert to strings
            index_exp = [
                str(i + len(columns_found) - 1)
                for i in range(last_index_int, last_index_int + len(colnames_exp_unmatched))
            ]

        else:
            index_exp = [
                str(i) for i in range(1, len(colnames_exp_unmatched) + 1)
            ]  # pragma: no cover

        schema_exp_unmatched = pl.DataFrame(
            {
                "index_exp": index_exp,
                "col_name_exp": col_name_exp,
                "col_name_exp_correct": col_exp_correct,
                "dtype_exp": dtype_exp,
                "dtype_exp_correct": dtype_exp_correct,
            }
        )

        # Combine this DataFrame to the `schema_exp` DataFrame
        schema_exp = pl.concat([schema_exp, schema_exp_unmatched], how="vertical")

    # Concatenate the tables horizontally
    schema_combined = pl.concat([schema_tbl, schema_exp], how="horizontal")

    # Return the DataFrame if the `debug_return_df` parameter is set to True
    if debug_return_df:
        return schema_combined

    target_str = STEP_REPORT_TEXT["schema_target"][lang]
    expected_str = STEP_REPORT_TEXT["schema_expected"][lang]
    column_str = STEP_REPORT_TEXT["schema_column"][lang]
    data_type_str = STEP_REPORT_TEXT["schema_data_type"][lang]
    supplied_column_schema_str = STEP_REPORT_TEXT["supplied_column_schema"][lang]

    step_report = (
        GT(schema_combined, id="pb_step_tbl")
        .fmt_markdown(columns=None)
        .opt_table_font(font=google_font(name="IBM Plex Sans"))
        .opt_align_table_header(align="left")
        .cols_label(
            cases={
                "index_target": "",
                "col_name_target": column_str,
                "dtype_target": data_type_str,
                "index_exp": "",
                "col_name_exp": column_str,
                "col_name_exp_correct": "",
                "dtype_exp": data_type_str,
                "dtype_exp_correct": "",
            }
        )
        .cols_width(
            cases={
                "index_target": "40px",
                "col_name_target": "190px",
                "dtype_target": "190px",
                "index_exp": "40px",
                "col_name_exp": "190px",
                "col_name_exp_correct": "30px",
                "dtype_exp": "190px",
                "dtype_exp_correct": "30px",
            }
        )
        .cols_align(align="right", columns="index_exp")
        .tab_style(
            style=style.text(color="black", font=google_font(name="IBM Plex Mono"), size="13px"),
            locations=loc.body(
                columns=["col_name_target", "dtype_target", "col_name_exp", "dtype_exp"]
            ),
        )
        .tab_style(
            style=style.text(size="13px"),
            locations=loc.body(columns=["index_target", "index_exp"]),
        )
        .tab_style(
            style=style.borders(sides="left", color="#E5E5E5", style="double", weight="3px"),
            locations=loc.body(columns="index_exp"),
        )
        .tab_style(
            style=style.css("white-space: nowrap; text-overflow: ellipsis; overflow: hidden;"),
            locations=loc.body(
                columns=["col_name_target", "dtype_target", "col_name_exp", "dtype_exp"]
            ),
        )
        .tab_spanner(
            label=target_str,
            columns=["index_target", "col_name_target", "dtype_target"],
        )
        .tab_spanner(
            label=expected_str,
            columns=[
                "index_exp",
                "col_name_exp",
                "col_name_exp_correct",
                "dtype_exp",
                "dtype_exp_correct",
            ],
        )
        .sub_missing(
            columns=[
                "index_target",
                "col_name_target",
                "dtype_target",
                "index_exp",
                "col_name_exp",
                "col_name_exp_correct",
                "dtype_exp",
                "dtype_exp_correct",
            ],
            missing_text="",
        )
        .tab_source_note(
            source_note=html(
                f"<div style='padding-bottom: 2px;'>{supplied_column_schema_str}</div>"
                "<div style='border-style: solid; border-width: thin; border-color: lightblue; "
                "padding-left: 2px; padding-right: 2px; padding-bottom: 3px;'><code "
                "style='color: #303030; font-family: monospace; font-size: 8px;'>"
                f"{expect_schema}</code></div>"
            )
        )
        .tab_options(source_notes_font_size="12px")
    )

    # Add background color to signify limits of target table schema (on LHS side)
    if len(colnames_exp_unmatched) > 0:
        step_report = step_report.tab_style(
            style=style.fill(color="#F3F3F3"),
            locations=loc.body(
                columns=[
                    "index_target",
                    "col_name_target",
                    "dtype_target",
                ],
                rows=pl.col("index_target").is_null(),
            ),
        )

    # If the version of `great_tables` is `>=0.17.0` then disable Quarto table processing
    if version("great_tables") >= "0.17.0":
        step_report = step_report.tab_options(quarto_disable_processing=True)

    # If `header` is None then don't add a header and just return the step report
    if header is None:
        return step_report

    # Get the other parameters for the `col_schema_match()` function
    case_sensitive_colnames = schema_info["params"]["case_sensitive_colnames"]
    case_sensitive_dtypes = schema_info["params"]["case_sensitive_dtypes"]
    full_match_dtypes = schema_info["params"]["full_match_dtypes"]

    # Get the passing symbol for the step
    passing_symbol = CHECK_MARK_SPAN if all_passed else CROSS_MARK_SPAN

    # Generate the title for the step report
    title = STEP_REPORT_TEXT["report_for_step_i"][lang].format(i=step) + " " + passing_symbol

    # Generate the details for the step report
    details = _create_col_schema_match_params_html(
        lang=lang,
        complete=complete,
        in_order=False,
        case_sensitive_colnames=case_sensitive_colnames,
        case_sensitive_dtypes=case_sensitive_dtypes,
        full_match_dtypes=full_match_dtypes,
    )

    # Generate the default template text for the header when `":default:"` is used
    if header == ":default:":
        header = "{title}{details}"

    # Use commonmark to convert the header text to HTML
    header = commonmark.commonmark(header)

    # Place any templated text in the header
    header = header.format(title=title, details=details)

    # Create the header with `header` string
    step_report = step_report.tab_header(title=md(header))

    return step_report


def _create_label_text_html(
    text: str,
    strikethrough: bool = False,
    strikethrough_color: str = "#DC143C",
    border_width: str = "1px",
    border_color: str = "#87CEFA",
    border_radius: str = "5px",
    background_color: str = "#F0F8FF",
    font_size: str = "x-small",
    padding_left: str = "4px",
    padding_right: str = "4px",
    margin_left: str = "5px",
    margin_right: str = "5px",
    margin_top: str = "2px",
) -> str:
    if strikethrough:
        strikethrough_rules = (
            f" text-decoration: line-through; text-decoration-color: {strikethrough_color};"
        )
    else:
        strikethrough_rules = ""

    return f'<div style="border-style: solid; border-width: {border_width}; border-color: {border_color}; border-radius: {border_radius}; background-color: {background_color}; font-size: {font_size}; padding-left: {padding_left}; padding-right: {padding_right}; margin-left: {margin_left}; margin-right: {margin_right};  margin-top: {margin_top}; {strikethrough_rules}">{text}</div>'


def _create_col_schema_match_params_html(
    lang: str,
    complete: bool = True,
    in_order: bool = True,
    case_sensitive_colnames: bool = True,
    case_sensitive_dtypes: bool = True,
    full_match_dtypes: bool = True,
) -> str:
    complete_str = STEP_REPORT_TEXT["schema_complete"][lang]
    in_order_str = STEP_REPORT_TEXT["schema_in_order"][lang]
    column_schema_match_str = STEP_REPORT_TEXT["column_schema_match_str"][lang]

    complete_text = _create_label_text_html(
        text=complete_str,
        strikethrough=not complete,
        strikethrough_color="steelblue",
    )

    in_order_text = _create_label_text_html(
        text=in_order_str,
        strikethrough=not in_order,
        strikethrough_color="steelblue",
    )

    symbol_case_sensitive_colnames = "&ne;" if case_sensitive_colnames else "="

    case_sensitive_colnames_text = _create_label_text_html(
        text=f"COLUMN {symbol_case_sensitive_colnames} column",
        strikethrough=False,
        border_color="#A9A9A9",
        background_color="#F5F5F5",
    )

    symbol_case_sensitive_dtypes = "&ne;" if case_sensitive_dtypes else "="

    case_sensitive_dtypes_text = _create_label_text_html(
        text=f"DTYPE {symbol_case_sensitive_dtypes} dtype",
        strikethrough=False,
        border_color="#A9A9A9",
        background_color="#F5F5F5",
    )

    symbol_full_match_dtypes = "&ne;" if full_match_dtypes else "="

    full_match_dtypes_text = _create_label_text_html(
        text=f"float {symbol_full_match_dtypes} float64",
        strikethrough=False,
        border_color="#A9A9A9",
        background_color="#F5F5F5",
    )

    return (
        '<div style="display: flex; font-size: 13.7px; padding-top: 7px;">'
        f'<div style="margin-right: 5px;">{column_schema_match_str}</div>'
        f"{complete_text}"
        f"{in_order_text}"
        f"{case_sensitive_colnames_text}"
        f"{case_sensitive_dtypes_text}"
        f"{full_match_dtypes_text}"
        "</div>"
    )

import logging
from multiprocessing import current_process
from pathlib import Path

import numpy as np
import pandas as pd

from util import parallel_processing


def batch_recompute(error_files: [Path], params: dict):
    summary_file = params["summary_file"].with_stem(params["summary_file"].stem + "_"
                                                    + str(parallel_processing.get_bucket_id()))
    logger = logging.getLogger(current_process().name)
    write_error_headers(summary_file)
    total = len(error_files)
    for i, error_file in enumerate(error_files):
        try:
            recompute_errors(error_file, summary_file)
            logger.info(f"({i + 1}/{total}) Completed: {error_file}")
        except Exception as e:
            logger.error(e)


def recompute_errors(error_file: Path, summary_file: Path):
    run_id = str(error_file.stem).split("_")[-1]
    errors = pd.read_csv(error_file)
    errors["scaled_row_value"] = errors["row_value"] / errors["fine_data"].str.len()
    errors["actual_value"] = pd.DataFrame(errors["fine_data"].values.tolist()).mean(1)
    errors["error"] = errors["scaled_row_value"] - errors["actual_value"]

    errors["ape"] = np.where(errors["actual_value"] != 0, abs(errors["error"]) / errors["actual_value"], -1)
    errors["s_ape"] = np.where(errors["actual_value"] != 0, abs(errors["error"])
                               / ((errors["actual_value"] + errors["scaled_row_value"])/2), -1)
    abs_apes = abs(errors["ape"])
    mape = abs_apes.mean()
    abs_sapes = abs(errors["s_ape"])
    smape = abs_sapes.mean()
    smape_ignore_missing = errors.loc[errors["s_ape"] >= 0.0, "s_ape"].mean()
    mape_ignore_missing = errors.loc[errors["ape"] >= 0.0, "ape"].mean()
    abs_errors = abs(errors["error"])
    mae = abs_errors.mean()
    rmse = (errors.error ** 2).mean() ** .5

    with summary_file.open("a+") as errors_file:
        errors_file.write(f"{run_id},{mape},{mape_ignore_missing},{smape},{smape_ignore_missing},{mae},{rmse}\n")
    # csv_file = error_file.with_suffix(".csv")
    # errors.drop(["errors", "fine_data"], axis=1).to_csv(csv_file)


def write_error_headers(file_path: Path) -> None:
    with file_path.open("w") as file:
        file.write("run_id,mape,mape_ignore_missing,smape,smape_ignore_missing,mae,rmse\n")

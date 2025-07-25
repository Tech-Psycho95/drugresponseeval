#!/usr/bin/env python

# Written by Judith Bernett and released under the MIT License.

import argparse
import pandas as pd
import pathlib

from drevalpy.visualization.utils import prep_results, write_results


def get_parser():
    parser = argparse.ArgumentParser(description="Collect results and write to single files.")
    parser.add_argument("--outfiles", type=str, nargs="+", required=True, help="Output files.")
    parser.add_argument("--path_data", type=str, default="data", help="Data directory path")
    return parser


def parse_results(outfiles):
    # get all files with the pattern f'{model_name}_evaluation_results.csv' from outfiles
    result_files = [file for file in outfiles if "evaluation_results.csv" in file]
    # get all files with the pattern f'{model_name}_evaluation_results_per_drug.csv' from outfiles
    result_per_drug_files = [file for file in outfiles if "evaluation_results_per_drug.csv" in file]
    # get all files with the pattern f'{model_name}_evaluation_results_per_cl.csv' from outfiles
    result_per_cl_files = [file for file in outfiles if "evaluation_results_per_cl.csv" in file]
    # get all files with the pattern f'{model_name}_true_vs_pred.csv' from outfiles
    t_vs_pred_files = [file for file in outfiles if "true_vs_pred.csv" in file]
    return result_files, result_per_drug_files, result_per_cl_files, t_vs_pred_files


def collapse_file(files):
    out_df = None
    for file in files:
        if out_df is None:
            out_df = pd.read_csv(file, index_col=0)
        else:
            out_df = pd.concat([out_df, pd.read_csv(file, index_col=0)])
    if out_df is not None and "drug" in out_df.columns:
        out_df["drug"] = out_df["drug"].astype(str)
    return out_df


if __name__ == "__main__":
    args = get_parser().parse_args()
    # parse the results from outfiles.outfiles
    outfiles = args.outfiles
    path_data = pathlib.Path(args.path_data)
    eval_result_files, eval_result_per_drug_files, eval_result_per_cl_files, true_vs_pred_files = parse_results(outfiles)

    # collapse the results into single dataframes
    eval_results = collapse_file(eval_result_files)
    eval_results_per_drug = collapse_file(eval_result_per_drug_files)
    eval_results_per_cell_line = collapse_file(eval_result_per_cl_files)
    t_vs_p = collapse_file(true_vs_pred_files)

    # prepare the results through introducing new columns algorithm, rand_setting, LPO_LCO_LDO, split, CV_split
    eval_results, eval_results_per_drug, eval_results_per_cell_line, t_vs_p = prep_results(
        eval_results=eval_results,
        eval_results_per_drug=eval_results_per_drug,
        eval_results_per_cell_line=eval_results_per_cell_line,
        t_vs_p=t_vs_p,
        path_data=path_data
    )

    # save the results to csv files
    write_results(
        path_out="",
        eval_results=eval_results,
        eval_results_per_drug=eval_results_per_drug,
        eval_results_per_cl=eval_results_per_cell_line,
        t_vs_p=t_vs_p,
    )

import pandas as pd
import numpy as np
from typing import List, Optional
import itertools
import functools
import operator
import pdb

def measure_fairness(
        dfs: dict[str, pd.DataFrame],
        funcs: List,
        metric_names: List[str] = ['rmse_weighted_l2'],
        attributes: List[str] = 'all',
        iterate_over: Optional[List[str]] = ['model', 'variable', 'lead_time']
    ) -> dict[str, pd.DataFrame]:
    '''
    Return a dict from attribute (str) -> dataframe, with a column for each metric
    '''
    # TODO: validate list nature of args
    if not type(funcs) == list:
        funcs = [funcs]
    if (type(metric_names) != list) and (type(metric_names) != str):
        raise ValueError(f'incorrect type for variable "metric_names", it must be list or str, given {type(metric_names)}')
    elif type(metric_names) == str:
        metric_names = [metric_names]
    if attributes == 'all':
        attributes = [k for k in dfs.keys() if k != 'baseline']
    elif not type(attributes) == list:
        raise ValueError(f'incorrect type for variable "attributes", it must be either "all" or a list')

    output = dict()

    for attribute in attributes:
        df = dfs[attribute]
        attr_output = []
        iter_cols = [k for k in iterate_over if k in df.columns]
        iter_combos = list(itertools.product(*[df[k].unique() for k in iter_cols]))
        for iter_vals in iter_combos:
            conditions = [(df[col] == val) for col, val in zip(iter_cols, iter_vals)]
            mask = functools.reduce(operator.and_, conditions)
            filtered_df = df[mask]
            specific_metrics_entry = {k: v for k, v in zip(iter_cols, iter_vals)}
            for metric in metric_names:
                for func in funcs:
                    specific_metrics_entry.update(func(filtered_df, metric))
            attr_output.append(specific_metrics_entry)
        output[attribute] = pd.DataFrame(attr_output)

    return output

def greatest_abs_diff(
        df: pd.DataFrame,
        metric: str
    ) -> dict:
    varmax = np.max(df[metric])
    varmin = np.min(df[metric])    
    return {f'gad_{metric}': varmax-varmin}

def variance(
        df: pd.DataFrame,
        metric: str
    ) -> dict:
    return {f'variance_{metric}': np.var(df[metric])}

def standard_deviation(
        df: pd.DataFrame,
        metric: str
    ) -> dict:
    return {f'std_{metric}': np.std(df[metric])}

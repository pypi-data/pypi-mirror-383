import plotly.express as px
import os
import pickle
import numpy as np
import pandas as pd
import geopandas as gpd
import safe_earth.metrics.fairness as fairness
from safe_earth.utils.stats import filter_outliers
import pdb

def fig2(df: pd.DataFrame, show: bool = True, save_path: str = 'outputs/viz/iclr/rmse_diff.pdf'):
    '''
    Plot Figure 2. Greatest Absolute Difference in RMSE fairness metric.
    '''
    fig_gad = px.line(
        df,
        x='lead_time',
        y='gad_rmse_weighted_l2',
        color='model',
        symbol='model',
        symbol_sequence=['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up'],
        facet_col='attribute',
        facet_col_spacing=0.04,
        facet_row='variable',
        facet_row_spacing=0.04,
        labels={
            'lead_time': 'lead time (hours)',
            'gad_rmse_weighted_l2': 'Greatest Absolute Difference in per-strata RMSE'
        }
    )
    fig_gad.for_each_trace(lambda t: t.update(name = newnames[t.name],
        legendgroup = newnames[t.name],
        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
        )
    )
    fig_gad.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
    fig_gad.update_xaxes(tickmode = 'array', tickvals = lead_times, showticklabels = True, tickangle=-90, tickfont_size=8, title_font_size=10)
    fig_gad.update_yaxes(matches=None, showticklabels=True)
    if show:
        fig_gad.show()
    fig_gad.write_image(save_path, width=1200, height=800, scale=4)

def fig3(df: pd.DataFrame, show: bool = True, save_path: str = 'outputs/viz/iclr/rmse_var.pdf'):
    '''
    Plot Figure 3. Variance of RMSE fairness metric.
    '''
    fig_var = px.line(
        df,
        x='lead_time',
        y='variance_rmse_weighted_l2',
        color='model',
        symbol='model',
        symbol_sequence=['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up'],
        facet_col='attribute',
        facet_col_spacing=0.04,
        facet_row='variable',
        facet_row_spacing=0.04,
        labels={
            'lead_time': 'lead time (hours)',
            'variance_rmse_weighted_l2': 'Variance in per-strata RMSE'
        }
    )
    fig_var.for_each_trace(lambda t: t.update(name = newnames[t.name],
        legendgroup = newnames[t.name],
        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
        )
    )
    fig_var.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
    fig_var.update_xaxes(tickmode = 'array', tickvals = lead_times, showticklabels = True, tickangle=-90, tickfont_size=8, title_font_size=10)
    fig_var.update_yaxes(matches=None, showticklabels=True)
    if show:
        fig_var.show()
    fig_var.write_image(save_path, width=1200, height=800, scale=4)

def fig4(df: pd.DataFrame, show: bool = True, save_path: str = 'outputs/viz/iclr/income_strata_plots.pdf'):
    '''
    Plot Figure 4. Analysis of the income attribute.
    '''
    # TODO: should this plot include baseline?
    df = df[df['attribute']=='income']
    fig = px.line(
        df,
        x='lead_time',
        y='rmse_weighted_l2',
        color='income',
        symbol='income',
        facet_col='model',
        facet_col_spacing=0.04,
        facet_row='variable',
        facet_row_spacing=0.04,
        labels={
            'lead_time': 'lead time (hours)',
            'rmse_weighted_l2': 'Per-strata RMSE'
        },
        category_orders={
            'income': ['High-income Countries', 'Upper-middle-income Countries', 'Lower-middle-income Countries', 'Low-income Countries', 'Baseline (all gridpoints)']
        }
    )
    fig.for_each_annotation(lambda a: a.update(text=newnames[a.text.split("=")[-1]] if a.text.split("=")[-1] in newnames else '('+a.text.split("=")[-1].capitalize()+')'))
    fig.update_xaxes(tickmode = 'array', tickvals = lead_times, showticklabels = True, tickangle=-90, tickfont_size=8, title_font_size=10)
    fig.update_yaxes(matches=None, showticklabels=True)

    yaxes = [ax for ax in fig.layout if ax.startswith("yaxis")]
    yaxes.sort(key=lambda s: int(s[5:]) if s != "yaxis" else 1)
    for i, yax in enumerate(yaxes):
        if i < 6:
            fig.layout[yax].update(range=[-25, 925])
        else:
            fig.layout[yax].update(range=[-.05, 4.55])
    xaxes = [ax for ax in fig.layout if ax.startswith("xaxis")]
    for xax in xaxes:
        fig.layout[xax].update(range=[-10, 250])

    if show:
        fig.show()
    fig.write_image(save_path, width=1600, height=800, scale=4)

# Figure 5
def fig5(df: pd.DataFrame, show: bool = True, save_path: str = 'outputs/viz/iclr/landcover_strata_plots.pdf'):
    '''
    Plot Figure 5. Analysis of the landcover attribute.
    '''
    # TODO: should this plot include baseline?
    df = df[df['attribute']=='landcover']
    fig = px.line(
        df,
        x='lead_time',
        y='rmse_weighted_l2',
        color='landcover',
        color_discrete_sequence=['green', 'blue'],
        symbol='landcover',
        facet_col='model',
        facet_col_spacing=0.04,
        facet_row='variable',
        facet_row_spacing=0.04,
        labels={
            'lead_time': 'lead time (hours)',
            'rmse_weighted_l2': 'Per-strata RMSE'
        }
    )
    fig.for_each_annotation(lambda a: a.update(text=newnames[a.text.split("=")[-1]] if a.text.split("=")[-1] in newnames else '('+a.text.split("=")[-1].capitalize()+')'))
    fig.update_xaxes(tickmode = 'array', tickvals = lead_times, showticklabels = True, tickangle=-90, tickfont_size=8, title_font_size=10)
    fig.update_yaxes(matches=None, showticklabels=True)

    yaxes = [ax for ax in fig.layout if ax.startswith("yaxis")]
    yaxes.sort(key=lambda s: int(s[5:]) if s != "yaxis" else 1)
    for i, yax in enumerate(yaxes):
        if i < 6:
            fig.layout[yax].update(range=[-25, 925])
        else:
            fig.layout[yax].update(range=[-.05, 4.05])
    xaxes = [ax for ax in fig.layout if ax.startswith("xaxis")]
    for xax in xaxes:
        fig.layout[xax].update(range=[-10, 250])

    if show:
        fig.show()
    fig.write_image(save_path, width=1600, height=800, scale=4)

# Figure 8
def fig8(df: pd.DataFrame, show: bool = True, save_path: str = 'outputs/viz/iclr/zoomed_income_strata_plots.pdf'):
    '''
    Plot Figure 8. Zoomed in analysis of the income attribute for the first 48 hours of lead time.
    '''
    # TODO: should this plot include baseline?
    df = df[df['attribute']=='income']
    fig = px.line(
        df,
        x='lead_time',
        y='rmse_weighted_l2',
        color='income',
        symbol='income',
        facet_col='model',
        facet_col_spacing=0.04,
        facet_row='variable',
        facet_row_spacing=0.04,
        labels={
            'lead_time': 'lead time (hours)',
            'rmse_weighted_l2': 'Per-strata RMSE'
        },
        category_orders={
            'income': ['High-income Countries', 'Upper-middle-income Countries', 'Lower-middle-income Countries', 'Low-income Countries', 'Baseline (all gridpoints)']
        }
    )
    fig.for_each_annotation(lambda a: a.update(text=newnames[a.text.split("=")[-1]] if a.text.split("=")[-1] in newnames else '('+a.text.split("=")[-1].capitalize()+')'))
    fig.update_xaxes(tickmode = 'array', tickvals = lead_times, showticklabels = True, tickangle=-90, tickfont_size=8, title_font_size=10)
    fig.update_yaxes(matches=None, showticklabels=True)

    yaxes = [ax for ax in fig.layout if ax.startswith("yaxis")]
    yaxes.sort(key=lambda s: int(s[5:]) if s != "yaxis" else 1)
    for i, yax in enumerate(yaxes):
        if i < 6:
            fig.layout[yax].update(range=[10, 150])
        else:
            fig.layout[yax].update(range=[.25, 1.25])
    xaxes = [ax for ax in fig.layout if ax.startswith("xaxis")]
    for xax in xaxes:
        fig.layout[xax].update(range=[-5, 50])

    if show:
        fig.show()
    fig.write_image(save_path, width=1600, height=800, scale=4)

if __name__ == '__main__':
    # define constants
    models = ['graphcast', 'keisler', 'pangu', 'sphericalcnn', 'fuxi', 'neuralgcm']
    newnames = {'graphcast':'GraphCast', 'keisler': 'Keisler (2022)', 'pangu': 'Pangu-Weather', 'sphericalcnn': 'Spherical CNN', 'fuxi': 'FuXi', 'neuralgcm': 'NeuralGCM'}
    lead_times = [x for x in range(12, 241, 12)]
    attributes = ['territory', 'subregion', 'income', 'landcover']

    # collate all model data into a unified dataframe
    iclr_data_path = 'outputs/results_iclr.pkl'
    if not os.path.exists(iclr_data_path):
        print('regathering data')
        iclr_data = pd.DataFrame()
        for attr in attributes:
            for model in models:
                with open(f'outputs/results_{model}_iclr.pkl', 'rb') as f:
                    model_dict = pickle.load(f)
                model_df = model_dict[attr]
                model_df['attribute'] = attr
                iclr_data = pd.concat([iclr_data, model_df], ignore_index=True)
        with open(iclr_data_path, 'wb') as f:
            pickle.dump(iclr_data, f)
    else:
        with open(iclr_data_path, 'rb') as f:
            iclr_data = pickle.load(f)

    # collate all error data
    error_data_path = 'outputs/results_iclr_error.pkl'
    if not os.path.exists(error_data_path):
        print('regathering error data')
        error_data = pd.DataFrame()
        for attr in attributes:
            for model in models:
                with open(f'outputs/results_{model}_errors.pkl', 'rb') as f:
                    model_dict = pickle.load(f)
                model_df = model_dict[attr]
                model_df['attribute'] = attr
                error_data = pd.concat([error_data, model_df], ignore_index=True)
        with open(error_data_path, 'wb') as f:
            pickle.dump(error_data, f)
    else:
        with open(error_data_path, 'rb') as f:
            error_data = pickle.load(f)

    # get outlier-excluded fairness metrics
    no_outliers = error_data.drop(error_data[error_data['attribute']=='landcover'].index)
    no_outliers = filter_outliers(no_outliers.copy())
    dfdict = {'territory': no_outliers[no_outliers['attribute']=='territory'], 'subregion': no_outliers[no_outliers['attribute']=='subregion'], 'income': no_outliers[no_outliers['attribute']=='income']}
    fairness_metrics = fairness.measure_fairness(dfdict, funcs=[fairness.greatest_abs_diff, fairness.variance])
    fairness_metrics['territory']['attribute'] = 'territory'
    fairness_metrics['subregion']['attribute'] = 'subregion'
    fairness_metrics['income']['attribute'] = 'income'
    no_outliers = pd.concat([fairness_metrics['territory'], fairness_metrics['subregion'], fairness_metrics['income']])

    # analysis pipeline
    fig2(iclr_data.copy())
    fig3(iclr_data.copy())
    fig4(error_data.copy())
    fig5(error_data.copy())
    fig2(no_outliers.copy(), save_path='outputs/viz/iclr/rmse_diff_no_outliers.pdf') # for fig 6, recreate fig 2 without outliers
    fig3(no_outliers.copy(), save_path='outputs/viz/iclr/rmse_var_no_outliers.pdf') # for fig 7, recreate fig 3 without outliers
    fig8(error_data.copy())

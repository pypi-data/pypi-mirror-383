import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import safe_earth
from safe_earth.data.climate.era5 import ERA5Var
import safe_earth.metrics.fairness as fairness
import pandas as pd
import numpy as np
import pickle
import time
import pdb
import platform

models = ['graphcast', 'keisler', 'pangu', 'sphericalcnn', 'fuxi', 'neuralgcm']
resolution = '240x121'
lead_times = [np.timedelta64(x, 'h') for x in range(12, 241, 12)]
variables = [ERA5Var('temperature', 850, 'T850'), ERA5Var('geopotential', 500, 'Z500')]
era5 = safe_earth.data.climate.era5.get_era5(resolution, variables=variables)

for model in models:
    print(f'===== ON MODEL: {model} =====', flush=True)

    print('about to load data', flush=True)

    preds = safe_earth.data.climate.wb2.get_wb2_preds(model, resolution, lead_times, variables=variables)

    print('about to run losses', flush=True)

    loss_gdf = safe_earth.metrics.losses.climate_weighted_l2(
        data=preds, 
        ground_truth=era5, 
        lon_dim='longitude', 
        lat_dim='latitude',
        lead_time_dim='prediction_timedelta'
    )

    print('about to run errors', flush=True)

    attributes = 'all'
    strata_metrics = safe_earth.metrics.errors.stratified_rmse(
        loss_gdf,
        loss_metrics=['weighted_l2'],
        attributes=attributes,
        added_cols={'model': model}
    )

    print('saving stratified errors', flush=True)

    with open(f'outputs/results_{model}_errors.pkl', 'wb') as f:
        pickle.dump(strata_metrics, f)

    print('moving onto fairness', flush=True)

    fairness_metrics = fairness.measure_fairness(strata_metrics, funcs=[fairness.greatest_abs_diff, fairness.variance])

    print('saving fairness results', flush=True)

    with open(f'outputs/results_{model}_iclr.pkl', 'wb') as f:
        pickle.dump(fairness_metrics, f)

print('completed successfully!', flush=True)

import os
import pickle
import numpy as np
import pandas as pd
import geopandas as gpd
import pdb

models = ['graphcast', 'keisler', 'pangu', 'sphericalcnn', 'fuxi', 'neuralgcm']
variables = ['T850', 'Z500']
lead_times = [x for x in range(12, 241, 12)]
attributes = ['territory', 'subregion', 'income', 'landcover']
metrics = ['gad_rmse_weighted_l2', 'variance_rmse_weighted_l2']

iclr_data_path = 'outputs/results_iclr.pkl'
if os.path.exists(iclr_data_path):
    with open(iclr_data_path, 'rb') as f:
        iclr_data = pickle.load(f)

output_latex = b''

for metric in metrics:
    for attr in attributes:
        output_latex += b'\n\n\\begin{table}[H]\n\t\\caption{' + \
            bytes(metric, 'utf8') + b' ' + bytes(attr, 'utf8') + \
            b'}\n\t\\label{' + \
            bytes(attr, 'utf8') + \
            b'-' + \
            bytes(metric, 'utf8') + \
            b'-benchmark}\n\t\\scriptsize\n\t\\centering' + \
            b'\n\t\\begin{tabular}{lllllllll}\n\t\t\\\\ \\toprule' + \
            b'\n\t\t& & \\multicolumn{6}{c}{Model} \\\\' + \
            b'\n\t\t\\cmidrule(r){3-8}\n\t\tVariable & Lead time (h) & ' + \
            b'GraphCast & Keisler & Pangu-Weather & Spherical CNN & ' + \
            b'FuXi & NeuralGCM \\\\\n\t\t\\midrule'
        for variable in variables:
            for lead_time in lead_times:
                table_entry = b'\t\t' + bytes(variable, 'utf8') + b' & ' + bytes(str(lead_time), 'utf8') + b'h'
                vals = []
                for model in models:
                    df = iclr_data[(iclr_data['variable']==variable) 
                        & (iclr_data['lead_time']==lead_time) 
                        & (iclr_data['model']==model)
                        & (iclr_data['attribute']==attr)
                    ] 
                    vals.append(df[metric].item()) # TODO: variance
                for val in vals:
                    if val == min(vals):
                        table_entry += b' & \\textbf{' + bytes('{0:.4f}'.format(val), 'utf8') + b'}'
                    else:
                        table_entry += b' & ' + bytes('{0:.4f}'.format(val), 'utf8')
                table_entry += b' \\\\'
                output_latex += b'\n' + table_entry
            if variable != variables[-1]: 
                output_latex += b'\n\t\t\\midrule'
        output_latex += b'\n\t\t\\bottomrule\n\t\\end{tabular}\n\\end{table}'  

with open('outputs/iclr_tables_latex.txt', 'wb') as f:
    f.write(output_latex)

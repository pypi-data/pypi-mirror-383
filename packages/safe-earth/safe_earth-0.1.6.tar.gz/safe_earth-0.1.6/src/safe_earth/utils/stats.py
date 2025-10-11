from sklearn.neighbors import LocalOutlierFactor as LOF
import numpy as np
import pandas as pd

def filter_outliers(df: pd.DataFrame, error_metric: str = 'rmse_weighted_l2') -> pd.DataFrame:
    for variable in df.variable.unique():
        for model in df.model.unique():
            for lt in df.lead_time.unique():
                for attribute in df.attribute.unique():
                    mask = (
                        (df['attribute'] == attribute) &
                        (df['variable'] == variable) &
                        (df['model'] == model) &
                        (df['lead_time'] == lt)
                    )
                    samples = df.loc[mask, error_metric].tolist()
                    n_neighbors = min(20, len(samples)-1) # this is default behavior in sklearn 1.7.2
                    estimator = LOF(n_neighbors=n_neighbors) # manually performing the min prevents a warning from displaying
                    outliers = (estimator.fit_predict(np.array(samples).reshape(-1, 1)) == -1)
                    df.drop(df.loc[mask][outliers].index, inplace=True)
    return df
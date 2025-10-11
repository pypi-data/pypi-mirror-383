from sklearn.neighbors import LocalOutlierFactor as LOF
import numpy as np

def filter_outliers(df: pd.DataFrame) -> pd.DataFrame:
    for variable in df.variable.unique():
        for model in df.model.unique():
            for lt in df.lead_time.unique():
                for attribute in df.attribute.unique():
                    mask = (
                        (error_data['attribute'] == attribute) &
                        (error_data['variable'] == variable) &
                        (error_data['model'] == model) &
                        (error_data['lead_time'] == lt)
                    )
                    rmses = df.loc[mask, 'rmse_weighted_l2'].tolist()
                    estimator = LOF()
                    outliers = (estimator.fit_predict(np.array(rmses).reshape(-1, 1)) == -1)
                    df.drop(df.loc[mask][outliers].index, inplace=True)
    return df
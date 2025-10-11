import geopandas as gpd
import pandas as pd
import numpy as np
from shapely import wkt
from typing import List
from safe_earth.utils.errors import *
from safe_earth.data.strata.generate_gdf import *
import pdb

def stratified_rmse(
        losses: gpd.GeoDataFrame,
        loss_metrics: List[str],
        attributes: List[str] = 'all',
        added_cols: dict[str, str] = None
    ) -> dict[str, pd.DataFrame]:
    '''
    Get the RMSE of each strata group across gridpoints (the unique geometries
    in losses) belonging to each group.

    Parameters
    ----------
    losses: gpd.GeoDataFrame
        Dataframe where each entry is a unique combination of gridpoint, varialbe,
        and any other coordinates (e.g., prediction_leadtime for climatic data).
    loss_metrics: List[str]
        The name of the columns in losses for which to calculate RMSE over.
    attributes: List[str]
        The list of strata types to calculate RMSE for. The RMSE for each group
        within the strata type will be calculated. Options:
            - 'all': will include everything
            - 'territory': territorial boundaries defined by pygeoboundaries from geoLab
            - 'subregion': UN-defined subregions for each territory plus Antarctica
            - 'income': World Bank income group classification of each territory, if available
    added_cols: dict[str, str]
        For each entry in the dictionary, a column with the key as the name will
        be added to the output dataframe with the constant value.

    Returns
    -------
    dict[str, pd.DataFrame]
        The string key will be the name of the stratum type (i.e., landcover,
        income, etc) and the dataframe will include the RMSE for each group
        within the stratum. The RMSE of every prediction will also be included
        in a dataframe with the key 'baseline'.
    '''
    output = {}

    # if need_to_download_gdf_file():
    #     path = generate_gdf_file()

    # TODO: should be able to remove this chunk by making path user definable, 
    # both here and in the generate_gdf.py funcs
    if os.path.exists(os.getcwd()+'/gdf_territory_region_income.csv'):
        path = os.getcwd()+'/gdf_territory_region_income.csv'
    elif os.path.exists('safe_earth/data/strata/gdf_territory_region_income.csv'):
        path = 'safe_earth/data/strata/gdf_territory_region_income.csv'
    elif os.path.exists(os.getcwd()+'src/safe_earth/data/strata/gdf_territory_region_income.csv'):
        path = os.getcwd()+'src/safe_earth/data/strata/gdf_territory_region_income.csv'
    elif os.path.exists('src/safe_earth/data/strata/gdf_territory_region_income.csv'):
        path = 'src/safe_earth/data/strata/gdf_territory_region_income.csv'
    else:
        try:
            path = generate_gdf_file()
            print(f'new strata file downloaded at {path}')
        except:
            raise OSError('Ill specified path for strata data')

    try:
        gdf = gpd.GeoDataFrame(gpd.read_file(path))
    except:
        raise OSError('Ill specified path for strata data')
    gdf['geometry'] = gdf['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(gdf, geometry=gdf['geometry'])
    gdf = gdf.set_geometry('geometry').set_crs(4326)

    baseline = rmse_wrapper(losses, losses.variable.unique(), losses.lead_time.unique(), loss_metrics, added_cols)
    # TODO: get rmse at each individual point
    output.update({'baseline': pd.DataFrame(baseline)})

    joined_gdf = gpd.sjoin(losses, gdf, how="left", predicate="intersects").reset_index(drop=True)

    if 'territory' in attributes or 'all' in attributes:
        df = []
        for territory in joined_gdf['shapeName'].unique():
            if not pd.isna(territory):
                trimmed_gdf = joined_gdf[joined_gdf.shapeName==territory]
                data = rmse_wrapper(trimmed_gdf, trimmed_gdf.variable.unique(), trimmed_gdf.lead_time.unique(), loss_metrics, added_cols)
                for d in data:
                    d['territory'] = territory
                df += data
        output.update({'territory': pd.DataFrame(df)})

    if 'subregion' in attributes or 'all' in attributes:
        df = []
        for subregion in joined_gdf['UNSDG-subregion'].unique():
            if not pd.isna(subregion):
                trimmed_gdf = joined_gdf[joined_gdf['UNSDG-subregion']==subregion]

                # gdf is based on territory, don't double count data twice within the same subregion
                trimmed_gdf = trimmed_gdf[~trimmed_gdf.duplicated(subset=['geometry', 'variable', 'lead_time', 'UNSDG-subregion'], keep='last')]
                
                data = rmse_wrapper(trimmed_gdf, trimmed_gdf.variable.unique(), trimmed_gdf.lead_time.unique(), loss_metrics, added_cols)
                for d in data:
                    d['subregion'] = subregion
                df += data
        output.update({'subregion': pd.DataFrame(df)})

    if 'income' in attributes or 'all' in attributes:
        df = []
        incomes = joined_gdf['worldBankIncomeGroup'].unique()
        incomes = [x for x in incomes if not x == 'No income group available']
        for income in incomes:
            if not pd.isna(income):
                trimmed_gdf = joined_gdf[joined_gdf['worldBankIncomeGroup']==income]

                # gdf is based on territory, don't double count data twice within the same income group
                trimmed_gdf = trimmed_gdf[~trimmed_gdf.duplicated(subset=['geometry', 'variable', 'lead_time', 'worldBankIncomeGroup'], keep='last')]
                
                data = rmse_wrapper(trimmed_gdf, trimmed_gdf.variable.unique(), trimmed_gdf.lead_time.unique(), loss_metrics, added_cols)
                for d in data:
                    d['income'] = income
                df += data
        output.update({'income': pd.DataFrame(df)})

    if 'landcover' in attributes or 'all' in attributes:
        land_gdf = joined_gdf[~pd.isna(joined_gdf.shapeName)]
        land_gdf = land_gdf[~land_gdf.duplicated(subset=['geometry', 'variable', 'lead_time'], keep='last')]
        land_data = rmse_wrapper(land_gdf, land_gdf.variable.unique(), land_gdf.lead_time.unique(), loss_metrics, added_cols)
        for d in land_data:
            d['landcover'] = 'land'
        water_gdf = joined_gdf[pd.isna(joined_gdf.shapeName)]
        water_gdf = water_gdf[~water_gdf.duplicated(subset=['geometry', 'variable', 'lead_time'], keep='last')]
        water_data = rmse_wrapper(water_gdf, water_gdf.variable.unique(), water_gdf.lead_time.unique(), loss_metrics, added_cols)
        for d in water_data:
            d['landcover'] = 'water'
        df = land_data+water_data
        output.update({'landcover': pd.DataFrame(df)})

    return output

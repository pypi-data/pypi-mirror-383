from datetime import date
import os
import tempfile
from typing import List, Tuple
import argopy
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import json
import xarray
from argopy import DataFetcher, ArgoIndex, ArgoNVSReferenceTables  
from .json_cache import load_cache, save_cache, md5_hash

from . import misc

def get_data(
        exv: str,
        variables: List[str],
        region: Tuple[float, float, float, float],
        time: Tuple[date, date],
        depth: Tuple[float, float],
        cache: bool = True         
    ) -> xarray.Dataset:
    """ 
    Fetches Argo data using the Argopy python package.
    """
    misc.log_print("Fetching data from Argo using Argopy")

    if not variables:
        misc.log_print("No variables")
        return None

    lon_east, lon_west, lat_north, lat_south = region
    depth_max, depth_min = depth
    date_min, date_max = time
    
    SELECTION = [
        lon_east, lon_west, lat_north, lat_south, 
        depth_min, depth_max,
        date_min, date_max
    ]
    
    # DD: adding exv for the query_hash computation to get diffrent cache files for different exv.
    SELECTION_extended = [ SELECTION, exv]
    print(SELECTION_extended)
    
    query_hash = md5_hash(json.dumps(SELECTION_extended));
    
    filename = f"ARGO_{date_min}-{date_max}_{depth_min}-{depth_max}m_{query_hash}.nc"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    
    misc.log_print(f"Temporary file path: {filepath}")
    
    if cache and os.path.exists(filepath):
        misc.log_print(f"Using cached file...")
        
        dataset = xarray.open_dataset(filepath)
        
        return dataset
    
    else:
        misc.log_print(f"Downloading data...")
    
        try:
            
            # DD: adding these few lines to handle parameter list and the type of dataset to query.
            accepted_params = accepted_params=np.concatenate((argopy.utils.list_bgc_s_variables(),argopy.utils.list_core_parameters()))
            
            variables=list(set(variables).intersection(set(accepted_params)))
            if exv in ["EXV017","EXV018","EXV019","EXV020"]:
                dstype='phy'
            else:
                if exv in ["EXV028","EXV029","EXV030","EXV033"]:
                    dstype='bgc'
                else:
                    misc.log_print("This essential variable (EXV) is not included within Argo data")
            
            # DD: switching back the mode to 'standard', i.e. only good values be they from real time or delayed mode processing.
            # N.B. using QC means we add an homogeneisation layer among the Research infrostructure. Some work has already been
            # performed toward this direction by ODV for instance.
            f = DataFetcher(
                    ds=dstype, 
                    mode='standard', 
                    params=variables,
                    parallel=True, 
                    progress=True, 
                    cache=False,
                    chunks_maxsize={'time': 30},
            )
            
            f = f.region(SELECTION).load()
        
            df = f.to_xarray()
            
            # df[f"{exv}"] = df[variables].mean(axis=1)
            
            # Save to file
            df.to_netcdf(filepath)
            
            return df
        except Exception as e:
            misc.log_print("Something went wrong querying ARGO", e)
            
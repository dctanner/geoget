# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_era5.ipynb (unless otherwise specified).

__all__ = ['get_config', 'send_request', 'fwi_set', 'era5_get_year', 'era5land_get']

# Cell
import cdsapi
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
from .geo import RegionST
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from functools import partial
from pathlib import Path

# Cell
def get_config(region:RegionST, variables:list, year:int):
    months = region.times[region.times.year==year].strftime('%m').unique().values.tolist()
    days = region.times[region.times.year==year].strftime('%d').unique().values.tolist()
    times = region.times[region.times.year==year].strftime('%H:%M').unique().tolist()
    bbox = [region.bbox.top, region.bbox.left, region.bbox.bottom, region.bbox.right]
    config = {'format': 'netcdf', 'variable': variables, 'year': [str(year)],
              'month': months, 'day': days, 'time': times,
              'area': f'{"/".join([str(s) for s in bbox])}'} # North, West, South, East
    return config

def send_request(product:str, config:dict, filename:str):
    c = cdsapi.Client()
    print('Sending request')
    c.retrieve(product, config, filename)

def fwi_set():
    return ['10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
            '2m_temperature', 'surface_pressure', 'total_precipitation']

def era5_get_year(year, region, save_path, variables, product):
    config = get_config(region, variables, year)
    filename = save_path/f'{product}_{region.name}_{year}.nc'
    r = send_request(product, config, str(filename))

def era5land_get(region, save_path, variables=fwi_set(), product='reanalysis-era5-land',
                 max_workers=8):
    f = partial(era5_get_year, region=region, save_path=save_path, variables=variables,
                product=product)
    years = region.times.year.unique().values
    with ThreadPoolExecutor(max_workers) as e:
        list(tqdm(e.map(f, years), total=len(years)))
# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_download.ipynb (unless otherwise specified).

__all__ = ['Ladsweb']

# Cell
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from rasterio.coords import BoundingBox, disjoint_bounds
import numpy as np
import json
import requests
import warnings
import re
import os
from time import sleep
from fastprogress.fastprogress import progress_bar
from nbdev.imports import test_eq

# Cell
class Ladsweb():
    def __init__(self, product:str, collection:str, tstart:str, tend:str,
                 bbox:list, bands:list=None, coordsOrTiles:str="coords", daynight:str="DNB",
                 repName:str='GEO', repPixSize:float=0.01, repResample:str='bilinear',
                 doMosaic:str='False'):
        self.product, self.collection = product, collection
        self.tstart, self.tend, self.bbox, self.bands = tstart, tend, bbox, bands
        self.coordsOrTiles, self.daynight, self.repName = coordsOrTiles, daynight, repName
        self.repPixSize, self.repResample, self.doMosaic = repName, repPixSize, doMosaic

    def search_files(self):
        "Search for files for the product, region and time span given."
        url = (f"https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/" +
            f"searchForFiles?product={self.product}&collection={self.collection}&" +
            f"start={self.tstart}&stop={self.tend}&north={self.bbox[3]}&south={self.bbox[1]}" +
            f"&west={self.bbox[0]}&east={self.bbox[2]}&coordsOrTiles={self.coordsOrTiles}" +
            f"&dayNightBoth={self.daynight}")
        return ','.join(re.findall('<return>(.*?)</return>', requests.get(url).text))

    def send_order(self, ids=None, email=None):
        "Send order for a set of ids obtained with `search_files` method."
        if email is None: raise Exception("`email` is not defined")
        bands = ','.join([self.product + f'___{b}' for b in self.bands])
        url = (f"http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/" +
            f"orderFiles?fileIds={ids}" +
            f"&subsetDataLayer={bands}" +
            f"&geoSubsetNorth={self.bbox[3]}" +
            f"&geoSubsetSouth={self.bbox[1]}" +
            f"&geoSubsetEast={self.bbox[2]}" +
            f"&geoSubsetWest={self.bbox[0]}" +
            f"&reprojectionName={self.repName}" +
            f"&reprojectionOutputPixelSize={self.repPixSize}" +
            f"&reprojectionResampleType={self.repResample}" +
            f"&doMosaic={self.doMosaic}" +
            f"&email={email}")
        return re.findall('<return>(.*?)</return>', requests.get(url).text)[0]

    def order_status(self, orderId):
        url = (f"http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/" +
                f"getOrderStatus?orderId={orderId}")
        return re.findall('<return>(.*?)</return>', requests.get(url).text)[0]

    def download_files(self, orderId, path_save, auth=None):
        "Download files if the order is Available."
        if auth is None: raise Exception("`auth` code is not defined")
        status = order_status(orderId)
        if order_status(orderId) != 'Available':
            msg = f"Order is not Available, current status is {status}"
            warnings.warn(msg, UserWarning)
            return
        command = ('wget -e robots=off -m -np -R .html,.tmp -nH --cut-dirs=3 '
                + 'https://ladsweb.modaps.eosdis.nasa.gov/archive/orders/'
                + f'{orderId}/ --header "Authorization: Bearer {auth}" -P {path_save}')
        download = os.system(command)
        return True

    def release_order(self, orderId, email=None):
        if email is None: raise Exception("`email` is not defined")
        url = (f"http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/" +
        f"releaseOrder?orderId={orderId}&email={email}")
        status = re.findall('<return>(.*?)</return>', requests.get(url).text)[0]
        return status == '1'
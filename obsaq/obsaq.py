import requests
import os
import pyreadr
import pandas as pd
import numpy as np
import json
import importlib.resources as pkg_resources


def _errmsg(msg):
    print('Error: ' + msg)
    
def _warnmsg(msg):
    """_summary_

    Args:
        msg (_type_): _description_
    """
    print('Warning: ' + msg)
    
class meta: 
    def __init__(self):
        with pkg_resources.open_text('obsaq', 'config.py') as file:
            self.source = json.load(file)
     
    def get_metadata(self, port):
        # Check the `port` is in the dictionary
        if port not in self.source:
            _errmsg("Invalid port. Must be one of " + str(self.source.keys()) + ". If you want get the metadata of all ports, please use `meta.get_metadata_Rdata`")
            exit()
        
        # Download the file
        url = self.source[port]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            basename = url.split('/')[-1]
            with open(basename, 'wb') as f:
                f.write(r.content)
        else:
            _errmsg("Unable to download file. Status code: " + str(r.status_code) + '. URL: ' + url)
            exit()
        
        # Load the file
        df = pyreadr.read_r(basename)
        os.remove(basename)
        if port == 'aurn':
            key = 'AURN_metadata'
        elif port == 'saqn':
            key = 'meta'
        elif port == 'aqe':
            key = 'metadata'
        elif port == 'waqn':
            key = 'metadata'
        elif port == 'ni':
            key = 'metadata'
        site_table = pd.DataFrame(df[key])
        self.sites = site_table
        return self.sites

    def get_metadata_RData(self):
        dfs = []
        for _ in self.source.keys():
            _df = self.get_metadata(_)
            dfs.append(_df)
        site_table = pd.concat(dfs)
        self.sites = site_table
        return self.sites
    
    def get_site(self, bounds=None, point=None, site_id=None):
        """_summary_

        Args:
            port (str): _description_
            bounds (list, optional): _description_. Defaults to [lon_min, lon_max, lat_min, lat_max].
            point (list, optional): _description_. Defaults to [lon, lat].

        Returns:
            _type_: _description_
        """
        # Get the metadata
        meta = self.sites
        
        if point is None and bounds is None and site_id is None:
            _errmsg("Must specify either `bounds`, `point`, or `site_id`")
            exit()
        
        if site_id is not None:
            print('Site is selected by site_id: ' + str(site_id))
            filtered_sites = meta[meta['site_id'] == site_id]
            self.final_sites = filtered_sites
            return self.final_sites
        else:
            if bounds is not None and point is None:
                print('Site is selected by bounds: ' + str(bounds))
                lon_min = bounds[0]
                lon_max = bounds[1]
                lat_min = bounds[2]
                lat_max = bounds[3]
                data_bounds = {'lon_min': lon_min, 'lon_max': lon_max, 'lat_min': lat_min, 'lat_max': lat_max}
                lon_min = data_bounds['lon_min']
                lon_max = data_bounds['lon_max']
                lat_min = data_bounds['lat_min']
                lat_max = data_bounds['lat_max']
                
                # Filter the data to include only sites within the specified bounds
                filtered_sites = meta[
                    (meta['longitude'] >= lon_min) &
                    (meta['longitude'] <= lon_max) &
                    (meta['latitude'] >= lat_min) &
                    (meta['latitude'] <= lat_max)
                ]
                self.final_sites = filtered_sites
                return self.final_sites
            if point is not None and bounds is None:
                print('Site is selected by point: ' + str(point))
                # Find the nearest point in meta.
                point_x = point[0]
                point_y = point[1]
                distances = np.sqrt((meta['longitude'] - point_x)**2 + (meta['latitude'] - point_y)**2)
                nearest_index = distances.argmin()
                nearest_site = meta.iloc[nearest_index]
                self.final_sites = nearest_site
                return self.final_sites
            
    def download_sites(self, port, year=1995, output_dir='data/prep_obs_data', log=False):
        
        os.makedirs(output_dir, exist_ok=True)
        
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        try:
            ids = np.unique(self.final_sites['site_id'].values)
        except AttributeError:
            ids = [self.final_sites['site_id']]
        
        for id in ids:
            if port == 'aurn':
                url = f'https://uk-air.defra.gov.uk/data_files/site_data/{id}_{year}.csv'
                # Download this file.
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    filename = url.split('/')[-1]
                    with open(f'{output_dir}/{filename}', 'wb') as f:
                        f.write(r.content)
                    print('Data has downloaded successfully. URL: ' + url)
                else:
                    if log:
                        _warnmsg(" !!!-- Unable to download file. URL: " + url)
                    else:
                        pass
            elif port == 'RData':
                url = f"https://uk-air.defra.gov.uk/openair/R_data/{id}_{year}.RData"
                # Download this file.
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    filename = url.split('/')[-1]
                    with open(f'{output_dir}/{filename}', 'wb') as f:
                        f.write(r.content)
                    print('Data has downloaded successfully. URL: ' + url)
                else:
                    if log:
                        _warnmsg(" !!!-- Unable to download file. URL: " + url)
                        continue
                    else:
                        continue
                _file = pyreadr.read_r(f'{output_dir}/{filename}')
                for _key in _file.keys():
                    _df = pd.DataFrame(_file[_key])
                    _df.to_csv(f'{output_dir}/{_key}.csv', index=False)
                os.remove(f'{output_dir}/{filename}')
            else:
                _errmsg("Invalid port. Must be one of 'aurn' or 'RData'")
                exit()
                
                
def read_sites(site_id, port, year=1995):  
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    os.makedirs('.temp', exist_ok=True)
    if port == 'aurn':
        url = f'https://uk-air.defra.gov.uk/data_files/site_data/{site_id}_{year}.csv'
        # Read this file.
        result = pd.read_csv(url, skiprows=4)
    elif port == 'RData':
        url = f"https://uk-air.defra.gov.uk/openair/R_data/{site_id}_{year}.RData"
        # Download this file.
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            filename = url.split('/')[-1]
            with open(f'.temp/{filename}', 'wb') as f:
                f.write(r.content)
            # print('Data has downloaded successfully. URL: ' + url)
        else:
            _warnmsg(" !!!-- Unable to check file. URL: " + url)
            return
            
        _file = pyreadr.read_r(f'.temp/{filename}')
        # print(f'.temp/{filename}')
        for _key in _file.keys():
            _df = pd.DataFrame(_file[_key])
            _df.to_csv(f'.temp/{_key}.csv', index=False)
    else:
        _errmsg("Invalid port. Must be one of 'aurn' or 'RData'")
        exit()
    return _df
                


    
            
            
          


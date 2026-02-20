
import requests
import os
import pyreadr
import pandas as pd
import numpy as np
import json
import importlib
import importlib.resources as pkg_resources
from io import StringIO
import re
from typing import Optional
from pandas.errors import DtypeWarning
warnings.simplefilter("ignore", DtypeWarning)

def _errmsg(msg):
    print('Error: ' + msg)

def _warnmsg(msg):
    print('Warning: ' + msg)


class meta:
    def __init__(self):
        with pkg_resources.open_text('obsaq', 'config.py') as file:
            self.source = json.load(file)

    def _dedupe_same_name_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        cols = list(df.columns)
        if len(cols) == len(set(cols)):
            return df  

        new_parts = []
        seen = set()
        for c in cols:
            if c in seen:
                continue
            seen.add(c)

            idxs = [i for i, cc in enumerate(cols) if cc == c]
            if len(idxs) == 1:
                new_parts.append(df.iloc[:, idxs[0]])
            else:
                block = df.iloc[:, idxs]
                merged = block.bfill(axis=1).iloc[:, 0]
                merged.name = c
                new_parts.append(merged)

        out = pd.concat(new_parts, axis=1)

        out = out.infer_objects(copy=False)
        return out

    def get_metadata(self, port):
        if port not in self.source:
            _errmsg("Invalid port. Must be one of " + str(self.source.keys()) +
                    ". If you want get the metadata of all ports, please use `meta.get_metadata_RData`")
            raise ValueError("Invalid port")

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
            raise RuntimeError("Download failed")

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
        else:
            key = list(df.keys())[0]

        site_table = pd.DataFrame(df[key])
        self.sites = site_table
        return self.sites

    def get_metadata_RData(self):
        dfs = []
        for _ in self.source.keys():
            _df = self.get_metadata(_)
            dfs.append(_df)
        site_table = pd.concat(dfs, ignore_index=True)
        self.sites = site_table
        return self.sites
    

    def get_site(self, bounds=None, point=None, site_id=None):
        meta_df = self.sites

        if point is None and bounds is None and site_id is None:
            _errmsg("Must specify either `bounds`, `point`, or `site_id`")
            raise ValueError("No site selector")

        if site_id is not None:
            print('Site is selected by site_id: ' + str(site_id))
            filtered_sites = meta_df[meta_df['site_id'] == site_id]
            self.final_sites = filtered_sites
            return self.final_sites

        if bounds is not None and point is None:
            print('Site is selected by bounds: ' + str(bounds))
            lon_min, lon_max, lat_min, lat_max = bounds

            filtered_sites = meta_df[
                (meta_df['longitude'] >= lon_min) &
                (meta_df['longitude'] <= lon_max) &
                (meta_df['latitude'] >= lat_min) &
                (meta_df['latitude'] <= lat_max)
            ]
            self.final_sites = filtered_sites
            return self.final_sites

        if point is not None and bounds is None:
            print('Site is selected by point: ' + str(point))
            point_x, point_y = point
            distances = np.sqrt((meta_df['longitude'] - point_x) ** 2 + (meta_df['latitude'] - point_y) ** 2)
            nearest_index = distances.argmin()
            nearest_site = meta_df.iloc[[nearest_index]]
            self.final_sites = nearest_site
            return self.final_sites

        return None

    def _filter_sites_by_date(self, meta: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
        """
        Station-level temporal filter:
        keep stations that overlap with [start, end]
        """

        if start is None and end is None:
            return meta

        start_ts = pd.to_datetime(start, errors="raise") if start is not None else None
        end_ts   = pd.to_datetime(end,   errors="raise") if end   is not None else None

        start_date = pd.to_datetime(meta["start_date"], errors="raise")

        # today = pd.Timestamp.today().normalize()
        # end_date = meta["end_date"].replace("ongoing", today)

        # end_date = pd.to_datetime(meta["end_date"].replace("ongoing", pd.NaT),errors="raise")
        # today = pd.Timestamp.today().normalize()
        # end_date = end_date.fillna(today)

        today = pd.Timestamp.today().normalize().strftime("%Y-%m-%d")
        end_date = meta["end_date"].replace("ongoing", today)
        end_date = pd.to_datetime(end_date, errors="raise")

        condition = pd.Series(True, index=meta.index)

        if end_ts is not None:
            condition &= (start_date <= end_ts)

        if start_ts is not None:
            condition &= (end_date >= start_ts)

        return meta.loc[condition].copy()

    def _filter_sites_by_pollutants(self, meta: pd.DataFrame, pollutant=None) -> pd.DataFrame:

        if pollutant is None:
            return meta
        if isinstance(pollutant, str):
            pollutants = [pollutant]
        else:
            pollutants = list(pollutant)

        mask = meta["parameter"].isin(pollutants)

        return meta.loc[mask].copy()

       
    def _parse_datetime(self, df: pd.DataFrame) -> pd.Series:
        if ("Date" in df.columns) and ("time" in df.columns):

            date_str = df["Date"].astype(str).str.strip()
            time_str = df["time"].astype(str).str.strip()

            is_24 = time_str.isin(["24:00", "24:00:00"])

            time_str = time_str.replace({"24:00": "00:00", "24:00:00": "00:00"})

            dt = pd.to_datetime(
                date_str + " " + time_str,
                errors="raise",
                dayfirst=True
            )

            dt.loc[is_24] = dt.loc[is_24] + pd.Timedelta(days=1)

            return dt

        for c in ["date", "Date", "datetime", "DateTime", "time"]:
            if c in df.columns:
                dt = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
                return dt

        return pd.to_datetime(pd.Series([pd.NaT] * len(df)), errors="coerce")
    
    def _filter_time(self, df: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
        if start is None and end is None:
            return df

        dt = self._parse_datetime(df)
        mask = pd.Series(True, index=df.index)

        if start is not None:
            start_ts = pd.to_datetime(start, errors="raise")
            mask &= (dt >= start_ts)

        if end is not None:
            end_ts = pd.to_datetime(end, errors="raise") + pd.Timedelta(days=1)
            mask &= (dt < end_ts)

        return df.loc[mask].copy()

    def _parameter_to_name(self, parameter: str) -> Optional[str]:
        if parameter is None:
            return None

        p = str(parameter).strip()
        if p.lower() == "all":
            return None

        if "parameter" not in self.sites.columns or "Parameter_name" not in self.sites.columns:
            _warnmsg("Metadata is missing required column(s) 'parameter' or 'Parameter_name'; cannot perform parameter-to-name mapping.")
            return None
        
        cand = self.sites.loc[self.sites["parameter"] == p, "Parameter_name"].dropna().astype(str).unique().tolist()
        if len(cand) == 0:
            _warnmsg(f"No matching 'Parameter_name' found in metadata for parameter={p}.")
            return None

        hourly = [x for x in cand if "hourly" in x.lower()]
        if len(hourly) > 0:
            return hourly[0]

        if len(cand) > 1:
            _warnmsg(f"Ambiguous mapping for parameter={p}: multiple 'Parameter_name' entries found. No 'Hourly' variant identified; using the first candidate: {cand[0]}.")

        return cand[0]

    
    def _match_column_by_parameter(self, df: pd.DataFrame, parameter: str) -> Optional[str]:
        if parameter is None:
            return None
        p = str(parameter).strip()
        if p.lower() == "all":
            return None

        def _norm(s: str) -> str:
            s = str(s).lower().strip() 
            s = re.sub(r"<\s*sub\s*>", "", s)
            s = re.sub(r"<\s*/\s*sub\s*>", "", s)
            s = re.sub(r"\s+", "", s)
            s = s.replace(".", "")
            s = s.replace("_", "").replace("-", "")
            return s

        target = _norm(p)

        for c in df.columns:
            if _norm(c) == target:
                return c
        for c in df.columns:
            if target in _norm(c):
                return c
        return None

    def _select_pollutant_columns_aurn(self, df: pd.DataFrame, pollutant="all") -> pd.DataFrame:
        if pollutant is None or str(pollutant).strip().lower() == "all":
            return df

        target_name = self._parameter_to_name(str(pollutant))
        if target_name is None:
            _warnmsg(f"No metadata mapping found for parameter={pollutant}; returning an empty DataFrame.")
            return df.iloc[0:0].copy()

        def _norm(s: str) -> str:
            s = str(s).lower().strip()
            s = re.sub(r"<\s*sub\s*>", "", s)
            s = re.sub(r"<\s*/\s*sub\s*>", "", s)
            s = s.replace("&nbsp;", "")
            s = re.sub(r"\s+", "", s)
            return s

        target_norm = _norm(target_name)

        matched = None
        for c in df.columns:
            if _norm(c) == target_norm:
                matched = c
                break
        if matched is None:
            for c in df.columns:
                if target_norm in _norm(c):
                    matched = c
                    break

        if matched is None:
            return df.iloc[0:0].copy()

        keep = []
        for c in ["Date", "time"]:
            if c in df.columns:
                keep.append(c)

        keep.append(matched)

        idx = list(df.columns).index(matched)
        for j in [idx + 1, idx + 2]:
            if j < len(df.columns):
                col = df.columns[j]
                if str(col).startswith("status") or str(col).startswith("unit"):
                    keep.append(col)

        keep = list(dict.fromkeys(keep))
        return df[keep]

    def download_sites(
        self,
        port,
        year=None,
        output_dir='data/prep_obs_data',
        log=False,
        pollutant="all",
        start=None,
        end=None,
        download_mode: str = "stream",
        save_per_site: bool = True,
        save_merged: bool = False,
        merged_filename: Optional[str] = None,
        add_site_id: bool = True
    ):

        os.makedirs(output_dir, exist_ok=True)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # n_sites_before = self.final_sites["site_id"].nunique()
        # print(f"Before filtering = {n_sites_before}", flush=True)

        self.final_sites = self._filter_sites_by_date(self.final_sites, start=start, end=end)
        print(self.final_sites)
        # n_sites = self.final_sites["site_id"].nunique()
        # print(f"After filter_sites_by_date: {n_sites} sites found.")

        # print("DEBUG type(final_sites):", type(self.final_sites))
        # # 如果它是 DataFrame，会有 columns / shape
        # if hasattr(self.final_sites, "shape"):
        #     print("DEBUG shape(final_sites):", self.final_sites.shape)
        # if hasattr(self.final_sites, "columns"):
        #     print("DEBUG columns(final_sites):", list(self.final_sites.columns)[:20])
        # # 如果它是 Series，看看它的 index
        # if hasattr(self.final_sites, "index") and not hasattr(self.final_sites, "columns"):
        #     print("DEBUG series index:", list(self.final_sites.index)[:20])


        self.final_sites = self._filter_sites_by_pollutants(
        self.final_sites,
        pollutant=pollutant
        )
        # n_sites = self.final_sites["site_id"].nunique()
        # print(f"After filter_sites_by_poll: {n_sites} sites found.")

        try:
            ids = np.unique(self.final_sites['site_id'].values)
        except AttributeError:
            ids = [self.final_sites['site_id']]

        if (start is not None) and (end is not None):
            y0 = pd.to_datetime(start).year
            y1 = pd.to_datetime(end).year
            years = list(range(y0, y1 + 1))
        elif year is not None:
            years = [int(year)]
        else:
            _errmsg("Provide either 'year' or both 'start' and 'end'.")
            raise ValueError("No year range")

        merged_list = []
        if merged_filename is None and save_merged:
            safe_pol = str(pollutant).replace(" ", "_").replace("/", "_")
            if start is not None or end is not None:
                merged_filename = f"MERGED_{port}_{safe_pol}_{str(start).replace('-','')}_{str(end).replace('-','')}.csv"
            else:
                merged_filename = f"MERGED_{port}_{safe_pol}_{years[0]}_{years[-1]}.csv"

        for sid in ids:

            if port == 'aurn':
                url_prefix = 'https://uk-air.defra.gov.uk/datastore/data_files/site_data'
                all_year_dfs = []

                for y in years:
                    url = f'{url_prefix}/{sid}_{y}.csv'
                    r = requests.get(url, headers=headers)

                    if r.status_code != 200:
                        if log:
                            _warnmsg(" !!!-- Unable to download file. URL: " + url)
                        continue

                    try:
                        df = pd.read_csv(StringIO(r.text), skiprows=4)
                    except Exception as e:
                        _warnmsg(f"Failed to read {sid}_{y}.csv: {e}")

                        continue

                    df = self._filter_time(df, start=start, end=end)
                    df = self._select_pollutant_columns_aurn(df, pollutant=pollutant)

                    df = self._dedupe_same_name_columns(df)

                    if not df.empty:
                        if add_site_id and "site_id" not in df.columns:
                            df.insert(0, "site_id", sid)
                        all_year_dfs.append(df)

                if len(all_year_dfs) == 0:
                    if log:
                        _warnmsg(f"{sid} | No data after merging multiple years; skipping.")

                    continue

                out_df = pd.concat(all_year_dfs, ignore_index=True)

                out_df = self._dedupe_same_name_columns(out_df)

                if save_per_site:
                    safe_pol = str(pollutant).replace(" ", "_").replace("/", "_")
                    tag = f"{sid}_{safe_pol}"
                    if start is not None or end is not None:
                        tag += f"_{str(start).replace('-', '')}_{str(end).replace('-', '')}"
                    else:
                        tag += f"_{years[0]}_{years[-1]}"
                    out_path = f"{output_dir}/{tag}.csv"
                    out_df.to_csv(out_path, index=False)
                    print('Saved per-site file: ' + out_path)

                if save_merged:
                    merged_list.append(out_df)

            elif port == 'RData':
                base = "https://uk-air.defra.gov.uk/openair/R_data"
                key_dfs = {}

                for y in years:
                    url = f"{base}/{sid}_{y}.RData"
                    r = requests.get(url, headers=headers)

                    if r.status_code != 200:
                        if log:
                            _warnmsg(" !!!-- Unable to download file. URL: " + url)
                        continue

                    filename = url.split('/')[-1]
                    local_path = f'{output_dir}/{filename}'
                    with open(local_path, 'wb') as f:
                        f.write(r.content)

                    try:
                        _file = pyreadr.read_r(local_path)
                    except Exception as e:
                        _warnmsg(f"Error parsing RData file '{filename}' with pyreadr: {e}")
                        os.remove(local_path)
                        continue

                    for _key in _file.keys():
                        _df = pd.DataFrame(_file[_key])

                        _df = self._filter_time(_df, start=start, end=end)

                        if pollutant is not None and str(pollutant).lower() != "all":
                            matched_col = self._match_column_by_parameter(_df, pollutant)
                            if matched_col is None:
                                continue
                            keep_cols = [c for c in ["date", "Date", "DateTime", "datetime", "time"] if c in _df.columns]
                            keep_cols.append(matched_col)
                            _df = _df[list(dict.fromkeys(keep_cols))]

                        _df = self._dedupe_same_name_columns(_df)

                        if not _df.empty:
                            if add_site_id and "site_id" not in _df.columns:
                                _df.insert(0, "site_id", sid)
                            key_dfs.setdefault(_key, []).append(_df)

                    os.remove(local_path)

                if len(key_dfs) == 0:
                    if log:
                        _warnmsg(f"{sid} | Empty dataset after multi-year RData merge; skipping.")
                        
                    continue

                safe_pol = str(pollutant).replace(" ", "_").replace("/", "_")

                for _key, dfs_list in key_dfs.items():
                    out_df = pd.concat(dfs_list, ignore_index=True)

                    out_df = self._dedupe_same_name_columns(out_df)

                    if save_per_site:
                        tag = f"{sid}_{_key}_{safe_pol}"
                        if start is not None or end is not None:
                            tag += f"_{str(start).replace('-', '')}_{str(end).replace('-', '')}"
                        else:
                            tag += f"_{years[0]}_{years[-1]}"
                        out_path = f"{output_dir}/{tag}.csv"
                        out_df.to_csv(out_path, index=False)
                        print('Saved per-site file: ' + out_path)

                    if save_merged:
                        merged_list.append(out_df)

            else:
                _errmsg("Invalid port. Must be one of 'aurn' or 'RData'")
                raise ValueError("Invalid port")

        if save_merged:
            if len(merged_list) == 0:
                _warnmsg("No data found for any site within the specified time range.")
                return None
            
            merged_df = pd.concat(merged_list, ignore_index=True)

            merged_df = self._dedupe_same_name_columns(merged_df)

            merged_path = os.path.join(output_dir, merged_filename)
            merged_df.to_csv(merged_path, index=False)
            print("Saved merged file: " + merged_path)
            return merged_df

        return None

def read_sites(site_id, port, year=1995):  
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    os.makedirs('.temp', exist_ok=True)
    if port == 'aurn':
        url = f'https://uk-air.defra.gov.uk/datastore/data_files/site_data/{site_id}_{year}.csv'
        # Read this file.
        df = pd.read_csv(url, skiprows=4)
        return df
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
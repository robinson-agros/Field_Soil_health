import json
import datetime
from dateutil.relativedelta import relativedelta
from sentinelhub.config import SHConfig
from shapely.geometry import shape
import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
import pandas as pd
import scipy.stats as st
from sentinelhub import CRS, Geometry, FisRequest, SHConfig

class Index:
    def __init__(self):
        self.INSTANCE_ID = 'cc37e3d2-1540-49cd-a137-4598dbad9dd1' #Esto debería ser un environment var.
        self.path = "Parcelas_Test.geojson" #Path donde están los archivos. 

    def raw_sat_data_extractor(self, GEOJSON, last_date = datetime.date.today(), months = 60):
        """Makes a query to Satellite Servers asking for NDVI basic information in the last X months since Y date. 

        GEOJSON: Field in Shapely POLYGON format. 
        last_date = datetime object of the target date for analysis. 
        months = number of months to look for in the analysis
        """
        first_date = last_date + relativedelta(months=-months)
        ts = ("{}-{}-{}".format(first_date.year, first_date.month, first_date.day),"{}-{}-{}".format(last_date.year, last_date.month, last_date.day))    
        poly = Geometry(GEOJSON, crs = CRS.WGS84)
        bbox = poly.bbox
        config = SHConfig()
        config.instance_id = self.INSTANCE_ID
        fis_request = FisRequest(layer='NDRI',
                                geometry_list=[poly],
                                time=ts,
                                maxcc = 0.05,
                                resolution='10m',
                                config=config)
        return fis_request.get_data()

    def fis_data_to_dataframe(self, fis_data):
        """ Creates a DataFrame from list of FIS responses
        """
        COLUMNS = ['channel', 'date', 'min', 'max', 'mean', 'stDev']
        data = []

        for fis_response in fis_data:
            for channel, channel_stats in fis_response.items():
                for stat in channel_stats:
                    #row = [int(channel[1:]), iso_to_datetime(stat['date'])]
                    row = [int(channel[1:]), parser.parse(stat['date'])]
                    for column in COLUMNS[2:]:
                        row.append(stat['basicStats'][column])
                    data.append(row)

        return pd.DataFrame(data, columns=COLUMNS).sort_values(['channel', 'date'])

    def health_DF_generator(self, fis_data, low_threshold, high_threshold):
        """
        Creates a DataFrame with Health and NDVI Index using low and high trheshold specified.
        fis_data: Data_Frame in the fis_to_dataframe format. 

        low_threshold: NDVI low threshold (below this threshold crops is not considered healthy)
        high_threshold: NDVI up threshold (up this threshold crop is considered weed) 
        """
        
        temp_df = fis_data[fis_data["channel"]==1]
        temp_df["date"] = pd.to_datetime(fis_data["date"],format="%Y-%m-%d")
        temp_df = temp_df.set_index("date")
        temp = temp_df.resample("2m").mean()
        #temp = temp_df.groupby(custom_dates[custom_dates.searchsorted(temp_df.index)]).mean()
        df_2m=temp.interpolate(method = 'linear').bfill().ffill()
        
        variability = ((df_2m['mean']/df_2m['stDev'])/4)*100
        z = (low_threshold - df_2m['mean'])/df_2m['stDev']
        z2 = (high_threshold - df_2m['mean'])/df_2m['stDev']
        noCrop = z.apply(lambda x: st.norm.cdf(x)*100)
        tooCrop = (1-z2.apply(lambda x: st.norm.cdf(x)))*100
        healthy = 100-noCrop-tooCrop
        risk = 100 - healthy
        df_2mH = pd.concat([df_2m["channel"],healthy,risk],axis=1)
        df_2mH = df_2mH.rename(columns={0:'Vigor Alto', 1:'Vigor Bajo'})
        return [df_2m, df_2mH]
    
    def index_generator(self, NDVI, health):
        """ Generates INDEX based on NDVI and health DataFrame
        """
        last_month = NDVI.index[-1].month
        NDVI_yearly_month = NDVI.loc[NDVI.index.month==last_month]
        health_yearly_month = health.loc[health.index.month==last_month]
        NDVI_mean = NDVI_yearly_month["mean"].iloc[0:-1].mean()
        health_mean = health_yearly_month["Vigor Alto"].iloc[0:-1].mean()
        
        NDVI_yearly_index = (NDVI_yearly_month["mean"].iloc[-1] - NDVI_mean)*100 / NDVI_mean
        #health_yearly_index = (health_yearly_month["Vigor Alto"].iloc[-1] - health_mean)*100 / health_mean
        health_yearly_index = (health_yearly_month["Vigor Alto"].iloc[-1] - health_mean)*100 / health_mean
        
        NDVI_slope = (NDVI_yearly_month["mean"].iloc[-1] - NDVI_yearly_month["mean"].iloc[-2]) / 2.0
        health_slope = (health_yearly_month["Vigor Alto"].iloc[-1] - health_yearly_month["Vigor Alto"].iloc[-2]) / 2.0
        
        NDVI_last = NDVI_yearly_month["mean"].iloc[-1]
        health_last = health_yearly_month["Vigor Alto"].iloc[-1]

        return [NDVI_yearly_index, NDVI_slope, NDVI_last, health_yearly_index, health_slope, health_last] #Normalizarlo

    def getIndexes(self, filter_):
        with open(self.path) as f:
            features = json.load(f)['features']

        [field] = [p for p in features if p["properties"]["name"]==filter_]
        field_polygon = shape(field['geometry']) #POLYGON GEOJSON Structure.

        raw_data = self.raw_sat_data_extractor(field_polygon)        
        df = self.fis_data_to_dataframe(raw_data)
        [NDVI,health] = self.health_DF_generator(df,0.35,0.75)
        return self.index_generator(NDVI, health)        

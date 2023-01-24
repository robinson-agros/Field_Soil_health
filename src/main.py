from pydantic import BaseModel
from typing import Optional, Dict, List
from fastapi import FastAPI
from indexes import Index
import json

app = FastAPI()
    
# Getting parcels data - Input farmer name 
file = open('Parcelas_Test.geojson')
info = json.load(file)

class UserBase(BaseModel):
    name: Optional[str] = None

class IndexOut(UserBase):
    geometry: Optional[Dict] = None
    index: Dict[str, float] = None
   
def get_geometry(user_name):
    for i in range(0, len(info['features'])):
        name = info['features'][i]['properties']['name']
        geometry = info['features'][i]['geometry']
        if name == user_name:
            return geometry
    return None

@app.get("/user/{user_name}", tags=['item'], response_model = IndexOut)
async def get_index(user_name: str):
    #userOut = get_index(user_name)
    #return userOut
    tmp = IndexOut()
    tmp.name = user_name
    geometry = get_geometry(user_name)
    index = Index() 
    if geometry is not None:
        _index = index.getIndexes(user_name)
        tmp.index = {
            "NDVI_yearly_index": _index[0], 
            "NDVI_slope": _index[1], 
            "NDVI_last": _index[2], 
            "health_yearly_index": _index[3], 
            "health_slope": _index[4], 
            "health_last": _index[5]
        }
    tmp.geometry = geometry
    return tmp
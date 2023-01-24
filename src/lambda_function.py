import json
from indexes import Index

print('Getting Sentinel values...')

file = open('Parcelas_Test.geojson')
info = json.load(file)

# Functions

def get_geometry(user_name):
    for i in range(0, len(info['features'])):
        name = info['features'][i]['properties']['name']
        geometry = info['features'][i]['geometry']
        if name == user_name:
            return geometry
    return None

def handler(event, context):

    # Input
    # Username: Edilberto_Sarango

    # 1. Log received user
    username = event.get("username", None)
    print(r"Received user:" + username.replace("_", ""))
    
    geometry = get_geometry(username)
    # 2. Use Sentinelhub API
    tmp = {
         'name' : username,
         'geometry': geometry
    }
    index = Index() 
    if geometry is not None:
        _index = index.getIndexes(username)
        tmp['index'] = {
            "NDVI_yearly_index": _index[0], 
            "NDVI_slope": _index[1], 
            "NDVI_last": _index[2], 
            "health_yearly_index": _index[3], 
            "health_slope": _index[4], 
            "health_last": _index[5]
        }

    # 3. Construct response object (JSON)
    return tmp

    
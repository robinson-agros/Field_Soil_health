import geopandas as gpd
import json
import plotly.express as px

# 0-5
colors = [['rgb(242, 248, 244)'],
          ['rgb(202, 226, 210)'],
          ['rgb(143, 193, 160)'],
          ['rgb(87, 158, 111)'],
          ['rgb(43, 79, 55)']]

def get_img(choice, health):
    if health > 80:
        hexColor = colors[4]
    elif health > 60:
        hexColor = colors[3]
    elif health > 40:
        hexColor = colors[2]
    elif health > 20:
        hexColor = colors[1]
    else:
        hexColor = colors[0]
    
      
    file = 'Parcelas_Test.geojson'
    gg = json.load(open(file))
    _geo_df = gpd.GeoDataFrame.from_features(
        gg['features']
    ) 

    geo_df = _geo_df[_geo_df['name']==choice]
    geo_choice = geo_df.reset_index()
    lon = (geo_choice.centroid.x)[0]
    lat = (geo_choice.centroid.y)[0]
    geo_df = geo_df.set_index("name")

    fig0 = px.choropleth_mapbox(geo_df,
                               geojson=geo_df.geometry,
                               locations=geo_df.index,
                               color=geo_df.index,
                               color_discrete_sequence=hexColor,
                               center={"lon":lon, "lat":lat},
                               mapbox_style="carto-positron",
                               zoom=16,
                               width=800,
                               height=500)
    fig0 = fig0.update_layout(showlegend=False, margin={"r":0,"t":0,"l":0,"b":0})

    fig0.write_image("tmp/parcela.png")

    fig1 = px.choropleth_mapbox(geo_df,
                               geojson=geo_df.geometry,
                               locations=geo_df.index,
                               color=geo_df.index,
                               color_discrete_sequence=hexColor,
                               center={"lon":lon, "lat":lat},
                               mapbox_style="stamen-terrain",
                               zoom=15,
                               width=800,
                               height=500)
    fig1 = fig1.update_layout(showlegend=False, margin={"r":0,"t":0,"l":0,"b":0})

    fig1.write_image("tmp/parcela_terr.png")

    fig2 = px.choropleth_mapbox(geo_df,
                               geojson=geo_df.geometry,
                               locations=geo_df.index,
                               color=geo_df.index,
                               color_discrete_sequence=hexColor,
                               center={"lon":lon, "lat":lat},
                               mapbox_style="open-street-map",
                               zoom=15,
                               width=800,
                               height=500)
    fig2 = fig2.update_layout(showlegend=False, margin={"r":0,"t":0,"l":0,"b":0})

    fig2.write_image("tmp/parcela_loc.png")

# 3ua2b79phjif15c5qidico2a83

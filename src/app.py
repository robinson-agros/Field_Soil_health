from _plotly_utils.colors import PLOTLY_SCALES
import streamlit as st
import geopandas as gpd
from PIL import Image 
from img_gen import get_img
import plotly.graph_objs as go
import requests
import json


# Read dataframe
@st.cache(allow_output_mutation=True)
def load_data():
    file = 'Parcelas_Test.geojson'
    geo_df = gpd.read_file(file)
    return geo_df

with open('token-url.txt') as f:
    url = f.readline()

_, auth, _, _ = url.split("&")
auth = auth.split("=").pop(1)

st.set_page_config(page_title="Index AGROS",
                   page_icon='🍃')

st.title('🍃 Index de parcelas')

geo_df = load_data()

# Temp names
choice = st.selectbox("Seleccione el nombre:", geo_df['name'])

# Dropdown list of names
st1 = st.container()
# Salud
st2 = st.container()
# NDVI 
st3 = st.container()

def indicadores(salud, ndvi):
    st2.header("Indicador de salud")
    col2_1, col2_2 = st2.columns(2)
    col2_1.markdown("""
    <p style =
        "color:#556270; font-size: 50px; font-weight: bolder"
    >{}%</p>
    """.format(round(salud, 4)), unsafe_allow_html=True)
    col2_1.markdown("""
    <p style =
        "color:#556270; font-size: 20px; font-weight: bold"
    >de su campo esta saludable</p>
    """, unsafe_allow_html=True)

    if salud > 80:
        ms = '✅ El campo se encuentra muy saludable. Es posible que las cosechas mejoren.'
    elif salud > 60:
        ms = '✔️ El campo se encuentra en un estado satisfactorio. Este puede ser mejorado.'
    elif salud > 40:
        ms = '⚠️ El campo no esta muy saludable. Debe tomarse medidas de control para que este mejore.'
    elif salud > 20:
        ms = '⛑ El campo no esta saludable y se recomienda urgentemente tomar medidas de control.'
    else:
        ms = '❌ Su campo se encuentra en peligro. Es urgente tomar medidas o este puede estar afectado permanentemente.'
    
    col2_2.text(" ")
    col2_2.text(" ")
    col2_2.text(" ")
    col2_2.markdown(ms)
    
    st3.header("Indicador NDVI") 
    fig = go.Figure(
        data = [
            go.Bar(
            y = [1] * 100,
            orientation='h',
            marker=dict(color=list(range(100, 0, -1)), colorscale='temps', line_width=0),
        )],
        layout=dict(
            barmode="stack",
            barnorm="fraction",
            showlegend=False,
            xaxis=dict(range=[-0.02, 1.02], showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            plot_bgcolor='rgba(0,0,0,0)',
            height=150,
            width=850,
            margin=go.layout.Margin(l=0, r=0, b=0, t=0)
        )
    )
    
    
    fig.write_image("tmp/bar.png")
    img1 = Image.open('tmp/bar.png')
    
    #st3.plotly_chart(fig, use_container_width=True)
    #fig2 = pd.DataFrame(np.arange(0, 1, 0.1) + 0.1)
    
    fig2 = go.Figure(
        data = [
            go.Scatter(
                x = [ndvi],
                y = [-0.02],
                mode='markers',
                marker_color='#FF0000',
                marker_size=30,
                marker_symbol='arrow-down'
        )],
        layout = dict(
            yaxis =dict(range=[-0.02, 0.02], showgrid=False, showticklabels=False),
            xaxis =dict(range=[-1.02, 1.02]),
            plot_bgcolor='rgba(0,0,0,0)',
            height=150,
            width=850,
            margin=go.layout.Margin(l=10, r=10, b=0, t=0),
        )
    )
    fig2.write_image("tmp/top.png")
    img2 = Image.open('tmp/top.png')
    

    st3.markdown("""
    <p style =
        "color:#556270; font-size: 50px; font-weight: bolder; text-align:center;"
    >{}</p>
    """.format(round(ndvi, 4)), unsafe_allow_html=True)
    st3.markdown("""
    <p style =
        "color:#556270; font-size: 20px; font-weight: bold; text-align:center;"
    >es el indicador NDVI de su campo</p>
    """, unsafe_allow_html=True)

    newimg = Image.blend(img1, img2, alpha=0.55)
    st3.image(newimg, caption='NDVI del campo del agricultor {}'.format(choice.replace('_', ' ')))

    #if ndvi > 0.75:
        #ms2 = '⚠️ El campo se encuentra con mucha clorofila. Esto puede indicar posible maleza, lo cual inhibira una buena produccion.'
    #elif ndvi > 0.55:
        #ms2 = '✅ El campo se encuentra en un buen estado. Es posible que su tierra se encuentre ndviable y tenga una buena produccion.'
    #elif ndvi > 0.3:
        #ms2 = '⛑ El campo no esta es buen estado. Es posible que la produccion se vea afectada y la tierra no este ndviable.'
    #else:
        #ms2 = '❌ La produccion del campo sera baja. Es posible que la produccion sea nula. La tierra puede ser rocosa, arida o un cuerpo acuatico.'
    #st3.markdown(ms2)
    

if st1.button("Mostrar"):
    url = "https://s5gb4e6069.execute-api.us-west-1.amazonaws.com/authorized"
    payload = json.dumps({
      "username": choice 
    })
    headers = {
            # Key access (lasts a day)
            # Get an account and copy access token from the url
            'Authorization': auth,
            'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    
    #st1.text(response_json)
    
    if choice is not None:
        health = response_json['index']['health_last']
        ndvi = response_json['index']['NDVI_last']
        col1_1, col1_2 = st1.columns(2)
        get_img(choice, health)
        img0 = Image.open('tmp/parcela.png')
        img1 = Image.open('tmp/parcela_terr.png')
        img2 = Image.open('tmp/parcela_loc.png')
        st1.image(img0, caption='Parcela del agricultor {}'.format(choice.replace('_', ' ')))
        col1_1.image(img1)
        col1_2.image(img2)
        indicadores(health, ndvi)

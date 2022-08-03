# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 15:07:56 2022

@author: manh.dangtran
"""

import dash
from dash import html, dcc
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
import plotly.figure_factory as ff
from datetime import datetime as dt
from datetime import date,timedelta
from plotly.subplots import make_subplots
import plotly.express as px
from sqlalchemy import true

city_lvl_df = pd.read_csv('data/city_lvl_df.csv')
district_lvl_df = pd.read_csv('data/district_lvl_df.csv')
city_lvl_df_daily = pd.read_csv('data/city_lvl_df_daily.csv')
raw = pd.read_csv('data/raw_t2_t3_18jul_25jul.csv').rename(columns = {'created_time': 'Date/Time', 'pick_longitude': 'Lon', 'pick_latitude': 'Lat', 'report_date': 'Date'})


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "T2 cities gross distribution"
# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

# Plotly mapbox public token
mapbox_access_token = 'pk.eyJ1IjoiamFzb25mbHlpbmciLCJhIjoiY2w0Nmx5OXZmMDlycDNubXM3MDdoZnExcyJ9.XNxyTyZOWPdjSSg5C0H-Xw'

# Dictionary of locations
list_of_locations = {
    "Hai Phong City": {"city_name": "Hai Phong City", "lat": 20.865139, "lon": 106.683830},
    "Dong Nai": {"city_name": "Dong Nai", "lat": 10.964112, "lon": 106.856461},
    "Binh Duong": {"city_name": "Binh Duong", "lat": 10.9929842 , "lon": 106.65570730000002},
    "Hue City": {"city_name": "Hue City", "lat": 16.4637, "lon": 107.5909},
    "Vung Tau": {"city_name": "Vung Tau", "lat": 10.411380, "lon": 107.136224},
    "Can Tho City": {"city_name": "Can Tho City", "lat": 10.0452, "lon": 105.7469},
    "Nghe An": {"city_name": "Nghe An", "lat": 18.679585, "lon": 105.681335},
    "Bac Ninh": {"city_name": "Bac Ninh", "lat": 21.1833326, "lon": 106.0499998},
    "Thai Nguyen": {"city_name": "Thai Nguyen", "lat": 21.59422, "lon": 105.84817},
    "Quang Ninh": {"city_name": "Quang Ninh", "lat": 20.959902, "lon": 107.042542},
    "Khanh Hoa": {"city_name": "Khanh Hoa", "lat": 12.243480, "lon": 109.196091},
    "Lam Dong": {"city_name": "Lam Dong", "lat": 11.940419, "lon": 108.458313},
    "Quang Nam": {"city_name": "Quang Nam", "lat": 15.87944, "lon": 108.335}
}


# Initialize data frame
raw["Date/Time"] = pd.to_datetime(raw["Date/Time"])
raw.index = raw["Date/Time"]
raw['Timeslot'] = raw["Date/Time"].dt.hour


totalList = []
for month in raw.groupby(raw.index.month):
    dailyList = []
    for day in month[1].groupby(month[1].index.day):
        dailyList.append(day[1])
    totalList.append(dailyList)
totalList = np.array(totalList)

raw.reset_index(drop=True, inplace=True)

# city_lvl_df = pd.read_csv('data\city level data\city_lvl_df.csv')
# district_lvl_df = pd.read_csv('data\district level data\district_lvl_df.csv')

city_lvl_df['created_date'] = pd.to_datetime(city_lvl_df['created_date'])
district_lvl_df['created_date'] = pd.to_datetime(district_lvl_df['created_date'])

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.A(
                            html.Img(
                                className="logo",
                                src=app.get_asset_url("shopeefood - resize.png"),
                                style={'height':'20%', 'width':'20%'},
                            ),
                            href="https://shopeefood.vn/",
                        ),
                        html.H2("T2 CITIES - DASHBOARD"),
                        html.P(
                            """Select different days using the date picker or by selecting
                            different time frames on the histogram."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=city_lvl_df['created_date'].min().date(),
                                    max_date_allowed=city_lvl_df['created_date'].max().date(),
                                    initial_visible_month=city_lvl_df['created_date'].max().date(),
                                    date=city_lvl_df['created_date'].max().date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="location-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_locations
                                            ],
                                            placeholder="Select a city",
                                            value = 'Hai Phong City'
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n) + ":00",
                                                    "value": n,
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Select certain hours",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select types of map
                                        dcc.Dropdown(
                                            id="map-index-selector",
                                            options=[ "Heat map", 
                                                     "Scatter plot",
                                            ],
                                            multi=False,
                                            placeholder="Select type of map",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select indices to show
                                        dcc.Dropdown(
                                            id="index-selector",
                                            options=[ "Gross order", 
                                                     "CND",
                                            ],
                                            multi=False,
                                            placeholder="Select index to check (Gross - CND)",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.P(id="total-orders"),
                        html.P(id="total-cnd"),
                        html.P(id="date-value"),
                        dcc.Markdown(
                            """
                            Source: [Jason Data Guy](https://github.com/jasondataguy)

                            """
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph"),
                        html.Div(
                            className="text-padding",
                            children=[
                                "Select any of the bars on the histogram to section data by time."
                            ],
                        ),
                        dcc.Graph(id="histogram"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="text-padding",
            children=[
                "Indices tracking"
            ],
        ),
        # first row
        html.Div(
            className="row",
            id="sixth-row",
            children=[
                # Formation bar plots
                html.Div(
                    id="orderlevel-graph-container",
                    # className="twelve columns",
                    children=[
                        dcc.Graph(id="orderlevel-graph"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="text-padding",
            children=[
                "Daily tracking by timeslot"
            ],
        ),
        # second row
        html.Div(
            className="row",
            # id="second-row",
            children=[
                # Formation bar plots
                html.Div(
                    id="stack-peak3-graph-container",
                    className="six columns",
                    children=[
                        dcc.Graph(id="stack-peak3-graph"),
                    ],
                ),
                html.Div(
                    id="demand-gross-net-graph-container",
                    className="six columns",
                    children=[
                        dcc.Graph(id="demand-gross-net-graph"),
                    ],
                ),
                html.Div(
                    id="g2n-graph-container",
                    className="six columns",
                    children=[
                        dcc.Graph(id="g2n-graph"),
                    ],
                ),
            ],
        ),
        # third row
        html.Div(
            className="row",
            id="third-row",
            children=[
                # Formation bar plots
                html.Div(
                    id="time-performance-graph-container",
                    className="six columns",
                    children=[
                        dcc.Graph(id="time-performance-graph"),
                    ],
                ),
                html.Div(
                    id="supply-graph-container",
                    className="six columns",
                    children=[
                        dcc.Graph(id="supply-graph"),
                    ],
                ),
                html.Div(
                    id="cnd-graph-container",
                    className="six columns",
                    children=[
                        dcc.Graph(id="cnd-graph"),
                    ],
                ),
            ],
        ),
        # forth row
        html.Div(
            className="row",
            id="forth-row",
            children=[
                # Formation bar plots
                html.Div(
                    id="cnd-timeslot-date-graph-container",
                    className="twelve columns",
                    children=[
                        dcc.Graph(id="cnd-timeslot-date-graph"),
                    ],
                ),
            ],
        ),
    ]
)

# This also higlights the color of the histogram bars based on
# if the hours are selected
def get_selection(month, day, selection):
    xVal = []
    yVal = []
    xSelected = []
    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]

    # Put selected times into a list of numbers xSelected
    xSelected.extend([int(x) for x in selection])

    for i in range(24):
        # If bar is selected then color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
        xVal.append(i)
        # Get the number of orders at a particular time
        yVal.append(len(totalList[month][day][totalList[month][day].index.hour == i]))
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]


# Selected Data in the Histogram updates the Values in the Hours selection dropdown menu
@app.callback(
    Output("bar-selector", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])))
    return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}


# Update the total number of orders Tag
@app.callback(Output("total-orders", "children"), [Input("date-picker", "date")])
def update_total_orders(datePicked):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    return "Total Number of orders: {:,d}".format(
        len(totalList[date_picked.month - 4][date_picked.day - 1])
    )


# Update the total number of cnd in selected times
@app.callback(
    [Output("total-cnd", "children"), Output("date-value", "children")],
    [Input("date-picker", "date"), Input("bar-selector", "value")],
)
def update_total_orders_selection(datePicked, selection):
    firstOutput = ""

    if selection != None or len(selection) != 0:
        date_picked = dt.strptime(datePicked, "%Y-%m-%d")
        totalInSelection = 0
        for x in selection:
            totalInSelection += len(
                totalList[date_picked.month - 4][date_picked.day - 1][
                    totalList[date_picked.month - 4][date_picked.day - 1].index.hour
                    == int(x)
                ]
            )
        firstOutput = "Total orders in selection: {:,d}".format(totalInSelection)

    if (
        datePicked is None
        or selection is None
        or len(selection) == 24
        or len(selection) == 0
    ):
        return firstOutput, (datePicked, " - showing hour(s): All")

    holder = sorted([int(x) for x in selection])

    if holder == list(range(min(holder), max(holder) + 1)):
        return (
            firstOutput,
            (
                datePicked,
                " - showing hour(s): ",
                holder[0],
                "-",
                holder[len(holder) - 1],
            ),
        )

    holder_to_string = ", ".join(str(x) for x in holder)
    return firstOutput, (datePicked, " - showing hour(s): ", holder_to_string)

# Get the Coordinates of the chosen months, dates and times
def getLatLonColor(selectedData, month, day):
    listCoords = totalList[month][day]

    # No times selected, output all times for chosen month and date
    if len(selectedData) == 0:
        return listCoords
    listStr = "listCoords["
    for time in selectedData:
        if selectedData.index(time) is not len(selectedData) - 1:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ") | "
        else:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ")]"
    return eval(listStr)

# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("bar-selector", "value"),
        Input("location-dropdown", "value"),
        Input("map-index-selector", "value"),
        Input("index-selector", "value"),
    ],
)

def update_graph(datePicked, selectedData, selectedLocation, selectedMap, selectedIndex):
    selected_map = "Heat map"
    selected_index = "No driver"
    selected_color = 'orange'
    mapbox_access_token = 'pk.eyJ1IjoiamFzb25mbHlpbmciLCJhIjoiY2w0Nmx5OXZmMDlycDNubXM3MDdoZnExcyJ9.XNxyTyZOWPdjSSg5C0H-Xw'
    zoom = 12.0
    latInitial = 20.8449
    lonInitial = 106.6881
    bearing = 0
    timeslot = list(range(0,24))
    city_name = 'Hai Phong City'
    date_picked = datePicked
    
    if selectedData:
        timeslot = selectedData
        
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
        latInitial = list_of_locations[selectedLocation]['lat']
        lonInitial = list_of_locations[selectedLocation]['lon']
    
    if selectedMap:
        selected_map = selectedMap
    
    if selectedIndex:
        if selectedIndex == "Gross order":
            selected_index = np.nan
            selected_color = 'blue'
        elif selectedIndex == "CND":
            selected_index = "No driver"
            selected_color = 'orange'

    if selected_map == "Scatter plot":
        fig = px.scatter_mapbox(
                data_frame = raw[(raw["city_name"] == city_name) & (raw["Date"] == date_picked) & (raw["Timeslot"].isin(timeslot)) & (raw["cancel_reason"] == selected_index)],
                lat='Lat',
                lon='Lon',
                # color_discrete_sequence = selected_color 
                # mode="markers",
                # hoverinfo="lat+lon+text",
                # marker=dict(
                #     showscale=True,
                #     color="Timeslot",
                #     opacity=0.5,
                #     size=5,
                #     colorscale=[
                #         [0, "#F4EC15"],
                #         [0.04167, "#DAF017"],
                #         [0.0833, "#BBEC19"],
                #         [0.125, "#9DE81B"],
                #         [0.1667, "#80E41D"],
                #         [0.2083, "#66E01F"],
                #         [0.25, "#4CDC20"],
                #         [0.292, "#34D822"],
                #         [0.333, "#24D249"],
                #         [0.375, "#25D042"],
                #         [0.4167, "#26CC58"],
                #         [0.4583, "#28C86D"],
                #         [0.50, "#29C481"],
                #         [0.54167, "#2AC093"],
                #         [0.5833, "#2BBCA4"],
                #         [1.0, "#613099"],
                #     ],
                #     colorbar=dict(
                #         title="Time of<br>Day",
                #         x=0.93,
                #         xpad=0,
                #         nticks=24,
                #         tickfont=dict(color="#d8d8d8"),
                #         titlefont=dict(color="#d8d8d8"),
                #         thicknessmode="pixels",
                #     ),
                # )
            )
        
        fig.update_layout(
            go.Layout(
                autosize=True,
                margin=go.layout.Margin(l=0, r=35, t=0, b=0),
                showlegend=False,
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                    style="light",
                    bearing=bearing,
                    zoom=zoom,
                ),
                updatemenus=[
                    dict(
                        buttons=(
                            [
                                dict(
                                    args=[
                                        {
                                            "mapbox.zoom": 12,
                                            "mapbox.center.lon": "106.6881",
                                            "mapbox.center.lat": "20.8449",
                                            "mapbox.bearing": 0,
                                            "mapbox.style": "light",
                                        }
                                    ],
                                    label="Reset Zoom",
                                    method="relayout",
                                )
                            ]
                        ),
                        direction="left",
                        pad={"r": 0, "t": 0, "b": 0, "l": 0},
                        showactive=False,
                        type="buttons",
                        x=0.45,
                        y=0.02,
                        xanchor="left",
                        yanchor="bottom",
                        bgcolor="#6d6d6d",
                        borderwidth=1,
                        bordercolor="#6d6d6d",
                        font=dict(color="#FFFFFF"),
                    )
                ],
            ),
        )
        return fig
 
    if selected_map == "Heat map":
        fig = ff.create_hexbin_mapbox(data_frame=raw[(raw["city_name"] == city_name) & (raw["Date"] == date_picked) & (raw["Timeslot"].isin(timeslot)) & (raw["cancel_reason"] == selected_index)], 
                                            lat="Lat", lon="Lon",
                                            nx_hexagon=20, 
                                            opacity=0.5, 
                                            labels={"color": "Density index"},
                                            mapbox_style='light',
                                            color_continuous_scale="viridis",
                                            show_original_data=True, 
                                            original_data_marker=dict(opacity=0.5, size=5, color=selected_color),
                                            min_count=50,
                                            zoom=12,
                                            center= {"lon": 106.6881, "lat": 20.8449}
                                            )       
        fig.update_layout(
            go.Layout(
                autosize=True,
                margin=go.layout.Margin(l=0, r=35, t=0, b=0),
                showlegend=False,
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                    style="light",
                    bearing=bearing,
                    zoom=zoom,
                ),
                updatemenus=[
                    dict(
                        buttons=(
                            [
                                dict(
                                    args=[
                                        {
                                            "mapbox.zoom": 12,
                                            "mapbox.center.lon": "106.6881",
                                            "mapbox.center.lat": "20.8449",
                                            "mapbox.bearing": 0,
                                            "mapbox.style": "light",
                                        }
                                    ],
                                    label="Reset Zoom",
                                    method="relayout",
                                )
                            ]
                        ),
                        direction="left",
                        pad={"r": 0, "t": 0, "b": 0, "l": 0},
                        showactive=False,
                        type="buttons",
                        x=0.45,
                        y=0.02,
                        xanchor="left",
                        yanchor="bottom",
                        bgcolor="#6d6d6d",
                        borderwidth=1,
                        bordercolor="#6d6d6d",
                        font=dict(color="#FFFFFF"),
                    )
                ],
            ),
        )
        return fig


# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [Input("date-picker", "date"), 
     Input("location-dropdown", "value"), 
     Input("index-selector", "value"),
],
)
def update_histogram(datePicked, selectedLocation, selectedIndex):
    selected_index = "CND"
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    city_name = 'Hai Phong City'
    
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
    if selectedIndex:
        selected_index = selectedIndex

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        dragmode="select",
        font=dict(color="black"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
    )
    if selected_index == "CND":
        return go.Figure(
            data=[
                go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                       y=city_lvl_df['cnd'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                       text=np.array(city_lvl_df['cnd'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                       textposition="outside",
                    #    texttemplate="%{text: .0}",
                       hoverinfo="x",
                       marker_color = 'rgb(166, 28, 0)',                         
                    ),
            ],
            layout=layout,
        )
    if selected_index == "Gross order":
        return go.Figure(
            data=[
                go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                       y=city_lvl_df['gross_order'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                       text=np.array(city_lvl_df['gross_order'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                       textposition="outside",
                    #    texttemplate="%{text: .0}",
                       hoverinfo="x",
                       marker_color = 'rgb(0, 67, 88)',                     
                       ),
            ],
            layout=layout,
        )
#time range applied to all graphs (from 7:00-22:00) 
time_range = range(7,22,1)

@app.callback(
    Output("orderlevel-graph", "figure"),
    [Input("date-picker", "date"), Input("location-dropdown", "value")],
)

def update_orderlevel_graph(datePicked, selectedLocation):
    date_picked = pd.to_datetime(dt.strptime(datePicked, "%Y-%m-%d"))
    city_name = 'Hai Phong City'
    
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
        
    fig = make_subplots(rows = 2, cols = 1,
                        row_heights=[0.3, 1.3],
                        # column_widths=[0.1, 0.1],
                        shared_yaxes=True,
                        shared_xaxes=True,
                        horizontal_spacing = 0.0,
                        vertical_spacing = 0.0,
                        specs=[[{"secondary_y": False}],
                              [{"secondary_y": True}]])     

    fig.add_trace(go.Bar(x=city_lvl_df_daily['created_date'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                         y=city_lvl_df_daily['%bw'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                        text=np.array((city_lvl_df_daily['%bw'][(city_lvl_df_daily['pick_city_name'] == city_name)]*100).round(0).astype('int').astype(str) + '%'),
                        textposition="none",
                        # texttemplate="%{text: .0%}",
                         name = 'BW impact'), row = 1, col = 1)
    
    fig.add_trace(go.Bar(x=city_lvl_df_daily['created_date'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                         y=city_lvl_df_daily['cnd'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                        text=np.array((city_lvl_df_daily['%cnd'][(city_lvl_df_daily['pick_city_name'] == city_name)]*100).round(1).astype(str) + '%'),
                        textposition="none",
                        # texttemplate="%{text: .0%}",
                         name='CND',
                         marker_color = 'rgb(166, 28, 0)'                           
                        ),
                  secondary_y = False, row = 2, col = 1
                 )    
    fig.add_trace(go.Bar(x=city_lvl_df_daily['created_date'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                         y=city_lvl_df_daily['cancel_by_mex_users'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                        # text=np.array(city_lvl_df_daily['%inactive_drivers'][(city_lvl_df_daily['created_date'] == '2022-07-10') & (city_lvl_df_daily['pick_city_name'] == 'Hai Phong City')]),
                        # textposition="inside",
                        # texttemplate="%{text: .0%}",
                         name='cancel by mex & users',
                         marker_color = 'rgb(253, 116, 0)'                           
                        ),
                  secondary_y = False, row = 2, col = 1
                 )
    fig.add_trace(go.Bar(x=city_lvl_df_daily['created_date'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                         y=city_lvl_df_daily['total_delivered'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                        text=np.array((city_lvl_df_daily['%g2n'][(city_lvl_df_daily['pick_city_name'] == city_name)]*100).round(0).astype('int').astype(str) + '%'),
                        textposition="inside",
                        # texttemplate="%{text: .0%}",
                         name='delivered',
                         marker_color = 'rgb(0, 67, 88)'                            
                        ),
                  secondary_y = False, row = 2, col =1
                 ) 
    fig.add_trace(go.Scatter(x=city_lvl_df_daily['created_date'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                         y=city_lvl_df_daily['A1'][(city_lvl_df_daily['pick_city_name'] == city_name)], 
                        # text=np.array(city_lvl_df_daily['%g2n'][(city_lvl_df_daily['pick_city_name'] == city_name)]),
                        # textposition="inside",
                        # texttemplate="%{text: .0%}",
                        name='A1',
                        mode="lines+text",
                        line_shape="spline"),
                  secondary_y = True, row = 2, col = 1
                 ) 
    fig.update_layout(barmode='stack',
            bargap=0,
            bargroupgap=0,
            template='simple_white',
            autosize=True,
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            hovermode="x unified",
            xaxis=dict(
            showgrid=False,
            fixedrange=True,
        ),
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            showlegend = True)    
    
    fig.update_traces(marker_line_width=0.1,
                      opacity = 0.5)
    
    fig.update_yaxes(visible=False, row=1, col=1)
    
    return fig

 
@app.callback(
    Output("stack-peak3-graph", "figure"),
    [Input("date-picker", "date"), Input("location-dropdown", "value")],
)

def update_stack_peak3_graph(datePicked, selectedLocation):
    date_picked = pd.to_datetime(dt.strptime(datePicked, "%Y-%m-%d"))
    city_name = 'Hai Phong City'
    
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
    fig = make_subplots(rows = 2, cols = 1,
                        row_heights=[0.2, 1],
                        # column_widths=[0.1, 0.1],
                        shared_yaxes=True,
                        shared_xaxes=True,
                        horizontal_spacing = 0.0,
                        vertical_spacing = 0.0,
                        specs=[[{"secondary_y": False}],
                              [{"secondary_y": True}]])     
    fig.add_trace(go.Bar(
        name='%BW impact',
            x=np.array(city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]),
            y=np.array(city_lvl_df['%orders_bw/gross'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]),
            text=np.array((city_lvl_df['%orders_bw/gross'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]*100).round(0).astype('int').astype(str) + '%'),
            textposition="none",
            ), secondary_y = False, row = 1, col = 1
        )    
    fig.add_trace(go.Bar(
        name='%stack',
            x=np.array(city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]),
            y=np.array(city_lvl_df['%stack'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]),
            marker_color = 'rgb(253, 116, 0)' 
            ), secondary_y = False, row = 2, col = 1
        )
    
    fig.add_trace(go.Bar(
        name='%peak3',
            x=np.array(city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]),
            y=np.array(city_lvl_df['%peak3'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]),
            marker_color = 'rgb(166, 28, 0)'                              
            ), secondary_y = False, row = 2, col = 1
        )
    
    # fig.add_trace(go.Scatter(
    # name='%Bad weather impact',
    #     x=np.array(city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]),
    #     y=np.array(city_lvl_df['%orders_bw/gross'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['timeslot'].isin(time_range))]),
    #     mode="lines",  
    #     line_shape="hvh",
    #     line_dash="dashdot",
    #     marker_color = '#096298' 
    #     ), secondary_y = True 
    # )
 
    fig.update_layout(
        barmode = 'overlay',
        bargap=0,
        bargroupgap=0, 
        template='simple_white',
        # autosize=True,
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        xaxis=dict(
        range=[6.5, 21.5],
        nticks=25,
        showgrid=False,
        fixedrange=True,
        ),
        yaxis=dict(    
        tickformat= ',.0%',
        showgrid=False,
        ),
        yaxis2=dict(    
        tickformat= ',.0%',
        showgrid=False,
        range=[0, 1],
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
        ),
        hovermode="x unified",
        showlegend = True
    )

    fig.update_traces(marker_line_width=0,
                      opacity = 0.5
                      )
    fig.update_yaxes(visible=False, tickformat= ',.0%', row=1, col=1)

    return fig   

# Update demand-gross-net Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("demand-gross-net-graph", "figure"),
    [Input("date-picker", "date"), Input("location-dropdown", "value")],
)

def update_demand_gross_net_graph(datePicked, selectedLocation):
    date_picked = pd.to_datetime(dt.strptime(datePicked, "%Y-%m-%d"))
    city_name = 'Hai Phong City'
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
        
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                             y=city_lvl_df['gross_order'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                             text=np.array(city_lvl_df['%change_gross_order'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                             textposition="top center",
                             texttemplate="%{text: .0%}",
                             mode="lines+text",
                             line_shape="spline",
                             fill='tozeroy', 
                             name='Gross orders', 
                             fillpattern=dict(fillmode='overlay'),
                            )
                 )
    fig.add_trace(go.Scatter(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                             y=city_lvl_df['net_order'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                            text=np.array(city_lvl_df['%change_net_order'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                             textposition="bottom center",
                             texttemplate="%{text: .0%}",
                             mode="lines+text",
                             line_shape="spline",
                             fill='tozeroy', 
                             name='Net orders',
                             fillpattern=dict(fillmode='overlay'),
                            )
                ) 
    fig.update_layout(barmode='stack',
            bargap=0.01,
            bargroupgap=0,
            template='simple_white',
            autosize=True,
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            hovermode="x unified",
            xaxis=dict(
            range=[6.5, 21.5],
            nticks=25,
            showgrid=False,
            fixedrange=True,
        ),
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            showlegend = True)

    return fig

# Update supply Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("supply-graph", "figure"),
    [Input("date-picker", "date"), Input("location-dropdown", "value")],
)

def update_supply_graph(datePicked, selectedLocation):
    date_picked = pd.to_datetime(dt.strptime(datePicked, "%Y-%m-%d"))
    city_name = 'Hai Phong City'
    
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
        
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        y=city_lvl_df['inactive_drivers'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        text=np.array(city_lvl_df['%inactive_drivers'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                        textposition="inside",
                        texttemplate="%{text: .0%}",
                        name='Inactive drivers (%)',
                            ),
                    secondary_y = False
                 ) 

    fig.add_trace(go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        y=city_lvl_df['active_drivers'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        text=np.array(city_lvl_df['%change_online_drivers'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                        textposition="outside",
                        texttemplate="%{text: .0%}",
                        name='Active drivers',
                            ),
                    secondary_y = False
                ) 
    fig.add_trace(go.Scatter(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                            y=city_lvl_df['driver_ADO'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                            name='Driver ADO',
                            mode="lines+text",
                            line_shape="spline",
                            ),
                    secondary_y = True
                 ) 
    fig.update_layout(barmode='stack',
            bargap=0.01,
            bargroupgap=0,
            template='simple_white',
            autosize=True,
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            hovermode="x unified",
            xaxis=dict(
            range=[6.5, 21.5],
            nticks=25,
            showgrid=False,
            fixedrange=True,
        ),
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            showlegend = True)

    return fig

@app.callback(
    Output("time-performance-graph", "figure"),
    [Input("date-picker", "date"), Input("location-dropdown", "value")],
)
def update_time_performance_graph(datePicked, selectedLocation):
    date_picked = pd.to_datetime(dt.strptime(datePicked, "%Y-%m-%d"))
    city_name = 'Hai Phong City'
    
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
        
    fig = go.Figure()
    fig.add_trace(
        go.Bar(name='down time',
            x=np.array(city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)])
            , y=np.array(city_lvl_df['avr.down_time'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)])
                , text=np.array(city_lvl_df['%down_time'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)])
                , texttemplate="%{text: .0%}")
        )

    fig.add_trace(
        go.Bar(name='working time', 
            x=np.array(city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)])
            , y=np.array(city_lvl_df['avr.work_time'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)])
            )
        )

    # Change the bar mode
    fig.update_layout(barmode='stack',   
            bargap=0,
            bargroupgap=0, 
            template='simple_white',
            autosize=True,
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            hovermode="x unified",
            xaxis=dict(
            range=[6.5, 21.5],
            nticks=25,
            showgrid=False,
            fixedrange=True,
        ),
            showlegend = True)
    
    # fig.update_traces(marker_line_width=0)
    return fig

@app.callback(
    Output("g2n-graph", "figure"),
    [Input("date-picker", "date"), Input("location-dropdown", "value")],
)
def update_g2n_graph(datePicked, selectedLocation):
    date_picked = pd.to_datetime(dt.strptime(datePicked, "%Y-%m-%d"))
    city_name = 'Hai Phong City'
    
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
        
    fig = make_subplots(specs=[[{"secondary_y": True}]])     
    
    fig.add_trace(go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                         y=city_lvl_df['%cnd'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        # text=np.array(city_lvl_df['%inactive_drivers'][(city_lvl_df['created_date'] == '2022-07-10') & (city_lvl_df['pick_city_name'] == 'Hai Phong City')]),
                        # textposition="inside",
                        # texttemplate="%{text: .0%}",
                         name='%cnd',
                         marker_color = 'rgb(166, 28, 0)'                           
                        ),
                  secondary_y = False
                 )    
    fig.add_trace(go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                         y=city_lvl_df['%cancel_by_mex_users'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        # text=np.array(city_lvl_df['%inactive_drivers'][(city_lvl_df['created_date'] == '2022-07-10') & (city_lvl_df['pick_city_name'] == 'Hai Phong City')]),
                        # textposition="inside",
                        # texttemplate="%{text: .0%}",
                         name='%cancelled by mex & users',
                         marker_color = 'rgb(253, 116, 0)'                           
                        ),
                  secondary_y = False
                 )
    fig.add_trace(go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                         y=city_lvl_df['%g2n'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        text=np.array(city_lvl_df['%g2n'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                        textposition="inside",
                        texttemplate="%{text: .0%}",
                         name='%g2n',
                         marker_color = 'rgb(0, 67, 88)'                            
                        ),
                  secondary_y = False
                 ) 
    fig.update_layout(barmode='stack',
            bargap=0,
            bargroupgap=0,
            template='simple_white',
            autosize=True,
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            hovermode="x unified",
            xaxis=dict(
            range=[6.5, 21.5],
            nticks=25,
            showgrid=False,
            fixedrange=True,
        ),
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="right",
            x=1
        ),
            showlegend = True)    
    
    fig.update_traces(marker_line_width=0.1,
                      opacity = 0.5)
    fig.update_yaxes(visible=False)
    
    return fig

@app.callback(
    Output("cnd-graph", "figure"),
    [Input("date-picker", "date"), Input("location-dropdown", "value")],
)
def update_cnd_graph(datePicked, selectedLocation):
    date_picked = pd.to_datetime(dt.strptime(datePicked, "%Y-%m-%d"))
    city_name = 'Hai Phong City'
    
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
    
    fig = make_subplots(rows = 2, cols = 1,
                        row_heights=[0.2, 1],
                        # column_widths=[0.1, 0.1],
                        shared_yaxes=True,
                        shared_xaxes=True,
                        horizontal_spacing = 0.0,
                        vertical_spacing = 0.0,
                        specs=[[{"secondary_y": False}],
                              [{"secondary_y": True}]])    
        
    fig.add_trace(go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        y=city_lvl_df['%cnd_bw'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)],
                        # customdata = np.array(city_lvl_df['%cnd/wholeday'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                        # text=np.array((city_lvl_df['%cnd_bw'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]*100).round(0).astype(str) + '%'),
                        textposition="none",
                        # texttemplate="%{text: .0%}",
                        # hovertemplate="%{customdata: .0%}",
                        name='CND_BW impact',                        
                        ),
                  secondary_y = False, row=1, col=1
                 )

    fig.add_trace(go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        y=city_lvl_df['cnd'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)],
                        customdata = np.array(city_lvl_df['%cnd/wholeday'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                        text=np.array(city_lvl_df['%cnd/wholeday'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)]),
                        textposition="none",
                         hovertemplate="%{customdata: .0%}",
                         name='cnd',
                         marker_color = 'rgb(166, 28, 0)'                           
                        ),
                  secondary_y = False, row=2, col=1
                 ) 

    # Add gross/supply line
    fig.add_trace(go.Scatter(x=city_lvl_df['timeslot'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        y=city_lvl_df['gross_order / online_time'][(city_lvl_df['created_date'] == date_picked) & (city_lvl_df['pick_city_name'] == city_name)], 
                        # text=np.array(city_lvl_df['%inactive_drivers'][(city_lvl_df['created_date'] == '2022-07-10') & (city_lvl_df['pick_city_name'] == 'Hai Phong City')]),
                        # textposition="inside",
                        # texttemplate="%{text: .0%}",
                        name='demand/supply', 
                        mode="lines+text",  
                        line_shape="spline"                      
                        ),
                  secondary_y = True, row=2, col=1
                 )

    fig.update_layout(barmode='stack',
            bargap=0,
            bargroupgap=0,
            template='simple_white',
            autosize=True,
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            xaxis=dict(
            range=[6.5, 21.5],
            nticks=25,
            showgrid=False,
            fixedrange=True,
        ),
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            showlegend = True)    
    
    fig.update_traces(marker_line_width=0.1,
                      opacity = 0.5)
    fig.update_yaxes(visible=False, tickformat= ',.0%', row=1, col=1)

    return fig

@app.callback(
    Output("cnd-timeslot-date-graph", "figure"),
    [Input("date-picker", "date"), Input("location-dropdown", "value")],
)
def update_cnd_timeslot_date_graph(datePicked, selectedLocation):
    date_picked = pd.to_datetime(dt.strptime(datePicked, "%Y-%m-%d"))
    city_name = 'Hai Phong City'  
    if selectedLocation:
        city_name = list_of_locations[selectedLocation]['city_name']
        
    from_date = date_picked + timedelta(-7)
    days_in_year = np.array(city_lvl_df['created_date'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (city_lvl_df['created_date'] <= date_picked)]) #gives me a list with datetimes for each day a year
    timeslot = np.array(city_lvl_df['timeslot'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (city_lvl_df['created_date'] <= date_picked)]) #gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,...] (ticktext in xaxis dict translates this to weekdays
    data_days = np.array(city_lvl_df['cnd'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (city_lvl_df['created_date'] <= date_picked)]) #random numbers to give some mad colorz
    text = np.array(city_lvl_df['cnd'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (city_lvl_df['created_date'] <= date_picked)]) #gives something like list of strings like '2018-01-25' for each date. Used in data trace to make good hovertext.
    def custom_data(): #custom data to add inside hover for each city
        if city_name == 'Hai Phong City':
            return np.stack((
                np.array(city_lvl_df['%cnd_bw'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range))])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Le Chan District') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Ngo Quyen District') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Hong Bang District') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
            
            )
                , axis=-1)    

        elif city_name == 'Binh Duong':
            return np.stack((
                np.array(city_lvl_df['%cnd_bw'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Thu Dau Mot Town') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Thuan An') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Di An') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
            
            )
                , axis=-1)   
    
        elif city_name == 'Dong Nai':
            return np.stack((
                np.array(city_lvl_df['%cnd_bw'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Bien Hoa City') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])

            )
                , axis=-1)   

        elif city_name == 'Vung Tau':
            return np.stack((
                np.array(city_lvl_df['%cnd_bw'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Vung Tau City') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Ba Ria City') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
            
            )
                , axis=-1)   

        elif city_name == 'Hue City':
            return np.stack((
                np.array(city_lvl_df['%cnd_bw'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Hue City') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])

            )
                , axis=-1)    
        
        elif city_name == 'Can Tho City':
            return np.stack((
                np.array(city_lvl_df['%cnd_bw'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])
                , np.array(district_lvl_df['cnd'][(district_lvl_df['pick_district_name'] == 'Ninh Kieu District') & (district_lvl_df['created_date'] >= from_date) & (district_lvl_df['timeslot'].isin(time_range)) & (district_lvl_df['created_date'] <= date_picked)])

            )
                , axis=-1)
    
    def hover_template():
        if city_name == 'Hai Phong City':
            return ["<b>BW impact</b>: %{customdata[0]: .1%}<br>"
            'Le Chan District</b>: %{customdata[1]}<br>' +
            'Ngo Quyen District</b>: %{customdata[2]}<br>' +
            'Hong Bang District</b>: %{customdata[3]}<br>' +
            "<extra></extra>"][0]
        
        elif city_name == 'Binh Duong':
            return ["<b>BW impact</b>: %{customdata[0]: .1%}<br>"
            'Thu Dau Mot Town</b>: %{customdata[1]}<br>' +
            'Thuan An</b>: %{customdata[2]}<br>' +
            'Di An</b>: %{customdata[3]}<br>' +
            "<extra></extra>"][0]

        elif city_name == 'Dong Nai':
            return ["<b>BW impact</b>: %{customdata[0]: .1%}<br>"
            'Bien Hoa City</b>: %{customdata[1]}<br>' +
            "<extra></extra>"][0]

        elif city_name == 'Vung Tau':
            return ["<b>BW impact</b>: %{customdata[0]: .1%}<br>"
            'Vung Tau City</b>: %{customdata[1]}<br>' +
            'Ba Ria City</b>: %{customdata[2]}<br>' +
            "<extra></extra>"][0]

        elif city_name == 'Hue City':
            return ["<b>BW impact</b>: %{customdata[0]: .1%}<br>"
            'Hue City</b>: %{customdata[1]}<br>' +
            "<extra></extra>"][0]
        
        elif city_name == 'Can Tho City':
            return ["<b>BW impact</b>: %{customdata[0]: .1%}<br>"
            'Ninh Kieu District</b>: %{customdata[1]}<br>' +
            "<extra></extra>"][0]        
    
    fig = make_subplots(rows=2, cols=2,
                    row_heights=[0.2, 0.8],
                    column_widths=[0.1, 0.1],
                    shared_yaxes=True,
                    shared_xaxes=True,
                    horizontal_spacing = 0.01,
                    vertical_spacing = 0.01)
    fig.add_trace(go.Bar(x=city_lvl_df['timeslot'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (city_lvl_df['created_date'] <= date_picked)], 
                         y=city_lvl_df['cnd'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (city_lvl_df['created_date'] <= date_picked)], 
                         name = 'CND by timeslot'), row = 1, col = 1)
    fig.add_trace(
        go.Heatmap(
            y = days_in_year,
            x = timeslot,
            z = data_days,
            # customdata = custom_data(),
            text=text,
            texttemplate="%{text}", 
            # hovertemplate=hover_template(),
            hoverinfo="text",
            xgap=0, # this
            ygap=0, # and this is used to make the grid-like apperance
            showscale=False,
            colorscale = 'reds',
        ), row = 2, col = 1
    )
    
    fig.add_trace(go.Bar(x=city_lvl_df['cnd'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (city_lvl_df['created_date'] <= date_picked)], 
                     y=city_lvl_df['created_date'][(city_lvl_df['pick_city_name'] == city_name) & (city_lvl_df['created_date'] >= from_date) & (city_lvl_df['timeslot'].isin(time_range)) & (city_lvl_df['created_date'] <= date_picked)], 
                     name = 'CND by date',
                    orientation='h'), row = 2, col = 2)
    
    fig.update_layout(barmode = 'stack',
        autosize=True,
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        yaxis=dict(
            showline = False, showgrid = False, zeroline = False, 
            # autorange="reversed",
            tickvals=days_in_year,
            tickformat="%b %d\n%a"
        ),
        xaxis=dict(
            showline=True,
            # autorange="reversed",
            side='top',
            # title="Date",
            tickvals=timeslot
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        showlegend = True
        ,
        plot_bgcolor=('rgb(255,255,255)') #making grid appear white
    )
    
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
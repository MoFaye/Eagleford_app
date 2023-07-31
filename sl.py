import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data
from datetime import date
import requests
from streamlit_lottie import st_lottie

st.set_page_config(page_title="Eagle Ford Play Analysis App", layout='wide')

hide_github_icon = """
#GithubIcon {
  visibility: hidden;
}
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

animation_url ='https://raw.githubusercontent.com/MoFaye/Eagleford_app/main/animation_lk9g19p3.json'
read_animation = requests.get(animation_url)
animation = read_animation.json()
st_lottie(animation, speed=1,
          height=250,
          key="initial")

row0_1, _, row0_2 = st.columns(
    (2, 0.1, 1)
)
row0_1.title("Visual Analysis of the Eagle Ford Play")

with row0_2:
    row0_2.subheader(
        "A Streamlit web app Developed by Mohammad Alfayez"
    )

_, row1_1, _ = st.columns((0.1, 3.2, 0.1))

with row1_1:
    st.write("")
    st.write("")
    st.markdown(
        "Welcome to my Eagle Ford analysis web app developed by Streamlit and Altair. "
        "The purpose of this app is to analyze different aspects of the play represented by the below tabs. "
        "It includes: a general Eagle Ford overview, a geological analysis, production trends, and completion "
        "analysis. Data is downsampled to 25% to ensure app responsiveness")

df = pd.read_csv("https://raw.githubusercontent.com/MoFaye/Eagleford_app/main/EF_data.csv")
#df = df.sample(frac=0.1, random_state=1)
df["drilling_start_date"] = pd.to_datetime(df["drilling_start_date"]).dt.date

# create normalized frac fluid, proppant wieght, and cost by lateral length
df["norm_fracture_fluid"] = df['fracture_fluid__ugl'] / df['lateral_length__ft']
df["norm_proppant"] = df['proppant__lbs'] / df['lateral_length__ft']
df["norm_total_cost"] = df['total_cost__ud'] / df['lateral_length__ft']

# create fluid type column
df['GOR'] = df['cum30_gas__mcf'] * 1000 / df['cum30_oil__bl']
df.loc[df['GOR'] > 200000, 'GOR'] = 200000
df["Fluid_type"] = "Black Oil"
df.loc[df['GOR'] > 2500, "Fluid_type"] = "Volatie Oil"
df.loc[df['GOR'] > 5000, "Fluid_type"] = "Gas Condensate"
df.loc[df['GOR'] > 100000, "Fluid_type"] = "Gas"
df.loc[df['GOR'].isnull(), "Fluid_type"] = "Null"

color_cat = [
    "#83c9ff",
    "#0068c9",
    "#ffabab",
    "#ff2b2b",
    "#7defa1",
    "#29b09d",
    "#ffd16a",
    "#ff8700",
    "#6d3fc0",
    "#d5dae5"]

sub_plays = ['Black Oil',
             'Hawkville Condensate',
             'Karnes Trough',
             'Maverick Condensate',
             'Northeast Oil',
             'Edwards Condensate',
             'Other Eagle Ford',
             'Southwest Gas',
             'Maverick Oil',
             'Southeast Gas']

fluid_type = [["Black Oil",
               "Volatie Oil",
               "Gas Condensate",
               "Gas",
               ],
              ['darkgreen',
               'lightgreen',
               'yellow',
               'darkred',
               ]]

st.divider()
with st.expander("**Press here to view filters**"):
    _, row_filter1, _, row_filter2, _ = st.columns((0.1, 1, 0.1, 1, 0.1))

    with row_filter1:

        sample_size = st.slider('Choose well Sample size: ', 0.1, 1.0, 0.25)

        df = df.sample(frac=sample_size, random_state=1)

        sub_filter = st.multiselect(
            '**Select sub-plays you are interested in:**',
            sub_plays,
            sub_plays
        )

        df = df[df['sub_play_name'].isin(sub_filter)]

        fluid_type_filter = st.multiselect(
            '**Select HC fluid type:**',
            fluid_type[0],
            fluid_type[0]
        )

        df = df[df['Fluid_type'].isin(fluid_type_filter)]

        tvd_slider = st.slider(
            '**Select the range of True Vertical Depth**',
            min_value=0,
            max_value=20000,
            value=(0, 20000)
        )

        df = df[(df['tvd__ft'] > tvd_slider[0])
                & (df['tvd__ft'] < tvd_slider[1])]

    with row_filter2:
        min_date = date.fromisoformat('2009-01-01')  # str to datetime
        max_date = date.fromisoformat('2023-01-01')
        value = (min_date, max_date)

        date_slider = st.slider(
            '**Select the range of drilled wells dates:**',
            min_value=min_date,
            max_value=max_date,
            value=value)

        df = df[(df['drilling_start_date'] > date_slider[0])
                & (df['drilling_start_date'] < date_slider[1])]

        lateral_slider = st.slider(
            '**Select the range of lateral length**',
            min_value=0,
            max_value=18000,
            value=(0, 18000)
        )

        df = df[(df['lateral_length__ft'] > lateral_slider[0])
                & (df['lateral_length__ft'] < lateral_slider[1])]

        pw_slider = st.slider(
            '**Select the range of Proppant Weight Concentration**',
            min_value=0,
            max_value=5000,
            value=(0, 5000)
        )

        df = df[(df['norm_proppant'] > pw_slider[0])
                & (df['norm_proppant'] < pw_slider[1])]

        ff_slider = st.slider(
            '**Select the range of Frac Fluid Concentration**',
            min_value=0,
            max_value=4000,
            value=(0, 4000)
        )

        df = df[(df['norm_fracture_fluid'] > ff_slider[0])
                & (df['norm_fracture_fluid'] < ff_slider[1])]

states = alt.topo_feature(data.us_10m.url,
                          feature='states'
                          )

xmin, xmax, ymin, ymax = (
    df['tophole_longitude__deg'].min(),
    df['tophole_longitude__deg'].max(),
    df['tophole_latitude__deg'].min(),
    df['tophole_latitude__deg'].max()
)

extent = {
    "type": "Feature",
    "geometry": {"type": "Polygon",
                 "coordinates": [[
                     [xmax, ymax],
                     [xmax, ymin],
                     [xmin, ymin],
                     [xmin, ymax],
                     [xmax, ymax]]]
                 },
    "properties": {}
}

# -- map size ------
map_width = 500
map_height = 800
# -- map size ------
r_width = 500
r_height = 300

background = alt.Chart(states).mark_geoshape(
    fill='gray',
    stroke='white',
    clip=True,
    tooltip=False,
).project('albersUsa',
          fit=extent
          ).properties(
    width=map_width,
    height=map_height
)

# -----page 1------
map_select = alt.selection_interval(name='map_select',
                                    resolve="intersect"
                                    )

count_select = alt.selection_point(name='count_select',
                                   encodings=['y'],
                                   resolve="intersect"
                                   )

time_select = alt.selection_interval(name="time_select",
                                     encodings=['x'],
                                     resolve="intersect",
                                     value=2009
                                     )

well_count_title = alt.TitleParams("Well Count by Sub-Play",
                                   anchor="middle",
                                   fontSize=20,
                                   )

subplay_well_count = alt.Chart(df,
                               title=well_count_title
                               ).mark_bar(size=15
                                          ).encode(
    x=alt.X('count(Name):Q',
            title="Well Count").scale(clamp=False),
    y=alt.Y('sub_play_name:N',
            title="Eagle FOrd Sub-Play").sort('-x'),
    color=alt.condition(count_select,
                        alt.Color('sub_play_name:N',
                                  scale=alt.Scale(
                                      domain=sub_plays,
                                      range=[
                                          "#83c9ff",
                                          "#0068c9",
                                          "#ffabab",
                                          "#ff2b2b",
                                          "#7defa1",
                                          "#29b09d",
                                          "#ffd16a",
                                          "#ff8700",
                                          "#6d3fc0",
                                          "#d5dae5"])
                                  ),
                        alt.value('grey'),
                        legend=None)
).properties(
    width=r_width,
    height=r_height
).add_params(
    count_select
).transform_filter(
    map_select
).transform_filter(
    time_select
).interactive()

points_title = alt.TitleParams("Eagle Ford Map of Well Locations",
                               anchor="middle",
                               fontSize=20,
                               )

points = alt.Chart(df,
                   title=points_title
                   ).mark_circle(
    size=10,
    color='steelblue'
).encode(
    longitude='tophole_longitude__deg:Q',
    latitude='tophole_latitude__deg:Q',
    color=alt.condition(map_select,
                        'sub_play_name:N',
                        alt.value('darkgrey'),
                        legend=None),
    tooltip=['sub_play_name',
             'tophole_longitude__deg',
             'tophole_latitude__deg']
).properties(
    width=map_width,
    height=map_height
).add_params(
    map_select
).transform_filter(
    count_select
).transform_filter(
    time_select
).interactive()

drill_time_title = alt.TitleParams("Wells Drilled Quarterly",
                                   anchor="middle",
                                   fontSize=20,
                                   )

drill_time = alt.Chart(data=df,
                       title=drill_time_title
                       ).mark_area().encode(
    x=alt.X('yearquarter(drilling_start_date):T',
            title='Time (Quarter)',
            # scale=alt.Scale(domain=[2009, 2022])
            ),
    y=alt.Y('count(Name):Q',
            title='Well count'),
    color=alt.Color('sub_play_name')
).properties(
    width=r_width,
    height=r_height
).add_params(
    time_select
).transform_filter(
    'year(datum.drilling_start_date) >= 2009'
).transform_filter(
    count_select
).transform_filter(
    map_select
)

overview_viz = alt.hconcat(background + points,
                           subplay_well_count & drill_time,
                           ).configure_concat(
    spacing=20
).configure(
    background='#262730',
    font="sans-serif",
    fieldTitle="verbal",
    autosize={"type": "fit", "contains": "padding"},
    title={
        "align": "left",
        "anchor": "start",
        "color": "#fafafa",
        "fontWeight": 600,
        "fontSize": 16,
        "orient": "top",
        "offset": 26},
).configure_axis(
    labelFontSize=12,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    labelFontStyle="normal",
    titleFontWeight=400,
    titleFontSize=14,
    titleColor="#e6eaf1",
    titleFontStyle="normal",
    ticks=False,
    gridColor="#31333F",
    domain=False,
    domainWidth=1,
    domainColor="#31333F",
    labelFlush=True,
    labelFlushOffset=1,
    labelBound=False,
    labelLimit=100,
    titlePadding=16,
    labelPadding=16,
    labelSeparation=4,
    labelOverlap=True
)

# ----- Page 2 -----
map2_width = 880
map2_height = 500
tvd_background = alt.Chart(states).mark_geoshape(
    fill='gray',
    stroke='white',
    clip=True,
    tooltip=False,
).project('albersUsa',
          fit=extent
          ).properties(
    width=map2_width,
    height=map2_height
)

tvd_title = alt.TitleParams("Eagle Ford Map of Well True Vertical Depth",
                            anchor="middle",
                            fontSize=20,
                            )

tvd = alt.Chart(df, title=tvd_title).mark_circle(
    size=10,
    color='steelblue'
).encode(
    longitude='tophole_longitude__deg:Q',
    latitude='tophole_latitude__deg:Q',
    color=alt.Color('tvd__ft:Q',
                    scale=alt.Scale(scheme='redblue', domain=[5000, 15000])),
    tooltip=['tvd__ft',
             'tophole_longitude__deg',
             'tophole_latitude__deg']
).properties(
    width=map2_width,
    height=map2_height
).interactive()

tvd_map = tvd_background + tvd

tvd_map = (tvd_map | alt.Chart().mark_point()).configure(
    background='#262730'
)

top_operators = df.groupby('operator_name'
                           )['api_number'].count(
).sort_values(
    ascending=False)

top_operators_list = top_operators[:5].index.copy()
top_operators_list = [x for x in top_operators_list]

df_op = df[df['operator_name'].isin(top_operators_list)]
df_op = df_op[df_op['norm_fracture_fluid'] < 4000]  # filter outliers
df_op = df_op[df_op['norm_proppant'] < 5000]  # filter outliers

op_ll_vio_dropdown = alt.binding_select(
    options=[None] + top_operators_list,
    labels=['All'] + top_operators_list,
    name='Select Operator: '
)

op_vio_select = alt.selection_single(
    fields=['operator_name'],
    bind=op_ll_vio_dropdown,
)

line_select = alt.selection_interval(name="line_select",
                                     encodings=['x'],
                                     resolve="intersect"
                                     )

op_ll_vio = alt.Chart(data=df_op).transform_density(
    'lateral_length__ft',
    as_=['lateral_length__ft',
         'density'],
    groupby=['operator_name']
).mark_area(
    orient='horizontal',
    tooltip=False
).properties(
    width=75,
).encode(
    x=alt.X('density:Q',
            sort=alt.EncodingSortField(field="operator_name",
                                       op="mean",
                                       order='ascending'),
            title=""
            )
    .stack('center')
    .impute(None)
    .title(None)
    .axis(labels=False,
          values=[0],
          grid=False,
          ticks=True),
    y=alt.Y('lateral_length__ft:Q'),
    color=alt.condition(op_vio_select,
                        alt.Color('operator_name:N',
                                  scale=alt.Scale(
                                      domain=top_operators_list,
                                      range=[
                                          "#83c9ff",
                                          "#0068c9",
                                          "#ffabab",
                                          "#ff2b2b",
                                          "#7defa1",
                                      ])
                                  ),
                        alt.value("grey")
                        ),
    column=alt.Column('operator_name:N',
                      title=None
                      ).spacing(0
                                ).header(titleOrient='bottom',
                                         labelOrient='bottom',
                                         labelPadding=0,
                                         labelColor='white',
                                         labelFontSize=15,
                                         labelAngle=0,
                                         labels=False)
)

ll_line = alt.Chart(df_op).mark_line().encode(
    x=alt.X('year(drilling_start_date):T',
            ),
    y=alt.Y('mean(lateral_length__ft):Q',
            title='Lateral Length (ft)'),
    color=alt.value("#FD8D14")
).add_params(
    op_vio_select
).transform_filter(
    op_vio_select
)

ll_band = alt.Chart(df_op).mark_errorband(extent='iqr').encode(
    x='year(drilling_start_date):T',
    y=alt.Y('lateral_length__ft'
            ).title(''),
    color=alt.value("#FD8D14")
).add_params(
    op_vio_select
).transform_filter(
    op_vio_select
)

ll_time = (ll_band + ll_line
           ).transform_filter(
    'year(datum.drilling_start_date) >= 2009'
).properties(
    width=275,
)

op_ff_vio = alt.Chart(data=df_op).transform_density(
    'norm_fracture_fluid',
    as_=['norm_fracture_fluid',
         'density'],
    groupby=['operator_name']
).mark_area(
    orient='horizontal',
    tooltip=False
).properties(
    width=150,
).encode(
    x=alt.X('density:Q',
            sort=alt.EncodingSortField(field="operator_name",
                                       op="mean",
                                       order='ascending'),
            title="",
            )
    .stack('center')
    .impute(None)
    .title(None)
    .axis(labels=False,
          values=[0],
          grid=False,
          ticks=True),
    y=alt.Y('norm_fracture_fluid:Q'),
    color=alt.condition(op_vio_select,
                        alt.Color('operator_name:N',
                                  scale=alt.Scale(
                                      domain=top_operators_list,
                                      range=[
                                          "#83c9ff",
                                          "#0068c9",
                                          "#ffabab",
                                          "#ff2b2b",
                                          "#7defa1",
                                      ])
                                  ),
                        alt.value("grey")
                        ),
    column=alt.Column('operator_name:N',
                      title=None)
    .spacing(0)
    .header(titleOrient='bottom',
            labelOrient='bottom',
            labelPadding=0,
            labelColor='white',
            labelFontSize=15,
            labels=False)
).properties(
    width=75,
)

ff_line = alt.Chart(df_op).mark_line().encode(
    x=alt.X('year(drilling_start_date):T',
            ),
    y=alt.Y('mean(norm_fracture_fluid):Q',
            title='Frac Fluid (gl/ft)'),
    color=alt.value("#FD8D14")
).add_params(
    op_vio_select
).transform_filter(
    op_vio_select
)

ff_band = alt.Chart(df_op).mark_errorband(extent='iqr').encode(
    x='year(drilling_start_date):T',
    y=alt.Y('norm_fracture_fluid'
            ).title(''),
    color=alt.value("#FD8D14")
).add_params(
    op_vio_select
).transform_filter(
    op_vio_select
)

ff_time = (ff_band + ff_line
           ).transform_filter(
    'year(datum.drilling_start_date) >= 2009'
).properties(
    width=275,
)

op_pw_vio = alt.Chart(data=df_op).transform_density(
    'norm_proppant',
    as_=['norm_proppant',
         'density'],
    groupby=['operator_name']
).mark_area(
    orient='horizontal',
    tooltip=False
).properties(
    width=150,
).encode(
    alt.X('density:Q',
          sort=alt.EncodingSortField(field="operator_name",
                                     op="mean",
                                     order='ascending'),
          title=""
          )
    .stack('center')
    .impute(None)
    .title(None)
    .axis(labels=False,
          values=[0],
          grid=False,
          ticks=True),
    y=alt.Y('norm_proppant:Q'),
    color=alt.condition(op_vio_select,
                        alt.Color('operator_name:N',
                                  scale=alt.Scale(
                                      domain=top_operators_list,
                                      range=[
                                          "#83c9ff",
                                          "#0068c9",
                                          "#ffabab",
                                          "#ff2b2b",
                                          "#7defa1",
                                      ])
                                  ),
                        alt.value("grey")
                        ),
    column=alt.Column('operator_name:N',
                      title=None)
    .spacing(0)
    .header(titleOrient='bottom',
            labelOrient='bottom',
            labelPadding=0,
            labelColor='white',
            labelFontSize=15,
            labels=False)
).properties(
    width=75,
)

op_ll_title = alt.TitleParams("Well Lateral Length by Operator",
                              anchor="middle",
                              fontSize=20,
                              )

op_ll_vio = (op_ll_vio | ll_time
             ).configure(
    background='#262730',
    font="sans-serif",
    fieldTitle="verbal",
    autosize={"type": "fit", "contains": "padding"},
    title={
        "align": "left",
        "anchor": "start",
        "color": "#fafafa",
        "fontWeight": 600,
        "fontSize": 16,
        "orient": "top",
        "offset": 26},
).configure_axis(
    labelFontSize=12,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    labelFontStyle="normal",
    titleFontWeight=400,
    titleFontSize=14,
    titleColor="#e6eaf1",
    titleFontStyle="normal",
    ticks=False,
    gridColor="#31333F",
    domain=False,
    domainWidth=1,
    domainColor="#31333F",
    labelFlush=True,
    labelFlushOffset=1,
    labelBound=False,
    labelLimit=100,
    titlePadding=16,
    labelPadding=16,
    labelSeparation=4,
    labelOverlap=True
).configure_legend(
    labelFontSize=14,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    titleFontSize=14,
    titleFontWeight=400,
    titleFontStyle="normal",
    titleColor="#e6eaf1",
    titlePadding=12,
    labelPadding=16,
    columnPadding=8,
    rowPadding=4,
    padding=7,
    symbolStrokeWidth=4,
).properties(title=op_ll_title)

op_ff_title = alt.TitleParams("Fracture Fluid Concentration by Operator",
                              anchor="middle",
                              fontSize=20,
                              )

op_ff_vio = (op_ff_vio | ff_time
             ).configure(
    background='#262730',
    font="sans-serif",
    fieldTitle="verbal",
    autosize={"type": "fit", "contains": "padding"},
    title={
        "align": "left",
        "anchor": "start",
        "color": "#fafafa",
        "fontWeight": 600,
        "fontSize": 16,
        "orient": "top",
        "offset": 26},
).configure_axis(
    labelFontSize=12,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    labelFontStyle="normal",
    titleFontWeight=400,
    titleFontSize=14,
    titleColor="#e6eaf1",
    titleFontStyle="normal",
    ticks=False,
    gridColor="#31333F",
    domain=False,
    domainWidth=1,
    domainColor="#31333F",
    labelFlush=True,
    labelFlushOffset=1,
    labelBound=False,
    labelLimit=100,
    titlePadding=16,
    labelPadding=16,
    labelSeparation=4,
    labelOverlap=True
).configure_legend(
    labelFontSize=14,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    titleFontSize=14,
    titleFontWeight=400,
    titleFontStyle="normal",
    titleColor="#e6eaf1",
    titlePadding=12,
    labelPadding=16,
    columnPadding=8,
    rowPadding=4,
    padding=7,
    symbolStrokeWidth=4
).properties(title=op_ff_title)

pw_line = alt.Chart(df_op).mark_line().encode(
    x=alt.X('year(drilling_start_date):T',
            ),
    y=alt.Y('mean(norm_proppant):Q',
            title='Proppant wt. (lb/ft)'),
    color=alt.value("#FD8D14")
).add_params(
    op_vio_select
).transform_filter(
    op_vio_select
)

pw_band = alt.Chart(df_op
                    ).mark_errorband(extent='iqr'
                                     ).encode(
    x='year(drilling_start_date):T',
    y=alt.Y('norm_proppant'
            ).title(''),
    color=alt.value("#FD8D14")
).add_params(
    op_vio_select
).transform_filter(
    op_vio_select
)

op_pw_title = alt.TitleParams("Proppant Weight Concentration by Operator",
                              anchor="middle",
                              fontSize=20,
                              )

pw_time = (pw_band + pw_line
           ).transform_filter(
    'year(datum.drilling_start_date) >= 2009'
).properties(
    width=275,
)

op_pw_vio = (op_pw_vio | pw_time
             ).configure(
    background='#262730',
    font="sans-serif",
    fieldTitle="verbal",
    autosize={"type": "fit", "contains": "padding"},
    title={
        "align": "left",
        "anchor": "start",
        "color": "#fafafa",
        "fontWeight": 600,
        "fontSize": 16,
        "orient": "top",
        "offset": 26},
).configure_axis(
    labelFontSize=12,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    labelFontStyle="normal",
    titleFontWeight=400,
    titleFontSize=14,
    titleColor="#e6eaf1",
    titleFontStyle="normal",
    ticks=False,
    gridColor="#31333F",
    domain=False,
    domainWidth=1,
    domainColor="#31333F",
    labelFlush=True,
    labelFlushOffset=1,
    labelBound=False,
    labelLimit=100,
    titlePadding=16,
    labelPadding=16,
    labelSeparation=4,
    labelOverlap=True
).configure_legend(
    labelFontSize=14,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    titleFontSize=14,
    titleFontWeight=400,
    titleFontStyle="normal",
    titleColor="#e6eaf1",
    titlePadding=12,
    labelPadding=16,
    columnPadding=8,
    rowPadding=4,
    padding=7,
    symbolStrokeWidth=4
).properties(title=op_pw_title)

# ----- Page 3 -----

map3_width = 580
map3_height = 500

pie_select = alt.selection_point(name='pie_select',
                                 resolve="intersect",
                                 fields=['Fluid_type']
                                 )

pvt_background = alt.Chart(states).mark_geoshape(
    fill='gray',
    stroke='white',
    clip=True,
    tooltip=False,
).project('albersUsa',
          fit=extent
          ).properties(
    width=map3_width,
    height=map3_height
)

pvt_title = alt.TitleParams("Eagle Ford Map of Hydrocarbon Fluid Type",
                            anchor="middle",
                            fontSize=20,
                            )

pvt = alt.Chart(df,
                title=pvt_title
                ).mark_circle(
    size=10,
    color='steelblue'
).encode(
    longitude='tophole_longitude__deg:Q',
    latitude='tophole_latitude__deg:Q',
    color=alt.condition(map_select,
                        alt.Color('Fluid_type:N',
                                  scale=alt.Scale(
                                      domain=fluid_type[0],
                                      range=fluid_type[1])),
                        alt.value('darkgrey')
                        ),
    tooltip=['tvd__ft',
             'tophole_longitude__deg',
             'tophole_latitude__deg']
).properties(
    width=map3_width,
    height=map3_height
).add_params(map_select
).transform_filter(pie_select
).interactive()

pvt_map = pvt_background + pvt

pie_chart = alt.Chart(df, ).transform_joinaggregate(
    Total='count()',
).encode(
    theta=alt.Theta("count():Q").stack(True),
    color=alt.condition(pie_select,
                        alt.Color("Fluid_type:N"),
                        alt.value("darkgrey"))
).mark_arc(outerRadius=150,
           innerRadius=75,
           padAngle=0.1,
           cornerRadius=8
).add_params(pie_select)

pie_text = pie_chart.mark_text(radius=115,
                               fill="darkblue"
).encode(alt.Text('count():Q')
)

pie = (pie_chart + pie_text).transform_filter(map_select)

dist_width = 300

eur_mbe_dist = alt.Chart(df
                         ).mark_bar(
    binSpacing=0,
    color='orange'
).encode(
    x=alt.X('eur_total__mbe:Q',
            scale=alt.Scale(domain=[0, 3],
                            clamp=True),
            title='Total EUR (MBE)',
            ).bin(maxbins=100),
    y=alt.Y('count()').stack(None),
).properties(width=dist_width
).transform_filter(pie_select
).transform_filter(map_select)

eur_oil_dist = alt.Chart(df
                         ).mark_bar(
    binSpacing=0,
    color="lightgreen"
).encode(
    alt.X('eur_oil__mbl:Q',
          scale=alt.Scale(domain=[0, 1.5], clamp=True),
          title='Oil EUR (MBL)',
          ).bin(maxbins=100),
    alt.Y('count()').stack(None),
).properties(width=dist_width
).transform_filter(pie_select
).transform_filter(map_select)

eur_gas_dist = alt.Chart(df
                         ).mark_bar(
    binSpacing=0,
    color='darkred'
).encode(
    alt.X('eur_gas__bf3:Q',
          scale=alt.Scale(domain=[0, 5],
                          clamp=True),
          title='Gas EUR (BSCF)',
          ).bin(maxbins=100),
    alt.Y('count()').stack(None),
).properties(width=dist_width
).transform_filter(pie_select
).transform_filter(map_select)

eur_dist = eur_gas_dist | eur_oil_dist | eur_mbe_dist

pvt_map = ((pvt_map | pie) & eur_dist).configure(
    background='#262730',
    font="sans-serif",
    fieldTitle="verbal",
    autosize={"type": "fit", "contains": "padding"},
    title={
        "align": "left",
        "anchor": "start",
        "color": "#fafafa",
        "fontWeight": 600,
        "fontSize": 16,
        "orient": "top",
        "offset": 26},
).configure_axis(
    labelFontSize=12,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    labelFontStyle="normal",
    titleFontWeight=400,
    titleFontSize=14,
    titleColor="#e6eaf1",
    titleFontStyle="normal",
    ticks=False,
    gridColor="#31333F",
    domain=False,
    domainWidth=1,
    domainColor="#31333F",
    labelFlush=True,
    labelFlushOffset=1,
    labelBound=False,
    labelLimit=100,
    titlePadding=16,
    labelPadding=16,
    labelSeparation=4,
    labelOverlap=True
).configure_legend(
    labelFontSize=14,
    labelFontWeight=400,
    labelColor="#e6eaf1",
    titleFontSize=14,
    titleFontWeight=400,
    titleFontStyle="normal",
    titleColor="#e6eaf1",
    titlePadding=12,
    labelPadding=16,
    columnPadding=8,
    rowPadding=4,
    padding=7,
    symbolStrokeWidth=4,
)


# -------------------
def round_costume(val, closest=10):
    val = round(val / closest, 0) * closest
    return int(val)


listTabs = ["Eagle Ford Overview",
            "Completion Analysis",
            "Production Analysis"]
whitespace = 20

overview_tab, Comp_tab, prod_tab = st.tabs([s.center(whitespace, "\u2001") for s in listTabs])

with overview_tab:
    st.header("Analyzing drilling activities in Eagle Ford ")
    st.markdown("Important general metrics based on your filtering:")

    _, col1, col2, col3, _ = st.columns((1, 1, 1, 1, 1))
    col1.metric(label="Wells Drilled",
                value=len(df.index))

    col2.metric(label="Average Well Cost",
                value=f"${round(df['total_cost__ud'].mean() / 10 ** 6, 1)} MM")

    col3.metric(label="Average Well IP90 Cum.",
                value=f"{round(df['cum90_total__be'].mean() / 10 ** 3, 1)}K BOE")
    _, row2_1, _ = st.columns((0.1, 3.2, 0.1))

    with row2_1:
        st.markdown(""
                    "The below visualizations consists of interactive charts showcasing a map of Eagle Ford wells "
                    "along with the drilling activities over time and the well count per sub-play. Try to select"
                    "one of the charts based on what you want to focus on"
                    "")
        st.altair_chart(overview_viz,
                        theme="streamlit",
                        use_container_width=True)

with Comp_tab:
    st.header("Analyzing Well Completion data")
    st.markdown("Important completion metrics based on your filtering:")
    _, col1, col2, col3, _ = st.columns((1, 1, 1, 1, 1))

    col1.metric(label="Average Lateral Length",
                value=f"{round_costume(df['lateral_length__ft'].mean())} ft")

    col2.metric(label="Average Frac Fluid Vol.",
                value=f"{round_costume(df['norm_fracture_fluid'].mean())} gal/ft")

    col3.metric(label="Average Proppant Wt.",
                value=f"{round_costume(df['norm_proppant'].mean())} lb/ft")
    _, row2_1, _ = st.columns((0.1, 3.2, 0.1))
    with row2_1:
        st.markdown("The below visualizations showcases comparisons on lateral length, frac fluid, and proppant "
                    "weight for the top five operators with the highest well count")

        st.altair_chart(tvd_map,
                        theme="streamlit",
                        use_container_width=True
                        )

        st.altair_chart(op_ll_vio,
                        theme="streamlit",
                        use_container_width=True
                        )

        st.altair_chart(op_ff_vio,
                        theme="streamlit",
                        use_container_width=True
                        )

        st.altair_chart(op_pw_vio,
                        theme="streamlit",
                        use_container_width=True)

with prod_tab:
    st.header("Analyzing Well Production Data")
    st.markdown("Important production metrics based on your filtering:")

    _, col1, col2, col3, _ = st.columns((1, 1, 1, 1, 1))
    col1.metric(label="Average EUR",
                value=f"{round(df['eur_total__mbe'].mean(), 2)} MMBOE")

    col2.metric(label="Average Gas Oil Ratio",
                value=f"{round_costume(df['GOR'].mean())} SCF/BL")

    col3.metric(label="Average Revenue ($80 Oil Price)",
                value=f"${round_costume(df['eur_total__mbe'].mean() * 80)} MM")

    _, row2_1, _ = st.columns((0.1, 3.2, 0.1))

    with row2_1:
        st.markdown(""
                    "The below visualizations consists of interactive charts showcasing a map of Eagle Ford wells "
                    "along reservoir fluid type devided into gas, gas condensate, volatile oil, and black oil. In "
                    "addition, the distribution of the estimated ultimate recovery (EUR) is displayed for the gas "
                    "produciton in bilion standard cubic ft (BSCF), oil production in million barrels of oil (MBL), "
                    "and total prodcution in millions in barrels of oil equivalent (MBE). Try selecting"
                    "one of the charts based on what you want to focus on"
                    "")
        st.altair_chart(pvt_map,
                        theme="streamlit",
                        use_container_width=True)

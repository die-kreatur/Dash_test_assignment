import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('games.csv')
df = df[df.Year_of_Release >= 2000].dropna(axis=0)
df['Year_of_Release'] = list(map(int, df.Year_of_Release))

app.layout = html.Div(children=[
    html.H1(children='Games dashboard',
            style={'fontSize': 30}),

    html.Div(children='''
        The dashboard reflects different games characteristics.
        To get started and view games distribution select genre and rating below.
    ''', style={'fontSize': 20}),

    html.Div(children=[
        dcc.Dropdown(
            id='selected_genre',
            options=[
                {'label': genre, 'value': genre} for genre in df.Genre.unique()],
            placeholder='Select a genre',
            multi=True,
            style={'width': '95%'}
        )
    ], style={'width': '50%', 'display': 'inline-block'}),

    html.Div(children=[
        dcc.Dropdown(
            id='selected_rating',
            options=[
                {'label': rating, 'value': rating} for rating in df.Rating.unique()],
            placeholder='Select a rating type',
            multi=True,
            style={'width': '95%'}
        )
    ], style={'width': '50%', 'display': 'inline-block'}),

    html.Div(id='output_container', children=[]),

    html.Div(children=[
        dcc.Graph(id='first_graph')
    ], style={'width': '50%', 'display': 'inline-block'}),

    html.Div(children=[
        dcc.Graph(id='second_graph')
    ], style={'width': '50%', 'display': 'inline-block'}),

    html.Div(children=[
        dcc.RangeSlider(
            id='slider',
            min=df.Year_of_Release.min(),
            max=df.Year_of_Release.max(),
            value=[df.Year_of_Release.min(), 2002],
            step=None,
            marks={str(year): str(year) for year in df.Year_of_Release.unique()}
        )
    ])
])


@app.callback(
    Output('first_graph', 'figure'),
    [Input('selected_genre', 'value'),
    Input('selected_rating', 'value'),
    Input('slider', 'value')]
)
def update_first_graph(selected_genre, selected_rating, selected_year):

    # Dropdowns have multi=True and value=None, so we can get 3 different types of selected_rating and selected_genre variables.
    # If no options are selected in any dropdown we get value=None and to handle it we should display empty graph
    if selected_genre is None or selected_rating is None:
        return {}

    # If only one option is selected we get 'str' type of selected_rating or selected_genre
    # while a few selected options give us a list.
    # To deal with it I'd prefer to convert a string into a list item and work with lists, using df.isin() method,
    # that gets a list as an argument
    if isinstance(selected_genre, str):
        # turns the string into a list element without append method
        selected_genre = selected_genre.split()
    if isinstance(selected_rating, str):
        selected_rating = selected_rating.split()

    df_fig = df.copy()
    df_fig = df_fig[(df_fig.Genre.isin(selected_genre)) &\
        (df_fig.Rating.isin(selected_rating))]
    df_fig = df_fig[(df_fig.Year_of_Release >= selected_year[0]) &\
        (df_fig.Year_of_Release <= selected_year[1])]
    df_fig = df_fig.groupby(['Year_of_Release', 'Platform'], as_index=False).agg({'Genre': 'count'})

    # Some combinations of selected_genre, selected_rating and selected_year give us no elements in games dataframe
    if df_fig.empty:
        return {}

    fig = px.area(df_fig, x='Year_of_Release', y='Genre', line_group='Platform', color='Platform',
        labels={'Genre': 'Number of games', 'Year_of_Release': 'Year of release'},
        title='Games distribution by year of release and platform')

    return fig


@app.callback(
    Output('second_graph', 'figure'),
    [Input('selected_genre', 'value'),
    Input('selected_rating', 'value'),
    Input('slider', 'value')]
)
def update_second_graph(selected_genre, selected_rating, selected_year):

    # The algorithm is the same to the previous function algorithm

    if selected_genre is None or selected_rating is None:
        return {}

    if isinstance(selected_genre, str):
        selected_genre = selected_genre.split()
    if isinstance(selected_rating, str):
        selected_rating = selected_rating.split()

    df_fig = df.copy()
    df_fig = df_fig[(df_fig.Genre.isin(selected_genre)) &\
         (df_fig.Rating.isin(selected_rating))]
    df_fig = df_fig[(df_fig.Year_of_Release >= selected_year[0]) &\
        (df_fig.Year_of_Release <= selected_year[1])]

    if df_fig.empty:
        return {}

    fig = px.scatter(df_fig, x='User_Score', y='Critic_Score', color='Genre',
        labels={'Critic_Score': 'Critic score', 'User_Score': 'User score'},
        title='Critics and users scores')

    return fig


@app.callback(
    Output('output_container', 'children'),
    [Input('selected_genre', 'value'),
    Input('selected_rating', 'value'),
    Input('slider', 'value')]
)
def counting_games(selected_genre, selected_rating, selected_year):

    if selected_genre is None or selected_rating is None:
        return 'The number of selected games is 0'

    if isinstance(selected_genre, str):
        selected_genre = selected_genre.split()
    if isinstance(selected_rating, str):
        selected_rating = selected_rating.split()

    df_fig = df.copy()
    df_fig = df_fig[(df_fig.Genre.isin(selected_genre)) &\
        (df_fig.Rating.isin(selected_rating))]
    df_fig = df_fig[(df_fig.Year_of_Release >= selected_year[0]) &\
        (df_fig.Year_of_Release <= selected_year[1])]

    return f'The number of selected games is {len(df_fig)}'

if __name__ == '__main__':
    app.run_server(debug=True)

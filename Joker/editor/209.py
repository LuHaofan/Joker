import requests
import json
import dash
from dash import dcc
from dash import html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__)
URL = "https://api.semanticscholar.org/graph/v1/paper/"
citation = "/citations?fields=title,authors"
reference = "/references?fields=title,authors"


def get_citation(paper_id):
    call_url = URL + paper_id + citation
    r = requests.get(call_url)
    data = r.content
    json_dict = json.loads(data)
    citattion_list = []
    for i in json_dict['data']:
        for (x, y) in i.items():
            # print(y['title'])
            citattion_list.append(y['title'])
    return citattion_list


def get_reference(paper_id):
    call_url = URL + paper_id + reference
    r = requests.get(call_url)
    data = r.content
    json_dict = json.loads(data)
    reference_list = []
    for i in json_dict['data']:
        for (x, y) in i.items():
            # print(y['title'])
            reference_list.append(y['title'])

    return reference_list


def draw_graph(paper_id):
    citation_list = get_citation(paper_id)
    refernce_list = get_reference(paper_id)
    element = []
    element.append({'data': {'id': 'center', 'label': 'center'}})
    for i in citation_list:
        element.append({'data': {'id': i, 'label': i}})
        element.append({'data': {'source': 'center', 'target': i}})
    for i in refernce_list:
        element.append({'data': {'id': i, 'label': i}})
        element.append({'data': {'source': i, 'target': 'center'}})
    default_stylesheet = [
        {
            'selector': 'node',
            'style': {
                'background-color': '#00bfff',
                'size':'100px'
                # 'label': 'data(label)'
            }
        }
    ]
    app.layout = html.Div([
        cyto.Cytoscape(
            id='cytoscape-event-callbacks-2',
            elements=element,
            layout={'name': 'breadthfirst'},
            stylesheet=default_stylesheet,
            style={'width': '800px', 'height': '600px'}
        ),
        html.P(id='cytoscape-tapNodeData-output')
    ])

    @app.callback(Output('cytoscape-tapNodeData-output', 'children'),
                  Input('cytoscape-event-callbacks-2', 'tapNodeData'))
    def displayTapNodeData(data):
        if data:
            return "You recently clicked/tapped the paper: " + data['label']
    app.run_server(debug=True)


print(get_citation("cb13b1b6a37e4080d8c13c5f33694b5aae90abcf"))
print(get_reference("cb13b1b6a37e4080d8c13c5f33694b5aae90abcf"))
draw_graph("cb13b1b6a37e4080d8c13c5f33694b5aae90abcf")

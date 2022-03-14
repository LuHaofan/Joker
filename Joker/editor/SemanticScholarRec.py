import numpy as np
import requests
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from numpy import sin, cos, pi
from scipy.optimize import leastsq
import json
import networkx as nx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from bokeh.plotting import figure, save, from_networkx
from bokeh.models import Circle, MultiLine, Range1d
import igraph
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go

class SSRec:
    def __init__(self, doi, keywords, num_rec):
        self.url_base = "http://api.semanticscholar.org/graph/v1/paper/search?query="
        self.num_rec = num_rec
        self.rec_list = None
        self.doi = doi
        self.paperId = None
        self.embedding = []
        self.keywords = keywords
        self.reduced_embedding = None
        self.classes = []
        self.title = None
        self.ref_list = []
        self.cite_list = []

    def setDOI(self, doi):
        self.doi = doi
    
    def setKeywords(self, keywords):
        self.keywords = keywords

    def save_state(self):
        with open("state.json", 'w') as f:
            json.dump({
                "paperId": self.paperId,
                "rec_list": list(self.rec_list),
                "embedding": self.embedding,
                "reduced_embedding": list(self.reduced_embedding),
                "classes": self.classes
            }, f)

    def getSelfEmbedding(self):
        qry = "https://api.semanticscholar.org/v1/paper/"+self.doi
        response = requests.get(qry).json()
        self.paperId = response["url"].split("/")[-1]
        self.title = response["title"]
        qry = "https://api.semanticscholar.org/graph/v1/paper/"+self.paperId+"?fields=embedding"
        response = requests.get(qry).json()
        self.embedding = response["embedding"]["vector"]

    def getRec(self):
        kw_str = ""
        for kw in self.keywords:
            kw_str += kw.lower()
            kw_str += "+"
        offset = 0
        limit = self.num_rec
        qry = self.url_base + kw_str[:-1]+"&offset={}&limit={}&fields=title,authors,url".format(offset,limit)
        self.rec_list = requests.get(qry).json()["data"]
        self.getRecEmbeddings()

    def getRecEmbeddings(self):
        i = 0
        total = len(self.rec_list)
        while (i < total):
            dic = self.rec_list[i]
            paperId = dic["paperId"]
            qry = "https://api.semanticscholar.org/graph/v1/paper/"+paperId+"?fields=embedding"
            print("{}/{} Querying: {}".format(i, total, dic["title"]))
            response = requests.get(qry).json()
            if "error" in response.keys():
                print(response["error"])
            else:
                embedding = response["embedding"]["vector"]
                self.rec_list[i]["embedding"] = embedding
                i+=1

    def CosineSimilarity(self, vec1, vec2):
        return np.dot(vec1, vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))

    def getSimilarityScores(self):
        for i in range(len(self.rec_list)):
            sim_score = self.CosineSimilarity(self.rec_list[i]["embedding"], self.embedding)
            self.rec_list[i]["similarity"] = sim_score


    def sortRecListBySimilarity(self):
        self.rec_list = sorted(self.rec_list, key=lambda d: d['similarity'], reverse=True) 

    def dumpToFile(self):
        tmp = []
        for i in range(len(self.rec_list)):
            tmp.append({
                "title": self.rec_list[i]["title"],
                "authors": self.rec_list[i]["authors"],
                "url": self.rec_list[i]["url"],
                "similarity": self.rec_list[i]["similarity"]
            })
        with open("editor/static/editor/json/query.json", 'w') as f:
            json.dump({"data": tmp}, f)

    def query(self):
        self.getSelfEmbedding()
        self.getRec()
        self.getReference()
        self.getCitations()
        self.drawReferenceGraph()
        self.drawCitationGraph()
        self.getSimilarityScores()
        self.sortRecListBySimilarity()
        self.dumpToFile()

    def drawSimilarityGraph(self):
        G = nx.Graph()
        G.add_node(0, title = self.title, similarity = 1)
        for i in range(1, len(ssr.rec_list)+1):
            G.add_node(i, title = ssr.rec_list[i-1]["title"], similarity = ssr.rec_list[i-1]["similarity"])
            G.add_edge(0, i, similarity = ssr.rec_list[i-1]["similarity"])
        pos = nx.spring_layout(G,weight='similarity')
        adjusted_node_size = dict([(i, ssr.rec_list[i-1]["similarity"]*50) for i in range(1, len(ssr.rec_list)+1)])
        adjusted_node_size[0] = 1*50
        nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)
        title = 'Similarity Graph'
        size_by_this_attribute = 'adjusted_node_size'
        color_by_this_attribute = 'adjusted_node_size'
        #Establish which categories will appear when hovering over each node
        color_palette = Reds8
        HOVER_TOOLTIPS = [("title", "@title"), ("similarity", "@similarity")]

        #Create a plot — set dimensions, toolbar, and title
        plot = figure(tooltips = HOVER_TOOLTIPS,
                    tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                    x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1), title=title)

        #Create a network graph object with spring layout
        # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
        network_graph = from_networkx(G, pos, scale=10, center=(0, 0))
        #Set node sizes and colors according to node degree (color as spectrum of color palette)
        minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
        maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
        #Set node size and color
        network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))

        #Set edge opacity and width
        network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

        #Add network graph to the plot
        plot.renderers.append(network_graph)

        # show(plot)
        save(plot, filename="editor/static/editor/tmp/sim_graph.html")

    def getReference(self):
        qry = "https://api.semanticscholar.org/graph/v1/paper/{}/references?fields=title,authors".format(self.paperId)
        response = requests.get(qry).json()
        ref = response["data"]
        self.ref_list = [item["citedPaper"] for item in ref]

    def getCitations(self):
        qry = "https://api.semanticscholar.org/graph/v1/paper/{}/citations?fields=title,authors".format(self.paperId)
        response = requests.get(qry).json()
        cite = response["data"]
        self.cite_list = [item["citingPaper"] for item in cite]

    def drawReferenceGraph(self):
        nr_vertices = len(self.ref_list)+1
        v_label = [self.title]
        for item in self.ref_list:
            title = item["title"]
            authors = ""
            for a in item["authors"]:
                authors+=a["name"]
                authors+=", "
            v_label.append(title+" | "+authors[:-2])

        G = Graph.Tree(nr_vertices, nr_vertices-1) # 2 stands for children number
        lay = G.layout('rt')

        position = {k: lay[k] for k in range(nr_vertices)}
        Y = [lay[k][1] for k in range(nr_vertices)]
        M = max(Y)

        es = EdgeSeq(G) # sequence of edges
        E = [e.tuple for e in G.es] # list of edges

        L = len(position)
        Xn = [position[k][0] for k in range(L)]
        Yn = [2*M-position[k][1] for k in range(L)]
        Xe = []
        Ye = []
        for edge in E:
            Xe+=[position[edge[0]][0],position[edge[1]][0], None]
            Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]

        labels = v_label
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Xe,
                        y=Ye,
                        mode='lines',
                        line=dict(color='rgb(210,210,210)', width=1),
                        hoverinfo='none'
                        ))
        fig.add_trace(go.Scatter(x=Xn,
                        y=Yn,
                        mode='markers',
                        name='bla',
                        marker=dict(symbol='circle-dot',
                                        size=18,
                                        color='#6175c1',    #'#DB4551',
                                        line=dict(color='rgb(50,50,50)', width=1)
                                        ),
                        text=labels,
                        hoverinfo='text',
                        opacity=0.8
                        ))
        axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
                    zeroline=False,
                    showgrid=False,
                    showticklabels=False,
                    )

        fig.update_layout(title= 'Reference Graph',
                    font_size=12,
                    showlegend=False,
                    xaxis=axis,
                    yaxis=axis,
                    margin=dict(l=40, r=40, b=85, t=100),
                    hovermode='closest',
                    plot_bgcolor='rgb(248,248,248)'
                    )
        fig.write_html("editor/static/editor/tmp/reference.html")

    def drawCitationGraph(self):
        if len(self.cite_list) == 0:
            G = nx.Graph()
            G.add_node(0, title = self.title, similarity = 1)
            pos = nx.spring_layout(G,weight='similarity')
            title = 'Citation Graph'
            #Establish which categories will appear when hovering over each node
            color_palette = Reds8
            HOVER_TOOLTIPS = [("title", "@title")]

            #Create a plot — set dimensions, toolbar, and title
            plot = figure(tooltips = HOVER_TOOLTIPS,
                        tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                        x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1), title=title)

            #Create a network graph object with spring layout
            # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
            network_graph = from_networkx(G, pos, scale=10, center=(0, 0))
            #Set node size and color
            network_graph.node_renderer.glyph = Circle(size=50, fill_color="Blue")

            #Set edge opacity and width
            network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

            #Add network graph to the plot
            plot.renderers.append(network_graph)

            save(plot, filename="editor/static/editor/tmp/citation.html")
            return

        nr_vertices = len(self.cite_list)+1
        v_label = [self.title]
        for item in self.cite_list:
            title = item["title"]
            authors = ""
            for a in item["authors"]:
                authors+=a["name"]
                authors+=", "
            v_label.append(title+" | "+authors[:-2])

        G = Graph.Tree(nr_vertices, nr_vertices-1) # 2 stands for children number
        lay = G.layout('rt')

        position = {k: lay[k] for k in range(nr_vertices)}
        Y = [lay[k][1] for k in range(nr_vertices)]
        M = max(Y)

        es = EdgeSeq(G) # sequence of edges
        E = [e.tuple for e in G.es] # list of edges

        L = len(position)
        Xn = [position[k][0] for k in range(L)]
        Yn = [2*M-position[k][1] for k in range(L)]
        Xe = []
        Ye = []
        for edge in E:
            Xe+=[position[edge[0]][0],position[edge[1]][0], None]
            Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]

        labels = v_label
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Xe,
                        y=Ye,
                        mode='lines',
                        line=dict(color='rgb(210,210,210)', width=1),
                        hoverinfo='none'
                        ))
        fig.add_trace(go.Scatter(x=Xn,
                        y=Yn,
                        mode='markers',
                        name='bla',
                        marker=dict(symbol='circle-dot',
                                        size=18,
                                        color='#6175c1',    #'#DB4551',
                                        line=dict(color='rgb(50,50,50)', width=1)
                                        ),
                        text=labels,
                        hoverinfo='text',
                        opacity=0.8
                        ))
        axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
                    zeroline=False,
                    showgrid=False,
                    showticklabels=False,
                    )

        fig.update_layout(title= 'Reference Graph',
                    font_size=12,
                    showlegend=False,
                    xaxis=axis,
                    yaxis=axis,
                    margin=dict(l=40, r=40, b=85, t=100),
                    hovermode='closest',
                    plot_bgcolor='rgb(248,248,248)'
                    )
        fig.write_html("editor/static/editor/tmp/citation.html")


if __name__ == "__main__":
    ssr = SSRec(doi = "10.1145/3422604.3425951", keywords=['wifi', 'sensing', 'localization'], num_rec= 30)
    ssr.query()
    ssr.drawReferenceGraph()
    # ssr.drawCitationGraph()
    # ssr.drawSimilarityGraph()


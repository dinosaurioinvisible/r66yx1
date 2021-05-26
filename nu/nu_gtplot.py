
import numpy as np
import networkx as nx
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def netplot(glx,arrows=False):

    # define figure
    fig = make_subplots(rows=1,cols=2)

    # genotype network graph
    gx = nx.DiGraph()
    for txi in glx.txs:
        for i,tx in enumerate(txi):
            gx.add_node(glx,pos=(tx,???))
            if i>0:
                gx.add_edge(txi[i-1],tx)
    # behavior/environment
    bx = nx.DiGraph()
    beh = [512*a+b for a,b in zip(glx.hm,glx.hs)]
    for i,[bi,ei] in enumerate(zip(beh,glx.he)):
        bx.add_node(bi,pos=(bi,ei))
        if i > 0:
            bx.add_edge(beh[i-1],beh[i])

    # network graph: edges
    bx_data = make_traces(bx)
    gx_data = make_traces(gx)

    # create graphs
    fig.add_trace(bx_data[0],row=1,col=1)
    fig.add_trace(bx_data[1],row=1,col=1)
    fig.add_trace(gx_data[0],row=1,col=2)
    fig.add_trace(gx_data[1],row=1,col=2)
    fig.update_layout(title="glider mappings: timesteps={}, known dashes={}, cycles={}".format(len(glx.states),len(glx.kdp),len(glx.cycles)),
                    titlefont_size=16,
                    showlegend=False,
                    margin=dict(b=20,l=10,r=10,t=30),
                    xaxis=dict(showgrid=False,zeroline=False,showticklabels=True),
                    yaxis=dict(showgrid=False,zeroline=False,showticklabels=True))
    fig.show()


def make_traces(ox):
    xedges,yedges = [],[]
    for edge in ox.edges():
        try:
            x0,y0 = ox.nodes[edge[0]]['pos']
            x1,y1 = ox.nodes[edge[1]]['pos']
            xedges.extend([x0,x1,None])
            yedges.extend([y0,y1,None])
        except:
            print("edges/nodes problem:")
            print("edge = {}".format(edge))
            print("node[edge[0]]={}, node[edge[1]]={}".format(ox.nodes[edge[0]],ox.nodes[edge[1]]))
    edge_trace = go.Scatter(x=xedges,y=yedges,
                            line=dict(
                                width=0.5,
                                color='#888'),
                            mode='lines')
    # network graph: nodes
    xnodes,ynodes= [],[]
    for node in ox.nodes():
        x,y = ox.nodes[node]['pos']
        xnodes.append(x)
        ynodes.append(y)
    node_adjs = []
    for node,adjs in enumerate(ox.adjacency()):
        node_adjs.append(len(adjs[1]))
    node_trace = go.Scatter(x=xnodes,y=ynodes,
                    mode='markers',
                    marker=dict(
                        showscale=True,
                        colorscale="YlGnBu",
                        reversescale=True,
                        color=node_adjs,
                        size=10,
                        colorbar=dict(
                            thickness=15,
                            title="recurrences",
                            xanchor='left',
                            titleside='right'),
                        line_width=2))
    return edge_trace,node_trace






###

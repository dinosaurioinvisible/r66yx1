
import numpy as np
import plotly.graph_objects as go
import networkx as nx

def netplot(glx,xy="states",arrows=False):

    # genotype network and graph
    gx = nx.DiGraph()
    if xy=="responses":
        for bi,ri in zip(glx.hb,glx.hr):
            gx.add_node(bi,pos=(ri,bi))
        gx.add_edges_from(glx.txs)
    elif xy=="states":
        for ti,tx in enumerate(glx.txs):
            gx.add_node(ti,pos=(tx[0],tx[1]))
            if ti>0:
                gx.add_edge(ti-1,ti)

    # graph: edges
    xedges,yedges = [],[]
    for edge in gx.edges():
        try:
            x0,y0 = gx.nodes[edge[0]]['pos']
            x1,y1 = gx.nodes[edge[1]]['pos']
        except:
            import pdb; pdb.set_trace()
        xedges.extend([x0,x1,None])
        yedges.extend([y0,y1,None])
    edge_trace = go.Scatter(x=xedges,y=yedges,
                            line=dict(
                                width=0.5,
                                color='#888'),
                            mode='lines')
    # graph: nodes
    xnodes,ynodes= [],[]
    for node in gx.nodes():
        x,y = gx.nodes[node]['pos']
        xnodes.append(x)
        ynodes.append(y)
    node_adjs = []
    for node,adjs in enumerate(gx.adjacency()):
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
                            title="genotype transitions",
                            xanchor='left',
                            titleside='right'),
                        line_width=2))
    # plot graph
    graph = go.Figure(data=[edge_trace,node_trace],
                    layout=go.Layout(
                    title="genotype graph mapping, timesteps={}, recurrences={}".format(len(glx.txs),glx.recs),
                    titlefont_size=16,
                    showlegend=False,
                    #hovermode='closest',
                    margin=dict(b=20,l=10,r=10,t=30),
                    xaxis=dict(showgrid=False,zeroline=False,showticklabels=True),
                    yaxis=dict(showgrid=False,zeroline=False,showticklabels=True)))
    # arrows
    if arrows:
        for edge in gx.edges():
            graph.add_annotation(
                x = gx.nodes[edge[1]]['pos'][0],
                y = gx.nodes[edge[1]]['pos'][1],
                ax = gx.nodes[edge[0]]['pos'][0],
                ay = gx.nodes[edge[0]]['pos'][1],
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,arrowsize=3,arrowwidth=1,arrowcolor="black")
    graph.show()



###

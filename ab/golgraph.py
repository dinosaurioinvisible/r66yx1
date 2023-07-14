import numpy as np 
import networkx as nx
import plotly.graph_object as go

# analisys of the dynamics of a small grid of GoL 

# create grid
def grid_dynamics(dims=(3,3)):
    array_width = dims[0]*dims[1]
    combinations = 2**(array_width)
    # state transitions
    grid_txs = np.zeros(combinations)
    for sti in range(combinations):
        # convert int into matrix/grid
        grid = np.flip(list(np.binary_repr(i).zfill(array_width))).astype(float).reshape(dims)
        # just for speed
        if np.sum(grid) <= 2:
            grid_txs[sti] = 0
        # GoL step function
        else:
            next_grid = np.zeros(dims)
            for i in range(dims[0]):
                for j in range(dims[1]):
                    # active cells in neighborhood 
                    nbsum = np.sum(grid[max(0,i-1):i+2,max(0,j-1):j+2] - grid[i,j]
                    ij = 1 if (nbsum==2 and grid[i,j]==1) or nbsum==3 else 0
                    next_grid[i,j] = ij
            grid_txs[sti] = np.sum([ij<<e for e,ij in enumerate(np.flip(next_grid.flatten()))])
    return grid_txs

def mkgraph(grid_txs):
    gx = nx.DiGraph()
    # make nodes 
    for sti,stx in enumerate(grid_txs):
        # ncells = np.sum(np.array(list(np.binary_repr(sti))))
        freq = np.sum(np.where(grid_txs==stx,1,0))
        gx.add_node(sti,pos=(sti,freq))
    # make edges
    for sti,stx in enumerate(grid_txs):
        gx.add_edge(sti,stx)

    # convert data for plotting
    

    # plot
    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='GoL grid dynamics',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[dict(
                        text="?",
                        showarrow=True,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002)],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()
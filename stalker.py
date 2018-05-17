#!/usr/bin/env python

import plotly.plotly as py
from plotly.graph_objs import *
import plotly.tools as pt
import networkx as nx
from networkx.readwrite import json_graph
import operator


def stalker_graph(data):
    nodes = data['nodes']
    links = data['edges']
    for i in links:
        i['value'] = 'init'
    M = nx.Graph()
    M = nx.Graph(
        [(i['source'], i['target'], {'value': i['value']}) for i in links])
    for i in nodes:
        node = i['id']
        M.add_node(node, salle=i['salle'])
        M.add_node(node, group=i['group'])
        M.add_node(node, name=i['name'])
        M.add_node(node, istrain=i['istrain'])
        M.add_node(node, age=i['age'])
        M.add_node(node, lat=i['lat'])
        M.add_node(node, lon=i['lon'])
        M.add_node(node, id=i['id'])
    return M


def stalker_evolution(M):
    # Common Neighbors
    CN = [(e[0], e[1], len(list(nx.common_neighbors(M, e[0], e[1]))))
          for e in nx.non_edges(M)]
    CN.sort(key=operator.itemgetter(2), reverse=True)

    # Jaccard coef
    jaccard = list(nx.jaccard_coefficient(M))
    jaccard.sort(key=operator.itemgetter(2), reverse=True)

    # Resource Allocation index
    RA = list(nx.resource_allocation_index(M))
    RA.sort(key=operator.itemgetter(2), reverse=True)

    # Adamic-Adar index
    AA = list(nx.adamic_adar_index(M))
    AA.sort(key=operator.itemgetter(2), reverse=True)

    # Preferential Attachement
    PA = list(nx.preferential_attachment(M))
    PA.sort(key=operator.itemgetter(2), reverse=True)

    # Community Common Neighbors !!! requires graph to have node attribute: 'community' !!!
    # CCN = list(nx.cn_soundarajan_hopcroft(M))
    # CCN.sort(key=operator.itemgetter(2), reverse = True)

    # Community Resource Allocation !!! requires graph to have node attribute: 'community' !!!
    # CRA = list(nx.ra_index_soundarajan_hopcroft(M))
    # CRA.sort(key=operator.itemgetter(2), reverse = True)

    # ###################### Prediction of future edge formation ####################

    FM = M
    for i in PA[0:int(0.1 * len(M.edges()))]:
        FM.add_edge(i[0], i[1], value='new')

    for i in CN[0:int(0.1 * len(M.edges()))]:
        FM.add_edge(i[0], i[1], value='new')

    return FM


def stalker_layout(FM):
    pos = nx.fruchterman_reingold_layout(FM, dim=3)
    lay = list()
    for i in pos.values():
        lay.append(list(i))
    return pos, lay


def stalker_centrality(FM, mesure):
    pos = stalker_layout(FM)[0]

    ulti = {}
    for i in pos.keys():
        ulti[i] = list(pos[i])

    # Eigenvector centrality criteria (normalised)
    Geigen = nx.eigenvector_centrality(FM)
    for i in Geigen:
        ulti[i].append(float(Geigen[i]) / max(Geigen.values()))

    # Closeness centrality
    Gclose = nx.closeness_centrality(FM)
    for i in Gclose:
        ulti[i].append(Gclose[i])

    # Betweeness centrality
    Gbetween = nx.betweenness_centrality(FM)
    for i in Gbetween:
        ulti[i].append(Gbetween[i])

    if mesure == "eigenvector":
        return [i[-3] for i in ulti.values()]
    elif mesure == "closeness":
        return [i[-2] for i in ulti.values()]
    elif mesure == "betweenness":
        return [i[-1] for i in ulti.values()]


def stalker_plot(FM, mesure):
    mapbox_access_token = 'pk.eyJ1IjoiY2xlaXR1cyIsImEiOiJjamgwZ2c1a3Yxc3dtMnFtb2ptdDR5ZWs0In0.sjZdn45v32AojmWGWIN9Tg'
    # pt.set_credentials_file(username='cleitus', api_key='LN8W33LMo7kMNz2LU7Ce')
    pt.set_credentials_file(username='zhening', api_key='9LICBZ681YiPTiSZCuFX')

    N = len(FM.nodes())
    labels = [i[1]['name'] for i in FM.nodes(data=True)]

    # ############################# 2d Map Plot #####################################

    # Nodes and Edges coordinates
    Xv = [k[1]['lat'] for k in FM.nodes(data=True)]
    Yv = [k[1]['lon'] for k in FM.nodes(data=True)]
    Xed = []
    Yed = []
    Xned = []
    Yned = []
    for edge in FM.edges():
        Xed += [FM.nodes(data=True)[edge[0]]['lat'],
                FM.nodes(data=True)[edge[1]]['lat'], None]
        Yed += [FM.nodes(data=True)[edge[0]]['lon'],
                FM.nodes(data=True)[edge[1]]['lon'], None]

    for edge in [(i[0], i[1]) for i in list(FM.edges(data=True)) if i[2]['value'] == 'new']:
        Xned += [FM.nodes(data=True)[edge[0]]['lat'],
                 FM.nodes(data=True)[edge[1]]['lat'], None]
        Yned += [FM.nodes(data=True)[edge[0]]['lon'],
                 FM.nodes(data=True)[edge[1]]['lon'], None]

    data = [
        Scattermapbox(
            lat=Xed,
            lon=Yed,
            mode='lines',
            line=dict(color='rgb(125,125,125)', width=1),
            hoverinfo='none'
        ),
        Scattermapbox(
            lat=Xned,
            lon=Yned,
            mode='lines',
            line=dict(color='rgb(158,18,130)', width=1),
            hoverinfo='none'
        ),
        Scattermapbox(
            lat=Xv,
            lon=Yv,
            mode='markers',
            name=mesure,
            marker=dict(size=10,

                        color=stalker_centrality(FM, mesure),

                        colorscale='Viridis'
                        ),
            text=labels,
            hoverinfo='text'
        )
    ]

    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=sum(Xv) / N,
                lon=sum(Yv) / N
            ),
            pitch=0,
            zoom=13
        ),
    )

    fig = dict(data=data, layout=layout)
    plot_url = py.plot(fig, filename=mesure + '_fb', auto_open=False)

    # ############################# 3d Layout Plot #####################################

    pos, lay = stalker_layout(FM)

    # Nodes and Edges coordinates
    Xv = [lay[k][0] for k in range(N)]  # x-coordinates of nodes
    Yv = [lay[k][1] for k in range(N)]  # y-coordinates
    Zv = [lay[k][2] for k in range(N)]  # z-coordinates
    Xed = []
    Yed = []
    Zed = []
    Xned = []
    Yned = []
    Zned = []
    for edge in FM.edges():
        Xed += [pos[edge[0]][0], pos[edge[1]][0], None]
        Yed += [pos[edge[0]][1], pos[edge[1]][1], None]
        Zed += [pos[edge[0]][2], pos[edge[1]][2], None]

    for edge in [(i[0], i[1]) for i in list(FM.edges(data=True)) if i[2]['value'] == 'new']:
        Xned += [pos[edge[0]][0], pos[edge[1]][0], None]
        Yned += [pos[edge[0]][1], pos[edge[1]][1], None]
        Zned += [pos[edge[0]][2], pos[edge[1]][2], None]

    trace1 = Scatter3d(x=Xed,
                       y=Yed,
                       z=Zed,
                       mode='lines',
                       line=Line(color='rgb(125,125,125)', width=1),
                       hoverinfo='none'
                       )

    trace2 = Scatter3d(x=Xv,
                       y=Yv,
                       z=Zv,
                       mode='markers',
                       name=mesure,
                       marker=Marker(symbol='dot',

                                     color=stalker_centrality(FM, mesure),

                                     size=6, colorbar=ColorBar(
                               title=''
                           ),
                                     colorscale='Viridis',
                                     line=Line(color='rgb(158,18,130)', width=0.5)
                                     ),
                       text=labels,  # node Labels
                       hoverinfo='text'
                       )

    data = Data([trace1, trace2])
    plot_url = py.plot(data, filename=mesure + '_fb_3d', auto_open=False)

    print('Stalker mode')
    return

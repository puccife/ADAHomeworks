import igraph as ig
import networkx as nx
import collections
from plotly.offline import init_notebook_mode, plot, iplot
import plotly.graph_objs as go
from plotly.graph_objs import *

def network_graph(cluster_country,jurisdiction_count):
    ## Input:
        # cluster_country : Contains the countries and to which cluster they belong to
        # jurisdiction_count : The count of each country corresponding to a jurisdiction
    ## Output:
        # A network visualization

    # Graph parameters
    data_graph = {}
    country_number_map = {}
    data_graph['links'] = []
    data_graph['nodes'] = []
    countries_number = []
    jurisdiction_number = []
    left_out_index = []

    # Cluster number for each country
    groups = list(cluster_country['cluster'].values)
    # Origin countries
    origin_countries = list(cluster_country.reset_index()['origin'].values)

    # Extract countries that are avialable in our clusters.
    filtered_jurds_count = jurisdiction_count.loc[jurisdiction_count.index.get_level_values('countries').isin(origin_countries)]
    # Extract the jurisdictions [ used to create edges]
    jurisdictions =  filtered_jurds_count.index.get_level_values('jurisdiction_description').values
    # Extract the countries [ used to create edges ]
    countries = filtered_jurds_count.index.get_level_values('countries').values


    #test_diff = set(origin_countries) - set(countries)

    # Countries that are in the jurisdictions but not mentioned in the set of origin countries.
    remaining_countries = list(set(jurisdictions) - set(origin_countries))

    # Adding the remaining countries.
    origin_countries.extend(remaining_countries)
    # Assigning a new group value for those countries.
    groups.extend([4]*len(remaining_countries))

    # Creating a number map for each country available.
    for i,country in enumerate(origin_countries):
        country_number_map[country]=i
    # Creating a sequential number array representing the countries.
    for country in countries:
        countries_number.append(country_number_map[country])
    # Creating a sequential number array representing the jurisdictions.
    for jurisdiction in jurisdictions:
        jurisdiction_number.append(country_number_map[jurisdiction])
    # Creating the edges.
    for i,jurisdiction in enumerate(jurisdictions):
        temp_dict = {}
        temp_dict['source'] = jurisdiction_number[i]
        temp_dict['target'] = countries_number[i]
        data_graph['links'].append(temp_dict)
    # Creating the nodes.
    for i,group in enumerate(groups):
        temp_dict = {}
        temp_dict['group'] = group
        temp_dict['name'] = origin_countries[i]
        data_graph['nodes'].append(temp_dict)
    # Number of edges.
    L=len(data_graph['links'])
    # Creating the edges of the graph.
    Edges=[(data_graph['links'][k]['source'], data_graph['links'][k]['target']) for k in range(L)]
    # Creating the graph.
    G=ig.Graph(Edges, directed=False)

    labels=[]
    group=[]

    # Extracting the labels and group of each node.
    for node in data_graph['nodes']:
        labels.append(node['name'])
        group.append(node['group'])
    # Creating the layout of the graph in 3d .
    layt=G.layout('kk', dim=3)
    # Number of nodes.
    N=len(data_graph['nodes'])

    # Resetting the filtered dataframe to apply counter function on.
    the_counter_df = filtered_jurds_count.reset_index()
    # Filter the dataframe so that we don't include self loops.
    the_counter_df = the_counter_df[the_counter_df['jurisdiction_description'] != the_counter_df['countries']]
    # Get a count of how many times each jurisdiction was repeated.
    counter_jurisdictions = collections.Counter(the_counter_df['jurisdiction_description'].values)
    # Get a count of how many times each country was repeated.
    counter_origin = collections.Counter(the_counter_df['countries'].values)
    # Creating the label that will be used to hover over the nodes.
    for i,label in enumerate(labels):
        labels[i] = 'Country: ' + labels[i] + ' || Connections: ' + str(counter_jurisdictions[label]+counter_origin[label])\
                        + ' || Group: ' + str(groups[i])
    # x-coordinates of nodes
    Xn=[layt[k][0] for k in range(N)]
    # y-coordinates of nodes
    Yn=[layt[k][1] for k in range(N)]
    # z-coordinates of nodes
    Zn=[layt[k][2] for k in range(N)]
    Xe=[]
    Ye=[]
    Ze=[]
    for e in Edges:
        # x-coordinates of edge ends
        Xe+=[layt[e[0]][0],layt[e[1]][0], None]
        # y-coordinates of edge ends
        Ye+=[layt[e[0]][1],layt[e[1]][1], None]
        # z-coordinates of edge ends
        Ze+=[layt[e[0]][2],layt[e[1]][2], None]

    # Information of the edges used in the 3D plot.
    trace1=Scatter3d(x=Xe,
                   y=Ye,
                   z=Ze,
                   mode='lines',
                   line=Line(color='rgb(125,125,125)', width=1),
                   hoverinfo='none'
                   )
    # Information of the nodes used in the 3D plot.
    trace2=Scatter3d(x=Xn,
                   y=Yn,
                   z=Zn,
                   mode='markers',
                   name='Countries',
                   marker=Marker(symbol='dot',
                                 size=6,
                                 color=group,
                                 colorscale='Viridis',
                                 line=Line(color='rgb(50,50,50)', width=0.5)
                                 ),
                   text=labels,
                   hoverinfo='text'
                   )

    # Axis properties
    axis=dict(showbackground=False,
              showline=False,
              zeroline=False,
              showgrid=False,
              showticklabels=False,
              title=''
              )
    # Plot layout
    layout = Layout(
             title="Network of  (3D visualization)",
             width=1000,
             height=1000,
             showlegend=False,
             scene=Scene(
             xaxis=XAxis(axis),
             yaxis=YAxis(axis),
             zaxis=ZAxis(axis),
            ),
         margin=Margin(
            t=100
        ),
        hovermode='closest',
            )

    data=Data([trace1, trace2])
    fig=Figure(data=data, layout=layout)

    iplot(fig, filename='Les-Miserables')

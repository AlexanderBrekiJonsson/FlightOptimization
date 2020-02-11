import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# This function imports flight data from pandas dataframe into a networkx graph.
# If two flights depart and arrive on the same day only the flight with the
# higer revenue will be added to the graph. The other flight will be added to
# a new dataframe rem_flights. Function returns an updated networkx graph and
# pandas dataframe including all flights that were not added to the graph.
def LoadDataIntoGraph(Graph, df):
    rem_flight_list = []
    for index, row in df.iterrows():
        FlightNumber = row['FlightNumber']
        DepDay = row['departureInt']
        AvaDay = row['avalibleInt']
        Price = row['Price']
        DepLocation = row['departureLocation']
        ReturnLocation = row['returnDestination']

        # Check if the two days already have an edge
        if G.has_edge(DepDay, AvaDay) == True:
            # If price for current edge is greater then overwrite edge
            if Price > G[DepDay][AvaDay]['weight']:
                rem_flight_list.append(G[DepDay][AvaDay]['Label'])
                G.add_edge(DepDay, AvaDay, weight=Price, Label=FlightNumber, dep = DepLocation, Ret = ReturnLocation)
            else:
                rem_flight_list.append(FlightNumber)
        else:
            G.add_edge(DepDay, AvaDay, weight=Price, Label=FlightNumber, dep = DepLocation, Ret = ReturnLocation)

        rem_flights = df[df['FlightNumber'].isin(rem_flight_list)]

    return Graph, rem_flights

# This function adds a wait edge (edge with revenue=0) between all nodes that
# are not connected by flights.
def addWaitEdges(Graph):
    for InnerNode in Graph:
        for OuterNode in Graph:
            if OuterNode-InnerNode > 0:
                if Graph.has_edge(InnerNode, OuterNode) == False:
                    Graph.add_edge(InnerNode, OuterNode, weight=0, Label='WaitEdge', dep='', Ret='')
    return Graph

# This function removes the longest path from the graph
def removeLongestPath(Graph):
    LongestP = nx.dag_longest_path(G, weight='weight')
    for x in range(0, len(LongestP)-1):
        if G[LongestP[x]][LongestP[x+1]]['Label'] == 'WaitEdge':
            pass
        else:
            Graph.add_edge(LongestP[x], LongestP[x+1], weight=0, Label='WaitEdge', dep='', Ret='')
            #Flights.append(str(G[LongestP[x]][LongestP[x+1]]['Label']))
    return Graph

# This function returns a list of flights in the longest path
def FlightsInLongestPath(G):
    Flights = []
    LongestP = nx.dag_longest_path(G, weight='weight')
    for x in range(0, len(LongestP)-1):
        if G[LongestP[x]][LongestP[x+1]]['Label'] == 'WaitEdge':
            pass
        else:
            Flights.append(str(G[LongestP[x]][LongestP[x+1]]['Label']))
    return Flights

# This function prints the longest path
def LongestPathPrint(G):
    LongestP = nx.dag_longest_path(G, weight='weight')
    for x in range(0, len(LongestP)-1):
        if G[LongestP[x]][LongestP[x+1]]['Label'] == 'WaitEdge':
            print('Wait from day: ' + str(LongestP[x]) + ' to ' + str(LongestP[x+1]))
        else:
            print('FlightNumber: ' + str(G[LongestP[x]][LongestP[x+1]]['Label']) + ', From: ' + str(G[LongestP[x]][LongestP[x+1]]['dep']) + ', To: ' + str(G[LongestP[x]][LongestP[x+1]]['Ret']))

# This function retruns the revenue from the longest path
def LongestPathRevenue(G):
    LongestPL = nx.dag_longest_path_length(G, weight='weight')
    return LongestPL

if __name__ == "__main__":
    # load data from CSV file
    df = pd.read_csv("flightData.csv", encoding = "ISO-8859-1", delimiter = ',')

    # Create graph object
    G = nx.DiGraph()

    # load flight data to graph
    G, rem_flights = LoadDataIntoGraph(G, df)

    # add wait edges to graph
    G = addWaitEdges(G)

    # find revenue and flights in longest path for plane 1
    print('----- Revenue for plane 1 -----')
    print(LongestPathRevenue(G))
    print(FlightsInLongestPath(G))
    print()

    # remove longest path load remaining flights and find revenue for plane 2
    G = removeLongestPath(G)
    G, rem_flights = LoadDataIntoGraph(G, rem_flights)
    G = addWaitEdges(G)
    print('----- Revenue for plane 2 -----')
    print(LongestPathRevenue(G))
    print(FlightsInLongestPath(G))
    print()

    # remove longest path load remaining flights and find revenue for plane 3
    G = removeLongestPath(G)
    G, rem_flights = LoadDataIntoGraph(G, rem_flights)
    G = addWaitEdges(G)
    print('----- Revenue for plane 3 -----')
    print(LongestPathRevenue(G))
    print(FlightsInLongestPath(G))
    print()

    # remove longest path load remaining flights and find revenue for plane 4
    G = removeLongestPath(G)
    G, rem_flights = LoadDataIntoGraph(G, rem_flights)
    G = addWaitEdges(G)
    print('----- Revenue for plane 4 -----')
    print(LongestPathRevenue(G))
    print(FlightsInLongestPath(G))
    print()

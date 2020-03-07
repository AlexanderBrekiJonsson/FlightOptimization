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
        if Graph.has_edge(DepDay, AvaDay) == True:
            # If price for current edge is greater then overwrite edge
            if Price > Graph[DepDay][AvaDay]['weight']:
                rem_flight_list.append(Graph[DepDay][AvaDay]['Label'])
                Graph.add_edge(DepDay, AvaDay, weight=Price, Label=FlightNumber, dep = DepLocation, Ret = ReturnLocation)
            else:
                rem_flight_list.append(FlightNumber)
        else:
            Graph.add_edge(DepDay, AvaDay, weight=Price, Label=FlightNumber, dep = DepLocation, Ret = ReturnLocation)

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
    LongestP = nx.dag_longest_path(Graph, weight='weight')
    for x in range(0, len(LongestP)-1):
        if Graph[LongestP[x]][LongestP[x+1]]['Label'] == 'WaitEdge':
            pass
        else:
            Graph.add_edge(LongestP[x], LongestP[x+1], weight=0, Label='WaitEdge', dep='', Ret='')
            #Flights.append(str(G[LongestP[x]][LongestP[x+1]]['Label']))
    return Graph

# This function returns a list of flights in the longest path
def FlightsInLongestPath(Graph):
    Flights = []
    LongestP = nx.dag_longest_path(Graph, weight='weight')
    for x in range(0, len(LongestP)-1):
        if Graph[LongestP[x]][LongestP[x+1]]['Label'] == 'WaitEdge':
            pass
        else:
            Flights.append(str(Graph[LongestP[x]][LongestP[x+1]]['Label']))
    return Flights

# This function prints the longest path
def LongestPathPrint(Graph):
    LongestP = nx.dag_longest_path(Graph, weight='weight')
    for x in range(0, len(LongestP)-1):
        if Graph[LongestP[x]][LongestP[x+1]]['Label'] == 'WaitEdge':
            print('Wait from day: ' + str(LongestP[x]) + ' to ' + str(LongestP[x+1]))
        else:
            print('FlightNumber: ' + str(Graph[LongestP[x]][LongestP[x+1]]['Label']) + ', From: ' + str(Graph[LongestP[x]][LongestP[x+1]]['dep']) + ', To: ' + str(Graph[LongestP[x]][LongestP[x+1]]['Ret']))

# This function retruns the revenue from the longest path
def LongestPathRevenue(Graph):
    LongestPL = nx.dag_longest_path_length(Graph, weight='weight')
    return LongestPL

def isRightFormat(df):
    std_cols = ['departureLocation', 'destination', 'departureDate', 'returnDestination', 'returnDate', 'Price']
    df_cols = df.columns
    if set(df_cols).issuperset(std_cols): return True
    else: return False

def prepare_df(df, TurnaroundTime):
    new_df = df
    new_df['FlightNumber'] = new_df.index

    new_df['departureDate'] = pd.to_datetime(new_df['departureDate'])
    new_df['departureInt'] = ((new_df['departureDate'] - pd.to_datetime('1970-01-01')).dt.total_seconds())/(24*60*60)
    min_date = new_df['departureInt'].min()
    new_df['departureInt'] = ((new_df['departureInt'] - min_date + 1)).astype(int)

    new_df['returnDate'] = pd.to_datetime(new_df['returnDate'])
    new_df['returnInt'] = ((new_df['returnDate'] - pd.to_datetime('1970-01-01')).dt.total_seconds())/(24*60*60)
    new_df['returnInt'] = ((new_df['returnInt'] - min_date + 1)).astype(int)

    new_df['avalibleInt'] = new_df['returnInt'] + TurnaroundTime


    return df

def solve(df, nr_planes, TurnaroundTime):
    solution_df = pd.DataFrame()

    if isRightFormat(df):
        print('isRightFormat')
        df = prepare_df(df, TurnaroundTime)

        G = nx.DiGraph()
        G, rem_flights = LoadDataIntoGraph(G, df)
        G = addWaitEdges(G)

        for plane_nr in range(1,nr_planes+1):
            path_revenue = LongestPathRevenue(G)
            path = FlightsInLongestPath(G)
            G = removeLongestPath(G)
            G, rem_flights = LoadDataIntoGraph(G, rem_flights)
            G = addWaitEdges(G)
            solution_df = solution_df.append({'Path': path, 'Revenue': path_revenue, 'Plane Number': plane_nr}, ignore_index=True)

    return solution_df[['Plane Number', 'Revenue', 'Path']]

if __name__ == "__main__":
    # load data from CSV file
    df = pd.read_csv("flightDataOrginal.csv", encoding = "ISO-8859-1", delimiter = ',')

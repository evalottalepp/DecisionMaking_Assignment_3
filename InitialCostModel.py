import numpy as np
import gurobipy as gb
from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

class costModel():
    def __init__(self,W,P,cap,U,K,c,f,demand,supply):
        self.W = W
        self.P = P
        self.supply = supply
        self.cap = cap
        self.demand = demand
        self.U = U
        self.K = K
        self.c = c
        self.f = f
        
        self.M = max(self.supply.sum(),self.demand.sum())
        
        self.nLocations = len(self.W) + len(self.P) + len(self.U)
        self.edges = [(i,j) for i in range(self.nLocations) for j in range(self.nLocations)]
        self.bookEdges = [(i,j,k) for i in range(self.nLocations) for j in range(self.nLocations) for k in self.K]

    
    def model(self):

        model = gb.Model('Cost Model')

        X = model.addVars(self.bookEdges, vtype=GRB.INTEGER, lb=0, name = 'X')
        Y = model.addVars(self.edges, vtype=GRB.INTEGER, lb=0, ub=1, name = 'Y')

        model.setObjective(
            gb.quicksum([
                        gb.quicksum([self.c[p,w] * X[p,w,k] for k in self.K]) 
                         + (self.f[p,w] * Y[p,w]) 
                         for p in self.P for w in self.W
                         ]) 
            + gb.quicksum([
                        gb.quicksum([self.c[w,u] * X[w,u,k] for k in self.K]) 
                         + (self.f[w,u] * Y[w,u]) 
                         for u in self.U for w in self.W
                         ])
            , GRB.MINIMIZE
        )


        # Warehouse cannot hold any books
        for w in self.W:
            for k in self.K:
                model.addConstr(
                    gb.quicksum([X[i,w,k] for i in range(self.nLocations)]) 
                    == gb.quicksum([X[w,i,k] for i in range(self.nLocations)])
                )
        
        # Supply of books at printer is held
        for p in self.P:
            for k in self.K:
                model.addConstr(
                    gb.quicksum([X[p,i,k] for i in range(self.nLocations)])
                    <= self.supply[p,k]
                )

        # Demand must be met
        for u in self.U:
            for k in self.K:
                model.addConstr(
                    gb.quicksum([X[i,u,k] for i in range(self.nLocations)])
                    == self.demand[u,k]
                )

        # Cannot send more than handled by warehouse
        for p in self.P:
            for w in self.W:
                model.addConstr(
                    gb.quicksum([X[p,w,k] for k in self.K])
                    <= (self.cap[w] * Y[p,w])
                )
                
                model.addConstr(
                    gb.quicksum([X[p,w,k] for k in self.K])
                    <= (gb.quicksum([self.supply[p,k] for k in self.K])*Y[p,w])
                )

        # Books sent from warehouse are less than capacity and demand
        for w in self.W:
            for u in self.U:
                model.addConstr(
                    gb.quicksum([X[w,u,k] for k in self.K])
                    <= (self.cap[w] * Y[w,u])
                )
                
                model.addConstr(
                    gb.quicksum([X[w,u,k] for k in self.K])
                    <= (gb.quicksum([self.demand[u,k] for k in self.K])*Y[w,u])
                )


            

        ## remove self sending or shipping impossible routes
        for u in self.U:
            for w in self.W:
                model.addConstr(
                    gb.quicksum([X[u,w,k] for k in self.K])
                    == 0
                )
            for u_other in self.U:
                model.addConstr(
                    gb.quicksum([X[u,u_other,k] for k in self.K])
                    == 0
                )
        
        for w in self.W:
            for p in self.P:
                model.addConstr(
                    gb.quicksum([X[w,p,k] for k in self.K])
                    == 0
                )
            for w_other in self.W:
                model.addConstr(
                    gb.quicksum([X[w,w_other,k] for k in self.K])
                    == 0
                )

        for p in self.P:
            for u in self.U:
                model.addConstr(
                    gb.quicksum([X[p,u,k] for k in self.K])
                    == 0
                )
            for p_other in self.P:
                model.addConstr(
                    gb.quicksum([X[p,p_other,k] for k in self.K])
                    == 0
                )

        # remove cross docks
        crossDocks = self.W[2:]
        for c in crossDocks:
            for p in self.P:
                model.addConstr(
                                gb.quicksum([X[p,c,k] for k in self.K])
                                == 0
                                )
            for u in self.U:
                model.addConstr(
                                gb.quicksum([X[c,u,k] for k in self.K])
                                == 0
                                )

        
        model.optimize()

        self.x_values = {key: var.X for key, var in X.items() if var.X > 0}
        self.y_values = {key: var.X for key, var in Y.items() if var.X > 0}

        return model
    

    def visualize_results(self):
        G = nx.DiGraph()

        # Add nodes for printers, warehouses, and universities
        G.add_nodes_from(self.W, type="Warehouse", color="blue")
        G.add_nodes_from(self.P, type="Printer", color="green")
        G.add_nodes_from(self.U, type="University", color="red")

        # Add edges for flows (X) and connections (Y)
        for (i, j, k), flow in self.x_values.items():
            G.add_edge(i, j, weight=flow, color="black")

        for (i, j), active in self.y_values.items():
            if active > 0:
                G.add_edge(i, j, color="red", style="dashed")

        # Draw the network
        pos = {}
        # Printers on the left
        for idx, p in enumerate(self.P):
            pos[p] = (0, idx)
        # Warehouses in the middle
        for idx, w in enumerate(self.W):
            pos[w] = (1, idx - len(self.W) // 2)
        # Universities on the right
        for idx, u in enumerate(self.U):
            pos[u] = (2, idx - len(self.U) // 2)

        edge_labels = {(i, j): f"{G[i][j]['weight']:.2f}" for i, j in G.edges if 'weight' in G[i][j]}

        # Draw nodes
        colors = [data['color'] for _, data in G.nodes(data=True)]
        nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=500)

        # Draw edges
        edge_colors = [G[u][v]['color'] for u, v in G.edges]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors)

        # Draw labels
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.title("Optimization Results: Flow and Connections")
        plt.show()

    def summarize_results(self):
        x_table = pd.DataFrame([
            {"From": i, "To": j, "Book": k, "Flow": flow}
            for (i, j, k), flow in self.x_values.items()
        ])
        print("Flow Summary:")
        print(x_table)

        y_table = pd.DataFrame([
            {"From": i, "To": j, "Active": active}
            for (i, j), active in self.y_values.items()
        ])
        print("\nActive Connections Summary:")
        print(y_table)
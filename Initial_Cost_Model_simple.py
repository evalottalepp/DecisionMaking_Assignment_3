import numpy as np
import gurobipy as gb
from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import itertools

class costModel_PW_WU():
    def __init__(self,W,P,cap,U,K,c,f,demand,supply):
        self.W = W  # warehouses
        self.P = P  # printers
        self.supply = supply
        self.cap = cap  # capacities
        self.demand = demand 
        self.U = U  # universities
        self.K = K  # book types
        self.c = c  # variable costs
        self.f = f  #fixed costs

        self.solvedModel = None
        
        self.M = max(self.supply.sum(),self.demand.sum())
        
        self.nLocations = len(self.W) + len(self.P) + len(self.U)
        self.edges = [(i,j) for i in range(self.nLocations) for j in range(self.nLocations)]
        self.bookEdges = [(i,j,k) for i in range(self.nLocations) for j in range(self.nLocations) for k in self.K]

    
    def set_U(self,U):
        self.U = U

    def model(self):

        model = gb.Model('Cost Model')

        X_PW = model.addVars(self.P,self.W,self.K, vtype=GRB.INTEGER, lb=0, name = 'X_PW')
        X_WU = model.addVars(self.W, self.U,self.K, vtype=GRB.INTEGER, lb=0, name = 'X_WU')

        
        Y_PW = model.addVars(self.P,self.W, vtype=GRB.BINARY, name = 'Y_PW')
        Y_WU = model.addVars(self.W, self.U, vtype=GRB.BINARY, name = 'Y_WU')

        model.setObjective(
            gb.quicksum([
                        gb.quicksum([self.c[p,w] * X_PW[p,w,k] for k in self.K]) 
                         + (self.f[p,w] * Y_PW[p,w]) 
                         for p in self.P for w in self.W
                         ]) 
            + gb.quicksum([
                        gb.quicksum([self.c[w,u] * X_WU[w,u,k] for k in self.K]) 
                         + (self.f[w,u] * Y_WU[w,u]) 
                         for u in self.U for w in self.W
                         ])
            , GRB.MINIMIZE
        )


        # Warehouse cannot hold any books
        for w in self.W:
            for k in self.K:
                model.addConstr(
                    gb.quicksum([X_PW[p,w,k] for p in self.P]) 
                    == gb.quicksum([X_WU[w,u,k] for u in self.U])
                )
        
        # Supply of books at printer is held
        for p in self.P:
            for k in self.K:
                model.addConstr(
                    gb.quicksum([X_PW[p,w,k] for w in self.W])
                    <= self.supply[p,k]
                )

        # Demand must be met
        for u in self.U:
            for k in self.K:
                model.addConstr(
                    gb.quicksum([X_WU[w,u,k] for w in self.W])
                    == self.demand[u,k]
                )

        # Cannot send more than handled by warehouse
        ######################### THis is what is stated in the assingment but may not be correct
        for w in self.W:
            for p in self.P: 
                model.addConstr(
                    gb.quicksum([X_PW[p,w,k] for k in self.K])
                    <= (self.cap[w] * Y_PW[p,w])
                )

                model.addConstr(
                    gb.quicksum([X_PW[p,w,k] for k in self.K])
                    <= (gb.quicksum([self.supply[p,k] for k in self.K])*Y_PW[p,w])
                )

        # Books sent from warehouse are less than capacity and demand
        ######################### THis is what is stated in the assingment but may not be correct
        for w in self.W:
            for u in self.U:
                model.addConstr(
                    gb.quicksum([X_WU[w,u,k] for k in self.K])
                    <= (self.cap[w] * Y_WU[w,u])
                )
                
                model.addConstr(
                    gb.quicksum([X_WU[w,u,k] for k in self.K])
                    <= (gb.quicksum([self.demand[u,k] for k in self.K])*Y_WU[w,u])
                )

        # Added capacity constraint for the warehouses - the total inflow of books from all printers must not be more than warehouse capacity
        # This is not relevant for when only one university is considered, rather when all of them are considered
        for w in self.W:
            model.addConstr(
                gb.quicksum(X_PW[p,w,k] for p in self.P for k in self.K) <= self.cap[w], name=f"capacity_{w}")



        # remove cross docks
        crossDocks = self.W[2:]
        for c in crossDocks:
            for p in self.P:
                model.addConstr(
                                gb.quicksum([X_PW[p,c,k] for k in self.K])
                                == 0
                                )
            for u in self.U:
                model.addConstr(
                                gb.quicksum([X_WU[c,u,k] for k in self.K])
                                == 0
                                )

        
        model.optimize()

        self.x_pw_values_all = {key: var.X for key, var in X_PW.items()}
        self.x_wu_values_all = {key: var.X for key, var in X_WU.items()}
        self.y_pw_values_all = {key: var.X for key, var in Y_PW.items()}
        self.y_wu_values_all = {key: var.X for key, var in Y_WU.items()}


        self.x_pw_values = {key: var.X for key, var in X_PW.items() if var.X > 0}
        self.x_wu_values = {key: var.X for key, var in X_WU.items() if var.X > 0}
        self.y_pw_values = {key: var.X for key, var in Y_PW.items() if var.X > 0}
        self.y_wu_values = {key: var.X for key, var in Y_WU.items() if var.X > 0}

        self.solvedModel = model

        return model
    
    def visualize_results(self):
        G = nx.DiGraph()

        # Add nodes for printers, warehouses, and universities
        G.add_nodes_from(self.W, type="Warehouse", color="blue")
        G.add_nodes_from(self.P, type="Printer", color="green")
        G.add_nodes_from(self.U, type="University", color="red")

        # Dictionary to store aggregated flow values for edge labels
        edge_flows = {}

        # Add edges for flows from printers to warehouses
        for (p, w, k), flow in self.x_pw_values.items():
            if (p, w) not in edge_flows:
                edge_flows[(p, w)] = 0
            edge_flows[(p, w)] += flow
            G.add_edge(p, w, color="black")  # Add edge without weight for visualization

        # Add edges for flows from warehouses to universities
        for (w, u, k), flow in self.x_wu_values.items():
            if (w, u) not in edge_flows:
                edge_flows[(w, u)] = 0
            edge_flows[(w, u)] += flow
            G.add_edge(w, u, color="black")  # Add edge without weight for visualization

        # Define positions for nodes
        pos = {}
        for idx, p in enumerate(self.P):
            pos[p] = (0, idx)
        for idx, w in enumerate(self.W):
            pos[w] = (1, idx - len(self.W) // 2)
        for idx, u in enumerate(self.U):
            pos[u] = (2, idx - len(self.U) // 2)

        # Create edge labels based on aggregated flows
        edge_labels = {edge: f"{flow:.2f}" for edge, flow in edge_flows.items()}

        # Draw nodes
        colors = [data['color'] for _, data in G.nodes(data=True)]
        nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=500)

        # Draw edges
        edge_colors = [G[u][v]['color'] for u, v in G.edges]
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors)

            # Draw labels
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=8,
            label_pos=0.65,  # Position of the label along the edge (0.5 is default)
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor="white", alpha=0.7),
        )

        plt.title("Optimization Results: Flow and Connections")
        plt.show()


    def summarize_results(self):

        mapper_pwu = {0: "P1", 1: "P2", 2: "P3", 3: "W1", 4: "W2", 5: "C1", 6: "C2",
                  7: "C3", 8: "U1", 9: "U2", 10: "U3", 11: "U4", 12: "U5"}
        mapper_b = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6"}

        def map_pwu(id):
            return mapper_pwu.get(id)
    
        def map_book(id):
            return mapper_b.get(id)
        
        x_pw_table = pd.DataFrame([
            {"From Printer": map_pwu(p), "To Warehouse": map_pwu(w), "Flow": flow, "Book": map_book(k)}
            for (p, w,k), flow in self.x_pw_values.items()
        ])
        print("Flow Summary (Printers to Warehouses):")
        print(x_pw_table)

        x_wu_table = pd.DataFrame([
            {"From Warehouse": map_pwu(w), "To University": map_pwu(u), "Flow": flow, "Book:" : map_book(k)}
            for (w, u,k), flow in self.x_wu_values.items()
        ])
        print("\nFlow Summary (Warehouses to Universities):")
        print(x_wu_table)

        y_pw_table = pd.DataFrame([
            {"From Printer": map_pwu(p), "To Warehouse": map_pwu(w), "Active": active}
            for (p, w), active in self.y_pw_values.items()
        ])
        print("\nActive Connections (Printers to Warehouses):")
        print(y_pw_table)

        y_wu_table = pd.DataFrame([
            {"From Warehouse": map_pwu(w), "To University": map_pwu(u), "Active": active}
            for (w, u), active in self.y_wu_values.items()
        ])
        print("\nActive Connections (Warehouses to Universities):")
        print(y_wu_table)

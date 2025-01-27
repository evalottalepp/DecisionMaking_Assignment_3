import numpy as np
import gurobipy as gb
from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import itertools

class ProfitModels:
    def __init__(self,W,P,cap,U,K,c,f,demand,supply,price=6):
        self.W = W  # warehouses
        self.P = P  # printers
        self.supply = supply
        self.cap = cap  # capacities
        self.demand = demand 
        self.U = U  # universities
        self.K = K  # book types
        self.c = c  # variable costs
        self.f = f  #fixed costs
        self.price = price
        

        self.solvedModel = None
        
        self.M = max(self.supply.sum(),self.demand.sum())
        
        self.nLocations = len(self.W) + len(self.P) + len(self.U)
        self.edges = [(i,j) for i in range(self.nLocations) for j in range(self.nLocations)]
        self.bookEdges = [(i,j,k) for i in range(self.nLocations) for j in range(self.nLocations) for k in self.K]

        self.mapper_pwu = {0: "P1", 1: "P2", 2: "P3", 3: "W1", 4: "W2", 5: "C1", 6: "C2", 
                            7: "C3", 8: "U1", 9: "U2", 10: "U3", 11: "U4", 12: "U5"}
        self.mapper_b = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6"}
    
    def set_U(self,U):
        self.U = U

    def model(self):

        model = gb.Model('Cost Model')

        X_PW = model.addVars(self.P,self.W,self.K, vtype=GRB.CONTINUOUS, lb=0, name = 'X_PW')
        X_WU = model.addVars(self.W, self.U,self.K, vtype=GRB.CONTINUOUS, lb=0, name = 'X_WU')

        
        Y_PW = model.addVars(self.P,self.W, vtype=GRB.BINARY, name = 'Y_PW')
        Y_WU = model.addVars(self.W, self.U, vtype=GRB.BINARY, name = 'Y_WU')

        model.setObjective(
            self.price * (gb.quicksum(
                [X_WU[w,u,k] 
                 for k in self.K for u in self.U for w in self.W]
            ))
            - (gb.quicksum([
                        gb.quicksum([self.c[p,w] * X_PW[p,w,k] for k in self.K]) 
                         + (self.f[p,w] * Y_PW[p,w]) 
                         for p in self.P for w in self.W
                         ]) 
            + gb.quicksum([
                        gb.quicksum([self.c[w,u] * X_WU[w,u,k] for k in self.K]) 
                         + (self.f[w,u] * Y_WU[w,u]) 
                         for u in self.U for w in self.W
                         ]))
            , GRB.MAXIMIZE
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

        # Demand must be met or 0 in case the company choses not to fore
        for u in self.U:
            for k in self.K:
                model.addConstr(
                    gb.quicksum([X_WU[w,u,k] for w in self.W])
                    <= self.demand[u,k]
                )

        # Cannot send more than handled by warehouse
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

        model.setParam('OutputFlag', 0)
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

    def map_pwu(self, id):
            return self.mapper_pwu.get(id)
    
    def map_book(self, id):
        return self.mapper_b.get(id)
    
    def visualize_network(self, model, printer = True):
        links = []
        flow_labels = {}

        node_labels = {}
        book_labels = {}

        for p in self.P:
            node_labels[p] = self.map_pwu(p)
        for w in self.W:
            node_labels[w] = self.map_pwu(w)
        for u in self.U:
            node_labels[u] = self.map_pwu(u)
        for k in self.K:
            book_labels[k] = self.map_book(k)
        
        printers = set()
        warehouses = set()
        universities = set()
        if model.status == GRB.OPTIMAL:
            objective_value = model.objVal
            
            for (p, w, k), flow in self.x_pw_values.items():
                printers.add(p)
                warehouses.add(w)
                key = (p, w)
                links.append(key)

                if key not in flow_labels:
                    flow_labels[key] = []
                flow_labels[key].append(f'{book_labels[k]}: {flow}')
                if printer:
                    print(f'Flow from printer {self.map_pwu(p)} to warehouse {self.map_pwu(w)} for book {self.map_book(k)}: {flow}')

            for (w, u, k), flow in self.x_wu_values.items():
                warehouses.add(w)
                universities.add(u)
                key = (w, u)
                links.append(key)

                if key not in flow_labels:
                    flow_labels[key] = []
                flow_labels[key].append(f'{book_labels[k]}: {flow}')
                if printer:
                    print(f'Flow from warehouse {self.map_pwu(w)} to university {self.map_pwu(u)} for book {self.map_book(k)}: {flow}')

        G = nx.DiGraph()
        G.add_nodes_from(printers | warehouses | universities)
        G.add_edges_from(links)

        total_nodes = len(printers) + len(warehouses) + len(universities)

        def calculate_positions(total_nodes, count, row_index):
            horizontal_spacing = total_nodes / count 
            return [((i + 0.5) * horizontal_spacing, row_index) for i in range(count)]

        pos = {}
        printer_positions = calculate_positions(total_nodes, len(printers), 2)
        warehouse_positions = calculate_positions(total_nodes, len(warehouses), 1)
        university_positions = calculate_positions(total_nodes, len(universities), 0)

        for idx, p in enumerate(printers):
            pos[p] = printer_positions[idx]
        for idx, w in enumerate(warehouses):
            pos[w] = warehouse_positions[idx]
        for idx, u in enumerate(universities):
            pos[u] = university_positions[idx]

        formatted_labels = {key: '\n'.join(value) for key, value in flow_labels.items()}
        visual_labels = {node: node_labels[node] for node in G.nodes}

        plt.figure(figsize=(12,5))
        plt.title(f'Network with objective value: {objective_value}')

        nx.draw(
            G, pos, labels=visual_labels, with_labels=True, node_size=300, node_color='lightblue', font_size=10, 
            font_weight='bold', edge_color='gray'
        )

        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=formatted_labels, font_size=8, label_pos=0.5, font_color='darkgreen'
        )

        plt.subplots_adjust(top=0.9)

        plt.show()
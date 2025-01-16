import numpy as np
import gurobipy as gb
from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import itertools

class profitModel():
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



        # # remove cross docks
        # crossDocks = self.W[2:]
        # for c in crossDocks:
        #     for p in self.P:
        #         model.addConstr(
        #                         gb.quicksum([X_PW[p,c,k] for k in self.K])
        #                         == 0
        #                         )
        #     for u in self.U:
        #         model.addConstr(
        #                         gb.quicksum([X_WU[c,u,k] for k in self.K])
        #                         == 0
        #                         )

        
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

from gurobipy import *
import json

# You do not need to modify this function
def read_instance(instance_path):
    with open(instance_path) as f:
        data = json.load(f)
    return data["p"], data["c"], data["alpha"], data["customers"], data["distances"], data["demands"]

def solve(p, c, alpha, customers, distances, demands):
    """Solves the hub location problem using the 3-index formulation.

    Args:
        p (int): number of hubs to open
        c (float): cost factor for flows between customer and hub in money units per demand and distance unit
        alpha (float): discount factor for intra-hub transports
        customers (list[int]): list of customer indices
        distances (list[list[float]]): distance matrix, distances[i][j] is the distance between customer i and customer j
        demands (list[list[float]]): demand matrix, demands[i][j] is the demand from customer i to customer j

    Returns:
        Gurobi.Model: the solved model
    """    
    model = Model("Hub Location")

    # You can try and disable cutting planes - what happens?
    # model.setParam(GRB.Param.Cuts, 0)
    # NOTE: Please do not turn off cutting planes in your final submission

    # --- Do we need to prepare something? ---

    # --- Variables ---

    # x is a binary variable indicating whether customer i is served by hub j
    x = tupledict()
    for i in customers:
        for j in customers:
            x[i, j] = model.addVar(vtype="b", name=f"x_{i}_{j}")

    # hub is a binary variable indicating whether a hub is located at location j
    hub = tupledict()
    for i in customers:
        hub[i] = model.addVar(vtype="b", name=f"hub_{i}")

    
    # y is teh amount of demand originating from customer i that transported from hub k to hub l
    y = tupledict()
    for i in customers:
        for k in range(p):
            for l in range(p):
                y[i, k, l] = model.addVar(vtype="c", lb=0, name=f"y_{i}_{k}_{l}")
    

    # -------------------------------------------------------------------------
    model.update()
    # -------------------------------------------------------------------------

    # --- Constraints ---
    # maximal p hubs
    model.addConstr(quicksum(hub[i] for i in customers) <= p)

    # each customer is served by exactly one hub
    for i in customers:
        model.addConstr(quicksum(x[i, j] for j in customers) == 1)
        for j in customers:
            # if customer i is served by hub j, then a hub must be located at location j.
            model.addConstr(x[i, j] <= hub[j])

    # --- Objective ---
    # minimize the total cost
    model.setObjective(quicksum(c * distances[i][j] * demands[i][j] * x[i, j] for i in customers for j in customers)+ 
                       # TODO: add the intra-hub transport costs
                       quicksum(alpha * c * distances[i][j] * demands[i][j] * y[i, k, l] for i in customers for k in range(p) for l in range(p)), 
                       GRB.MINIMIZE)
    

    # --- Solve model ---

    # If you want to solve just the LP relaxation, uncomment the lines below
    # model.update()
    # model = model.relax()

    model.optimize()
    # model.write("model.lp")

    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")

    return model


if __name__ == "__main__":
    p, c, alpha, customers, distances, demands = read_instance("n10.json")

    solve(p, c, alpha, customers, distances, demands) 
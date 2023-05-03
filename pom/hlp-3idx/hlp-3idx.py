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

    # x_i_k equal to one if and only if node i is assigned to hub k
    x = tupledict()
    for i in customers:
        for k in customers:
            x[i, k] = model.addVar(vtype="b", name=f"x_{i}_{k}")
    
    # y = tupledict()
    # for ... 
        # y[i, k, l] = model.addVar(vtype="c", lb=0, name=f"y_{i}_{k}_{l}",
        # obj = ...)

    # y is the amount of demand originating from customer i that transported from hub k to hub l
    y = tupledict()
    for i in customers:
        for k in customers:
            for l in customers:
                y[i, k, l] = model.addVar(vtype="c", lb=0, name=f"y_{i}_{k}_{l}")
    

    # -------------------------------------------------------------------------
    model.update()
    # -------------------------------------------------------------------------

    # --- Constraints ---
    # 1. maximal p hubs
    model.addConstr(quicksum(x[i, i] for i in customers) <= p)

    # 2. each customer is served by exactly one hub
    for i in customers:
        model.addConstr(quicksum(x[i, k] for k in customers) == 1)
        # 3. customers are assigned to open hubs
        for k in customers:
            model.addConstr(x[i, k] <= x[k, k])
    
    # 4. the flow entering to hub l either directly from customer i or via other hubs k 
    # has to be equal to the flow leaving to either other hubs k or to destination nodes j
    for i in customers:
        for l in customers:
            model.addConstr(quicksum(demands[i][j] for j in customers) * x[i, l] + quicksum(y[i, k, l] for k in customers) == 
                            quicksum(y[i, l, k] for k in customers) + quicksum(demands[i][j] * x[j, l] for j in customers))
        

    # --- Objective ---
    # minimize the total cost
    model.setObjective(c * (quicksum(quicksum(demands[i][j] for j in customers) * quicksum(distances[i][j]  * x[i, j] for j in customers) +
                                     quicksum(demands[j][i] for j in customers) * quicksum(distances[i][j]  * x[i, j] for j in customers)
        for i in customers))
        + alpha * c * quicksum(distances[k][l] * y[i, k, l] for i in customers for k in customers for l in customers), 
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
    p, c, alpha, customers, distances, demands = read_instance("n20.json")

    solve(p, c, alpha, customers, distances, demands) 
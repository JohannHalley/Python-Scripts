from gurobipy import *
import json

# You do not need to modify this function
def read_instance(instance_path):
    with open(instance_path) as f:
        data = json.load(f)
    return data["p"], data["c"], data["alpha"], data["customers"], data["distances"], data["demands"]

def solve(p, c, alpha, customers, distances, demands):
    """Solves the hub location problem using the 4-index formulation.

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

    # the flow originated at i and destination j transits via hub arc (k, l)
    x = tupledict()
    for i in customers:
        for j in customers:
            for k in customers:
                for l in customers:
                    x[i, j, k, l] = model.addVar(vtype="b", name=f"x_{i}_{j}_{k}_{l}")
                    
    # x_i_k equal to one if and only if node i is assigned to hub k
    z = tupledict()
    for i in customers:
        for k in customers:
            z[i, k] = model.addVar(vtype="b", name=f"z_{i}_{k}")
                                            
    model.update()

    # --- Constraints ---
    # 1. maximal p hubs
    model.addConstr(quicksum(z[i, i] for i in customers) <= p)

    # 2. each customer is served by exactly one hub
    for i in customers:
        model.addConstr(quicksum(z[i, k] for k in customers) == 1)
    # 3. customers are assigned to open hubs
        for k in customers:
            model.addConstr(z[i, k] <= z[k, k])

    # 4. flow conservation
    # x_i_j_k_l = 1 if and only if z_i_k = 1 and z_j_l = 1
    for i in customers:
        for j in customers:
            for k in customers:
                for l in customers:
                    model.addConstr(2 * x[i, j, k, l] <= z[i, k] + z[j, l])

    for i in customers:
        for j in customers:
            model.addConstr(quicksum(x[i, j, k, l] for k in customers for l in customers) == 1)
        

    # ---- Objective ----
    model.setObjective(alpha * c * quicksum(distances[k][l] * demands[i][j] * x[i, j, k, l] 
                                for i in customers for j in customers for k in customers for l in customers)
                    + c * quicksum(distances[i][k] * quicksum(demands[i][j] + demands[j][i] for j in customers) * z[i, k] 
                                for i in customers for k in customers)
        , GRB.MINIMIZE)


    # --- Solve model ---

    # If you want to solve just the LP relaxation, uncomment the lines below
    model.update()
    model = model.relax()

    model.optimize()
    # model.write("model.lp")

    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")

    return model


if __name__ == "__main__":
    p, c, alpha, customers, distances, demands = read_instance("n10.json")

    solve(p, c, alpha, customers, distances, demands) 
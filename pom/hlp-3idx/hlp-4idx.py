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
                    x[i, j, k, l] = model.addVar(vtype="c", lb=0, name=f"x_{i}_{j}_{k}_{l}")

    # for ... 
        # x[i, j, k, l] = model.addVar(vtype="c", lb=0, name=f"x_{i}_{j}_{k}_{l}",
        # obj = ...)

    # more variables are necessary

    model.update()

    # --- Constraints ---


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
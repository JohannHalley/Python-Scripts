from gurobipy import *
import json
from itertools import combinations


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

    x = tupledict()
    for i in customers:
        for j in customers:
            for k in customers:
                for l in customers:
                    x[i, j, k, l] = model.addVar(vtype="b", name=f"x_{i}_{j}_{k}_{l}",
                                                 obj=alpha * c * demands[i][j] * distances[k][l])

    y = tupledict()
    for i in customers:
        for j in customers:
            # if one customer is assigned to a hub, the the shipment it send and receive have to pass this hub
            # to send from i
            demand = sum(demands[i])
            # i receive from other customers
            for k in customers:
                demand += demands[k][i]
            y[i, j] = model.addVar(vtype='b', name=f"y_{i}_{j}", obj=c * demand * distances[i][j])
    # more variables are necessary

    model.update()
    # --- Constraints ---
    for i in customers:
        for j in customers:
            for k in customers:
                for l in customers:
                    # x[i,j,k,l] could be 1, if i is assigned to k and j is assigned to l
                    model.addConstr(2 * x[i, j, k, l] <= (y[i, k] + y[j, l]))

    # model.addConstrs(x.sum(i, "*", j, "*") <= y[i, j] * 1000 for i in customers for j in customers)
    # model.addConstrs(x.sum("*", i, "*", j) <= y[i, j] * 1000 for i in customers for j in customers)
    # model.addConstrs(x.sum("*", "*", i, "*") <= y[i, i] * 1000 for i in customers)
    # model.addConstrs(x.sum("*", "*", "*", i) <= y[i, i] * 1000 for i in customers)
    # for each pairs for customer, there are a x path from i to j
    model.addConstrs(x.sum(i, j, "*", "*") == 1 for i in customers for j in customers)

    # for i in customers:
    #     for j in customers:
    #         for k in customers:
    #             model.addConstr(
    #                 quicksum(x[i, j, k, m] for m in customers) + quicksum(x[i, j, m, k] for m in customers if m != k) <=
    #                 y[k, k])
    # open exactly p hubs
    model.addConstr(quicksum(y[j, j] for j in customers) == p)

    # one customer can be assigned to exactly one hub
    model.addConstrs(y[i, j] <= y[j, j] for i in customers for j in customers)
    model.addConstrs(quicksum(y[i, j] for j in customers) == 1 for i in customers)

    # --- Solve model ---

    # If you want to solve just the LP relaxation, uncomment the lines below
    model.update()
    # model = model.relax()

    model.optimize()

    # model.write("model.lp")

    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")
    def printSolution():
        if model.status == GRB.OPTIMAL:

            for i in customers:
                for j in customers:
                    # if (y[i,j].x != 0):
                    #     print((i,j))

                    for k in customers:
                        for l in customers:
                            if (x[i, j, k, l].x != 0):
                                print((i, j, k, l))

    # printSolution()
    return model


if __name__ == "__main__":
    p, c, alpha, customers, distances, demands = read_instance("n10.json")

    solve(p, c, alpha, customers, distances, demands)

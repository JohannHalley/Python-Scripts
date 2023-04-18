#!/usr/bin/env python3
from gurobipy import *
import json
import networkx as nx
from networkx.readwrite import json_graph


def build_graph_nodes(g_street, jobs, g_time_expanded):
    # get max j_d for all jobs and number of nodes in g_street
    max_j_d = max([job['j_d'] for job in jobs.values()])
    node_num = len(g_street.nodes())

    for l in g_street.nodes():
        for t in range(max_j_d + 1):
            g_time_expanded.add_node((l, t), pos=(l, t + 1))

    # Adding source and sink nodes
    # add source node for every time step in the time-expanded graph, g_time_expanded
    for id, job in jobs.items():
        # add source node
        g_time_expanded.add_node((id, 'start'), pos=(int(id), 0))
        # add sink node
        g_time_expanded.add_node((id, 'end'), pos=(
            node_num + int(id), job['j_d'] + 2))


def build_graph_arcs(g_street, jobs, g_time_expanded):
    max_j_d = max([job['j_d'] for job in jobs.values()])

    # Adding arcs
    # add all arcs from g_street for every time step in the time-expanded graph, g_time_expanded
    for t in range(max_j_d + 1):
        for arc in g_street.edges():
            # check if arc is not out of bounds, then add links
            if t + g_street.edges[arc]['weight'] <= max_j_d:
                g_time_expanded.add_edge((arc[0], t), (arc[1], t + g_street.edges[arc]['weight']))
                g_time_expanded.add_edge((arc[1], t), (arc[0], t + g_street.edges[arc]['weight']))

    # add waiting arcs
    for t in range(max_j_d):
        for node in g_street.nodes():
            g_time_expanded.add_edge((node, t), (node, t + 1))

    # add arcs from source node to first node of job and from last node of job to sink node
    for id, job in jobs.items():
        # add arc from source node to first node(start location with release tiem) of job
        g_time_expanded.add_edge((id, 'start'), (job['j_s'], job['j_r']))

        # add arc from last node of job to sink node
        for t in range(job['j_r'], job['j_d'] + 1):
            g_time_expanded.add_edge((job['j_t'], t), (id, 'end'))


# --- TODO ---
# This function is missing not only its content but also proper documentation!
# We recommend you to finish the docstring
# As a sidenote, in most code editors you can add function comment strings like below
# automatically with a key combination.
# For VSC, the extension autoDocstring is necessary.
def build_graph(g_street, jobs):
    """Constructs the time-expanded graph

    Args:
        g_street (which datatype?): What is this? 
            _node, _adj
        jobs (dict): Good documentation is important!
            "jobs": {
                "1": {
                    "j_s": 2,   # start node
                    "j_t": 1,   # target node
                    "j_r": 1,   # release time
                    "j_d": 2    # deadline
                },
                "0": {
                    "j_s": 0,
                    "j_t": 2,
                    "j_r": 0,
                    "j_d": 3
                }
            }
    Returns:
         time-expanded graph (directed graph):
    """

    # New directed graph
    g_time_expanded = nx.DiGraph()

    build_graph_nodes(g_street, jobs, g_time_expanded)

    build_graph_arcs(g_street, jobs, g_time_expanded)

    return g_time_expanded


# You do not need to change anything in this function
def read_instance(full_instance_path):
    """Reads JSON file

    Args:
        full_instance_path (string): Path to the instance

    Returns:
        Dictionary: Jobs
        nx.DiGraph: Graph of the street network
    """
    with open(full_instance_path) as f:
        data = json.load(f)
    return (data['jobs'], json_graph.node_link_graph(data['graph']))


# Lots of work to do in this function!
def solve(full_instance_path):
    """Solving function, takes an instance file, constructs the time-expanded graph, builds and solves a gurobi model

    Args:
        full_instance_path (string): Path to the instance file to read in

    Returns:
        model: Gurobi model after solving
        G: time-expanded graph
    """

    # Read in the instance data
    jobs, g_street = read_instance(full_instance_path)

    # Construct graph --- NOTE: Please use networkx for this task, it is necessary for the plots in the Jupyter file.
    g_time_expanded = build_graph(g_street, jobs)

    # === Gurobi model ===
    model = Model("AGV")

    # --- Variables ---
    # Commodity arc variables
    x = {}
    for e in g_time_expanded.edges:
        x[e] = model.addVar(name=f"x_{e}", vtype="b", obj=1)

    # Potentially additional variables? --- TODO ---

    # --- Constraints
    # multi-commodity Flow conservation constraints
    for node in g_time_expanded.nodes:
        if node[1] != 'start' and node[1] != 'end':
            model.addConstr(quicksum(x[(e[0], node)] for e in g_time_expanded.in_edges(node)) - 
                            quicksum(x[(node, e[1])] for e in g_time_expanded.out_edges(node)) == 0)
        if node[1] == 'start':
            model.addConstr(quicksum(x[(e[0], node)] for e in g_time_expanded.in_edges(node)) - 
                            quicksum(x[(node, e[1])] for e in g_time_expanded.out_edges(node)) == -1)
        if node[1] == 'end':
            model.addConstr(quicksum(x[(e[0], node)] for e in g_time_expanded.in_edges(node)) - 
                            quicksum(x[(node, e[1])] for e in g_time_expanded.out_edges(node)) == 1)

    # Solve the model
    model.update()
    model.optimize()

    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")

    # # Obtain a list of vertices that are in the solution
    # stable_set = []
    # if model.status == GRB.OPTIMAL:
    #     for v in G.nodes:
    #         if round(x[v].x) == 1:
    #             stable_set.append(v)
    
    # color_map = ["blue" if v not in stable_set else "red" for v in G.nodes]


    return model, g_time_expanded

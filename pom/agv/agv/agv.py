#!/usr/bin/env python3
from gurobipy import *
import json
import networkx as nx
from networkx.readwrite import json_graph



def build_graph_nodes(g_street, jobs, g_time_expanded):
    # get max j_d for all jobs
    max_j_d = max([job['j_d'] for job in jobs.values()])
    print(max_j_d)

    # Adding nodes 
    # add all nodes from g_street for every time step in the time-expanded graph, g_time_expanded
    for t in range(max_j_d):
        for node in g_street.nodes():
            g_time_expanded.add_node(f"{node}_{t}", pos=(node, t))

def build_graph_arcs(g_street, jobs, g_time_expanded):
    # Adding arcs
    # add all arcs from g_street for every time step in the time-expanded graph, g_time_expanded
    for t in range(max_j_d):
        for arc in g_street.edges():
            # check if arc is not out of bounds
            if t + g_street.edges[arc]['weight'] <= max_j_d - 1:
                print(f"add arc from {arc[0]}_{t} to {arc[1]}_{t + g_street.edges[arc]['weight']} with wight {g_street.edges[arc]['weight']}")
                g_time_expanded.add_edge(f"{arc[0]}_{t}", f"{arc[1]}_{t + g_street.edges[arc]['weight']}", weight=g_street.edges[arc]['weight'])
    




# --- TODO ---
# This function is missing not only its content but also proper documentation! We recommend you to finish the docstring
# As a sidenote, in most code editors you can add function comment strings like below automatically with a key combination. For VSC, the extension autoDocstring is necessary.
def build_graph(g_street, jobs):
    """Constructs the time-expanded graph

    Args:
        g_street (which datatype?): What is this?
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
        (some datatype(s)): what do you want to return?
    """

    # New directed graph
    g_time_expanded = nx.DiGraph()

    # get max j_d for all jobs
    max_j_d = max([job['j_d'] for job in jobs.values()])

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
    jobs, g_street= read_instance(full_instance_path)

    # Construct graph --- NOTE: Please use networkx for this task, it is necessary for the plots in the Jupyter file.
    g_time_expanded = build_graph(g_street, jobs)

    # === Gurobi model ===
    model = Model("AGV")

    # --- Variables ---



    # Commodity arc variables
    x = {}  # --- TODO ---



    # Potentially additional variables? --- TODO ---

    # --- Constraints
    # --- TODO ---



    # Solve the model
    model.update()
    model.optimize()
    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")

    return model, g_time_expanded 

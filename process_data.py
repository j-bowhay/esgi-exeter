import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import os
import pickle
import cv2
import itertools

# =====================================================================================
# Data loading
# =====================================================================================

def resize_to_mask_dims(image, mask_shape):
    """
    Resize a cv2-read image to match the (h, w) the masks/bboxes were
    generated against (e.g. a pymupdf page render at a given DPI).

    mask_shape: (h, w) of the mask array, e.g. new_rooms[some_key][0].shape
    """
    target_h, target_w = mask_shape[:2]
    if image.shape[:2] == (target_h, target_w):
        return image
    resized = cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    return resized


def load_graph_from_json(plan):
    with open(f"data/{plan}/graph_output.json", "r") as f:
        data = json.load(f)

    G = json_graph.node_link_graph(
        data,
        edges="links",
    )

    image = plt.imread(f"data/{plan}/output/graph_on_input.png")

    with open(f"data/{plan}/output/model_processed.pkl", "rb") as f:
        room_masks = pickle.load(f)
    first_key = next(iter(room_masks))
    mask_shape = room_masks[first_key][0].shape
    image = resize_to_mask_dims(image, mask_shape)

    return G, image

def graph_generator():
    """Yield all graphs and their corresponding images from the data directory.
    """
    subfolders= [f.path.split("/")[-1] for f in os.scandir("/home/up19056/development/esgi_exeter/data") if f.is_dir()]
    for plan in sorted(subfolders):
        G, image = load_graph_from_json(plan)
        yield plan, G, image

# =====================================================================================
# Plotting
# =====================================================================================

def plot(G, im=None, ax=None):
    """Plot the graph G with optional background image im."""
    if ax is None:
        fig, ax = plt.subplots()

    pos = {
        node: tuple(data["position"])
        for node, data in G.nodes(data=True)
    }
    nodes_colours = []
    for _, data in G.nodes(data=True):
        if data["room_name"] == "door":
            nodes_colours.append("#0084FF")
        elif data["room_name"] == "exit_door":
            nodes_colours.append("#00FF00")
        else:
            nodes_colours.append("#FF00AA")
    edges_colours = []
    for _, _, connection in G.edges.data("connection"):
        if connection == "door":
            edges_colours.append("#0084FF")
        elif connection == "adjacent":
            edges_colours.append("#FF00AA")
        else:
            edges_colours.append("#0F0F0F")


    if im is not None:
        ax.imshow(im)
    nx.draw_networkx(
        G,
        pos=pos,
        with_labels=True,
        node_color=nodes_colours,
        node_size=300,
        font_size=8,
        edge_color=edges_colours,
        width=4,
        ax=ax
    )

        # Node legend
    node_handles = [
        mlines.Line2D([], [], color="#0084FF", marker='o', linestyle='None',
                      markersize=10, label="Door"),
        mlines.Line2D([], [], color="#00FF00", marker='o', linestyle='None',
                      markersize=10, label="Exit door"),
        mlines.Line2D([], [], color="#FF00AA", marker='o', linestyle='None',
                      markersize=10, label="Room"),
    ]

    # Edge legend
    edge_handles = [
        mlines.Line2D([], [], color="#0084FF", linewidth=4, label="Door connection"),
        mlines.Line2D([], [], color="#FF00AA", linewidth=4, label="Adjacent"),
        mlines.Line2D([], [], color="#0F0F0F", linewidth=4, label="Other"),
    ]

    ax.legend(
        handles=node_handles + edge_handles,
        loc="upper right",
        frameon=True
    )
    ax.set_aspect('equal')

# =====================================================================================
# Summary statistics
# =====================================================================================

def plot_individual_degree_dist(G):
    """Plot the degree distribution of a single graph G."""
    degree_sequence = sorted((d for n, d in G.degree()), reverse=True)
    plt.bar(*np.unique(degree_sequence, return_counts=True))
    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    plt.show()

def degree_distribution_all(remove_doors=True):
    degrees = []
    for plan, G in graph_generator():
        plan_degrees = [d for n, d in G.degree() if n not in [node for node, data in G.nodes(data=True) if data["room_name"] == "door"]] if remove_doors else [d for n, d in G.degree()]
        degrees.extend(plan_degrees)
        print(f"Plan: {plan}, {max(plan_degrees)=}")
    plt.bar(*np.unique(degrees, return_counts=True))
    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    plt.show()

# =====================================================================================
# Graph mangling
# =====================================================================================

def remove_wall_adjacency_edges(G):
    edges_to_remove = [(u, v) for u, v, data in G.edges(data=True) if data["connection"] == "adjacent"]
    G.remove_edges_from(edges_to_remove)
    return G

def rename_exit_door(G):
    for node, data in G.nodes(data=True):
        if data["room_name"] == "door":
            edges = list(G.edges(node, data=True))
            for edge in edges:
                if edge[2]["connection"] == "exit":
                    G.nodes[node]["room_name"] = "exit_door"
                    break
    return G

def add_outside_node(G):
    G.add_node("outside", room_name="outside", position=(0, 0))
    for node, data in G.nodes(data=True):
        if data["room_name"] == "exit_door":
            G.add_edge(node, "outside", connection="exit_door")
    return G

def get_doors(G):
    return [node for node, data in G.nodes(data=True) if data["room_name"] == "door"]

# =====================================================================================
# Checks
# =====================================================================================

def check_double_doors(G):
    door_nodes = get_doors(G)
    for door1, door2 in itertools.combinations(door_nodes, 2):
        if len(nx.common_neighbors(G, door1, door2)) > 1:
            return True
    return False

def fix_double_doors(G):
    door_nodes = get_doors(G)
    for door1, door2 in itertools.combinations(door_nodes, 2):
        common_neighbors = list(nx.common_neighbors(G, door1, door2))
        if len(common_neighbors) > 1:
            # Remove one of the doors
            G.remove_node(door2)
    return G

def check_redundant_adjacency_edges(G):
    doors = get_doors(G)
    for door in doors:
        neighbors = list(G.neighbors(door))
        if G.has_edge(neighbors[0], neighbors[1]):
            return True
    return False

def remove_redundant_adjacency_edges(G):
    doors = get_doors(G)
    for door in doors:
        neighbors = list(G.neighbors(door))
        if G.has_edge(neighbors[0], neighbors[1]):
            G.remove_edge(neighbors[0], neighbors[1])
    return G

def check_all(plot_failed=True):
    n_failed = 0
    failure_count = {"No exit": 0,
                     "Missing internal door": 0,
                     "Double doors detected": 0,
                     "Not planar": 0,
                     "Redundant adjacency edges detected": 0}
    error_dist = []
    for i, (plan, G, image) in enumerate(graph_generator()):
        errors = 0
        msg = f"{plan=}"
        failed = False
        rename_exit_door(G)
        G_with_adjacency = G.copy()
        add_outside_node(G)
        remove_wall_adjacency_edges(G)
        if not nx.is_connected(G):
            expected_components = 1
            if G.degree("outside") == 0:
                msg += " | D6 No exit"
                failure_count["No exit"] += 1
                errors += 1
                expected_components += 1
            if len(list(nx.connected_components(G))) > expected_components:
                msg += " | D3 Missing internal door"
                failure_count["Missing internal door"] += 1
                errors += 1
            failed = True
        if check_double_doors(G):
            msg += " | D1 Double doors detected"
            failure_count["Double doors detected"] += 1
            failed = True
            errors += 1
        if not nx.is_planar(G):
            msg += " | A1 Not planar"
            failure_count["Not planar"] += 1
            failed = True
            errors += 1
        if check_redundant_adjacency_edges(G_with_adjacency):
            msg += " | A3 Redundant adjacency edges detected"
            failure_count["Redundant adjacency edges detected"] += 1
            failed = True
            errors += 1
        if failed:
            n_failed += 1
            print(msg)
            if plot_failed:
                G_fixed = G_with_adjacency.copy()
                fix_double_doors(G_fixed)
                remove_redundant_adjacency_edges(G_fixed)
                fig, axs = plt.subplots(1, 2, figsize=(12, 6))
                plot(G_with_adjacency, image, ax=axs[0])
                plot(G_fixed, image, ax=axs[1])
                plt.show()
        error_dist.append(errors)
    print(failure_count)
    print(f"{n_failed=}, out of {i}")
    return failure_count, error_dist

failure_count, error_dist = check_all(plot_failed=False)
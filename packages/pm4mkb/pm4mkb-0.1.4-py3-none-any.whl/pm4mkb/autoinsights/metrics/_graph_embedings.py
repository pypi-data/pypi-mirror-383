from __future__ import annotations
from pathlib import Path

from numpy import insert
from pandas import DataFrame, MultiIndex

from catboost import CatBoostClassifier

from networkx import DiGraph, shortest_path

from pm4mkb.metrics import TransitionMetric

from ._annotations import COLUMNS
from .node2vec import Node2Vec


def find_paths(G, u, n):
    if n == 0:
        return [[u]]

    return [[u] + path for neighbor in G.neighbors(u) for path in find_paths(G, neighbor, n - 1)]


def find_cycles(G, u, n):
    paths = find_paths(G, u, n)
    return [tuple(path) for path in paths if (path[-1] == u) and sum(x == u for x in path) == 2]


def get_self_loop_weight(G, node):
    cycles = find_cycles(G, node, 1)
    if cycles:
        if G.get_edge_data(node, node):
            return G.get_edge_data(node, node)["weight"]
        else:
            return 0.0
    else:
        return 0.0


def get_n2n_loop_weight(G, node):
    cycles = find_cycles(G, node, 2)
    if cycles:
        min_weight = []
        for cycle in cycles:
            another_node = cycle[1]
            forward_weight = G.get_edge_data(node, another_node)
            backward_weiht = G.get_edge_data(another_node, node)
            if forward_weight and backward_weiht:
                min_weight.append(min(forward_weight["weight"], backward_weiht["weight"]))
            else:
                min_weight.append(0.0)
        return sum(min_weight)
    else:
        return 0.0


def get_3_loop_weight(G, node):
    cycles = find_cycles(G, node, 3)
    if cycles:
        min_weight = []
        for cycle in cycles:
            first_node = cycle[1]
            second_node = cycle[2]
            node_first_weight = G.get_edge_data(node, first_node)
            first_second_weight = G.get_edge_data(first_node, second_node)
            second_node_weight = G.get_edge_data(second_node, node)
            if node_first_weight and first_second_weight and second_node_weight:
                min_weight.append(
                    min(
                        node_first_weight["weight"],
                        first_second_weight["weight"],
                        second_node_weight["weight"],
                    )
                )
            else:
                min_weight.append(0.0)
        return sum(min_weight)
    else:
        return 0.0


def get_start_start_loop_weight(G, node):
    G.add_edge("temp_node", node)
    for edge in G.in_edges(node):
        G.add_edge(edge[0], "temp_node")
    try:
        path = shortest_path(G, source=node, target="temp_node")

        G.remove_node("temp_node")
        path = path[:-1] + [node]
        if len(path) > 2:
            return min([G.get_edge_data(path[i], path[i + 1])["weight"] for i in range(len(path) - 1)])
        else:
            return 0.0
    except Exception:
        return 0.0


def dh2cycle_metric(dh):
    header = DataFrame(
        [
            COLUMNS.loop_self,
            COLUMNS.loop_roundtrip,
            COLUMNS.loop_ping_pong,
            COLUMNS.loop_start,
        ],
        columns=["Метрика", "Этап"],
    )
    header = MultiIndex.from_frame(header)
    res = DataFrame(
        0.0,
        index=dh.stage.unique(),
        columns=header,
    )
    transition_metric = TransitionMetric(dh, time_unit="s")
    transition_metric.apply().head()
    edges_count_metric = transition_metric.count().to_dict()

    graph = DiGraph()
    weighted_graph = DiGraph()
    for key in edges_count_metric:
        node1 = key[0]
        node2 = key[1]
        weight = edges_count_metric[key]
        graph.add_edge(node1, node2, weight=1.0)
        weighted_graph.add_edge(node1, node2, weight=weight)

    node2vec = Node2Vec(
        graph,
        walk_length=10,
        num_walks=80,
        p=0.25,
        q=4,
        workers=1,
        use_rejection_sampling=0,
    )
    node2vec.train(window_size=5, epochs=3)
    embeddings = node2vec.get_embeddings()

    model = CatBoostClassifier()

    model_path = Path(__file__).parent
    model_path = model_path / "models" / "catboost_model.dump"
    model.load_model(model_path)

    for node, emb in embeddings.items():
        label1 = get_self_loop_weight(graph, node)
        label2 = get_n2n_loop_weight(graph, node)
        label3 = get_3_loop_weight(graph, node)
        label4 = get_start_start_loop_weight(graph, node)

        label1 = 1 if label1 > 0 else 0
        label2 = 1 if label2 > 0 else 0
        label3 = 1 if label3 > 0 else 0
        label4 = 1 if label4 > 0 else 0

        prediction = model.predict(insert(emb, 0, [label1, label2, label3, label4]))
        predicted_labels = list(f"0b{int(prediction):04b}"[2:])[::-1]

        weight1 = get_self_loop_weight(weighted_graph, node)
        weight2 = get_n2n_loop_weight(weighted_graph, node)
        weight3 = get_3_loop_weight(weighted_graph, node)
        weight4 = get_start_start_loop_weight(weighted_graph, node)

        res.loc[node, COLUMNS.loop_self] = weight1 if float(predicted_labels[0]) > 0 else 0.0
        res.loc[node, COLUMNS.loop_roundtrip] = weight2 if float(predicted_labels[1]) > 0 else 0.0
        res.loc[node, COLUMNS.loop_ping_pong] = weight3 if float(predicted_labels[2]) > 0 else 0.0
        res.loc[node, COLUMNS.loop_start] = weight4 if float(predicted_labels[3]) > 0 else 0.0
    return res

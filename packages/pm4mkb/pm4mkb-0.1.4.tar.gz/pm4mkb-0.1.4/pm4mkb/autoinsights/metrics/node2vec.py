from __future__ import annotations
from itertools import chain
from multiprocessing import cpu_count
from random import choice, random, shuffle
from typing import TYPE_CHECKING, Iterable

from dataclassy import dataclass
from joblib import Parallel, delayed
from loguru import logger

from numpy import array, sum as np_sum, uint8, where, zeros
from numpy.random import random as np_random

from gensim.models import Word2Vec

from networkx.classes.graph import Graph

from pm4mkb._cpu_jobs_manager import get_parallelization_workers


if TYPE_CHECKING:
    from numpy import float64, float32
    from numpy.typing import NDArray
    from pm4mkb.baza import Stage


def create_alias_table(ratios: NDArray[float64]) -> tuple[list[float], list[float]]:
    """
    Create an alias table for the given ratios.

    Args:
        ratios (List[float]): The ratios to create the alias table for.
    Returns:
        Tuple[List[float], List[float]]: The accept and alias tables.
    """
    accept, alias = zeros(ratios.size, dtype=uint8), zeros(ratios.size, dtype=uint8)

    if not ratios.size:
        return accept, alias

    # For some reason, multiply each element by the size of array
    ratios *= ratios.size

    # Separate ratios into small and large arrays
    small_threshold = 1.0
    (small_indices,) = where(ratios < small_threshold)
    (large_indices,) = where(ratios >= small_threshold)

    while small_indices.size and large_indices.size:
        small_idx, large_idx = small_indices[-1], large_indices[-1]

        accept[small_idx], alias[small_idx] = ratios[small_idx], large_idx
        ratios[large_idx] -= 1 - ratios[small_idx]

        # Pop the last index from small or large array, depending on the ratio
        if ratios[large_idx] >= small_threshold:
            small_indices = small_indices[:-1]
        else:
            large_indices = large_indices[:-1]

    # Mark indices where small or large found
    accept[small_indices] = 1.0
    accept[large_indices] = 1.0

    return accept, alias


def alias_sample(accept: list[float], alias: list[float]) -> int | float:
    """
    Sample an index from a probability distribution.

    Args:
        accept (List[float]): Probability distribution.
        alias (List[float]): Alias table.

    Returns:
        int: Sampled index.
    """
    random_idx = int(np_random() * len(accept))  # Random 'accept' index
    random_ratio: float = np_random()

    # Check if random number in [0, 1] is less than acceptance probability
    # Return alias index instead
    return random_idx if random_ratio < accept[random_idx] else alias[random_idx]


def batch_numbers(walk_iterations: int, workers: int) -> list[int]:
    integer_division = walk_iterations // workers

    if walk_iterations % workers == 0:
        return [integer_division] * workers
    else:
        return [integer_division] * workers + [walk_iterations % workers]


class RandomWalker:
    graph: Graph
    # TODO better namings
    p: float
    q: float
    use_rejection_sampling: bool

    workers: int
    verbose: int

    _alias_nodes: dict[Stage, tuple[list[float], list[float]]]
    _alias_edges: dict[tuple[Stage, Stage], tuple[list[float], list[float]]]

    __slots__ = __annotations__

    def __init__(self, graph, p=1, q=1, use_rejection_sampling=False, workers=cpu_count() // 2, verbose=0):
        self.graph = graph
        """
        Parameters
        ----------
        graph : Graph
            The graph on which the algorithm will run
        p : float
            Return parameter,
            controls the likelihood of immediately revisiting a node in the walk.
        q : float
            In-out parameter,
            allows the search to differentiate between “inward” and “outward” nodes
        use_rejection_sampling : bool
            Whether to use the rejection sampling strategy in node2vec. Defaults to False.
        workers : int
            The number of parallelization workers.
            Defaults to half of the available logical CPU cores.
        verbose : int
            The verbosity level. Defaults to 0.
        """
        self.p = p
        self.q = q
        self.use_rejection_sampling = use_rejection_sampling
        self.workers = get_parallelization_workers(workers)
        self.verbose = verbose

    def simulate_walks(self, num_walks, walk_length):
        nodes = list(self.graph.nodes())

        walks = Parallel(
            n_jobs=self.workers,
            verbose=self.verbose,
        )(delayed(self._simulate_walks)(nodes, num, walk_length) for num in batch_numbers(num_walks, self.workers))

        return chain(*walks)

    def preprocess_transition_probabilities(self):
        """Preprocessing of transition probabilities for guiding the random walks."""

        def compute_node_probabilities(node: Stage) -> NDArray[float64]:
            probabilities = array(
                [self.graph[node][neighbor].get("weight", 1.0) for neighbor in self.graph.neighbors(node)]
            )

            return probabilities / np_sum(probabilities)

        self._alias_nodes = {
            node: create_alias_table(compute_node_probabilities(node)) for node in self.graph.nodes()
        }
        if not self.use_rejection_sampling:
            self._alias_edges = {edge: self._get_alias_edge(edge[0], edge[1]) for edge in self.graph.edges()}

            if not self.graph.is_directed():
                for edge in self.graph.edges():
                    self._alias_edges[(edge[1], edge[0])] = self._get_alias_edge(edge[1], edge[0])

    def _deep_walk(self, walk_length: int, start_node: Stage) -> list[Stage]:
        """
        Perform a deep walk starting from the given start_node in the graph.

        Returns:
            list: The list of nodes visited during random walk.
        """
        # Initialize the walk with the start_node
        walk = [start_node]

        # Walk until we have walk_length nodes in the walk
        # Or until we reach a node with no neighbors
        for _ in range(walk_length - 1):
            # Get the neighbors of the current node
            neighbors = list(self.graph.neighbors(walk[-1]))

            if not neighbors:
                break
            # Add a random neighbor to the walk
            walk.append(choice(neighbors))

        return walk

    def _node2vec_walk(self, walk_length: int, start_node: Stage) -> list[Stage]:
        """
        Perform a walk on the graph starting from the given start_node.
        Walk algorithm uses aliases received from probabilities pre-computation.

        Returns:
            list: The list of nodes visited during the walk.
        """
        # Initialize the walk with the start_node
        walk = [start_node]

        # Walk until we have walk_length nodes in the walk
        # Or until we reach a node with no neighbors
        for _ in range(walk_length - 1):
            node = walk[-1]
            # Get the neighbors of the current node
            neighbors = list(self.graph.neighbors(node))

            if not neighbors:
                break

            # Get the alias probabilities and
            # sample the next node using the probabilities
            if len(walk) > 1:
                previous_node = walk[-2]
                edge = (previous_node, node)

                weights = self._alias_edges[edge]
                next_node = neighbors[alias_sample(weights[0], weights[1])]
            else:
                # If the walk length is 1, use node instead of edge
                weights = self._alias_nodes[node]
                next_node = neighbors[alias_sample(weights[0], weights[1])]

            walk.append(next_node)

        return walk

    # TODO refactor
    def _knight_king_walk(self, walk_length: int, start_node: Stage) -> list[Stage]:
        """
        Reference:
        KnightKing: A Fast Distributed Graph Random Walk Engine
        http://madsys.cs.tsinghua.edu.cn/publications/SOSP19-yang.pdf
        """

        def rejection_sample(inv_p, inv_q, nbrs_num):
            upper_bound = max(1.0, max(inv_p, inv_q))
            lower_bound = min(1.0, min(inv_p, inv_q))
            shatter = 0
            second_upper_bound = max(1.0, inv_q)
            if inv_p > second_upper_bound:
                shatter = second_upper_bound / nbrs_num
                upper_bound = second_upper_bound + shatter
            return upper_bound, lower_bound, shatter

        inv_p = 1.0 / self.p
        inv_q = 1.0 / self.q
        walk = [start_node]
        while len(walk) < walk_length:
            cur = walk[-1]
            current_neighbors = list(self.graph.neighbors(cur))
            if current_neighbors:
                if len(walk) == 1:
                    walk.append(
                        current_neighbors[alias_sample(self._alias_nodes[cur][0], self._alias_nodes[cur][1])]
                    )
                else:
                    upper_bound, lower_bound, shatter = rejection_sample(inv_p, inv_q, len(current_neighbors))
                    prev = walk[-2]
                    prev_nbrs = set(self.graph.neighbors(prev))
                    while True:
                        prob = random() * upper_bound
                        if prob + shatter >= upper_bound:
                            next_node = prev
                            break
                        next_node = current_neighbors[
                            alias_sample(self._alias_nodes[cur][0], self._alias_nodes[cur][1])
                        ]
                        if prob < lower_bound:
                            break
                        if prob < inv_p and next_node == prev:
                            break
                        _prob = 1.0 if next_node in prev_nbrs else inv_q
                        if prob < _prob:
                            break
                    walk.append(next_node)
            else:
                break
        return walk

    def _simulate_walks(
        self,
        nodes: list[Stage],
        num_walks: int,
        walk_length: int,
    ):
        """
        Simulates random walks on the graph.
        Args:
            nodes: List of nodes to generate walks for.
            num_walks: Number of walks for generation.
            walk_length: Limited length of the walk.
        Returns:
            List of generated walks for each node on each iteration.
        """

        def generate_walk(*args) -> list[Stage]:
            """Generates a random walk based on the self state."""
            if self.p == 1 and self.q == 1:
                return self._deep_walk(*args)
            elif self.use_rejection_sampling:
                return self._knight_king_walk(*args)
            else:
                return self._node2vec_walk(*args)

        # Empty list of known length to store generated walks
        walks = [[]] * (num_walks * len(nodes))

        for _ in range(num_walks):
            shuffle(nodes)

            for step, node in enumerate(nodes):
                walks[step] = generate_walk(walk_length, node)

        return walks

    def _get_alias_edge(self, visited_node: int, node: int):
        """
        Compute unnormalized transition probability
        between the nodes and their neighbors, given the previously visited nodes.

        Parameters
        ----------
        visited_node : int
            The previously visited node.
        node : int
            The current node.

        Returns
        -------
        list
            The alias table for the given node.
        """

        def compute_neighbor_probabilities(neighbor) -> float:
            """
            Return p if the neighbor is the visited node,
            return q if the neighbor is not connected to the visited node.
            Otherwise, return 1.
            """
            if neighbor == visited_node:
                return self.p

            return self.q if not self.graph.has_edge(neighbor, visited_node) else 1.0

        # Compute unnormalized probabilities for each neighbor of the node
        probabilities: NDArray[float64] = array(
            [
                self.graph[node][neighbor].get("weight", 1.0) / compute_neighbor_probabilities(neighbor)
                for neighbor in self.graph.neighbors(node)
            ]
        )
        # Normalize the probabilities
        normalized_probabilities = probabilities / np_sum(probabilities)

        # Create an alias table from the probabilities
        return create_alias_table(normalized_probabilities)


@dataclass(slots=True)
class Node2Vec:
    graph: Graph
    walker: RandomWalker = None
    w2v_model: Word2Vec = None
    sentences: Iterable[list[Stage]] = []

    workers: int = cpu_count() // 2
    verbose: int = 0

    _embeddings: dict[Stage, NDArray[float32]] = {}

    def __post_init__(self, walk_length, num_walks, p=1.0, q=1.0, use_rejection_sampling=False):
        self.walker = RandomWalker(self.graph, p=p, q=q, use_rejection_sampling=use_rejection_sampling)
        logger.info("Расчет вероятностей переходов...")
        self.walker.preprocess_transition_probabilities()

        self.workers = get_parallelization_workers(self.workers)
        self.sentences = self.walker.simulate_walks(num_walks=num_walks, walk_length=walk_length)

    def train(self, embed_size=128, window_size=5, epochs=5, **kwargs):
        kwargs.update(
            dict(
                workers=self.workers,
                window=window_size,
                epochs=epochs,
                sentences=self.sentences,
                min_count=kwargs.get("min_count", 0),
                vector_size=embed_size,
                sg=1,
                hs=0,  # node2vec doesn't use Hierarchical Softmax
            )
        )

        logger.info("Обучение Node2Vec на эмбеддингах...")
        self.w2v_model = Word2Vec(**kwargs)
        logger.info("Обучение Node2Vec завершено")

        return self.w2v_model

    def get_embeddings(self):
        if self.w2v_model is None:
            logger.info("Для получения эмбеддингов должна быть обученная модель")
            return {}

        self._embeddings = {word: self.w2v_model.wv[word] for word in self.graph.nodes()}

        return self._embeddings

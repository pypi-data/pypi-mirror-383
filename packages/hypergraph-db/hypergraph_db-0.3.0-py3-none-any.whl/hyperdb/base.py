from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


@dataclass
class BaseHypergraphDB:
    r"""
    Base class for hypergraph database.
    """

    storage_file: Union[str, Path] = field(default="my_hypergraph.hgdb", compare=False)

    def save(self, file_path: Union[str, Path]) -> bool:
        r"""
        Save the hypergraph to a file.

        Args:
            ``file_path`` (``Union[str, Path]``): The file path to save the
                hypergraph.

        Returns:
            ``bool``: True if successful, False otherwise.
        """
        raise NotImplementedError

    def save_as(self, format: str, file_path: Union[str, Path]):
        r"""
        Save the hypergraph to a specific format.

        Args:
            ``format`` (``str``): The export format (e.g., "json", "csv", "graphml").
            ``file_path`` (``Union[str, Path]``): The file path to export the hypergraph.
        """
        raise NotImplementedError

    def load(self, file_path: Union[str, Path]) -> bool:
        r"""
        Load the hypergraph from a file.

        Args:
            ``file_path`` (``Union[str, Path]``): The file path to load the hypergraph from.

        Returns:
            ``bool``: True if successful, False otherwise.
        """
        raise NotImplementedError

    def load_from(self, format: str, file_path: Union[str, Path]):
        r"""
        Load a hypergraph from a specific format.

        Args:
            ``format`` (``str``): The import format (e.g., "json", "csv", "graphml").
            ``file_path`` (``Union[str, Path]``): The file path to import the hypergraph from.
        """
        raise NotImplementedError

    def _clear_cache(self):
        r"""
        Clear the cache.
        """
        raise NotImplementedError

    def v(self, v_id: Any, default: Any = None) -> dict:
        r"""
        Return the vertex data.

        Args:
            ``v_id`` (``Any``): The vertex id.
            ``default`` (``Any``): The default value if the vertex does not exist.
        """
        raise NotImplementedError

    def e(self, e_tuple: Union[List, Set, Tuple], default: Any = None) -> dict:
        r"""
        Return the hyperedge data.

        Args:
            ``e_tuple`` (``Union[List, Set, Tuple]``): The hyperedge tuple: (v1_name, v2_name, ..., vn_name).
            ``default`` (``Any``): The default value if the hyperedge does not exist.
        """
        raise NotImplementedError

    def encode_e(self, e_tuple: Union[List, Set, Tuple]) -> Tuple:
        r"""
        Sort and check the hyperedge tuple.

        Args:
            ``e_tuple`` (``Union[List, Set, Tuple]``): The hyperedge tuple: (v1_name, v2_name, ..., vn_name).
        """
        raise NotImplementedError

    @cached_property
    def all_v(self) -> Set[Any]:
        r"""
        Return a set of all vertices in the hypergraph.
        """
        raise NotImplementedError

    @cached_property
    def all_e(self) -> Set[Tuple]:
        r"""
        Return a set of all hyperedges in the hypergraph.
        """
        raise NotImplementedError

    @cached_property
    def num_v(self) -> int:
        r"""
        Return the number of vertices in the hypergraph.
        """
        raise NotImplementedError

    @cached_property
    def num_e(self) -> int:
        r"""
        Return the number of hyperedges in the hypergraph.
        """
        raise NotImplementedError

    def add_v(self, v_id: Any, v_data: Optional[Dict] = None):
        r"""
        Add a vertex to the hypergraph.

        Args:
            ``v_id`` (``Any``): The vertex id.
            ``v_data`` (``Dict``, optional): The vertex data. Defaults to None.
        """
        raise NotImplementedError

    def add_e(self, e_tuple: Tuple, e_data: Optional[Dict] = None):
        r"""
        Add a hyperedge to the hypergraph.

        Args:
            ``e_tuple`` (``Tuple``): The hyperedge tuple: (v1_name, v2_name, ..., vn_name).
            ``e_data`` (``Dict``, optional): The hyperedge data.
        """
        raise NotImplementedError

    def remove_v(self, v_id: Any):
        r"""
        Remove a vertex from the hypergraph.

        Args:
            ``v_id`` (``Any``): The vertex id.
        """
        raise NotImplementedError

    def remove_e(self, e_tuple: Tuple):
        r"""
        Remove a hyperedge from the hypergraph.

        Args:
            ``e_tuple`` (``Tuple``): The hyperedge tuple: (v1_name, v2_name, ..., vn_name).
        """
        raise NotImplementedError

    def update_v(self, v_id: Any, v_data: Dict[Any, Any]):
        r"""
        Update the vertex data.

        Args:
            ``v_id`` (``Any``): The vertex id.
            ``v_data`` (``Dict[Any, Any]``): The vertex data.
        """
        raise NotImplementedError

    def update_e(self, e_tuple: Union[List[Any], Set[Any], Tuple[Any, ...]], e_data: Dict[Any, Any]):
        r"""
        Update the hyperedge data.

        Args:
            ``e_tuple`` (``Union[List[Any], Set[Any], Tuple[Any, ...]]``): The hyperedge tuple.
            ``e_data`` (``Dict[Any, Any]``): The hyperedge data.
        """
        raise NotImplementedError

    def has_v(self, v_id: Any) -> bool:
        r"""
        Return True if the vertex exists in the hypergraph.

        Args:
            ``v_id`` (``Any``): The vertex id.
        """
        raise NotImplementedError

    def has_e(self, e_tuple: Tuple) -> bool:
        r"""
        Return True if the hyperedge exists in the hypergraph.

        Args:
            ``e_tuple`` (``Tuple``): The hyperedge tuple: (v1_name, v2_name, ..., vn_name).
        """
        raise NotImplementedError

    def degree_v(self, v_id: Any) -> int:
        r"""
        Return the degree of the vertex.

        Args:
            ``v_id`` (``Any``): The vertex id.
        """
        raise NotImplementedError

    def degree_e(self, e_tuple: Tuple) -> int:
        r"""
        Return the degree of the hyperedge.

        Args:
            ``e_tuple`` (``Tuple``): The hyperedge tuple: (v1_name, v2_name, ..., vn_name).
        """
        raise NotImplementedError

    def nbr_e_of_v(self, v_id: Any) -> set:
        r"""
        Return the hyperedge neighbors of the vertex.

        Args:
            ``v_id`` (``Any``): The vertex id.
        """
        raise NotImplementedError

    def nbr_v_of_e(self, e_tuple: Tuple) -> set:
        r"""
        Return the vertex neighbors of the hyperedge.

        Args:
            ``e_tuple`` (``Tuple``): The hyperedge tuple: (v1_name, v2_name, ..., vn_name).
        """
        raise NotImplementedError

    def nbr_v(self, v_id: Any, exclude_self: bool = True) -> set:
        r"""
        Return the vertex neighbors of the vertex.

        Args:
            ``v_id`` (``Any``): The vertex id.
            ``exclude_self`` (``bool``): Whether to exclude the vertex itself from neighbors.
        """
        raise NotImplementedError

    def sub(self, v_name_list: List[str]):
        r"""
        Return the sub-hypergraph.

        Args:
            ``v_name_list`` (``List[str]``): The list of vertex ids.
        """
        raise NotImplementedError

    def sub_from_v(self, v_id: Any, depth: int):
        r"""
        Return the sub-hypergraph from the vertex.

        Args:
            ``v_id`` (``Any``): The vertex id.
            ``depth`` (``int``): The depth of the sub-hypergraph.
        """
        raise NotImplementedError

    def query_v(self, filters: Dict[str, Any]) -> List[str]:
        r"""
        Query and return vertices that match the given filters.

        Args:
            ``filters`` (``Dict[str, Any]``): A dictionary of conditions to filter vertices.
        """
        raise NotImplementedError

    def query_e(self, filters: Dict[str, Any]) -> List[Tuple]:
        r"""
        Query and return hyperedges that match the given filters.

        Args:
            ``filters`` (``Dict[str, Any]``): A dictionary of conditions to filter hyperedges.
        """
        raise NotImplementedError

    def stats(self) -> dict:
        r"""
        Return basic statistics of the hypergraph.
        """
        raise NotImplementedError

    def draw(self, port: int = 8080, open_browser: bool = True, blocking: bool = True):
        """
        Draw the hypergraph data of the current HyperDB instance

        Args:
            ``port``: Server port number, defaults to 8080
            ``open_browser``: Whether to automatically open the browser, defaults to True
            ``blocking``: Whether to block the main thread, defaults to True. Set to False for non-blocking mode.

        Returns:
            HypergraphViewer instance
        """
        from .draw import draw_hypergraph

        return draw_hypergraph(hypergraph_db=self, port=port, open_browser=open_browser, blocking=blocking)

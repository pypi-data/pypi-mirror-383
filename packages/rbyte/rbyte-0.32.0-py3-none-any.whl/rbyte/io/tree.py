from collections.abc import Callable

from optree import PyTree, tree_broadcast_map


class TreeBroadcastMapper:
    """A `pipefunc.PipeFunc`-friendly wrapper of `optree.tree_broadcast_map`."""

    __name__ = __qualname__  # ty: ignore[unresolved-reference]

    def __call__[T, U](  # noqa: PLR0913
        self,
        *,
        func: Callable[..., U],
        left: PyTree[T],
        right: PyTree[T],
        is_leaf: Callable[[T], bool] | None = None,
        none_is_leaf: bool = False,
        namespace: str = "",
    ) -> PyTree[U]:
        return tree_broadcast_map(
            func,
            left,
            right,
            is_leaf=is_leaf,
            none_is_leaf=none_is_leaf,
            namespace=namespace,
        )

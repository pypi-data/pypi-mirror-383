from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Literal,
    TypeAlias,
    TypeVar,
    TypeGuard,
)

from .cell import Cell

T = TypeVar("T")
R = TypeVar("R")
CoordSequence: TypeAlias = tuple[int, int] | list[int]
Index2D: TypeAlias = CoordSequence | Cell


def is_coord_sequence(obj: Any) -> TypeGuard[CoordSequence]:
    return (
        isinstance(obj, (tuple, list))
        and len(obj) == 2
        and isinstance(obj[0], int)
        and isinstance(obj[1], int)
    )


class Grid(Generic[T]):
    __slots__ = ("grid",)

    def __init__(self, grid: list[list[T]]):
        self.grid = grid

    @property
    def height(self):
        return len(self.grid)

    @property
    def width(self):
        return len(self.grid[0])

    @property
    def rows(self):
        return self.grid

    @property
    def columns(self):
        return [list(col) for col in zip(*self.grid)]

    def find(self, value: T) -> Generator[Cell, Any, None]:
        return (
            Cell(i, j)
            for i in range(self.height)
            for j in range(self.width)
            if self.grid[i][j] == value
        )

    def find_first(self, value: T) -> Cell | None:
        return next(self.find(value), None)

    def transpose(self) -> "Grid[T]":
        return Grid([list(col) for col in zip(*self.grid)])

    def rotate_clockwise(self) -> "Grid[T]":
        return Grid([list(col) for col in zip(*self.grid[::-1])])

    def rotate_counter_clockwise(self) -> "Grid[T]":
        return Grid([list(col) for col in zip(*self.grid)][::-1])

    def neighbours(
        self, cell: Cell, neighbour_type: Literal["cardinal", "diagonal", "all"]
    ) -> Generator[Cell, Any, None]:
        return (nb for nb in cell.neighbours(neighbour_type) if nb in self)

    def neighbour_directions(
        self, cell: Cell, neighbour_type: Literal["cardinal", "diagonal", "all"]
    ) -> Generator[tuple[int, int], Any, None]:
        return (
            direction
            for direction in cell.neighbour_directions(neighbour_type)
            if cell + direction in self
        )

    def copy(self) -> "Grid":
        return Grid([row[:] for row in self.grid])

    def items(self) -> Generator[tuple[Cell, T], Any, None]:
        for i in range(self.height):
            for j in range(self.width):
                yield Cell(i, j), self.grid[i][j]

    def map(self, func: Callable[[Cell, T], R]) -> "Grid[R]":
        new_grid = Grid.fill(self.height, self.width, None)

        for i in range(self.height):
            for j in range(self.width):
                new_grid.grid[i][j] = func(Cell(i, j), self.grid[i][j])

        return new_grid

    def apply(self, func: Callable[[Cell, T], None]) -> None:
        for cell, value in self.items():
            func(cell, value)

    def join_to_str(self, column_sep: str = "", row_sep: str = "\n") -> str:
        return row_sep.join(column_sep.join(map(str, row)) for row in self.grid)

    def get(self, cell: Index2D, default: T = None) -> T:
        if cell in self:
            return self[cell]
        return default

    def __getitem__(self, key: Index2D) -> T:
        if is_coord_sequence(key):
            return self.grid[key[0]][key[1]]
        if isinstance(key, Cell):
            return self.grid[key.row][key.column]
        raise TypeError(f"Invalid index type: {type(key).__name__}")

    def __setitem__(self, key: Index2D, value: T):
        if is_coord_sequence(key):
            self.grid[key[0]][key[1]] = value
        elif isinstance(key, Cell):
            self.grid[key.row][key.column] = value
        else:
            raise TypeError(f"Invalid index type: {type(key).__name__}")

    def __contains__(self, item: Index2D) -> bool:
        if is_coord_sequence(item):
            item1, item2 = item
        elif isinstance(item, Cell):
            item1, item2 = item.row, item.column
        else:
            raise TypeError(f"Invalid index type: {type(item)}")

        return 0 <= item1 < self.height and 0 <= item2 < self.width

    def __iter__(self):
        return (cell for row in self.grid for cell in row)

    def __repr__(self):
        s = "Grid(\n"
        for row in self.grid:
            s += f"    {row},\n"
        return s + ")"

    def __eq__(self, other):
        return isinstance(other, Grid) and self.grid == other.grid

    @staticmethod
    def fill(rows: int, columns: int, value: T) -> "Grid[T]":
        return Grid([[value] * columns for _ in range(rows)])

    @staticmethod
    def checkered(rows: int, columns: int, values: tuple[T, T]) -> "Grid[T]":
        return Grid(
            [[values[(i + j) % 2] for j in range(columns)] for i in range(rows)]
        )

    @staticmethod
    def from_function(rows: int, cols: int, func: Callable[[int, int], T]) -> "Grid[T]":
        return Grid([[func(i, j) for j in range(cols)] for i in range(rows)])

"""Cell- and lineage-related objects and functions."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeAlias

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import scipy.signal as sig

from delta import utils

Pole: TypeAlias = npt.NDArray[np.int16]


class CellDoesNotExistError(Exception):
    """The given cell does not exist."""


class CellNotOnFrameError(Exception):
    """The cell is not on the specified frame."""


class NonConsecutiveCellsError(Exception):
    """The cells are not consecutive."""


class OverlappingCellsError(Exception):
    """The cells overlap in time."""


class CellAlreadyHasDaughterError(Exception):
    """The cell already has a daughter at this frame."""


class CellDoesNotHaveMotherError(Exception):
    """The cell does not have a mother."""


@dataclass
class CellFeatures:
    """Container for cell features of a given cell at a given frame."""

    new_pole: Pole
    """Location of "Young" cell pole created after division of the septum."""
    old_pole: Pole
    """Location of "Old" cell pole that is maintained at division"""
    length: float = 0.0
    """Cell length, in pixels. Long axis of a rotated bounding box."""
    width: float = 0.0
    """Cell width, pixels. Short axis of a rotated bounding box."""
    area: float = 0.0
    """Cell area, in square pixels. Sum of pixels inside the contour."""
    perimeter: float = 0.0
    """Cell perimeter length, in pixels. Sum of pixels along the contour as
    computed by opencv's ``arcLength()`` function"""
    fluo: list[float] = field(default_factory=list)
    """Average (mean) fluorescence level(s) within cell contour."""
    edges: str = ""
    """String describing image edges touched by the cell. Can be a combination
    of the following: '-x', '+x', '-y', '+y'. Empty otherwise."""
    growthrate_length: float = np.nan
    """Growth rate of the cell length, see documentation."""
    growthrate_area: float = np.nan
    """Growth rate of the cell area, see documentation."""

    def __eq__(self, other: object) -> bool:
        """Equality function for CellFeatures."""
        if not isinstance(other, CellFeatures):
            return NotImplemented
        eq_new_pole = np.array_equal(self.new_pole, other.new_pole)
        eq_old_pole = np.array_equal(self.old_pole, other.old_pole)
        eq_length = np.allclose(self.length, other.length)
        eq_width = np.allclose(self.width, other.width)
        eq_area = np.allclose(self.area, other.area)
        eq_perimeter = np.allclose(self.perimeter, other.perimeter)
        eq_fluo = np.allclose(self.fluo, other.fluo)
        eq_edges = self.edges == other.edges
        eq_growthrate_length = np.allclose(
            self.growthrate_length, other.growthrate_length, equal_nan=True
        )
        eq_growthrate_area = np.allclose(
            self.growthrate_area, other.growthrate_area, equal_nan=True
        )
        eqs = [
            eq_new_pole,
            eq_old_pole,
            eq_length,
            eq_width,
            eq_area,
            eq_perimeter,
            eq_fluo,
            eq_edges,
            eq_growthrate_length,
            eq_growthrate_area,
        ]
        return all(eqs)

    def swap_poles(self) -> None:
        """Swap the new and old poles of the cell, in place."""
        self.new_pole, self.old_pole = self.old_pole, self.new_pole


@dataclass
class Cell:
    """Container for a cell across the movie."""

    motherid: int | None
    "Index of cell's mother"
    first_frame: int
    "Number of first frame of cell existence"
    _daughterids: list[int | None]
    _features: list[CellFeatures]

    @property
    def last_frame(self) -> int:
        """
        Return the last frame on which this cell appears.

        Returns
        -------
        last_frame : int
        """
        return self.first_frame + len(self._daughterids) - 1

    @property
    def frames(self) -> range:
        """
        Return the range of frame for which this cell is known.

        Returns
        -------
        frames : range
        """
        return range(self.first_frame, self.last_frame + 1)

    def features(self, frame: int) -> CellFeatures:
        """
        Return the cell features of the cell at a given frame.

        Parameters
        ----------
        frame : int
            Frame number.

        Returns
        -------
        cellfeatures : CellFeatures

        Raises
        ------
        CellNotOnFrameError
            If the cell is not present on the given frame.
        """
        if frame not in self.frames:
            raise CellNotOnFrameError
        return self._features[frame - self.first_frame]

    def daughterid(self, frame: int) -> int | None:
        """
        Return the daughter ID at a given frame, or None.

        Parameters
        ----------
        frame : int
            Frame number.

        Returns
        -------
        daughterid : int or None
            Index of the daughter. None if no division at frame.

        Raises
        ------
        CellNotOnFrameError
            If the cell is not present on the given frame.
        """
        if frame not in self.frames:
            raise CellNotOnFrameError
        return self._daughterids[frame - self.first_frame]

    def poles(self, frame: int) -> tuple[Pole, Pole]:
        """
        Return the poles of the cell at a given frame: (old_pole, new_pole).

        Parameters
        ----------
        frame : int
            Frame number.

        Returns
        -------
        old_pole : Pole
        new_pole : Pole

        Raises
        ------
        CellNotOnFrameError
            If the cell is not present on the given frame.
        """
        try:
            features = self.features(frame)
        except CellNotOnFrameError as err:
            raise CellNotOnFrameError from err
        return (features.old_pole, features.new_pole)


@dataclass
class Lineage:
    """
    Represents the cell lineages contained in a ROI.

    Only two functions are required to create a full lineage tree:
      * ``create`` and ``extend`` to create a cell and extend it frame
        after frame;

        .. code:: none

                           create(frame=0)
                            ------------>
            frames : 0....5....        0....5....
            cell #1:                   ╺

                           create(frame=5)
                            ------------>
            frames : 0....5....        0....5....
            cell #1: ╺╼╼╼╼╼╼╼╼╼        ╺╼╼╼╼╼╼╼╼╼
            cell #2:                        ╺

                     create(frame=5, motherid=1)
                            ------------>
            frames : 0....5....        0....5....
            cell #1: ╺╼╼╼╼╼╼╼╼╼        ╺╼╼╼╼┮╼╼╼╼
            cell #2:                        ┕

                           extend(cellid=2)
                            ------------>
            frames : 0....5....        0....5....
            cell #1: ╺╼╼╼╼┮╼╼╼╼        ╺╼╼╼╼┮╼╼╼╼
            cell #2:      ┕                 ┕╼


    To manipulate an already created tree, one needs four more:
      * ``split`` and ``merge``, to split a cell into two cells, and
        reverse the operation;
      * ``adopt``, to change the mother of a cell;
      * ``pivot``, to switch the roles of mother and daughter cells.

    The use of these methods is best illustrated by the following diagrams:

    .. code:: none

                      split(1, frame=5)
                        ------------>
        frames : 0....5....        0....5....
        cell #1: ╺╼╼╼╼╼╼╼╼╼        ╺╼╼╼╼
        cell #2:                        ╺╼╼╼╼
                        <------------
                         merge(2, 1)


                         adopt(2, 1)        pivot(2)        adopt(2, None)
                        ------------>     ------------>     ------------->
        frames : 0..3......        0..3......        0..3......        0..3......
        cell #1: ╺╼╼╼╼╼╼╼╼╼        ╺╼╼┮╼╼╼╼╼╼        ╺╼╼┮╼╼╼           ╺╼╼╼╼╼╼
        cell #2:    ╺╼╼╼              ┕╼╼╼              ┕╼╼╼╼╼╼           ╺╼╼╼╼╼╼
                        <------------     <------------     <-------------
                        adopt(2, None)       pivot(2)         adopt(2, 1)
    """

    cells: dict[int, Cell] = field(default_factory=dict)
    "Dictionary of cellids to ``Cell``s"

    def _order_descendants(self, cellid: int) -> list[int]:
        """Auxiliary function for ``__str__``."""
        descendants = [cellid]
        for daughterid in self.cells[cellid]._daughterids[::-1]:
            if daughterid is not None:
                descendants += self._order_descendants(daughterid)
        return descendants

    def _order_descendants_plot(
        self, cellid: int, *, frame: int | None = None, up: bool = True
    ) -> list[int]:
        cell = self.cells[cellid]
        if frame is None:
            frame = cell.first_frame
        for f in range(frame, cell.last_frame + 1):
            daughterid = cell.daughterid(f)
            if daughterid is None:
                continue
            mothers = self._order_descendants_plot(cellid, frame=f + 1, up=up)
            daughters = self._order_descendants_plot(daughterid, frame=f, up=not up)
            if up:
                return mothers + daughters
            return daughters + mothers
        return [cellid]

    def __str__(self) -> str:
        """Pretty-print the lineage tree."""
        # The second symbol is for the first frame of the cell,
        # the first one for all the others.
        # e.g. `symbols["normal"][is_first_frame]`
        symbols = {
            "ismother": "┮┍",
            "hasmother": "╼┕",
            "normal": "╼╺",
            "line": "│",
            "nothing": " ",
        }
        roots = [icell for icell, cell in self.cells.items() if cell.motherid is None]
        roots.sort(key=lambda icell: self.cells[icell].first_frame)
        strs = [
            "frames    : "
            + "."
            * (max((cell.last_frame for cell in self.cells.values()), default=-1) + 1)
        ]
        for rootid in roots:
            descendants = self._order_descendants(rootid)
            lines = [symbols["nothing"]] * (
                max((cell.last_frame for cell in self.cells.values()), default=-1) + 1
            )
            for descendantid in descendants:
                s = f"cell #{descendantid:04}: "
                cell = self.cells[descendantid]
                for frame in range(cell.last_frame + 1):
                    if frame not in cell.frames:
                        s += lines[frame]
                    else:
                        is_first_frame = cell.first_frame == frame
                        if is_first_frame:
                            lines[frame] = symbols["nothing"]
                        if cell.daughterid(frame) is not None:
                            s += symbols["ismother"][is_first_frame]
                            lines[frame] = symbols["line"]
                        elif cell.motherid is not None:
                            s += symbols["hasmother"][is_first_frame]
                        else:
                            s += symbols["normal"][is_first_frame]
                strs.append(s)
        return "\n".join(strs)

    def plot(
        self,
        *,
        order_key: Callable[[Cell], float] | None = None,
        ax: plt.Axes,
        colors: dict[int, tuple[float, float, float]] | None = None,
    ) -> plt.Axes:
        """
        Create a plot of the lineage tree on the provided ``ax``.

        Examples
        --------
        To plot lineages from vertical mothermachines you might want to
        order the initial cells in the order they have on the first frame
        of the mothermachine:

        .. code:: python

            import matplotlib.pyplot as plt


            def order_key(cell: Cell) -> int:
                # sort by the y coordinate of the first pole
                pole1, pole2 = cell.poles(cell.first_frame)
                return pole1[0]


            fig, ax = plt.subplots()
            roi.plot(order_key=order_key, ax=ax)
            plt.show()

        Parameters
        ----------
        order_key : Callable[[Cell], float] | None
            Function that takes a ``Cell`` and returns a number.
            The ordering of these numbers will determine the order of the mother
            cells on the figure.
        ax : plt.Axes | None
            The matplotlib axes object on which to plot the graph.
        """
        if order_key is None:
            order_key = lambda cell: cell.first_frame  # noqa: E731

        if ax is None:
            _, ax = plt.subplots()

        if colors is None:
            colors = utils.random_colors(sorted(self.cells.keys()))

        roots = [
            (icell, cell) for icell, cell in self.cells.items() if cell.motherid is None
        ]
        roots.sort(key=lambda icell_cell: order_key(icell_cell[1]))
        offset = len(self.cells)
        offsets = {}
        for rootid, _ in roots:
            descendants = self._order_descendants_plot(rootid)
            for i, descendantid in enumerate(descendants):
                offsets[descendantid] = offset - i
            for descendantid in descendants:
                cell = self.cells[descendantid]
                offsetd = offsets[descendantid]
                ax.plot(
                    [cell.first_frame, cell.last_frame],
                    [offsetd, offsetd],
                    color=colors[descendantid],
                )
                if cell.motherid is not None:
                    ax.plot(
                        [cell.first_frame, cell.first_frame],
                        [offsets[cell.motherid], offsetd],
                        color="black",
                    )
            offset -= len(descendants)

        return ax

    def compare(self, other: object, level: int = 0) -> list | None:  # type: ignore[type-arg]
        """Print or return the list of differences between two Lineage objects."""
        diffs: list[str | list] = []  # type: ignore[type-arg]
        if not isinstance(other, Lineage):
            diffs.append(utils.color_diff("", "Lineage", type(other)))
        else:
            diffs.append("Lineage")
            if len(self.cells) != len(other.cells):
                diffs.append(
                    utils.color_diff("# cells: ", len(self.cells), len(other.cells))
                )
            elif self.cells.keys() != other.cells.keys():
                a = sorted(self.cells.keys() - other.cells.keys())
                b = sorted(other.cells.keys() - self.cells.keys())
                diffs.append(
                    utils.color_diff("cell ids: ", f"{{...}}U{a}", f"{{...}}U{b}")
                )
            else:
                for cellid, cell in self.cells.items():
                    if cell != other.cells[cellid]:
                        diffs.append(
                            utils.color_diff("", f"cell {cellid}", f"cell {cellid}")
                        )
        if level == 0:
            utils.print_diffs(diffs)
            return None
        return diffs

    def create(
        self, frame: int, features: CellFeatures, motherid: int | None = None
    ) -> int:
        """
        Create a new cell at frame ``frame``.

        Parameters
        ----------
        frame : int
            The frame where the new cell appears for the first time.
        features : CellFeatures
            Cell features at first frame.
        motherid : int | None
            Cell ID of the mother cell, if there is one.
            The default is None.

        Returns
        -------
        cellid : int
            The cellid of the newly created cell.
        """
        cellid = max(self.cells.keys(), default=0) + 1
        assert cellid not in self.cells
        new_cell = Cell(
            motherid=None,
            first_frame=frame,
            _daughterids=[None],
            _features=[features],
        )
        self.cells[cellid] = new_cell
        self.adopt(cellid, motherid)
        return cellid

    def extend(self, cellid: int, features: CellFeatures) -> None:
        """
        Extend ``cellid`` with one more frame.

        Equivalent to creating a new cell and then merging it into ``cellid``,
        but avoids increasing the cell counter while doing so.

        Examples
        --------
        .. code:: none

            frames    : ......
            cell #0001: ╺╼╼╼╼

                extend(cellid=1, features=features)

            frames    : ......
            cell #0001: ╺╼╼╼╼╼

        """
        if cellid not in self.cells:
            raise CellDoesNotExistError
        self.cells[cellid]._daughterids.append(
            None
        )  # Daughter is adopted upon .create()
        self.cells[cellid]._features.append(features)

    def merge(self, cellid: int, merge_into_cellid: int) -> None:
        """
        Rename a cell (``cellid``) to merge it into another one (``merge_into_cellid``).

        The cells need to be exactly consecutive (i.e. ``cellid``'s first frame
        is one frame after ``merge_into_cellid``'s last frame).

        Inverse of ``split``.

        Examples
        --------
        .. code:: none

            frames    : ..........
            cell #0001: ╺╼╼╼╼
            cell #0002:      ╺╼╼╼╼

                merge(cellid=2, merge_into_cellid=1)

            frames    : ..........
            cell #0001: ╺╼╼╼╼╼╼╼╼╼

        Parameters
        ----------
        cellid : int
            The cellid of the cell to be renamed.
        merge_into_cellid : int
            The cellid of the cell that will incorporate the other one.
        """
        if cellid not in self.cells or merge_into_cellid not in self.cells:
            raise CellDoesNotExistError
        cell = self.cells[cellid]
        first_frame = cell.first_frame
        # Check if cells are exactly consecutive:
        if first_frame - 1 > self.cells[merge_into_cellid].last_frame:
            raise NonConsecutiveCellsError
        if first_frame - 1 < self.cells[merge_into_cellid].last_frame:
            error_msg = (
                f"#{cellid}: [{self.cells[cellid].first_frame}, {self.cells[cellid].last_frame}], "
                f"#{merge_into_cellid}: [{self.cells[merge_into_cellid].first_frame}, {self.cells[merge_into_cellid].last_frame}]"
            )
            raise OverlappingCellsError(error_msg)
        # Everything good, we proceed
        # Reassign cell daughter to new cell id
        for daughterid in cell._daughterids:
            if daughterid is not None:
                self.cells[daughterid].motherid = merge_into_cellid
        # Remove from old mother's list of daughters
        if cell.motherid is not None:
            mother = self.cells[cell.motherid]
            mother._daughterids[cell.first_frame - mother.first_frame] = None
        # Finally, append features and daughters lists to merged into cell
        self.cells[merge_into_cellid]._features += cell._features
        self.cells[merge_into_cellid]._daughterids += cell._daughterids
        del self.cells[cellid]

    def split(self, cellid: int, frame: int) -> int:
        """
        Break a cell lineage into two independent cell lineages.

        Inverse of ``merge``.

        Examples
        --------
        .. code:: none

            frames    : 0....5....
            cell #0001: ╺╼╼╼╼╼╼╼╼╼

                split(cellid=1, frame=5)

            frames    : 0....5....
            cell #0001: ╺╼╼╼╼
            cell #0002:      ╺╼╼╼╼

        Parameters
        ----------
        cellid : int
            The cellid of the cell to break.
        frame : int
            The frame number of the first frame of the new cell.

        Returns
        -------
        new_cellid : int
            The cellid of the newly created cell.
        """
        if cellid not in self.cells:
            raise CellDoesNotExistError
        cell = self.cells[cellid]
        if frame not in cell.frames:
            raise CellNotOnFrameError
        if cell.daughterid(frame) is not None:
            error_msg = "Cannot split at a frame where the cell divides."
            raise CellAlreadyHasDaughterError(error_msg)
        # Everything good, we can proceed.
        # Create new cell at frame, copy over features and daughters
        new_cellid = self.create(frame, cell.features(frame))
        self.cells[new_cellid]._features += cell._features[
            frame + 1 - cell.first_frame :
        ]
        self.cells[new_cellid]._daughterids = cell._daughterids[
            frame - cell.first_frame :
        ]
        # Remove features and daughters after frame for old cell
        cell._features = cell._features[: frame - cell.first_frame]
        cell._daughterids = cell._daughterids[: frame - cell.first_frame]
        # Reassign daughters to new cell
        for daughterid in self.cells[new_cellid]._daughterids:
            if daughterid is not None:
                self.cells[daughterid].motherid = new_cellid
        return new_cellid

    def adopt(self, cellid: int, motherid: int | None) -> None:
        """
        Attribute a new mother ``motherid`` (which can be ``None``) to the cell ``cellid``.

        The mother ``motherid`` needs to exist at the frame where
        the ``cellid`` appears for the first time, and not already
        have a daughter in the same frame.

        This function is its own inverse.

        Examples
        --------
        .. code:: none

            frames    : ..........
            cell #0001: ╺╼╼╼╼╼╼╼╼╼
            cell #0002:      ╺╼╼╼╼

                adopt(cellid=2, motherid=1)

            frames    : ..........
            cell #0001: ╺╼╼╼╼┮╼╼╼╼
            cell #0002:      ┕╼╼╼╼

                adopt(cellid=2, motherid=None)

            frames    : ..........
            cell #0001: ╺╼╼╼╼╼╼╼╼╼
            cell #0002:      ╺╼╼╼╼

        Parameters
        ----------
        cellid : int
            The cellid of the cell that will become the daughter.
        motherid : int | None
            The cellid of the cell that will become the mother.
        """
        if cellid not in self.cells:
            raise CellDoesNotExistError
        if motherid is not None and motherid not in self.cells:
            raise CellDoesNotExistError
        first_frame = self.cells[cellid].first_frame
        if (
            motherid is not None
            and self.cells[motherid].daughterid(first_frame) is not None
        ):
            raise CellAlreadyHasDaughterError
        # Everything good, we proceed.
        # If the cell had a mother, we erase it
        old_motherid = self.cells[cellid].motherid
        if old_motherid is not None:
            old_mother_frame_index = first_frame - self.cells[old_motherid].first_frame
            self.cells[old_motherid]._daughterids[old_mother_frame_index] = None
        # Now we link it to its new mother
        self.cells[cellid].motherid = motherid
        if motherid is not None:
            new_mother_frame_index = first_frame - self.cells[motherid].first_frame
            self.cells[motherid]._daughterids[new_mother_frame_index] = cellid

    def pivot(self, cellid: int) -> None:
        """
        Swap the roles between cell ``cellid`` and its mother.

        Examples
        --------
        .. code:: none

            frames    : .......
            cell #0001: ╺┮┮╼
            cell #0003:  │┕╼╼
            cell #0002:  ┕╼┮╼╼
            cell #0004:    ┕╼╼╼

                pivot(cellid=2)

            frames    : .......
            cell #0001: ╺┮╼┮╼╼
            cell #0004:  │ ┕╼╼╼
            cell #0002:  ┕┮╼
            cell #0003:   ┕╼╼
        """
        if cellid not in self.cells:
            raise CellDoesNotExistError
        cell = self.cells[cellid]
        if cell.motherid is None:
            raise CellDoesNotHaveMotherError
        motherid = cell.motherid
        # Splitting original mother cell
        self.adopt(cellid, None)
        new_cellid = self.split(motherid, cell.first_frame)
        # Merging the original daughter into the mother
        self.merge(cellid, motherid)
        # Renaming new_cellid into cellid
        self.cells[cellid] = self.cells[new_cellid]
        for daughterid in self.cells[cellid]._daughterids:
            if daughterid is not None:
                self.cells[daughterid].motherid = cellid
        del self.cells[new_cellid]
        # Attaching the new daughter cell to the new mother
        self.adopt(cellid, motherid)

    def swap_poles(self, cellid: int, frame: int | None = None) -> None:
        """
        Swap the poles of the cell ``cellid`` for all the frames or for frame ``frame`` onwards.

        This operation can lead to some tree reassignments if ``cellid`` has
        daughters, to respect the pole ages.

        Notes
        -----
        This function assumes that ``delta.utilities.track_poles`` and
        ``delta.utilities.division_poles`` are symmetrical with respect to
        ``prev_old`` and ``prev_new`` (i.e. switching ``prev_old`` and ``prev_new``
        also switch their results).
        """
        if cellid not in self.cells:
            raise CellDoesNotExistError
        cell = self.cells[cellid]
        if frame is None:
            frame = cell.first_frame
        if frame not in cell.frames:
            raise CellNotOnFrameError
        # Everything good, we proceed.
        cell.features(frame).swap_poles()
        for f in range(frame + 1, cell.last_frame + 1):
            daughterid = cell.daughterid(f)
            if daughterid is not None:
                self.pivot(daughterid)  # No need to recursively swap daughters poles
                return
            cell.features(f).swap_poles()

    def compute_growthrates(self, feature: str, smooth_frames: int = 7) -> None:
        r"""
        Compute the growth rates of all cells on all frames and store them.

        Essentially, if a cell and its daughter have the following lengths:

            m₀ ---> m₁ ---> m₂ -+-> m₃ ---> m₄ ---> m₅
                                |
                                +-> d₃ ---> d₄ ---> d₅

        Then the following ratios give the size increase:

                        mother                  daughter
            frame 1:    m₂ / m₀
            frame 2:    (m₃+d₃) / m₁
            frame 3:    m₄ / (m₂m₃/(m₃+d₃))     d₄ / (m₂d₃/(m₃+d₃))
            frame 4:    m₅ / m₃                 d₅ / d₃

        Notice that if we write the lengths in the following way:

                        mother                  daughter
            frame 0:    m₀
            frame 1:    m₁
            frame 2:    m₂                      m₂ / (1+m₃/d₃)
            frame 3:    m₃ (1+d₃/m₃)            d₃
            frame 4:    m₄ (1+d₃/m₃)            d₄
            frame 5:    m₅ (1+d₃/m₃)            d₅

        Then dividing frame+1 by frame-1 always gives the correct growth ratios.
        We add another similar factor for each division.

        This function just does the same thing directly in log, to avoid lengths
        increasing too much during long experiments.

        The values computed are in units of ``1/frame``, because DeLTA doesn't
        know the interval between frames. To convert these values into other
        units, they should be divided by the interval between frames, in any
        unit, for example, if frames are 5 minutes apart and you want the
        growth rate in ``1/h``:

        .. code:: none

            GR[1/h] = GR[DeLTA] / (5 / 60)
            -------   ---------   -------- Interval between frames in [h/frame]
                   \           \
                    \           Growth rate given by DeLTA in [1/frame]
                     \
                      Growth rate in [1/h]

        Parameters
        ----------
        feature : str
            Feature to use for the growth rate computation, typically "length"
            or "area".
        smooth_frames : int, default 7
            Size of the centered window over which to smooth the growth rate.
        """
        if feature not in {"length", "area"}:
            error_msg = "Growth rate can only be computed based on length or area."
            raise ValueError(error_msg)
        if smooth_frames < 3:
            error_msg = "The size of the centered window must be at least 3."
            raise ValueError(error_msg)

        def all_log_values(
            cellid: int | None, until_daughterid: int | None = None
        ) -> tuple[list[float], float]:
            """
            Compute the log of the values (area or length) of ``cellid``.

            It starts from its earliest ancestor and ends at ``until_daughterid``
            or at the last frame of the cell if None. The values are adjusted to
            remove the jump associated with every division.
            """
            if cellid is None:
                return [], 0.0
            cell = self.cells[cellid]
            # Recursively computing the log values of the ancestors until cellid
            log_values, log_div_ratio = all_log_values(cell.motherid, cellid)
            # Finally, computing the log values of cellid
            for frame in cell.frames:
                value = cell.features(frame).__dict__[feature]
                # If there is a division we need to update log_div_ratio
                if (daughterid := cell.daughterid(frame)) is not None:
                    daughter_value = (
                        self.cells[daughterid].features(frame).__dict__[feature]
                    )
                    if daughterid == until_daughterid:
                        log_div_ratio += np.log1p(value / daughter_value)
                        return log_values, log_div_ratio
                    log_div_ratio += np.log1p(daughter_value / value)
                # Storing the log value adjusted by log_div_ratio
                log_values.append(np.log(value) + log_div_ratio)
            return log_values, log_div_ratio

        for cellid, cell in self.cells.items():
            log_values, _ = all_log_values(cellid)

            if len(log_values) >= 2:
                # Taking the derivative and smoothing with the Savitsky-Golay filter
                window_length = min(smooth_frames, len(log_values))
                growth_rates = sig.savgol_filter(
                    log_values,
                    window_length=window_length,
                    polyorder=min(1, window_length - 1),
                    deriv=1,
                )
            else:
                # Returning np.nan instead of 0 if the growthrate can't be computed
                growth_rates = [np.nan] * len(log_values)

            # Cutting growthrate to correct length (life of cell)
            growth_rates = growth_rates[-len(cell.frames) :]

            # Storing the growthrate values in the cell structures
            for frame, growth_rate in zip(cell.frames, growth_rates, strict=True):
                if feature == "length":
                    cell.features(frame).growthrate_length = growth_rate
                else:
                    cell.features(frame).growthrate_area = growth_rate

"""Crystal structure generation step of ASSYST."""

from dataclasses import dataclass
from collections.abc import Sequence
from itertools import product, islice
from warnings import catch_warnings, warn
from typing import Self, Iterable, Iterator, Literal, overload, Union

from .filters import DistanceFilter

from ase import Atoms
import numpy as np
from pyxtal import pyxtal as _pyxtal
from pyxtal.msg import Comp_CompatibilityError
from pyxtal.tolerance import Tol_matrix
from tqdm.auto import tqdm


def pyxtal(
    group: Union[int, list[int]],
    species: tuple[str],
    num_ions: tuple[int],
    dim=3,
    repeat=1,
    allow_exceptions=True,
    **kwargs,
) -> Union[Atoms, list[dict]]:
    """
    Generate random crystal structures with PyXtal.

    `group` must be between 1 and the largest possible value for the given dimensionality:
        dim=3 => 1 - 230 (space groups)
        dim=2 => 1 -  80 (layer groups)
        dim=1 => 1 -  75 (rod groups)
        dim=0 => 1 -  58 (point groups)

    When `group` is passed as a list of integers or `repeat>1`, generate multiple structures and return them in a list
    of dicts containing the keys `atoms`, `symmetry` and `repeat` for the ASE structure, the symmetry group
    number and which iteration it is, respectively.

    Args:
        group (list of int, or int): the symmetry group to generate or a list of them
        species (tuple of str): which species to include, defines the stoichiometry together with `num_ions`
        num_ions (tuple of int): how many of each species to include, defines the stoichiometry together with `species`
        dim (int): dimensionality of the symmetry group, 0 is point groups, 1 is rod groups, 2 is layer groups and 3 is space groups
        repeat (int): how many random structures to generate
        allow_exceptions (bool): when generating multiple structures, silence errors when the requested stoichiometry and symmetry group are incompatible
        **kwargs: passed to `pyxtal.pyxtal` function verbatim

    Returns:
        :class:`~.Atoms`: the generated structure, if repeat==1 and only one symmetry group is requested
        list of dict of all generated structures, if repeat>1 or multiple symmetry groups are requested

    Raises:
        ValueError: if `species` and `num_ions` are not of the same length
        ValueError: if stoichiometry and symmetry group are incompatible and allow_exceptions==False or only one structure is requested
    """

    if len(species) != len(num_ions):
        raise ValueError(
            "species and num_ions must be of same length, "
            f"not {species} and {num_ions}!"
        )
    stoich = "".join(f"{s}{n}" for s, n in zip(species, num_ions))

    def generate(group):
        s = _pyxtal()
        try:
            s.from_random(
                dim=dim, group=group, species=species, numIons=num_ions, **kwargs
            )
        except Comp_CompatibilityError:
            if not allow_exceptions:
                raise ValueError(
                    f"Symmetry group {group} incompatible with stoichiometry {stoich}!"
                ) from None
            else:
                return None
        s = s.to_ase()
        s.wrap(center=(0, 0, 0))
        return s

    # return a single structure
    if repeat == 1 and isinstance(group, int):
        allow_exceptions = False
        return generate(group)
    else:
        structures = []
        if isinstance(group, int):
            group = [group]
        failed_groups = []
        for g in tqdm(group, desc="Spacegroups"):
            for i in range(repeat):
                s = generate(g)
                if s is None:
                    failed_groups.append(g)
                    continue
                structures.append({"atoms": s, "symmetry": g, "repeat": i})
        if len(failed_groups) > 0:
            warn(
                f"Groups [{', '.join(map(str, failed_groups))}] could not be generated with stoichiometry {stoich}!",
                stacklevel=2,
            )
        return structures


@dataclass(eq=True, frozen=True)
class Formulas(Sequence):
    """Simple helper to generate lists of structure compositions.

    :func:`.sample_space_groups` is the intended consumer and expects an iterable of dictionaries, where each dictionary
    maps an element name to the number of atoms of this type in one structure.
    :class:`.Formulas` behaves as if it were such a tuple, but extends the basic python arithmetic operations to make
    building the list a bit simpler.

    The class can be initialized from any tuple of dictionaries.

    >>> el_manual = Formulas(({'Cu': 1}, {'Cu': 2}))

    :meth:`.range` is a helper class method that initializes `Formulas` for a single element and takes the same
    arguments as the builtin `range`, except that it skips the zero.

    >>> el = Formulas.range('Cu', 3)
    Formulas(atoms=({'Cu': 1}, {'Cu': 2}))
    >>> el == el_manual
    True

    Addition is overloaded to the addition of the underlying tuples.

    >>> Formulas.range('Cu', 1, 5) == Formulas.range('Cu', 1, 3) + Formulas.range('Cu', 3, 5)

    The bitwise or operation is akin to the inner product

    >>> Formulas.range('Cu', 3) | Formulas.range('Ag', 3)
    Formulas(atoms=({'Cu': 1, 'Ag': 1}, {'Cu': 2, 'Ag': 2}))

    >>> Formulas.range('Cu', 3) * Formulas.range('Ag', 3)
    Formulas(atoms=({'Cu': 1, 'Ag': 1}, {'Cu': 2, 'Ag': 1}, {'Cu': 1, 'Ag': 2}, {'Cu': 2, 'Ag': 2}))
    """

    atoms: tuple[dict[str, int], ...]

    @property
    def elements(self) -> set[str]:
        """Set of elements present in elements."""
        e: set[str] = set()
        for s in self.atoms:
            e = e.union(s.keys())
        return e

    @classmethod
    def range(cls, elements: str | Iterable[str], *range_args) -> Self:
        """Creates formulas with number of atoms as given by the builtin `range`.

        Multiple elements are combined as the outer product."""
        if isinstance(elements, str):
            return cls(tuple({elements: i} for i in range(*range_args)))
        formulas = [cls.range(e, *range_args) for e in elements]
        total = formulas[0]
        for f in formulas[1:]:
            total *= f
        return total

    def __add__(self, other: Self) -> Self:
        """Extend underlying list of stoichiometries."""
        return type(self)(self.atoms + other.atoms)

    def __or__(self, other: Self) -> Self:
        """Inner product of underlying stoichiometries.

        Truncates to the length of the shortest of the two element sequences.
        Must not share elements with other.elements."""
        assert self.elements.isdisjoint(
            other.elements
        ), "Can only or stoichiometries of different elements!"
        s: tuple[dict[str, int], ...] = ()
        for me, you in zip(self.atoms, other.atoms):
            s += (me | you,)
        return type(self)(s)

    def __mul__(self, other: Self) -> Self:
        """Outer product of underlying stoichiometries.

        Must not share elements with other.elements."""
        assert self.elements.isdisjoint(
            other.elements
        ), "Can only multiply stoichiometries of different elements!"
        s: tuple[dict[str, int], ...] = ()
        for me, you in product(self.atoms, other.atoms):
            s += (me | you,)
        return type(self)(s)

    # Sequence Impl'
    @overload
    def __getitem__(self, index: int) -> dict[str, int]: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[dict[str, int]]: ...
    def __getitem__(self, index):
        return self.atoms[index]

    def __len__(self) -> int:
        return len(self.atoms)

    def trim(self, min_atoms: int = 1, max_atoms: int | None = None) -> Self:
        """Returns a copy of itself with formulas with lesser or more atoms than given limits removed."""
        if max_atoms is not None:
            return type(self)(
                tuple(f for f in self if min_atoms <= sum(f.values()) <= max_atoms)
            )
        else:
            return type(self)(tuple(f for f in self if min_atoms <= sum(f.values())))


def sample_space_groups(
    formulas: Formulas | Iterable[dict[str, int]],
    spacegroups: list[int] | tuple[int, ...] | Iterable[int] | None = None,
    min_atoms: int = 1,
    max_atoms: int = 10,
    max_structures: int | None = None,
    dim: Literal[0, 1, 2, 3] = 3,
    tolerance: (
        Literal["metallic", "atomic", "molecular", "vdW"] | DistanceFilter | dict
    ) = "metallic",
) -> Iterator[Atoms]:
    """
    Create symmetric random structures.

    Args:
        formulas (Formulas or iterable of dicts from str to int): list of chemical formulas
        spacegroups (list of int): which space groups to generate
        max_atoms (int): do not generate structures larger than this
        max_structures (int): generate at most this many structures
        dim (one of 0, 1, 2, or 3): the dimensionality of the structures to generate; if lower than 3 the code generates
            samples no longer from space groups, but from the subperiodic layer, rod, or point groups.
        tolerance (str, dict of elements to radii):
            specifies minimum allowed distances between atoms in generated structures;
            if str then it should be one values understood by :class:`pyxtal.tolerace.Tol_matrix`;
            if dict each value gives the minimum *radius* allowed for an atom, whether a given distance is allowed then
            depends on the sum of the radii of the respective elements

    Yields:
        `Atoms`: random symmetric crystal structures
    """

    if not 0 <= dim <= 3:
        raise ValueError(f"dim must be in range [0, 3], not {dim}!")

    # number of (sub-)periodic symmetry groups available in 0-3 dimensions
    max_group = [58, 75, 80, 230][dim]

    if spacegroups is None:
        spacegroups = range(1, max_group + 1)
    spacegroups = list(spacegroups)

    min_spg = min(spacegroups)
    max_spg = max(spacegroups)
    if min_spg <= 0 or max_group < max_spg:
        raise ValueError(
            f"spacegroups must be in range [1, {max_group}], not [{min_spg}, {max_spg}] (dim={dim})!"
        )

    tm: Tol_matrix | None
    match tolerance:
        case "metallic" | "atomic" | "molecular" | "vdW":
            tm = Tol_matrix(prototype=tolerance)
        case dict():
            tm = (
                DistanceFilter(tolerance).to_tol_matrix()
                if len(tolerance) > 0
                else None
            )
        case DistanceFilter():
            tm = tolerance.to_tol_matrix()
        case _:
            raise ValueError("invalid value tolerance={tolerance}!")

    for stoich in (bar := tqdm(formulas)):
        # pyxtal never returns structures when one element with zero atoms is present, so filter here first for
        # robustness
        stoich = {e: n for e, n in stoich.items() if n > 0}
        if len(stoich) == 0:
            continue
        elements, num_atoms = zip(*stoich.items())
        if not min_atoms <= sum(num_atoms) <= max_atoms:
            continue
        stoich_str = "".join(f"{s}{n}" for s, n in zip(elements, num_atoms))
        bar.set_description(stoich_str)

        def pop(s):
            atoms = s.pop("atoms")
            atoms.info.update(s)
            return atoms

        with catch_warnings(category=UserWarning, action="ignore"):
            px = pyxtal(spacegroups, elements, num_atoms, dim=dim, tm=tm)
            yield from islice(map(pop, px), max_structures)
            if max_structures is not None:
                max_structures -= len(px)
                if max_structures <= 0:
                    break

"""
Convenience shorts to create ASE calculators to be used inside ASSYST.

Exists mostly to avoid passing around potentially large and unpickle-able calculator objects.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from functools import lru_cache
import os

from ase.calculators.calculator import Calculator
from ase.calculators.morse import MorsePotential
from pyiron_snippets.import_alarm import ImportAlarm

with ImportAlarm(
    "grace-tensorpotential required; install with "
    "'conda install -c conda-forge grace-tensorpotential' or 'pip install tensorpotential'",
    raise_exception=True,
) as grace_alarm:
    from tensorpotential.calculator import grace_fm


class AseCalculatorConfig(ABC):
    """Base class to keep calculator configurations."""

    @abstractmethod
    def get_calculator(self) -> Calculator:
        """Return the actual calculator object.

        Returns:
            :class:`ase.calculators.calculator.Calculator`: the actually usable calculator
        """
        pass


@dataclass(frozen=True, eq=True)
class Grace(AseCalculatorConfig):
    """Universal Graph Atomic Cluster Expansion models.

    .. attention::
        This class needs additional dependencies!
        Install `tensorpotential` from `PyPI <https://pypi.org/project/tensorpotential/>`__.
    """

    model: str = "GRACE-FS-OAM"

    @lru_cache(maxsize=1)
    @grace_alarm
    def get_calculator(self) -> Calculator:
        # disable tensorflow warnings noise
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        return grace_fm(self.model)


@dataclass(frozen=True, eq=True)
class Morse(AseCalculatorConfig):
    """Morse potential for testing.  Parameters as in ASE."""

    epsilon: float = 1.0
    r0: float = 1.0
    rho0: float = 1.0

    def get_calculator(self) -> Calculator:
        return MorsePotential(**asdict(self))

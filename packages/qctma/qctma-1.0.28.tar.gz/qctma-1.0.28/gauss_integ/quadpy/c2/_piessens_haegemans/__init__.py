import pathlib

from ...helpers import article
from .._helpers import _read, register

source = article(
    authors=["Robert Piessens", "Ann Haegemans"],
    title="Cubature Formulas of Degree Nine for Symmetric Planar Regions",
    journal="Mathematics of Computation",
    volume="29",
    number="11",
    month="jul",
    year="1975",
    pages="810-815",
    url="https://doi.org/10.1090/S0025-5718-1975-0368393-5",
)

this_dir = pathlib.Path(__file__).resolve().parent


def piessens_haegemans_1():
    return _read(this_dir / "piessens_haegemans_1.json", source)


def piessens_haegemans_2():
    return _read(this_dir / "piessens_haegemans_2.json", source)


register([piessens_haegemans_1, piessens_haegemans_2])

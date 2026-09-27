from collections import defaultdict
import datetime
import itertools
import logging
import unidecode

import parkrun
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.models.event import Event
from parkrun.models.runner import Runner

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, force=True)

ELEMENTS: set[str] = set(map(lambda s: s.strip().lower(), "H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn, Fr, Ra, Ac, Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr, Rf, Db, Sg, Bh, Hs, Mt, Ds, Rg, Cn, Uut, Fl, Uup, Lv, Uus, Uuo".split(",")))

logger.debug("Loaded %d elements", len(ELEMENTS))

ELEMENTS_PER_INITIAL: dict[str, set[str]] = defaultdict(set)
for element in ELEMENTS:
    ELEMENTS_PER_INITIAL[element[0]].add(element)

logger.debug("Loaded %d elements per initial: %s", sum(len(i) for i in ELEMENTS_PER_INITIAL.values()), ELEMENTS_PER_INITIAL)


def per_letter(location_names: set[str], elements: set[str]) -> tuple[int, dict[str, str], set[str]]:
    """
    Given a set of location names that all start with the same initial and a set
    of elements that also start with this initial, return the best assignment of
    locations to elements where in any assignment, all of the remaining letters
    of the element are in the location name.
    """

    initial: str = list(elements)[0][0]
    logger.debug(initial)

    max_valid: int = 0
    max_assignment: dict[str, str] = dict()
    max_unassigned: set[str] = set()
    for elements_order in itertools.permutations(elements, r=min(len(elements), len(location_names))):
        num_valid: int = 0
        assignment: dict[str, str] = dict()
        unassigned: set[str] = set()
        for location_name, element in zip(location_names, elements_order):
            if element[1:] == "" or all(letter in location_name[1:] for letter in element[1:]):
                num_valid += 1
                assignment[element] = location_name
            else:
                unassigned.add(location_name)
        if len(max_assignment) == 0 or num_valid > max_valid:
            max_valid = num_valid
            max_assignment = assignment
            max_unassigned = unassigned

        # Don't try extra permutations if already got all
        if max_valid == len(elements):
            break

    for element in elements:
        if element not in max_assignment:
            max_assignment[element] = ""

    assignment_str = "\n".join(f"\t{element}: {location_name}" for element, location_name in max_assignment.items())
    print(f"\n\n{initial}: {max_valid}/{len(elements)}\nAssignment:\n{assignment_str}\nUnassigned: {max_unassigned}")

    return max_valid, max_assignment, max_unassigned


def periodic_table(runner_id: int, start_date: datetime.date, end_date: datetime.date) -> None:
    runner: Runner = fetch_runner_results(runner_id, start_date, end_date)
    unique_location_names: set[str] = set(map(lambda event: unidecode.unidecode(event.name).strip().lower(), runner.unique_locations))

    max_valid: int = 0
    assignment: dict[str, str] = dict()
    unassigned: set[str] = set()
    for initial, elements in ELEMENTS_PER_INITIAL.items():
        location_names = {location_name for location_name in unique_location_names if location_name.lower().startswith(initial)}
        max_valid_initial, assignment_initial, unassigned_initial = per_letter(location_names, elements)
        max_valid += max_valid_initial
        assignment.update(assignment_initial)
        unassigned.update(unassigned_initial)

    assignment_str: str = "\n".join(f"\t{element}: {location_name}" for element, location_name in sorted(assignment.items()))
    unassigned_str: str = "\n".join(f"- {location_name}" for location_name in sorted(unassigned))
    print(f"\n\nOverall {max_valid}/{len(ELEMENTS)}:\nAssignment:\n{assignment_str}\nUnassigned:\n{unassigned_str}")

if __name__ == "__main__":
    periodic_table(parkrun.PARKRUNNERS_ENV_NAME_TO_ID["ME"], datetime.date.min, datetime.date.max)

from collections import deque
import datetime
import logging
import unidecode
from typing import Sequence

import parkrun
from parkrun.api.scraper_runner import fetch_runner_results
from parkrun.models.runner import Runner

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, force=True)

ELEMENTS: Sequence[str] = "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og".split()

logger.debug("Loaded %d elements", len(ELEMENTS))


def normalise(name: str) -> str:
    """
    Return the name in the form used for comparisons: accents removed and
    lowercase.
    """

    return unidecode.unidecode(name).strip().lower()


def can_spell(element: str, location_name: str) -> bool:
    """
    Return whether the location name can be used for the element. It can if it
    starts with the element's first letter and each of the element's remaining
    letters appears somewhere in the rest of the name, in any order.
    """

    element = normalise(element)
    location_name = normalise(location_name)
    return location_name.startswith(element[0]) and all(letter in location_name[1:] for letter in element[1:])


def best_assignment(elements: Sequence[str], location_names: Sequence[str]) -> dict[str, str]:
    """
    Return an assignment of elements to locations with as many elements
    assigned as possible, where each location is used at most once and each
    element is only assigned a location it can spell. Where there is a choice
    of which locations to use, locations earlier in location_names are
    preferred, so pass them in order of priority (e.g. first visited first).

    This is maximum bipartite matching: locations on one side, elements on the
    other, and an edge wherever the location can spell the element. It is
    solved with Kuhn's augmenting path algorithm:

    Go through the locations one at a time, trying to find each one an element
    while keeping every location assigned so far assigned (possibly to a
    different element). If one of the elements the current location can spell
    is free, take it. Otherwise, one of the locations holding those elements
    could move to a different element it can spell, freeing its element for the
    current location. If that element isn't free either, its location could
    move too, and so on. A chain of moves ending in a free element is an
    "augmenting path" and applying it increases the number of assigned elements
    by one without unassigning any location.

    The augmenting path is found with a breadth-first search so that it is the
    shortest possible, i.e. it moves the fewest already assigned locations. In
    particular, a free element is always taken if there is one. This keeps
    assignments as stable as possible as locations are added over time.

    If no augmenting path exists for a location then it can't be assigned
    without unassigning another, so it is left unassigned. It can be proven
    that this greedy order never has to be revisited: a location with no
    augmenting path now will never gain one later, so the result is optimal.

    Since a location, once assigned, only ever moves to a different element
    and never becomes unassigned, earlier locations are never given up in
    favour of later ones. So of all the optimal assignments, this uses the
    earliest locations possible. It also means that computing the assignment
    from scratch with a new location added to the end gives the same result as
    adding the new location to the previous assignment.

    Each location's search visits each element at most once, so the whole
    thing takes at most locations * edges steps.
    """

    # Precompute the edges of the graph: which elements each location could be
    # used for, in the given order of elements for deterministic results.
    candidates: dict[str, list[str]] = {
        location_name: [element for element in elements if can_spell(element, location_name)]
        for location_name in location_names
    }
    element_to_location: dict[str, str] = dict()
    location_to_element: dict[str, str] = dict()

    def try_assign(new_location_name: str) -> bool:
        """
        Try to assign the new location an element using the shortest augmenting
        path. Return whether this succeeded.
        """

        # Breadth-first search over locations that could move. For each element
        # reached, record which location in the search reached it so the path
        # can be followed back. Each element is only reached once, so the first
        # time is by the shortest path, and elements already reached are skipped
        # to avoid going round in circles.
        queue: deque[str] = deque([new_location_name])
        reached_from: dict[str, str] = dict()
        while queue:
            location_name = queue.popleft()
            for element in candidates[location_name]:
                if element in reached_from:
                    continue
                reached_from[element] = location_name

                if element in element_to_location:
                    # Taken, so try moving its location in a later step of the search
                    queue.append(element_to_location[element])
                    continue

                # Free, so apply the augmenting path: follow it back to the new
                # location, moving each location on it to the element after it
                while True:
                    location_name = reached_from[element]
                    previous_element = location_to_element.get(location_name)
                    if previous_element is not None:
                        logger.debug("Moving %s from %s to %s", location_name, previous_element, element)
                    element_to_location[element] = location_name
                    location_to_element[location_name] = element
                    if location_name == new_location_name:
                        return True
                    assert previous_element is not None
                    element = previous_element

        return False

    for location_name in location_names:
        if not try_assign(location_name):
            logger.debug("Could not assign %s from candidates %s", location_name, candidates[location_name])

    return element_to_location


def periodic_table(runner_id: int, start_date: datetime.date, end_date: datetime.date) -> None:
    runner: Runner = fetch_runner_results(runner_id, start_date, end_date)
    # Results are most recent first so reverse to get locations in order of first visit
    location_names: list[str] = list(dict.fromkeys(result.location.name for result in reversed(runner.results)))
    assignment: dict[str, str] = best_assignment(ELEMENTS, location_names)
    assigned_location_names: set[str] = set(assignment.values())
    unassigned_location_names: list[str] = [location_name for location_name in location_names if location_name not in assigned_location_names]

    assignment_str: str = "\n".join(f"\t{element}: {assignment.get(element, '')}" for element in ELEMENTS)
    unassigned_str: str = "\n".join(f"- {location_name}" for location_name in unassigned_location_names)
    print(f"Overall {len(assignment)}/{len(ELEMENTS)}:\nAssignment:\n{assignment_str}\nUnassigned locations:\n{unassigned_str}")


if __name__ == "__main__":
    periodic_table(parkrun.PARKRUNNERS_ENV_NAME_TO_ID["ME"], datetime.date.min, datetime.date.max)

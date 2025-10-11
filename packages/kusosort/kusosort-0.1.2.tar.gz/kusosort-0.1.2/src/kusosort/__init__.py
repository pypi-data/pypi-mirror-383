from ._kusosort_impl import (
    bogo_sort_int, bogo_sort_float, bogo_sort_string,
    bozo_sort_int, bozo_sort_float, bozo_sort_string,
    stalin_sort_int, stalin_sort_float, stalin_sort_string,
    miracle_sort_int, miracle_sort_float, miracle_sort_string,
    abe_sort_int, abe_sort_float, abe_sort_string,
    quantum_bogo_sort_multiverse_int, quantum_bogo_sort_multiverse_float, quantum_bogo_sort_multiverse_string
)
from typing import List, TypeVar, Callable

T = TypeVar('T', int, float, str)

def _get_sort_function_set(data: List[T]):
    """Helper function to return the correct set of C++ functions based on the list's type."""
    if not data: return (None,) * 7
    if isinstance(data[0], str):
        return ( bogo_sort_string, bozo_sort_string, stalin_sort_string, miracle_sort_string, abe_sort_string, None, quantum_bogo_sort_multiverse_string)
    elif isinstance(data[0], float) or any(isinstance(x, float) for x in data):
        return ( bogo_sort_float, bozo_sort_float, stalin_sort_float, miracle_sort_float, abe_sort_float, None, quantum_bogo_sort_multiverse_float)
    else:
        return ( bogo_sort_int, bozo_sort_int, stalin_sort_int, miracle_sort_int, abe_sort_int, None, quantum_bogo_sort_multiverse_int)

# --- Public API with new, shorter names ---

def bogo(data: List[T]) -> None:
    bogo_fn, *_, = _get_sort_function_set(data)
    if bogo_fn: bogo_fn(data)

def bozo(data: List[T]) -> None:
    _, bozo_fn, *_, = _get_sort_function_set(data)
    if bozo_fn: bozo_fn(data)

def stalin(data: List[T]) -> List[T]:
    *_, stalin_fn, _, _, _, _ = _get_sort_function_set(data)
    stalin_fn = _get_sort_function_set(data)[2]
    return stalin_fn(data) if stalin_fn else []

def miracle(data: List[T], max_attempts: int = 10, prey: Callable[[], None] = None) -> None:
    def default_prey(): print("The miracle did not happen...")
    user_prey = prey if prey is not None else default_prey
    miracle_fn = _get_sort_function_set(data)[3]
    if miracle_fn:
        success = miracle_fn(data, max_attempts, user_prey)
        if not success: print("The miracle didn't happen, and the list was not sorted.")

def abe(data: List[T]) -> None:
    abe_fn = _get_sort_function_set(data)[4]
    if abe_fn:
        result = abe_fn(data)
        data[:] = result

def quantum_bogo(data: List[T], num_universes: int = 1) -> None:
    if num_universes < 1: print("At least one universe is required."); return
    if len(data) <= 1: print("The list is already sorted."); return

    *_, qbsm_fn = _get_sort_function_set(data)
    if not qbsm_fn: return

    successful_universes = qbsm_fn(data, num_universes)
    success_indices = {result[0] for result in successful_universes}

    print(f"Executing Quantum Bogo Sort across {num_universes} universes...")
    for i in range(1, num_universes + 1):
        if i in success_indices:
            sorted_array = [res[1] for res in successful_universes if res[0] == i][0]
            print(f"✅ Universe {i}: Sort successful! Result: {sorted_array}")
        else:
            print(f"💥 Universe {i} was destroyed.")
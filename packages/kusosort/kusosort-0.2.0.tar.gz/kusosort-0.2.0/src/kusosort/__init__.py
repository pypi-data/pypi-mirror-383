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
    if not data:
        return (None, None, None, None, None, None, None)
    
    # Check for string type first
    if isinstance(data[0], str):
        return (bogo_sort_string, bozo_sort_string, stalin_sort_string, miracle_sort_string, abe_sort_string, None, quantum_bogo_sort_multiverse_string)
    # Check for float type
    elif any(isinstance(x, float) for x in data):
        return (bogo_sort_float, bozo_sort_float, stalin_sort_float, miracle_sort_float, abe_sort_float, None, quantum_bogo_sort_multiverse_float)
    # Default to integer type
    else:
        return (bogo_sort_int, bozo_sort_int, stalin_sort_int, miracle_sort_int, abe_sort_int, None, quantum_bogo_sort_multiverse_int)

# --- Public API with new, shorter names ---

def _default_progress_printer(current_array: list):
    """A default function to print the sorting progress on a single line."""
    # \r moves the cursor to the beginning of the line, effectively overwriting it.
    print(f"Sorting... current state: {current_array}", end='\r')


def bogo(data: List[T], verbose: bool = False) -> List[T]:
    """Sorts a list using Bogo Sort. Returns a new sorted list."""
    # If verbose is True, use the default printer. Otherwise, do nothing.
    callback = _default_progress_printer if verbose else lambda arr: None
    
    func_set = _get_sort_function_set(data)
    bogo_fn = func_set[0]
    
    result = bogo_fn(data, callback) if bogo_fn else []

    if verbose:
        print()
    
    return result

def bozo(data: List[T], verbose: bool = False) -> List[T]:
    """Sorts a list using Bozo Sort. Returns a new sorted list."""
    # If verbose is True, use the default printer. Otherwise, do nothing.
    callback = _default_progress_printer if verbose else lambda arr: None

    func_set = _get_sort_function_set(data)
    bozo_fn = func_set[1]

    result = bozo_fn(data, callback) if bozo_fn else []

    if verbose:
        print()

    return result

def stalin(data: List[T]) -> List[T]:
    """Sorts a list using Stalin Sort. Returns a new list."""
    func_set = _get_sort_function_set(data)
    stalin_fn = func_set[2]
    return stalin_fn(data) if stalin_fn else []

def miracle(data: List[T], max_attempts: int = 10, prey: Callable[[], None] = None) -> List[T]:
    """
    Waits for a miracle to sort the list.
    Returns the final state of the list (sorted or not).
    """
    def default_prey(): print("The miracle did not happen...")
    user_prey = prey if prey is not None else default_prey
    func_set = _get_sort_function_set(data)
    miracle_fn = func_set[3]
    
    if not miracle_fn:
        return []

    result = miracle_fn(data, max_attempts, user_prey)
    # Check if the returned list is sorted to print the message
    is_sorted = all(result[i] <= result[i+1] for i in range(len(result)-1))
    if not is_sorted:
        print("The miracle didn't happen, and the list was not sorted.")
    
    return result

def abe(data: List[T]) -> List[T]:
    """Sorts a list using Abe Sort (running maximum). Returns a new list."""
    func_set = _get_sort_function_set(data)
    abe_fn = func_set[4]
    return abe_fn(data) if abe_fn else []

def quantum_bogo(data: List[T], num_universes: int = 1) -> None:
    """Performs one step of Bogo sort in multiple parallel universes."""
    if num_universes < 1: 
        print("Warning: At least one universe is required.") 
        return data
    if len(data) <= 1: 
        print("The list is already sorted.")
        return data

    func_set = _get_sort_function_set(data)
    qbsm_fn = func_set[6]
    if not qbsm_fn: return

    successful_universes = qbsm_fn(data, num_universes)
    success_indices = {result[0] for result in successful_universes}

    print(f"Executing Quantum Bogo Sort across {num_universes} universes...")
    for i in range(1, num_universes + 1):
        if i in success_indices:
            sorted_array = [res[1] for res in successful_universes if res[0] == i][0]
            print(f"Universe {i}: Sort successful! Result: {sorted_array}")
        else:
            print(f"Universe {i} was destroyed.")

    if successful_universes:
        # Return the sorted list from the first successful universe
        return successful_universes[0][1]
    else:
        # Return the original, unmodified list if all failed
        return data
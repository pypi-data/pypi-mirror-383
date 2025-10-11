# tests/test_sorts.py

import pytest
import kusosort
import sys

# --- Test Datasets ---
# Using @pytest.fixture allows reusing the same data across multiple tests
@pytest.fixture
def basic_list():
    """A basic list for general testing."""
    return [8, 3, 1, 5, 4]

@pytest.fixture
def empty_list():
    """An empty list."""
    return []

@pytest.fixture
def single_element_list():
    """A list with only one element."""
    return [42]

@pytest.fixture
def sorted_list():
    """A pre-sorted list."""
    return [1, 2, 3, 4, 5]

@pytest.fixture
def reverse_sorted_list():
    """A list sorted in reverse order."""
    return [5, 4, 3, 2, 1]

@pytest.fixture
def duplicate_elements_list():
    """A list containing duplicate elements."""
    return [4, 1, 3, 4, 2, 1]

@pytest.fixture
def negative_numbers_list():
    """A list containing negative numbers."""
    return [-5, 1, -8, 4, 0]

# --- 1. Stalin Sort Tests ---
class TestStalinSort:
    def test_basic_case(self, basic_list):
        """Tests if it works correctly on a basic list."""
        assert kusosort.stalin(basic_list) == [8]

    def test_empty_list(self, empty_list):
        """Tests if it returns an empty list when given one."""
        assert kusosort.stalin(empty_list) == []

    def test_single_element(self, single_element_list):
        """Tests if a single-element list is returned as is."""
        assert kusosort.stalin(single_element_list) == [42]

    def test_already_sorted(self, sorted_list):
        """Tests if a pre-sorted list remains unchanged."""
        assert kusosort.stalin(sorted_list) == [1, 2, 3, 4, 5]

    def test_reverse_sorted(self, reverse_sorted_list):
        """Tests if a reverse-sorted list results in only the first element."""
        assert kusosort.stalin(reverse_sorted_list) == [5]

    def test_with_duplicates(self, duplicate_elements_list):
        """Tests if it works correctly with duplicate elements."""
        assert kusosort.stalin(duplicate_elements_list) == [4, 4]

    def test_with_negative_numbers(self, negative_numbers_list):
        """Tests if it works correctly with negative numbers."""
        assert kusosort.stalin(negative_numbers_list) == [-5, 1, 4]

    def test_original_list_is_not_modified(self, basic_list):
        """Ensures that the original list is not modified."""
        original_copy = basic_list.copy()
        kusosort.stalin(basic_list)
        assert basic_list == original_copy

# --- 2. Abe Sort Tests ---
class TestAbeSort:
    def test_running_maximum_case(self):
        """Tests the 'running maximum' implementation of Abe Sort."""
        data = [3, 5, 2, 8, 4]
        kusosort.abe(data)
        assert data == [3, 5, 5, 8, 8]

    def test_reverse_sorted_case(self, reverse_sorted_list):
        """Tests a reverse-sorted list, which should become a list of the first element."""
        data = reverse_sorted_list.copy()
        kusosort.abe(data)
        assert data == [5, 5, 5, 5, 5]

    def test_already_sorted_is_unchanged(self, sorted_list):
        """Tests that a sorted list remains unchanged."""
        data = sorted_list.copy()
        kusosort.abe(data)
        assert data == sorted_list

    def test_empty_list(self, empty_list):
        """Tests if an empty list remains empty."""
        data = empty_list.copy()
        kusosort.abe(data)
        assert data == []

    def test_single_element(self, single_element_list):
        """Tests if a single-element list remains unchanged."""
        data = single_element_list.copy()
        kusosort.abe(data)
        assert data == [42]

# --- 3. Miracle Sort Tests ---
class TestMiracleSort:
    def test_already_sorted_succeeds(self, sorted_list, capsys):
        """Ensures a miracle occurs for a sorted list and no failure message is printed."""
        data = sorted_list.copy()
        kusosort.miracle(data)
        captured = capsys.readouterr()
        assert "was not sorted" not in captured.out
        assert data == [1, 2, 3, 4, 5]

    def test_unsorted_fails_with_message(self, basic_list, capsys):
        """Ensures a failure message is printed for an unsorted list."""
        data = basic_list.copy()
        kusosort.miracle(data, max_attempts=3)
        captured = capsys.readouterr()
        assert "was not sorted" in captured.out

    def test_already_sorted_succeeds_with_pray(self, sorted_list, capsys):
        def my_prayer():
            print("GOD")
            data = sorted_list.copy()
            kusosort.miracle(data, max_attempts=3, prey=my_prayer)
            captured = capsys.readouterr()
            assert "was not sorted" not in captured.out
            assert data == [1, 2, 3, 4, 5]
     
    def test_unsorted_fails_with_message_with_prey(self, basic_list, capsys):
        """Ensures a failure message is printed for an unsorted list."""
        def my_prayer():
            print("GOD")
        data = basic_list.copy()
        kusosort.miracle(data, max_attempts=3, prey=my_prayer)
        captured = capsys.readouterr()
        assert "was not sorted" in captured.out

# --- 4. Quantum Bogo Sort Tests ---
class TestQuantumBogoSort:
    def test_already_sorted_succeeds(self, sorted_list, capsys):
        """Ensures all universes succeed (are not destroyed) for a sorted list."""
        kusosort.quantum_bogo(sorted_list.copy(), num_universes=5)
        captured = capsys.readouterr()
        # Checks that the "destroyed" message is not present
        assert "destroyed" not in captured.out
        # Checks that the "successful" message appears 5 times
        assert captured.out.count("Sort successful") == 5

    def test_unsorted_reports_destruction_and_success(self, capsys):
        """Checks that both success and destruction are reported for a high-probability case."""
        # A 2-element list has a 50% chance of being sorted
        data = [2, 1]
        kusosort.quantum_bogo(data, num_universes=10)
        captured = capsys.readouterr()
        # Checks that both messages are likely present in the output
        assert "destroyed" in captured.out
        assert "successful" in captured.out

# --- 5. Bogo Sort / Bozo Sort Tests ---
# WARNING: These tests are probabilistic and may fail in very rare cases.
class TestChaoticSorts:
    @pytest.mark.skipif(sys.platform == "win32", reason="Timeout may not work well on Windows CI")
    @pytest.mark.timeout(10) # Fails the test if it doesn't complete in 10 seconds
    def test_bogo_simple(self):
        """Tests if a 3-element bogo sort finishes in a reasonable time."""
        data = [2, 3, 1]
        kusosort.bogo(data)
        assert data == [1, 2, 3]

    @pytest.mark.skipif(sys.platform == "win32", reason="Timeout may not work well on Windows CI")
    @pytest.mark.timeout(10)
    def test_bozo_simple(self):
        """Tests if a 3-element bozo sort finishes in a reasonable time."""
        data = [2, 3, 1]
        kusosort.bozo(data)
        assert data == [1, 2, 3]
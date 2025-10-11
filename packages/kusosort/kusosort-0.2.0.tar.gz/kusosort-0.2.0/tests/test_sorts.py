import pytest
import kusosort
import sys

# --- Test Data Fixtures ---
# Prepares various types of data for reuse across tests.

@pytest.fixture
def unsorted_int_list():
    """Provides a basic unsorted list of integers."""
    return [3, 1, 5, 2, 4]

@pytest.fixture
def unsorted_float_list():
    """Provides an unsorted list of floats."""
    return [3.14, 1.61, 2.71]

@pytest.fixture
def unsorted_str_list():
    """Provides an unsorted list of strings."""
    return ["c", "a", "d", "b"]

# --- Generic Tests for Deterministic Sorts ---

class TestDeterministicSorts:
    # Use parametrize to run the same test with different data for multiple functions
    @pytest.mark.parametrize("sort_func_name", ["stalin", "abe"])
    @pytest.mark.parametrize("input_data, expected_stalin, expected_abe", [
        ([], [], []),                                  # Empty list
        ([42], [42], [42]),                            # Single element list
        ([1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]),      # Pre-sorted list
        ([5, 4, 3, 2, 1], [5], [5, 5, 5, 5, 5]),        # Reverse-sorted list
        ([2, 1, 3, 2], [2, 3], [2, 2, 3, 3]),          # List with duplicates
        ([-5, 1, -8, 0], [-5, 1], [-5, 1, 1, 1]),   # List with negative numbers
        (["c", "a", "d", "b"], ["c", "d"], ["c", "c", "d", "d"]), # List of strings
    ])
    def test_various_cases(self, sort_func_name, input_data, expected_stalin, expected_abe):
        """Tests multiple edge cases for stalin and abe sort."""
        sort_func = getattr(kusosort, sort_func_name)
        original_copy = input_data.copy()

        # Choose the correct expected output based on the function being tested
        expected_data = expected_stalin if sort_func_name == "stalin" else expected_abe
        
        result = sort_func(input_data)

        assert result == expected_data
        assert input_data == original_copy # Verify original list is untouched

# --- Algorithm-Specific Tests ---

class TestMiracleSort:
    def test_already_sorted_returns_sorted(self, unsorted_int_list):
        """Ensures that for a pre-sorted list, the list is returned unmodified."""
        sorted_list = sorted(unsorted_int_list)
        original_copy = sorted_list.copy()
        
        result = kusosort.miracle(sorted_list, max_attempts=3)
        
        assert result == original_copy
        assert sorted_list == original_copy # Verify original is untouched

    def test_unsorted_returns_unsorted(self, unsorted_int_list):
        """Ensures it returns the original unsorted list after all attempts fail."""
        original_copy = unsorted_int_list.copy()
        
        result = kusosort.miracle(original_copy, max_attempts=3)
        
        assert result == original_copy
        assert unsorted_int_list == original_copy # Verify original is untouched
    
    def test_already_sorted_succeeds_with_pray(self, unsorted_int_list):
        def my_prayer():
            print("GOD")
        sorted_list = sorted(unsorted_int_list)
        original_copy = sorted_list.copy()
        result = kusosort.miracle(original_copy, max_attempts=3, prey=my_prayer)
        assert result == original_copy
        assert sorted_list == original_copy # Verify original is untouched
            
    def test_unsorted_returns_unsorted_with_pray(self, unsorted_int_list):
        """Ensures it returns the original unsorted list after all attempts fail."""
        def my_prayer():
            print("GOD")
        original_copy = unsorted_int_list.copy()
        
        result = kusosort.miracle(original_copy, max_attempts=3, prey=my_prayer)
        
        assert result == original_copy
        assert unsorted_int_list == original_copy # Verify original is untouched

class TestChaoticSorts:
    # These tests are probabilistic and slow, so we use small inputs and timeouts.
    @pytest.mark.parametrize("sort_func_name", ["bogo", "bozo"])
    @pytest.mark.parametrize("input_data, sorted_data", [
        ([2, 1], [1, 2]),                             # Small integers
        ([3.14, 1.61], [1.61, 3.14]),                  # Small floats
        (["b", "a"], ["a", "b"]),                       # Small strings
    ])
    @pytest.mark.timeout(60) # Increased timeout for potentially slower operations
    def test_chaotic_sorts_with_verbose(self, sort_func_name, input_data, sorted_data):
        """
        Tests bogo and bozo sort with verbose output.
        Verifies it returns a new sorted list and does not modify the original.
        """
        sort_func = getattr(kusosort, sort_func_name)
        original_copy = input_data.copy()

        print(f"\n--- Testing {sort_func_name} on {original_copy} with verbose=True ---")
        result = sort_func(input_data, verbose=True)
        print(f"--- {sort_func_name} test complete ---")

        assert result == sorted_data
        assert input_data == original_copy # Verify original is untouched

class TestQuantumBogoSort:
    def test_quantum_bogo_visual_inspection(self):
        """
        A test specifically for visually inspecting the output of quantum_bogo.
        This test does not use capsys, so output will be printed to the console
        when run with 'pytest -s'.
        """
        print("\n--- [Visual Inspection] Running quantum_bogo with an unsorted list ---")
        data = [2, 1, 4, 3]
        
        # This function's print statements will be visible during the test run
        kusosort.quantum_bogo(data, num_universes=15)
        
        # This test only checks that the function runs without error,
        # the main purpose is visual confirmation of the output.
        assert True
        
    def test_sorted_reports_only_success(self, capsys):
        """
        Tests that for a pre-sorted list, only success messages are printed.
        """
        data = [1, 2, 3]
        kusosort.quantum_bogo(data, num_universes=5)
        
        # capsys.readouterr() captures all print output
        captured = capsys.readouterr()
        output = captured.out

        # 1. Check for the initial header message
        assert "Executing Quantum Bogo Sort across 5 universes..." in output
        
        # 2. Check that the success message appears 5 times
        assert output.count("Sort successful!") == 5
        
        # 3. CRUCIAL: Check that the destruction message does NOT appear
        assert "was destroyed." not in output

    def test_unsorted_reports_destruction_and_success(self, capsys):
        """
        Checks that for an unsorted list, both success and destruction
        messages are reported.
        """
        # A 2-element list is guaranteed to produce both outcomes over 10 trials
        data = [2, 1]
        kusosort.quantum_bogo(data, num_universes=10)
        
        captured = capsys.readouterr()
        output = captured.out

        # 1. Check for the initial header message
        assert "Executing Quantum Bogo Sort across 10 universes..." in output
        
        # 2. Check that the success message is present at least once
        assert "Sort successful!" in output
        
        # 3. Check that the destruction message is present at least once
        assert "was destroyed." in output
    
    def test_sorted_list_prints_and_returns_correctly(self, capsys):
        """
        Tests that a pre-sorted list returns itself and only prints success messages.
        """
        data = [1, 2, 3]
        
        # Function call
        result = kusosort.quantum_bogo(data, num_universes=5)
        
        # 1. Test the return value
        assert result == [1, 2, 3]
        
        # 2. Test the printed output
        captured = capsys.readouterr()
        output = captured.out
        assert "successful" in output
        assert "destroyed" not in output

    def test_unsorted_list_prints_and_returns_correctly(self, capsys):
        """
        Tests that an unsorted list returns the correct result (sorted or original)
        and prints the correct messages.
        """
        # --- Case 1: Success is highly likely ---
        data_simple = [2, 1]
        result_success = kusosort.quantum_bogo(data_simple, num_universes=20)
        
        # 1a. Test the return value (should be sorted)
        assert result_success == [1, 2]

        # 1b. Test the printed output
        captured_success = capsys.readouterr()
        assert "successful" in captured_success.out
        assert "destroyed" in captured_success.out

        # --- Case 2: Failure is highly likely ---
        data_complex = [5, 4, 3, 2, 1]
        original_copy = data_complex.copy()
        result_failure = kusosort.quantum_bogo(data_complex, num_universes=1)
        
        # 2a. Test the return value (should be the original list)
        assert result_failure == original_copy
        
        # 2b. Test the printed output
        captured_failure = capsys.readouterr()
        assert "successful" not in captured_failure.out
        assert "destroyed" in captured_failure.out
# kusosort

A collection of joke sorting algorithms implemented in C++ for Python.
For educational and entertainment purposes only.

## Installation

```bash
pip install kusosort
```

## Usage

```python
import kusosort
import random

# スターリンソート
unsorted_list = [1, 5, 2, 6, 3, 4, 0]
sorted_list = kusosort.stalin(unsorted_list)
print(f"Original: {unsorted_list}")
# Original: [1, 5, 2, 6, 3, 4, 0]
print(f"Stalin sorted: {sorted_list}")
# Stalin sorted: [1, 5, 6]

# ミラクルソート
data = [3, 1, 2]

def my_prayer():
    print("神よ...")

kusosort.miracle(data, max_attempts=3, prey=my_prayer)
# 神よ...
# 神よ...
# 神よ...
# 奇跡は起きず、ソートできませんでした

# ボゴソート (注意: 終わらない可能性があります)
# data = random.sample(range(10), 10)
# kusosort.bogo_sort(data)
# print(f"Bogo sorted: {data}")
```

## Algorithms

- `bogo(data)`
- `bozo(data)`
- `stalin(data)`
- `miracle(data, max_attempts=10, prey=None)`
- `abe_(data)`
- `quantum_bogo(data)`
# Notes
- Dataset is acquired from [kaggle](https://www.kaggle.com/datasets/pratyushpuri/grocery-store-sales-dataset-in-2025-1900-record)
- Every command or execution is run on `capstone-module-1/` directory
- The only help I got from LLM is for `read_input` function, the rest are stackoverflow and official docs. 
And it's also heavily modified anyway. For reference, here is what the LLM answered:
```python
from typing import TypeVar, Type, Any

T = TypeVar("T")

def to_type(value: Any, target_type: Type[T]) -> T:
    """
    Convert value into the given target_type, if possible.
    
    Args:
        value: The input value to convert.
        target_type: The type to convert into.
    
    Returns:
        Converted value of type T.
    """
    return target_type(value)
```

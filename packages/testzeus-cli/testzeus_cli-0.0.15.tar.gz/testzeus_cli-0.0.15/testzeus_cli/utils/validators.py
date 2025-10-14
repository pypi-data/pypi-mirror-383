"""
Input validation utilities for TestZeus CLI.
"""

from typing import Dict, List, Optional, TypeVar, Union
import re

T = TypeVar("T")


def validate_required_arg(value: Optional[T], name: str) -> T:
    """
    Validate that a required argument is provided

    Args:
        value: Argument value to validate
        name: Name of the argument for error message

    Returns:
        The value if valid

    Raises:
        ValueError: If the value is None
    """
    if value is None:
        raise ValueError(f"Required argument '{name}' is missing")
    return value


def validate_id(id_value: str, entity_type: str = "entity") -> str:
    """
    Validate that an ID is in the correct format for PocketBase

    Args:
        id_value: ID value to validate
        entity_type: Type of entity for error message

    Returns:
        The validated ID

    Raises:
        ValueError: If the ID is invalid
    """
    if (
        not id_value
        or not isinstance(id_value, str)
        or len(id_value) != 15
        or not id_value.isalnum()
    ):
        raise ValueError(
            f"Invalid {entity_type} ID: must be 15 alphanumeric characters"
        )
    return id_value.strip()


def parse_key_value_pairs(pairs: List[str]) -> Dict[str, Union[str, Dict[str, Union[str, List[str]]]]]:
    """
    Parse a list of key=value pairs into a dictionary with operator support

    Args:
        pairs: List of strings in 'key<operator>value' format
               Examples: 'tags?=urgent,important', 'status=ready'

    Returns:
        Dictionary of parsed key-value pairs with operators
        Example: {
            "tags": {"operator": "?=", "value": ["urgent", "important"]},
            "status": "ready"
        }

    Raises:
        ValueError: If any pair doesn't follow the expected format
    """
    result = {}
    
    # Define supported operators (order matters - longer operators first)
    operators = ['?=', '=']
    
    for pair in pairs:
        if not pair.strip():
            continue
            
        # Find the operator in the pair
        found_operator = None
        key = None
        value_part = None
        
        for op in operators:
            if op in pair:
                parts = pair.split(op, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value_part = parts[1].strip()
                    found_operator = op
                    break
        
        if not found_operator or not key or value_part is None:
            raise ValueError(
                f"Invalid format for key-value pair: '{pair}'. Expected 'key<operator>value' where operator is one of: {', '.join(operators)}"
            )
        
        # Parse values (split by comma for multiple values)
        values = [v.strip() for v in value_part.split(',') if v.strip()]
        
        if not values:
            raise ValueError(
                f"No values provided for key '{key}' in pair: '{pair}'"
            )
        
        # Handle different operators
        if found_operator == '=':
            # For simple equality, return just the value (single value only)
            if len(values) == 1:
                result[key] = values[0]
            else:
                # Multiple values with = operator should still use the complex format
                result[key] = {
                    "operator": found_operator,
                    "value": values
                }
        else:
            # For other operators, use the complex format
            result[key] = {
                "operator": found_operator,
                "value": values
            }
    
    return result

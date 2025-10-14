"""
Text processing utilities for string manipulation, formatting, and analysis.

This module provides functions for:
- Converting lists to DokuWiki table format
- Finding string occurrences with context
- Pretty-printing nested dictionaries
- Extracting substrings between delimiters
- Displaying items in column format
- Extracts price from a string and returns it as float
"""

from itertools import zip_longest
from collections.abc import Iterable
from typing import List, Dict, Any, Union
import re


def list_to_doku_wiki_table(data: List[List[str]]) -> None:
    """
    Convert a 2D list to DokuWiki table format and print it.
    
    The first row is treated as headers (with ^ delimiters),
    subsequent rows are treated as data (with | delimiters).
    
    Args:
        data: 2D list where first row contains headers
        
    Example:
        >>> data = [['Name', 'Age'], ['Alice', '25'], ['Bob', '30']]
        >>> list_to_doku_wiki_table(data)
        ^ Name ^ Age ^
        | Alice | 25 |
        | Bob | 30 |
    """
    if not data or not data[0]:
        return
        
    print(f'^ {" ^ ".join(data[0])} ^')
    for line in data[1:]:
        print(f'| {" | ".join(line)} |')


def find_all_occurrences(input_string: str, str_to_find: str, print_len: bool = True) -> List[int]:
    """
    Find all starting positions of a substring in a string.
    
    Args:
        input_string: The string to search in
        str_to_find: The substring to find
        print_len: Whether to print the number of occurrences found
        
    Returns:
        List of starting positions where the substring was found
        
    Example:
        >>> find_all_occurrences("hello world hello", "hello")
        occurrences found: 2
        [0, 12]
    """
    start_index = 0
    positions = []
    
    while start_index != -1:
        start_index = input_string.find(str_to_find, start_index)
        if start_index != -1:
            positions.append(start_index)
            start_index += 1

    if print_len:
        print(f'occurrences found: {len(positions)}')

    return positions


def print_dict(data: Union[Dict[str, Any], List[Any]], depth: int = 0, indent: int = 2, max_depth: int = 99) -> None:
    """
    Pretty-print nested dictionaries and lists with indentation.
    
    Args:
        data: Dictionary or list to print
        depth: Current depth level (for recursion)
        indent: Number of spaces per indentation level
        max_depth: Maximum depth to print (prevents infinite recursion)
        
    Example:
        >>> data = {'key1': ['item1', 'item2'], 'key2': {'nested': 'value'}}
        >>> print_dict(data)
        * key1
        - item1
        - item2
        * key2
          * nested
    """
    if depth <= max_depth:
        if isinstance(data, list):
            if depth < max_depth:
                for item in data:
                    if isinstance(item, str):
                        print(f'- {" " * (indent * (depth + 1))}{item}')
                    elif isinstance(item, dict):
                        print_dict(item, depth + 1, indent, max_depth)
            else:
                print(f'. {" " * (indent * depth)}>')
        elif isinstance(data, dict):
            for (key, value) in data.items():
                print(f'* {" " * (indent * depth)}{key}')
                if isinstance(value, list):
                    print_dict(value, depth, indent, max_depth)
                elif isinstance(value, dict):
                    print_dict(value, depth + 1, indent, max_depth)
    else:
        print(f'. {" " * (indent * depth)}>')


def print_if_found(
        input_string: str,
        str_to_find: str,
        len_to_print: int,
        do_print: bool = True,
        print_empty: bool = False) -> List[str]:
    """
    Find occurrences of a substring and print surrounding context.
    
    Args:
        input_string: The string to search in
        str_to_find: The substring to find
        len_to_print: Total length of context to show around each occurrence
        do_print: Whether to print the results
        print_empty: Whether to print a message if nothing is found
        
    Returns:
        List of context strings around each occurrence
        
    Example:
        >>> print_if_found("hello world hello", "world", 10)
        llo world 
        ['llo world ']
    """
    result = []
    start_indexes = find_all_occurrences(input_string, str_to_find, print_len=False)
    
    for start_index in start_indexes:
        start_pos = max(0, start_index - (len_to_print // 2))
        end_pos = start_index + (len_to_print // 2) + len(str_to_find)
        context = input_string[start_pos:end_pos]
        
        if do_print:
            print(f'\n{context}\n')
        result.append(context)
        
    if print_empty and not result:
        print('Not Found.')
        
    return result


def substring_between(
        input_string: str,
        start_string: str,
        end: Union[str, int],
        start_offset: int = 0) -> List[str]:
    """
    Extract substrings between start and end markers.
    
    Args:
        input_string: The string to extract from
        start_string: The starting delimiter
        end: The ending delimiter (string) or length (int)
        start_offset: Offset to apply before the start position
        
    Returns:
        List of extracted substrings
        
    Example:
        >>> substring_between("start{content}end start{more}end", "start{", "}", 0)
        ['content}', 'more}']
    """
    result = []
    start_indexes = find_all_occurrences(input_string, start_string, print_len=False)
    start_offset = abs(start_offset)
    
    for start_index in start_indexes:
        adjusted_start = max(start_index - start_offset, 0)
        substring = input_string[adjusted_start:]
        
        if isinstance(end, str):
            end_index = substring.find(end)
            if end_index != -1:
                result.append(substring[:end_index + len(end)])
        elif isinstance(end, int):
            result.append(substring[:end])
            
    return result


def print_in_columns(
        items: List[Any],
        num_cols: int = 2,
        add_spaces: int = 2,
        return_type: str = '') -> Union[List[str], List[tuple], None]:
    """
    Display items in a column format with proper alignment.
    
    Args:
        items: List of items to display
        num_cols: Number of columns
        add_spaces: Additional spaces between columns
        return_type: Return format ('raw' for tuples, any other string for formatted strings)
        
    Returns:
        None (prints output), list of formatted strings, or list of tuples
        
    Example:
        >>> print_in_columns(['a', 'b', 'c', 'd'], num_cols=2)
        a  c
        b  d
    """
    if not items:
        return [] if return_type else None
        
    # Handle matrix input (nested iterables)
    if items and not isinstance(items[-1], str) and isinstance(items[-1], Iterable):
        items = [elem for col in zip(*items) for elem in col]
    
    num_items = len(items)
    (quotient, remainder) = divmod(num_items, num_cols)
    rows = quotient + (1 if remainder > 0 else 0)
    
    # Create columns using slicing
    columns = [items[i*rows: (i+1)*rows] for i in range(num_cols)]
    
    # Calculate maximum width for each column
    col_widths = [max((len(str(x)) for x in col), default=0) for col in columns]

    # Return raw tuples if requested
    if return_type and 'raw' in return_type:
        return [row for row in zip_longest(*columns, fillvalue='')]

    # Create formatted strings
    joiner = ' ' * add_spaces
    result = []
    
    for row in zip_longest(*columns, fillvalue=''):
        formatted_row = joiner.join(f'{item:<{w}}' for item, w in zip(row, col_widths))
        result.append(formatted_row)
        
    if return_type:
        return result
    else:
        print('\n'.join(result))
        return None


def extract_number(text: str, strict: bool = True) -> float:
    """
    Extracts a number from text and returns it as float.

    Gracefully handles various text formats containing numbers,
    including those with commas, currency symbols, and other characters.

    Args:
        text: String containing numeric information
        strict: If True, raises ValueError when no number is found.
                If False, returns 0.0 when no number is found (default: True)

    Returns:
        float: Extracted number

    Raises:
        ValueError: When strict=True and no number is found,
                   or when multiple decimal points exist

    Examples:
        >>> extract_number("1,234.56원")
        1234.56
        >>> extract_number("₩ 1_234_567")
        1234567.0
        >>> extract_number("2,500 items")
        2500.0
        >>> extract_number("Score: 98.5%")
        98.5
        >>> extract_number("text only", strict=False)
        0.0
        >>> extract_number("text only", strict=True)
        ValueError: No number found

    Test Examples:
        # strict=True (default) tests
        test_cases = [
            ("1,234.56원", 1234.56),
            ("₩ 2,500", 2500.0),
            ("1_000_000", 1000000.0),
            ("3,456.78 (including tax)", 3456.78),
            ("USD 99.99 [discounted]", 99.99),
            ("Score: 85.5", 85.5),
            ("Temperature: -12.3°C", 12.3),  # Note: minus sign not preserved
        ]

        # strict=False tests
        lenient_cases = [
            ("1,234.56원", 1234.56),
            ("no number here", 0.0),
            ("text only", 0.0),
            ("", 0.0),
            (None, 0.0),
            ("100 items", 100.0),
            ("free (0원)", 0.0),
        ]

        # Always error cases (regardless of strict mode)
        error_cases = [
            "1.234.56",  # multiple decimal points
        ]
    """
    # Input validation - fail fast
    if not text or not isinstance(text, str):
        if strict:
            raise ValueError(f"Invalid input: {text}")
        return 0.0

    # Extract content before brackets for cleaner number extraction
    brackets = ['(', '[', '{']
    for bracket in brackets:
        if bracket in text:
            text = text.split(bracket)[0]

    # Remove common separators (thousands separators, spaces)
    cleaned = text.replace(',', '').replace(' ', '').replace('_', '')

    # Extract numeric patterns (digits and decimal points)
    number_pattern = re.findall(r'[\d.]+', cleaned)

    if not number_pattern:
        if strict:
            raise ValueError(f"No number found: '{text}'")
        return 0.0

    # Use first found number fragment
    combined = number_pattern[0]

    # Validate decimal point count
    decimal_count = combined.count('.')
    if decimal_count > 1:
        raise ValueError(f"Multiple decimal points found: '{text}' -> '{combined}'")

    # Check for edge cases (empty or just decimal point)
    if combined in ('.', ''):
        if strict:
            raise ValueError(f"No valid number found: '{text}'")
        return 0.0

    # Convert to float with error handling
    try:
        return float(combined)
    except ValueError as e:
        if strict:
            raise ValueError(f"Number conversion failed: '{text}' -> '{combined}', error: {e}")
        return 0.0

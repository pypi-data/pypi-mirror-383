import pandas as pd
import inspect
from typing import get_origin, get_args, Sequence
from types import UnionType
from functools import wraps

def validate_df(df: pd.DataFrame, schema: dict[str, type | UnionType], optional_columns: Sequence[str] = []) -> pd.DataFrame:
    for col, excpected_type in schema.items():
        if col not in df.columns:
            if col in optional_columns:
                continue
            raise TypeError(f"Column '{col}' is missing from DataFrame")
        
        for idx, value in df[col].items():
            if value is None or (isinstance(value, float) and pd.isna(value)):
                if get_origin(excpected_type) is UnionType and type(None) in get_args(excpected_type):
                    continue
                else:
                    raise TypeError(f"Column '{col}' at index {idx} has None/NaN value which is not allowed")
            if not _check_type(value, excpected_type):
                raise TypeError(f"Column '{col}' at index {idx} has value '{value}' of type {type(value).__name__}, expected {excpected_type}")
    return df


def pdvalidate(schemas: dict[str, dict[str, type | UnionType]], optional_columns: dict[str, Sequence[str]] | None = None):
    optional_columns = optional_columns or {}
    def decorator(func):
        func.__doc__ = (func.__doc__ or "") + "\n\nExpected DataFrame schemas:\n"
        for name, schema in schemas.items():
            schema_str = "\n".join(
                f"  - {col}: {typ}" for col, typ in schema.items()
            )
            func.__doc__ += f"  • {name}:\n{schema_str}\n"
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            for name, schema in schemas.items():
                if (df := bound_args.arguments.get(name)) is None:
                    continue
                
                _ = validate_df(df, schema, optional_columns.get(name, []))
                    
            return func(*args, **kwargs)
        return wrapper
    return decorator

def _check_type(value, expected_type):
    match expected_type:
        case UnionType():
            return any(_check_type(value, t) for t in get_args(expected_type))
        case _:
            return isinstance(value, expected_type)
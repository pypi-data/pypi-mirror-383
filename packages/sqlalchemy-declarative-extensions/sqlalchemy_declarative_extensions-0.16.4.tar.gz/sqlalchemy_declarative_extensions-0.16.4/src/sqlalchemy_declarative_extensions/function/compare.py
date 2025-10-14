from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import Sequence, Union

from sqlalchemy.engine import Connection

from sqlalchemy_declarative_extensions.dialects import get_function_cls, get_functions
from sqlalchemy_declarative_extensions.function.base import Function, Functions
from sqlalchemy_declarative_extensions.op import ExecuteOp


@dataclass
class CreateFunctionOp(ExecuteOp):
    function: Function

    def reverse(self):
        return DropFunctionOp(self.function)

    def to_sql(self) -> list[str]:
        return self.function.to_sql_create()


@dataclass
class UpdateFunctionOp(ExecuteOp):
    from_function: Function
    function: Function

    def reverse(self):
        return UpdateFunctionOp(self.function, self.from_function)

    def to_sql(self) -> list[str]:
        return self.function.to_sql_update()


@dataclass
class DropFunctionOp(ExecuteOp):
    function: Function

    def reverse(self):
        return CreateFunctionOp(self.function)

    def to_sql(self) -> list[str]:
        return self.function.to_sql_drop()


Operation = Union[CreateFunctionOp, UpdateFunctionOp, DropFunctionOp]


def compare_functions(connection: Connection, functions: Functions) -> list[Operation]:
    result: list[Operation] = []

    functions_by_name = {f.qualified_name: f for f in functions.functions}
    expected_function_names = set(functions_by_name)

    raw_existing_functions = get_functions(connection)
    existing_functions = filter_functions(raw_existing_functions, functions.ignore)
    existing_functions_by_name = {
        f.qualified_name: f.normalize() for f in existing_functions
    }
    existing_function_names = set(existing_functions_by_name)

    new_function_names = expected_function_names - existing_function_names
    removed_function_names = existing_function_names - expected_function_names

    function_cls = get_function_cls(connection)
    for function in functions:
        function_name = function.qualified_name

        function_created = function_name in new_function_names

        concrete_function = function_cls.from_unknown_function(function)
        normalized_function = concrete_function.normalize()

        if function_created:
            result.append(CreateFunctionOp(normalized_function))
        else:
            existing_function = existing_functions_by_name[function_name]
            normalized_existing_function = existing_function

            if normalized_existing_function != normalized_function:
                result.append(
                    UpdateFunctionOp(normalized_existing_function, normalized_function)
                )

    if not functions.ignore_unspecified:
        for removed_function in removed_function_names:
            function = existing_functions_by_name[removed_function]
            result.append(DropFunctionOp(function))

    return result


def filter_functions(
    functions: Sequence[Function], exclude: list[str]
) -> list[Function]:
    return [
        f
        for f in functions
        if not any(
            fnmatch.fnmatch(f.qualified_name, exclusion) for exclusion in exclude
        )
    ]

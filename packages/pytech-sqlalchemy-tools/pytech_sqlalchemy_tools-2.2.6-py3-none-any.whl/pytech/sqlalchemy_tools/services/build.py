import dataclasses
from string import ascii_letters
from types import NoneType

from sqlalchemy.orm import Mapped
from sqlalchemy.schema import Column, UniqueConstraint
from sqlalchemy.sql import sqltypes

from pytech.sqlalchemy_tools.models import BaseSqlModel

__all__ = ["build_sqlalchemy_model"]


def build_sqlalchemy_model(  # noqa: PLR0912, PLR0913
    from_dataclass: type,
    table_name: str,
    model_name: str,
    additional_fields: dict | None = None,
    pk_fields: list | None = None,
    unique_fields: list | None = None,
    extensible_model: bool = False,
) -> BaseSqlModel:
    """
    Dynamically creates a SQLAlchemy model from a provided dataclass.
    The dataclass annotation must be Mappable SQL Alchemy types!

    The table_name and the model_name only accept ascii_letters and the '_'.

    If the specified primary_key is in the annotations
    that field will be used as primary key otherwise
    a primary_key column must be specified as additional field.

    :param from_dataclass:
        the dataclass to use to create the model.
        All annotations must be Mappable SQLAlchemy types.
    :param table_name: the name the table will take in the database.
    :param model_name: the name the Model class will take.
    :param additional_fields: fields to add to the model.
    :param pk_fields: the fields to use as primary key.
    :param unique_fields: the fields for which to set a unique constraint.
    :param extensible_model: specifies if the model can be extended default False).
    :return: the BaseSqlModel created from the dataclass.
    """

    if not (
        isinstance(from_dataclass, type) and dataclasses.is_dataclass(from_dataclass)
    ):
        raise TypeError("'from_dataclass' must be a valid dataclass.")

    if not isinstance(table_name, str):
        raise TypeError("'table_name' must be a string.")

    if not isinstance(model_name, str):
        raise TypeError("'model_name' must be a string.")

    if not isinstance(additional_fields, dict | NoneType):
        raise TypeError("'additional_fields' must be a dict.")

    if not isinstance(pk_fields, list | NoneType):
        raise TypeError("'pk_fields' must be a list.")

    if not isinstance(unique_fields, list | NoneType):
        raise TypeError("'unique_fields' must be a list.")

    # All dataclass annotations must be Mappable SQLAlchemy types.
    invalid_keys = [
        key
        for key, val in from_dataclass.__annotations__.items()
        if val not in sqltypes._type_map
    ]
    if invalid_keys:
        raise ValueError(
            f"'from_dataclass' has invalid annotations: {', '.join(invalid_keys)}"
        )

    if not set(table_name).issubset(f"_{ascii_letters}"):
        raise ValueError("'table_name' contains invalid characters.")

    if not set(model_name).issubset(f"_{ascii_letters}"):
        raise ValueError("'model_name' contains invalid characters.")

    _dataclass_fields = from_dataclass.__dataclass_fields__

    model_attrs = {
        "__tablename__": table_name,
        "__annotations__": {k: Mapped[v.type] for k, v in _dataclass_fields.items()},
    }

    if additional_fields:
        # If additional_fields are defined we check they are well-defined
        if not all(
            [
                set(field_name).issubset(f"_{ascii_letters}")
                for field_name in additional_fields
            ]
        ):
            raise ValueError("'additional_fields' contains invalid characters.")

        if not all([isinstance(field, Column) for field in additional_fields.values()]):
            raise ValueError("'additional_fields' must be valid Columns")

        model_attrs |= additional_fields

    if pk_fields:
        # If pk_fields was specified we check that the keys are valid
        if not set(pk_fields).issubset(_dataclass_fields.keys()):
            raise ValueError("'pk_fields' must be a list of valid keys.")

        model_attrs |= {
            "__mapper_args__": {"primary_key": pk_fields},
        }

    table_args = []
    if unique_fields:
        if not set(unique_fields).issubset(_dataclass_fields.keys()):
            raise ValueError("'unique_fields' must be a list of valid keys.")
        table_args.append(UniqueConstraint(*unique_fields))

    if extensible_model:
        table_args.append({"extend_existing": True})

    model_attrs |= {"__table_args__": tuple(table_args)}

    return type(model_name, (BaseSqlModel,), model_attrs)

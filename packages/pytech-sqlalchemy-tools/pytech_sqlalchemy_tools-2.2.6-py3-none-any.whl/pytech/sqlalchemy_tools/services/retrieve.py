import dataclasses

from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from pytech.sqlalchemy_tools.models import BaseSqlModel

__all__ = ["retrieve_all_data"]


def retrieve_all_data(
    session: Session,
    model: type[BaseSqlModel],
    where_clause: _ColumnExpressionArgument[bool] = None,
) -> list:
    """
    Function used to retrieve data from a specific model using a specific Engine.

    :param session: the session to use for the connection
    :param model: the model class from which retrieve the data
    :param where_clause: optional custom where conditions
    :return:
    """

    if not isinstance(session, Session):
        raise TypeError("'session' must be a valid Session.")

    if not issubclass(model, BaseSqlModel):
        raise TypeError("'model' must inherit from 'BaseSqlModel'.")

    statement = select(model)
    if where_clause is not None:
        statement = statement.where(where_clause)

    result = session.execute(statement=statement)

    return [dataclasses.asdict(el) for [el] in result]

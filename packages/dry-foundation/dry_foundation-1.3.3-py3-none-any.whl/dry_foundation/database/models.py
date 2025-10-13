"""
ORM model definitions corresponding to tables in the SQLite database.
"""

from datetime import date

from flask import g
from sqlalchemy import select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, declared_attr

from . import SQLAlchemy


class Model(DeclarativeBase):
    """A declarative base for all models."""

    metadata = SQLAlchemy.metadata

    def _format_repr_attr(self, name):
        value = getattr(self, name)
        value_str = f"{value}"
        # Abbreviate the string if it is longer than a set length
        abbrev_len = 25
        if len(value_str) > abbrev_len:
            value_str = f"{value_str[:abbrev_len]}..."
        if type(value) in (str, date):
            value_str = f"'{value_str}'"
        return f"{name}={value_str}"

    def __repr__(self):
        repr_attributes = self.__table__.columns.keys()
        pairs = [self._format_repr_attr(_) for _ in repr_attributes]
        attributes_str = ", ".join(pairs)
        return f"{self.__class__.__name__}({attributes_str})"

    @hybrid_property
    def fields(self):
        return self.__table__.columns

    @hybrid_property
    def primary_key_field(self):
        return self.__mapper__.primary_key[0]


class AuthorizedAccessMixin:
    """A mixin class to facilitate making user-restricted queries."""

    _user_id_join_chain = ()
    _alt_authorized_ids = ()

    @declared_attr.cascading
    @classmethod
    def user_id_model(cls):
        if cls._user_id_join_chain:
            return cls._user_id_join_chain[-1]
        return cls

    @hybrid_property
    def _authorizing_criteria(cls):
        try:
            user_id_field = cls.user_id_model.user_id
        except AttributeError:
            msg = (
                "An authorized access model must either contain a direct "
                "reference to the user ID or specify a chain of joins to a "
                "table where the user ID can be verified."
            )
            raise AttributeError(msg)
        # Ensure that the hybrid property's return value is always a list of values
        authorized_ids = list(cls.authorized_ids)
        return user_id_field.in_(authorized_ids)

    @hybrid_property
    def authorized_ids(self):
        # Add any extra IDs specified (e.g., user ID 0 for common entries)
        current_user_id = getattr(g.user, "id", None)
        authorized_user_ids = [current_user_id] if current_user_id else []
        authorized_user_ids.extend(self._alt_authorized_ids)
        return authorized_user_ids

    @classmethod
    def select_for_user(cls, *args, guaranteed_joins=(), **kwargs):
        """
        Build a select query restricting results to only an authorized user.

        Parameters
        ----------
        *args :
            The arguments to pass to the `sqlalchemy.select` function.
            If no arguments are given, the query selects the
        guaranteed_joins : tuple
            Database models (and by extension, their tables) that are
            not included in this model's "user ID join chain" but which
            should be added to this specific user-authorized join.
        **kwargs :
            The keyword arguments to pass to the `sqlalchemy.select`
            function.

        Returns
        -------
        query : sqlalchemy.sql.selectable.Select
            A statement representing the select query to make against
            the database.
        """
        query = cls._join_user(
            select(*args, **kwargs) if args else select(cls, **kwargs)
        )
        for target in guaranteed_joins:
            if target not in cls._user_id_join_chain:
                query = query.join(target)
        return query.where(cls._authorizing_criteria)

    @classmethod
    def _join_user(cls, query):
        """Perform joins necessary to link the current model to a `User`."""
        from_arg = cls
        for join_model in cls._user_id_join_chain:
            # Specify left ("from") and right ("target") sides of joins exactly
            target_arg = join_model
            query = query.join_from(from_arg, target_arg)
            from_arg = target_arg
        return query

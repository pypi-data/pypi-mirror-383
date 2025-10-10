from typing import Generator, Any, overload

from .db_data_model import DBDataModel
from .db_wrapper_mixin import DBWrapperMixin
from .common import OrderByItem, DataModelType


class DBWrapper(DBWrapperMixin):
    """
    Database wrapper class.
    """

    #####################
    ### Query methods ###
    #####################

    # Action methods
    def get_one(
        self,
        empty_data_class: DataModelType,
        custom_query: Any = None,
    ) -> DataModelType | None:
        """
        Retrieves a single record from the database by class defined id.

        Args:
            empty_data_class (DataModelType): The data model to use for the query.
            custom_query (Any, optional): The custom query to use for the query. Defaults to None.

        Returns:
            DataModelType | None: The result of the query.
        """
        # Figure out the id key and value
        id_key = empty_data_class.id_key
        id_value = empty_data_class.id
        if not id_key:
            raise ValueError("Id key is not set")
        if not id_value:
            raise ValueError("Id value is not set")

        # Get the record
        res = self.get_all(
            empty_data_class,
            id_key,
            id_value,
            limit=1,
            custom_query=custom_query,
        )
        for row in res:
            return row
        else:
            return None

    def get_by_key(
        self,
        empty_data_class: DataModelType,
        id_key: str,
        id_value: Any,
        custom_query: Any = None,
    ) -> DataModelType | None:
        """
        Retrieves a single record from the database using the given key.

        Args:
            empty_data_class (DataModelType): The data model to use for the query.
            id_key (str): The name of the key to use for the query.
            id_value (Any): The value of the key to use for the query.
            custom_query (Any, optional): The custom query to use for the query. Defaults to None.

        Returns:
            DataModelType | None: The result of the query.
        """
        # Get the record
        res = self.get_all(
            empty_data_class,
            id_key,
            id_value,
            limit=1,
            custom_query=custom_query,
        )
        for row in res:
            return row
        else:
            return None

    def get_all(
        self,
        empty_data_class: DataModelType,
        id_key: str | None = None,
        id_value: Any | None = None,
        order_by: OrderByItem | None = None,
        offset: int = 0,
        limit: int = 100,
        custom_query: Any = None,
    ) -> Generator[DataModelType, None, None]:
        """
        Retrieves all records from the database.

        Args:
            empty_data_class (DataModelType): The data model to use for the query.
            id_key (str | None, optional): The name of the key to use for filtering. Defaults to None.
            id_value (Any | None, optional): The value of the key to use for filtering. Defaults to None.
            order_by (OrderByItem | None, optional): The order by item to use for sorting. Defaults to None.
            offset (int, optional): The number of results to skip. Defaults to 0.
            limit (int, optional): The maximum number of results to return. Defaults to 100.
            custom_query (Any, optional): The custom query to use for the query. Defaults to None.

        Returns:
            Generator[DataModelType, None, None]: The result of the query.
        """
        # Query and filter
        _query = (
            custom_query
            or empty_data_class.query_base()
            or self.filter_query(
                empty_data_class.schema_name,
                empty_data_class.table_name,
            )
        )
        _params: tuple[Any, ...] = ()
        _filter = None

        # TODO: Rewrite this so that filter method with loop is not used here
        if id_key and id_value:
            (_filter, _params) = self.create_filter({id_key: id_value})

        # Order and limit
        _order = self.order_query(order_by)
        _limit = self.limit_query(offset, limit)

        # Create a SQL object for the query and format it
        query_sql = self._format_filter_query(_query, _filter, _order, _limit)

        # Log
        self.log_query(self.db_cursor, query_sql, _params)

        # Execute the query
        self.db_cursor.execute(query_sql, _params)

        # Instead of fetchall(), we'll use a generator to yield results one by one
        while True:
            row = self.db_cursor.fetchone()
            if row is None:
                break

            yield self.turn_data_into_model(empty_data_class.__class__, row)

    def get_filtered(
        self,
        empty_data_class: DataModelType,
        filter: dict[str, Any],
        order_by: OrderByItem | None = None,
        offset: int = 0,
        limit: int = 100,
        custom_query: Any = None,
    ) -> Generator[DataModelType, None, None]:
        # Query and filter
        _query = (
            custom_query
            or empty_data_class.query_base()
            or self.filter_query(
                empty_data_class.schema_name,
                empty_data_class.table_name,
            )
        )
        (_filter, _params) = self.create_filter(filter)

        # Order and limit
        _order = self.order_query(order_by)
        _limit = self.limit_query(offset, limit)

        # Create SQL query
        query_sql = self._format_filter_query(_query, _filter, _order, _limit)

        # Log
        self.log_query(self.db_cursor, query_sql, _params)

        # Execute the query
        self.db_cursor.execute(query_sql, _params)

        # Instead of fetchall(), we'll use a generator to yield results one by one
        while True:
            row = self.db_cursor.fetchone()
            if row is None:
                break

            yield self.turn_data_into_model(empty_data_class.__class__, row)

    def _insert(
        self,
        empty_data_class: DBDataModel,
        schema_name: str | None,
        table_name: str,
        store_data: dict[str, Any],
        id_key: str,
    ) -> tuple[int, int]:
        """
        Stores a record in the database.

        Args:
            empty_data_class (DBDataModel): The data model to use for the query.
            schema_name (str | None): The name of the schema to store the record in.
            table_name (str): The name of the table to store the record in.
            store_data (dict[str, Any]): The data to store.
            id_key (str): The name of the key to use for the query.

        Returns:
            tuple[int, int]: The id of the record and the number of affected rows.
        """
        values = list(store_data.values())
        table_identifier = self.make_identifier(schema_name, table_name)
        return_key = self.make_identifier(empty_data_class.table_alias, id_key)
        insert_query = self._format_insert_query(
            table_identifier,
            store_data,
            return_key,
        )

        # Log
        self.log_query(self.db_cursor, insert_query, tuple(values))

        # Insert
        self.db_cursor.execute(insert_query, tuple(values))
        affected_rows = self.db_cursor.rowcount
        result = self.db_cursor.fetchone()

        return (
            result[id_key] if result and id_key in result else 0,
            affected_rows,
        )

    @overload
    def insert(self, records: DataModelType) -> tuple[int, int]:  # type: ignore
        ...

    @overload
    def insert(self, records: list[DataModelType]) -> list[tuple[int, int]]: ...

    def insert(
        self,
        records: DataModelType | list[DataModelType],
    ) -> tuple[int, int] | list[tuple[int, int]]:
        """
        Stores a record or a list of records in the database.

        Args:
            records (DataModelType | list[DataModelType]): The record or records to store.

        Returns:
            tuple[int, int] | list[tuple[int, int]]: The id of the record and
                the number of affected rows for a single record or a list of
                ids and the number of affected rows for a list of records.
        """
        status: list[tuple[int, int]] = []

        one_record = False
        if not isinstance(records, list):
            one_record = True
            records = [records]

        for row in records:
            store_id_key = row.id_key
            store_data = row.store_data()
            if not store_id_key or not store_data:
                continue

            res = self._insert(
                row,
                row.schema_name,
                row.table_name,
                store_data,
                store_id_key,
            )
            if res:
                row.id = res[0]  # update the id of the row

            status.append(res)

        if one_record:
            return status[0]

        return status

    def _update(
        self,
        empty_data_class: DBDataModel,
        schema_name: str | None,
        table_name: str,
        update_data: dict[str, Any],
        update_id: tuple[str, Any],
    ) -> int:
        """
        Updates a record in the database.

        Args:
            empty_data_class (DBDataModel): The data model to use for the query.
            schema_name (str | None): The name of the schema to update the record in.
            table_name (str): The name of the table to update the record in.
            update_data (dict[str, Any]): The data to update.
            update_id (tuple[str, Any]): The id of the record to update.

        Returns:
            int: The number of affected rows.
        """
        (id_key, id_value) = update_id
        values = list(update_data.values())
        values.append(id_value)

        table_identifier = self.make_identifier(schema_name, table_name)
        update_key = self.make_identifier(empty_data_class.table_alias, id_key)
        update_query = self._format_update_query(
            table_identifier, update_key, update_data
        )

        # Log
        self.log_query(self.db_cursor, update_query, tuple(values))

        # Update
        self.db_cursor.execute(update_query, tuple(values))
        affected_rows = self.db_cursor.rowcount

        return affected_rows

    @overload
    def update(self, records: DataModelType) -> int:  # type: ignore
        ...

    @overload
    def update(self, records: list[DataModelType]) -> list[int]: ...

    def update(self, records: DataModelType | list[DataModelType]) -> int | list[int]:
        """
        Updates a record or a list of records in the database.

        Args:
            records (DataModelType | list[DataModelType]): The record or records to update.

        Returns:
            int | list[int]: The number of affected rows for a single record or a list of
                affected rows for a list of records.
        """
        status: list[int] = []

        one_record = False
        if not isinstance(records, list):
            one_record = True
            records = [records]

        for row in records:
            update_data = row.update_data()
            update_id_key = row.id_key
            update_id_value = row.id
            if not update_data or not update_id_key or not update_id_value:
                continue

            status.append(
                self._update(
                    row,
                    row.schema_name,
                    row.table_name,
                    update_data,
                    (
                        update_id_key,
                        update_id_value,
                    ),
                )
            )

        if one_record:
            return status[0]

        return status

    def update_data(
        self,
        record: DBDataModel,
        update_data: dict[str, Any],
        update_id_key: str | None = None,
        update_id_value: Any = None,
    ) -> int:
        update_id_key = update_id_key or record.id_key
        update_id_value = update_id_value or record.id
        status = self._update(
            record,
            record.schema_name,
            record.table_name,
            update_data,
            (
                update_id_key,
                update_id_value,
            ),
        )

        return status

    def _delete(
        self,
        empty_data_class: DBDataModel,
        schema_name: str | None,
        table_name: str,
        delete_id: tuple[str, Any],
    ) -> int:
        """
        Deletes a record from the database.

        Args:
            empty_data_class (DBDataModel): The data model to use for the query.
            schema_name (str | None): The name of the schema to delete the record from.
            table_name (str): The name of the table to delete the record from.
            delete_id (tuple[str, Any]): The id of the record to delete.

        Returns:
            int: The number of affected rows.
        """
        (id_key, id_value) = delete_id

        table_identifier = self.make_identifier(schema_name, table_name)
        delete_key = self.make_identifier(empty_data_class.table_alias, id_key)
        delete_query = self._format_delete_query(table_identifier, delete_key)

        # Log
        self.log_query(self.db_cursor, delete_query, (id_value,))

        # Delete
        self.db_cursor.execute(delete_query, (id_value,))
        affected_rows = self.db_cursor.rowcount

        return affected_rows

    @overload
    def delete(self, records: DataModelType) -> int:  # type: ignore
        ...

    @overload
    def delete(self, records: list[DataModelType]) -> list[int]: ...

    def delete(self, records: DataModelType | list[DataModelType]) -> int | list[int]:
        """
        Deletes a record or a list of records from the database.

        Args:
            records (DataModelType | list[DataModelType]): The record or records to delete.

        Returns:
            int | list[int]: The number of affected rows for a single record or a list of
                affected rows for a list of records.
        """
        status: list[int] = []

        one_record = False
        if not isinstance(records, list):
            one_record = True
            records = [records]

        for row in records:
            delete_id_key = row.id_key
            delete_id_value = row.id
            if not delete_id_key or not delete_id_value:
                continue

            status.append(
                self._delete(
                    row,
                    row.schema_name,
                    row.table_name,
                    (
                        delete_id_key,
                        delete_id_value,
                    ),
                )
            )

        if one_record:
            return status[0]

        return status

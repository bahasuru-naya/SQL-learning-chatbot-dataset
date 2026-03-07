from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sqlalchemy import create_engine, inspect
import time


def create_sql_connection():
    username = 'root'
    password = 'bahasurubn0008'
    host = 'localhost'
    port = 3306
    database = 'csitem'
    # Construct the connection URL
    connection_url = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"

    # Create the SQLAlchemy engine
    engine = create_engine(connection_url)

    # Create and return the connection
    connection = engine.connect()
    return connection


# ----------Experimental part STRAT-------------

# Define keywords related to stocks, prices, and sales
stock_keywords = ['stock', 'inventory', 'shares', 'equity']
price_keywords = ['price', 'cost', 'value', 'rate']
sales_keywords = ['sales', 'revenue', 'transactions', 'orders', 'quantitysold']

# Initialize tables dictionary to store table structures
tables = {}


# Function to check if a table is related to stocks
def is_stock_table(table):
    return any(keyword in column.lower() for keyword in stock_keywords for column in tables.get(table, []))


# Function to check if a table is related to prices
def is_price_table(table):
    return any(keyword in column.lower() for keyword in price_keywords for column in tables.get(table, []))


# Function to check if a table is related to sales
def is_sales_table(table):
    return any(keyword in column.lower() for keyword in sales_keywords for column in tables.get(table, []))


def check_table():
    global table_names
    global stocktable
    global salestable
    global pricetable

    connection2 = create_sql_connection()

    # Your SQL query to retrieve table names and column names
    query2 = (f"SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema = "
              f"'csitem';")

    # Execute the query using the engine
    result_proxy2 = connection2.execute(query2)
    result2 = result_proxy2.fetchall()
    connection2.close()

    if result2:
        # Extract table names from the ResultProxy object
        table_names = [row[0] for row in result2]

        # Fetch column names for each table
        for table_name in table_names:
            connection1 = create_sql_connection()
            query1 = (f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' ORDER "
                      f"BY ORDINAL_POSITION;")
            result_proxy1 = connection1.execute(query1)
            result1 = result_proxy1.fetchall()
            connection1.close()

            if result1:
                columns = [row[0] for row in result1]
                tables[table_name] = columns

    for table_name in table_names:
        if is_stock_table(table_name):
            stocktable = table_name
        if is_price_table(table_name):
            pricetable = table_name
        if is_sales_table(table_name):
            salestable = table_name


# ----------Experimental part END-------------


class ActionShowAllTables(Action):
    def name(self) -> Text:
        return "action_show_all_tables"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            connection = create_sql_connection()
            inspector = inspect(connection)
            msg = ''
            # Get all table names
            table_names = inspector.get_table_names()

            if not table_names:
                dispatcher.utter_message("No tables found in the database.")
                return []

            for table_name in table_names:
                msg = msg + f"Table: {table_name} \n ~"

                # Query the database
                query = f"SELECT * FROM {table_name}"
                result = connection.execute(query).fetchall()

                if result:
                    # Extract headers and rows
                    headers = result[0].keys() if result else []
                    rows = [dict(row) for row in result]

                    # Calculate column widths
                    column_widths = {header: max(len(str(row.get(header, ""))) for row in rows + [{header: header}]) for
                                     header in headers}

                    # Construct and add header row
                    header_str = "|" + "|".join(header.ljust(column_widths[header]) for header in headers) + "|"
                    msg += header_str + "\n"

                    # Construct and add each row
                    for row in rows:
                        row_str = "|" + "|".join(
                            str(row.get(header, "")).ljust(column_widths[header]) for header in headers) + "|"
                        msg += row_str + "\n"

                    msg += " ~"  # End with an asterisk
                else:
                    dispatcher.utter_message("No results found in this table.")

            dispatcher.utter_message(msg)
            # Close the database connection
            connection.close()
        except Exception as e:
            dispatcher.utter_message(f"An error occurred while showing the data: {str(e)}")

        return []


class ActionShowTable(Action):
    def name(self) -> Text:
        return "action_show_table"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get('entities', [])

        if entities:
            try:
                table_name = entities[0]['value']

                connection = create_sql_connection()

                # Query the database
                query = f"SELECT * FROM {table_name} "
                result = connection.execute(query).fetchall()

                # Close the database connection
                connection.close()
                msg = f"Sql query: \n {query} \n \n Result: \n ~"

                if result:
                    # Extract headers and rows
                    headers = result[0].keys() if result else []
                    rows = [dict(row) for row in result]

                    # Calculate column widths
                    column_widths = {header: max(len(str(row.get(header, ""))) for row in rows + [{header: header}]) for
                                     header in headers}

                    # Construct and add header row
                    header_str = "|" + "|".join(header.ljust(column_widths[header]) for header in headers) + "|"
                    msg += header_str + "\n"

                    # Construct and add each row
                    for row in rows:
                        row_str = "|" + "|".join(
                            str(row.get(header, "")).ljust(column_widths[header]) for header in headers) + "|"
                        msg += row_str + "\n"

                    msg += " ~"  # End with an asterisk
                    dispatcher.utter_message(msg)
                else:
                    dispatcher.utter_message("No results found.")
            except Exception as e:
                dispatcher.utter_message(f"An error occurred while show the data: {str(e)}")
        else:
            dispatcher.utter_message("Table name not provided.")

        return []


class ActionAddItemsStock(Action):
    def name(self) -> Text:
        return "action_add_items_stock"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get('entities', [])

        if entities:
            item_name = next((entity['value'] for entity in entities if entity['entity'] == 'item_name'), None)
            quantity = next((entity['value'] for entity in entities if entity['entity'] == 'quantity'), None)
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)

            try:
                if item_name and quantity and table_name:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"INSERT INTO {table_name} (item_name, stock) VALUES ('{item_name}', {quantity})"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query: \n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully added {quantity} {item_name}(s) to {table_name}. \n \n Type 'show {table_name}' to see the changes.")

                elif item_name and quantity:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"INSERT INTO stock (item_name, stock) VALUES ('{item_name}', {quantity})"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully added {quantity} {item_name}(s) to itemstock. \n \n Type 'show stock' to see the changes.")
                else:
                    dispatcher.utter_message("Missing required information. Please provide item name, quantity, "
                                             "and table name.")
            except Exception as e:
                dispatcher.utter_message(f" An error occurred while inserting data: {str(e)}")

        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionUpdateItemsStock(Action):
    def name(self) -> Text:
        return "action_update_items_stock"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get('entities', [])

        if entities:
            iid = next((entity['value'] for entity in entities if entity['entity'] == 'id'), None)
            item_name = next((entity['value'] for entity in entities if entity['entity'] == 'item_name'), None)
            quantity = next((entity['value'] for entity in entities if entity['entity'] == 'quantity'), None)
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)
            try:
                if item_name and quantity and table_name and iid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE {table_name} SET item_name = '{item_name}', stock = {quantity}  WHERE id = {iid}"
                    connection.execute(query)
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    # Close the database connection
                    connection.close()

                    dispatcher.utter_message(f"{msg} Successfully updated {quantity} {item_name}(s) to {table_name}. \n \n Type 'show {table_name}' to see the changes.")

                elif item_name and quantity and iid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE stock SET item_name = '{item_name}', stock = {quantity}  WHERE id = {iid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated {quantity} {item_name}(s) to itemstock. \n \n Type 'show stock' to see the changes.")
                elif item_name and iid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE stock SET item_name = '{item_name}' WHERE id = {iid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated {item_name}(s) to itemstock. \n \n Type 'show stock' to see the changes.")
                elif quantity and iid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE stock SET  stock = {quantity}  WHERE id = {iid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated {item_name} to itemstock. \n \n Type 'show stock' to see the changes.")
                else:
                    dispatcher.utter_message("Missing required information. Please provide item name, quantity, "
                                             "and table name.")
            except Exception as e:
                dispatcher.utter_message(f"An error occurred while updating data: {str(e)}")

        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionAddItemsPrice(Action):
    def name(self) -> Text:
        return "action_add_items_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])

        if entities:
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)
            idnum = next((entity['value'] for entity in entities if entity['entity'] == 'id'), None)
            price = next((entity['value'] for entity in entities if entity['entity'] == 'price'), None)
            try:
                if idnum and price and table_name:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"INSERT INTO {table_name} (id, price) VALUES ('{idnum}', {price})"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully added {idnum} {price} to {table_name}. \n \n Type 'show price' to see the changes.")
                elif idnum and price:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"INSERT INTO price (id, price) VALUES ('{idnum}', {price})"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully added {idnum} {price} to itemprice. \n \n Type 'show price' to see the changes.")
                else:
                    dispatcher.utter_message("Missing required information. Please provide id, price, and table "
                                             "name.")
            except Exception as e:
                dispatcher.utter_message(f"An error occurred while inserting data: {str(e)}")

        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionUpdateItemsPrice(Action):
    def name(self) -> Text:
        return "action_update_items_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])

        if entities:
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)
            idnum = next((entity['value'] for entity in entities if entity['entity'] == 'id'), None)
            price = next((entity['value'] for entity in entities if entity['entity'] == 'price'), None)
            try:
                if idnum and price and table_name:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE {table_name} SET price = {price} WHERE id = {idnum}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated price={price} where id={idnum} in {table_name}. \n \n Type 'show price' to see the changes.")
                elif idnum and price:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE price SET price = {price} WHERE id = {idnum}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated price={price} where id={idnum} in price. \n \n Type 'show price' to see the changes.")
                else:
                    dispatcher.utter_message("Missing required information. Please provide id, price, and table "
                                             "name.")
            except Exception as e:
                dispatcher.utter_message(f"An error occurred while updating data: {str(e)}")

        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionAddItemsSales(Action):
    def name(self) -> Text:
        return "action_add_items_sales"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])

        if entities:
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)
            idnum = next((entity['value'] for entity in entities if entity['entity'] == 'id'), None)
            sales = next((entity['value'] for entity in entities if entity['entity'] == 'sales'), None)
            date = next((entity['value'] for entity in entities if entity['entity'] == 'date'), None)

            try:
                if idnum and sales and date and table_name:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"INSERT INTO {table_name} (id, QuantitySold,SaleDate) VALUES ('{idnum}', {sales},'{date}')"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully added {idnum} {sales} {date} to {table_name}. \n \n Type 'show sales' to see the changes.")

                elif idnum and sales and date:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"INSERT INTO sales (id, QuantitySold,SaleDate) VALUES ('{idnum}', {sales},'{date}')"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully added {idnum} {sales} {date} to itemsales. \n \n Type 'show sales' to see the changes.")
                else:
                    dispatcher.utter_message("Missing required information. Please provide id, number of sales, "
                                             "date and table ")
            except Exception as e:
                dispatcher.utter_message(f"An error occurred while inserting data: {str(e)}")
        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionUpdateItemsSales(Action):
    def name(self) -> Text:
        return "action_update_items_sales"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])

        if entities:
            sid = next((entity['value'] for entity in entities if entity['entity'] == 'sale_id'), None)
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)
            idnum = next((entity['value'] for entity in entities if entity['entity'] == 'id'), None)
            sales = next((entity['value'] for entity in entities if entity['entity'] == 'sales'), None)
            date = next((entity['value'] for entity in entities if entity['entity'] == 'date'), None)

            try:
                if idnum and sales and date and table_name and sid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE {table_name} SET id = {idnum}, QuantitySold = {sales}, SaleDate = '{date}' WHERE SaleID = {sid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated {idnum} {sales} {date} to {table_name}. \n \n Type 'show sales' to see the changes.")

                elif idnum and sales and date and sid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE sales SET id = {idnum}, QuantitySold = {sales}, SaleDate = '{date}' WHERE SaleID = {sid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated {idnum} {sales} {date} to itemsales. \n \n Type 'show sales' to see the changes.")

                elif idnum and sales and sid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE sales SET id = {idnum}, QuantitySold = {sales} WHERE SaleID = {sid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated {idnum} {sales} to itemsales. \n \n Type 'show sales' to see the changes.")

                elif idnum and date and sid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE sales SET id = {idnum}, SaleDate = '{date}' WHERE SaleID = {sid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated {idnum}  {date} to itemsales. \n \n Type 'show sales' to see the changes.")

                elif sales and date and sid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE sales SET  QuantitySold = {sales}, SaleDate = '{date}' WHERE SaleID = {sid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated  {sales} {date} to itemsales. \n \n Type 'show sales' to see the changes.")

                elif idnum and sid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE sales SET id = {idnum} WHERE SaleID = {sid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated {idnum}  to itemsales. \n \n Type 'show sales' to see the changes.")

                elif sales and sid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE sales SET  QuantitySold = {sales} WHERE SaleID = {sid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated  {sales}  to itemsales. \n \n Type 'show sales' to see the changes.")

                elif date and sid:
                    connection = create_sql_connection()

                    # Constructing the SQL INSERT query
                    query = f"UPDATE sales SET  SaleDate = '{date}' WHERE SaleID = {sid}"
                    connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    dispatcher.utter_message(f"{msg} Successfully updated  {date} to itemsales. \n \n Type 'show sales' to see the changes.")

                else:
                    dispatcher.utter_message("Missing required information. Please provide id, number of sales, "
                                             "date and table ")
            except Exception as e:
                dispatcher.utter_message(f"An error occurred while updating data: {str(e)}")
        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionDeleteItemsStock(Action):
    def name(self) -> Text:
        return "action_delete_items_stock"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get('entities', [])

        if entities:
            item_name = next((entity['value'] for entity in entities if entity['entity'] == 'item_name'), None)
            quantity = next((entity['value'] for entity in entities if entity['entity'] == 'quantity'), None)
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)
            idnum = next((entity['value'] for entity in entities if entity['entity'] == 'id'), None)

            if item_name and quantity and table_name:

                try:
                    connection = create_sql_connection()

                    # Constructing the SQL DELETE query
                    query = f"DELETE FROM {table_name} WHERE item_name = '{item_name}' AND stock = {quantity}"

                    result = connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    # Check if any rows were affected by the delete operation
                    if result.rowcount > 0:
                        dispatcher.utter_message(f"{msg} Successfully deleted {quantity} {item_name}(s) from {table_name}. \n \n Type 'show stock' to see the changes.")
                    else:
                        dispatcher.utter_message(f"No rows found matching the criteria in {table_name}.")
                except Exception as e:
                    dispatcher.utter_message(f"An error occurred while deleting the row: {str(e)}")

            elif idnum and table_name:

                try:
                    connection = create_sql_connection()

                    # Constructing the SQL DELETE query
                    query = f"DELETE FROM {table_name} WHERE id = '{idnum}' "
                    result = connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    # Check if any rows were affected by the delete operation
                    if result.rowcount > 0:
                        dispatcher.utter_message(f"{msg} Successfully deleted {idnum}  from {table_name}. \n \n Type 'show stock' to see the changes.")
                    else:
                        dispatcher.utter_message(f"No rows found matching the criteria in {table_name}.")
                except Exception as e:
                    dispatcher.utter_message(f"An error occurred while deleting the row: {str(e)}")

            else:
                dispatcher.utter_message("Missing required information. Please provide item name, quantity, and table "
                                         "name or id and table name.")

        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionDeleteItemsPrice(Action):
    def name(self) -> Text:
        return "action_delete_items_price"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])

        if entities:
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)
            idnum = next((entity['value'] for entity in entities if entity['entity'] == 'id'), None)
            price = next((entity['value'] for entity in entities if entity['entity'] == 'price'), None)

            if idnum and price and table_name:

                try:
                    connection = create_sql_connection()

                    # Constructing the SQL DELETE query
                    query = f"DELETE FROM {table_name} WHERE id = '{idnum}' AND price = '{price}'"
                    result = connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    # Check if any rows were affected by the delete operation
                    if result.rowcount > 0:
                        dispatcher.utter_message(f"{msg} Successfully deleted {idnum} {price} from {table_name}. \n \n Type 'show price' to see the changes.")
                    else:
                        dispatcher.utter_message(f"No rows found matching the criteria in {table_name}.")
                except Exception as e:
                    dispatcher.utter_message(f"An error occurred while deleting the row: {str(e)}")

            elif idnum and table_name:

                try:
                    connection = create_sql_connection()

                    # Constructing the SQL DELETE query
                    query = f"DELETE FROM {table_name} WHERE id = '{idnum}' "
                    result = connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    # Check if any rows were affected by the delete operation
                    if result.rowcount > 0:
                        dispatcher.utter_message(f"{msg} Successfully deleted {idnum}  from {table_name}. \n \n Type 'show price' to see the changes.")
                    else:
                        dispatcher.utter_message(f"No rows found matching the criteria in {table_name}.")
                except Exception as e:
                    dispatcher.utter_message(f"An error occurred while deleting the row: {str(e)}")

            else:
                dispatcher.utter_message("Missing required information. Please provide id, price, and table "
                                         "name or id and table name.")

        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionDeleteItemsSales(Action):
    def name(self) -> Text:
        return "action_delete_items_sales"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])

        if entities:
            table_name = next((entity['value'] for entity in entities if entity['entity'] == 'table_name'), None)
            idnum = next((entity['value'] for entity in entities if entity['entity'] == 'id'), None)
            sales = next((entity['value'] for entity in entities if entity['entity'] == 'sales'), None)
            date = next((entity['value'] for entity in entities if entity['entity'] == 'date'), None)
            sale_id = next((entity['value'] for entity in entities if entity['entity'] == 'sale_id'), None)

            if idnum and sales and date and table_name:

                try:
                    connection = create_sql_connection()

                    # Constructing the SQL DELETE query
                    query = f"DELETE FROM {table_name} WHERE id = '{idnum}' AND  QuantitySold = '{sales}' AND SaleDate ='{date}'"
                    result = connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    # Check if any rows were affected by the delete operation
                    if result.rowcount > 0:
                        dispatcher.utter_message(f"{msg} Successfully deleted {idnum} {sales} {date} from {table_name}.\n \n Type 'show sales' to see the changes.")
                    else:
                        dispatcher.utter_message(f"No rows found matching the criteria in {table_name}.")
                except Exception as e:
                    dispatcher.utter_message(f"An error occurred while deleting the row: {str(e)}")

            elif sale_id and table_name:

                try:
                    connection = create_sql_connection()

                    # Constructing the SQL DELETE query
                    query = f"DELETE FROM {table_name} WHERE SaleID = '{sale_id}' "
                    result = connection.execute(query)

                    # Close the database connection
                    connection.close()
                    msg = f"Sql query:\n {query} \n \n Result: \n "

                    # Check if any rows were affected by the delete operation
                    if result.rowcount > 0:
                        dispatcher.utter_message(f"{msg} Successfully deleted {sale_id}  from {table_name}. \n \n Type 'show sales' to see the changes.")
                    else:
                        dispatcher.utter_message(f"No rows found matching the criteria in {table_name}.")
                except Exception as e:
                    dispatcher.utter_message(f"An error occurred while deleting the row: {str(e)}")

            else:
                dispatcher.utter_message("Missing required information. Please provide item name, quantity, and table "
                                         "name or sale id and table name.")

        else:
            dispatcher.utter_message("No entities found in the user message.")

        return []


class ActionRetrieveDataFromTables(Action):
    def name(self) -> Text:
        return "action_retrieve_data_from_tables"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        start_time = time.time()
        entities = tracker.latest_message.get('entities', [])
        check_table()

        if entities:
            table1 = next((entity['value'] for entity in entities if entity['entity'] == 'table1'), None)
            table2 = next((entity['value'] for entity in entities if entity['entity'] == 'table2'), None)
            condition = next((entity['value'] for entity in entities if entity['entity'] == 'condition'), None)
            query = ""
            if table1 and table2 and condition:

                connection = create_sql_connection()

                if table1 == "items" and table2 == "sales":
                    query = (
                        f"SELECT * FROM {stocktable} INNER JOIN {salestable} ON {stocktable}.id = {salestable}.id WHERE "
                        f"{salestable}.QuantitySold {condition}")
                elif table1 == "items" and table2 == "price":
                    query = (
                        f"SELECT * FROM {stocktable} INNER JOIN {pricetable} ON {stocktable}.id = {pricetable}.id WHERE "
                        f"{pricetable}.price {condition}")
                else:
                    dispatcher.utter_message("Sorry, I couldn't understand your query.")

                result = connection.execute(query).fetchall()

                # Close the database connection
                connection.close()
                msg = f"Sql query:\n {query} \n \n Result: \n ~"

                if result:
                    # Extract headers and rows
                    headers = result[0].keys() if result else []
                    rows = [dict(row) for row in result]

                    # Calculate column widths
                    column_widths = {header: max(len(str(row.get(header, ""))) for row in rows + [{header: header}]) for
                                     header in headers}

                    # Construct and add header row
                    header_str = "|" + "|".join(header.ljust(column_widths[header]) for header in headers) + "|"
                    msg += header_str + "\n"

                    # Construct and add each row
                    for row in rows:
                        row_str = "|" + "|".join(
                            str(row.get(header, "")).ljust(column_widths[header]) for header in headers) + "|"
                        msg += row_str + "\n"

                    msg += " ~"  # End with an asterisk
                    dispatcher.utter_message(msg)
                else:
                    dispatcher.utter_message("No results found.")

            elif table1 and table2:

                connection = create_sql_connection()

                if table1 == "sales" and table2 == "items":

                    query = (f"SELECT {stocktable}.item_name, {salestable}.QuantitySold,{salestable}.SaleDate "
                             f" FROM {stocktable} INNER JOIN {salestable} ON {stocktable}.id = {salestable}.id")

                elif table1 == "price" and table2 == "items":
                    query = (
                        f"SELECT {stocktable}.item_name, {pricetable}.price FROM {stocktable} INNER JOIN {pricetable} ON "
                        f"{stocktable}.id = {pricetable}.id")
                else:
                    dispatcher.utter_message("Sorry, I couldn't understand your query.")

                result = connection.execute(query).fetchall()

                # Close the database connection
                connection.close()
                msg = f"Sql query:\n {query} \n \n Result: \n ~"
                if result:
                    # Extract headers and rows
                    headers = result[0].keys() if result else []
                    rows = [dict(row) for row in result]

                    # Calculate column widths
                    column_widths = {header: max(len(str(row.get(header, ""))) for row in rows + [{header: header}]) for
                                     header in headers}

                    # Construct and add header row
                    header_str = "|" + "|".join(header.ljust(column_widths[header]) for header in headers) + "|"
                    msg += header_str + "\n"

                    # Construct and add each row
                    for row in rows:
                        row_str = "|" + "|".join(
                            str(row.get(header, "")).ljust(column_widths[header]) for header in headers) + "|"
                        msg += row_str + "\n"

                    msg += " ~"  # End with an asterisk
                    dispatcher.utter_message(msg)
                else:
                    dispatcher.utter_message("No results found.")

            else:
                dispatcher.utter_message("Missing required information. Please provide more information.")

        else:
            dispatcher.utter_message("No entities found in the user message.")
        print("--- %s seconds ---" % (time.time() - start_time))
        return []


class ActionNLUFallback(Action):
    def name(self) -> Text:
        return "action_nlu_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Custom logic using user_message
        dispatcher.utter_message("It seems like you're asking a question that is outside the scope of my "
                                 "capabilities. Please rephrase your question or try another one.")

        return []

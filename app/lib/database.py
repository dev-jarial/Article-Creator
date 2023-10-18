import mysql.connector
from mysql.connector import Error


# Global methods to push interact with the Database

# This method establishes the connection with the MySQL
def create_server_connection(host_name, user_name, user_password):
    # Implement the logic to create the server connection
    connection = None
    try:
        connection = mysql.connector.connect(host=host_name, user=user_name, password=user_password, auth_plugin='mysql_native_password')
    except Error as e:
        print("Error while connecting to MySQL", e)

    return connection


def drop_db_if_exists(connection, db_name):
    try:
        query = "DROP DATABASE IF EXISTS " + db_name
        cursor = connection.cursor()
        cursor.execute(query)
    except Error as e:
        print("Something went wrong: {}".format(e))


def create_and_use_db(connection, db_name):
    create_db_if_not_exists(connection, db_name)
    use_db(connection, db_name)


def create_db_if_not_exists(connection, db_name):
    try:
        query = "CREATE DATABASE IF NOT EXISTS " + db_name
        cursor = connection.cursor()
        cursor.execute(query)
    except Error as e:
        print("Something went wrong: {}".format(e))


def use_db(connection, db_name):
    try:
        query = "USE `" + db_name+"`"
        cursor = connection.cursor()
        cursor.execute(query)
    except Error as e:
        print("Something went wrong: {}".format(e))


# This method will create the database and make it an active database
def create_and_switch_database(connection, db_name, switch_db):
    # For database creation use this method
    # If you have created your database using UI, no need to implement anything
    try:
        if connection is not None:
            drop_db_if_exists(connection, db_name)
            create_and_use_db(connection, db_name)
    except Exception as e:
        pass


# This method will establish the connection with the newly created DB
def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(host=host_name, user=user_name, password=user_password, database=db_name)
    except Error as e:
        print("Error while connecting to MySQL", e)

    return connection


# Use this function to create the tables in a database
def create_table(connection, table_creation_statement):
    try:
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute(table_creation_statement)
    except Exception as e:
        print("Error while connecting to MySQL", e)


# Perform all single insert statements in the specific table through a single function call
def create_insert_query(connection, query):
    # This method will perform creation of the table
    # this can also be used to perform single data point insertion in the desired table
    try:
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute(query)
    except Exception as e:
        print("Error while connecting to MySQL", e)


# retrieving the data from the table based on the given query
def select_query(connection, query):
    # fetching the data points from the table 
    try:
        if connection is not None:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print("Error while connecting to MySQL", e)

    return None


# Execute multiple insert statements in a table
def insert_many_records(connection, sql, val):
    try:
        if connection is not None:
            cursor = connection.cursor()
            cursor.executemany(sql, val)
            connection.commit()
            return True
    except Exception as e:
        print("Error while connecting to MySQL", e)

    return False

def execute(connection, query):
    try:
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            return True
    except Exception as e:
        print("Error while connecting to MySQL", e)

    return False

def close(connection):
    connection.close()
import os
from typing import Union
import re
import logging
import mysql.connector

DATABASE_URL = os.environ.get("<environment_variable_name>")
credential = [x for x in re.split('/|:|@', DATABASE_URL)[1:] if x != '']

username = str(credential[0])
password = str(credential[1])
host = str(credential[2])
port = str(credential[3])
database = str(credential[4])

#info = {"user": username, "password": password, "host": host, "database": database}

def tasteCheck(input_info: Union[str, list[str]] , expected_info: Union[type, list[type]]) -> bool:

    """Compares a given input to its expected type. Returns `False` if the input data type does not match the expected data type.

    Example:

    Input:
    ```Python
    mixed_list = [12, 'Hello World!', [1,2,3]]
    expected_types = [int, str, list]

    res = tasteCheck(mixed_list, expected_types)

    print(res)
    ```
    Output:
    ```Python
    True
    ```
    """

    if type(input_info) != list:
        if type(input_info) == expected_info:
            return True
        else:
            return False
    else:
        temp = list(zip(input_info, expected_info))
        results = [True if type(inp) == exp else False for inp, exp in temp]
        return all(results)

def tupleToString(Data : Union[tuple, list[tuple]]) -> str:
    """
    Feeding a list of tuples or a single tuple to the function, it will transform them into a string. For example `tupleToString( ('column', 'value') )` will return `"column = value"`.
    """
    result = ""

    if type(Data) == list and len(Data) >= 1:
        for data in Data:
            column = str(data[0])
            value = str(data[1])

            result += "{} = {},".format(column, value)
      
        result = result.rstrip(result[-1])
        return result
   
    else:
        column = str(Data[0])
        value = str(Data[1])
        result = "{} = {}".format(column, value)
        return result



def runCustomQuery(QUERY : str, commit : bool = False, fetch : bool = False) -> tuple[bool, Union[None, str, list[tuple]]]:

    """     
    Run a custom query.

    Parameters:
        - `QUERY`[String]: The query you want to run.
        - `commit`[Boolean]: Commit any changes to the table. `False` by default.
        - `fetch`[Boolean]: If you're expecting a result, set to `True`. It's `False` by default.
    
    Output:
        - If the query is successfully executed it will return `True`. Otherwise, `False`.
        - (Optional) The result of the query will be returned if `fetch` is set to `True`.

    Note: Setting `fetch = True` will make the function return any result as a list of tuples.

    Example:

    Input:
    ```Python
    query = "SELECT COUNT(*) FROM TEST_TABLE;"

    _, res = runCustomQuery(query, fetch = True)

    print(res)
    ```
    Output:
    ```Python
    [(12,)]
    ```

    """

    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database = database
    )
    cur = conn.cursor()
    result : Union[str, None] = None

    try:
        cur.execute(QUERY)
        if commit: conn.commit()
        if fetch: result = cur.fetchall()
        cur.close()
        conn.close()
        return True, result
    except:
        logging.exception("There has been an error executing the query. Please check syntax.")
        return False, result

def createTable(tableName : str, attr : list[tuple], foreign_key : Union[tuple, list[tuple]] = None, auto_increment = False):
    
    ### DESCRIPTION ###
    """
    Create a table in the database.
    
    Parameters:
        - `tableName`[String]: Table name.
        - `attr`[Tuple]: List of column names, with their attributes and whether they can be `NULL`or not. Example: `[('Col', 'INT', 'NOT NULL'),...]`. To define a primary key, just put`PRIMARY KEY`instead of`NULL`or`NOT NULL`.
        - foreign_key [String]: If the table has any foreign keys, they should be provided as tuples. For example: `('Col', 'RefTab', 'RefCol' [Optionally: 'onDeleteAction', 'onUpdateAction'])`.
        - `auto_increment` [Boolean]: If you want the indices to increase automatically (by 1), set `auto_increment` to `True`. It's `False` by default.


    Output:
        - The function will output `True` if the command was successful, otherwise `False`.
    """

    ### ALGORITHM ###
    error_msg = "An error occured. Unexpected data type."

    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database = database
    )
    cur = conn.cursor()

    QUERY = "CREATE TABLE IF NOT EXISTS {} (".format(tableName)
    for col in attr:
        col_name = col[0]
        col_type = col[1]
        if_null = col[2]

        if tasteCheck([col_name, col_type, if_null], [str, str, str]):
            if if_null == "PRIMARY KEY" and auto_increment:
                QUERY += "{} {} {} AUTO_INCREMENT,".format(col_name, col_type, if_null)
            else:
                QUERY += "{} {} {},".format(col_name, col_type, if_null)
        else:
            logging.exception(error_msg)
            return False

    ### IF FOREIGN KEY IS PRESENT ##
    if foreign_key is not None:
        for FK in foreign_key:
            fk_col_name = FK[0]
            ref_table = FK[1]
            ref_col_name = FK[2]
            onDelete = FK[3] if len(FK) > 3 else None
            onUpdate = FK[4] if len(FK) > 4 else None
            
            if len(FK) == 3:
                if tasteCheck([fk_col_name, ref_table, ref_col_name], [str, str, str]):
                    QUERY += "FOREIGN KEY ({}) REFERENCES {} ({}),".format(fk_col_name, ref_table, ref_col_name)
            if len(FK) == 4:
                if tasteCheck([fk_col_name, ref_table, ref_col_name, onDelete or onUpdate], [str, str, str, str]):
                    action = "ON DELETE" if onDelete is not None else "ON UPDATE"
                    QUERY += "FOREIGN KEY ({}) REFERENCES {} ({}) {} {},".format(fk_col_name, ref_table, ref_col_name, action, onDelete or onUpdate)

    QUERY = QUERY.rstrip(QUERY[-1]) #remove last comma.
    QUERY += ");"

    ### EXECUTE THE QUERY ###
    try:
        cur.execute(QUERY)
        cur.close()
        conn.close()
        return True

    except:
        logging.exception("The query was not successfully executed. Please check that you have inserted the correct parameters and used the correct format.")
        return False


def dropTable(tableName : str) -> bool:
    """
    Delete the entire table. Please use this carefully.

    Parameters:
        - `tableName`[String]: Table name.
    
    Output:
        - If the query is successfully executed it will return `True`. Otherwise, `False`.
    """

    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database = database
    )
    cur = conn.cursor()

    QUERY = "DROP TABLE IF EXISTS {};".format(tableName)

    try:
        cur.execute(QUERY)
        cur.close()
        conn.close()
        return True
    except:
        logging.exception("There has been an error. {} was unsuccessfully dropped. Please check syntax.".format(tableName))
        return False
    

def updateTable(tableName : str, updated_attr: list[tuple], condition : str = None) -> bool:
    """
    Updates the entries of the table. Note that if you don't specify a condition, all records will be updated.

    Parameters:
        - `tableName`[String]: Table name.
        - `updated_attr`[Tuple]: Target column and updated value pair. Both need to be passed as strings.
        - `condition`[String]: Insert a custom condition, like `userID = 123456` or `COUNT < 3`. It will be `None` by default.
    
    Output:
        - If the query is successfully executed it will return `True`. Otherwise, `False`.
    """

    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database = database
    )
    cur = conn.cursor()

    QUERY = "UPDATE {} SET {} ".format(tableName, tupleToString(updated_attr))

    if condition is not None:
        QUERY += "WHERE {}".format(condition)

    QUERY += ";"

    try:
        cur.execute(QUERY)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        logging.exception("There has been an error executing the query. Please check syntax.")
        return False


def insertToTable(tableName : str, target_cols : Union[str, list[str]], values : Union[str, list[str]]) -> bool:
    """
    Insert values into the table.

    Parameters:
        - `tableName`[String]: Table name.
        - `target_cols`[String]: Columns that are going to be affected.
        - `values`: Values that will be inserted into the target columns.
    
    Output:
        - If the query is successfully executed it will return `True`. Otherwise, `False`.
    """

    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database = database
    )
    cur = conn.cursor()

    if tasteCheck(values, [str for _ in range(len(values))]):
        QUERY = "INSERT INTO {} ({}) VALUES ({});".format(tableName, ', '.join(target_cols) if type(target_cols) == list else target_cols, ', '.join(values) if type(values) == list else values)
    else:
        values = [str(x) for x in values]
        QUERY = "INSERT INTO {} ({}) VALUES ({});".format(tableName, ', '.join(target_cols) if type(target_cols) == list else target_cols, ', '.join(values) if type(values) == list else values)
        
    try:
        cur.execute(QUERY)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        logging.exception("There has been an error executing the query. Please check syntax.")
        return False

def search(tableName : str, columns : Union[str, list[str]] = "*", count : bool = False, distinct : bool = False, condition : str = None) -> tuple[bool, Union[list[tuple], None]]:
    """
    Return the entries from the specified columns.

    Parameters:
        - `tableName`[String]: Table name.
        - `columns`[String]: Column name(s). If it's not specified, all columns will be selected.
        - `count`[Boolean]: Return the number of entries instead of the entries themselves.
        - `distinct`[Boolean]: Return only distinct entries (i.e. No repetitions).
        - `condition`[String]: Return entries that satisfy the condition. For example: `COL >= 10`.
    
    Output:
        - If the query is successfully executed it will return `True`. Otherwise, `False`.

    Example:

    Input:
    ```Python
    condition = "COL1 >= 150000"

    _, res = search('TEST', count=True, condition = condition)

    print(res)
    ```
    Output:
    ```Python
    1
    ```
    """

    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database = database
    )
    cur = conn.cursor()

    if count:
        if distinct:
            QUERY = "SELECT COUNT(DISTINCT {}) FROM {}".format(columns or ', '.join(columns), tableName)
        else:
            QUERY = "SELECT COUNT({}) FROM {}".format(columns or ', '.join(columns), tableName)
    else:
        if distinct:
            QUERY = "SELECT DISTINCT {} FROM {}".format(columns or ', '.join(columns), tableName)
        else:
            QUERY = "SELECT {} FROM {}".format(columns or ', '.join(columns), tableName)

    if condition is not None:
        QUERY += " WHERE {}".format(condition)

    QUERY += ";"

    try:
        cur.execute(QUERY)
        result = cur.fetchall()[0][0] if count else cur.fetchall()
        cur.close()
        conn.close()
        return True, result
    except:
        logging.exception("There has been an error executing the query. Please check syntax.")
        return False, None


def deleteEntry(tableName : str, condition: str = None, all : bool = False) -> bool:
    """
    Delete the entry (or entries) that matched the condition. 

    Parameters:
        - `tableName`[String]: Table name.
        - `condition`[String]: The condition statement. For example: `COUNT(OBJ) < 10`.
        - `all`[Boolean]: If you set this to `True`, all entries will be deleted from the table. It's `False` by default.
    
    Note: If `condition` and `all = True` are both set, nothing will happen. You can only set one of the two.

    Output:
        - If the query is successfully executed it will return `True`. Otherwise, `False`.
    """

    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database = database
    )
    cur = conn.cursor()
    
    if all and condition is None:
        QUERY = "DELETE FROM {};".format(tableName)
    elif condition is not None and not all:
        QUERY = "DELETE FROM {} WHERE {};".format(tableName, condition)
    else:
        logging.exception("You cannot have condition and all both set and you need at least one of them set. Please check the parameters.")
        return False

    try:
        cur.execute(QUERY)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        logging.exception("There has been an error executing the query. Please check syntax.")
        return False

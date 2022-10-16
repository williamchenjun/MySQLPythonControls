# MySQL/MariaDB Python Controls
I wrote a few functions to make it more convenient to run MySQL/MariaDB queries.

You will need to have `mysql` installed. There are plenty of tutorials on the internet. For mac, you can install using pip by running `pip install mysql-connector-python`.

## Quick Start
All the functions already have clear instructions and explanations in the code, but I will try to summarise it here as well.

### Table of Contents
- [Connecting to the Database](#connecting-to-the-database)
- [Aid Functions](#aid-functions)
- [Custom MySQL Queries with `runCustomQuery`](#custom-mysql-queries-with-runcustomquery)
- [Create a Table in the Database](#create-a-table-in-the-database)
- [Deleting a Table from the Database](#deleting-a-table-from-the-database)
- [Updating the Entries in a Table](#updating-the-entries-in-a-table)
- [Inserting Entries into the Table](#inserting-entries-into-the-table)
- [Retrieving Data from Table](#retrieving-data-from-table)
- [Deleting Entries from a Table](#deleting-entries-from-a-table)

### Connecting to the Database
```python
DATABASE_URL = os.environ.get("<environment_variable_name>")
credential = [x for x in re.split('/|:|@', DATABASE_URL)[1:] if x != '']

username = str(credential[0])
password = str(credential[1])
host = str(credential[2])
port = str(credential[3])
database = str(credential[4])
```
`DATABASE_URL` is a string and it will be the connection string to your database. It contains all the necessary information in order to make a connection. That is `"mysql://<username>:<password>@<host>:<port>/<database>"`. By storing your connection string in `DATABASE_URL`, through list comprehension, we filter out all the necessary information. (Note: I'm using `os.environ.get("...")` to get my connection string from the environment, since I'm using Heroku. You can either do the same, or you can just set `DATABASE_URL` equal to the connection string. However, that is not a secure practice if you're going to publish or deploy your code.)

### Aid Functions
The first two functions that appear in the code are only aid functions. They have no access to and cannot affect the database. 

The first one is `tasteCheck`. This function takes the parameters `input_info` (a string or list of strings), and `expected_info` (a data type or list of data types). It returns a boolean (true or false). The point of this function is to verify that the data type of a list of items you have is what you expect. That is, if you have the following list `[1, 'Hello', [2,3]]` you would expect the type of each item of the list to be respectively `[int, str, list]`. So if you run `tasteCheck([1, 'Hello', [2,3]], [int, str, list])` it will return `True` if the data types match, otherwise `False`.

The second function is `tupleToString`. It's a function that will convert a 2-item tuple `(a,b)` in the string `"a = b"`. If you haven't guessed it yet, this is used to make it easier for us to insert data in tables. The function only has one (mandatory) parameter and it should be a tuple or a list of tuples. For example, if you feed it `[(A,B), (C,D)]` it will return `"A=B, C=D"`.

### Custom MySQL Queries with `runCustomQuery`
Sometimes you might just want to run your own queries. This is made slightly more convenient by `runCustomQuery`. This function has only one mandatory parameter, and two optional ones. The first parameter is `QUERY` (a string) and you might have already guessed it: it represents the (custom) query that you want to run. If your query affects and changes the table (e.g. `INSERT`, `DELETE`, `ALTER`, etc.), then you should set `commit` to `True`. It's `False` by default. The last parameter, `fetch` (boolean), is also set to `False` by default. If you expect a result from your query (e.g. after running a `SELECT` query), then you should set this to `True`. The function will always return two values, the "status" of the process (it will return `True` if the query was successfully ran, otherwise `False`) and the "fetch result" if you expect any (otherwise, it's `None` by default). So everytime you use it, make sure to set it as `status, result = runCustomQuery(...)` to collect both outputs.

### Create a Table in the Database

This is pretty straightforward. If you're familiar with SQL, the way you create a table is by running the following query
```MYSQL
CREATE TABLE [IF NOT EXISTS] <tablename> (
{<COLUMN_NAME> <ATTR_TYPE> NULL|NOT NULL|PRIMARY KEY [AUTO_INCREMENT] [CHECK <condition>]}[, ...],
[FOREIGN KEY (<FOREIGN_KEY>) REFERENCES <REF_TABLE> (<REF_TABLE_PK>)[, ...]],
[ON DELETE <onDeleteAction>]
[ON UPDATE <onUpdateAction>]
);
```
> **Note**: Curly brackets imply that it's mandatory information, square brackets indicate optional information, and the ellipsis indicates that there can be multiple occurences of the same type. Angle brackets correspond to the name of tables, data types, actions or column names that you choose.

The function `createTable` makes this a bit simpler. It takes 4 parameter, 2 of which are mandatory. The first parameter is `tableName` (string) and I'm sure it's pretty obvious what is supposed to go there. The second parameter is `attr` (list of tuples) which corresponds to the `<COLUMN_NAME> <ATTR_TYPE> NULL|NOT NULL|PRIMARY KEY [AUTO_INCREMENT] [CHECK <condition>]` part of the code. Although, I haven't added a `CHECK` feature yet. The third parameter is `foreign_key` (tuple or a list of tuples) and as you might have guessed it lets you set specific columns as foreign keys. It is set to `None` by default. Lastly, `auto_increment` (boolean) should be set to `True` if you want your primary key to auto-increment. It's `False` by default.

The output of the function is the status. If the query runs successfully, it will return `True`. Otherwise, `False` (which means you might have to check your parameters).

### Deleting a Table from the Database
The function is used to drop (i.e. delete) a table from your database. `dropTable` only takes one parameter, which is the `tableName`. As you might expect, running this function will remove the specified table from the database and the output will be `True` if successful, `False` otherwise.

### Updating the Entries in a Table
To update the entrie(s) in a table, you can use `updateTable`. It takes 3 parameters: `tableName` (string), `updated_attr` (list of tuples) and `condition` (string). The first two are mandatory: `updated_attr` should be in the form `[('COLUMN_NAME', 'UPDATED_VALUE'), ...]`. This function only allows simple updates of the type `UPDATE <tableName> SET COLUMN = VALUE, ...`. The last parameter, `condition`, allows you to set a condition (Note: the condition needs to be written in SQL and passed as a string). For example: 
```python
#Fix needed: For now you have to also include " " for the values if they're strings.
columns_to_update = [('BookAge', '"Old"'), ('PageColor', '"Yellow"'), ('BookState', '"Bad"')] 
oldBooks = "DATEDIFF(yy, BookPublishDate, NOW()) >= 50"
stat = updateTable(tableName = 'BookShelf', updated_attr = columns_to_update, condition = oldBooks)

print(stat) #output: True
```
In SQL this would translate to 
```mysql
UPDATE BookShelf
SET BookAge = "Old", PageColor = "Yellow", BookState = "Bad"
WHERE DATEDIFF(yy, BookPublishDate, NOW()) >= 50;
```

### Inserting Entries into the Table
The function `insertToTable` is used to insert new entries into the specified table (one at a time). It takes 3 mandatory parameters: `tableName` (string), `target_cols` (string or list of strings) and `values` (string or list of strings). Example usage:

```python
target = ['USER_ID', 'IS_ADMIN']
values = [19674, 'FALSE']

stat = insertToTable('GroupAdministrators', target_cols = target, values = values)

print(stat) #output: True
```
Where the SQL equivalent is:
```mysql
INSERT INTO GroupAdministrators (USER_ID, IS_ADMIN)
VALUES (19674, FALSE);
```
### Retrieving Data from Table
To retrieve data from your table you should use `search`. This function can take 5 parameters, where only 1 is mandatory. `tableName` (string) is the only mandatory parameter, and if it's the only one defined, the function will return all table entries. The second parameter is `columns` (a string or list of strings) and it specifies the columns you want to select. It's set to `"*"` by default, meaning that it will select all the columns. (Note: It is possible to set new columns using the keyword "AS". Read more about it <a href="https://www.w3schools.com/sql/sql_ref_as.asp" target="_blank">here</a>). The third parameter is `count` (boolean) and you should set it to `True` if you want the function to return the number of entries selected. Otherwise, it's `False` by default. The fourth parameter is `distinct` (boolean) and if set to `True` it will return all distinct (i.e. unique) entries from your table. It's `False` by default. Lastly, we have `condition` (string) which allows you to, again, set some conditions in SQL and pass it as a string. Example usage:
```python
headers = ['Country', 'Temperature_Readings_1998', 'Temperature_Readings_2022', '(Temperature_Readings_1998 - Temperature_Readings_2022) AS Temperature_Diff']
developingCountries = "Country_GDP >= 1.0" #unit: trillion

stat, results = search('ClimateReadings', columns = headers, count = False, distinct = True, condition = developingCountries)

print(stat) #output: True
print(results) #outputs a list of tuples: [(Country, Temperature_Readings_1998, Temperature_Readings_2022, Temperature_Diff), ...]
```
The SQL equivalent is
```mysql
SELECT Country, Temperature_Readings_1998, Temperature_Readings_2022, (Temperature_Readings_1998 - Temperature_Readings_1998) AS Temperature_Diff
FROM ClimateReadings
WHERE Country_GDP >= 1.0;
```
### Deleting Entries from a Table
To delete entries from a table we use `deleteEntry`. Just like the other functions, it is pretty straightforward to use. The function has 3 parameters, where only 1 is mandatory: `tableName`(string), `condition`(string) and `all`(boolean). The first one we already know what it is. `condition` is the condition you want to set when deleting your entries (e.g. only delete entries older than a certain date). It's set to `None` by default. Lastly, if you set `all` to `True` the query will instruct the machine to delete all the entries in your table. So be careful with it! It's set to `False` by default. (Note: You can't have `all` set to `True` and have a `condition` at the same time. You can either specify a condition or delete all. If you don't specify either, it'll raise an error.)

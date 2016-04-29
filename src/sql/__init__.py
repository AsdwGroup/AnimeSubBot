    #!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A additional Sqlite-interface needed for the DatabaseConnection.
"""
# standard library
import sys
import time
# This is needed to sleep while trying
# to reconnect to the server.
# third party requirements
import mysql.connector
# The custom modules
import gobjects
import clogging
import language  # import the _() function!


class Api(object):
    """
    This class is user a mysql interface.
    
    It is a interface between the mysql connector that talks with 
    the database and the python code. As well dynamically creates
    the queries that have to be executed.       
    """

    def __init__(self,
                 User,
                 Password,
                 LanguageObject,
                 LoggingObject,
                 DatabaseName = None,
                 Host="127.0.0.1",
                 Port="3306",
                 ReconnectTimer = 3000,):

        """
        This API enables an easy DatabaseConnection to the mysql driver 
        and to the server with the database .
    
        VARIABLES:
            User                     ``string``                             
                contains the database user
            Password                 ``string``                               
                contains the database user password
            DatabaseName             ``string``                             
                contains the database name
            Host                     ``string``
                contains the database host ip
            Port                     ``string``
                contains the database port 
            OptionalObjects          ``dictionary``
                contains optional objects like the language object, 
                the logging object or else
        """

        self.User = User
        self.Password = Password
        self.Host = Host
        self.DatabaseName = DatabaseName
        self.Port = Port
        self.ReconnectTimer = (ReconnectTimer / 1000.0)


        # Predefining some attributes so that they later can be used for evil.
        
        self.LanguageObject = LanguageObject.CreateTranslationObject()
        # This is the language objects only value. 
        # It enables the translation of the texts. 
        self._ = self.LanguageObject.gettext

        self.LoggingObject = LoggingObject


        # Create the connection to the database.
        self.DatabaseConnection = None
        self.DatabaseConnection = self._CreateConnection_()

    def _CreateConnection_(self):
        """
        This method creates the mysql connection database.
        
        This method will return a mysql connection object if the
        connection could be created successfully. If not it will
        catch the error and make a log entry. 
        
        Variables:
            \-
        """

        try:
            config = {
                "user": self.User,
                "password": self.Password,
                "host": self.Host,
                "port": 3306,
                "use_pure":True,
                "raise_on_warnings": True,
            }
            
            if self.DatabaseName:
                config['database'] = self.DatabaseName
            
            return mysql.connector.connect(**config)

        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.LoggingObject.warning(
                    self._(
                        "The database connector returned following"
                        " error: {Error}"
                    ).format(Error=err) + " " +
                    self._(
                        "Something is wrong with your user name or "
                        "password."
                    ),
                )

            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.LoggingObject.error(
                    self._(
                        "The database connector returned following"
                        " error: {Error}"
                    ).format(Error=err) + " " +
                    self._(
                        "The database does not exist, please contact your "
                        "administrator."
                    )
                )

            elif err.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
                self.LoggingObject.critical(
                    self._(
                        "The database connector returned following"
                        " error: {Error}"
                    ).format(Error=err) + " " +
                    self._(
                        "The database server seems to be offline, please "
                        "contact your administrator."
                    )
                )

            else:
                self.LoggingObject.error(err)

        except Exception:
            self.LoggingObject.critical(
                self._(
                    "The database connector returned following "
                    "error: {Error}"
                ).format(Error=sys.exc_info()[0])
            )
            self.CloseConnection()


    def CloseConnection(self, ):
        """
        This method will close the open connection for good.
        
        Variables:
            \-
        """
        try:
            self.DatabaseConnection.close()
        except mysql.connector.Error as err:
            self.LoggingObject.error(
                self._("The database connector returned following error: "
                       "{Error}").format(Error=err) + " " + self._(
                    "The database connection could not be closed correctly,"
                    " please contact your administrator!"))
        except Exception:
            self.LoggingObject.critical(
                self._("The database connector returned following error: "
                       "{Error}").format(Error=sys.exc_info()[0]))

    def DetectConnection(self):
        """
        This method will check if the database connection is open.

        It return True if the connection exists else False.
        It as well tries to reconnect if no connection is available.

        Variables:
            \-
        """

        Connection = True
        while True:
            if self.DatabaseConnection is not None:
                try:
                    self.DatabaseConnection.reconnect()
                    Connection = True
                except mysql.connector.Error as err:
                    Connection = False

                    if (err.errno ==
                            mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR):
                        self.LoggingObject.warning(
                            self._("The database connector returned following"
                                   " error: {Error}").format(Error=err) + " " +
                            self._(
                                "Something is wrong with your user name or "
                                "password."),
                        )

                    elif (err.errno ==
                              mysql.connector.errorcode.ER_BAD_DB_ERROR):
                        self.LoggingObject.error(
                            self._("The database connector returned following"
                                   " error: {Error}").format(Error=err) + " " +
                            self._(
                                "The database does not exist, please contact"
                                " your administrator.")
                        )

                    elif (err.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR):
                        self.LoggingObject.critical(
                            self._("The database connector returned following"
                                   " error: {Error}").format(Error=err) + " " +
                            self._(
                                "The database server seems to be offline, "
                                "please contact your administrator.")
                        )

                    else:
                        self.LoggingObject.error(err)

                    if self._DieOnLostConnection is True:
                        raise SystemExit
                except Exception as Error:
                    Connection = False
                    self.LoggingObject.critical(
                        self._("The database connector returned following "
                               "error: {Error}").format(Error=Error))
                    if self._DieOnLostConnection is True:
                        raise SystemExit

                if self.DatabaseConnection.is_connected() is True:
                    if Connection is False:
                        self.LoggingObject.info(self._(
                            "The connection to the database server has been "
                            "reestablished.")
                        )
                    return True

                else:
                    Connection = False
                    self.LoggingObject.critical(self._(
                        "There is no connection to the database, please"
                        " contact your administrator!")
                    )
            else:
                Connection = False
                self.DatabaseConnection = self.CreateConnection()

            # sleep for the given time
            time.sleep(self.ReconnectTimer)

    def CreateCursor(self,
                     Buffered=False,
                     Dictionary=True):
        """
        This method creates the connection cursor
        
        It returns the connection cursor.
        
        Variables:
            Buffered            ``boolean``
                If the cursor is buffered or not default to False.
           Dictionary           ``boolean``
               If the cursor should return a dictionary or not.
        """
        return self.DatabaseConnection.cursor(
            buffered=Buffered,
            dictionary=Dictionary
        )

    def GetLastRowId(self, Cursor):
        """
        This method returns the last used row id of the cursor.
        
        Variables:
            Cursor                ``object``
                cursor object.
        """
        return Cursor.lastrowid

    def DestroyCursor(self, Cursor):
        """
        This method closes the cursor.
        
        Variables:
            Cursor                ``object``
                cursor object.
        """
        return Cursor.close()

    def ExecuteTrueQuery(self,
                         Cursor,
                         Query,
                         Data=None):
        """
        A method to execute the query statements.
        
        All the query will be passed over this method so that the 
        exceptions can be catched at one central place. This method
        will return the results from the database.
        
        Variables:
            Cursor                ``object``
                contains the cursor object
            Query                 ``string``
                contains the query that has to be executed
            Data                  ``list``
                contains the data to be send to the databse
         
        .. code-block:: python\n       
            cursor = cnx.cursor(prepared=True)
            stmt = "SELECT fullname FROM employees WHERE id = %s" # (1)
            cursor.execute(stmt, (5,))                            # (2)
            # ... fetch data ...
            cursor.execute(stmt, (10,))                           # (3)
            # ... fetch data ...
            
            Query = "SELECT fullname FROM employees WHERE id = %s or id = %s"
            Data = (10, 15)
        """
        try:
            if Data != None:
                if not isinstance(Data, dict) and not isinstance(Data, list):
                    if isinstance(Data, int):
                        Data = (Data,)
                    elif isinstance(Data, str):
                        Data = (Data,)
                    Data = [str(i) for i in list(Data)]
                    Cursor.execute(Query, Data)
                else:
                    Cursor.execute(Query, Data)
            else:
                Cursor.execute(Query)

            CursorContent = []
            for Item in Cursor:
                CursorContent.append(Item)
            return CursorContent

        except mysql.connector.Error as err:
            self.LoggingObject.error(
                self._("The database returned following error: {Error}"
                       ).format(Error=err) + " " +
                self._(
                    "The executed query failed, please contact your "
                    "administrator."
                )
            )
            if isinstance(Data, list):
                Data = ', '.join((str(i) for i in Data))
            elif isinstance(Data, dict):
                Data = ', '.join("{Key}={Value}".format(
                    Key=Key, Value=Value) for (Key, Value) in Data.items()
                                 )
            self.LoggingObject.error(
                self._("The failed query is:\nQuery:\n{Query}\n\nData:\n{Data}"
                       ).format(
                    Query=Query,
                    Data=Data)
            )

    def CreateTable(self,
                    Cursor,
                    TableName,
                    TableData,
                    IfNotExists=True,
                    Engine="InnoDB"):
        """
        A method to dynamically create a table entry to the database.
        
        HOW TO USE:\n
        .. code-block:: python\n
            TableData = (
                ('Id', 'INT UNSIGNED NOT NULL AUTO_INCREMENT'),
                ('Unique', 'ID'),
                ('PRIMARY KEY', 'ID'),
                ('Foreigh Key', 'ID', 'Persons(P_Id)')
                )
                    
        Variables:
            Cursor                ``object``
                contains the cursor object
            TableName             ``string``
                contains the table name that has to be created
            TableData             ``array (list or tuple)``
                contains the table columns that will be created
            IfNotExists           ``boolean``
                determines if the query will be created with the prefix
                ``IF NOT EXISTS`` is used as a default since it doesn't 
                really matter
            Engine                ``string``
                determine what mysql engine will be used
                
        """

        try:
            Query = "CREATE TABLE "
            if IfNotExists:
                Query += "IF NOT EXISTS "

            Query += TableName + " ("

            PrimaryKeyId = None
            UniqueKeyId = None
            ForeignKeyId = None

            for i in range(len(TableData)):
                if (TableData[i][0].lower() != 'primary key' and
                            TableData[i][0].lower() != 'unique' and
                            TableData[i][0].lower() != 'foreign key'):
                    if i == 0:
                        Query += TableData[i][0] + " " + TableData[i][1]
                    else:
                        Query += ", " + TableData[i][0] + " " + TableData[i][1]

                else:
                    if (TableData[i][0].lower() == 'primary key'):
                        PrimaryKeyId = i
                    elif TableData[i][0].lower() == 'unique':
                        UniqueKeyId = i
                    elif TableData[i][0].lower() == 'foreign key':
                        ForeignKeyId = i

            # If a unique key has been added.
            if UniqueKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += (" " + TableData[UniqueKeyId][0] + " (" +
                          TableData[UniqueKeyId][1] + ")"
                          )

            # If a Primary Key has been added.
            if PrimaryKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += (" " + TableData[PrimaryKeyId][0] + " (" +
                          TableData[PrimaryKeyId][1] + ")"
                          )

            # If a Foreign Key has been added.
            if ForeignKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += (" " + TableData[ForeignKeyId][0] + " (" +
                          TableData[ForeignKeyId][1] + ") REFERENCES " +
                          TableData[ForeignKeyId][2]
                          )

            Query += ")"

            if Engine != None:
                if Engine in ("MRG_MYISAM",
                              "MyISAM",
                              "BLACKHOLE",
                              "CSV",
                              "MEMORY",
                              "ARCHIVE",
                              "InnoDB"):
                    Query += "ENGINE=" + Engine

            Query += ";"
            Cursor.execute(Query)
            return True

        except mysql.connector.Error as err:
            self.LoggingObject.error(
                self._("The database connector returned following error: "
                       "{Error}").format(Error=err) + " " +
                self._("The following database table \"{TableName}\" could not"
                       " be created, please contact your administrator."
                       ).format(TableName=TableName),
            )
            self.DatabaseConnection.rollback()
            return False

    def SelectEntry(self,
                    Cursor,
                    FromTable,
                    Columns,
                    OrderBy=[None],
                    Amount=None,
                    Where=[],
                    Data=(),
                    Distinct=False, ):
        """
        A simple SQL SELECT builder method
        
        This method will be replaces in the future by the query class
        generator.
        
        Variables:
            Cursor                ``object``
                contains the cursor object  
                
            FromTable,            ``string``
                contains the table name from which the system takes
                the information
            
            Columns               ``array (list or tuple)``
                contains the columns to be inserted into
            
            OrderBy               ``array (list or tuple)``
                contains the order in which the data will be returned
                
                .. code-block:: python\n
                    Example
                        [
                            [
                                column_name, 
                                "ASC"
                            ],
                            [
                                column_name, 
                                    #if the order is empty ASC will be used
                            ],
                            [
                                column_name,
                                "DESC"
                            ]
                        ] 
                
            Amount                ``None or integer``
                is the limit of entries that will be returned
                
            Where                 ``array (list or tuple)`` 
                contains the filter of the query
                Example\n
                .. code-block:: python\n
                    [
                        [
                            'column_name', 
                            operator, 
                            value
                        ], 
                        operator,
                         [    
                             column_name, 
                             operator, 
                             "%s" 
                             # if %s is used the value has to be 
                             # mentioned in the Data variable
                        ]
                    ]
                    
            Data                 ``array (list or tuple)``
                contains the data that will be inserted into the query
                
            Distinct             ``boolean``
                determines if the search is distinct or not
        """

        Query = ["SELECT"]

        if Distinct:
            Query.append("DISTINCT")

        # columns
        for i in range(len(Columns)):
            if i + 1 < len(Columns):
                Query.append(Columns[i] + ",")
            else:
                Query.append(Columns[i])

        # from Table
        Query.append("FROM " + FromTable)

        # Where
        if Where != []:
            Query.append("WHERE")
            for i in range(len(Where)):
                if type(Where[i]) == type([]):
                    Query.append(Where[i][0])
                    Query.append(Where[i][1])
                    Query.append("{0}".format(Where[i][2]))
                elif type(Where[i]) == type(""):
                    Query.append(Where[i])

                #                 if i+1 != len(Where):
                #                     Query.append(",")

                # print(Where[i])

                # Query.append(Where[i])

        # Order By
        if OrderBy[0] is not None:
            Query.append("ORDER BY")

            for i in range(len(OrderBy)):
                for x in range(len(OrderBy[i])):
                    if not OrderBy[i] in ("and", "or"):
                        Query.append(OrderBy[i][x])
                    else:
                        Query.append(OrderBy[i])

                if i + 1 < len(OrderBy):
                    Query.append(",")



        # Limit
        if (Amount is not None) and (isinstance(Amount, int)):
            Query.append("LIMIT " + str(Amount))

        Query.append(";")

        Query = ' '.join([str(i) for i in Query])

        if Data == ():
            return self.ExecuteTrueQuery(Cursor, Query, )
        else:
            return self.ExecuteTrueQuery(Cursor, Query, Data)

    def UpdateEntry(self,
                    Cursor,
                    TableName,
                    Columns,
                    Where=[],
                    Autocommit=False):
        """
        This method will update a record in the database.
        
        This method will return something like this:\n
        .. code-block:: sql\n
            UPDATE table_name
            SET column1=value1,column2=value2,...
            WHERE some_column=some_value;
        
        Variables:
            Cursor                ``object``
                contains the cursor object 
                 
            TableName             ``string``
                contains the table name into wich the system will 
                insert the information 
                
            Columns               ``dictionary``
                contains the columns into that will be inserted
                Example\n
                .. code-block:: python\n
                    {
                        'id' : id,
                        Name': 'Max'
                    }
                
            Where                 ``array (list or tuple)``
                contains the query filter
                Example\n
                .. code-block:: python\n
                    [
                        [
                            "Id", 
                            "=", 
                            2
                        ], 
                        "AND", 
                        "(", 
                        [
                            "as", 
                            "65" 
                            # Here will automatically the equality 
                            # operator be used. ("=")
                            
                        ], 
                        "OR", # This will raise an error
                        ")",
                    ]
                
            Autocommit            ``boolean``
                If autocommit is true the method will automatically
                commit the values to the database.
            
        """

        Query = "UPDATE "

        Query += TableName

        Query += " SET "

        # Create the key value pair 
        temp = []
        for Key in Columns.keys():
            temp.append("{Key}=%({Key})s".format(Key=str(Key)))

        Query += ', '.join(temp)

        if Where != []:

            Query += " WHERE "

            # This variable is used to ensure that no 2 operator will 
            # follow each other
            LastTypeAnOperator = False
            for i in range(len(Where)):

                if type(Where[i]) == type([]):
                    LastTypeAnOperator = False
                    Where[i] = [str(i) for i in Where[i]]
                    Query += str(Where[i][0])
                    if Where[i][1].upper() in ("=",
                                               "<",
                                               ">",
                                               "<>",
                                               "!=",
                                               ">=",
                                               "<=",
                                               "BETWEEN",
                                               "LIKE",
                                               "IN"):
                        Query += Where[i][1]
                        Query += "%({Where})s".format(Where=Where[i][0] +
                                                            "Where"
                                                      )
                        Columns[Where[i][0] + "Where"] = Where[i][2]
                    else:
                        Query += "=%({Where})s".format(Where=Where[i][0] +
                                                             "Where"
                                                       )
                        Columns[Where[i][0] + "Where"] = Where[i][1]

                elif isinstance(Where[i], str):
                    if LastTypeAnOperator is False:
                        LastTypeAnOperator = True
                        if Where[i].upper() in ("(", ")", "AND", "OR"):
                            Query += " {} ".format(Where[i])
                        else:
                            raise ValueError(self._(
                                "The where type in your query is not in the "
                                "list of valid types. {Error}").format(
                                Error=Where[i])
                            )
                    else:
                        raise ValueError(self._("There where two operator "
                                                "behind each other that "
                                                "doesn't work.")
                                         )
        Query += ";"
        #         print(Query)
        #         print(Columns)
        #         print(Query % Columns)

        self.ExecuteTrueQuery(Cursor, Query, Columns)
        if Autocommit is True:
            # Autocommit the update to the server
            self.Commit()
        return True

    def InsertEntry(self,
                    Cursor,
                    TableName,
                    Columns={},
                    Duplicate=None,
                    AutoCommit=False):
        """
        This method will insert any type of entry into the database.
        
        This method will return something like this:\n
        .. code-block:: sql\n
            UPDATE table_name
            SET column1=value1,column2=value2,...
            WHERE some_column=some_value;
        
        Variables:
            Cursor                ``object``
                contains the cursor object 
                 
            TableName             ``string``
                contains the table name into wich the system will 
                insert the information 
                
            Columns               ``dictionary``
                contains the columns into that will be inserted
                Example\n
                .. code-block:: python\n
                    {
                        'id' : id,
                        Name': 'Max'
                    }
            Duplicate             ``None or dictionary``
                contains the columns in those the possible duplicates 
                values exist
                
            Autocommit            ``boolean``
                If autocommit is true the method will automatically
                commit the values to the database.
        """

        Query = "INSERT INTO "

        Query += TableName + " ("

        Query += ', '.join(Columns.keys())
        Query += ") VALUES ("
        Query += ", ".join(["%(" + str(i) + ")s" for i in Columns.keys()])

        Query += ")"

        if Duplicate != None:
            Query += " ON DUPLICATE KEY UPDATE "
            Duplicates = []
            for Key in Duplicate.keys():
                Duplicates.append("{Key} = %({Value})s".format(Key=str(Key),
                                                               Value=str(Key)
                                                               )
                                  )

            Query += ', '.join(Duplicates)
        Query += ";"

        # print(Query)

        self.ExecuteTrueQuery(Cursor, Query, Columns)

        if AutoCommit:
            # Make sure data is committed to the database
            self.Commit()
        return True

    def DeleteEntry(self,
                    Cursor,
                    TableName,
                    Where={},
                    AutoCommit=False ):
        """
        This method will delete the selected entry.

        .. code-block:: sql\n
            DELETE FROM table_name WHERE some_column=some_value;

        .. code-block:: python\n
            Where = {
                some_column:some_value,
                some_column2:some_value2;
            }
        """

        try:
            Query = ["DELETE",
                     "FROM",
                     TableName,
                     "WHERE"
                     ]

            if not Where:
                raise AttributeError(self._("The where clause is not "
                                            "available")
                                     )

            for Key, Value in Where:
                Query.append("{Value}=%({Key})s".format(
                    Value=Value,
                    Key=Key
                )
                )

            # Join the query to a string and append a semicolon.
            Query = " ".join(Query)+";"
            self.ExecuteTrueQuery(Cursor, Query, Where)

            if AutoCommit:
                # Make sure data is committed to the database
                self.Commit()

            return True

        except AttributeError as Error:
            self.LoggingObject.error(Error)
            raise

        except Exception as Error:
            self.LoggingObject.error(
                self._("The database connector returned following error: "
                       "{Error}").format(Error = Error)
            )

            return False

    def Commit(self, ):
        """
        This method will commit the changes to the database.
        
        Variables:
            Cursor                ``object``
                contains the cursor object 
        """
        try:
            self.DatabaseConnection.commit()
        except mysql.connector.Error as Error:
            self.LoggingObject.error(
                self._("The database connector returned following error:"
                       " {Error}").format(Error=Error))
            self.DatabaseConnection.rollback()

    def Rollback(self,):
        """
        This method will rollback the changes made.
        """

        self.DatabaseConnection.rollback()
                
class SqlDatabaseInstaller(object):
    """
    This class is soley here for the installation of the database 
    structure.
    
    DATABASE STRUCTURE:
            
        +------------------------------------------------------------+    
        |User_Table                                                  |
        +==================+===================+=====================+  
        |Internal_Id       |contains the       |Integer              |  
        |                  |internal user id   |(auto increment)     |                  
        +------------------+-------------------+---------------------+ 
        |External_Id       |contains the       |Integer              |    
        |                  |external user id   |(Null)               |
        |                  |used by telegram   |                     | 
        +------------------+-------------------+---------------------+ 
        |Creation_Date     |contains the       |Timestamp            |
        |                  |creation date of   |(current timestamp)  |
        |                  |of the user entry  |                     |
        +------------------+-------------------+---------------------+        
        |User_Name         |contains the user  |Text                 |          
        |                  |name if it exists  |(Null)               |
        +------------------+-------------------+---------------------+      
        |First_Name        |contains the first |Text                 |         
        |                  |name if it exists  |(Null)               |
        +------------------+-------------------+---------------------+
        |Last_Name         |contains the last  |Text                 |                       
        |                  |name id exists     |(Null)               |
        +------------------+-------------------+---------------------+
        |Is_Admin          |if the user is a   |Boolean              |    
        |                  |bot admin          |(False)              |
        +------------------+-------------------+---------------------+
        |    UNIQUE (External_User_ID)                               |     
        +------------------------------------------------------------+   
        |    PRIMARY KEY (Internal_User_ID)                          |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+
        |Group_Table                                                 |
        +==================+===================+=====================+
        |Internal_Id       |contains the Id    |Integer              | 
        |                  |of the Group       |(auto increment)     |
        +------------------+-------------------+---------------------+
        |External_Id       |contains the       |Integer              |    
        |                  |external user id   |(Null)               |
        |                  |used by telegram   |                     | 
        +------------------+-------------------+---------------------+
        |Creation_Date     |contains the       |Timestamp            |
        |                  |creation date of   |(current timestamp)  |
        |                  |of the user entry  |                     |
        +------------------+-------------------+---------------------+
        |User_Name         |contains the user  |Text                 |          
        |                  |name if it exists  |(Null)               |
        +------------------+-------------------+---------------------+ 
        |    UNIQUE (External_User_ID)                               |     
        +------------------------------------------------------------+   
        |    PRIMARY KEY (Internal_User_ID)                          |
        +------------------------------------------------------------+
        
        
        +------------------------------------------------------------+
        |Session_Table                                               |
        +==================+===================+=====================+ 
        |Session_Id        |contains the Id    |Integer              | 
        |                  |of the session     |(auto increment)     |
        +------------------+-------------------+---------------------+ 
        |Command_By_User   |contains the       |Integer              |
        |                  |internal user id   |(Null)               |
        +------------------+-------------------+---------------------+ 
        |Command           |contains the last  |Varchar(256)         |
        |                  |send command       |(Null)               |
        +------------------+-------------------+---------------------+ 
        |Last_Used_Id      |contains the last  |Integer              | 
        |                  |used id of         |(Null)               |
        |                  |whatever was used  |                     |
        +------------------+-------------------+---------------------+ 
        |    UNIQUE (Command_By_User)                                |     
        +------------------------------------------------------------+   
        |    PRIMARY KEY (Session_Id)                                |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+
        |Messages_Table                                              |
        +==================+===================+=====================+ 
        |Id                |contains the Id    |Integer              | 
        |                  |of the message     |(auto increment)     |
        +------------------+-------------------+---------------------+
        |Creation_Date     |contains the       |Timestamp            |
        |                  |creation date of   |(current timestamp)  |
        |                  |of the user entry  |                     |
        +------------------+-------------------+---------------------+
        |Message           |contains the json  |TEXT                 |
        |                  |sting that was send|(Null)               |
        +------------------+-------------------+---------------------+
        |Set_By_User       |contains the Id    |Integer              | 
        |                  |of the user that   |(Null)               |
        |                  |has set the        |                     |
        |                  |setting            |                     |
        +------------------+-------------------+---------------------+ 
        |    FOREIGN KEY Set_By_User/User_Table(Internal_User_Id)    |     
        +------------------------------------------------------------+ 
        |    PRIMARY KEY (Id)                                        |
        +------------------------------------------------------------+        
        
        +------------------------------------------------------------+ 
        |Setting_Table                                               |
        +==================+===================+=====================+ 
        |Setting_Id        |contains the Id    |Integer              | 
        |                  |of the setting     |(auto increment)     |
        +------------------+-------------------+---------------------+
        |Creation_Date     |contains the       |timestamp            |
        |                  |creation date of   |(current timestamp)  |
        |                  |of the settings    |                     |     
        |                  |entry              |                     |
        +------------------+-------------------+---------------------+     
        |Settings_Name     |contains the name  |Varchar(128)         |
        |                  |of the setting     |(Null)               |    
        +------------------+-------------------+---------------------+ 
        |Default_String    |contains the       |Varchar(256)         |   
        |                  |default string     |(Null)               |  
        |                  |value              |                     | 
        +------------------+-------------------+---------------------+ 
        |Default_Integer   |contains the       |Integer              |        
        |                  |default integer    |(Null)               |   
        |                  |value              |                     | 
        +------------------+-------------------+---------------------+ 
        |Default_Boolean   |contains the       |Boolean              |
        |                  |default bloolean   |(Null)               |
        |                  |value              |                     | 
        +------------------+-------------------+---------------------+ 
        |    PRIMARY KEY (Setting_Id)                                |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+
        |User_Setting_Table                                          |
        +==================+===================+=====================+ 
        |User_Setting_Id   |contains the Id    |Integer              | 
        |                  |of the setting     |(auto increment)     |
        +------------------+-------------------+---------------------+
        |Creation_Date     |contains the       |timestamp            |
        |                  |creation date of   |(current timestamp)  |
        |                  |of the settings    |                     |     
        |                  |entry              |                     |
        +------------------+-------------------+---------------------+  
        |Master_Setting_Id |contains the Id    |Integer              | 
        |                  |of the setting     |(Null)               |
        |                  |from the           |                     |
        |                  |Sessions_Table     |                     |
        +------------------+-------------------+---------------------+  
        |Set_By_User       |contains the Id    |Integer              | 
        |                  |of the user that   |(Null)               |
        |                  |has set the        |                     |
        |                  |setting            |                     |
        +------------------+-------------------+---------------------+  
        |User_String       |contains the       |Varchar(256)         |   
        |                  |default string     |(Null)               |  
        |                  |value              |                     | 
        +------------------+-------------------+---------------------+ 
        |User_Integer      |contains the       |Integer              |        
        |                  |set integer        |(Null)               |   
        |                  |value              |                     | 
        +------------------+-------------------+---------------------+ 
        |User_Boolean      |contains the       |Boolean              |
        |                  |set bloolean       |(Null)               |
        |                  |value              |                     | 
        +------------------+-------------------+---------------------+
        |    FOREIGN KEY Master_Setting_Id/Setting_Table(Setting_Id) |     
        +------------------------------------------------------------+ 
        |    FOREIGN KEY Set_By_User/User_Table(Internal_User_Id)    |     
        +------------------------------------------------------------+         
        |    PRIMARY KEY (User_Setting_Id)                           |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+
        |Channel_Table                                               |
        +==================+===================+=====================+
        |Internal_Id       |contains the Id    |Integer              | 
        |                  |of the Anime       |(auto increment)     |
        +------------------+-------------------+---------------------+
        |External_Name     |contains the name  |Text                 |
        |                  |of the channel     |(Null)               |
        +------------------+-------------------+---------------------+
        |Creation_Date     |contains the       |timestamp            |
        |                  |creation date of   |(current timestamp)  |
        |                  |of the anime       |                     |     
        |                  |entry              |                     |
        +------------------+-------------------+---------------------+     
        |True_Name         |contains the       |Varchar(128)         |
        |                  |actuall name of the|(Null)               |
        |                  |channel            |                     |
        +------------------+-------------------+---------------------+
        |Description       |contains the       |Text                 |
        |                  |description of the |(Null)               |
        |                  |anime (will be sent|                     | 
        |                  |to the channel     |                     |
        |                  |after upload       |                     |
        +------------------+-------------------+---------------------+
        |    UNIQUE (External_Name)                                  |     
        +------------------------------------------------------------+ 
        |    PRIMARY KEY (Internal_Id)                               |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+
        |Anime_Table                                                 |
        +==================+===================+=====================+ 
        |Anime_Id          |contains the Id    |Integer              | 
        |                  |of the Anime       |(auto increment)     |
        +------------------+-------------------+---------------------+
        |Creation_Date     |contains the       |timestamp            |
        |                  |creation date of   |(current timestamp)  |
        |                  |of the anime       |                     |     
        |                  |entry              |                     |
        +------------------+-------------------+---------------------+     
        |Anime_Name        |contains the name  |Varchar(128)         |
        |                  |of the Anime       |(Null)               |    
        +------------------+-------------------+---------------------+
        |Airing_Year       |contains the year  |YEAR(4)              |
        |                  |of the first airing|(Null)               |
        +------------------+-------------------+---------------------+
        |MyAnimeList_Url   |contains the url   |Varchar(2083)        |
        |                  |to the anime on    |(Null)               |
        |                  |MyAnimeList.net    |                     |
        +------------------+-------------------+---------------------+
        |Telegram_Url      |contains the url   |Varchar(2083)        |
        |                  |to the anime on    |(Null)               |
        |                  |our channel        |                     |
        +------------------+-------------------+---------------------+
        |Channel_Id        |contains the       |Integer              | 
        |                  |internal Id of the |(Null)               |
        |                  |channel            |                     |
        +------------------+-------------------+---------------------+
        |Image_Name        |contains the MD5   |Binary(16)           |
        |                  |for directory      |(Null)               |
        |                  |where the image is |                     | 
        |                  |stored on the      |                     | 
        |                  |filesystem         |                     | 
        +------------------+-------------------+---------------------+
        |    FOREIGN KEY Channel_Id/Channel_Table(Internal_Id)       | 
        +------------------------------------------------------------+
        |    PRIMARY KEY (Id)                                        |
        +------------------------------------------------------------+

    """
    
    def __init__(self,
                 User,
                 Password,
                 DatabaseName,
                 Language,
                 Logging,
                 Host="127.0.0.1",
                 Port="3306",
                 ReconnectTimer = 3000
                 ):
                 
        """
        This is the database installer class that will install the
        database if needed.
    
        VARIABLES:
            User                     ``string``                             
                contains the database user
            Password                 ``string``                               
                contains the database user password
            DatabaseName             ``string``                             
                contains the database name
            NewDatabase                   ``boolean``
                set's if a new database shall be created or just adding
                the tables.
            Host                     ``string``
                contains the database host ip
            Port                     ``string``
                contains the database port 
        """
        self.User = User
        self.Password = Password
        self.DatabaseName = DatabaseName
        self.Host = Host
        self.Port = Port
        self.ReconnectTimer = ReconnectTimer
        self.DatabaseName = self.DatabaseName         
        self.Language = Language
        self.Logger = Logging   
        
    def _NewSqlObject_(self, DatabaseName = None):

        ApiObject = Api(
            User = self.User,
            Password = self.Password,
            LanguageObject = self.Language,
            LoggingObject = self.Logger,
            DatabaseName = DatabaseName,
            Host = self.Host,
            Port = self.Port,
            ReconnectTimer = self.ReconnectTimer,
        )
        
        Cursor = ApiObject.CreateCursor()
        return ApiObject, Cursor 
    
    def Install(self, InstallDB = False):
        if InstallDB is True:
            self.SqlObject, self.Cursor = self._NewSqlObject_(None)
            self._CreateDatabase_(self.Cursor, self.DatabaseName)
            self.SqlObject.CloseConnection()
                
        # rebuild sqlobject with safe connection
        self.SqlObject, self.Cursor = self._NewSqlObject_(self.DatabaseName)
        self._CreateMainTables_()
        self.SqlObject.CloseConnection()
        
    def _CreateDatabase_(self, Cursor, DatabaseName):
        """
        This method will create a database. Use with caution!
        
        Variables:
            Cursor                ``object``
                contains the cursor object
            DatabaseName          ``string``
                contains the database name that has to be created
        """
        Query = ("CREATE DATABASE IF NOT EXISTS {DatabaseName} DEFAULT "
                "CHARACTER SET 'utf8'".format(DatabaseName=DatabaseName)
                )

        self.ExecuteTrueQuery(
            Cursor,
            Query
        )
    
    def _CreateMainTables_(self):
        """
        This method will create all the default tables and data.
        
        Variables:
            Cursor                ``object``
                contains the cursor object        
        """

        # First all the tables
        # UserTable
        TableName = "User_Table"
        TableData = (
            ("Internal_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("External_Id", "Integer DEFAULT NULL"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("User_Name", "TEXT DEFAULT NULL"),
            ("First_Name", "TEXT DEFAULT NULL"),
            ("Last_Name", "TEXT DEFAULT NULL"),
            ("Is_Admin", "Boolean DEFAULT FALSE"),
            ("UNIQUE", "External_Id"),  
            ("PRIMARY KEY", "Internal_Id"),
        )

        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        
        # Group_Table
        TableName = "Group_Table"
        TableData = (
            ("Internal_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("External_Id", "Integer DEFAULT NULL"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("User_Name", "TEXT DEFAULT NULL"),
            ("UNIQUE", "External_Id"),  
            ("PRIMARY KEY", "Internal_Id"),
        )
        
        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
 
        
        # SessionHandling - saves the last send command
        TableName = "Session_Table"
        TableData = (
            ("Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("Command_By_User", "Integer DEFAULT NULL"),  # is the internal id of the user
            ("Command", "Varchar(256) DEFAULT NULL"),
            ("Last_Used_Id", "Integer DEFAULT NULL"),
            ("FOREIGN KEY", "Command_By_User", "User_Table(Internal_Id)"),
            ("UNIQUE", "Command_By_User"),
            ("PRIMARY KEY", "Id"),
        )
        
        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        
        # List of messages send to the bot
        TableName = "Input_Messages_Table"
        TableData = (
            ("Id", "Integer NOT NULL AUTO_INCREMENT"),            
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Message", "Text"),
            ("PRIMARY KEY", "Id"),
        )

        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        
        # List of messages send from the bot
        TableName = "Output_Messages_Table"
        TableData = (
            ("Id", "Integer NOT NULL AUTO_INCREMENT"),            
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Message", "Text"),
            ("PRIMARY KEY", "Id"),
        )

        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        
        # Settings
        TableName = "Setting_Table"
        TableData = (
            ("Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Setting_Name", "Varchar(128) DEFAULT NULL"),
            ("Default_String", "Varchar(256) DEFAULT NULL"),
            ("Default_Integer", "Integer DEFAULT NULL"),
            ("Default_Boolean", "Boolean DEFAULT NULL"),
            ("PRIMARY KEY", "Id")
        )

        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        

        # UserSetSetting
        TableName = "User_Setting_Table"
        TableData = (
            ("Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Set_By_User", "Integer DEFAULT NULL"),  # This settings master entry in
            ("Master_Setting_Id", "Integer DEFAULT NULL"),  # This setting has been set by
            ("User_String", "Varchar(256) DEFAULT NULL"),
            ("User_Integer", "Integer DEFAULT NULL"),
            ("User_Boolean", "Boolean DEFAULT NULL"),
            ("FOREIGN KEY", "Master_Setting_Id", "Setting_Table(Id)"),
            ("FOREIGN KEY", "Set_By_User", "User_Table(Internal_Id)"),
            ("PRIMARY KEY", "Id"),
        ) 
        
        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        
        # UserTable
        TableName = "Channel_Table"
        TableData = (
            ("Internal_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("External_Id", "Integer DEFAULT NULL"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("True_Name", "TEXT DEFAULT NULL"),
            ("Description", "TEXT DEFAULT NULL"),
            ("UNIQUE", "External_Id"),  
            ("PRIMARY KEY", "Internal_Id"),
        )

        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        
        # ListOfAnime - Masterlist
        TableName = "Anime_Table"
        TableData = (
            ("Id", "Integer NOT NULL AUTO_INCREMENT"),            
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Anime_Name", "Varchar(256) DEFAULT NULL"),
            ("Airing_Year", "YEAR(4) DEFAULT NULL"),
            ("MyAnimeList_Url", "Varchar(2083)"),
            ("Telegram_Url", "Varchar(2083)"),
            ("Channel_Id", "Integer DEFAULT NULL"),
            ("Image_Name", "Binary(16) DEFAULT NULL"),
            ("PRIMARY KEY", "Id"),
        )

        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        
        
        # ListOfAnime - Masterlist
        TableName = "Episode_Table"
        TableData = (
            ("Id", "Integer NOT NULL AUTO_INCREMENT"),            
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Name", "Varchar(256) DEFAULT NULL"),
            ("Telegram_Url", "Varchar(2083)"),
            ("Channel_Id", "Integer DEFAULT NULL"),
            ("FOREIGN KEY", "Channel_Id", "Anime_Table(Id)"),
            ("PRIMARY KEY", "Id"),
        )

        self.SqlObject.CreateTable(self.Cursor, TableName, TableData, )
        
        # Second all the inserts
        
        # the inserts for the settings 
        Columns = {
            "Setting_Name": "Language",
            "Default_String": "en_US"
        }
        self.SqlObject.InsertEntry(self.Cursor, "Setting_Table", Columns)

        # commit all the changes
        self.SqlObject.Commit()
       
class DistributorApi(object):
    """
    This class is a distributor for the database connection classes.
    """
    def __init__(self,                 
                 User,
                 Password,
                 LanguageObject,
                 LoggingObject,
                 DatabaseName = None,
                 Host="127.0.0.1",
                 Port="3306",
                 ReconnectTimer = 3000,):
        
        self.User = User
        self.Password = Password
        self.DatabaseName = DatabaseName
        self.DatabaseHost = Host
        self.DatabasePort = Port
        self.ReconnectTimer = ReconnectTimer
        
        self.LanguageObject = LanguageObject
        self.LoggingObject = LoggingObject
    
    def New(self):
        """
        This method will return a new database object for the subprocess
        to connect to.
        
        Variables:
            \-
        """
        DatabaseObject = Api(
                 User = self.User,
                 Password = self.Password,
                 LanguageObject = self.LanguageObject,
                 LoggingObject = self.LoggingObject,
                 DatabaseName = self.DatabaseName,
                 Host = self.DatabaseHost,
                 Port = self.DatabasePort,
                 ReconnectTimer = self.ReconnectTimer,
                             )
        return DatabaseObject     
             
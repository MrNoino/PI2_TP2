import mysql.connector
import os, db_env, http_codes

class DBWrapper:

    def __init__(self):
        
        self.__connection = None
        self.__cursor = None

    def connect(self):
        try:
            self.__connection = mysql.connector.connect(host= os.getenv("DB_HOST"),
                                                port= os.getenv("DB_PORT"),
                                                user= os.getenv("DB_USER"),
                                                password= os.getenv("DB_PASSWORD"),
                                                database= os.getenv("DB_NAME"),
                                                charset= 'utf8'
                                            )

            self.__cursor = self.__connection.cursor(dictionary=True)
            
        except mysql.connector.Error as e:

            print(e)

    def close(self):
        if self.__connection:
            self.__connection.close()
            self.__connection = None
            self.__cursor = None

    def query(self, sql, params=None, is_procedure= True, fetch_mode = "all"):

        if self.__connection:

            try:

                data = {} if fetch_mode == 'one' else []

                if(is_procedure):

                    self.__cursor.callproc(sql, params)

                    for result in self.__cursor.stored_results():
                        
                        data = result.fetchone() if fetch_mode == 'one' else result.fetchall()

                else:

                    self.__cursor.execute(sql, params)

                    data = self.__cursor.fetchone() if fetch_mode == 'one' else self.__cursor.fetchall()

                return data if data else []

            except mysql.connector.Error as e:

                print(e)
                return None
            
        else:

            return None

    def manipulate(self, sql, params=None):

        if self.__connection:

            try:

                self.__cursor.callproc(sql, params)
                self.__connection.commit()

                return self.__cursor.rowcount
            
            except mysql.connector.Error as e:

                self.__connection.rollback()
                print(e)
                return False
            
        else:

            return False
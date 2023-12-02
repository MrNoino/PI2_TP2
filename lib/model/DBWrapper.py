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

    def query(self, procedure, params=None, fetch_mode = "all"):

        if self.__connection:

            try:

                self.__cursor.callproc(procedure, params)

                data = []

                for result in self.__cursor.stored_results():
                    
                    if fetch_mode == 'one':
                        data = result.fetchone()

                    else:
                        data = result.fetchall()

                return data

            except mysql.connector.Error as e:

                print(e)
                return None
            
        else:

            return None

    def manipulate(self, procedure, params=None):

        if self.__connection:

            try:

                self.__cursor.callproc(procedure, params)
                self.__connection.commit()

                return self.__cursor.rowcount
            
            except mysql.connector.Error as e:

                self.__connection.rollback()
                print(e)
                return False
            
        else:

            return False
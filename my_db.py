ODBCdriverVerStr = "17"
server_name = 'MAYO23'  # Added server name (adjust as needed)
db_name = 'Ps_RFM'
usrName = 'sa'
passwrd = ''
bol_winSecureAuth = True  # Simplified bool initialization

connDefn = None  # Initialize connection variable

import pyodbc

def GetConnStrFull():
    global server_name, db_name, usrName, passwrd, bol_winSecureAuth, ODBCdriverVerStr

    print("\nTEST: @@GetConnStrFull()")
    print(f" >> server_name = {server_name}")
    print(f" >> db_name = {db_name}")
    print(f" >> bol_winSecureAuth = {bol_winSecureAuth}")
    print(f" >> usrName = {usrName}")
    print(f" >> passwrd = {'******' if passwrd else '(empty)'}")
    print(f" >> ODBCdriverVerStr = {ODBCdriverVerStr}\n")

    ODBCdriverVerStr = str(ODBCdriverVerStr).strip().lower()
    driver = "SQL Server" if ODBCdriverVerStr == "pure" or not ODBCdriverVerStr else f"ODBC Driver {ODBCdriverVerStr} for SQL Server"

    if bol_winSecureAuth:
        conn_str = f"DRIVER={{{driver}}};SERVER={server_name};DATABASE={db_name};Trusted_Connection=yes;"
    else:
        conn_str = f"DRIVER={{{driver}}};SERVER={server_name};DATABASE={db_name};UID={usrName};PWD={passwrd}"
    
    return conn_str

def get_db_connection():
    global connDefn
    if connDefn is None:
        conn_str = GetConnStrFull()
        print(f"Attempting connection with: {conn_str}")  # Debug print
        connDefn = pyodbc.connect(conn_str)
    return connDefn

# Test the connection
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT @@version;")
    row = cursor.fetchone()
    print("Connection successful! SQL Server version:")
    print(row[0])
except Exception as e:
    print(f"Connection failed: {e}")
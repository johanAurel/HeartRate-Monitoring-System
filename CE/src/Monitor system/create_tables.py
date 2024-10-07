import mysql.connector
import questionary
import time

pw = '0000'
# Connect to the database
mydb = mysql.connector.connect(
    user='admin',
    password= pw,  # Make sure to use a strong password if applicable
    host='localhost',  # Change '%' to 'localhost' or the specific host
    database='health_wearables'
)

mycursor = mydb.cursor()

# Corrected SQL statement to create the table
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Devices (
        id INT AUTO_INCREMENT PRIMARY KEY,  # Use INT with AUTO_INCREMENT
        name VARCHAR(255) NOT NULL  # Added NOT NULL for better data integrity
    )
""")

# Execute the SHOW TABLES command
mycursor.execute("SHOW COLUMNS FROM Devices")

# Fetch and print the results
outputs = mycursor.fetchall()
for output in outputs:
    print(output)

time.sleep(3)
permissions = questionary.select('Do you want to keep this password ?', choices=['yes', 'no']).ask()
if permissions == 'yes':
    print("Password saved successfully")
else:
    password = input("Please enter new password")
    mycursor.execute(f"ALTER USER 'admin'@'localhost' IDENTIFIED BY {password};")
    pw = password 


# Close the cursor and connection
mycursor.close()
mydb.close()


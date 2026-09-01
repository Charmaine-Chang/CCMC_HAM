"""Local MySQL connection settings (example template).

Copy this file to CCMC_HAM/connect_local.py and fill in your own values.
connect_local.py is gitignored and will never be committed.

You can also override everything with environment variables:
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
"""

dbuser = "root"
dbpass = "change-me"
dbhost = "127.0.0.1"
dbport = 3306
dbname = "ccmc_ham"
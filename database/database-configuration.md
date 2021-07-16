# Configuring a new database

## Connect to database server:
    Firstly, there are no users or databases.
### Connect with root:
    ```bash
    mysql -h $DATABASE_HOST --user root --password
    ```
### Create new user:
    ```mysql
    CREATE USER username IDENTIFIED BY 'password';
    ```
### Create new database
    ```mysql
    CREATE DATABASE database_name CHARACTER SET="utf8" COLLATE="utf8_general_ci";
    ```
### Grants privileges to the new user (choose one or some):
    ```mysql
    GRANT [INSERT\DELETE\ALTER\INSERT\SELECT\UPDATE\...] ON database_name.* TO username;
    ```
### Reconnect with new user:
    ```bash
    mysql -h $DATABASE_HOST --user username --password database_name
    ```



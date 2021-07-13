# Setup database server

Follow these instuctions for installing database server on your machine or follow instuctions in `docker-inst.md` for installing docker.

*Installation is actual mainly for archlinux, but mostly common to other distros. But it will be completly different for windows*

## Installation
1) Download mariadb (mysql analog, open sorce, some times better performance).

    If you use btrfs filesystem run:
    ```bash
    chattr +C /var/lib/mysql
    ```
2) Configure MariaDB:
    ```bash
    mysql_install_db --user=mysql --basedir=/usr --datadir=/var/lib/mysql 
    ```
    This action will create two accounts: **root@localhost** with root priviliges and **mysql@localhost**.
    More info: https://mariadb.com/kb

    MariaDB can be started after every reboot with this command (single usage):
    ```bash
    systemctl enable --now mariadb
    ```
    The "--now" flag will allow you use mariadb right after running the command.
    You can run `mysql` for checking that installation has been successful.
3) Run `mysql_secure_installation` for completing secure measure.


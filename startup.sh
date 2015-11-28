#!/bin/bash
/etc/init.d/mysql start
#do the import here
#!/bin/bash
MYSQL=`which mysql`

Q1="CREATE DATABASE IF NOT EXISTS gip;"
Q2="GRANT USAGE ON *.* TO root@localhost;"
Q3="GRANT ALL PRIVILEGES ON gip.* TO root@localhost;"
Q4="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}${Q4}"

$MYSQL -uroot  -e "$SQL"

python manage.py syncdb
#some shit breaks here, do it twice... :(
python manage.py syncdb

export DJANGO_SETTINGS_MODULE=gip.settings

python carga_bd.py

# GIP
HowTo:

$ docker build -t gip_image .

$ docker run  --name my_running_gip -i -t gip_image

You can always start it using:

$ docker start my_running_gip

and acces to it with:

$ docker exec -i -t my_running_gip bash

Probably now you want to:

$ /etc/init.d/mysql start

And... remove passwd for mysql

$ sed -i "s/        'PASSWORD': 'root',/        'PASSWORD': '',/g" gip/settings.py
$ mysql -uroot --execute='create database gip;'
$ python manage.py syncdb

execute it twice... till is migrated to django 1.8

$ python manage.py syncdb

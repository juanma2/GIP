# GIP
HowTo:
$ docker build -t gip_image .

$ docker run  --name my_running_gip -i -t gip_image

You can always start it using:

$ docker start my_running_gip

and acces to it with:

$ docker exec -i -t my_running_gip bash

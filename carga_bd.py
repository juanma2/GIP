##FROM BASH :  export DJANGO_SETTINGS_MODULE=gip.settings
##FROM BASH :  cd /home/adminuser/GIP/

import django
import random
import datetime
import time
django.setup()

import rlcompleter, readline
readline.parse_and_bind('tab:complete')
from django.db import models
from gip.models import Tarifas
from gip.models import Destinos
from gip.models import Proveedor
from gip.models import Producto
from gip.models import Pedidos
from gip.models import Cliente
from gip.models import Carrito
from gip.models import Categoria
from gip.models import Lista
from gip.models import Elemento

from django.contrib.auth.models import User, Group

grupocliente = Group.objects.create(name='cliente')
grupocliente.save()
grupoproveedor = Group.objects.create(name='proveedor')
grupoproveedor.save()

#I want ot create 20K products, 25 providers and 10K clients.
MAX_DESTINOS = 25
MAX_TARIFAS = 4
MAX_PROVEEDORES = 2
MAX_PRODUCTOS = 7000
MAX_PRODUCTOS = 1000
MAX_PRODUCTOS = 100
MAX_CLIENTES = 2000
MAX_CLIENTES = 200
MAX_CLIENTES = 20
MAX_LISTAS= 5
MAX_CATEGORIAS = 8
MAX_ELEMENTOS = 25
#2.5K codigos postales
print "Current time " + time.strftime("%X")
print "creating destions... "
#for i in range(1,2500):
for i in range(1,MAX_DESTINOS):
  b = Destinos(codigo=i, nombre='CP - '+str(i))
  b.save()
  #time.sleep(0.01)

print "Current time " + time.strftime("%X")
#only 25 providers
print "creating providers... "
for i in range(1,MAX_PROVEEDORES):
  user = User.objects.create_user('PROVEEDOR'+str(i), 'p@p.com', 'password')
  user.groups.add(grupoproveedor)
  user.save()
  c = Proveedor(user=user, nombre='Proveedor'+str(i), descripcion='Descripcion'+str(i))
  c.save()
  #a provider can work in 350 CP
  for k in range(1,MAX_DESTINOS-1):
    c.destinos_reparto.add(random.randint(1,MAX_DESTINOS-1))
  c.save()
  ##and has 5 rates
  #for i in range(1,5):
  #  c.tipos_tarifas.add(random.randint(1,25))
  #c.save()
  
print "Current time " + time.strftime("%X")
  
#to do that, i need Tarifas 125 tarifas and 2.5K CP
print "creating tarifas... "
for i in range(1,MAX_TARIFAS):
  a = Tarifas(nombre='tarifa'+str(i), descripcion='descripcion'+str(i), elproveedor_id=random.randint(1,MAX_PROVEEDORES- 1 ))
  a.save()
  #time.sleep(0.01)

print "Current time " + time.strftime("%X")

print "Creating categorias..."
for i in range(1,MAX_CATEGORIAS):
  cat = Categoria(nombre='categoria'+str(i),short_url='categoria-'+str(i))
  cat.save()

print "Current time " + time.strftime("%X")
print "Creating listas"
for i in range(1,MAX_LISTAS*MAX_CLIENTES):
  #the client_id is uniq, the list is random sample
  lis = Lista(nombre='lista'+str(i))
  lis.save()

#here comes... 25K products
#for i in range(1,25000):
###Should not be needed, we are usinng "real" data
##print "Current time " + time.strftime("%X")
##print "creating provducts... "
##for i in range(1,MAX_PRODUCTOS):
##  p = Proveedor()
##  p.id = random.randint(1,MAX_PROVEEDORES - 1)
##  d = Producto(nombre='Producto'+str(i), descripcion='Descripcion'+str(i), formato='Formato'+str(i), caducidad_precio = datetime.datetime.now() + datetime.timedelta(days=1), proveedor=p,tarifa_id=random.randint(1,MAX_TARIFAS -1 ), categoria_id=random.randint(1,MAX_CATEGORIAS-1 ) )
##  d.save()
##
##print "Current time " + time.strftime("%X")



##here comes... 25K products
##for i in range(1,25000):
#print "Current time " + time.strftime("%X")
#print "creating provducts... "
#print "we are loading from a json"
##0: Nombre
##3: Producto ID
##4: Formato
##5: Descripcion
##7: Imagen
import json
from pprint import pprint

with open('./small_data_set.json') as data_file:
    data = json.load(data_file)

for i in data:
  p = Proveedor()
  p.id = random.randint(1,MAX_PROVEEDORES - 1)
  d = Producto(nombre = data[i][0].encode('utf-8'), descripcion = data[i][5].encode('utf-8'), formato = data[i][4].encode('utf-8'), caducidad_precio = datetime.datetime.now() + datetime.timedelta(days=1), proveedor=p,tarifa_id=random.randint(1,MAX_TARIFAS -1 ), categoria_id=random.randint(1,MAX_CATEGORIAS-1 ),image_url= data[i][7].encode('utf-8'), product_ref=data[i][3].encode('utf-8'), precio = random.randint(1,100) )
  d.save()
#
#print "Current time " + time.strftime("%X")



#and now, the clients, 2K
#for i in range(1,2001):
print "Current time " + time.strftime("%X")
print "creating clients... "
for i in range(1,MAX_CLIENTES):
  user = User.objects.create_user('CLIENTE'+str(i), 'p@p.com', 'password')
  user.groups.add(grupocliente)
  user.save()
  cliente = Cliente(user=user, nombre='Cliente'+str(i), descripcion='Descripcion'+str(i), cif='NIFNIFNIF'+str(i), direccion='calle direccion' ,ciudad='ciudadXX', telefono='telefono 123', contacto_nombre='Contact'+str(i) )
  #a client can has more than one CP
  cliente.save()
  for k in range(1,random.randint(2,5)):
    cliente.tarifa.add(random.randint(1,MAX_TARIFAS-1))
  for k in range(1,random.randint(2,5)):
    cliente.listas.add(random.randint(1,MAX_CATEGORIAS-1))
  for k in range(1,random.randint(2,5)):
    cliente.destino_reparto.add(random.randint(1,MAX_DESTINOS-1))
  cliente.save()

print "Current time " + time.strftime("%X")



print "Current time " + time.strftime("%X")
print "Creating Elementos"
for i in range(1,MAX_LISTAS*MAX_ELEMENTOS*MAX_CLIENTES):
  #the client_id is uniq, the list is random sample
  p = random.randint(1,MAX_PRODUCTOS- 1 )
  #TODO: p can be empty, 
  l = random.randint(1,MAX_LISTAS*MAX_CLIENTES- 1 )
  c = random.randint(1,20)
  ele = Elemento(nombre='elem'+str(i),cantidad= c, producto_id = p, lista_id= l )
  ele.save()


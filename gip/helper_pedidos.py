import datetime

from gip.models import Pedidos
from django.contrib.auth.models import User


def send_order(pedido,proveedor): 
  cliente = pedido['cliente']
  print "***************************************************************"
  print "implement email, or, whatever needed in gip/helper_pedidos.py"
  print cliente 
  orden = pedido['orden']
  print orden
  precio = pedido['precio']
  print precio
  total = 0.0
  u = User.objects.filter(id=pedido['cliente']['user_id'])
  for i in pedido['orden']:
    total += orden[i]*precio[i]
  print total 
  #once that your pedido is ready, you should set all the items as "active"
  p = Pedidos(producto_serializado=pedido, proveedor_id = proveedor.id, total = total , fecha_creacion = datetime.datetime.now())
  p.save()
  print pedido
  p.cliente.add(pedido['cliente']['id'])
  print "***************************************************************"
  return True

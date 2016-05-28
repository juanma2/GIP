import datetime

from gip.models import Pedidos
from django.contrib.auth.models import User


PEDIDOS_ESTADOS = (
    ('400', 'Pendiente Proveedor'),
    ('500', 'Pendiente Cliente'),
    ('600', 'Aceptado'),
    ('700', 'Rechazado'),
    ('800', 'Cancelado'),
    ('900', 'Enviado'),
    ('1000', 'Finalizado'),
)

def send_order(pedido,proveedor): 
  cliente = pedido['cliente']
  print "***************************************************************"
  print "implement email, or, whatever needed in gip/helper_pedidos.py"
  print cliente 
  orden = pedido['orden']
  print orden
  print precio
  precio = pedido['precio']
  total = 0.0
  u = User.objects.filter(id=pedido['cliente']['user_id'])
  for i in pedido['orden']:
    total += orden[i]*precio[i]
  print total 
  p = Pedidos(producto_serializado=pedido, proveedor_id = proveedor.id, total = total , fecha_creacion = datetime.datetime.now())
  p.save()
  print pedido
  p.cliente.add(pedido['cliente']['id'])
  print "***************************************************************"
  return True
#    codigo = models.IntegerField(default=0) # db_index
#    producto_serializado = models.CharField(max_length=5000) # es el producto en ese momento del tiempo, es unico pedazo de dict o.. json. 
#    total = models.DecimalField(max_digits=6, decimal_places=4)
#    PEDIDOS_ESTADOS = (
#        ('400', 'Pendiente Proveedor'),
#        ('500', 'Pendiente Cliente'),
#        ('600', 'Aceptado'),
#        ('700', 'Rechazado'),
#        ('800', 'Cancelado'),
#        ('900', 'Enviado'),
#        ('1000', 'Finalizado'),
#    )
#    estados = models.CharField(max_length=1, choices=PEDIDOS_ESTADOS)
#    def __unicode__(self):
#        return u"%s" % (self.codigo)


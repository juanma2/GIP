import datetime

from django.db import models
from django.contrib.auth.models import Group, User
from django.utils.timezone import now
from django_fsm import FSMField, transition


#I wish to place it out of here, but... is not working in helpers :(
def number_invoice():
  no = Pedidos.objects.count()
  if no == None:
    num = 1
  else:
    num = no + 1
  invoice_num = "{0:0>6}".format(num)
  REF = 'REF'
  YEAR = str(datetime.date.today().year)
  MONTH = str(datetime.date.today().month)
  return REF+YEAR+MONTH+invoice_num


#http://stackoverflow.com/questions/9492190/django-categories-sub-categories-and-sub-sub-categories
class Categoria(models.Model):
    nombre = models.CharField(max_length=200)
    short_url = models.SlugField()
    padre = models.ForeignKey('self', blank = True, null = True, related_name="hijo")
    def __unicode__(self):
        if self.padre:
          msg = "%s -> %s " %(self.nombre, self.padre)
        else:
          msg =  "%s " % (self.nombre)
        return msg

class Destinos(models.Model):
    codigo = models.IntegerField(default=0)# db_index
    nombre = models.CharField(max_length=200)
    def __unicode__(self):
        return "%s %s" % (self.nombre, self.codigo)

class Proveedor(models.Model):
    user = models.OneToOneField(User)
    nombre = models.CharField(max_length=200)
    cif = models.CharField(max_length=200)# db_index
    descripcion = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=200)
    destinos_reparto = models.ManyToManyField(Destinos) # should test if is better create classes like Proveedor destinos and do a 1to1 
    telefono = models.CharField(max_length=200)
    email = models.CharField(max_length=200,blank=True)
    web = models.CharField(max_length=200,blank=True)
    contacto_nombre = models.CharField(max_length=200)
    contacto_dni = models.CharField(max_length=200,blank=True)
    contacto_direccion = models.CharField(max_length=200,blank=True)
    contacto_ciudad = models.CharField(max_length=200,blank=True)
    ##NOP contacto_CP = models.ManyToManyField(Destinos,blank=True)
    contacto_telefono = models.CharField(max_length=200,blank=True)
    contacto_email = models.CharField(max_length=200,blank=True)    

#    tipos_tarifas = models.ManyToManyField(Tarifas) # Maybe create Tarifas per provider... or any other solution
    def __unicode__(self):
        return "%s" % (self.nombre)

class Tarifas(models.Model):
    nombre = models.CharField(max_length=200) 
    descripcion = models.CharField(max_length=200)
    porciento = models.IntegerField(default=0)
    elproveedor = models.ForeignKey(Group)
    def __unicode__(self):
        return "%s - %s" % (self.nombre,self.elproveedor)

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    product_ref = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200)
    cantidad_minima = models.IntegerField(default=0)
    formato = models.CharField(max_length=200)
    caducidad_precio = models.DateTimeField(default = datetime.datetime.now() + datetime.timedelta(days=1) )#by default +24 hours
    #so.. proveedor, is a group :(, otherwise, I do not know as proveedor user which products belongs to me.
    proveedor = models.ForeignKey(Group)
    ###ESTA ES LA SOLUCION #la tarifa es unica, no many, anades un precio, y creas 4 PRODUCTOS
    ###CADA CLIENTE TIENE UNA TARIFA POR PROVEEDOR
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    tarifa = models.ForeignKey(Tarifas)
    categoria = models.ForeignKey(Categoria)
    image_url = models.CharField(max_length=300)
    especificaciones = models.CharField(max_length=2000,default="need to add WYSIWYG")
    fecha_creacion = models.DateTimeField(default = now)
    fecha_actualizacion = models.DateTimeField(default = now, null=True, blank=True )
    #add something like disable.
    baja = models.BooleanField(default=False)
    def ha_caducado(self):
        #TODO: check and debug, timezone is not defined!!
        return self.caducidad_precio <= timezone.now() - datetime.timedelta(days=1)

    def __unicode__(self):
        return u"%s" % (self.nombre)


class Promo(models.Model):
    nombre = models.CharField(max_length=200)
    tarifa = models.ForeignKey(Tarifas)
    producto = models.ForeignKey(Producto, blank = True, null = True)
    #may have counter, or... check remaining or.. something like that
    #WARNING, the product in promo can be browsed ? or a "special produtc"? Now, is a normal Produc, forrMVP is enough
    #disable  field
    #caducidad field
    #html_description field
    #orden Integer
    #noticia = coll =12 I don't like the idea of mixing news and offers here.
    #ofertas = coll =4
    def __unicode__(self):
        return u"%s" % (self.nombre)

class Lista(models.Model):
    nombre = models.CharField(max_length=200)
    def __unicode__(self):
        return u"%s " % (self.nombre)

class Cliente(models.Model):
    user = models.OneToOneField(User)
    nombre = models.CharField(max_length=200)
    cif = models.CharField(max_length=200)# db_index
    descripcion = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=200)
    telefono = models.CharField(max_length=200)
    email = models.CharField(max_length=200,blank=True)
    web = models.CharField(max_length=200,blank=True)
    iae = models.CharField(max_length=200,blank=True)
    destino_reparto = models.ManyToManyField(Destinos) # This is many to many, not  only one
    #pedidos = models.ManyToManyField(Pedidos,blank=True) # This is many to many, not  only one
    tarifa = models.ManyToManyField(Tarifas) # a client has many rates to be applied, one per provider
    listas = models.ManyToManyField(Lista,blank=True) # if is not empty, need to create one, with the user creation TODO 
    contacto_nombre = models.CharField(max_length=200)
    contacto_dni = models.CharField(max_length=200,blank=True)
    contacto_direccion = models.CharField(max_length=200,blank=True)
    contacto_ciudad = models.CharField(max_length=200,blank=True)
    ##NOP contacto_CP = models.ManyToManyField(Destinos,blank=True)
    contacto_telefono = models.CharField(max_length=200,blank=True)
    contacto_email = models.CharField(max_length=200,blank=True)
    baja = models.NullBooleanField(null=True,default=False)
    #precomputed favorites
    def __unicode__(self):
        return u"%s" % (self.nombre)


class Pedidos(models.Model):
    class STATE:
        NUEVO                         =   100
        RECEPCION                     = 10000
        RECHAZADO                     = 11000
        REFORMULAR_PEDIDO             = 12100
        NO_ACEPTADO                   = 12200
        ACEPTADO_CLIENTE              = 12300
        CURSAR_PEDIDO                 = 20000
        EN_PREPARACION                = 30000
        EN_CAMINO                     = 40000
        ENTREGADO                     = 50000
        COBRADO                       = 60000
        HISTORICO                     = 90000
        CANCELADO		      =    -1
    STATE_CHOICES = (
                     (STATE.NUEVO                          ,'Nuevo'),
                     (STATE.RECEPCION                      ,'Recepcion'),
                     (STATE.RECHAZADO                      ,'Rechazado'),
                     (STATE.REFORMULAR_PEDIDO              ,'Reformular Pedido'),
                     (STATE.NO_ACEPTADO                    ,'No Aceptado Cliente'),
                     (STATE.ACEPTADO_CLIENTE               ,'Aceptado Cliente'),
                     (STATE.CURSAR_PEDIDO                  ,'Cursar Pedido'),
                     (STATE.EN_PREPARACION                 ,'En preparacion'),
                     (STATE.EN_CAMINO                      ,'En camino'),
                     (STATE.ENTREGADO                      ,'Entregado'),
                     (STATE.COBRADO                        ,'Cobrado'),
                     (STATE.HISTORICO                      ,'Historico'),
                     (STATE.CANCELADO                      ,'Cancelado'),

    )

    id = models.AutoField(primary_key=True)
    pedidostate = FSMField(
      default=STATE.NUEVO,
      verbose_name='Estado Pedido',
      choices=STATE_CHOICES,
      #protected=True,
      )
    codigo = models.CharField(max_length=16, default=number_invoice) #TODO: multithread issue requesting invoices numbers... wait for it
    producto_serializado = models.CharField(max_length=5000) # es el producto en ese momento del tiempo, es unico pedazo de dict o.. json. 
    total = models.DecimalField(max_digits=25, decimal_places=4)
    #You, My friend, were stupid enough to relay a pedido in a User, instead of a cliente, fix: views_cliente.py:459 , this model...
    cliente = models.ManyToManyField(Cliente)
    fecha_creacion = models.DateTimeField('fecha creacion')
    proveedor = models.ForeignKey(Group)

    #django-fsm transitions... here comes the fun
    #this one, should be State.NUEVO... but it does not work, so I used "*" .... TODO:Fix it!!
    @transition(field=pedidostate, source=STATE.NUEVO, target=STATE.RECEPCION)
    #@transition(field=pedidostate, source="*", target=STATE.RECEPCION)
    def getting(self):
      """
      Order requested, the user click in "pedir"
      Llega a la pestan sin validar, puedes validar, ver o rechazar.
      """
      
      return True

    @transition(field=pedidostate, source=STATE.RECEPCION, target=STATE.RECHAZADO)
    def rejecting(self):
      """
      """
      return True

    @transition(field=pedidostate, source=STATE.RECEPCION, target=STATE.CURSAR_PEDIDO)
    def checking(self):
      """
      """
      return True

    @transition(field=pedidostate, source=STATE.RECEPCION, target=STATE.REFORMULAR_PEDIDO)
    def reorder(self):
      """
      """
      return True

    @transition(field=pedidostate, source=STATE.REFORMULAR_PEDIDO, target=STATE.ACEPTADO_CLIENTE)
    def re_acept(self):
      """
      """
      return True

    @transition(field=pedidostate, source=STATE.ACEPTADO_CLIENTE, target=STATE.REFORMULAR_PEDIDO)
    def re_re_order(self):
      """
      """
      return True


    @transition(field=pedidostate, source=STATE.ACEPTADO_CLIENTE, target=STATE.CURSAR_PEDIDO)
    def re_checking(self):
      """
      """
      return True


    @transition(field=pedidostate, source=STATE.NO_ACEPTADO, target=STATE.REFORMULAR_PEDIDO)
    def re_reorder(self):
      """
      """
      return True

    @transition(field=pedidostate, source=STATE.NO_ACEPTADO, target=STATE.CANCELADO)
    def re_rejecting(self):
      """
      """
      return True

#    @transition(field=pedidostate, source=STATE.RECHAZADO, target=STATE.CANCELADO)
#    def notify_rejecting(self):
#      """
#      Order notify the cliente that order were rejected, and there is nothing else to do
#      """
#      return True




##########HAPPY PATH STARTS HERE in CURSAR_PEDIDO

    @transition(field=pedidostate, source=STATE.CURSAR_PEDIDO, target=STATE.EN_PREPARACION)
    def preparing(self):
      """
      Order in process in the proveedor side
      """
      return True

    @transition(field=pedidostate, source=STATE.EN_PREPARACION, target=STATE.EN_CAMINO)
    def sending(self):
      """
      Order OMW!!
      """
      return True

    @transition(field=pedidostate, source=STATE.EN_CAMINO, target=STATE.ENTREGADO)
    def delivering(self):
      """
      Order delivered
      """
      return True

    @transition(field=pedidostate, source=STATE.ENTREGADO, target=STATE.COBRADO)
    def cashing(self):
      """
      Order payed
      """
      return True

    @transition(field=pedidostate, source=STATE.COBRADO, target=STATE.HISTORICO)
    def historify(self):
      """
      Order archived
      """
      return True

    def __unicode__(self):
        return u"%s" % (self.codigo)

class Elemento(models.Model):
    nombre = models.CharField(max_length=200)
    cantidad = models.IntegerField(default=0)
    producto = models.ForeignKey(Producto, null = True, blank = True )
    lista = models.ForeignKey(Lista)
    order = models.IntegerField(default=0, null = True, blank = True ) #default order
    stock_optimo = models.IntegerField(default=0, null = True, blank = True ) 
    existencias = models.IntegerField(default=0, null = True, blank = True ) 
    def __unicode__(self):
        return u"%s" % (self.nombre)

class Carrito(models.Model):
    codigo = models.IntegerField(default=0) # db_index
    caducidad = models.DateTimeField('date published') #no reason to keep an order more than 24 hours
    #You must check the caducidad of each prodcut :(
    producto_serializado = models.CharField(max_length=2000) # es el producto en ese momento del tiempo, es unico. 
    #could be interesting apply discounts per ammount
    def __unicode__(self):
        return u"%s" % (self.nombre)

class PedidosProveedorView(models.Model):
    #this one should have a copy of the order done by the client that should be confirmed, modifed or rejected( with reasons)
    pass

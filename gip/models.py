import datetime

from django.db import models

####
#http://stackoverflow.com/questions/9492190/django-categories-sub-categories-and-sub-sub-categories
class Categoria(models.Model):
    nombre = models.CharField(max_length=200)
    short_url = models.SlugField()
    padre = models.ForeignKey('self', blank = True, null = True, related_name="hijo")
    def __str__(self):
        if self.padre:
          msg = "%s -> %s " %(self.nombre, self.padre)
        else:
          msg =  "%s " % (self.nombre)
        return msg

class Destinos(models.Model):
    codigo = models.IntegerField(default=0)# db_index
    nombre = models.CharField(max_length=200)
    def __str__(self):
        return "%s %s" % (self.nombre, self.codigo)

class Proveedor(models.Model):
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
    def __str__(self):
        return "%s" % (self.nombre)

class Tarifas(models.Model):
    nombre = models.CharField(max_length=200) 
    descripcion = models.CharField(max_length=200)
    porciento = models.IntegerField(default=0)
    elproveedor = models.ForeignKey(Proveedor)
    def __str__(self):
        return "%s - %s" % (self.nombre,self.elproveedor)


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200)
    cantidad_minima = models.IntegerField(default=0)
    formato = models.CharField(max_length=200)
    caducidad_precio = models.DateTimeField(default = datetime.datetime.now() + datetime.timedelta(days=1) )#by default +24 hours
    proveedor = models.ForeignKey(Proveedor)
    ###ESTA ES LA SOLUCION #la tarifa es unica, no many, anades un precio, y creas 4 PRODUCTOS
    ###CADA CLIENTE TIENE UNA TARIFA POR PROVEEDOR
    precio = models.IntegerField(default=0)
    tarifa = models.ForeignKey(Tarifas)
    categoria = models.ForeignKey(Categoria)
    especificaciones = models.CharField(max_length=2000,default="need to add WYSIWYG")
    def ha_caducado(self):
        return self.caducidad <= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return "%s" % (self.nombre)

class Pedidos(models.Model):
    codigo = models.IntegerField(default=0) # db_index
    producto_serializado = models.CharField(max_length=2000) # es el producto en ese momento del tiempo, es unico pedazo de dict o.. json. 
    def __str__(self):
        return "%s" % (self.codigo)


class Cliente(models.Model):
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
    pedidos = models.ManyToManyField(Pedidos,blank=True) # This is many to many, not  only one
    tarifa = models.ManyToManyField(Tarifas) # a client has many rates to be applied, one per provider
    contacto_nombre = models.CharField(max_length=200)
    contacto_dni = models.CharField(max_length=200,blank=True)
    contacto_direccion = models.CharField(max_length=200,blank=True)
    contacto_ciudad = models.CharField(max_length=200,blank=True)
    ##NOP contacto_CP = models.ManyToManyField(Destinos,blank=True)
    contacto_telefono = models.CharField(max_length=200,blank=True)
    contacto_email = models.CharField(max_length=200,blank=True)    

    #precomputed favorites
    def __str__(self):
        return "%s" % (self.nombre)


class Carrito(models.Model):
    codigo = models.IntegerField(default=0) # db_index
    caducidad = models.DateTimeField('date published') #no reason to keep an order more than 24 hours
    #You must check the caducidad of each prodcut :(
    producto_serializado = models.CharField(max_length=2000) # es el producto en ese momento del tiempo, es unico. 
    #could be interesting apply discounts per ammount
    def __str__(self):
        return "%s" % (self.nombre)

class PedidosProveedorView(models.Model):
    #this one should have a copy of the order done by the client that should be confirmed, modifed or rejected( with reasons)
    pass

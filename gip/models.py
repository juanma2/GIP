from django.db import models

class Tarifas(models.Model):
    nombre = models.CharField(max_length=200) 
    descripcion = models.CharField(max_length=200)
    porciento = models.IntegerField(default=0)

    def __str__(self):
        return "%s" % (self.nombre)

class Destinos(models.Model):
    codigo = models.IntegerField(default=0)# db_index
    nombre = models.CharField(max_length=200)
    def __str__(self):
        return "%s %s" % (self.nombre, self.codigo)


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200)
    destinos = models.ManyToManyField(Destinos) # should test if is better create classes like Proveedor destinos and do a 1to1 
    tipos_tarifas = models.ManyToManyField(Tarifas) # Maybe create Tarifas per provider... or any other solution
    def __str__(self):
        return "%s" % (self.nombre)


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200)
    formato = models.CharField(max_length=200)
    cantidad_minima = models.IntegerField(default=0)
    caducidad = models.DateTimeField('date published') #by default +24 hours
    proveedor = models.ForeignKey(Proveedor)
    tipos_tarifas = models.ManyToManyField(Tarifas) #a product can has different rates, so , all of them should be here
    precio = models.IntegerField(default=0)
    #precio = valor * tarifa aplicables ... pre-calculated object and check before show it is awesome!
    def precio(self,cliente_id):
        #tarifa = cliente_id.tarifa.value() 
        #return precio * tarifa  
        pass
    def ha_caducado(self):
        #return self.caducidad <= timezone.now() - datetime.timedelta(days=1)
        pass

    def __str__(self):
        return "%s" % (self.nombre)

class Pedidos(models.Model):
    codigo = models.IntegerField(default=0) # db_index
    producto_serializado = models.CharField(max_length=2000) # es el producto en ese momento del tiempo, es unico pedazo de dict o.. json. 
    def __str__(self):
        return "%s" % (self.codigo)


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    NIF = models.CharField(max_length=200)# db_index
    descripcion = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    destino_reparto = models.ManyToManyField(Destinos) # This is many to many, not  only one
    pedidos = models.ManyToManyField(Pedidos,blank=True) # This is many to many, not  only one
    tarifa = models.ForeignKey(Tarifas) # a client has only one rate to be applied, by one provider BBOOM!!!
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


from django.contrib import admin

from .models import Tarifas
from .models import Destinos
from .models import Proveedor
from .models import Producto
from .models import Pedidos
from .models import Cliente
from .models import Carrito

admin.site.register(Tarifas)
admin.site.register(Destinos)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Pedidos)
admin.site.register(Cliente)
admin.site.register(Carrito)


from django.contrib import admin

from .models import Tarifas
from .models import Destinos
from .models import Proveedor
from .models import Producto
from .models import Pedidos
from .models import Cliente
from .models import Carrito
from .models import Categoria
from .models import Lista
from .models import Elemento
from .models import Promo
from .models import HistoricoListas

admin.site.register(Tarifas)
admin.site.register(Destinos)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Pedidos)
admin.site.register(Cliente)
admin.site.register(Carrito)
admin.site.register(Categoria)
admin.site.register(Lista)
admin.site.register(Elemento)
admin.site.register(Promo)
admin.site.register(HistoricoListas)


from django.contrib.auth.models import User, Group

def is_cliente(user):
    return user.groups.filter(name='cliente').exists()

def is_proveedor(user):
    return user.groups.filter(name='proveedor').exists()



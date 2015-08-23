from django.contrib.auth.models import User, Group

#todo check if is_active, is not done by login_:Requiered, I guess :S
def is_cliente(user):
    return user.groups.filter(name='cliente').exists()

def is_proveedor(user):
    return user.groups.filter(name='proveedor').exists()



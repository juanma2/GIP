from django.shortcuts import render

#import only the needed ones

from gip.models import *
from gip.views_cliente import *


def index(request):
    my_test_string = 'Oh! Yeah!'
    context = {'my_test_string': my_test_string}
    return render(request, 'index.html', context)

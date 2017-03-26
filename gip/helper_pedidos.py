import datetime

import ast 

from gip.models import Pedidos, HistoricoListas
from django.contrib.auth.models import User


def send_order(pedido,proveedor,c_pedido): 
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
  p.cliente.add(pedido['cliente']['id'])
  print "let's try"
  try:
    print p.id 
    history = HistoricoListas(pedido_id = p, listas_serializado = c_pedido) 
    history.save()
    history.id
    print "history saved!!"
  except:
    print "something went wrong with order "+pedido.id+" trying to save listas... but we arae not gonna block them"
  print "***************************************************************"
  return True


def generate_modales_historico(pedidos):
  modales = ''
  for pedido in pedidos:
    if int(pedido.pedidostate) in [12100]:
      header = """
          <div class="modal" onclick="" id="modaldemostrarpedido_{0}">
              <div class="modal-dialog modal-lg" id="customer-order">
                  <div class="modal-content">
                      <div class="modal-header modal-header-info">
                          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">X</button>
                          <h4 class="modal-title">ID.Pedido: {1}</h4>
                      </div>
                      <div class="modal-body">
                        <table class="table">
                                      <thead> 
                                          <tr>
                                              <th>Referencia</th>
                                              <th colspan="2">Nombre del producto</th>


                                              <th>Precio/ud</th>
                                              <th>Total</th>

                                          </tr>
                                      </thead>
                                      <tbody>
      """.format(pedido.codigo,pedido.codigo)
      products = ast.literal_eval(pedido.producto_serializado)
      body = ''
      for i in products['orden']:
        body += """
                                          <tr>
                                              <td>{0}</td>
                                              <td>
                                                  <!-- <a href="s#fichamodal" data-toggle="modal">
                                                      <img src="img/.jpg" alt="">
                                                  </a> -->
                                              </td>
                                              <td><a href="s#fichamodal" data-toggle="modal">{1}</a></td>
                                              <td>{2}</td>
                                              <td>{3}</td>
                                          </tr>
          """.format(i,products['descripcion'][i].encode("utf-8"),products['orden'][i], products['orden'][i] * products['precio'][i])
      foot = """
                                      <tfoot>

                                          <tr>
                                              <th colspan="4" class="text-right">Total</th>
                                              <th>{0}</th>
                                              <th></th>
                                          </tr>
                                      </tfoot>
                                  </table>
                      </div>
                      <div class="modal-footer">
                          <button type="reset" class="btn btn-default" data-dismiss="modal">Cerrar</button>
                      </div>
                  </div>
              </div>
        <!--acaba modal muestra pedido tipo 1-->
      </div>""".format(pedido.total)
      modales += header+body+foot
  return modales

    

    

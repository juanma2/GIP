def list_grouper(query_pedidos):
  #TODO: add this tab definition to a Model or to settings
  def_tabs = {
    0:'Sin Validar',
    1:'En Proceso',
    2:'fuera de la empresa',
    3:'Historico',
  }
  #TODO: add this transitions to a Model or to settings 
  grouped_by = {
    'Sin Validar':[100,10000,11000,11100,11200,12000,12100,12200,12300,12110],
    'En Proceso':[20000,30000,40000],
    'fuera de la empresa':[50000,60000],
    'Historico':[90000,-1]
  }
  ##this is the generated transitions tabs shortcut list
  working_scheme = {}
  for i in def_tabs:
    for k in grouped_by[def_tabs[i]]:
      working_scheme[str(k)] = i

  #bufff... if you have to modify this... you are allowed to do it from scratch
  sorted_pedidos = {}
  for t in grouped_by:
     #this is shit, cause dict.keys() do not work as expected with default dict
     sorted_pedidos[t] = []
  for t in query_pedidos:
    #sorted_pedidos[def_tabs[working_scheme[t['pedido_state']]]] = counted_tabs.get(def_tabs[working_scheme[t['pedido_state']]],0) + 1
    #TODO; if there is something unexpeted, like pediido_state = 101, will crash, FYI
    sorted_pedidos[def_tabs[working_scheme[t.pedido_state]]].append(t)
  #this is "slow", but.. will automate the way the tabs are counted and provided :)
  return sorted_pedidos, def_tabs



def generator_pedidos_tabs(pedidos_list):
  genetared_html =''
  genetared_html += """
                <table class="table">
                  <thead>
                    <tr>
                      <th>Check</th>
                      <th>ID. Pedido</th>
                      <th>Fecha Pedido</th>
                      <th>Cliente</th>
                      <th>Destino</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>"""
  for pedido in pedidos_list:
    clientes = ''
    direccion_reparto = ''
    for current_cliente in pedido.cliente.all():
      clientes += str(current_cliente.nombre)+" "
      #TODO: fix when you have a clear idea where to deliver
      direccion_reparto += str(current_cliente.direccion)+", "+str(current_cliente.ciudad)
    genetared_html += ' \
                     <tr> \
                       <td><label><input type="checkbox"></label></td> \
                       <td>{0}</td> \
                       <td>{1}</td> \
                       <td>{2}</td> \
                       <td>{3}</td> \
                       <td> - </td> \
  '.format(pedido.codigo, pedido.fecha_creacion, clientes,direccion_reparto)
  genetared_html += '    </tbody> \
               </table> \
               <button type="button" class="btn btn-success">Validar seleccionados</button> \
       </div> \
     </div> \
       </div>  \
'
  return genetared_html


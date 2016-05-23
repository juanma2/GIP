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
  for num, i in enumerate(grouped_by):
    for k in grouped_by[i]:
      working_scheme[str(k)] = num

  #bufff... if you have to modify this... you are allowed to do it from scratch
  sorted_pedidos = {}
  for t in grouped_by:
     #this is shit, cause dict.keys() do not work as expected with default dict
     sorted_pedidos[t] = []
  for t in query_pedidos:
    #sorted_pedidos[def_tabs[working_scheme[t['pedido_state']]]] = counted_tabs.get(def_tabs[working_scheme[t['pedido_state']]],0) + 1
    sorted_pedidos[def_tabs[working_scheme[t.pedido_state]]].append(t)
  #this is "slow", but.. will automate the way the tabs are counted and provided :)
  return sorted_pedidos, def_tabs


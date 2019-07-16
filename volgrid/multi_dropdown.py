'''
Created on Jul 12, 2019

@author: bperlman1
'''
# Add the folder that contains this module, and it's parent folder to sys.path
#   so that you can import the dgrid module
import sys,os
if  not os.path.abspath('./') in sys.path:
    sys.path.append(os.path.abspath('./'))
if  not os.path.abspath('../') in sys.path:
    sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('../../dashgrid'))
sys.path.append(os.path.abspath('../../dashgrid/dashgrid'))
from dashgrid import dgrid
import numpy as np
import dash

def _symbol_list_to_dropdown_dict(symbol_list):
    dict_choices = {}
    for symbol in symbol_list:
        commod = symbol[0:-3]
        month = symbol[-3]
        if commod not in dict_choices:
            dict_choices[commod] = [month]
        else:
            if month not in dict_choices[commod]:
                dict_choices[commod].extend(month)
    return dict_choices

        



        
if __name__=='__main__':
    years = ['%02d' %(x) for x in np.arange(11,20)]
    es_list = ['ES'+m+y for m in 'HMVZ' for y in years]
    cl_list = ['CL'+m+y for m in 'FGHJKMNQUVXZ' for y in years]
    cb_list = ['CB'+m+y for m in 'FGHJKMNQUVXZ' for y in years]
    symbol_list = es_list + cl_list + cb_list
#     commod_mon_dd = CommodityMonthDropdown('test_multi_dd',commod_list)
    commod_dict = _symbol_list_to_dropdown_dict(symbol_list)
    commod_list = list(commod_dict.keys())
    commod_dd = dgrid.DropDown('test_multi_dd',commod_list,commod_list)
    initial_month_list = list(commod_dict[commod_list[0]])

    def get_months(value_list):
        l  = commod_dict[value_list[0]]
        print(l)
        return l
    
    month_dd = dgrid.DropDown('month_dd',initial_month_list,initial_month_list,
                    input_component=commod_dd,input_transformer=get_months)
    app = dash.Dash()
    app.layout = dgrid.html.Div([commod_dd.html,month_dd.html])
    
    callback_components = [commod_dd,month_dd]
    [c.callback(app) for c in callback_components]
        
    host = '127.0.0.1'
    port = 8700    
    app.run_server(host=host,port=port)
            
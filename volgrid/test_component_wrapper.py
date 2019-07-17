import dash
import sys,os
from dashgrid.dgrid import ComponentWrapper
if  not os.path.abspath('./') in sys.path:
    sys.path.append(os.path.abspath('./'))
if  not os.path.abspath('../') in sys.path:
    sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('../../dashgrid'))
sys.path.append(os.path.abspath('../../dashgrid/dashgrid'))
# print(sys.path)
from dashgrid import dgrid
import dash_html_components as html


dash_list = dgrid.component_example_dataframe_graph().component_list
clist = [dgrid.ComponentWrapper.build_from_json(cj) for cj in dash_list]

app = dash.Dash()

app.layout = html.Div([c.html for c in clist])
[c.callback(app) for c in clist if len(c.callback_inputs)>0]
app.run_server(host='127.0.0.1',port=8600)


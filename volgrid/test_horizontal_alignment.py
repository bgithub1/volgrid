import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State


grid_style = {'display': 'grid',
  'grid-template-columns': '79.9% 10% 10%',
  'grid-gap': '1px',
  'border': '1px solid #000'
}
s  = style={'border':'1px solid #000','text-align':'center','verticalAlign':'middle',
            'height':'70px'}
s1 = s.copy()
s1['font-size']  = '28px'
s1['font-weight'] = 'bold'


c1 = html.H1(['hello'],style={'height':'1px'},id='c1')

op = [
    {'label':'choice1','value':'apples'},
    {'label':'choice2','value':'oranges'}
    ]

op2 = {
        'apples':[{'label':'mac','value':'mac'},
               {'label':'cort','value':'cort'},
               {'label':'pink','value':'pink'}
               ],
        'oranges':[{'label':'naval','value':'naval'},
               {'label':'juice','value':'juice'},
               ]
    }            
    


c2 = dcc.Dropdown(id='c2',value='apples',style=s,placeholder='make a choice')
c3 = dcc.Dropdown(id='c3',style=s,placeholder='choose month')

s0 = dcc.Store(id='s0')
s1 = dcc.Store(id='s1',data=op)

app = dash.Dash()
app.layout = html.Div([html.Div([c1,c2,c3],style=grid_style),s0,s1])

@app.callback(
    [Output(c2.id,'options'),Output(s0.id,'data')], 
    [Input(s1.id,'data')] 
    )
def execute_callback1(value):
    return value,value

@app.callback(
    [Output(c3.id,'options'),Output(c3.id,'value')], 
    [Input(c2.id,'value')] 
    )
def execute_callback2(value):
    ops = op2[value]
    return ops,value

app.run_server(host='127.0.0.1',port=8500)



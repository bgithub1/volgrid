import dash

import dash_core_components as dcc
import dash_html_components as html


grid_style = {'display': 'grid',
  'grid-template-columns': '79.9% 19.9%',
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

c2 = dcc.Dropdown(id='c2',options=op, value='choice1',style=s,placeholder='make a choice')

app = dash.Dash()
app.layout = html.Div([c1,c2],style=grid_style)
app.run_server(host='127.0.0.1',port=8500)
# Add the folder that contains this module, and it's parent folder to sys.path
#   so that you can import the dgrid module
import sys,os
if  not os.path.abspath('./') in sys.path:
    sys.path.append(os.path.abspath('./'))
if  not os.path.abspath('../') in sys.path:
    sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('../../dashgrid'))
sys.path.append(os.path.abspath('../../dashgrid/dashgrid'))
# print(sys.path)
from dashgrid import dgrid
import dash_core_components as dcc

from volgrid import create_voltables

#  do rest of imports
import dash
import dash_html_components as html
import pandas as pd
import numpy as np
import pandas_datareader.data as pdr
import datetime
import argparse as ap

DEFAULT_IV_FILE_PATH = './df_iv_final.csv'

# Create css styles for some parts of the display
STYLE_TITLE={
    'line-height': '20px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '1px',
    'textAlign': 'center',
    'background-color':'#21618C',
    'color':'#FFFFF9',
    'vertical-align':'middle',
} 


STYLE_UPGRID = STYLE_TITLE.copy()
STYLE_UPGRID['background-color'] = '#EAEDED'
STYLE_UPGRID['line-height'] = '10px'
STYLE_UPGRID['color'] = '#21618C'
STYLE_UPGRID['height'] = '50px'


def get_main_grid(commod_code,year_2_digits,df_iv_csv_path):
    SYMBOL_TO_RESEARCH = commod_code
    yy = '%02d' %(int(str(year_2_digits)))
    vt = create_voltables.VolTable(df_iv_csv_path)
    all_contracts = sorted(vt.df_iv.symbol.unique())
    clist = [c for c in all_contracts if (c[:2]==f'{SYMBOL_TO_RESEARCH}') & (c[-2:]==yy)]
    grid_list = []
    for c in clist:
        dft = vt.df_iv[vt.df_iv.symbol==c]        
        if len(dft)<=0:
            print(f'no data for symbol {c}')
            continue
        fig_list = vt.graph_skew(c)
        # create a reactive grid graph
        for fig in fig_list:
            gr = dgrid.GridGraph(fig.layout.title, fig.layout.title ,None,figure=fig,
                    df_x_column='moneyness')
            grid_list.append(gr)    

    # combine the table and the graph into the main grid
    main_grid =  dgrid.create_grid(grid_list,num_columns=2)
    return main_grid

    
def execute(args):
    # create the app layout         
    host = args.host
    port = args.port

#     loc_div = dcc.Location(id='url', refresh=False)
    title_div = html.Div([html.H3('Commodity Options Historical Skew Analysis (by day/strike)')],style=STYLE_TITLE)
    m = html.H3("From the dropdown buttons to the right, select a Commodity and/or a Year",style={'height':'1px'})
    info_div = dgrid.GridItem(m,html_id='explain')

    def _transform_commod_selection(data):
        print(data)
        return data
    select_commod_div  = dgrid.DropDownDiv('commod_dropdown', 
                            ['E-Mini SP','Nymex Crude','Ice Brent'], 
                             ['ES','CL','CB'],style=STYLE_UPGRID,
                            transformer_method=_transform_commod_selection
                             )

    years = ['%02d' %(y) for y in np.arange(11,20)]
    full_years = ['20'+y for y in years]
    last_year_index = len(years)-1
    select_year_div =  dgrid.DropDownDiv('year_dropdown', 
                            full_years,years ,style=STYLE_UPGRID,default_initial_index=last_year_index)

    
    dropdown_grid = dgrid.create_grid([info_div,select_commod_div,select_year_div],num_columns=3,column_width_percents=[70,14.95,14.95])

    def _get_main_grid_from_dropdowns():
        commod_code = select_commod_div.current_value
        if commod_code is None:
            commod_code = 'ES'
        year_2_digits = select_year_div.current_value
        if year_2_digits is None:
            year_2_digits = 19
        print(f'entering _get_main_grid_from_dropdowns commod_code: {commod_code} year {year_2_digits}')
        df_iv_csv_path = DEFAULT_IV_FILE_PATH.replace('.csv',f'_{commod_code}.csv')
        mg = get_main_grid(commod_code, year_2_digits, df_iv_csv_path)
        return mg
        
    content_div = dgrid.ReactiveDiv('page_content',select_commod_div.output_tuple,
                        input_transformer=lambda commod:_get_main_grid_from_dropdowns())
    
    app = dash.Dash()
    main_div = html.Div(children=[title_div,dropdown_grid,content_div.html])
    app.layout = html.Div(children=[main_div])
    
    callback_components = [select_commod_div,select_year_div,content_div]
    [c.callback(app) for c in callback_components]
        

#     @app.callback(dash.dependencies.Output('page-content', 'children'),
#                   [dash.dependencies.Input('url', 'pathname')])
#     def display_page(pathname):
#         commod_code = 'ES' if pathname is None or pathname =='/'  else pathname.upper().replace('/','')
#         main_grid = get_main_grid(commod_code,19,DEFAULT_IV_FILE_PATH.replace('.csv',f'_{commod_code}.csv'))
#         title_div = html.Div([html.H3('Commodity Options Historical Skew Analysis (by day/strike)')],style=STYLE_TITLE)
#         ret_layout = [title_div,main_grid]
#         return ret_layout
    
    # run server    
    app.run_server(host=host,port=port)
     
    
if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('--host',type=str,
                        help='host url to run server.  Default=127.0.0.1',
                        default='127.0.0.1')   
    parser.add_argument('--port',type=str,
                        help='port to run server.  Default=8400',
                        default='8500')   
    parser.add_argument('--df_iv_csv_path',type=str,
                        help='Path to implied volatility csv file.  Default=./df_iv_final.csv',
                        default=DEFAULT_IV_FILE_PATH)   
    parser.add_argument('--commod_code',type=str,
                        help='commodity code to analyze, like CL,CB or ES. Default=ES',
                        default='ES')   
    n = datetime.datetime.now()
    yyyymmdd = n.strftime('%Y%m%d')
    yy = int(str(yyyymmdd)[2:4])
    current_2_char_year = yy
    parser.add_argument('--year_2_digits',type=int,
                        help='2 digit year of the commodity contracts you want to visualize, from 11 to the 2 digit current year. Default=current year',
                        default=yy)  
    
    args = parser.parse_args()
    execute(args)
    
    

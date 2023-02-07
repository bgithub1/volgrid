'''
Created on Feb 10, 2019

@author: bperlman1
'''
# import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import pandas as pd
import numpy as np
import dash_table
import plotly.graph_objs as go
# import argparse as ap
import datetime,base64,io,pytz
import flask
# from flask import redirect,url_for
# from pip._vendor.urllib3.connectionpool import _Default


import logging

def root_logger(logfile,logging_level=None):
    level = logging_level
    if level is None:
        level = logging.DEBUG
    # get root level logger
    logger = logging.getLogger()
    if len(logger.handlers)>0:
        return logger
    logger.setLevel(logging.getLevelName(level))

    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)   
    return logger

DEFAULT_TIMEZONE = 'US/Eastern'

#**************************************************************************************************


grid_style = {'display': 'grid',
              'border': '1px solid #000',
              'grid-gap': '10px 10px',
            'grid-template-columns': '1fr 1fr'}


chart_style = {'margin-right':'auto' ,'margin-left':'auto' ,'height': '98%','width':'98%'}

#**************************************************************************************************

button_style={
    'line-height': '40px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '1px',
    'textAlign': 'center',
    'background-color':'#fffff0',
    'vertical-align':'middle',
}

blue_button_style={
    'line-height': '40px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '1px',
    'textAlign': 'center',
    'background-color':'#A9D0F5',
    'vertical-align':'middle',
}


select_file_style={
    'line-height': '40px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '1px',
    'textAlign': 'center',
#     'background-color':'#42e2f4',
    'background-color':'#b0e2f4',
    'vertical-align':'middle',
}

buttons_grid_style = {'display': 'grid',
  'grid-template-columns': '49.5% 49.5%',
  'grid-gap': '1px'
}  

#**************************************************************************************************

def format_df(df_in,non_value_cols):
    df = df_in.copy()
    value_columns = [c for c in df.columns.values if c not in non_value_cols]
    for c in value_columns:
        try:
            df[c] = df[c].round(3)
        except:
            pass
    all_cols = non_value_cols + value_columns 
    df = df[all_cols]
    return df

#**************************************************************************************************

def parse_contents(contents):
    '''
    app.layout contains a dash_core_component object (dcc.Store(id='df_memory')), 
      that holds the last DataFrame that has been displayed. 
      This method turns the contents of that dash_core_component.Store object into
      a DataFrame.
      
    :param contents: the contents of dash_core_component.Store with id = 'df_memory'
    :returns pandas DataFrame of those contents
    '''
    c = contents.split(",")[1]
    c_decoded = base64.b64decode(c)
    c_sio = io.StringIO(c_decoded.decode('utf-8'))
    df = pd.read_csv(c_sio)
    # create a date column if there is not one, and there is a timestamp column instead
    cols = df.columns.values
    cols_lower = [c.lower() for c in cols] 
    if 'date' not in cols_lower and 'timestamp' in cols_lower:
        date_col_index = cols_lower.index('timestamp')
        # make date column
        def _extract_dt(t):
            y = int(t[0:4])
            mon = int(t[5:7])
            day = int(t[8:10])
            hour = int(t[11:13])
            minute = int(t[14:16])
            return datetime.datetime(y,mon,day,hour,minute,tzinfo=pytz.timezone(DEFAULT_TIMEZONE))
        # create date
        df['date'] = df.iloc[:,date_col_index].apply(_extract_dt)
    return df

#**************************************************************************************************
class GridItem():
    def __init__(self,child,html_id=None,use_loading=False):
        self.child = child
        self.html_id = html_id
        self.use_loading = use_loading
    @property
    def html(self):
        if self.use_loading:
            if self.html_id is not None:
                h =  html.Div(children=self.child,className='grid-item',id=self.html_id)
            else:
                h =  html.Div(children=self.child,className='grid-item')
            return dcc.Loading(children=[h],type='cube')
        else:
            if self.html_id is not None:
                return html.Div(children=self.child,className='grid-item',id=self.html_id)
            else:
                return html.Div(children=self.child,className='grid-item')
#**************************************************************************************************


class GridTable():
    def __init__(self,html_id,title,
                 input_content_tuple=None,
                 df_in=None,
                 columns_to_display=None,
                 editable_columns=None,
                 input_transformer=None,
                 use_html_table=False):
        self.html_id = html_id
        self.title = title
        self.df_in = df_in
        self.input_content_tuple =  input_content_tuple
        self.columns_to_display = columns_to_display
        self.editable_columns = [] if editable_columns is None else editable_columns
        self.datatable_id = f'{html_id}_datatable'
        self.output_content_tuple = (self.datatable_id,'data')
        self.input_transformer = input_transformer
        self.use_html_table = use_html_table
        if self.input_transformer is None:
            self.input_transformer = lambda dict_df: None if dict_df is None else pd.DataFrame(dict_df)
        self.dt_html = self.create_dt_html(df_in=df_in)


    def create_dt_div(self,df_in=None):
        dt = dash_table.DataTable(
            page_current= 0,
            page_size= 100,
            page_action='native',
            sort_action='native',
            filter_action='none', # 'fe',
#             content_style='grow',
            style_cell_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ] + [
                {
                    'if': {'column_id': c},
                    'textAlign': 'left',
                } for c in ['symbol', 'underlying']
            ],
            
            style_as_list_view=False,
            style_table={
                'maxHeight':'450','overflowX': 'scroll',
            } ,
            editable=True,
            css=[{"selector": "table", "rule": "width: 100%;"}],
            id=self.datatable_id
        )
        if df_in is None:
            df = pd.DataFrame({'no_data':[]})
        else:
            df = df_in.copy()
            if self.columns_to_display is not None:
                df = df[self.columns_to_display]                
        dt.data=df.to_dict("rows")
        dt.columns=[{"name": i, "id": i,'editable': True if i in self.editable_columns else False} for i in df.columns.values]                    
        return [
                html.H4(self.title,style={'height':'3px'}),
                dt
            ]


    
    def create_dt_html(self,df_in=None):         
        dt_html = html.Div(self.create_dt_div(df_in=df_in),
            id=self.html_id,
            style={'margin-right':'auto' ,'margin-left':'auto' ,'height': '98%','width':'98%','border':'thin solid'}
        )
        return dt_html
        
    @property
    def html(self):
        return self.dt_html
        

    def callback(self,theapp):
        @theapp.callback(
            # outputs
            Output(self.html_id,'children'),
            [Input(component_id=self.input_content_tuple[0], component_property=self.input_content_tuple[1])]
        )
        def output_callback(dict_df):
#             if dict_df is None:
#                 return None
            if self.df_in is None:
                df = self.input_transformer(dict_df)
            else:
                df = self.df_in.copy()
            dt_div = self.create_dt_div(df)
            return dt_div
            
        return output_callback

#**************************************************************************************************



def charts(x_vals,y_vals,chart_title,x_title,y_title):
    fig = go.Figure(data = [go.Bar(
                x=x_vals,
                y=y_vals
        )])
    fig['layout'] = {
                'title':chart_title,
                'xaxis':{
                    'title':x_title
                },
                'yaxis':{
                     'title':y_title
                }
            }

    return fig




class GridGraph():
    def __init__(self,html_id,title,
                 input_content_tuple=None,
                 df_x_column=None,
                 df_y_columns=None,
                 x_title=None,
                 y_title=None,
                 figure=None,
                 df_in=None,
                 plot_bars=False,
                 input_transformer=None):
        # self.html_id = html_id
        self.html_id = html_id
        self.input_content_tuple = input_content_tuple

        self.output_content_tuple = (self.html_id,'figure')        
        self.df_x_column = df_x_column
        self.df_y_columns = df_y_columns
        self.input_transformer = input_transformer 
        if self.input_transformer is None:
            self.input_transformer = lambda dict_df: pd.DataFrame(dict_df)
        self.plot_bars = plot_bars
        self.title = title
        self.x_title = 'x_title' if x_title is None else x_title
        self.y_title = 'y_title' if y_title is None else y_title
        f = figure if figure is not None else self.make_chart_figure(df_in)
        gr = dcc.Graph(
                id=html_id,
                figure=f,               
                )
        self.gr_html = html.Div(
            gr,
            className='item1',
            style={'margin-right':'auto' ,'margin-left':'auto' ,'height': '98%','width':'98%','border':'thin solid'}
        ) 
    @property
    def html(self):
        return self.gr_html        

    
    def get_x_y_values(self,df):
        if df is None or len(df)<1:
            return (np.array([]),np.array([[]]))
        if self.df_x_column is None:
            x_vals = list(df.index)
        else:
            x_vals=df[self.df_x_column].values    
        if self.df_y_columns is None:
            if self.df_x_column is None:
                ycols = df.columns.values
            else:
                ycols = [c for c in df.columns.values if c != self.df_x_column]
        else:
            ycols = self.df_y_columns
        y_vals = df[ycols].values
        return (x_vals,y_vals)
    
    def make_chart_figure(self,df):
        if df is not None:
            x_vals,y_vals = self.get_x_y_values(df)
            if self.plot_bars: 
                bars =  [go.Bar(x=x_vals,y=y_vals[:,i]) for i in range(y_vals.shape[1])]
            else:
                bars =  [go.Scatter(x=x_vals,y=y_vals[:,i]) for i in range(y_vals.shape[1])]   
        else:
            bars = [go.Bar(x=[],y=[])]
        fig = go.Figure(data = bars,
            layout= go.Layout(title = self.title,plot_bgcolor='#f5f5f0'),
        )
        return fig
        
    def callback(self,theapp):
        @theapp.callback(
            Output(self.html_id,'figure'), 
            [Input(component_id=self.input_content_tuple[0], component_property=self.input_content_tuple[1])],
        )
        def update_graph(dict_df,*args):
            if dict_df is not None:
                df = self.input_transformer(dict_df)#pd.DataFrame(dict_df)
            else:
                df = None
            return self.make_chart_figure(df)



#**************************************************************************************************

#**************************************************************************************************
class DccStore():        
    def __init__(self,html_id,
                 input_content_tuple,
                 transformer_module):
        self.html_id = html_id
        self.input_content_tuple = input_content_tuple
        self.transformer_module = transformer_module
        self.dcc_store = dcc.Store(id=html_id)
        self.dcc_html = html.Div(self.dcc_store,style={"display": "none"})
        self.output_content_tuple = (self.html_id,'data')

    @property
    def html(self):
        return self.dcc_html        

    def callback(self,theapp):
        @theapp.callback(
            Output(self.html_id,'data'), 
            [Input(component_id=self.input_content_tuple[0], component_property=self.input_content_tuple[1])],
        )
        def update_store(input_data,*args):
            return self.transformer_module(input_data)
#**************************************************************************************************
           


def create_grid(component_array,num_columns=2,column_width_percents=None,additional_grid_properties_dict=None):
    gs = grid_style.copy()
    percents = [str(round(100/num_columns-.001,1))+'%' for _ in range(num_columns)] if column_width_percents is None else [str(c)+'%' for c in column_width_percents]
    perc_string = " ".join(percents)
    gs['grid-template-columns'] = perc_string 
    if additional_grid_properties_dict is not None:
        for k in additional_grid_properties_dict.keys():
            gs[k] = additional_grid_properties_dict[k]           
#     g =  html.Div([GridItem(c).html if type(c)==str else c.html for c in component_array], style=gs)

    div_children = []
    for i,c in enumerate(component_array):
        if type(c)==str:
            div_children.append(GridItem(c).html)
        elif hasattr(c,'html'):
            div_children.append(c.html)
        else:
            div_children.append(c)
    g = html.Div(div_children,style=gs)
    return g

#**************************************************************************************************

#**************************************************************************************************
class MultiInput():
    def __init__(self,html_id,input_tuple_list):
        self.html_id = html_id
        self.input_tuple_list = input_tuple_list
        self.store = dcc.Store(id=html_id)
        self.output_tuple = (html_id,'data')
        self.div = html.Div([self.store],style={'display':'none'})
    
    @property
    def html(self):
        return self.div        
    
    def callback(self,theapp):
        @theapp.callback(
            Output(self.output_tuple[0],self.output_tuple[1]),
            [Input(t[0],t[1]) for t in self.input_tuple_list],
        )
        def update_div(*values):
            return values        
        return update_div
       
#**************************************************************************************************


#**************************************************************************************************

class ReactiveDiv():
    def __init__(self,html_id,input_tuple,
                 input_transformer=None,display=True,
                 dom_storage_dict=None,
                 style=None):
        self.html_id = html_id
        self.input_tuple = input_tuple
        s = button_style if style is None else style

        self.dom_storage_id = f'reactive_div_dom_storage_{self.html_id}'
        self.dom_storage_dict = {} if dom_storage_dict is None else dom_storage_dict
        self.dom_storage = dcc.Store(id=self.dom_storage_id,storage_type='session',data=self.dom_storage_dict)
        if display:
            # self.div = dcc.Loading(children=[html.Div([],id=self.html_id,style=s),self.dom_storage],type='cube')
            self.div = dcc.Loading(
                children=[html.Div([],id=self.html_id,style=s),self.dom_storage],type='cube',fullscreen=True
            )
        else:
            self.div = html.Div([html.Div([],id=self.html_id,style={'display':'none'}),self.dom_storage])

        self.input_transformer = input_transformer 
        if self.input_transformer is None:
            self.input_transformer = lambda value,data: str(value)
        
        
    @property
    def html(self):
        return self.div        
    
    def callback(self,theapp):
        @theapp.callback(
            Output(self.html_id,'children'),
            [Input(self.input_tuple[0],self.input_tuple[1])],
            [State(self.dom_storage_id,'data')]
        )
        def update_div(value,data):
            print('entering ReactiveDiv callback')
            d = self.dom_storage_dict if len(data)<=0 else data
            return self.input_transformer(value,d)        
        return update_div    
    
#**************************************************************************************************
default_markdown_style={
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '1px',
    'background-color':'#ffffff',
}

class MarkDownDiv():
    def __init__(self,html_id,markdown_text,markdown_style=None):
        self.html_id = html_id
        ms = default_markdown_style if  markdown_style is None else markdown_style
        self.html_element = html.Span(dcc.Markdown(markdown_text),style=ms)
            
    @property
    def html(self):
        return self.html_element        
#**************************************************************************************************

#**************************************************************************************************


#**************************************************************************************************
class StatusDiv():
    '''
    Use a list of lists to update display a status message from multiple inputs:
        The inner dimension is a list where:
            dimension 0 is an input_tuple
            dimension 1 is a string message to display if that input fires
    
    Example:
      [
        [
            (input_tuple_from_gridtable1),'gridtable1 is completed'
        ],
        [
            (input_tuple_from_gridtable2),'gridtable2 is completed'
        ],
        [
            (input_tuple_from_gridtable3),'gridtable3 is completed'
        ]
      ]
    '''
    def __init__(self,html_id,input_tuple_list,style=None):
        '''
        
        :param html_id:
        :param input_tuple_list: a list of lists as described above
        '''
        self.html_id = html_id
        self.store_list = []
        for i in range(len(input_tuple_list)):
            dccs = DccStore(f'{html_id}_{i}', input_tuple_list[i][0], lambda x: input_tuple_list[i][1])
            self.store_list.append(dccs)
        s = style
        if s is None:
            s = select_file_style
        self.div = html.Div([html.Div([],id=self.html_id,style=s)]+[s.html for s in self.store_list])
        self.input_history=[None for _ in input_tuple_list]   
        
    @property
    def html(self):
        return self.div        
    
    def callback(self,theapp):
        @theapp.callback(
            Output(self.html_id,'children'),
            [Input(inp.output_content_tuple[0],inp.output_content_tuple[1]) for inp in self.store_list]
        )
        def update_div(*inputs):
            print('entering StatusDiv callback')
            print(inputs)
            for i in range(len(inputs)):
                if inputs[i] is not None and self.input_history[i] is None:
                    self.input_history[i] = inputs[i]
                    return inputs[i]
                if inputs[i] is not None and inputs[i] != self.input_history[i]:
                    self.input_history[i] = inputs[i]
                    return inputs[i]                     
            return None  
        [c.callback(theapp) for c in self.store_list]      
        return update_div

#**************************************************************************************************

#**************************************************************************************************
class CsvUploadButton():
    def __init__(self,button_id,display_text=None,style=None):
        self.style = button_style if style is None else style
        self.button_id = button_id
        self.html_id = button_id
        self.output_tuple = (f'{self.button_id}_df','data')
        disp_txt = 'CLICK to select a portfolio csv' if display_text is None else display_text
        dc = dcc.Upload(
                id=self.button_id,
                children=html.Div([disp_txt]),
                # Allow multiple files to be uploaded
                multiple=False,
            )
        self.dc = dc
        self.store = dcc.Store(id=f'{self.button_id}_df')
    @property
    def html(self):
        return html.Div([self.dc,self.store],style=self.style)       
    
    def callback(self,theapp):
        @theapp.callback(
            # TODO: change this to Output(self.output_tuple[0],self.output_tuple[1])
            Output(f'{self.button_id}_df','data'), 
            [
                Input(self.button_id, 'contents'),
            ]
        )
        def  update_filename(contents):
            if contents is None:
                return None
            dict_df = parse_contents(contents).to_dict('rows')
            return dict_df
        return update_filename
#**************************************************************************************************

    
    
def create_span(html_content,html_id=None,style=None):
    if html_id is not None:
        htmldiv = html.Div(html_content,id=html_id)
    else:
        htmldiv = html.Div(html_content)
    s = html.Span(
            htmldiv,
           style=select_file_style if style is None else style
        )
    return s

#**************************************************************************************************
class CsvUploadSpan():
    def __init__(self,html_id):    
        csv_ub = CsvUploadButton(html_id)
        csv_name = ReactiveDiv(f'{html_id}_csv_name',(csv_ub.html_id,'filename'))
        self.upload_components = [csv_ub,csv_name]
        self.up_div  = html.Div([create_span(c.html) for c in self.upload_components],style=buttons_grid_style)
        self.output_tuple = csv_ub.output_tuple
    @property
    def html(self):
        return self.up_div

class CsvUploadGrid():
    def __init__(self,html_id,display_text=None,file_name_transformer=None,style=None):  
        self.style = blue_button_style if style is None else style  
        csv_ub = CsvUploadButton(html_id,style=self.style,display_text=display_text)
        csv_name = ReactiveDiv(f'{html_id}_csv_name',(csv_ub.html_id,'filename'),style=self.style,
                               input_transformer=file_name_transformer)
        self.upload_components = [csv_ub,csv_name]
        self.grid = create_grid(self.upload_components)
        self.output_tuple = csv_ub.output_tuple

#**************************************************************************************************


#**************************************************************************************************
class DropDownDiv():
    def __init__(self,html_id,
                 dropdown_labels,
                 dropdown_values,
                 placeholder = None,
                 transformer_method=None,
                 default_initial_index=0,
                 style=None):
        self.html_id = html_id
        self.style = button_style if style is None else style
        self.input_tuple = (f'{html_id}_dropdown','value')
        self.dropdown_choices = [{'label':l,'value':v} for l,v in zip(dropdown_labels,dropdown_values)]
        self.dropdown = dcc.Dropdown(id=self.input_tuple[0], value=dropdown_values[default_initial_index],
                options=self.dropdown_choices,
                placeholder="Select an Option" if placeholder is None else placeholder,
                style=self.style)
        self.dropdown_div = html.Div([self.dropdown])
        
        self.transformer_method = transformer_method
        if self.transformer_method is None:
            self.transformer_method = lambda v: v
        self.dcc_id = f'{html_id}_dropdown_output'
        self.dcc_store = dcc.Store(id=self.dcc_id)
        self.output_tuple = (self.dcc_id,'data')
        self.fd_div = html.Div([self.dropdown_div,self.dcc_store])
        self.current_value = None

    @property
    def html(self):
        return self.fd_div
        

    def callback(self,theapp):     
        @theapp.callback(
            Output(self.output_tuple[0], self.output_tuple[1]), 
            [Input(self.input_tuple[0],self.input_tuple[1])]
            )
        def set_dcc(value):
            print(f'entering {self.html_id} with data {value}')
            transformed_value = self.transformer_method(value)
            self.current_value = transformed_value
            return transformed_value        
        return set_dcc                            
#**************************************************************************************************


#**************************************************************************************************
class FileDownLoadDiv():
    def __init__(self,html_id,
                 dropdown_labels,dropdown_values,a_link_text,
                 create_file_name_transformer=None,
                 style=None):
        self.html_id = html_id
        s = button_style if style is None else style
        self.input_tuple = (f'{html_id}_dropdown','value')
        dropdown_choices = [{'label':l,'value':v} for l,v in zip(dropdown_labels,dropdown_values)]
        dropdown_div = html.Div([
                dcc.Dropdown(id=self.input_tuple[0], value=dropdown_values[0],
                options=dropdown_choices
                ,style=s,placeholder="Select a File Download Option")
        ])
        self.output_tuple = (f'{html_id}_last_downloaded','href')
        href_div = html.Div(html.A(a_link_text,href='',id=self.output_tuple[0]),style=s)
        gs= grid_style
        gs['background-color'] = '#fffff0'
        self.fd_div = html.Div([dropdown_div,href_div],style=gs)
        self.create_file_name_transformer = lambda value: value if create_file_name_transformer is None else create_file_name_transformer
    @property
    def html(self):
        return self.fd_div
        

    def callback(self,theapp):     
        @theapp.callback(
            Output(self.output_tuple[0], self.output_tuple[1]), 
            [Input(self.input_tuple[0],self.input_tuple[1])]
            )
        def update_link(value):
            return '/dash/urlToDownload?value={}'.format(value)        
        return update_link
    
    def route(self,theapp):
        @theapp.server.route('/dash/urlToDownload')
        def download_csv():
            value = flask.request.args.get('value')            
            fn = self.create_file_name_transformer(value)
            print(f'FileDownLoadDiv callback file name = {fn}')
            return flask.send_file(fn,
                               mimetype='text/csv',
                               attachment_filename=fn,
                               as_attachment=True)
#             return download_csv
                
#**************************************************************************************************


#**************************************************************************************************
class  BaseComponent():
    def __init__(self,html_id,
                 display_component,
                 display_properties,
                 input_component=None,
                 input_transformer=None,
                 display=True,
                 style=None):
        self.html_id = html_id
        self.display_component = display_component
        self.display_properties = display_properties
        self.display_component_html = self.display_component.html if hasattr(self.display_component, 'html') else display_component
        self.display_component_id = str(self.display_component.id) if not hasattr(self.display_component,'html_id') else self.display_component.html_id
        self.input_component = display_component if input_component is None else input_component
        self.input_component_id = str(self.input_component.id) if not hasattr(self.input_component,'html_id') else self.input_component.html_id
#         self.available_props = [p for p in self.input_component.available_properties if hasattr(input_component, p)]
        self.input_transformer = input_transformer
        if self.input_transformer is None:
            self.input_transformer = lambda input_list: input_list
        self.display = display
        self.output_store_id = f'{self.html_id}_dropdown_output'
        self.output_store = dcc.Store(id=self.output_store_id)
        if hasattr(self.input_component, 'output_store_id'):
            output_store_id = self.input_component.output_store_id
            output_store_input = [Input(output_store_id,'data')]
        else:
            output_store_input = []
        self.inputs =  output_store_input + [Input(self.display_component_id,p) for p in self.display_properties]

        self.style = style
        self._div = html.Div([html.Div([self.display_component_html],id=html_id),self.output_store])

    @property
    def html(self):
        return self._div
        

    def callback(self,theapp):     
        @theapp.callback(
            Output(self.output_store_id,'data'), 
            self.inputs 
            )
        def execute_callback(*inputs_and_states):
            print(f'execute_callback: {self.html_id} {list(inputs_and_states)}')
            if all([x is None for x in list(inputs_and_states)]):
                return list(inputs_and_states)
            return self.input_transformer(list(inputs_and_states))       
        return execute_callback
    
            
        
#**************************************************************************************************


#**************************************************************************************************
#gt1.html.children[1]
#gr1.html.children

class GridDataTable(html.Div):
    def __init__(self,html_id,title,
                 input_content_tuple=None,
                 df_in=None,
                 columns_to_display=None,
                 editable_columns=None,
                 input_transformer=None,
                 use_html_table=False):
        super(GridDataTable,self).__init__([],id=html_id)
        self.html_id = html_id
        self.title = title
        self.df_in = df_in
        self.input_content_tuple =  input_content_tuple
        self.columns_to_display = columns_to_display
        self.editable_columns = [] if editable_columns is None else editable_columns
        self.datatable_id = f'{html_id}_datatable'
        self.output_content_tuple = (self.datatable_id,'data')
        self.input_transformer = input_transformer
        self.use_html_table = use_html_table
        if self.input_transformer is None:
            self.input_transformer = lambda dict_df: None if dict_df is None else pd.DataFrame(dict_df)
        self.children = self.create_dt_html(df_in=df_in)

    def create_dt_div(self,df_in=None):
        dt = dash_table.DataTable(
            page_current= 0,
            page_size= 100,
            page_action='native',
            sort_action='native',
            filter_action='none', # 'fe',
#             content_style='grow',
            style_cell_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ] + [
                {
                    'if': {'column_id': c},
                    'textAlign': 'left',
                } for c in ['symbol', 'underlying']
            ],
            
            style_as_list_view=False,
            style_table={
                'maxHeight':'450','overflowX': 'scroll',
            } ,
            editable=True,
            css=[{"selector": "table", "rule": "width: 100%;"}],
            id=self.datatable_id
        )
        if df_in is None:
            df = pd.DataFrame({'no_data':[]})
        else:
            df = df_in.copy()
            if self.columns_to_display is not None:
                df = df[self.columns_to_display]                
        dt.data=df.to_dict("rows")
        dt.columns=[{"name": i, "id": i,'editable': True if i in self.editable_columns else False} for i in df.columns.values]                    
        return [
                html.H4(self.title,style={'height':'3px'}),
                dt
            ]


    
    def create_dt_html(self,df_in=None):         
        dt_html = html.Div(self.create_dt_div(df_in=df_in),
            id=self.html_id+"_inner_html",
            style={'margin-right':'auto' ,'margin-left':'auto' ,'height': '98%','width':'98%','border':'thin solid'}
        )
        return dt_html
         

class MyDiv(html.Div):
    def __init__(self,children,my_id=None,data=None):
        super(MyDiv,self).__init__(children,id=my_id)
        self.data = data
    @property
    def data(self):
        return self.__data
    @data.setter
    def data(self, data):
        self.__data = data
    
    

class component_example_dataframe_graph():
    def __init__(self):
        logger = root_logger('logfile.log', 'DEBUG')
        df_initial = pd.DataFrame({'symbol':['ibm','spy'],'position':[100,200]})
        def file_store_transformer(contents):
            if contents is None or len(contents)<=0 or contents[0] is None:
                d =  df_initial.to_dict('rows')
            else:
                d = parse_contents(contents[0]).to_dict('rows')
            return [d]

        dc = dcc.Upload(
                id='file_upload',
                children=html.Div(['click to upload']),
                # Allow multiple files to be uploaded
                multiple=False,
            )        
        file_upload = {
            'component':dc,
            'properties_to_output':None,
            'input_component_tuples':[(dc.id,['last_modified'])],
            }
        
        file_store = {
            'component':dcc.Store(id='file_store'),
            'properties_to_output':['data'],
            'input_component_tuples':[(file_upload['component'].id,['contents'])],
            'style':{'display':'none'},
            'callback_input_transformer':file_store_transformer
            }
        

        dt = GridDataTable('dt1', 'portfolio table', 
                    (file_store['component'].id,'data'), 
                    columns_to_display=['symbol','position'], 
                    editable_columns=['position']         
            )
        
        def dt_callback(input_list):
            dict_df = input_list[0]
            df = pd.DataFrame(dict_df)
            children = dt.create_dt_div(df)
            return [children,dict_df]

        
        dt1 = {
#             'component':dt,
            'component':dt.children,
#             'properties_to_output':['children'],
            'properties_to_output':['children',dt.output_content_tuple],
            'input_component_tuples':[(file_store['component'].id,file_store['properties_to_output'])],
            'callback_input_transformer':dt_callback
            }
        
#         gr = GridGraph('g1', 'graph 1',dt.output_content_tuple,
        gr = GridGraph('g1', 'graph 1',dt.output_content_tuple,
                          df_x_column='symbol',df_y_columns=['position'],
                          
                          plot_bars=True)
        def graph_callback(input_list):
            dict_df = input_list[0]
            df =  pd.DataFrame(dict_df)
            fig = gr.make_chart_figure(df)
            return [fig]
        
        gr1 = {
            'component':gr.html.children,
            'properties_to_output':['figure'],
            'input_component_tuples':[(dt.output_content_tuple[0],[dt.output_content_tuple[1]])],    
            'callback_input_transformer':graph_callback
            }        
        
        dd_commod = {
            'component':dcc.Dropdown(id='dd_commod',value='ES',options=[{'label':v,'value':v} for v in ['ES','CL','CB']]),
            'properties_to_output':['value'],
            }
        def dd_month_callback(input_list):
            commod = input_list[0]
            if commod == 'ES':
                op = [{'label':v,'value':v} for v in 'HMUZ']
            else:
                op =  [{'label':v,'value':v} for v in 'FGHJKMNQUVXZ']
            return [op[0]['value'],op]
            
        dd_month = {
            'component':dcc.Dropdown(id='dd_month'),
            'properties_to_output':['value','options'],
            'input_component_tuples':[(dd_commod['component'].id,['value'])],
            'callback_input_transformer':dd_month_callback
            }
        self.component_list=[file_upload,file_store,dt1,gr1,dd_commod,dd_month]



def get_used_properties(dash_component):
    aplist = []
    for ap in dash_component.available_properties:
        if hasattr(dash_component,ap) and ap != 'id':
            aplist.append(ap)
    return aplist

class  ComponentWrapper():
    @staticmethod
    def build_from_json(component_json):
        cbt = None if 'callback_input_transformer' not in component_json else component_json['callback_input_transformer']
        ict = None if 'input_component_tuples' not in component_json else component_json['input_component_tuples']
        cw = ComponentWrapper(component_json['component'], 
                component_json['properties_to_output'], 
                input_component_tuples=ict, 
                callback_input_transformer=cbt, 
                style=None if 'style' not in component_json else component_json['style'])
        return cw
        
    
    def __init__(self,
                 dash_component,
                 input__tuples=None,
                 output_tuples=None,
                 callback_input_transformer=None,
                 style=None,
                 logger=None):
        self.logger = root_logger('logfile.log', 'INFO') if logger is None else logger
        self.component = dash_component
        self.cid = self.component.id
        self.id = self.cid
        self.html_id = f'{self.cid}_html'
        self.properties_to_output = [] if output_tuples is None else output_tuples
        # create callback output list
        self.output_tuples = output_tuples   
        self.output_data_tuple = None 
        if output_tuples is not None:
            for ot in output_tuples:
                if ot[1] == 'data' and self.output_data_tuple is None:
                    self.output_data_tuple = ot
                      
        self.callback_outputs = []
        for p in self.properties_to_output:
            if type(p)==tuple:
                t = p
#                 o = Output(*p)
            else:
#                 o = Output(self.cid,p)
                t = (self.id,p)
            o = Output(*t)
            self.callback_outputs.append(o)
        
        # create callback input list  
        self.callback_inputs = []
        if input__tuples is not None:
            for ict in input__tuples:
                ic_id = ict[0]
                p = ict[1]
                self.callback_inputs += [Input(ic_id,p)]
                
        self.style = {} if style is None else style
        
        self.callback_input_transformer = callback_input_transformer
        def _default_transform(callback_input_list):
            return callback_input_list
        
        if self.callback_input_transformer is None:
            self.callback_input_transformer = _default_transform
        self.div = html.Div([self.component])
        
    @property
    def html(self):
        return self.div           

    def callback(self,theapp):     
        @theapp.callback(
            self.callback_outputs, 
            self.callback_inputs 
            )
        def execute_callback(*inputs_and_states):
            l = list(inputs_and_states)
            self.logger.debug(f'{self.html_id} input: {l}')
            ret = self.callback_input_transformer(l)
            self.logger.debug(f'{self.html_id} output: {ret}')
            return ret
        if len(self.callback_inputs)<=0:
            return None     
        return execute_callback
    
            
class  ComponentWrapper2():
    @staticmethod
    def build_from_json(component_json):
        cbt = None if 'callback_input_transformer' not in component_json else component_json['callback_input_transformer']
        ict = None if 'input_component_tuples' not in component_json else component_json['input_component_tuples']
        cw = ComponentWrapper2(component_json['component'], 
                component_json['properties_to_output'], 
                input_component_tuples=ict, 
                callback_input_transformer=cbt, 
                style=None if 'style' not in component_json else component_json['style'])
        return cw
        
    
    def __init__(self,
                 dash_component,
                 properties_to_output=None,
                 input_component_tuples=None,
                 callback_input_transformer=None,
                 style=None,
                 logger=None):
        self.logger = root_logger('logfile.log', 'INFO') if logger is None else logger
        self.component = dash_component
        self.cid = self.component.id
        self.html_id = f'{self.cid}_html'
        self.properties_to_output = [] if properties_to_output is None else properties_to_output
        # create callback output list
        output_sink_id = f'output_sink_{self.cid}'
        self.sink = dcc.Store(id=output_sink_id)
        self.callback_outputs = []
        for p in self.properties_to_output:
            if type(p)==tuple:
                o = Output(*p)
            else:
                o = Output(self.cid,p)
            self.callback_outputs.append(o)
        self.callback_outputs += [Output(output_sink_id,'data')]
#         self.callback_outputs = [Output(self.cid,p) for p in self.properties_to_output]  + [Output(output_sink_id,'data')]      
        
        # create callback input list
        
        self.callback_inputs = []
        if input_component_tuples is not None:
            for ict in input_component_tuples:
                ic_id = ict[0]
                props = ict[1]
                self.callback_inputs += [Input(ic_id,p) for p in props]
                
        self.style = {} if style is None else style
        self.callback_input_transformer = callback_input_transformer
        def _default_transform(callback_input_list):
#             r = (callback_input_list[0])
#             return r
            return callback_input_list
        if self.callback_input_transformer is None:
            self.callback_input_transformer = _default_transform
        self.div = html.Div([self.component,self.sink])
        
    @property
    def html(self):
        return self.div           

    def callback(self,theapp):     
        @theapp.callback(
            self.callback_outputs, 
            self.callback_inputs 
            )
        def execute_callback(*inputs_and_states):
            l = list(inputs_and_states)
            self.logger.debug(f'{self.html_id} input: {l}')
            x = self.callback_input_transformer(l)
            if len(self.callback_outputs)>1:
                ret = x + [None]
            else:
                ret =  [x]
            self.logger.debug(f'{self.html_id} output: {ret}')
            return ret
        if len(self.callback_inputs)<=0:
            return None     
        return execute_callback
    
        
#**************************************************************************************************



# do dcc's always output to one of their own display properties?  can they change one of their own properties?

class DropDown(BaseComponent):
    def __init__(self,html_id,labels,values,input_component=None,style=None,
                 input_transformer=None):
        super(DropDown,self).__init__(html_id, 
                dcc.Dropdown(id=f'dropdown_{html_id}',value=values[0],options=[{'label':l,'value':v} for l,v in zip(labels,values)]), 
                input_component = input_component,
                display_properties = ['value'],
                style=style,
                input_transformer=(lambda value_list:value_list[0]) if input_transformer is None else input_transformer)














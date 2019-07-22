'''
Created on Jul 10, 2019

@author: bperlman1
'''
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.graph_objs.layout import Font,Margin


def plotly_plot(df_in,x_column,plot_title=None,
                y_left_label=None,y_right_label=None,
                bar_plot=False,figsize=(16,10),
                number_of_ticks_display=20,
                yaxis2_cols=None):
    ya2c = [] if yaxis2_cols is None else yaxis2_cols
    ycols = [c for c in df_in.columns.values if c != x_column]
    # create tdvals, which will have x axis labels
    td = list(df_in[x_column]) 
    nt = len(df_in)-1 if number_of_ticks_display > len(df_in) else number_of_ticks_display
    spacing = len(td)//nt
    tdvals = td[::spacing]
    
    # create data for graph
    data = []
    # iterate through all ycols to append to data that gets passed to go.Figure
    for ycol in ycols:
        if bar_plot:
            b = go.Bar(x=td,y=df_in[ycol],name=ycol,yaxis='y' if ycol not in ya2c else 'y2')
        else:
            b = go.Scatter(x=td,y=df_in[ycol],name=ycol,yaxis='y' if ycol not in ya2c else 'y2')
        data.append(b)

    # create a layout
    layout = go.Layout(
        title=plot_title,
        xaxis=dict(
            ticktext=tdvals,
            tickvals=tdvals,
            tickangle=45,
            type='category'),
        yaxis=dict(
            title='y main' if y_left_label is None else y_left_label
        ),
        yaxis2=dict(
            title='y alt' if y_right_label is None else y_right_label,
            overlaying='y',
            side='right'),
        margin=Margin(
            b=100
        )        
    )

    fig = go.Figure(data=data,layout=layout)
    return fig

class VolTable():
    def __init__(self,df_implied_vol_csv_path):
        self.df_implied_vol_csv_path = df_implied_vol_csv_path
        self.df_iv = pd.read_csv(self.df_implied_vol_csv_path)

    def create_skew_per_date_df(self,contract):
        '''
        Create a DataFrame whose columns are settle_date's and whose
           rows are amounts from the money.
        You can use this to graph the skew of a symbol, and have
           multiple day's curves per graph
        :param contract:
        '''
        # get just that symbol's data and only days that have sufficient skew data
        dft = self.df_iv[self.df_iv.symbol==contract]
        
        # make sure that, for each settle_date in dft, there are sufficient
        #    number of records (1 record per moneyness). 
        dft_count = dft[['settle_date','symbol']].groupby('settle_date',as_index=False).count()
        valid_settle_dates = dft_count[dft_count.symbol>2].settle_date.unique()
        # make df12 only have settle_dates that have sufficient moneyness records
        df12 = dft[dft.settle_date.isin(valid_settle_dates)]
        
        # for each settle_date, there will be some that don't 
        #   have a record for every level of moneyness
        # Just select those moneyness levels where, for that moneyness level,
        #   there are are an equal number of settle_dates
        df_counts = df12[['settle_date','moneyness']].groupby('settle_date',as_index=False).count()
        max_count = df_counts.moneyness.max()
        first_max_count_settle_date = df_counts[df_counts.moneyness==max_count].iloc[0].settle_date
        
        # now loop through each date, and turn that date into a column of 
        #   the final DataFrame
        df_ret = df12[df12.settle_date==first_max_count_settle_date][['moneyness']]
        all_settle_dates = sorted(df_counts.settle_date.unique())
        for settle_date in all_settle_dates:
            df_temp = df12[df12.settle_date==settle_date][['moneyness','vol_skew']]
            df_ret = df_ret.merge(df_temp,on='moneyness',how='outer')
            df_ret = df_ret.rename(columns={'vol_skew':str(settle_date)})
        df_ret = df_ret.sort_values('moneyness')
        df_ret.moneyness = df_ret.moneyness.round(4)
        return df_ret


    def graph_skew(self,contract):
        '''
        Create a multiple graph figures for one contract, where each figure
          graphs multiple lines for mulitple settle_dates, and where
          the x axis is moneyness, and the y axis is vol skew
        Graph skew for ONLY ONE symbol.
        If df_iv_final contains more than one symbol, we will only graph the first symbol in the DataFrames    
        '''
        dfp = self.create_skew_per_date_df(contract)
        
        settle_dates = sorted([c for c in dfp.columns.values if c != 'moneyness'])
        splits = list(np.arange(5,len(settle_dates),5))
        settle_date_groups = np.split(np.array(settle_dates),splits)
        ret_figs = []
        for sdg in settle_date_groups:
            sdg_sorted = [str(c) for c in sorted(sdg)]
            cols = ['moneyness']+list(sdg_sorted)
            dfp_sub = dfp[cols]
            t = f'{contract} {sdg[0]} - {sdg[-1]}' 
            f = plotly_plot(dfp_sub,x_column='moneyness',plot_title=t,y_left_label='vol skew')
            ret_figs.append(f)
        return ret_figs

                

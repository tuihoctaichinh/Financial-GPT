# coding: utf-8
import os
import sys
# Add the parent directory of mypackage to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apps.get_data_Y import *
from app import app
from app import server

from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import json
import pandas as pd
import requests
import numpy as np
import dash_bootstrap_components as dbc
idx = pd.IndexSlice
from datetime import datetime
import polars as pl
from requests_html import AsyncHTMLSession
asession = AsyncHTMLSession()
from dateutil.relativedelta import relativedelta

def get_price(ticker):
    url = 'https://finfo-api.vndirect.com.vn/v4/ratios/latest?filter=itemCode:51003&where=code:'+ticker+'&order=reportDate'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
    try:
        r = requests.get(url,headers=headers)
        raw = pd.json_normalize(json.loads(r.content)['data'])
        fs = raw[['code','value','reportDate']]
        return fs
    except:
        print('Có lỗi, xin nhập mã khác')

def add_data(ticker):
    ticker = ticker.upper()
    try:
        x = get_data_Y(ticker)
        return x
    except:
        print('Có lỗi, xin nhập mã khác')

layout = html.Div(children=[
    html.Header(children='Graph công ty thường Năm', className='ml-4',
                style={'font-size': '30px', 'font-weight': 'bold', 'font-family': 'Arial', 'text-align': 'center'}),
    html.Div(children='''Chọn mã CK và nhấn Enter:''', className='ml-4', style={'font-size': '20px'}),
    dcc.Input(id='input', value='VNM', type='text', debounce=True, className='ml-4'),
    html.Br(),
    html.Br(),
    dbc.Container(id='price-SQLY',className='six columns',
                 style={'width': '30%', 'display': 'inline-block','margin-left':'5px'}),
    html.Div(id='intermediate-valueSQLY', style={'display': 'none'}),
    html.Div([
        html.Div([dcc.Graph(id='output-graph1SQLY')], className='six columns',
                 style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='output-graph2SQLY')], className='six columns',
                 style={'width': '50%', 'display': 'inline-block'}),
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='output-graph3SQLY')], className='six columns',
                 style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='output-graph4SQLY')], className='six columns',
                 style={'width': '50%', 'display': 'inline-block'}),
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='output-graph5SQLY')], className='six columns',
                 style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='output-graph6SQLY')], className='six columns',
                 style={'width': '50%', 'display': 'inline-block'}),
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(id='output-graph7SQLY')], className='six columns',
                 style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='output-graph8SQLY')], className='six columns',
                 style={'width': '50%', 'display': 'inline-block'}),
    ], className='row')
])

@app.callback(Output('price-SQLY', 'children'),
              [Input(component_id='input', component_property='value')])
def display_price(ticker):
    price = get_price(ticker)
    mc = price['value']/1000000000
    text = 'Vốn hóa của ' + price['code'].values[0] + ' tại ' + price['reportDate'].values[0] + ' là: ' + mc.map('{:,.0f}'.format).values[0] + ' tỷ VND'
    alert = dbc.Alert(text,dismissable=False,is_open=True,color="success")
    return alert

@app.callback(Output('intermediate-valueSQLY', 'children'), [Input(component_id='input', component_property='value')])
def clean_data(ticker):
    dfY = add_data(ticker)
    return dfY.write_json(row_oriented=True)


@app.callback(
    Output(component_id='output-graph1SQLY', component_property='figure'),
    [Input(component_id='intermediate-valueSQLY', component_property='children')]
)
def profit(dat):
    chart = pl.from_pandas(pd.read_json(dat))
    date = chart.select(pl.col("dates")).to_series()
    test = go.Scatter(y=chart.select(pl.col("Lãi gộp_m")).to_series(), x=date, name="Gross Margin", yaxis='y2',
                      line=dict(color='red', width=3), mode='lines',line_shape='spline')
    test2 = go.Scatter(y=chart.select(pl.col("EBT_m")).to_series(), x=date, name="OP Margin (inc. ir)",
                       yaxis='y2', line=dict(color='rgb(191, 214, 48)', width=3), mode='lines',line_shape='spline')
    test3 = go.Scatter(y=chart.select(pl.col("Lãi/(lỗ) thuần sau thuế_m")).to_series(), x=date,
                       name="Net Margin", yaxis='y2', line=dict(color='darkturquoise', width=3), mode='lines',line_shape='spline')
    test4 = go.Bar(y=chart.select(pl.col("Doanh số thuần")).to_series(), x=date, name='Doanh thu thuần',
                   marker=dict(color=('teal')))
    data_set = [test, test2, test3, test4]
    fig = go.Figure(data=data_set,layout=dict(title='Doanh thu và tỷ suất LN',
                           xaxis=dict(tickformat='%Y', showgrid=False),
                           yaxis=go.layout.YAxis(  # hoverformat = '.1f'
                           )
                           , yaxis2=go.layout.YAxis(tickformat='.1%', gridwidth=3, showgrid=False,
                                                    overlaying='y', side='right')
                           , legend=dict(x=1.1, y=1)
                           ))
    
    return fig.update_layout( template='plotly_dark',title_x=0.5,
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)')

@app.callback(
    Output(component_id='output-graph2SQLY', component_property='figure'),
    [Input(component_id='intermediate-valueSQLY', component_property='children')]
)
def roae(dat):
    chart = pl.from_pandas(pd.read_json(dat))
    date = chart.select(pl.col("dates")).to_series()

    test1 = go.Scatter(y=chart.select(pl.col("roe")).to_series(), x=date, name="roe", yaxis='y2',
                       line=dict(color='red', width=3), mode='lines',line_shape='spline')
    test2 = go.Scatter(y=chart.select(pl.col("roe_core")).to_series(), x=date, name="roe cốt lõi", yaxis='y2',
                       line=dict(color='rgb(191, 214, 48)', width=3), mode='lines',line_shape='spline')
    test3 = go.Bar(y=chart.select(pl.col("op")).to_series(), x=date, name='LNTT cốt lõi',
                   marker=dict(color=('teal')))
    test4 = go.Bar(y=(chart.select(pl.col("Trong đó: Chi phí lãi vay")).to_series()), x=date, name='Chi phí lãi vay',
                   marker=dict(color=('goldenrod')))
    test5 = go.Bar(y=chart.select(pl.col("fin_income")).to_series(), x=date, name='LN tài chính',
                   marker=dict(color=('#A4DE02')))
    test6 = go.Bar(y=chart.select(pl.col("Lãi/(lỗ) từ công ty liên doanh")).to_series(), x=date, name='LN LDLK',
                   marker=dict(color=('deeppink')))
    test7 = go.Bar(y=chart.select(pl.col("Thu nhập khác, ròng")).to_series(), x=date, name='LN khác',
                   marker=dict(color=('darkgray')))
    test8 = go.Scatter(y=chart.select(pl.col("Lãi/(lỗ) thuần sau thuế")).to_series(), x=date, name="LNST",
                       line=dict(color='darkturquoise', width=3,dash='dot'), mode='lines',line_shape='spline')

    roae = [test1, test2, test3, test4, test5, test6,test7,test8]
    fig = go.Figure(data=roae,layout=go.Layout(barmode='relative',
                                title='Lợi nhuận trước thuế',
                                xaxis=dict(tickformat='%Y', showgrid=False),
                                yaxis2=go.layout.YAxis(tickformat='.1%', gridwidth=3, overlaying='y', side='right',
                                                       showgrid=False)

                                , legend=dict(x=1.1, y=1)

                                # yaxis2=dict(title='Price',overlaying='y', side='right')
                                ))
    return fig.update_layout(template='plotly_dark',title_x=0.5,
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)')

@app.callback(
    Output(component_id='output-graph3SQLY', component_property='figure'),
    [Input(component_id='intermediate-valueSQLY', component_property='children')]
)
def asset(dat):
    chart = pl.from_pandas(pd.read_json(dat))
    date = chart.select(pl.col("dates")).to_series()
    asset_bar1 = go.Bar(y=chart.select(pl.col("bs_cash")).to_series(), x=date, name='Tiền+ĐTNH',
                        marker=dict(color=('teal')))
    asset_bar2 = go.Bar(y=chart.select(pl.col("bs_ar")).to_series(), x=date, name="Phải thu ngắn+dài hạn",
                        marker=dict(color=('#A4DE02')))
    asset_bar3 = go.Bar(y=chart.select(pl.col("Hàng tồn kho, ròng")).to_series(), x=date, name="Hàng tồn kho",
                        marker=dict(color=('green')))
    asset_bar4 = go.Bar(y=chart.select(pl.col("bs_fa")).to_series(), x=date, name="TSCĐ",
                        marker=dict(color=('rgb(200, 0, 0)')))
    asset_bar5 = go.Bar(y=chart.select(pl.col("Tài sản dở dang dài hạn")).to_series(), x=date, name="XDCB",
                        marker=dict(color=('goldenrod')))

    asset_bar6 = go.Bar(y=chart.select(pl.col("Đầu tư dài hạn")).to_series(), x=date, name="Đầu tư dài hạn",
                        marker=dict(color=('deeppink')))
    asset_bar7 = go.Bar(y=chart.select(pl.col("other_asset")).to_series(), x=date, name="Khác",
                        marker=dict(color=('darkgray')))
    asset_bar8 = go.Scatter(y=chart.select(pl.col("ca/ta")).to_series(), x=date, yaxis='y2',
                            name="TS ngắn hạn/Tổng tài sản", line=dict(color='deeppink', width=3, dash='dot'),
                            mode='lines',line_shape='spline')
    # asset_bar9 = go.Scatter(y=chart.select(pl.col("mc")).to_series(), x=date, yaxis='y', name="Vốn hóa",
    #                         line=dict(color='darkturquoise', width=3), mode='lines+markers')
    asset_data = [asset_bar1, asset_bar2, asset_bar3, asset_bar4, asset_bar5, asset_bar6, asset_bar7,asset_bar8
                #   , asset_bar9
                  ]

    fig = go.Figure(data=asset_data,layout=go.Layout(barmode='relative'
                                , xaxis=dict(tickformat='%Y', showgrid=False)
                                , yaxis=go.layout.YAxis(gridwidth=3  # ,hoverformat = '.1f'
                                                        )
                                , yaxis2=go.layout.YAxis(showgrid=False, tickformat='.1%',
                                                         overlaying='y', side='right', range=[0, 1])
                                , title='Cơ cấu tài sản'
                                , legend=dict(x=1.1, y=1)
                                ))

    return fig.update_layout(template='plotly_dark',title_x=0.5,
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)')

@app.callback(
    Output(component_id='output-graph4SQLY', component_property='figure'),
    [Input(component_id='intermediate-valueSQLY', component_property='children')]
)
def equity(dat):
    chart = pl.from_pandas(pd.read_json(dat))
    date = chart.select(pl.col("dates")).to_series()
    asset_bar1 = go.Bar(y=chart.select(pl.col("Vốn góp")).to_series(), x=date, name="Vốn điều lệ",
                        marker=dict(color=('teal')))
    asset_bar2 = go.Bar(y=chart.select(pl.col("Lãi chưa phân phối")).to_series(), x=date, name="LN chưa phân phối",
                        marker=dict(color=('#A4DE02')))
    asset_bar3 = go.Bar(y=chart.select(pl.col("Cổ phiếu Quỹ")).to_series(), x=date,
                        name="Cổ phiếu quỹ", marker=dict(color=('pink')))
    asset_bar4 = go.Bar(y=chart.select(pl.col("other_equity")).to_series(), x=date,
                        name="Vốn khác", marker=dict(color=('green')))
    asset_bar5 = go.Bar(y=chart.select(pl.col("Phải trả người bán")).to_series(), x=date, name="Phải trả ngắn hạn",
                        marker=dict(color=('#FFFF99')))
    asset_bar6 = go.Bar(y=chart.select(pl.col("Vay ngắn hạn")).to_series(), x=date, name='Vay ngắn hạn',
                        marker=dict(color=('goldenrod')))
    asset_bar7 = go.Bar(y=chart.select(pl.col("Vay dài hạn")).to_series(), x=date, name="Vay dài hạn",
                        marker=dict(color=('rgb(200, 0, 0)')))
    asset_bar8 = go.Bar(y=chart.select(pl.col("bs_cust_pre")).to_series(), x=date, name="KH trả tiền trước",
                        marker=dict(color=('deeppink')))
    asset_bar9 = go.Bar(y=chart.select(pl.col("other_lia")).to_series(), x=date, name="Nợ khác",
                        marker=dict(color=('darkgray')))

    # asset_bar10 = go.Scatter(y=chart.select(pl.col("mc")).to_series(), x=date, name="Vốn hóa",
    #                          line=dict(color='darkturquoise', width=3), mode='lines+markers')
    asset_bar11 = go.Scatter(y=chart.select(pl.col("de")).to_series(), x=date, yaxis='y2', name="D/E",
                             line=dict(color='deeppink', width=3, dash='dot'), mode='lines',line_shape='spline')
    asset_data = [asset_bar1, asset_bar2, asset_bar3, asset_bar4, asset_bar5, asset_bar6, asset_bar7, asset_bar8,
                  asset_bar9, 
                #   asset_bar10, 
                  asset_bar11]

    fig = go.Figure(data=asset_data,layout=go.Layout(barmode='relative'
                                , xaxis=dict(tickformat='%Y', showgrid=False)
                                , yaxis2=go.layout.YAxis(showgrid=False, tickformat='.1%', overlaying='y',
                                                         side='right')
                                , yaxis=go.layout.YAxis(gridwidth=3  # ,hoverformat = '.1f'
                                                        )
                                , title='Cơ cấu nguồn vốn'
                                , legend=dict(x=1.1, y=1)
                                ))

    return fig.update_layout(template='plotly_dark',title_x=0.5,
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)')

@app.callback(
    Output(component_id='output-graph5SQLY', component_property='figure'),
    [Input(component_id='intermediate-valueSQLY', component_property='children')]
)
def growth(dat):
    chart = pl.from_pandas(pd.read_json(dat))
    date = chart.select(pl.col("dates")).to_series()
    g1 = go.Scatter(y=chart.select(pl.col("g_Doanh số thuần")).to_series(), x=date, name="Tăng trưởng doanh thu",
                    line=dict(color='teal', width=3), mode='lines+markers')
    g2 = go.Scatter(y=chart.select(pl.col("g_op")).to_series(), x=date, name="Tăng trưởng LN cốt lõi",
                    line=dict(color='rgb(191, 214, 48)', width=3), mode='lines+markers')
    g3 = go.Scatter(y=chart.select(pl.col("g_Lãi/(lỗ) thuần sau thuế")).to_series(), x=date, name="Tăng trưởng LNST",
                    line=dict(color='red', width=3), mode='lines+markers')
    g = [g1, g2, g3]
    fig = go.Figure(data=g, layout=go.Layout(barmode='relative'
                                                      , xaxis=dict(tickformat='%Y', showgrid=False)
                                                      , yaxis=go.layout.YAxis(showgrid=False, tickformat='.1%',
                                                                               overlaying='y'
                                                                               )

                                                      , title='Tăng trưởng'
                                                      , legend=dict(x=1.1, y=1)
                                                      ))

    return fig.update_layout(template='plotly_dark', title_x=0.5,
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)')

@app.callback(
    Output(component_id='output-graph6SQLY', component_property='figure'),
    [Input(component_id='intermediate-valueSQLY', component_property='children')]
)
def cf(dat):
    chart = pl.from_pandas(pd.read_json(dat))
    date = chart.select(pl.col("dates")).to_series()
    asset_bar1 = go.Bar(y=chart.select(pl.col("Lãi/(lỗ) thuần sau thuế")).to_series(), x=date, name="LNST",
                        marker=dict(color=('teal')))
    asset_bar2 = go.Bar(y=chart.select(pl.col("cf_dep")).to_series(), x=date, name="Khấu hao",
                        marker=dict(color=('#A4DE02')))
    asset_bar3 = go.Bar(y=chart.select(pl.col("Tiền thu từ phát hành cổ phiếu và vốn góp")).to_series(), x=date, name="Tăng vốn",
                        marker=dict(color='deeppink'))
    asset_bar4 = go.Bar(y=chart.select(pl.col("cf_div")).to_series(), x=date,
                        name="Cổ tức tiền mặt", marker=dict(color=('rgb(200, 0, 0)')))
    # asset_bar5 = go.Bar(y=chart.select(pl.col("cf_treasury")).to_series(), x=date, name="CP quỹ",
    #                     marker=dict(color=('goldenrod')))
    asset_bar6 = go.Bar(y=chart.select(pl.col("Tiền mua tài sản cố định và các tài sản dài hạn khác")).to_series(), x=date, name="Đầu tư TSCĐ",
                        marker=dict(color=('#FFFF99')))
    asset_bar7 = go.Bar(y=chart.select(pl.col("cf_khac")).to_series(), x=date, name='CF khác',
                        marker=dict(color=('darkgray')))
    asset_data = [asset_bar1, asset_bar2, asset_bar3, asset_bar4, 
    # asset_bar5, 
    asset_bar6,asset_bar7]

    fig = go.Figure(data=asset_data, layout=go.Layout(barmode='relative'
                                , xaxis=dict(tickformat='%Y')
                                # , yaxis2=go.layout.YAxis(showgrid=False, tickformat='.1%', title='D/A', overlaying='y',
                                #                          side='right')
                                , yaxis=go.layout.YAxis(gridwidth=3  # ,hoverformat = '.1f'
                                                        )
                                , title='Dòng tiền'
                                , legend=dict(x=1.1, y=1)
                                ))

    return fig.update_layout(template='plotly_dark',title_x=0.5,
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)')
@app.callback(
    Output(component_id='output-graph7SQLY', component_property='figure'),
    [Input(component_id='intermediate-valueSQLY', component_property='children')]
)
def pe(dat):
    chart = pl.from_pandas(pd.read_json(dat))
    date = chart.select(pl.col("dates")).to_series()
    bar1 = go.Scatter(y=chart.select(pl.col("Lãi/(lỗ) thuần sau thuế")).to_series(), x=date, name='LNST 4Q',
                      line=dict(color='red', width=3,dash='dot'), mode='lines',line_shape='spline')
    bar2 = go.Scatter(y=chart.select(pl.col("core_e")).to_series(), x=date, name='LNST cốt lõi 4Q',
                      line=dict(color='rgb(191, 214, 48)', width=3,dash='dot'), mode='lines',line_shape='spline')
    # bar3 = go.Scatter(y=chart.select(pl.col("mc")).to_series(), x=date, name="Vốn hóa (phải)",
    #                   line=dict(color='darkturquoise', width=3), mode='lines+markers', yaxis='y')
    # bar4 = go.Scatter(y=chart.select(pl.col("P/E")).to_series(), x=date, name="P/E (phải)",
    #                   line=dict(color='lavender', width=3),
    #                   mode='lines',line_shape='spline', yaxis='y2')

    data_PE = [bar1, bar2]
    # , bar3,bar4]
    fig = go.Figure(data=data_PE, layout=go.Layout(xaxis=dict(showgrid=False,tickformat='%Y')
                                , yaxis=go.layout.YAxis(gridwidth=3)
                                , yaxis_type='log'
                                , yaxis2=go.layout.YAxis(overlaying='y', side='right', showgrid=False
                                                         ,range=[0,30],)
                                , title='P/E'
                                , legend=dict(x=1.1, y=1)
                                ))

    return fig.update_layout(template='plotly_dark', title_x=0.5,
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)')

@app.callback(
    Output(component_id='output-graph8SQLY', component_property='figure'),
    [Input(component_id='intermediate-valueSQLY', component_property='children')]
)
def pb(dat):
    chart = pl.from_pandas(pd.read_json(dat))
    date = chart.select(pl.col("dates")).to_series()
    bar1 = go.Scatter(y=chart.select(pl.col("VỐN CHỦ SỞ HỮU")).to_series(), x=date, name='Giá trị số sách',
                      line=dict(color='lavender', width=3), mode='lines+markers')
    # bar2 = go.Scatter(y=chart.select(pl.col("mc")).to_series(), x=date, name='Vốn hóa',
    #                   line=dict(color='darkturquoise', width=3), mode='lines+markers')
    bar3 = go.Scatter(y=chart.select(pl.col("roe")).to_series(), x=date, name="ROE (phải)",
                      line=dict(color='red', width=3,dash='dot'), mode='lines',line_shape='spline', yaxis='y2')
    bar4 = go.Scatter(y=chart.select(pl.col("roe_core")).to_series(), x=date, name="ROE_core (phải)",
                      line=dict(color='rgb(191, 214, 48)', width=3,dash='dot'), mode='lines',line_shape='spline', yaxis='y2')

    data_PB = [bar1,
            #    bar2
                bar3, bar4]

    fig = go.Figure(data=data_PB, layout=go.Layout(xaxis=dict(showgrid=False,tickformat='%Y')
                                                   , yaxis=go.layout.YAxis(gridwidth=3)
                                                   , yaxis_type='log'
                                                   , yaxis2=go.layout.YAxis(overlaying='y', side='right',rangemode='tozero',
                                                                            showgrid=False,tickformat=".1%")
                                                   , title='P/B'
                                                   , legend=dict(x=1.1, y=1)
                                                   ))

    return fig.update_layout(template='plotly_dark', title_x=0.5,
                             plot_bgcolor='rgba(0, 0, 0, 0)',
                             paper_bgcolor='rgba(0, 0, 0, 0)')

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

if __name__ == '__main__':
   app.run_server(debug=True)


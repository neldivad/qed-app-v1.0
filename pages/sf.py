import streamlit as st
import streamlit.components.v1 as components
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

import pandas as pd
import numpy as np
import requests
import pytz 
from datetime import datetime

import plotly.graph_objs as go
import plotly.express as px

def sf_fundamentals():
    with st.sidebar:
        pass

    # ##########################
    # st.header('SimFin Fundamentals')
    st.subheader('Fundamental data')

    # Session state
    current_year= datetime.now(pytz.timezone('US/Eastern')).year
    sf_tickers = get_simfin_tickers()
    tickers = sf_tickers['Ticker']

    preset = st.selectbox('Select sector (if you don\'t know what to choose)', ['Big Tech', 'Banks', 'Fintech', 'Energy'], help= 'Autoselect a basket of tickers')
    if preset == 'Banks':
        sel_tickers = st.multiselect('Add/subtract ticker', tickers, ['BAC', 'WFC', 'JPM'], help= 'Data retrieved from SimFin API')
    if preset == 'Fintech':
        sel_tickers = st.multiselect('Add/subtract ticker', tickers, ['PYPL', 'V', 'MA'], help= 'Data retrieved from SimFin API')
    if preset == 'Big Tech':
        sel_tickers = st.multiselect('Add/subtract ticker', tickers, ['AAPL', 'MSFT', 'GOOG'], help= 'Data retrieved from SimFin API')
    if preset == 'Energy':
        sel_tickers = st.multiselect('Add/subtract ticker', tickers, ['XOM', 'CVX', 'VLO'], help= 'Data retrieved from SimFin API')

    col1, col2, col3 = st.columns([1,1,1]) 
    with col1:
        start_date = st.selectbox('Start date', [*range(current_year, 2000, -1)])
    with col2:
        end_date   = st.selectbox('End date', [*range(current_year, 2000, -1)])
    with col3:
        statement  = st.selectbox('Statement', ['Profit Loss', 'Balance Sheet', 'Cash Flow', 'Derived Ratios', 'All', ], help= 'Financial statement of your interest')

    if st.checkbox('Get fundamental data'): # You can't do nested forms
        if len(sel_tickers) > 10:
            st.warning("To preserve bandwidth, you can only select up to 10 tickers")
        elif end_date < start_date:
            st.warning('Error: End date must be larger than start date')
        else:
            state = ''
            if statement == 'Profit Loss':
                state = 'pl'
            elif statement == 'Balance Sheet':
                state = 'bs'
            elif statement == 'Cash Flow':
                state = 'cf'
            elif statement == 'Derived Ratios':
                state = 'derived'
            else:
                state = 'all'

            # Datatable
            with st.expander('Show data table', expanded=False):
                df = get_simfin_fundamental(
                    ticker_list= sel_tickers,
                    statement= state,
                    year_start= start_date,
                    year_end= end_date,
                )
                sub_df = subset_fundamental(df)
                AgGrid(df)
                AgGrid(sub_df)

            # Select column and make chart
            base_col = ['Ticker', 'Fiscal Year', 'Fiscal Period','Publish Date', 'Report Date']
            fin_ind = sub_df.columns.unique() 
            fin_ind = fin_ind.drop(base_col)

            with st.form(key='Select financial Indicator'):
                ydata = st.selectbox('Select financial indicator', fin_ind )
                if st.form_submit_button(label= 'Create chart'):
                    bear = [
                        ["2020-02-01", "2020-04-15"],
                        ["2021-11-01", "2022-1-15"],
                    ]
                    make_line_chart(
                        sub_df, 
                        xdata= sub_df['Report Date'], ydata= sub_df[ ydata ].astype(float), 
                        cdata= sub_df['Ticker'], bear_regime= bear)

    st.write('---')
    st.subheader('Price ratio data')
    if st.checkbox('Get price ratio data'):
        if len(sel_tickers) > 10:
            st.warning("To preserve bandwidth, you can only select up to 10 tickers")
        elif end_date < start_date:
            st.warning('Error: End date must be larger than start date')
        else:
            with st.expander('Show data table', expanded=False):
                prices = get_simfin_prices(
                    ticker_list=sel_tickers,
                    year_start= start_date,
                    year_end= end_date,
                )
                sub_prices = subset_prices(prices)
                AgGrid(prices)
                AgGrid(sub_prices)

            base_price_col = ['Ticker', 'Date', 'High', 'Low', 'Adj. Close', 'Volume']
            price_ind = sub_prices.columns.unique() 
            price_ind = price_ind.drop(base_price_col)

            with st.form(key='Select Price Indicator'):
                ydata = st.selectbox('Select price indicator', price_ind)
                if st.form_submit_button(label= 'Create chart'):
                    bear = [
                        ["2020-02-01", "2020-04-15"],
                        ["2021-11-01", "2022-1-15"],
                    ]
                    make_line_chart(
                        sub_prices, 
                        xdata= sub_prices['Date'], ydata= sub_prices[ ydata ].astype(float),
                        cdata= sub_prices['Ticker'], bear_regime= bear)

                    make_price_spread(
                        sub_prices, 
                        xdata= sub_prices['Date'], 
                        cdata= sub_prices['Ticker'], 
                        bear_regime= bear, ind= 'Earnings & Revenue'
                    )
                    make_price_spread(
                        sub_prices, 
                        xdata= sub_prices['Date'], 
                        cdata= sub_prices['Ticker'], 
                        bear_regime= bear, ind= 'Earnings', expand=False
                    )
                    make_price_spread(
                        sub_prices, 
                        xdata= sub_prices['Date'], 
                        cdata= sub_prices['Ticker'], 
                        bear_regime= bear, ind= 'Revenue', expand= False
                    )
                    


#--------------------------
# Helper function
#-------------------------
def make_line_chart(df, xdata, ydata, cdata, bear_regime):
    with st.expander('Show Line chart', expanded=True):
        fig = px.line(
            df, x= xdata, y= ydata, 
            color= cdata, 
            )

        for date in bear_regime:
            fig.add_vrect(
                x0= date[0], 
                x1= date[1], 
                line_width=0, 
                fillcolor="red", 
                opacity=0.1
            )
        # Add figure title
        fig.update_layout(
            title_text= f'<b>{ydata.name}</b>'
        )
        fig.update_layout(
            showlegend=True, 
            # hovermode="x unified",
        )
        fig.update_xaxes(range= [ xdata.values.min(), xdata.values.max() ])
        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                    ])
            )
        )

        labels_to_show_in_legend = cdata.unique()[:3] # Display only the first 2 ticker as default
        for trace in fig['data']: 
            if (not trace['name'] in labels_to_show_in_legend):
                trace['visible'] = 'legendonly'
        
        if ydata.name == 'Altman Z Score (ttm)':
            fig.add_hline(y= 3,line_dash= 'dot')  
        if ydata.name != 'Altman Z Score (ttm)':
            fig.add_hline(y= 0,line_dash= 'dot') 
              
        st.plotly_chart(fig)
        st.markdown('*Click on the legend to plot the graph of the asset price in the current year.*')

def make_price_spread(df, xdata, cdata, bear_regime, ind= 'Earnings', expand= True):
    if ind == 'Earnings':
        indicator = ['Price to Earnings Ratio (ttm)', 'EV/EBITDA (ttm)']
    if ind == 'Revenue':
        indicator = ['Price to Sales Ratio (ttm)', 'EV/Sales (ttm)',]
    if ind == 'Earnings & Revenue': 
        indicator = ['EV/Sales (ttm)','EV/EBITDA (ttm)']
    
    temp = df[indicator]

    with st.expander(f"Price ratios: {ind}", expanded=expand):
        fig = px.line(
            df,
            x= xdata,
            y= temp.columns.values,
            color= cdata,
        )

        for date in bear_regime:
            fig.add_vrect(
                x0= date[0], 
                x1= date[1], 
                line_width=0, 
                fillcolor="red", 
                opacity=0.1
            )
        fig.add_hline(
            y= 0,
            line_dash= 'dot',
            )

        fig.update_layout(hovermode="x unified",)
        fig.update_yaxes(title_text=f'<b>Price Ratio Spread</b>')
        fig.update_xaxes(title_text='', range= [ xdata.values.min(), xdata.values.max() ])
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                    ])
            )
        )
        labels_to_show_in_legend = cdata.unique()[:1] # Display only the first ticker's spread for default
        for trace in fig['data']: 
            if (not trace['name'] in labels_to_show_in_legend):
                trace['visible'] = 'legendonly'

        st.plotly_chart(fig)
        st.markdown('> *Shaded region = bear regime*')


#############################
# Helper functions
#############################
@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None, 'builtins.weakref': lambda _: None})
def get_simfin_tickers():
    api_key = st.secrets['sf_api_key']
    data = requests.get(f'https://simfin.com/api/v2/companies/list?api-key={api_key}').json()
    df = pd.DataFrame.from_dict(data['data'], orient='columns')
    df.columns= data['columns']
    return df

@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None, 'builtins.weakref': lambda _: None})
def get_simfin_prices(ticker_list, year_start= None, year_end= None):
    """
    """
    import pytz 
    from datetime import datetime

    current_year= datetime.now(pytz.timezone('US/Eastern')).year
    if year_end is None:
        year_end = current_year

    if year_start is None:
        year_start = year_end -1

    api_key = st.secrets['sf_api_key']
    columns = [] # variable to store the names of the columns
    output  = [] # variable to store our datas
    req_url = 'https://simfin.com/api/v2/companies/prices'

    parameters = {"ticker": ",".join(ticker_list), "ratios": '&ratios', 'start':f'{year_start}-01-01', 'end':f'{year_end}-12-31', "api-key": api_key}
    request = requests.get(req_url, parameters)
    all_data = request.json()
    
    for response_index, data in enumerate(all_data):
        if data['found'] and len(data['data']) > 0:
            if len(columns) == 0:
                columns = data['columns']
            output += data['data']

    df = pd.DataFrame(output, columns=columns)
    return df


@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None, 'builtins.weakref': lambda _: None})
def get_simfin_fundamental(ticker_list, statement='pl', year_start= None, year_end= None):
    """
    req_url      : String input. URL to request data from SimFin+ API. 
    ticker_list  : List input. List of tickers to pass
    statement    : String input. Options include "pl", "bs", "cf", "derived", "all"
    year_start   : Integer input. Defaults to current year.
    year_end     : Integet input. Defaults to current year

    Documentation link https://simfin.com/api/v2/documentation/#tag/Company/paths/~1companies~1statements/get
    """
    import pytz 
    from datetime import datetime

    current_year= datetime.now(pytz.timezone('US/Eastern')).year
    if year_end is None:
        year_end = current_year

    if year_start is None:
        year_start = year_end -1

    api_key = st.secrets['sf_api_key']
    columns = [] # variable to store the names of the columns
    output  = [] # variable to store our datas
    req_url = 'https://simfin.com/api/v2/companies/statements'

    parameters = {"statement": statement, "ticker": ",".join(ticker_list), "period": "quarters", "fyear": ",".join([str(x) for x in list(range(year_start,year_end+1))]), "api-key": api_key}
    request = requests.get(req_url, parameters)
    all_data = request.json()
    
    for response_index, data in enumerate(all_data):
        if data['found'] and len(data['data']) > 0:
            if len(columns) == 0:
                columns = data['columns']
            output += data['data']

    df = pd.DataFrame(output, columns=columns)
    return df

def subset_fundamental(df):
    cols = [
        'Ticker', 'Fiscal Year', 'Fiscal Period','Publish Date', 'Report Date',
        'Revenue', 'Cost of Revenue', 'Operating Expense', 'Selling & Marketing', 'General & Administrative', 'Research & Development', 'Operating Income (Loss)', 'Non-Operating Income (Loss)', 'Gross Profit', 'Net Income',
        'Cash & Cash Equivalents', 'Short Term Investments', 'Accounts & Notes Receivable', 'Inventories', 
        'Total Current Assets', 'Total Noncurrent Assets', 'Total Assets', 
        'Accounts Payable', 'Total Current Liabilities', 'Total Noncurrent Liabilities', 'Total Liabilities', 
        'Retained Earnings', 'Total Equity', 
        'Stock-Based Compensation', 'EBITDA', 'Total Debt', 'Free Cash Flow', 
        'Gross Profit Margin', 'Operating Margin', 'Net Profit Margin',
        'Return on Equity', 'Return on Assets', 'Free Cash Flow to Net Income', 
        'Current Ratio', 'Liabilities to Equity Ratio', 'Debt Ratio', 
        'Piotroski F-Score', 'Return On Invested Capital', 'Net Debt / EBITDA', 'Net Debt / EBIT'
        ]
    subset = []
    for col in df.columns:
        if col in cols:
            subset.append(col)
    
    sub_df = df[subset]
    sub_df.index = sub_df['Publish Date']
    return sub_df

def subset_prices(df):
    cols = [
        'Date', 'Ticker', 'High', 'Low', 'Adj. Close', 'Volume', 'Market-Cap', 'Enterprise Value (ttm)',
        'Price to Earnings Ratio (quarterly)', 'Price to Earnings Ratio (ttm)', 
        'Price to Sales Ratio (quarterly)', 'Price to Sales Ratio (ttm)', 
        'Price to Free Cash Flow (quarterly)', 'Price to Free Cash Flow (ttm)', 
        'EV/EBITDA (ttm)', 'EV/Sales (ttm)', 'EV/FCF (ttm)', 'Altman Z Score (ttm)',
    ]
    subset = []
    for col in df.columns:
        if col in cols:
            subset.append(col)
    
    sub_df = df[subset]
    sub_df = sub_df.reindex(columns= cols)
    sub_df.index = sub_df['Date']
    return sub_df

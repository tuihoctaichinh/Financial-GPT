import os
import sys
# Add the parent directory of mypackage to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apps.config import *
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

## STOCK LISTING
def live_stock_list ():
    """
    Return a DataFrame of all available stock symbols. Live data is retrieved from the API.
    """
    url = "https://wifeed.vn/api/thong-tin-co-phieu/danh-sach-ma-chung-khoan"
    response = requests.request("GET", url).json()
    df = pd.DataFrame(response['data'])
    # rename columns fullname_vi to companyName, code to ticker, loaidn to companyType, san to exchange
    df = df.rename(columns={'fullname_vi': 'organName', 'code': 'ticker', 'loaidn': 'organTypeCode', 'san': 'comGroupCode'})
    return df

def organ_listing (lang='vi', headers=ssi_headers):
    """
    Return a DataFrame of all available stock symbols. Live data is retrieved from the SSI API.
    Parameters:
        lang (str): language of the data. Default is 'vi', other options are 'en'
        headers (dict): headers of the request
    """
    url = f"https://fiin-core.ssi.com.vn/Master/GetListOrganization?language={lang}"
    response = requests.request("GET", url, headers=headers)
    status = response.status_code
    if status == 200:
        data = response.json()
        # print('Total number of companies: ', data['totalCount'])
        df = pd.DataFrame(data['items'])
        return df
    else:
        print('Error in API response', response.text)

def indices_listing (lang='vi', headers=ssi_headers):
    """
    Return a DataFrame of all available indices. Live data is retrieved from the SSI API.
    Parameters:
        lang (str): language of the data. Default is 'vi', other options are 'en'
        headers (dict): headers of the request
    """
    url = f"https://fiin-core.ssi.com.vn/Master/GetAllCompanyGroup?language={lang}"
    response = requests.request("GET", url, headers=headers)
    status = response.status_code
    if status == 200:
        data = response.json()
        df = pd.DataFrame(data['items'])
        df = df.sort_values(by='comGroupOrder').reset_index(drop=True)
        df = df[['comGroupCode', 'parentComGroupCode', 'comGroupOrder']]
        return df
    else:
        print('Error in API response', response.text)

def offline_stock_list (path='https://raw.githubusercontent.com/thinh-vu/vnstock/beta/data/listing_companies_enhanced-2023.csv'):
    """
    This function returns the list of all available stock symbols from a csv file, which is stored on Github.
    Parameters: 
        path (str): The path of the csv file to read from. Default is the path of the file 'listing_companies_enhanced-2023.csv'. You can find the latest updated file at `https://github.com/thinh-vu/vnstock/tree/main/src`
    Returns: df (DataFrame): A pandas dataframe containing the stock symbols and other information. 
    """
    df = pd.read_csv(path)
    return df

def listing_companies (live=False, source='Wifeed'):
    """
    This function returns the list of all available stock symbols from a csv file or a live api request.
    Parameters: 
        live (bool): If True, return the list of all available stock symbols from a live api request. If False, return the list of all available stock symbols from the Github csv file (monthly update). Default is False.
    Returns: df (DataFrame): A pandas dataframe containing the stock symbols and other information. 
    """
    # if live = True, return live_stock_list(), else return offline_stock_list()
    if live == True:
        if source == 'Wifeed':
            df = live_stock_list()
        elif source == 'SSI':
            df = organ_listing()
    elif live == False:
        df = offline_stock_list()
    return df

# COMPANY OVERVIEW
def company_overview (symbol):
    """
    This function returns the company overview of a target stock symbol
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/overview').json()
    df = json_normalize(data)
    # Rearrange columns
    df = df[['ticker', 'exchange', 'industry', 'companyType',
            'noShareholders', 'foreignPercent', 'outstandingShare', 'issueShare',
            'establishedYear', 'noEmployees',  
            'stockRating', 'deltaInWeek', 'deltaInMonth', 'deltaInYear', 
            'shortName', 'industryEn', 'industryID', 'industryIDv2', 'website']]
    return df

# RECENTLY ADDED -------

def company_profile (symbol='TCB', headers=tcbs_headers):
    """
    Return a DataFrame of company overview data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/overview"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response)
    df['ticker'] = symbol
    # convert text from html to plain text for all columns in the df, add error handling
    for col in df.columns:
        try:
            df[col] = df[col].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text())
            df[col] = df[col].str.replace('\n', ' ')
        except:
            pass
    return df

def company_large_shareholders (symbol='TCB', headers=tcbs_headers):
    """
    Return a DataFrame of company large share holders data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/large-share-holders"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response['listShareHolder'])
    df['ticker'] = symbol
    # rename columns 'name' to shareHolder, ownPercent to shareOwnPercent
    df.rename(columns={'name': 'shareHolder', 'ownPercent': 'shareOwnPercent'}, inplace=True)
    df.drop(columns=['no'], inplace=True)
    return df

def company_fundamental_ratio (symbol='TCB', mode='simplify', missing_pct=0.8, headers=tcbs_headers):
    """
    Return a DataFrame of company tooltip data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    mode (str): 'simplify' or '', default is 'simplify' which return only data points with values, if set to '', return all columns.
    missing_pct (float): a float number between 0 and 1, default is 0.8, which means remove all columns from df that have more than 80% missing values.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/finance/{symbol}/tooltip"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response)
    df['ticker'] = symbol
    # move ticker column to the front
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]
    # if mode = 'simplify', filter out all columns contain 'Name' in their values, otherwise if value set to '', return all columns
    if mode == 'simplify':
        df = df.loc[:,~df.columns.str.contains('Name')]
    # Remove all columns from df that have more than 80% missing values.
    df = df.loc[:, df.isnull().mean() < missing_pct]
    return df

def ticker_price_volatility (symbol='TCB', headers=tcbs_headers):
    """
    Return a DataFrame of ticker price volatility data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/price-volatility"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response)
    # add ticker_ as the prefix to all columns except ticker column
    df.columns = ['ticker_' + col if col != 'ticker' else col for col in df.columns]
    return df

def company_insider_deals (symbol='TCB', page_size=20, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of company insider trading data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    size (int): number of items per page, default is 20.
    page (int): page number, default is 0.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/insider-dealing?page={page}&size={page_size}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response['listInsiderDealing'])
    df.drop(columns=['no'], inplace=True)
    # rename columns anDate to dealAnnounceDate, dealingMethod to dealMethod, dealingAction to dealAction, quantity to dealQuantity, price to dealPrice, dealRatio
    df.rename(columns={'anDate': 'dealAnnounceDate', 'dealingMethod': 'dealMethod', 'dealingAction': 'dealAction', 'quantity': 'dealQuantity', 'price': 'dealPrice', 'ratio': 'dealRatio'}, inplace=True)
    # convert dealAnnounceDate column to datetime format, keep the same format as 'd/m/y'
    df['dealAnnounceDate'] = pd.to_datetime(df['dealAnnounceDate'], format='%d/%m/%y')
    # sort the DataFrame by dealAnnounceDate column
    df.sort_values(by='dealAnnounceDate', ascending=False, inplace=True)
    # replace value of dealMethod column, 1 with 'Cổ đông lớn', 2 with 'Cổ đông sáng lập', 0 with Cổ đông nội bộ
    df['dealMethod'].replace({1: 'Cổ đông lớn', 2: 'Cổ đông sáng lập', 0: 'Cổ đông nội bộ'}, inplace=True)
    # replace value of dealAction column, 1 with 'Bán', 0 with 'Mua'
    df['dealAction'].replace({'1': 'Bán', '0': 'Mua'}, inplace=True)
    return df



def company_officers (symbol='TCB', page_size=20, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of company officers data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    page_size (int): number of records per page, default is 20, can be increased to 100 or so.
    page (int): page number, default is 0.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{symbol}/key-officers?page={page}&size={page_size}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = json_normalize(response['listKeyOfficer'])
    df['ticker'] = symbol
    df.drop(columns=['no'], inplace=True)
    # rename companyName to subCompanyName, ownPercent to subCompanyOwnPercent
    df.rename(columns={'name': 'officerName', 'position': 'officerPosition', 'ownPercent':'officerOwnPercent'}, inplace=True)
    # sort by officerOwnPercent
    df.sort_values(by=['officerOwnPercent', 'officerPosition'], ascending=False, inplace=True)
    return df

def company_events (symbol='TPB', page_size=15, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of ticker events data.
    Parameters:
    ticker (str): ticker of the company, default is 'TPB', other tickers available can be obtained from the function `listing_companies()`.
    page_size (int): number of records per page, default is 15, can be increased to 100 or so.
    page (int): page number, default is 0. You can increase the page number to get more events.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/events-news?page={page}&size={page_size}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = pd.DataFrame(response['listEventNews'])
    return df

def company_news (symbol='TCB', page_size=15, page=0, headers=tcbs_headers):
    """
    Return a DataFrame of ticker news data.
    Parameters:
    ticker (str): ticker of the company, default is 'TCB', other tickers available can be obtained from the function `listing_companies()`.
    page_size (int): number of records per page, default is 15, can be increased to 100 or so.
    page (int): page number, default is 0. You can increase the page number to get more news.
    """
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/activity-news?page={page}&size={page_size}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    df = pd.DataFrame(response['listActivityNews'])
    df['ticker'] = symbol
    return df

# FINANCIAL REPORT
## Financial report from SSI
def financial_report (symbol='SSI', report_type='BalanceSheet', frequency='Quarterly', periods=200, latest_year=None, headers=ssi_headers): # Quarterly, Yearly
    """
    Return financial reports of a stock symbol by type and period.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        report_type (:obj:`str`, required): BalanceSheet, IncomeStatement, CashFlow
        report_range (:obj:`str`, required): Yearly or Quarterly.
    """
    symbol = symbol.upper()
    organ_code = organ_listing().query(f'ticker == @symbol')['organCode'].values[0]
    this_year = str(datetime.now().year)
    if latest_year == None:
      latest_year = this_year
    else:
      if isinstance(latest_year, int) != True:
        print('Please input latest_year as int number')
      else:
        pass
    url = f'https://fiin-fundamental.ssi.com.vn/FinancialStatement/Download{report_type}?language=vi&OrganCode={organ_code}&Skip=0&Frequency={frequency}&numberOfPeriod={periods}&latestYear={latest_year}'
    response = requests.get(url, headers=headers)
    # print(response.text)
    status = response.status_code
    if status == 200:
        df = pd.read_excel(BytesIO(response.content), skiprows=7).dropna()
        return df
    else:
        print(f'Error {status} when getting data from SSI. Details:\n {response.text}')
        return None

## report from TCBS
def financial_flow(symbol='TCB', report_type='incomestatement', report_range='quarterly', get_all=True): # incomestatement, balancesheet, cashflow | report_range: 0 for quarterly, 1 for yearly
    """
    This function returns the quarterly financial ratios of a stock symbol. Some of expected ratios are: priceToEarning, priceToBook, roe, roa, bookValuePerShare, etc
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        report_type (:obj:`str`, required): select one of 3 reports: incomestatement, balancesheet, cashflow.
        report_range (:obj:`str`, required): yearly or quarterly.
    """
    if report_range == 'yearly':
        range = 1
    elif report_range == 'quarterly':
        range = 0
    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/finance/{symbol}/{report_type}', params={'yearly': range, 'isAll': get_all}).json()
    df = json_normalize(data)
    df[['year', 'quarter']] = df[['year', 'quarter']].astype(str)
    # if report_range == 'yearly' then set index to df['year'], else set index to df['year'] + df['quarter']
    if report_range == 'yearly':
        df['index'] = df['year']
    elif report_range == 'quarterly':
        df['index'] = df['year'].str.cat('-Q' + df['quarter'])
    df = df.set_index('index').drop(columns={'year', 'quarter'})
    return df

def financial_ratio_compare (symbol_ls=["CTG", "TCB", "ACB"], industry_comparison=True, frequency='Yearly', start_year=2010, headers=ssi_headers): 
    """
    This function returns financial report of a stock symbol by type and period.
    Args:
        symbol (:obj:`str`, required): ["CTG", "TCB", "ACB"].
        industry_comparison (:obj: `str`, required): "True" or "False"
        frequency (:obj:`str`, required): Yearly or Quarterly.
        start_year (:obj:`str`, required): Enter the start year of the report.
    """
    global timeline
    if frequency == 'Yearly':
        timeline = str(start_year) + '_5'
    elif frequency == 'Quarterly':
        timeline = str(start_year) + '_4'

    list_len = len(symbol_ls)
    if list_len == 1:
        url = f'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/DownloadFinancialRatio2?language=vi&OrganCode={symbol_ls[0]}&CompareToIndustry={industry_comparison}&Frequency={frequency}&Ratios=ryd21&Ratios=ryd25&Ratios=ryd14&Ratios=ryd7&Ratios=rev&Ratios=isa22&Ratios=ryq44&Ratios=ryq14&Ratios=ryq12&Ratios=rtq51&Ratios=rtq50&Ratios=ryq48&Ratios=ryq47&Ratios=ryq45&Ratios=ryq46&Ratios=ryq54&Ratios=ryq55&Ratios=ryq56&Ratios=ryq57&Ratios=nob151&Ratios=casa&Ratios=ryq58&Ratios=ryq59&Ratios=ryq60&Ratios=ryq61&Ratios=ryd11&Ratios=ryd3&TimeLineFrom={timeline}'.format(symbol_ls[0], industry_comparison, '', frequency, timeline)
    elif  list_len > 1:
        main_symbol = symbol_ls[0]
        company_join = '&CompareToCompanies=' + '&CompareToCompanies='.join(symbol_ls[1:])
        url = f'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/DownloadFinancialRatio2?language=vi&OrganCode={main_symbol}&CompareToIndustry={industry_comparison}{company_join}&Frequency={frequency}&Ratios=ryd21&Ratios=ryd25&Ratios=ryd14&Ratios=ryd7&Ratios=rev&Ratios=isa22&Ratios=ryq44&Ratios=ryq14&Ratios=ryq12&Ratios=rtq51&Ratios=rtq50&Ratios=ryq48&Ratios=ryq47&Ratios=ryq45&Ratios=ryq46&Ratios=ryq54&Ratios=ryq55&Ratios=ryq56&Ratios=ryq57&Ratios=nob151&Ratios=casa&Ratios=ryq58&Ratios=ryq59&Ratios=ryq60&Ratios=ryq61&Ratios=ryd11&Ratios=ryd3&TimeLineFrom={timeline}'
    r = requests.get(url, headers=headers)
    df = pd.read_excel(BytesIO(r.content), skiprows=7)
    # drop rows with all NaN values
    df = df.dropna(how='all')
    # drop all rows with Chỉ số columns contain Dữ liệu được cung cấp bởi FiinTrade or https://fiintrade.vn/
    df = df[~df['Chỉ số'].str.contains('Dữ liệu được cung cấp bởi FiinTrade')]
    df = df[~df['Chỉ số'].str.contains('https://fiintrade.vn/')]
    return df


# STOCK FILTERING

def financial_ratio (symbol, report_range, is_all=False):
    """
    This function retrieves the essential financial ratios of a stock symbol on a quarterly or yearly basis. Some of the expected ratios include: P/E, P/B, ROE, ROA, BVPS, etc
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
        report_range (:obj:`str`, required): 'yearly' or 'quarterly'.
        is_all (:obj:`boo`, required): Set to True to retrieve all available years of data,  False to retrieve the last 5 years data (or the last 10 quarters). Default is True.
    """
    if report_range == 'yearly':
        x = 1
    elif report_range == 'quarterly':
        x = 0
    
    if is_all == True:
      y = 'true'
    else:
      y = 'false'

    data = requests.get(f'https://apipubaws.tcbs.com.vn/tcanalysis/v1/finance/{symbol}/financialratio?yearly={x}&isAll={y}').json()
    df = json_normalize(data)
    # drop nan columns
    df = df.dropna(axis=1, how='all')
    #if report_range == 'yearly' then set index column to be df['year'] and drop quarter column, else set index to df['year'] + df['quarter']
    if report_range == 'yearly':
        df = df.set_index('year').drop(columns={'quarter'})
    elif report_range == 'quarterly':
        # add prefix 'Q' to quarter column
        df['quarter'] = 'Q' + df['quarter'].astype(str)
        # concatenate quarter and year columns
        df['range'] = df['quarter'].str.cat(df['year'].astype(str), sep='-')
        # move range column to the first column
        df = df[['range'] + [col for col in df.columns if col != 'range']]
        # set range column as index
        df = df.set_index('range')
    df = df.T
    return df


def dividend_history (symbol):
    """
    This function returns the dividend historical data of the seed stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{}/dividend-payment-histories?page=0&size=20'.format(symbol)).json()
    df = json_normalize(data['listDividendPaymentHis']).drop(columns=['no', 'ticker'])
    return df


## STOCK RATING
def  general_rating (symbol):
    """
    This function returns a dataframe with all rating aspects for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/general?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data).drop(columns='stockRecommend')
    return df

def biz_model_rating (symbol):
    """
    This function returns the business model rating for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/business-model?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df

def biz_operation_rating (symbol):
    """
    This function returns the business operation rating for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/business-operation?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df

def financial_health_rating (symbol):
    """
    This function returns the financial health rating for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/financial-health?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df


def valuation_rating (symbol):
    """
    This function returns the valuation rating for the desired stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/valuation?fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df


def industry_financial_health (symbol):
    """
    This function returns the industry financial health rating for the seed stock symbol.
    Args:
        symbol (:obj:`str`, required): 3 digits name of the desired stock.
    """
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/{}/financial-health?fType=INDUSTRY'.format(symbol)).json()
    df = json_normalize(data)
    return df


# RECENTLY ADDED -------

def stock_evaluation (symbol='ACB', period=1, time_window='D', headers=tcbs_headers):
    """
    Return a DataFrame contains the stock evaluation data of the ticker.
    Parameters:
    symbol (str): ticker of the company, default is 'ACB', other tickers available can be obtained from the function `listing_companies()`.
    period (int): period of the stock evaluation, default is 1. All available: '1' (1 year), '3' (3 years), '5' (5 years)
    time_window (str): time window of the stock evaluation, default is 'D'. All available: 'D' (1 day), 'W' (1 week). For period = 1, time_window = 'D' or 'W', otherwise time_window = 'W'.
    """
    # create url to get stock evaluation data
    url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/evaluation/{symbol}/historical-chart?period={period}&tWindow={time_window}"
    # get stock evaluation data
    response = requests.get(url, headers=headers).json()
    # convert json to dataframe
    df = pd.DataFrame(response['data'])
    # rename columns: pe to PE, pb to PB, industryPe to Industry PE, industryPb to Industry PB, indexPe to VNIndex PE, indexPb to VNIndex PB
    df.rename(columns={'pe': 'PE', 'pb': 'PB', 'industryPe': 'industryPE', 'industryPb': 'industryPB', 'indexPe': 'vnindexPE', 'indexPb': 'vnindexPB', 'from': 'fromDate', 'to': 'toDate'}, inplace=True)
    # add ticker value to the dataframe
    df['ticker'] = symbol
    # move ticker column to the first column
    df = df[['ticker', 'fromDate', 'toDate', 'PE', 'PB', 'industryPE', 'vnindexPE', 'industryPB', 'vnindexPB']]
    # convert fromDate and toDate to datetime
    df['fromDate'] = pd.to_datetime(df['fromDate'])
    df['toDate'] = pd.to_datetime(df['toDate'])
    return df

#get company name from ticker, source: SSI organization listing
def get_companyname(ticker,lang): 
    org_listing = organ_listing(lang)
    try:
        org_name = org_listing[org_listing['ticker']==ticker.upper()]['organName']
        org_name = org_name.values[0]
        return org_name
    except:
        return None

#get company industry from ticker, source: SSI ICB industry listing
def get_industry(ticker,lang): 
    try:
        org_listing = organ_listing(lang)
        org_icbCode = org_listing[org_listing['ticker']==ticker.upper()]['icbCode']
        org_icbCode = org_icbCode.values[0]
        url = f'https://fiin-core.ssi.com.vn/Master/GetAllIcbIndustry?language=en'
        response = requests.get(url,headers=ssi_headers)
        response.json()
        df = pd.DataFrame(response.json()['items'])
        industry = df[df['icbCode']==org_icbCode]['icbName'].values[0]
        return industry
    except:
        return None

# get market cap of the company by multiplying the close price with the number of shares
def get_mc(ticker,period='Q'): 
    # Get SSI's org code from ticker
    org_listing = organ_listing()
    org_code = org_listing[org_listing['ticker']==ticker]['organCode']
    org_code = org_code.values[0]

    #------------------------------------------------------------------------------------#
    # Crawl data number of shares from SSI
    # insert url
    url=f'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/GetFinancialRatioV2?language=vi&Type=Company&OrganCode={org_code}&Timeline=2006_4&Timeline=2007_1&Timeline=2007_2&Timeline=2007_3&Timeline=2007_4&Timeline=2008_1&Timeline=2008_2&Timeline=2008_3&Timeline=2008_4&Timeline=2009_1&Timeline=2009_2&Timeline=2009_3&Timeline=2009_4&Timeline=2010_1&Timeline=2010_2&Timeline=2010_3&Timeline=2010_4&Timeline=2011_1&Timeline=2011_2&Timeline=2011_3&Timeline=2011_4&Timeline=2012_1&Timeline=2012_2&Timeline=2012_3&Timeline=2012_4&Timeline=2013_1&Timeline=2013_2&Timeline=2013_3&Timeline=2013_4&Timeline=2014_1&Timeline=2014_2&Timeline=2014_3&Timeline=2014_4&Timeline=2015_1&Timeline=2015_2&Timeline=2015_3&Timeline=2015_4&Timeline=2016_1&Timeline=2016_2&Timeline=2016_3&Timeline=2016_4&Timeline=2017_1&Timeline=2017_2&Timeline=2017_3&Timeline=2017_4&Timeline=2018_1&Timeline=2018_2&Timeline=2018_3&Timeline=2018_4&Timeline=2019_1&Timeline=2019_2&Timeline=2019_3&Timeline=2019_4&Timeline=2020_1&Timeline=2020_2&Timeline=2020_3&Timeline=2020_4&Timeline=2021_1&Timeline=2021_2&Timeline=2021_3&Timeline=2021_4&Timeline=2022_1&Timeline=2022_2&Timeline=2022_3&Timeline=2022_4&Timeline=2023_1&Timeline=2023_2&Timeline=2023_3&Timeline=2023_4&Timeline=2024_1&Timeline=2024_2&Timeline=2024_3&Timeline=2024_4'

    # Define the headers
    headers = ssi_headers
    # Make the request
    response = requests.get(url, headers=headers)

    # Check the response
    if response.status_code == 200:
        print("Success!")
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

    df = pd.DataFrame(response.json()['items'])
    df

    #------------------------------------------
    # find column name of number of shares data
    x=df.iloc[[5],:]['value']

    #convert x to df, where headers are the keys of the dictionary, 
    y = pd.DataFrame(x.to_dict())

    # rename cols to ratio and value
    y.rename(columns={'5':'value'}, inplace=True)

    y['value']=y.iloc[4:,0]/10**9
    y[np.abs(y.iloc[:,1]-29112.72)<1] # find the row where the value is 29112.72 

    df1=pd.DataFrame(df['value'])

    # convert each cell from df1 to dataframe
    df2 = pd.DataFrame(df1['value'].to_dict())
    df2=df2.T
    df_numberOfShares=df2[['yearReport','lengthReport','ryd3']]

    #rename cols y to year, quarter and numberOfShares
    df_numberOfShares.rename(columns={'yearReport':'year','lengthReport':'quarter','ryd3':'numberOfShares'}, inplace=True)
    df_numberOfShares

    #------------------------------------------------------------------------------------#
    # Crawl data close prices from cafef
    url2=f'https://s.cafef.vn/Ajax/PageNew/DataHistory/PriceHistory.ashx?Symbol={ticker}&StartDate=&EndDate=&PageIndex=1&PageSize=200000'

    # use request to get the data
    response2 = requests.get(url2)
    response2.text

    x=response2.json()['Data']
    x2=pd.DataFrame(x['Data'])

    # create column year, month, date based on col 'Ngay'
    x2['year']=x2['Ngay'].apply(lambda x: x.split('/')[2])
    x2['month']=x2['Ngay'].apply(lambda x: x.split('/')[1])
    x2['date']=x2['Ngay'].apply(lambda x: x.split('/')[0])
    x2['year']=x2['year'].astype(int)
    x2['month']=x2['month'].astype(int)
    x2['date']=x2['date'].astype(int)

    #find the lastest trading day of each quarter
    x2['quarter']=x2['month'].apply(lambda x: (x-1)//3+1)
    x2['quarter']
    #filter the lastest trading day of each quarter basd on the quarter and date columns, filter months 3,6,9,12
    x3=x2[(x2['month']==3) | (x2['month']==6) | (x2['month']==9) | (x2['month']==12)]
    x4=x3.groupby(['year','quarter']).apply(lambda x: x[x['date']==x['date'].max()])

    #convert x4['GiaDongCua'] to df
    df_closePrice = pd.DataFrame(x4['GiaDongCua'])*(10**3)
    
    # turn index of y to columns
    df_closePrice.reset_index(inplace=True)
    # delete the 3rd column
    df_closePrice.drop(columns=['level_2'], inplace=True)
    # rename the col 'GiaDongCua' to 'closePrice'
    df_closePrice.rename(columns={'GiaDongCua':'closePrice'}, inplace=True)
    
    #------------------------------------------------------------------------------------#
    # Merge df NumberOfShares and ClosePrice into df_mc
    df_mc_Q=pd.merge(df_numberOfShares,df_closePrice, on=['year','quarter'])
    df_mc_Q['marketCap']=df_mc_Q['numberOfShares']*df_mc_Q['closePrice']
    # add a column for quarter and year, in the format of 'Q12020', based on cols 'year' and 'quarter', by turning values 'quarter' into Q1, Q2, Q3, Q4
    df_mc_Q['quarter']=df_mc_Q['quarter'].apply(lambda x: 'Q'+str(x))
    df_mc_Q['year']=df_mc_Q['year'].astype(str)
    df_mc_Q['period']=df_mc_Q['quarter']+df_mc_Q['year']
    #move col 'quarterYear' to the first col
    cols = df_mc_Q.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df_mc_Q = df_mc_Q[cols]
    #drop cols 'year' and 'quarter'
    df_mc_Q.drop(columns=['year','quarter'], inplace=True)
    #turn quarterYear to index
    #df_mc_Q.set_index('quarterYear', inplace=True)
    if period=='Q':
        return df_mc_Q
    else:
        #keep only the tuples for Q4 of each year
        df_mc_Y=df_mc_Q[df_mc_Q['period'].str.contains('Q4')]
        #remove 'Q4' from the index
        df_mc_Y['period']=df_mc_Y['period'].str.replace('Q4','')
        # rename index to Year
        #df_mc_Y.index.rename('Year', inplace=True)
        return df_mc_Y


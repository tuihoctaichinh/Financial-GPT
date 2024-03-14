import os
import sys
# Add the parent directory of mypackage to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apps.config import *
from apps.fundamental import *
import polars as pl
import pyodbc


list_chitieu = ['TỔNG TÀI SẢN','TÀI SẢN NGẮN HẠN','Tiền và tương đương tiền','Giá trị thuần đầu tư ngắn hạn','Các khoản phải thu','Hàng tồn kho, ròng','TÀI SẢN DÀI HẠN','Phải thu dài hạn','Tài sản cố định','GTCL TSCĐ hữu hình','Nguyên giá TSCĐ hữu hình','Khấu hao lũy kế TSCĐ hữu hình','GTCL Tài sản thuê tài chính','Nguyên giá tài sản thuê tài chính','Khấu hao lũy kế tài sản thuê tài chính','GTCL tài sản cố định vô hình','Nguyên giá TSCĐ vô hình','Khấu hao lũy kế TSCĐ vô hình','Bất động sản đầu tư','Nguyên giá tài sản đầu tư','Khấu hao lũy kế tài sản đầu tư','Tài sản dở dang dài hạn','Đầu tư dài hạn',
                'NỢ PHẢI TRẢ','Nợ ngắn hạn','Phải trả người bán','Người mua trả tiền trước','Doanh thu chưa thực hiện ngắn hạn','Vay ngắn hạn','Nợ dài hạn','Người mua trả tiền trước dài hạn','Doanh thu chưa thực hiên','Vay dài hạn','Trái phiếu chuyển đổi','VỐN CHỦ SỞ HỮU','Vốn góp','Thặng dư vốn cổ phần','Cổ phiếu Quỹ','Lãi chưa phân phối','Lợi ích cổ đông không kiểm soát','Doanh số thuần','Lãi gộp','Thu nhập tài chính','Chi phí tài chính','Trong đó: Chi phí lãi vay','Lãi/(lỗ) từ công ty liên doanh','Chi phí bán hàng','Chi phí quản lý doanh  nghiệp','Thu nhập khác, ròng','Lãi/(lỗ) ròng trước thuế','Lãi/(lỗ) thuần sau thuế','Lợi nhuận của Cổ đông của Công ty mẹ',
                'Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh','Khấu hao TSCĐ',
                # 'Chi phí dự phòng','Chi phí lãi vay','Chi phí lãi vay đã trả','Thuế thu nhập doanh nghiệp đã trả',
                'Lưu chuyển tiền tệ ròng từ hoạt động đầu tư','Tiền mua tài sản cố định và các tài sản dài hạn khác','Tiền thu được từ thanh lý tài sản cố định','Cổ tức và tiền lãi nhận được','Lưu chuyển tiền tệ từ hoạt động tài chính','Tiền thu từ phát hành cổ phiếu và vốn góp','Chi trả cho việc mua lại, trả lại cổ phiếu','Tiền thu được các khoản đi vay','Tiển trả các khoản đi vay','Tiền thanh toán vốn gốc đi thuê tài chính','Cổ tức đã trả'
]
def add_ratios_Q(x):
    x = x[list_chitieu]
    x['bs_cash'] = x['Tiền và tương đương tiền'] + x['Giá trị thuần đầu tư ngắn hạn']
    x['bs_ar'] = x['Các khoản phải thu'] + x['Phải thu dài hạn']
    x['bs_fa'] = x['GTCL TSCĐ hữu hình'] + x['GTCL Tài sản thuê tài chính'] + x['GTCL tài sản cố định vô hình'] + x['Bất động sản đầu tư'] 
    x['bs_gross_fa'] = x['Nguyên giá TSCĐ hữu hình'] + x['Nguyên giá tài sản thuê tài chính'] + x['Nguyên giá TSCĐ vô hình'] + x['Nguyên giá tài sản đầu tư']
    x['other_asset'] = (x['TỔNG TÀI SẢN'] - x['bs_cash'] - x['bs_ar'] - x['Hàng tồn kho, ròng'] - x['bs_fa'] - x['Tài sản dở dang dài hạn']-x['Đầu tư dài hạn'])
    x['bs_cust_pre'] = x['Doanh thu chưa thực hiện ngắn hạn'] + x['Doanh thu chưa thực hiên'] + x['Người mua trả tiền trước'] + x['Người mua trả tiền trước dài hạn']
    x['debt'] = x['Vay ngắn hạn'] + x['Vay dài hạn'] + x['Trái phiếu chuyển đổi']
    x['other_lia'] = (x['NỢ PHẢI TRẢ'] - x['debt'] - x['Phải trả người bán'] - x['bs_cust_pre'])
    x['other_equity'] = (x['VỐN CHỦ SỞ HỮU'] - x['Vốn góp'] - x['Lãi chưa phân phối'] - x['Cổ phiếu Quỹ'])
    x['netdebt'] = (x['debt'] - x['bs_cash'])
    x['ca/ta'] = x['TÀI SẢN NGẮN HẠN']/(1+x['TỔNG TÀI SẢN'])
    x['de'] = x['debt']/(1+x['VỐN CHỦ SỞ HỮU'])

    x['tax_rate'] = 1-(x['Lãi/(lỗ) thuần sau thuế']/(1+x['Lãi/(lỗ) ròng trước thuế']))
    x['op'] = (x['Lãi gộp'] + x['Chi phí bán hàng'] + x['Chi phí quản lý doanh  nghiệp'])
    x['core_e'] = x['op'] * (1 - x['tax_rate'])
    x['fin_income'] = x['Thu nhập tài chính'] + (x['Chi phí tài chính'] - x['Trong đó: Chi phí lãi vay'])
    x['EBT'] = x['op'] + x['Trong đó: Chi phí lãi vay']
    
   
    x['cf_div'] = x['Cổ tức đã trả'] + x['Chi trả cho việc mua lại, trả lại cổ phiếu']
    x['cf_delta_debt'] = x['Tiền thu được các khoản đi vay'] + x['Tiển trả các khoản đi vay'] + x['Tiền thanh toán vốn gốc đi thuê tài chính']
    x['cf_dep'] = x['Khấu hao TSCĐ'] 
    # + x['Chi phí dự phòng']
    x['cf_khac'] = (x['Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh']+x['Lưu chuyển tiền tệ ròng từ hoạt động đầu tư']+x['Lưu chuyển tiền tệ từ hoạt động tài chính']) - (x['Lãi/(lỗ) thuần sau thuế']+x['cf_dep']+x['Tiền mua tài sản cố định và các tài sản dài hạn khác']+x['Tiền thu từ phát hành cổ phiếu và vốn góp']+x['cf_delta_debt']+x['cf_div'])
    
    x['operating_EBITDA'] = x['op']+x['cf_dep']
    x['EBITDA'] = (x['Lãi/(lỗ) ròng trước thuế']-x['Thu nhập khác, ròng'] + x['cf_dep'] - x['Trong đó: Chi phí lãi vay'])


    return x

col1 = ['Lãi gộp', 'op', 'EBT', 'Lãi/(lỗ) ròng trước thuế', 'Lãi/(lỗ) thuần sau thuế', 'Lợi nhuận của Cổ đông của Công ty mẹ', 'core_e','EBITDA']
col3 = ['Doanh số thuần', 'Lãi gộp', 'op', 'EBT', 'Lãi/(lỗ) ròng trước thuế', 'Lãi/(lỗ) thuần sau thuế', 'Lợi nhuận của Cổ đông của Công ty mẹ', 'core_e','EBITDA']
col2 = ['Doanh số thuần', 'Lãi gộp', 'op', 'EBT', 'Lãi/(lỗ) ròng trước thuế', 'Lãi/(lỗ) thuần sau thuế', 'Lợi nhuận của Cổ đông của Công ty mẹ', 'core_e','EBITDA', 
        'Doanh số thuần_4Q', 'Lãi gộp_4Q', 'op_4Q','Lãi/(lỗ) ròng trước thuế', 'Lãi/(lỗ) thuần sau thuế_4Q', 'Lợi nhuận của Cổ đông của Công ty mẹ_4Q', 'core_e_4Q','EBITDA_4Q']
def margin_func(x):
    for i in col1:
        x[i + "_m"] = x[i] / (1+x['Doanh số thuần'])
    return x

def ttm(x):
    for i in col3:
        x[i + "_4Q"] = x[i].rolling(4, min_periods=4).sum()
    return x

def g_func(x):
    for i in col2:
        x["g_" + i] = x[i].pct_change(periods=3) 
    x['roe_4Q'] = x['Lãi/(lỗ) thuần sau thuế_4Q']/x['VỐN CHỦ SỞ HỮU'].rolling(4, min_periods=4).mean()
    x['roe_core_4Q'] = x['core_e_4Q']/x['VỐN CHỦ SỞ HỮU'].rolling(4, min_periods=4).mean()
    x['roa_4Q'] = x['Lãi/(lỗ) thuần sau thuế_4Q']/x['TỔNG TÀI SẢN'].rolling(4, min_periods=4).mean()
    return x

def get_fs_Q(ticker):
    bs = financial_report(ticker,'BalanceSheet','Quarterly')
    # bs = bs.loc[:, (bs==0).mean() < .6]
    pl = financial_report(ticker,'IncomeStatement','Quarterly')
    # pl = pl.loc[:, (pl==0).mean() < .6]
    cf = financial_report(ticker,'CashFlow','Quarterly')
    cf = cf.rename(columns={'Unnamed: 0': 'CHỈ TIÊU'})
    cf.set_index('CHỈ TIÊU', inplace=True)
    cf2 = pd.DataFrame(index = {'Khấu hao TSCĐ':'CHỈ TIÊU'}, columns = cf.columns).fillna(0)
    if cf2.index[0] in cf.index:
        pass
    else:
        cf = pd.concat([cf,cf2],axis=0)
    cf = cf.reset_index().rename(columns={'index': 'CHỈ TIÊU'})

    fs = pd.concat([bs,pl,cf])
    #delete all the column with NaN value > 40
    fs = fs.dropna(axis=1,thresh=40)
    fs = fs.T
    fs.columns = fs.iloc[0]
    fs = fs.iloc[1:,:]
    #Dropping rows if more than half of the values are zeros 
    # fs = fs.loc[fs.isna().sum(axis=1)<50]

    fs = add_ratios_Q(fs)
    fs = margin_func(fs)
    fs = ttm(fs)
    fs = g_func(fs)
    fs['year'] = fs.index.str[-4:].astype(int)
    fs['quarter'] = fs.index.str[1].astype(float)
    fs['dates'] = pd.PeriodIndex(year=fs["year"], quarter=fs["quarter"])
    fs['dates'] = fs['dates'].dt.to_timestamp(freq='Q')
    fs = fs.sort_values(by='dates')
    return fs


def get_data_Q(ticker):
    x = get_fs_Q(ticker)
    x = pl.from_pandas(x)
    # y = get_mc(ticker)
    # x = pl.concat([y,x],how='align')
    # x = x.with_columns((pl.col('mc')/pl.col('Lãi/(lỗ) thuần sau thuế_4Q')).alias('P/E'))
    # x = x.with_columns((pl.col('mc')/pl.col('VỐN CHỦ SỞ HỮU')).alias('P/B'))
    x = x.with_columns([(pl.col('dates').dt.strftime("%Y-%m")).alias('dates')])
    return x
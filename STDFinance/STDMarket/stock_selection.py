'''
Ref: http://www.shenqigongshi.com/realtime-intro

原选股逻辑：
1. 对公司质量进行排序 
    - 以合并财报资本收益率为基准
    - 资本收益率=息税前利润/(净运营资本 + 固定资产)
2. 对公司价格进行排序
    - 以合并财报股票收益率为基准
    - 股票收益率=息税前利润/企业价值
    - (企业价值 = 总市值 + 其他权益工具 + 带息债务 + 少数股东权益)
3. 得到质优价廉的公司 
    - 1和2两排名相加得综合排名，排名越小，表示综合质量越高
    - 根据实时选股名单，买入排名靠前的30-80只股票

代码输出：
    一个excel文件（stock_selection.xlsx)内含三列：
        - stock：股票代码
        - date：财报截止日期【以下数据用的是个股截止21年9月30日的财报数据】
        - rank：综合排名（若出现.5，表示计算排名的时候，对于同样数值的行排名取平均数，比如2个相同数值出现在第一名之后，这2两个相同数值的排名取（2+3）/2 = 2.5名。
'''
import pandas as pd

# 数据来源于国泰安，选21Q3数据（21Q4数据有许多缺省），人工找数据并在excel里进行预处理。
# 暂时没有找到自动化找数的好方法。
# 已尝试：
# ---Tushare积分要800+才能获取财报指标数据，初始用户只有100积分，要积分需加入讨论或打钱。
# ---国泰安API需要账户、密码才能接入，但学校账号是集体账号，不支持。
# ---网易财经数据年度数据只更新到09年。
fp_prefix = 'stock_selection_'
fp_suffix = ['dy.csv', 'ebit.csv', 'nwc.csv']
data_fps = [fp_prefix + s for s in fp_suffix]


def data_prep(data_fps=data_fps):
    '''
    资本收益率ROA=息税前利润/(净运营资本 + 固定资产)
    股票收益率DY=息税前利润/企业价值

    输入：
    输出：一个pd.DataFrame，列由股票代码stock、资本收益率roa、股票收益率dy组成。
    '''
    data = pd.DataFrame()
    for fp in data_fps:
        temp = pd.read_csv(
            fp, parse_dates=['date'], dtype={'stock': 'string'}, index_col=['stock', 'date'])
        # temp['stock'] = temp['stock'].
        # temp.set_index(['stock', 'date'])
        data = pd.concat([temp, data], axis=1)
    data['roa'] = data['ebit'] / data['ta-cl']
    return data


def quality_rank(df):
    '''1. 对公司质量进行排序 
    - 以财报资本收益率为基准
    - 资本收益率=息税前利润/(净运营资本 + 固定资产)

    输入：一个pd.DataFrame
    输出：在输入pd.DataFrame的基础上新加一列以roa为key进行排序得到的排名(列名：QR)
    '''
    df['QR'] = df['roa'].rank()
    return df


def price_rank(df):
    '''2. 对公司价格进行排序
    - 以财报股票收益率为基准
    - 股票收益率=息税前利润/企业价值
    - (企业价值 = 总市值 + 其他权益工具 + 带息债务 + 少数股东权益)

    输入：一个pd.DataFrame
    输出：在输入pd.DataFrame的基础上新加一列以dy为key进行排序得到的排名(列名：PR)
    '''
    df['PR'] = df['dy'].rank()
    return df


def final_rank(df):
    '''3. 得到质优价廉的公司 
    - 1和2两排名相加得综合排名，排名越小，表示综合质量越高
    - 根据实时选股名单，买入排名靠前的30-80只股票

    输入：一个pd.DataFrame（df）
    处理：
        - 在输入df的基础上新加一列QR与PR相加得到的排名(列名：QR+PR)；
        - 将df以"QR+PR"为key进行排序，得到综合排名（列明：Rank）
    输出：处理过的df
    '''
    df['QR+PR'] = df['QR'] + df['PR']
    df['Rank'] = df['QR+PR'].rank()
    return df.sort_values(by=['Rank'], ascending=True)


if __name__ == '__main__':
    df = data_prep()
    df = quality_rank(df)
    print(df.head())
    df = price_rank(df)
    print(df.head())
    df = final_rank(df)
    print(df.head())
    # df.index[0] = df.index[0].astype(str).str.zfill(6)
    # Output stocks and their final ranks.
    df['Rank'].to_excel('stock_selection.xlsx')

import pandas as pd
from io import BytesIO, StringIO 
import requests, zipfile
from pandas_datareader import data as pdr
import numpy as np
from scipy import stats
import yfinance as yf
import datetime as datetime
import calendar
from dateutil.relativedelta import relativedelta
from dateutil import parser
from sklearn import linear_model
import holidays
import statsmodels.api as sm
import boto3
yf.pdr_override() # <== that's all it takes :-)

from decouple import config
import os

zip_file_url ='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'

def convertDateFormat(indexDate):
	return datetime.datetime.strptime(str(int(indexDate)), '%Y%m%d').strftime('%Y-%m-%d')

def getAIFData():
	AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
	AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
	AWS_DATA_LOCATION = config('AWS_DATA_LOCATION')

	client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
	        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	

	object_key = AWS_DATA_LOCATION + '/data.csv'
	csv_obj = client.get_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=object_key)
	body = csv_obj['Body']
	csv_string = body.read().decode('utf-8')
	df = pd.read_csv(StringIO(csv_string), skiprows=2, usecols=['Date', 'NAV'], index_col='Date')
	df.drop(df.tail(1).index,inplace=True)
	print(df.index)
	# df.index = df.index.apply(convertDateFormat)
	df.index = pd.to_datetime(df.index.map(lambda x : convertDateFormat(x)))
	print(df)
	return df

aifNAVdata = getAIFData()


def get_daily_returns_df(prices):
    return ((prices / prices.shift(1) - 1).dropna())

def securities_year_to_date_return(securities, weights):
	endDate = datetime.datetime.today()
	while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
		endDate = endDate - datetime.timedelta(days=1)
	endEndDate = endDate + datetime.timedelta(days=1)
	
	startDate = datetime.datetime(endDate.year - 1, 12, 31)
	while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
	  	startDate = startDate - datetime.timedelta(days=1)
	startEndDate = startDate + datetime.timedelta(days=1)
	print(str(startDate))
	print(str(startEndDate))
	print(str(endDate))
	print(str(endEndDate))
	# print(datetime.date(2020, 1, 20) in holidays.US(years=[startDate.year, endDate.year]))
	# print(holidays.US(years=[startDate.year, endDate.year]))
	
	
	beg = pdr.get_data_yahoo(securities, start=startDate.strftime('%Y-%m-%d'), end=startEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
	print(beg)
	end = pdr.get_data_yahoo(securities, start=endDate.strftime('%Y-%m-%d'), end=endEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
	# allSecuritiesAllData = pdr.get_data_yahoo(securities, start=dateStart.strftime('%Y-%m-%d'), end=dateEnd.strftime('%Y-%m-%d'),  as_panel = False)
	print(end)

	allSecuritiesAllData = pd.concat([beg['Adj Close'], end['Adj Close']])
	print(allSecuritiesAllData)
	w = weights * get_daily_returns_df(allSecuritiesAllData)
	if(isinstance(w, pd.DataFrame)):
		w = w.sum(axis = 1, skipna = True)

	print(w)
	print("YTD: " + str(w[0]))
	ret = w[0]
	return '{:.1%}'.format(ret)

def portfolio_year_to_date_return():
	endDate = datetime.datetime.today()
	while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
		endDate = endDate - datetime.timedelta(days=1)

	startDate = datetime.datetime(endDate.year - 1, 12, 31)
	while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
	  	startDate = startDate - datetime.timedelta(days=1)

	# print(str(startDate))
	# print(str(endDate))
	# print(aifNAVdata[-60:])
	# print(aifNAVdata.index)
	print(aifNAVdata.loc[startDate.strftime('%Y-%m-%d')])
	print(aifNAVdata.loc[endDate.strftime('%Y-%m-%d')])
	ret = aifNAVdata.loc[endDate.strftime('%Y-%m-%d')][0] / aifNAVdata.loc[startDate.strftime('%Y-%m-%d')][0] - 1
	print("YTD: " + str(ret))
	return '{:.1%}'.format(ret)

def security_total_return(securities, entry_price, entry_date, exit_price, exit_date):
	if (entry_price is None) or (exit_price is None):
		if entry_price is None:
			startDate = parser.parse(entry_date)
			startEndDate = startDate + datetime.timedelta(days=1)
			beg = pdr.get_data_yahoo(securities, start=startDate.strftime('%Y-%m-%d'), end=startEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
			entry_price = beg['Adj Close'][0]

		if exit_price is None:
			endDate = startDate = parser.parse(exit_date)
			while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
				endDate = endDate - datetime.timedelta(days=1)
			endEndDate = endDate + datetime.timedelta(days=1)
			end = pdr.get_data_yahoo(securities, start=endDate.strftime('%Y-%m-%d'), end=endEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
			exit_price = end['Adj Close'][0]
	print(entry_price)
	print(exit_price)
	print(exit_price/entry_price - 1)
	ret = (exit_price/entry_price - 1)
	return '{:.1%}'.format(ret)
	# allSecuritiesAllData = pdr.get_data_yahoo(securities, start=dateStart.strftime('%Y-%m-%d'), end=dateEnd.strftime('%Y-%m-%d'),  as_panel = False)
	

def portfolio_total_return(securities, weights, startDate, endDate): #need to fix this with csv data
	startDate = datetime.datetime.today()
	startEndDate = startDate + datetime.timedelta(days=1)
	endDate = datetime.datetime(startDate.year - 1, 12, 31)
	while(endDate.weekday() > 4):
		endDate = endDate - datetime.timedelta(days=1)
	endEndDate = endDate + datetime.timedelta(days=1)
	beg = pdr.get_data_yahoo(securities, start=startDate.strftime('%Y-%m-%d'), end=startEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
	end = pdr.get_data_yahoo(securities, start=endDate.strftime('%Y-%m-%d'), end=endEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
	# allSecuritiesAllData = pdr.get_data_yahoo(securities, start=dateStart.strftime('%Y-%m-%d'), end=dateEnd.strftime('%Y-%m-%d'),  as_panel = False)

	allSecuritiesAllData = pd.concat([end['Adj Close'], beg['Adj Close']])
	w = weights * get_daily_returns_df(allSecuritiesAllData)
	if(isinstance(w, pd.DataFrame)):
		w = w.sum(axis = 1, skipna = True)
	# print(w[0])
	return w[0]

def one_year_risk_adjusted_return(threeFactor, securities, weights):
	r = requests.get(zip_file_url, stream=True)
	z = zipfile.ZipFile(BytesIO(r.content))
	dailydf = pd.read_csv(z.open('F-F_Research_Data_5_Factors_2x3_daily.CSV'), skiprows=3)[-300:]
	dailydf = dailydf.rename(columns={"Unnamed: 0": "Date"})

	dailydf.index = [datetime.datetime.strptime(str(date_num), '%Y%m%d') for date_num in dailydf['Date'].tolist()]
	dailydf = dailydf.drop(columns=['Date'])

	last_index = dailydf.index[-1]
	endDate = datetime.datetime(last_index.year, last_index.month, calendar.monthrange(last_index.year, last_index.month)[1])
	startDate = last_index - relativedelta(years=1)
	allSecuritiesAllData = pdr.get_data_yahoo(securities, start=startDate.strftime('%Y-%m-%d'), end=endDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
	# allSecuritiesAllData = pdr.get_data_yahoo(securities, start=dateStart.strftime('%Y-%m-%d'), end=dateEnd.strftime('%Y-%m-%d'),  as_panel = False)
	allSecuritiesAllData = allSecuritiesAllData['Adj Close'][1:]
	w = weights * get_daily_returns_df(allSecuritiesAllData)
	if isinstance(w, pd.DataFrame):
		dailyPortfolioReturns = pd.DataFrame(w.sum(axis=1, skipna=True), columns=["Daily Portfolio Returns"])
	else:
		dailyPortfolioReturns = pd.DataFrame(w.values, columns=["Daily Portfolio Returns"], index=w.index)
	dfjoin = dailydf.join(dailyPortfolioReturns).dropna()

	portfolioExcessReturns = pd.DataFrame(dfjoin['Daily Portfolio Returns'].values - dfjoin['RF'].values, columns=['RP-RF'], index=dailyPortfolioReturns.index.values.flatten())
	portfolioExcessReturns
	dfjoin = dfjoin.join(portfolioExcessReturns).drop(columns=['Daily Portfolio Returns', 'RF'])

	if threeFactor:
		factors = dfjoin.columns.tolist()[0:-4]
	else:
		factors = dfjoin.columns.tolist()[0:-2]

	X = dfjoin[factors] 
	Y = dfjoin['RP-RF']
	 
	# with sklearn
	regression = linear_model.LinearRegression()
	regression.fit(X, Y)
	print('Intercept: \n', regression.intercept_)
	print('Coefficients: \n', regression.coef_)
	ret = regression.intercept_
	return '{:.1%}'.format(ret)

# one_year_risk_adjusted_return(True, securities=['SPY', 'LYV', 'HXL'], weights=[1/3, 1/3, 1/3])
# one_year_risk_ adjusted_return(True, securities=['HXL'], weights=[1])
# securities_year_to_date_return(securities=['HXL'], weights=[1])
portfolio_year_to_date_return()

# security_total_return(securities=['HXL'], entry_price=None, entry_date="2020-01-03", exit_price=None, exit_date="2020-01-17")
# security_total_return(securities=['HXL'], entry_price=None, entry_date="2020-01-03", exit_price=78.18, exit_date="2020-01-17")
# security_total_return(securities=['HXL'], entry_price=75.35, entry_date="2020-01-03", exit_price=78.18, exit_date="2020-01-17")
# security_total_return(securities=['HXL'], entry_price=75.35, entry_date="2020-01-03", exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d'))
# getAIFData()
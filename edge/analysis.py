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
import json
from pytz import timezone
yf.pdr_override() # <== that's all it takes :-)

from decouple import config
import os
from django.conf import settings

zip_file_url ='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'

def convertDateFormat(indexDate):
	return datetime.datetime.strptime(str(int(indexDate)), '%Y%m%d').strftime('%Y-%m-%d')

def getAIFData():
	# data_AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
	# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
	# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
	# AWS_DATA_LOCATION = config('AWS_DATA_LOCATION')

	client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
	        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

	

	object_key = settings.AWS_DATA_LOCATION + '/data.csv'
	csv_obj = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_key)
	body = csv_obj['Body']
	csv_string = body.read().decode('utf-8')
	df = pd.read_csv(StringIO(csv_string), skiprows=2, usecols=['Date', 'NAV'], index_col='Date')
	df.drop(df.tail(1).index,inplace=True)
	# print(df.index)
	# df.index = df.index.apply(convertDateFormat)
	df.index = pd.to_datetime(df.index.map(lambda x : convertDateFormat(x)))
	# print(df)
	return df

aifNAVdata = getAIFData()

def AIFNAVDataForTemplate():
	# print(len(aifNAVdata.values.flatten().tolist()))
	return json.dumps(aifNAVdata.values.flatten().tolist())

def AIFIndexDataForTemplate():
	# print(aifNAVdata.index)
	index = pd.Series(aifNAVdata.index).map(lambda x : x.strftime('%m-%d-%Y'))
	# print(index.values.tolist())
	# print(json.dumps(index.values.tolist()))
	# print(len(index.values.tolist()))
	return json.dumps(index.values.tolist())

def get_daily_returns_df(prices):
    return ((prices / prices.shift(1) - 1).dropna())

def securities_year_to_date_return(securities, weights):
	eastern = timezone('US/Eastern')
	endDate = datetime.datetime.now(eastern)
	
	beforeMondayDayEnd = endDate.hour < 17 and endDate.weekday() == 0
	if beforeMondayDayEnd:
		endDate = datetime.datetime.today() - datetime.timedelta(days=1)

	while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
		print(endDate)
		endDate = endDate - datetime.timedelta(days=1)
	endEndDate = endDate + datetime.timedelta(days=1)
	
	startDate = datetime.datetime(endDate.year - 1, 12, 31)
	while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
	  	startDate = startDate - datetime.timedelta(days=1)
	startEndDate = startDate + datetime.timedelta(days=1)
	print("securities_year_to_date_return :" + str(startDate))
	print("securities_year_to_date_return :" + str(startEndDate))
	print("securities_year_to_date_return :" + str(endDate))
	print("securities_year_to_date_return :" + str(endEndDate))
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
	print("securities_year_to_date_return :" + str(w[0]))
	ret = w[0]
	return '{:.1%}'.format(ret)

def portfolio_year_to_date_return():
	endDate = aifNAVdata.index[len(aifNAVdata) - 1]
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
	print("Portfolio YTD: " + str(ret))
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

			eastern = timezone('US/Eastern')
			now = datetime.datetime.now(eastern)
			beforeMondayDayEnd = now.hour < 17 and now.weekday() == 0 and endDate.weekday() == 0
			if beforeMondayDayEnd:
				endDate = datetime.datetime.today() - datetime.timedelta(days=1)

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
	

def portfolio_one_year_return():
	endDate = aifNAVdata.index[len(aifNAVdata) - 1]
	startDate = endDate - relativedelta(years=1)
	while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
	  	startDate = startDate - datetime.timedelta(days=1)

	print(aifNAVdata.loc[startDate.strftime('%Y-%m-%d')])
	print(aifNAVdata.loc[endDate.strftime('%Y-%m-%d')])
	ret = aifNAVdata.loc[endDate.strftime('%Y-%m-%d')][0] / aifNAVdata.loc[startDate.strftime('%Y-%m-%d')][0] - 1
	print("Total portfolio return: " + str(ret))
	return '{:.1%}'.format(ret)


# Find RAR of a portfolio constructed from AIF's NAV
def one_year_risk_adjusted_return_from_NAV(threeFactor):
	r = requests.get(zip_file_url, stream=True)
	z = zipfile.ZipFile(BytesIO(r.content))
	dailyFactorDF = pd.read_csv(z.open('F-F_Research_Data_5_Factors_2x3_daily.CSV'), skiprows=3)[-300:]
	dailyFactorDF = dailyFactorDF.rename(columns={"Unnamed: 0": "Date"})

	dailyFactorDF.index = [datetime.datetime.strptime(str(date_num), '%Y%m%d') for date_num in dailyFactorDF['Date'].tolist()]
	dailyFactorDF = dailyFactorDF.drop(columns=['Date'])

	last_index = dailyFactorDF.index[-1]
	endDate = datetime.datetime(last_index.year, last_index.month, calendar.monthrange(last_index.year, last_index.month)[1])
	startDate = last_index - relativedelta(years=1)
	while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
	  	startDate = startDate - datetime.timedelta(days=1)
	print(startDate)
	print(endDate)

	dailyPortfolioReturns = get_daily_returns_df(aifNAVdata[startDate.strftime('%Y-%m-%d'):endDate.strftime('%Y-%m-%d')])
	dailyPortfolioReturns = pd.DataFrame(dailyPortfolioReturns.values, columns=["Daily Portfolio Returns"], index=dailyPortfolioReturns.index) * 100
	# print(dailyPortfolioReturns)
	dfjoin = dailyFactorDF.join(dailyPortfolioReturns).dropna()
	print(dfjoin)
	portfolioExcessReturns = pd.DataFrame(dfjoin['Daily Portfolio Returns'].values - dfjoin['RF'].values, columns=['RP-RF'], index=dfjoin.index.values.flatten())
	# print(portfolioExcessReturns)
	dfjoin = dfjoin.join(portfolioExcessReturns).drop(columns=['Daily Portfolio Returns', 'RF'])
	print(dfjoin)
	if threeFactor:
		factors = dfjoin.columns.tolist()[0:3]
	else:
		factors = dfjoin.columns.tolist()[0:5]

	print(factors)
	X = dfjoin[factors] 
	Y = dfjoin['RP-RF']
	# print(X)
	# print(Y)
	 
	# with sklearn
	regression = linear_model.LinearRegression()
	regression.fit(X, Y)
	print('Intercept: \n', regression.intercept_)
	print('Coefficients: \n', regression.coef_)
	ret = regression.intercept_ * 365 / 100
	return '{:.1%}'.format(ret)

# Find RAR of a portfolio constructed from individual stock info from Yahoo Finance
def one_year_risk_adjusted_return_from_securities(threeFactor, securities, weights):
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
# portfolio_year_to_date_return()
# portfolio_total_return(datetime.datetime.strptime('2019-12-31', '%Y-%m-%d'), datetime.datetime.strptime('2020-02-07', '%Y-%m-%d'))
# portfolio_total_return(datetime.datetime.strptime('2020-02-03', '%Y-%m-%d'), datetime.datetime.strptime('2020-02-07', '%Y-%m-%d'))
one_year_risk_adjusted_return_from_NAV(True)
# AIFIndexDataForTemplate()
# AIFNAVDataForTemplate()
# security_total_return(securities=['HXL'], entry_price=None, entry_date="2020-01-03", exit_price=None, exit_date="2020-01-17")
# security_total_return(securities=['HXL'], entry_price=None, entry_date="2020-01-03", exit_price=78.18, exit_date="2020-01-17")
# security_total_return(securities=['HXL'], entry_price=75.35, entry_date="2020-01-03", exit_price=78.18, exit_date="2020-01-17")
# security_total_return(securities=['HXL'], entry_price=75.35, entry_date="2020-01-03", exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d'))
# getAIFData()
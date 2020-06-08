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

# from decouple import config
# import os
from django.conf import settings

class Data():
	"""docstring for Data"""
	def __init__(self):
		self.zip_file_url ='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'
		self.data = self._get_data()

	def _convert_date_format(self, indexDate):
		return datetime.datetime.strptime(str(int(indexDate)), '%Y%m%d').strftime('%Y-%m-%d')

	def _get_data(self):
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
		
		df.index = pd.to_datetime(df.index.map(lambda x : self._convert_date_format(x)))
		# print(df)
		return df

	def dashboard_as_of(self):
		# print(self.data.index[-1].strftime('%m-%d-%Y'))
		return self.data.index[-1].strftime('%m-%d-%Y')

	def pitch_as_of(self):
		eastern = timezone('US/Eastern')
		endDate = datetime.datetime.now(eastern)
		
		beforeMondayDayEnd = endDate.hour < 17 and endDate.weekday() == 0
		if beforeMondayDayEnd:
			endDate = datetime.datetime.today() - datetime.timedelta(days=1)
		# print(self.data.index[-1].strftime('%m-%d-%Y'))
		return endDate.strftime('%m-%d-%Y')

	def aif_nav_data_for_template(self, time_horizon_params):
		ret = None
		if time_horizon_params:
			endDate = self.data.index[len(self.data) - 1]
			startDate = endDate - relativedelta(**time_horizon_params)
			while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
			  	startDate = startDate - datetime.timedelta(days=1)

			print(self.data.loc[startDate.strftime('%Y-%m-%d')])
			print(self.data.loc[endDate.strftime('%Y-%m-%d')])
			time_series = self.data.loc[startDate.strftime('%Y-%m-%d'):endDate.strftime('%Y-%m-%d')]
			print("TIME SERIES")
			print(time_series)
			time_series.index = time_series.index.strftime('%m-%d-%Y')
			ret = time_series["NAV"].to_dict()
		else:
			time_series = self.data.loc[:]
			print("TIME SERIES")
			print(time_series)
			time_series.index = time_series.index.strftime('%m-%d-%Y')
			ret = time_series["NAV"].to_dict()
		# print(len(navs.values.flatten().tolist()))
		# print(navs)
		# print(json.dumps(navs.values.flatten().tolist()))
		# print(ret)

		return ret

	def get_current_price(self, securities):
		eastern = timezone('US/Eastern')
		endDate = datetime.datetime.now(eastern)
		
		beforeMondayDayEnd = endDate.hour < 17 and endDate.weekday() == 0
		if beforeMondayDayEnd:
			endDate = datetime.datetime.today() - datetime.timedelta(days=1)

		while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
			print(endDate)
			endDate = endDate - datetime.timedelta(days=1)
		endEndDate = endDate + datetime.timedelta(days=1)

		end = pdr.get_data_yahoo(securities, start=endDate.strftime('%Y-%m-%d'), end=endEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
		ret = end['Adj Close'][0]
		print("get_current_price: " + str(ret))
		return round(ret, 2)


	def get_daily_returns_df(self, prices):
	    return ((prices / prices.shift(1) - 1).dropna())

	def securities_year_to_date_return(self, securities, weights):
		print('start')
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

		allSecuritiesAllData = pd.concat([beg['Adj Close'], end['Adj Close']]).dropna()
		print(allSecuritiesAllData)
		w = weights * self.get_daily_returns_df(allSecuritiesAllData)
		print(w)
		if(isinstance(w, pd.DataFrame)):
			w = w.sum(axis = 1, skipna = True)

		print(w)
		print("securities_year_to_date_return :" + str(w[0]))
		ret = w[0]
		return '{:.1%}'.format(ret)

	def portfolio_year_to_date_return(self):
		endDate = self.data.index[len(self.data) - 1]
		while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
			endDate = endDate - datetime.timedelta(days=1)

		startDate = datetime.datetime(endDate.year - 1, 12, 31)
		while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
		  	startDate = startDate - datetime.timedelta(days=1)

		# print(str(startDate))
		# print(str(endDate))
		# print(self.data[-60:])
		# print(self.data.index)
		print(self.data.loc[startDate.strftime('%Y-%m-%d')])
		print(self.data.loc[endDate.strftime('%Y-%m-%d')])
		ret = self.data.loc[endDate.strftime('%Y-%m-%d')][0] / self.data.loc[startDate.strftime('%Y-%m-%d')][0] - 1
		print("Portfolio YTD: " + str(ret))
		return '{:.1%}'.format(ret)

	def security_total_return(self, securities, entry_price, entry_date, exit_price, exit_date):
		if (entry_price is None) or (exit_price is None):
			if entry_price is None:
				if entry_date:
					startDate = parser.parse(entry_date)
					startEndDate = startDate + datetime.timedelta(days=1)
					beg = pdr.get_data_yahoo(securities, start=startDate.strftime('%Y-%m-%d'), end=startEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
					entry_price = beg['Adj Close'][0]
				else:
					return None

			if exit_price is None:
				if exit_date:
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
				else:
					return None
		# print(entry_price)
		# print(exit_price)
		# print(exit_price/entry_price - 1)
		ret = (exit_price/entry_price - 1)
		return '{:.1%}'.format(ret)
		# allSecuritiesAllData = pdr.get_data_yahoo(securities, start=dateStart.strftime('%Y-%m-%d'), end=dateEnd.strftime('%Y-%m-%d'),  as_panel = False)
		

	def portfolio_one_year_return(self):
		endDate = self.data.index[len(self.data) - 1]
		startDate = endDate - relativedelta(years=1)
		while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
		  	startDate = startDate - datetime.timedelta(days=1)

		print(self.data.loc[startDate.strftime('%Y-%m-%d')])
		print(self.data.loc[endDate.strftime('%Y-%m-%d')])
		ret = self.data.loc[endDate.strftime('%Y-%m-%d')][0] / self.data.loc[startDate.strftime('%Y-%m-%d')][0] - 1
		print("Total portfolio return: " + str(ret))
		return '{:.1%}'.format(ret)


	# Find RAR of a portfolio constructed from AIF's NAV
	def one_year_risk_adjusted_return_from_NAV(self, threeFactor):
		r = requests.get(self.zip_file_url, stream=True)
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
		# print("one_year_risk_adjusted_return_from_NAV startDate: " + str(startDate))
		# print("one_year_risk_adjusted_return_from_NAV Date: " + str(endDate))

		dailyPortfolioReturns = self.get_daily_returns_df(self.data[startDate.strftime('%Y-%m-%d'):endDate.strftime('%Y-%m-%d')])
		dailyPortfolioReturns = pd.DataFrame(dailyPortfolioReturns.values, columns=["Daily Portfolio Returns"], index=dailyPortfolioReturns.index) * 100
		# print(dailyPortfolioReturns)
		dfjoin = dailyFactorDF.join(dailyPortfolioReturns).dropna()
		# print(dfjoin)
		portfolioExcessReturns = pd.DataFrame(dfjoin['Daily Portfolio Returns'].values - dfjoin['RF'].values, columns=['RP-RF'], index=dfjoin.index.values.flatten())
		# print(portfolioExcessReturns)
		dfjoin = dfjoin.join(portfolioExcessReturns).drop(columns=['Daily Portfolio Returns', 'RF'])
		# print(dfjoin)
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
	def one_year_risk_adjusted_return_from_securities(self, threeFactor, securities, weights):
		r = requests.get(self.zip_file_url, stream=True)
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
		w = weights * self.get_daily_returns_df(allSecuritiesAllData)
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

		print("factors: " + str(factors))

		X = dfjoin[factors] 
		Y = dfjoin['RP-RF']
		 
		# with sklearn
		regression = linear_model.LinearRegression()
		regression.fit(X, Y)
		print('Intercept: \n', regression.intercept_)
		print('Coefficients: \n', regression.coef_)
		print(regression)
		ret = regression.intercept_
		return '{:.1%}'.format(ret)
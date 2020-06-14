import pandas as pd
from io import BytesIO, StringIO
from pandas_datareader import data as pdr
import numpy as np
from scipy import stats
import yfinance as yf
import datetime as datetime
import calendar
from dateutil.relativedelta import relativedelta
from dateutil import parser
import statsmodels.api as sm
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

from .tools.risk_adjusted_returns import *

class NAVData():
	"""docstring for Data"""
	def __init__(self, latest_data_file_name):
		self.data = self._get_data(latest_data_file_name)

	def _convert_date_format(self, indexDate):
		return datetime.datetime.strptime(str(int(indexDate)), '%Y%m%d').strftime('%Y-%m-%d')

	def _get_data(self, file_url):
		client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
		        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

		object_key = settings.AWS_DATA_LOCATION + '/' + file_url
		csv_obj = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=object_key)
		body = csv_obj['Body']
		csv_string = body.read().decode('utf-8')
		df = pd.read_csv(StringIO(csv_string), skiprows=2, usecols=['Date', 'NAV'], index_col='Date')
		df.drop(df.tail(1).index,inplace=True)
		df.index = pd.to_datetime(df.index.map(lambda x : self._convert_date_format(x)))

		return df

class PortfolioAnalysis():
	"""docstring for PortfolioAnalysis"""
	def __init__(self, nav_data):
		self.data = nav_data.data

	def as_of(self):
		return self.data.index[-1].strftime('%m-%d-%Y')

	def portfolio_one_year_return(self):
		endDate = self.data.index[len(self.data) - 1]
		startDate = endDate - relativedelta(years=1)
		while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
		  	startDate = startDate - datetime.timedelta(days=1)

		ret = self.data.loc[endDate.strftime('%Y-%m-%d')][0] / self.data.loc[startDate.strftime('%Y-%m-%d')][0] - 1
		return '{:.1%}'.format(ret)

	def portfolio_year_to_date_return(self):
		endDate = self.data.index[len(self.data) - 1]
		while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
			endDate = endDate - datetime.timedelta(days=1)

		startDate = datetime.datetime(endDate.year - 1, 12, 31)
		while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
		  	startDate = startDate - datetime.timedelta(days=1)

		ret = self.data.loc[endDate.strftime('%Y-%m-%d')][0] / self.data.loc[startDate.strftime('%Y-%m-%d')][0] - 1
		return '{:.1%}'.format(ret)

	def aif_nav_data_for_template(self, time_horizon_params):
		ret = None
		if time_horizon_params:
			endDate = self.data.index[len(self.data) - 1]
			startDate = endDate - relativedelta(**time_horizon_params)
			while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
			  	startDate = startDate - datetime.timedelta(days=1)

			time_series = self.data.loc[startDate.strftime('%Y-%m-%d'):endDate.strftime('%Y-%m-%d')]
			time_series.index = time_series.index.strftime('%m-%d-%Y')
			ret = time_series["NAV"].to_dict()
		else:
			time_series = self.data.loc[:]
			time_series.index = time_series.index.strftime('%m-%d-%Y')
			ret = time_series["NAV"].to_dict()

		return ret

class SecurityAnalysis():
	"""docstring for SecurityAnalysis"""

	def as_of(self):
		eastern = timezone('US/Eastern')
		endDate = datetime.datetime.now(eastern)
		
		beforeMondayDayEnd = endDate.hour < 17 and endDate.weekday() == 0
		if beforeMondayDayEnd:
			endDate = datetime.datetime.today() - datetime.timedelta(days=1)

		return endDate.strftime('%m-%d-%Y')

	def get_current_price(self, securities):
		eastern = timezone('US/Eastern')
		endDate = datetime.datetime.now(eastern)
		
		beforeMondayDayEnd = endDate.hour < 17 and endDate.weekday() == 0
		if beforeMondayDayEnd:
			endDate = datetime.datetime.today() - datetime.timedelta(days=1)

		while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
			endDate = endDate - datetime.timedelta(days=1)
		endEndDate = endDate + datetime.timedelta(days=1)

		end = pdr.get_data_yahoo(securities, start=endDate.strftime('%Y-%m-%d'), end=endEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
		ret = end['Adj Close'][0]
		return round(ret, 2)	

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
		
		ret = (exit_price/entry_price - 1)
		return '{:.1%}'.format(ret)

	def _get_daily_returns_df(self, prices):
	    return ((prices / prices.shift(1) - 1).dropna())

	def securities_year_to_date_return(self, securities, weights):
		eastern = timezone('US/Eastern')
		endDate = datetime.datetime.now(eastern)
		
		beforeMondayDayEnd = endDate.hour < 17 and endDate.weekday() == 0
		if beforeMondayDayEnd:
			endDate = datetime.datetime.today() - datetime.timedelta(days=1)

		while(endDate.weekday() > 4 or endDate in holidays.US(years=endDate.year)):
			endDate = endDate - datetime.timedelta(days=1)
		endEndDate = endDate + datetime.timedelta(days=1)
		
		startDate = datetime.datetime(endDate.year - 1, 12, 31)
		while(startDate.weekday() > 4 or startDate in holidays.US(years=startDate.year)):
		  	startDate = startDate - datetime.timedelta(days=1)
		startEndDate = startDate + datetime.timedelta(days=1)
		
		beg = pdr.get_data_yahoo(securities, start=startDate.strftime('%Y-%m-%d'), end=startEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
		end = pdr.get_data_yahoo(securities, start=endDate.strftime('%Y-%m-%d'), end=endEndDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)

		allSecuritiesAllData = pd.concat([beg['Adj Close'], end['Adj Close']]).dropna()
		
		w = weights * self._get_daily_returns_df(allSecuritiesAllData)
		if(isinstance(w, pd.DataFrame)):
			w = w.sum(axis = 1, skipna = True)

		ret = w[0]
		return '{:.1%}'.format(ret)
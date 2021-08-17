import requests, zipfile
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

class RiskAdjustedReturns():
	"""docstring for RiskAdjustedReturns"""
	def __init__(self, nav_data):
		self.data = nav_data.data
		self._fama_french_factors_zip_file_url = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'

	def _get_daily_returns_df(self, prices):
	    return ((prices / prices.shift(1) - 1).dropna())

	# Find RAR of a portfolio constructed from AIF's NAV
	def one_year_risk_adjusted_return_from_NAV(self, threeFactor):
		r = requests.get(self._fama_french_factors_zip_file_url, stream=True)
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

		dailyPortfolioReturns = self._get_daily_returns_df(self.data[startDate.strftime('%Y-%m-%d'):endDate.strftime('%Y-%m-%d')])
		dailyPortfolioReturns = pd.DataFrame(dailyPortfolioReturns.values, columns=["Daily Portfolio Returns"], index=dailyPortfolioReturns.index) * 100
		
		dfjoin = dailyFactorDF.join(dailyPortfolioReturns).dropna()
		portfolioExcessReturns = pd.DataFrame(dfjoin['Daily Portfolio Returns'].values - dfjoin['RF'].values, columns=['RP-RF'], index=dfjoin.index.values.flatten())
		dfjoin = dfjoin.join(portfolioExcessReturns).drop(columns=['Daily Portfolio Returns', 'RF'])
		
		if threeFactor:
			factors = dfjoin.columns.tolist()[0:3]
		else:
			factors = dfjoin.columns.tolist()[0:5]
		
		X = dfjoin[factors] 
		X = sm.add_constant(X)
		Y = dfjoin['RP-RF']

		regression = sm.OLS(Y, X).fit()
		ret = regression.params[0] * 365 / 100
		return regression.summary2().tables[1].to_dict()
		

	# Find RAR of a portfolio constructed from individual stock info from Yahoo Finance
	def one_year_risk_adjusted_return_from_securities(self, threeFactor, securities, weights):
		r = requests.get(self._fama_french_factors_zip_file_url, stream=True)
		z = zipfile.ZipFile(BytesIO(r.content))
		dailydf = pd.read_csv(z.open('F-F_Research_Data_5_Factors_2x3_daily.CSV'), skiprows=3)[-300:]
		dailydf = dailydf.rename(columns={"Unnamed: 0": "Date"})

		dailydf.index = [datetime.datetime.strptime(str(date_num), '%Y%m%d') for date_num in dailydf['Date'].tolist()]
		dailydf = dailydf.drop(columns=['Date'])

		last_index = dailydf.index[-1]
		endDate = datetime.datetime(last_index.year, last_index.month, calendar.monthrange(last_index.year, last_index.month)[1])
		startDate = last_index - relativedelta(years=1)
		allSecuritiesAllData = pdr.get_data_yahoo(securities, start=startDate.strftime('%Y-%m-%d'), end=endDate.strftime('%Y-%m-%d'),  as_panel = False, auto_adjust=False)
		allSecuritiesAllData = allSecuritiesAllData['Adj Close'][1:]
		w = weights * self._get_daily_returns_df(allSecuritiesAllData)
		if isinstance(w, pd.DataFrame):
			dailyPortfolioReturns = pd.DataFrame(w.sum(axis=1, skipna=True), columns=["Daily Portfolio Returns"])
		else:
			dailyPortfolioReturns = pd.DataFrame(w.values, columns=["Daily Portfolio Returns"], index=w.index)
		dfjoin = dailydf.join(dailyPortfolioReturns).dropna()

		portfolioExcessReturns = pd.DataFrame(dfjoin['Daily Portfolio Returns'].values - dfjoin['RF'].values, columns=['RP-RF'], index=dailyPortfolioReturns.index.values.flatten())
		portfolioExcessReturns
		dfjoin = dfjoin.join(portfolioExcessReturns).drop(columns=['Daily Portfolio Returns', 'RF'])

		if threeFactor:
			factors = dfjoin.columns.tolist()[0:3]
		else:
			factors = dfjoin.columns.tolist()[0:5]

		X = dfjoin[factors] 
		X = sm.add_constant(X)
		Y = dfjoin['RP-RF']
		 
		regression = sm.OLS(Y, X).fit()
		ret = regression.params[0] * 365 / 100
		return regression.summary2().tables[1].to_dict()
import pandas as pd
from io import BytesIO
import requests, zipfile
from pandas_datareader import data as pdr
import numpy as np
from scipy import stats
import yfinance as yf
import datetime as datetime
import calendar
from dateutil.relativedelta import relativedelta
from sklearn import linear_model
import statsmodels.api as sm
yf.pdr_override() # <== that's all it takes :-)

from decouple import config
import os

zip_file_url ='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'

def get_daily_returns_df(prices):
    return ((prices / prices.shift(1) - 1).dropna())

def year_to_date_return(securities, weights):
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
	print(w[0])

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
	dailyPortfolioReturns = pd.DataFrame(w.sum(axis = 1, skipna = True), columns=["Daily Portfolio Returns"])
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

# one_year_risk_adjusted_return(True, securities=['SPY', 'LYV', 'HXL'], weights=[1/3, 1/3, 1/3])
year_to_date_return(securities=['HXL'], weights=[1])

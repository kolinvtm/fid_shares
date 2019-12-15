import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import micex
import numpy as np
import pickle


def make_df_from_iss(html):

    soup = BeautifulSoup(html, 'lxml')

    cols_ = [x['name'].lower() for x in soup.find_all('columns')[0].find_all('column')]

    try:
        meta_ = [x['name'].lower() for x in soup.find_all('columns')[1].find_all('column')]
    except Exception as e:
        print(str(e))

    col_types = {x['name']:x['type'] for x in soup.find_all('column')}

    df = pd.DataFrame(columns=cols_)

    for d in [{k:x[k] for k in cols_} for x in soup.find_all('rows')[0].find_all('row')]:
        df = df.append(d,ignore_index=True)

    for d in [{k:int(x[k]) for k in meta_} for x in soup.find_all('rows')[1].find_all('row')]:
        meta_dict.update(d)

    return df,meta_dict

def mk_date_format(self, date_ = None):
        if date_ == None:
            date_ = datetime.datetime.now()
            while date_.weekday()>=5:
                date_-=datetime.timedelta(1)
            self.date_ = date_
            return datetime.datetime.strftime(date_,"%Y-%m-%d")

def make_df_from_iss_new(self, market='shares', from_ = '2019-12-01', till_=None):

        if till_ == None:
            till_ = mk_date_format(self)

        start_ = 0
        limit_ = 100

        total = 500

        df_target = pd.DataFrame()

        if market=='shares':
            iterator =  self.secids[:2]
            boardgroup='/boardgroups/57/'

        elif market=='index':
            iterator = ['IMOEX']
            boardgroup='/'

        for sec in iterator:
            print(sec)
            while start_<total:

                html = requests.get(micex_url.format(market,boardgroup,sec,from_,till_,start_,limit_)).text

                df, meta_dict = make_df_from_iss(html)

                total = meta_dict['total']
                start_ +=100
                df_target = pd.concat([df_target, df], sort = False, ignore_index = True)

        return df_target

meta_dict = {}
micex_url = "https://iss.moex.com/iss/history/engines/stock/markets/{}{}securities/{}.xml?from={}&till={}&start={}&iss.meta=on&h&sort_order=TRADEDATE&limit={}"


m = micex.Micex()

index = make_df_from_iss_new(m,market='index')
df = make_df_from_iss_new(m)

index.set_index('tradedate', inplace=True)

df.set_index('tradedate', inplace=True)

index['close'] = index['close'].astype('float32')
index['Index_chg'] = index['close']/index['close'].shift(1)

new = pd.concat([df,index['Index_chg']],axis=1)
new.replace('',np.nan, inplace=True)

new['close']=new['close'].astype('float32')

new['Close_chg']  =new['close']/new['close'].shift()

new['Label'] = new['Close_chg']>new['Index_chg']

new['high'] = new['high'].astype('float32')
new['low'] = new['low'].astype('float32')
new['value']=new['value'].astype('float32')
new['close'] = new['close'].astype('float32')
new['open'] = new['open'].astype('float32')

new['d_high_low'] = new['high']-new['low']
new['d_close_open'] = new['close']-new['open']

new['d_high_low']=new['d_high_low']/new['d_high_low'].shift()

new.loc[new['d_high_low']==np.inf,['d_high_low']]=0

new['value_chg']=new['value']/new['value'].shift()


print("""Correlations:
{}
""".format(new[new.columns[-6:]].corr()))


new.reset_index(inplace=True)


deviation_url = "https://iss.moex.com/iss/statistics/engines/stock/deviationcoeffs?iss.meta=on&date={}"

#c
holidays_= [datetime.datetime(y,m,d)
            for y in range(2014,2020,1)
            for m,d in [(1,1),(1,2),(1,3),(1,4),
                        (1,5),(1,6),(1,7),(2,23),
                        (3,8),(5,1),(5,9),(6,12),(11,4)]]

#c
dev = pd.DataFrame()

startdate = datetime.datetime(2019,12,1)
enddate = datetime.datetime.now()

while startdate<=enddate:
    r = requests.get(deviation_url.format(datetime.datetime.strftime(startdate,"%Y-%m-%d")))
    dev_temp, _ = make_df_from_iss(r.text)
    dev = pd.concat([dev,dev_temp], sort=False, ignore_index=True)
    startdate+=datetime.timedelta(1)
    while startdate.weekday() in [5,6] or startdate in holidays_:
        startdate+=datetime.timedelta(1)


dev.rename({'tradedate':'tradedate_2',
            'secid':'secid_2'},axis=1, inplace=True)

dev['index']=dev['tradedate_2']+'_'+dev['secid_2']
new['index']=new['tradedate']+'_'+new['secid']

dev.set_index('index', inplace=True)
new.set_index('index',inplace=True)

t = pd.concat([new,dev],axis=1,sort=False)

print(t.loc[t['secid']=='ABRD'].tail(10))

with open('micex_wide.pickle','wb') as p:
    pickle.dump(t,p)

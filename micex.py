import pandas as pd
import requests

from bs4 import BeautifulSoup

import datetime


class Micex:
    
    def __init__(self):
        self.urls = {'shares':'https://iss.moex.com/iss/statistics/engines/stock/quotedsecurities?date={}'}
        self.resp = {'resp_body':None,
                    'meta':None}
        self.secids_with_names = None
        self.secids = self.get_secids()
        
    
    def load_secids(self, date_ = '2019-11-28'):
        
        r = requests.get(self.urls['shares'].format(date_))
        
        df=self.make_df_from_iss(r.text)
        
        self.secids_with_names = df.loc[((df.name.str.endswith('ао'))|
                                         (df.name.str.endswith('shs')))&
                                         (df.mainboardid=='TQBR'),['secid','name']]
        
        return self.secids_with_names 
        
    
    def mk_date_format(self):
        return datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d")
    
    def make_df_from_iss(self, html):
    
        soup = BeautifulSoup(html, 'lxml')

        cols_ = [x['name'].lower() for x in soup.find_all('columns')[0].find_all('column')]
        
        try: 
            meta_ = [x['name'].lower() for x in soup.find_all('columns')[1].find_all('column')]
        except Exception as e:
            print(str(e))

        col_types = {x['name']:x['type'] for x in soup.find_all('column')}

        df = pd.DataFrame(columns=cols_)

        self.resp['resp_body'] = html
        self.resp['meta'] = meta_

        for d in [{k:x[k] for k in cols_} for x in soup.find_all('rows')[0].find_all('row')]:
            df = df.append(d,ignore_index=True)

        return df
    
    def get_secids(self):
        if self.secids_with_names == None:
            self.load_secids()
        
        self.secids =  self.secids_with_names['secid'].values
        
        print('Count of secids: ', len(self.secids),'\n','1st 5 secids', self.secids[:5],
             'Last 5 secids', self.secids[-5:])
        
        return self.secids

    
m1 = Micex()

print(m1.secids)

print()

print(m1.resp['meta'])

# print(m1.secids_with_names)

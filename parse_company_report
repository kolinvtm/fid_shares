import pandas as pd
import requests

from bs4 import BeautifulSoup

import numpy as np


class CompanyBS:
    def __init__(self,*comp_tickets):
        self.comp_tickets = list(comp_tickets)
        self.url =  "https://smart-lab.ru/q/{}/f/y/"
        
    def load(self, dropna_flag=False):
        df = pd.DataFrame()
        for ticket in self.comp_tickets:
            temp_df = self.parse_comp_rep(ticket)
            df = pd.concat([df,temp_df],sort=False,ignore_index=True)
        
        df.replace(' ', np.nan, inplace=True)
        
        if dropna_flag:
            df.dropna(axis=1, inplace=True)
            
        return df


    def parse_comp_rep(self, company_ticket):

        r = requests.get(self.url.format(company_ticket))

        soup = BeautifulSoup(r.text, 'lxml')

        table = np.array([z for z in [(x.find('th').text.replace('\n','').replace('\t',''),                 [y.text.replace('\n','').replace('\t','') for y in x.find_all('td')]) 
                                      for x in soup.find('table').find_all('tr') if x.find('th')]])

        cols = table[0,1][1:6]

        df = pd.DataFrame(columns = cols)
        ind_ = []
        for x,y in zip(table[1:,1],table[1:,0]):
            if len(x[1:6])==5:
                ind_.append(y)
                df = df.append({k:v for k,v in zip(cols,x[1:6])},ignore_index=True)

        df.index = ind_
        df= df.T
        df=df.reset_index()
        df['Company'] = company_ticket

        return df
        

p1 = CompanyBS('ALRS','SBER','GAZP')

print(p1.load())

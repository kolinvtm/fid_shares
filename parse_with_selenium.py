
from selenium import webdriver
import os
from time import sleep
import pickle
import collections

import pandas as pd

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from difflib import SequenceMatcher


class Parser:
    def __init__(self, company_name):
        self.login = None
        self.password = None
        self.driver = None
        self.search_company = company_name
        
        self.start()
        self.auth()
    
    def start(self):
        pass
        
    
    def auth(self):
        self.driver.get('')
        self.driver.find_element_by_name('username').send_keys(self.login)
        self.driver.find_element_by_name('password').send_keys(self.password)
        self.driver.find_elements_by_tag_name('button')[0].click()
        
    
    def parse_coeff(self):
        url_cls_inf = ''
        dict_comp_sp=collections.defaultdict()
        
        for num, company in enumerate(self.search_company):
            try:
                self.driver.get(url_cls_inf)

                sleep(1.5)

                if num == 0:
                    count_BS = 50

                self.clear_input_sp(count_BS)

                self.driver.find_elements_by_tag_name('input')[0].send_keys(company)
                sleep(1)
                self.driver.find_elements_by_tag_name('input')[0].send_keys(Keys.ENTER)

                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'sp-summary__title')))
                sleep(0.5)

                urls_arr =[y.get_attribute('href') for x in self.driver.find_elements_by_class_name('sp-summary__title') for y in x.find_elements_by_tag_name('a')]

                res_arr = [x.text for x in self.driver.find_elements_by_class_name('sp-summary__title')]

                max_sim =0
                target_arr = []
                taget_id =0
                for id_sim, sim in enumerate(res_arr):
                    sim_ratio = self.similar(company.upper(),sim.upper())
                    if sim_ratio>max_sim:
                        max_sim=sim_ratio
                        target_arr= [sim]
                        taget_id=id_sim

                self.driver.get(urls_arr[taget_id])
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-company-info__content')))
                sleep(0.5)

                self.driver.get(urls_arr[taget_id][:-3]+str(524))
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-pages')))
                sleep(1.5)
                
               """
               need some func here
               """

                print('success'.upper(), num, company, sep=' ')
                
                count_BS=len(company)+2
                
            except Exception as e:
                print(str(e))
        
        
        

    def clear_input_sp(self, n=50):
        for i in range(n):
            self.driver.find_elements_by_tag_name('input')[0].send_keys(Keys.BACKSPACE)
            
    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()
            
            
    def close(self):
        self.driver.close()
        
    def got_524(self, self):
        #that got 524 page

        d = {}

        for id_h, x in enumerate(self.driver.find_elements_by_tag_name('tbody')[1].find_elements_by_tag_name('tr')):

            coeff_row = [y.text if y.text !='' else 'NaN' for y  in x.find_elements_by_tag_name('td') ]
            if coeff_row.count('NaN') < len(coeff_row)-1:
                d[coeff_row[0]]= coeff_row[1:]
            return d
            
     def is_bank(self):
         #for banks
         
        d = {}

        head_ = [h.text for h in s.driver.find_elements_by_tag_name('thead')[0].find_elements_by_tag_name('th')]

        for id_h, x in enumerate(s.driver.find_elements_by_tag_name('tbody')[0].find_elements_by_tag_name('tr')):

            coeff_row = [y.text if y.text !='' else 'NaN' for y  in x.find_elements_by_tag_name('td')]
            if coeff_row.count('NaN') < len(coeff_row)-1:
                d[coeff_row[0]]= {k:v for k,v in zip(head_[1:],coeff_row[1:])}
         return d

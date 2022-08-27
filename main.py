from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options #importing chrome whebdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import requests
import re
import pandas as pd


def load_more_topic():
    options=Options()
    b=webdriver.Chrome(options=options)
    url="https://www.smallcase.com/discover/all"
    b.get(url)

    while True:
        time.sleep(0.75)
        try:
            btn=b.find_element(By.XPATH,"//div[@class='LoadMoreButton__wrapper__2VAhr text-center mt16 pt8 pb8 pl8 pr8 full-width pointer']")
            b.execute_script("arguments[0].click();", btn)
        except NoSuchElementException:
            break
    doc=b.page_source
   
    topic_dict_df=scrape_load_more_topic_link_title(doc)
    whole_data_df=scrape_topic_data(topic_dict_df)
    return whole_data_df

def scrape_load_more_topic_link_title(doc):
    soup = BeautifulSoup(doc, 'html.parser')
    
    link_class="AllSmallcases__smallcasecard-link__2A7p_"
    topic_link=soup.find_all('a',{'class':link_class})
    topic_links=[]
    base_url="https://www.smallcase.com"
    for link in topic_link:
        topic_links.append(base_url+link['href'])
    
    return topic_links

def scrape_topic_data(topic_links):
    title_list=[]
    manageby_list=[]
    smalldescription_list=[]
    cagr_time_period_list=[]
    cagr_rate_list=[]
    volatility_list=[]
    overview_list=[]
    Minimum_Investment_Amount_list=[]
    launch_date_list=[]
    value_of_company_list=[]
    equity_small_cap_list=[]
    no_of_smallcases_list=[]
    about_manager_list=[]
    for i in topic_links:    
        topic_page_url=i
        response=requests.get(topic_page_url,allow_redirects=False)
        topic_doc=BeautifulSoup(response.text,'html.parser')

        #getting title
        title_class="SmallcaseProfileBanner__title-section__1a8wr"
        title1=topic_doc.find_all('div',{'class':title_class})
        title=title1[0].find('h1',{'class':'ellipsis SmallcaseTitle__name__3TX4_ font-medium mb8'}).text
        title_list.append(title)

        #getting manage by 
        managed=title1[1].find('p',{'class':'text-13 text-normal'}).text.strip()
        mana=managed.replace('Free Access','')
        manage_by=mana.replace('by','')
        manageby_list.append(manage_by)

        #getting small descriptions
        small_description=topic_doc.find('div',{'class':'SmallcaseDescription__description__3M27M text-15 lh-157 text-dark'}).text
        smalldescription_list.append(small_description)

        #getting csgr time period year
        time_period=topic_doc.find('div',{'class':'flex SmallcaseProfileBannerStatbox__statbox-inner__vGW_n'})
        cagr_period=time_period.find('div',{'class':'text-14 text-light text-left StatBox__title__3yY1q font-regular text-light'}).text
        cagr_time_period=cagr_period.replace('Y CAGR',' year')
        cagr_time_period_list.append(cagr_time_period)

        #getting cagr rate
        try:
            cagr_rate=time_period.find('div',{'class':'text-green font-regular text-dark text-20 StatBox__value__2FWUJ mt8'}).text
            cagr_rate_list.append(cagr_rate)
        except:
            cagr_rate=time_period.find('div',{'class':'text-red font-regular text-dark text-20 StatBox__value__2FWUJ mt8'}).text
            cagr_rate_list.append(cagr_rate)

        #getting volatility 
        volatility_div=topic_doc.find('div',{'class':'VolatilityLabel__volatility-tag-container__dcnic pt4 pb4 pl8 pr8 br-4 flex'})
        volatility=volatility_div.find('div').text
        volatility_list.append(volatility)

        #getting overview
        overview_1=topic_doc.find('div',{'id':'rationale'}).text
        overview_list.append(overview_1)

        #getting Minimum Investment Amount
        minimum_amount=topic_doc.find('p',{"class":"text-20 font-regular text-dark"}).text
        minimum_amount1=minimum_amount.replace('\xa0','')
        Minimum_Investment_Amount_list.append(minimum_amount1)

        #getting launch date list
        launch_date=topic_doc.find('p',{'class':'text-center font-regular text-dark'}).text
        launch_date_list.append(launch_date)

        #getting value of company list
        value=topic_doc.find_all('div',{'class':'Statbox__value__2vZLj'})
        value_of_company=value[0].text
        value_of_company_list.append(value_of_company)

        #getting equity small cap
        equity_small_cap=value[1].text
        equity_small_cap_list.append(equity_small_cap)

        #getting no of samllcases
        try:
            no_of_smallcases1=topic_doc.find('div',{'class':'ManagersCardUI__sub-header__VNEp3 text-13 font-medium'}).text
            no_of_smallcases=(re.findall('[0-9]+',no_of_smallcases1))[0]
            no_of_smallcases_list.append(no_of_smallcases)
        except:
            no_of_smallcases_list.append('not available')

        #getting about manager
        about=topic_doc.find_all('div',{'class':'mb16'})
        about_manager=about[-1].text
        about_manager_list.append(about_manager)
        
        
    whole_data={"Title":title_list,
        "Manage By":manageby_list,
        "Small Description":smalldescription_list,
        "CAGR Time Period":cagr_time_period_list,
        "CAGR Rate":cagr_rate_list,
        "Volatility":volatility_list,
        "Overview":overview_list,
        "Minimum Investment Amount":Minimum_Investment_Amount_list,
        "Launch Date":launch_date_list,
        "Past performance: Small Case":value_of_company_list,
        "Past performance: Equity":equity_small_cap_list,
        "Number of Smallcases managed by Manager":no_of_smallcases_list,
        "About Manager":about_manager_list,
       }
    whole_data_df=pd.DataFrame(whole_data)
    whole_data_df.to_excel("WholeData.xlsx",index=False) 


load_more_topic()
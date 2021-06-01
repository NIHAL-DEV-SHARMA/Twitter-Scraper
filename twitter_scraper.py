# some imports
import csv
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# creating argument parser
parser = argparse.ArgumentParser(description='It will scrape Twetter using folowing inputs')
parser.add_argument( '-u' ,'--username', metavar='user_name' ,required=True , type=str, help='Enter your username or email here')
parser.add_argument( '-p' ,'--password', metavar='password', required=True , type=str, help='Enter your password of twitter here')
parser.add_argument( '-s' ,'--searchterm', metavar='search_term',required=True,type=str, help='Enter your SearchTerm to search')
parser.add_argument( '-f' ,'--filename', metavar='file_name' ,required=False , type=str, help='Enter your name of file in which you wanna save the data')
parser.add_argument( '-t' ,'--timeout', metavar='timeout' ,required=False , type=int, help='Timeout ')

# Parsing the shit
args = parser.parse_args() 




class Scraper:
    def __init__(self , driver , timeout=5):
        self.driver = driver
        self.timeout = timeout
    
    def init_args(self , userName , password ,hastag , filename ):
        
        self.userName = userName
        self.password = password
        self.hastag = hastag
        self.filename = filename
        
        
        print("Initialised Variables")
    
    def get_tweet_data(self , card):
        
        """
            --> Extract data from tweet card
        """
        
        username = card.find_element_by_xpath('.//span').text
        try:
            handle = WebDriverWait(self.driver , self.timeout).until(EC.presence_of_element_located((By.XPATH , './/span[contains(text(), "@")]'))).text
        except NoSuchElementException:
            return

        try:
            postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
        except NoSuchElementException:
            return

        comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
        responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
        
        text = comment + responding
        
        retweet_cnt = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
        like_cnt = card.find_element_by_xpath('.//div[@data-testid="like"]').text
        
        # Saving them in tweet 
        tweet = (username, handle, postdate, text,retweet_cnt, like_cnt)
        return tweet
    
    def login_user(self):
        
        """
            --> login the user to twitter
        """
        
        self.driver.get('https://www.twitter.com/login')
        
        username = WebDriverWait(self.driver , self.timeout).until(EC.presence_of_element_located((By.XPATH , '//*[@id="react-root"]/div/div/div[2]/main/div/div/div[2]/form/div/div[1]/label/div/div[2]/div/input')))
        username.send_keys(self.userName)
        
        password= WebDriverWait(self.driver , self.timeout).until(EC.presence_of_element_located((By.XPATH , '//input[@name="session[password]"]')))
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)
        
    def main(self):
        self.login_user() #calling login_user 
        
        # > finding search input and sending term in it
        search_input = WebDriverWait(self.driver , self.timeout ).until(EC.presence_of_element_located((By.XPATH , '//input[@aria-label="Search query"]')))
        search_input.send_keys(self.hastag)
        search_input.send_keys(Keys.RETURN)
        
        # > navigating to latest page
        WebDriverWait(self.driver , self.timeout ).until(EC.presence_of_element_located((By.LINK_TEXT ,'Latest' ))).click()
        
        # > get all tweets on the page
        
        data = []
        tweet_ids = set()
        last_position = self.driver.execute_script("return window.pageYOffset;")
        scrolling = True
            
        """
        NOTE -->  
        
        Twitter render the data when we scroll So,
        To get the data we first need to scroll for data
        
        """
        while scrolling:
            page_cards = self.driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
            
            for card in page_cards[-15:]:
                tweet = self.get_tweet_data(card)
                if tweet:
                    tweet_id = ''.join(tweet)
                    if tweet_id not in tweet_ids: # checking for duplicate tweet if not then append it to data
                        tweet_ids.add(tweet_id)
                        data.append(tweet)
                        
            scroll_attempt = 0
            while True:
                # -> checking scroll position
                
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                
                time.sleep(1)
                
                curr_position = self.driver.execute_script("return window.pageYOffset;")
                
                if last_position == curr_position:
                    scroll_attempt += 1
                    
                    # end of scroll region
                    
                    if scroll_attempt >= 3:
                        scrolling = False
                        break
                    else:
                        time.sleep(1) # attempt another scroll
                else:
                    last_position = curr_position
                    break
                    
        self.driver.close()
        print('Successfuly scraped data! \n')
        print(f'lenght of data: {len(data)}\n')
        
        # Saving the data in CSV
        with open(f'{self.filename}.csv', 'w', newline='', encoding='utf-8') as f:
            header = ['username', 'handle', 'postdate', 'tittle','retweets', 'likes']
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)



# I am using brave you are free to user chrome , firefox i dont care

driver_path = "driver/chromedriver.exe"
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

option = webdriver.ChromeOptions()
option.binary_location = brave_path
option.add_argument("--incognito")

driver = webdriver.Chrome(executable_path=driver_path, chrome_options=option)

# Initial time
start_time=time.time()

scraper = Scraper(driver , args.timeout )
scraper.init_args(args.username , args.password , args.searchterm , args.filename )
scraper.main()

print(f"Total time taken by scraping is {time.time()-start_time}")
from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import datetime
import requests
import time
import json
import sys
import re

# Create a new instance of the Chrome driver
# options = webdriver.ChromeOptions()
options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('ignore-certificate-errors')
options.add_argument("--ignore-ssl-errors");
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=options)
driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)

# Get System Variables
sysVars = sys.argv

# Function to validate the url
def is_url(cadena):
    try:
        resultado = urlparse(cadena)
        return all([resultado.scheme, resultado.netloc])
    except ValueError:
        return False

# Check if we receive the url of the store
search_index = 1
crawl_type = 2 # full or only
        
if 0 <= search_index < len(sysVars):
    # If the condition is true, continue with the script
    
    # When the crawl type was not specified we use the "only" crawl
    if crawl_type == len(sysVars):
        sysVars.append("only") 

    if is_url(sysVars[search_index]) == True:    
        # Select url variable and get only website hostname to get urls information 
        mainUrl = urlparse(sysVars[search_index])

        # Print variable to validate if we receive the domain correctly
        # print(mainUrl.hostname)

        # Set the url with which we will work          
        if sysVars[crawl_type] == "full":
            # Generate the cache to the full page
            selected_url ='https://' + mainUrl.hostname + '/sitemap.xml'
        else:
            # Generate the cache to a specific page
            selected_url ='https://' + mainUrl.hostname + mainUrl.path    

        # Print variable to validate if we set the route correctly
        print(selected_url)
                  
    else:
        # If the condition is not true, stop the script
        print("URL is malformed. Valid URL example: https://yourdomain.com")
        sys.exit()

else:
    # If the condition is not true, stop the script
    print("URL is empty. Valid URL example: https://yourdomain.com")
    sys.exit()


# Get website 
driver.get(selected_url)

# Get the current URL of the webpage
driver_url = driver.current_url

# Send a GET request to the webpage using requests module
driver_response = requests.get(driver_url)

# Get the status code
driver_status_code = driver_response.status_code

# Print the status code
# print("Status code:", driver_status_code)

# Creating a time delay of 5 seconds
time.sleep(5)

current_time = datetime.datetime.now()
print()
print("Start time: " + str(current_time))

if driver_status_code == 200:

    if sysVars[crawl_type] == "full":
        # Get list of links from sitemap 
        folderMain = driver.find_element(By.ID, "folder0")
        foldersCount = len(folderMain.find_elements(By.CLASS_NAME, "folder"))

        # Create list of urls and add them to the array
        i = 1
        urls = []
        while i <= 5: # foldersCount
            folderID = "folder" + str(i)
            folder = driver.find_element(By.ID, folderID)
            div1 = folder.find_element(By.CSS_SELECTOR, "div.opened")
            div2 = div1.find_element(By.CSS_SELECTOR, "div.line")
            span = div2.find_element(By.CSS_SELECTOR, "span:nth-child(2)")
            urls.append(span.text)    
            i += 1
    else:
        urls = [selected_url]


    # Visit individual urls twice to generate varnish cache
    for url in urls:

        print()
        print("Working on: " + str(url))
        print()
    
        # Go to the url
        driver.get(url)
        # Creating a time delay of 5 seconds
        time.sleep(5)

        # Go to the url a second time
        driver.get(url)
        # Creating a time delay of 5 seconds
        time.sleep(5)

        # Access requests via the `requests` attribute
        for request in driver.requests:

            if request.response:

                if request.response.headers['Content-Type'] == 'application/json':
                    
                    # Function to validate a URL
                    def validate_url(link):
                                        
                        # Define the patterns for URL validation
                        patterns = [
                            r"\/checkout",
                            r"\/customer",
                            r"((hah_api\/cart)+[^\/]|(hah_api\/cart\/add)+[^\/]|(hah_api\/cart\/sidebar)+[^\/]|(hah_api\/cart\/delete)+[^\/]|(hah_api\/cart\/update)+[^\/])",
                            r"((hah_api\/checkout\/index)+[^\/]|(hah_api\/checkout\/place)+[^\/]|(hah_api\/checkout\/region)+[^\/])",
                            r"((hah_api\/customer\/create)+[^\/]|(hah_api\/customer\/login)+[^\/]|(hah_api\/customer\/logout)+[^\/])",
                            r"((hah_api\/account\/captcha)+[^\/]|(hah_api\/account\/forgot)+[^\/]|(hah_api\/account\/reset)+[^\/]|(hah_api\/account\/update)+[^\/]|(hah_api\/account\/password)+[^\/]|(hah_api\/account\/info)+[^\/])",
                            r"((hah_api\/address\/index)+[^\/]|(hah_api\/address\/create)+[^\/]|(hah_api\/address\/update)+[^\/]|(hah_api\/address\/delete)+[^\/])",
                            r"((hah_api\/order\/index)+[^\/]|(hah_api\/order\/view)+[^\/]|(hah_api\/order\/cancel)+[^\/]|(hah_api\/order\/invoice)+[^\/])",
                            r"((hah_api\/common\/talk)+[^\/]|(hah_api\/common\/region)+[^\/])",
                            r"((hah_api\/wishlist\/index)+[^\/]|(hah_api\/wishlist\/remove)+[^\/]|(hah_api\/wishlist\/add)+[^\/]|(hah_api\/wishlist\/status)+[^\/])",
                            r"(hah_api\/payment\/index)+[^\/]",
                            r"(hah_api\/contact\/post)+[^\/]",
                            r"(hah_api\/newsletter\/subscribe)+[^\/]",
                            r"(hah_api\/draw\/index)+[^\/]", 
                            r"(hah_api\/hotel\/save)+[^\/]", 
                            r"(hah_api\/search)+[^\/]", 
                            r"(hah_api\/search\/index)+[^\/]", 
                            r"(hah_api\/search\/suggest)+[^\/]", 
                            r"(hah_api\/membercard\/index)+[^\/]"
                        ]
                        
                        # Concatenates the patterns in a regular expression using the logical operator OR (|)
                        pattern = "|".join(patterns)
                                    
                        # Check if the URL matches the pattern
                        p = re.compile(pattern)
                        result = p.findall(str(link))                   
                        
                        if result:
                            return True
                        else:
                            return False
                    
                    if validate_url(request.url) == False:                    
                        # print(f"{request.url}")
                        # print("Valid url.")
                        # print()
                        
                        # Purge URL Cache
                        headers_for_purge = {
                            'X-Magento-Tags-Pattern': '.*',
                            'Origin': 'https://front2.mercurestore.com', 
                            'Referer': 'https://front2.mercurestore.com/', 
                            'Host': 'stage.mercurestore.com',
                        }
                        response_for_purge = requests.request('PURGE', request.url, headers=headers_for_purge)
                        
                        print("Purging cache: " + str(request.url))
                        print("Purging response: " + str(response_for_purge.status_code))
                        
                        
                        # Warm URL Cache
                        headers = {
                            'Accept-Charset': 'UTF-8', 
                            'Origin': 'https://front2.mercurestore.com', 
                            'Referer': 'https://front2.mercurestore.com/', 
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36', 
                            'Content-Type': 'application/x-www-form-urlencoded', 
                            'Host': 'stage.mercurestore.com', 
                            'Connection': 'keep-alive', 
                            'Accept': '*/*', 
                            'Accept-Encoding': 'gzip, deflate, br', 
                            'Cookie': 'PHPSESSID=ataokjsr7q60cfqlp3gq01d52h; X-Magento-Vary=32d628c2559522aa14f1063a481ae6cc696fc48e; store=mercurestore_en', 
                        }

                        r = requests.post(request.url, headers=headers)            
                        header_array = json.dumps(str(r.headers))
                        header_array_decode = json.JSONDecoder().decode(header_array)
                        dictionary = eval(header_array_decode)
                    
                        x_varnish = ( "X-Varnish", dictionary.get("X-Varnish") )

                        print("Warming up cache: " + str(request.url))   
                        print("Varnish headers: " + str(x_varnish))  # print ('X-Varnish', 622799 229506)
                        print()

                        # print(str(request.url))

                    else:
                        print(f"{request.url}")
                        print("UNCACHEABLE")
                        print()
                    
driver.close()



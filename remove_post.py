from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import argparse
import pickle

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument("disable-gpu")
global driver
driver = webdriver.Chrome('chromedriver', options=chrome_options)

def login_page(url,email,password):
    try:
        driver.get(url)
        # get_login_email = driver.find_element_by_xpath("//input[@name='email']")
        get_login_email = driver.find_element(by=By.XPATH, value="//input[@name='email']")
        get_login_email.send_keys(email)
        time.sleep(2)
        # get_login_pass = driver.find_element_by_xpath("//input[@name='pass']")
        get_login_pass = driver.find_element(by=By.XPATH, value="//input[@name='pass']")
        get_login_pass.send_keys(password)
        time.sleep(2)
        # get_login_btn = driver.find_element_by_xpath("//input[@name='input']")
        get_login_btn = driver.find_element(by=By.XPATH, value="//input[@value='Log In']")
        get_login_btn.click()

        get_cookies = driver.get_cookies() 
        pickle.dump( get_cookies , open("cookiesFB.pkl","wb"))

        return get_cookies
    except Exception as e:
        print(e)
        return False

def go_to_profile(url,cookies):
    driver.get(url)

    for cookie in cookies:
        driver.add_cookie(cookie)

    time.sleep(5)
    return url + "/profile"

def get_profile_post(url):
    driver.get(url)

    try:        
        which_text = driver.find_element(by=By.XPATH, value="//div[@class='story_body_container']//p").text
        post_created_date = driver.find_element(by=By.XPATH, value="//div[@class='story_body_container']/following-sibling::footer/div/abbr").text
        get_container = driver.find_element(by=By.XPATH, value="//div[@id='tlFeed']/div[@class='feed']/section/article[1]")
        catch_more_elem = get_container.find_element(by=By.XPATH, value="//footer//a[text()='More']").get_attribute('href')
        
    except Exception as e:
        # print(e)
        catch_more_elem = None
        which_text = None
        post_created_date = None

    return catch_more_elem, {"text": which_text, "created_date": post_created_date}


def do_remove_post(link):
    driver.get(link) # go to page
    time.sleep(3)
    confirm_btn = driver.find_element(By.XPATH, value="//form//input[@type='submit' and @value='Submit']")
    try:
        get_delete_radio = driver.find_element(By.XPATH, value="//form//input[@type='radio' and @value='DELETE']")
        get_delete_radio.click()
        confirm_btn.click()
    except:
        try:
            remove_tag_profile = driver.find_element(By.XPATH, value="//form//input[@type='radio' and @value='UNTAG']")
            remove_tag_profile.click()
            confirm_btn.click()
        except:
            try:
                hide_from_profile = driver.find_element(By.XPATH, value="//form//input[@type='radio' and @value='HIDE_FROM_TIMELINE']")
                hide_from_profile.click()
                confirm_btn.click()
            except Exception as e:
                print(e)
                return False

    return True

if __name__ == "__main__":

    main_url = "https://mbasic.facebook.com"

    parser = argparse.ArgumentParser(description="Facebook Remove Old Post (for lazy person)")
    parser.add_argument('--email', dest='email', type=str, required=True)
    parser.add_argument('--pwd', dest='pwd', type=str, required=True)
    parser.add_argument('--limit', dest='limit', type=int)

    args = parser.parse_args()

    email = args.email
    password = args.pwd
    limit_post = args.limit if args.limit else 0

    try:
        login = pickle.load(open("cookiesFB.pkl", "rb"))
        print("Using Cookies")
    except:
        print("login session started")
        login = login_page(main_url,email,password)        
    
    print(f"You set delete limit on {limit_post}")
    print("=" * 70)
    que = 1
    if len(login) > 0:
        profilepage = go_to_profile(main_url, login)
        do_crawl = True
        while do_crawl:
            print(f"Now getting post url - [page:{que}]")
            moreinpost, content = get_profile_post(profilepage)
            print("Caption: ", content['text'])
            print("Post Created Date: ", content['created_date'])

            if moreinpost is not None:
                print("removing post")
                do_remove = do_remove_post(moreinpost)
                if do_remove:
                    print(f"You have successfully remove {que} post")
            else:
                print("post not found")
                break
            
            print("-" * 70)
            time.sleep(5)

            if limit_post > 0 and que == limit_post:
                do_crawl = False
            que += 1

    driver.close()
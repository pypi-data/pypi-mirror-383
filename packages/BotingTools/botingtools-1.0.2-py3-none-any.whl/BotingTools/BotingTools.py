import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
from random_username.generate import generate_username
from gpt4all import GPT4All
import socket
import random
import requests
import json
import urllib
import urllib.request
from urllib.request import urlopen
from selenium_recaptcha_solver import RecaptchaSolver
from fake_useragent import UserAgent
import undetected_chromedriver as uc
import stackapi
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from stackapi import StackAPI
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, video, concatenate_videoclips, clips_array, TextClip

class BotingTools:
    
    def __init__(self, BotingTools):
        self.BotingTools = BotingTools
    
    #------------#
    #   Others   #
    #------------#
    
    def ai_chat(prompt):
        model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf") # downloads / loads a 4.66GB LLM
        with model.chat_session():
            text = model.generate(prompt, max_tokens=1024)
        
        return text
    
    def delete_string(file, words):
        f = open(file, "r")
        lst = []
        for line in f:
            for word in words:
                if word in line:
                    line = line.replace(word,'')
            lst.append(line)
        f.close()
        f = open(file, "w")
        for line in lst:
            f.write(line)
        f.close()
    
    def delete_line(temp_file):
        file = open(temp_file, "r")
        lines = file.readlines()
        new_lines = []
        for line in lines:
            if "DNS" not in line.strip():
                new_lines.append(line)
        file = open(temp_file, "w")
        file.writelines(new_lines)
        file.close()
    
    def get_email():
        driver = Driver(uc=True, headless=True)
        driver.uc_activate_cdp_mode("https://email-fake.com")
        
        email = ""
        
        while email == "":
            try: #Consent Button
                driver.uc_click("/html/body/div[7]/div[2]/div[2]/div[2]/div[2]/button[1]")
            except:
                pass
                
            try: #Change Email Button
                driver.uc_click('/html/body/div[2]/div/div[2]/table/tbody/tr[2]/td[1]/a/button')
            except:
                pass

            time.sleep(0.5)
            
            try: #Get email Text
                email = driver.get_text("email_ch_text")
            except:
                pass
            
        driver.quit()
       
        return email
        
    #-----------#
    #   Proxy   #
    #-----------#
        
    def verify_tor_proxy(blocked_countries):
        #Check Ip
        http_proxy  = "socks5://127.0.0.1:9050"
        https_proxy = "socks5://127.0.0.1:9050"
        proxies = { 
                      "http"  : http_proxy, 
                      "https" : https_proxy, 
                    }
        ip_address = requests.get("http://wtfismyip.com/text", proxies=proxies).text
        ip_address = ip_address.rstrip()
        #print(ip_address)
        
        # create the url for the API, using f-string
        token = "3f4d82419bf119"
        url = f"https://www.ipinfo.io/{ip_address}?token={token}"

        # call the API and save the response
        with urlopen(url) as response:
            response_content = response.read()

        # parsing the response 
        data = json.loads(response_content)
        country = data['country']
        print(country)

        if country in blocked_countries:
            return True
        else:
            return False

    def create_tor_proxy(tor_path, torrc_path):
        #Delete Service
        os.system("sc delete tor")
        
        #Create Service
        arg = "" + tor_path + " --service install -options -f " + torrc_path
        os.system(arg)
    
    def renew_tor_proxy(tor_path, torrc_path):
        #Make Sure Service is Stopped
        os.system("sc stop tor")

        # Start Tor manually if not already running
        tor_process = subprocess.Popen(
            [tor_path, "-f", torrc_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for Tor SOCKS port (9050) to open
        start = time.time()
        while time.time() - start < 30:
            try:
                s = socket.create_connection(("127.0.0.1", 9050), timeout=2)
                s.close()
                break
            except OSError:
                time.sleep(1)
        else:
            raise RuntimeError("Tor did not start in time")
        
        os.system("sc qc tor")
        
        # Send NEWNYM to the control port (9051)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9051))
            s.sendall(b'AUTHENTICATE "yourpassword"\r\n')
            s.sendall(b'SIGNAL NEWNYM\r\n')

    def start_tor_proxy(blocked_countries, tor_path, torrc_path):
        BotingTools.renew_tor_proxy(tor_path, torrc_path)
        
        #Start Proxy With IP From Allowed Country
        i = 0
        while i == 0:
            if BotingTools.verify_tor_proxy(blocked_countries):
                BotingTools.renew_tor_proxy(tor_path, torrc_path)
            else:
                i = 1

    def inplace_change(temp_file, filename, old_string, new_string, temp_file_name):
        # Safely read the input filename using 'with'
        with open(filename) as f:
            s = f.read()

        # Safely write the changed content, if found in the file
        os.remove(temp_file)
        file = open(temp_file, "w")
        s = s.replace(old_string, new_string)
        file.truncate(0)
        file.write(s)

    def connect_vpn(websites, index_file, vpn_folder, temp_file, temp_file_name):    
        try: #Make Sure to quit Wireguard:
            command = '"C:\\Program Files\\WireGuard\\wireguard.exe" /uninstalltunnelservice %s' % (temp_file_name)
            proc = subprocess.Popen(command)
            subprocess.call("TASKKILL /f  /IM  wireguard.exe")
        except:
            pass
        
        #Get Website IP
        ip = ""
        o = 0
        for website in websites:
            o += 1
            ip += socket.gethostbyname(website)
            ip += "/24, "
            l = socket.gethostbyname(website).split(".")
            l[2] = int(l[2]) + 1
            temp = ""
            for i in range(len(l)):
                temp += str(l[i])
                if i < len(l) - 1:
                    temp += "."
            ip += temp
            ip += "/24, "
            l = socket.gethostbyname(website).split(".")
            l[2] = int(l[2]) - 1
            temp = ""
            for i in range(len(l)):
                temp += str(l[i])
                if i < len(l) - 1:
                    temp += "."
            ip += temp
            ip += "/24, "
        #remove Last ","
        a = [i for i, letter in enumerate(ip) if letter == ","]
        index = a[len(a)-1]
        ip = ip[:index] + ip[index+1:]
        
        #Get Index
        file = open(index_file, 'r')
        t = file.read() #read leaves file handle at the end of file
        if t == "":
            i = 0
        else:
            i = int(t)
        
        #Create List With OpenVPN Config Files
        f = []
        for (dirpath, dirnames, filenames) in walk(vpn_folder):
            f.extend(filenames)
            break
        if i >= len(f):
            i = 0
        
        #Get Config File Name
        config = f[int(i)]
        
        #Change Config File with Website Ip:
        file = "%s\\%s" % (vpn_folder, config)
        BotingTools.inplace_change(temp_file, file, "0.0.0.0/0", ip, temp_file_name)
        BotingTools.delete_string(temp_file, [", ::/0"])
        
        #Update Index File
        i += 1
        file = open(index_file, 'w')
        file.write(str(i))
        
        file = open(temp_file, 'r')
        #print(file.read())
        
        #Start OpenVpn
        command = '"c:\\Program Files\\WireGuard\\wireguard.exe" /installtunnelservice %s' % (temp_file)
        proc = subprocess.Popen(command) 

    #-------------#
    #   Account   #
    #-------------#

    def human_wait(min_seconds=0.5, max_seconds=2):
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def start_driver(websites, index_file, vpn_folder, temp_file, temp_file_name, website_to_login, chrome_version, headless=0):
        try:
            os.system("taskkill /im chrome.exe /f")
        except:
            pass
        
        #Generate a random User-Agent
        user_agent = UserAgent().random
        
        #Start Browser
        options = uc.ChromeOptions()
        if headless == 1:
            options.add_argument('--headless')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        options.add_argument(f"user-agent={user_agent}")
        driver = uc.Chrome(options=options, version_main=chrome_version)
       
        o = 0
        while o == 0:
            BotingTools.connect_vpn(websites, index_file, vpn_folder, temp_file, temp_file_name)
            time.sleep(5)
            
            try:
                driver.get(website_to_login)
                o = 1
            except TimeoutException as e:
                print("\n\n")
                print(f"[Timeout] {e}")
            except WebDriverException as e:
                print("\n\n")
                print(f"[Connection Error] {e.msg}")
        
        #Disable WebDriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        #Execute Cloudflare's challenge script
        driver.execute_script("return navigator.language")
        
        return driver
    
    def create_account(email, driver, website_loged_in, name_path=None, email_path=None, Pass_path=None, conf_pass_path=None, sign_button1_path=None, sign_button2_path=None):
        end = 0
        while end == 0:
            fill = 0
            captcha = 0
            signup = 0
            
            #Signup Button
            while signup == 0:
                try: 
                    driver.find_element(By.XPATH, sign_button1_path).click()
                    print("\nFILL: Signup Button Clicked")
                except:
                    print("\nFILL: Signup Button Fail")
                try: #Password
                    driver.find_element(By.XPATH, Pass_path).clear()
                    driver.find_element(By.XPATH, Pass_path).send_keys("A1ssssss!")
                    signup = 1
                    print("\nFILL: Password Filled")
                    BotingTools.human_wait()
                except:
                    pass
            
            #Fill Information
            while fill == 0:
                
                try:#Check if Filled
                    if driver.find_element(By.XPATH, Pass_path).get_attribute("value").strip() == "":
                        fill = 0
                    else:
                        fill = 1
                except:
                    pass
                
                try:#Check for Errors
                    mes = driver.find_element(By.XPATH, "/html/body").text
                    if mes == "e:Captcha is incorrect or has expired. Please try again.":
                        print("\ne:Captcha is incorrect or has expired. Please try again.")
                        driver.refresh()
                except:
                    pass
                
                try: #No Thanks Button           
                    driver.find_element(By.XPATH, "/html/body/div[14]/div[1]/div[2]/div/div[1]").click()
                    print("\nCREATE ACCOUNT: No Thanks Button Clicked")
                    BotingTools.human_wait()
                except:
                    pass
                
                try: #Name
                    driver.find_element(By.XPATH, name_path).clear()
                    driver.find_element(By.XPATH, name_path).send_keys(generate_username(1)[0])
                    print("\nCREATE ACCOUNT: Name Filled")
                    BotingTools.human_wait()
                except:
                    pass
                try: #Email
                    driver.find_element(By.XPATH, email_path).clear()
                    driver.find_element(By.XPATH, email_path).send_keys(email)
                    print("\nCREATE ACCOUNT: Email Filled")
                    BotingTools.human_wait()
                except:
                    pass
                try: #Password
                    driver.find_element(By.XPATH, Pass_path).clear()
                    driver.find_element(By.XPATH, Pass_path).send_keys("A1ssssss!")
                    print("\nCREATE ACCOUNT: Password Filled")
                    BotingTools.human_wait()
                except:
                    pass
                try: #Confirm Password
                    driver.find_element(By.XPATH, conf_pass_path).clear()
                    driver.find_element(By.XPATH, conf_pass_path).send_keys("A1ssssss!")
                    print("\nCREATE ACCOUNT: Confirm Password Filled")
                    BotingTools.human_wait()
                except:
                    pass
                   
            #Captcha
            while driver.current_url != website_loged_in and captcha == 0:
                
                try: #No Thanks Button           
                    driver.find_element(By.XPATH, "/html/body/div[14]/div[1]/div[2]/div/div[1]").click()
                    print("\nCAPTHCA: No Thanks Button Clicked")
                    BotingTools.human_wait()
                except:
                    pass
                
                solver = RecaptchaSolver(driver=driver)
                recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                solver.click_recaptcha_v2(iframe=recaptcha_iframe)
                
                #Check if Button is Clickable
                if driver.find_element(By.XPATH, sign_button2_path).is_enabled():
                    pass
                else:
                    captcha = 1
                    driver.refresh()
                    
                try: #Register Button
                    driver.find_element(By.XPATH, sign_button2_path).click()
                    print("\nCAPTCHA: Register Button Clicked")
                    time.sleep(10)
                except:
                    pass
    
    def registration_bonus(driver):
        verify = 0   
        while verify == 0:
            try:
                driver.find_element(By.ID, "free_play_error").click()
                print("\nVERIFY: Error")
                verify = 1
                end = 1
            except:
                pass
            try:
                driver.find_element(By.ID, "multiply_now_text").click()
                print("\nVERIFY: Close Play Now Window")
                verify = 1
                end = 1
            except:
                try:
                    element = driver.find_element(By.ID, "free_play_form_button")
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    element.click()
                    time.sleep(2)
                    print("\nVERIFY: Claim Button Clicked")
                except:
                    pass
            
            if "Someone has already played from this IP in the last hour." in driver.find_element(By.ID, "same_ip_error").text:
                print("\nVERIFY: Same IP Error")
                verify = 1
                end = 1

    #-------------#
    #   Youtube   #
    #-------------#
    
    def stackapi():
        #Retrieve The Text From Stack Overflow:
        SITE = StackAPI('stackoverflow')
        SITE.max_pages=1
        SITE.page_size=100
        
        #Create Anwsers
        time1 = random.randrange(1262304000, 1696118400)
        time2 = random.randrange(time1, 1696118400)
        question = SITE.fetch('questions', Key='4qArFpyh*TIw4)Man)R)7Q((', client_id=29098, fromdate=time1, todate=time2, max=1, pagesize=1, max_pages=1, sort='votes', filter='!9YdnSIN*P') #filter='quota_max'
        
        return question

    def text_to_video_2s(text, t, clip2_path, font_path):
        # Add text to Video
        clip = VideoFileClip(clip2_path) 
        txt_clip = TextClip(font_path, text, size=(1920, 1080), text_align='left', font_size=20, duration=2)  
        txt_clip.with_start(t)
        txt_clip.with_end(t + 2)
        clip = CompositeVideoClip([clip, txt_clip])

        #Calculate Timestamp
        t += 2

        a = [clip, t]
        return a

    def txt_to_img(t, i, img_folder, font_path):
    
        im = Image.new("RGB", (1920, 1080), "#fff")
        box = ((0, 0, 1920, 1080))
        draw = ImageDraw.Draw(im)
        #draw.rectangle(box, outline="#000")

        text = t
        font_size = 100
        size = None
        while (size is None or size[0] > box[2] - box[0] or size[1] > box[3] - box[1]) and font_size > 0:
            font = ImageFont.truetype(font_path, font_size)
            #size = font.getsize_multiline(text)
            dummy_img = Image.new("RGB", (1, 1))
            draw = ImageDraw.Draw(dummy_img)
            bbox = draw.multiline_textbbox((0, 0), text, font=font)
            size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
            font_size -= 1
        draw.multiline_text((box[0], box[1]), text, "#000", font)
        path = img_folder + str(i) + ".png"
        im.save(path)

    def text_to_video_30s(text, t, img_folder, clip1_path, img, font_path):
        # Add text to Video, add to img, add img to video
        clip = VideoFileClip(clip1_path) 
        BotingTools.txt_to_img(text, 1, img_folder, font_path)
        txt_clip = ImageClip(img)
        txt_clip.with_start(t)
        txt_clip.with_end(t + 30)
        clip = CompositeVideoClip([clip, txt_clip])

        #Calculate Timestamp
        t += 30
        
        a = [clip, t]
        return a
    
    def trend_script():
        # GET TREND #
        pytrend = TrendReq(hl='en-US', tz=360)
        print(pytrend)
        trends = pytrend.trending_searches()

        rand1=random.Random()
        num = rand1.randint(0, len(trends[0]))

        print("\nTrend: " + trends[0][num])
        
        return trends[0][num]
    
    def decide_topic():
        #Decide Topic Randomly:
        topics = ["programming", "python", "web Development", "html", "Computers", "Viruses", "Hacking", "Gamming"]
        rand1=random.Random()
        num = rand1.randint(0, len(topics))
        topic = topics[num - 1]
        print("\nQuiz Topic: " + topic)
        
        return topic
    
    def upload_quiz(driver, question, a1, a2, a3, a4, n):
        #   UPLOAD   #
        driver.get("https://www.youtube.com/@TheKnowledgeBase69/community")
        sleep(5)
            
        #quiz:    
        driver.find_element(By.CSS_SELECTOR, "span.style-scope:nth-child(4) > ytd-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > button:nth-child(1)").click()
        print("\nQuiz Button Clicked")
        
        print(2)
        
        #Question:
        driver.find_element(By.ID, "contenteditable-root").send_keys(question)
        print("\nQuiz Question Written")
        
        print(3)
        
        #Add Anwsers:
        driver.find_element(By.CSS_SELECTOR, "#quiz-attachment > div.button-container.style-scope.ytd-backstage-quiz-editor-renderer > yt-button-renderer > yt-button-shape > button").click()
        driver.find_element(By.CSS_SELECTOR, "#quiz-attachment > div.button-container.style-scope.ytd-backstage-quiz-editor-renderer > yt-button-renderer > yt-button-shape > button").click()
        print("\nQuiz Add Answer Button CLicked Twice")
        
        print(4)
        
        #anwser 1:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[1]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a1)
        print("\nQuiz Anwser 1 Written")
        
        print(5)
        
        #anwser 2:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[2]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a2)
        print("\nQuiz Anwser 2 Written")
        
        print(6)
        
        #anwser 3:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[3]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a3)
        print("\nQuiz Anwser 3 Written")
        
        print(7)
        
        #anwser 4:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[4]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a4)
        print("\nQuiz Anwser 4 Written")

        print(8)

        #Select Correct Anwser:
        if n == 1:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 1 Selected as Real")
        elif n == 2:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 2 Selected as Real")
        elif n == 3:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 3 Selected as Real")
        elif n == 4:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 4 Selected as Real")
        
        print(9)
        
        #Publish:
        WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='submit-button']/yt-button-shape/button"))).click()
        print("\nQuiz Publish Button Clicked")
            
        sleep(5)
        print("\nQuiz Sucessfully Uploaded")
        
    def upload_img(driver, path):
        driver.get("https://www.youtube.com/@TheKnowledgeBase69/community")
        print("\nMeme Youtube Opened")
        try:
            #Image:
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.ytd-backstage-post-dialog-renderer:nth-child(1) > ytd-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > button:nth-child(1)"))).click()
            print("\nMeme Image Button Clicked")
            
            sleep(1)
            
            #DRag'n'drop:
            elem = driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/div[2]/tp-yt-paper-input-container/div[2]/div/div[3]/ytd-backstage-multi-image-select-renderer/div[1]/input")
            driver.execute_script("arguments[0].scrollIntoView();", elem)
            elem.send_keys(path)
            print("\nMeme Image Drag and Drop Successfull")
            
            sleep(1)

            #Publish:                                                                          
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#submit-button > yt-button-shape:nth-child(1) > button:nth-child(1)"))).click()
            print("\nMeme Publish Button Clicked")
            
            sleep(5)
            print("\nMeme Uploaded Sucessfully")
        except:
            pass
    
    def create_video_trend(script, audio_path, video_clip_path, trend_video_path):
        #Text to Speech:
        language = 'en' 
        myobjAnwser = gTTS(text=script, lang=language, slow=False)
        myobjAnwser.save(audio_path)
        print("\nAudio Created")    
            
        clip = VideoFileClip(video_clip_path)
        audioclip = AudioFileClip(audio_path)
        duration = audioclip.duration
        videoclip = clip.subclipped(0, duration)

        new_audioclip = CompositeAudioClip([audioclip])
        videoclip.audio = new_audioclip
        videoclip.write_videofile(trend_video_path, threads=4, logger=None, ffmpeg_params=['-crf','18', '-aspect', '9:16'])

    def create_youtube_quiz(driver):
            topic = BotingTools.decide_topic()

            text = BotingTools.ai_chat("short quiz about " + topic + " with 3 fake anwsers and one real one. Include 1 question and 4 answers (for a total of FIVE senteces) seperated by the symbol |, have the question be first and the real anwser be second, include only the question and anwers and nothing else")
            
            print("\nText: " + text)
            words = text.split()
            t2 = text.split("|")
            print("\nQuiz: " + str(t2))
            
            # if text == "" or len(t2) > 5:
                # continue
            
            #Seperate Question and Anwsers:
            question = t2[0]
            real = t2[1]
            fake1 = t2[2]
            fake2 = t2[3]
            fake3 = t2[4]
            
            #Decide order of anwsers randomly
            a1 = ""
            a2 = ""
            a3 = ""
            a4 = ""
            rand=random.Random()
            n = rand.randint(1, 4)
            
            if n == 1:
                a1 = real
                a2 = fake1
                a3 = fake2
                a4 = fake3
                print("\nQuiz Order 1")
            if n == 2:
                a1 = fake1
                a2 = real
                a3 = fake2
                a4 = fake3
                print("\nQuiz Order 2")
            if n == 3:
                a1 = fake1
                a2 = fake2
                a3 = real
                a4 = fake3
                print("\nQuiz Order 2")
            if n == 4:
                a1 = fake1
                a2 = fake2
                a3 = fake3
                a4 = real
                print("\nQuiz Order 2")
            
            BotingTools.upload_quiz(driver, question, a1, a2, a3, a4, n)
    
    def create_youtube_meme(driver, img_path):
            text = BotingTools.ai_chat("Random short caption for a meme about Programming that you never told before, include only the caption and nothing else")
                
            # if text == "":
                # continue
                
            #Divide Caption to Fit Image
            i = 0
            t = ""
            words = text.split()
            for word in words:
                t += word + " "
                i += 1
                if i == 4:
                    i = 0
                    t += "\n"

            print("\nMeme Captcion: " + str(t))

            #Decide Wich Image to Use Randomy
            n = random.randrange(1,10)
            print("\nMeme Image " + str(n))
             
            #Delete Previous meme:
            try:
                os.remove(img_path) 
                print("\nMeme Deleted")
            except:
                print("\nMeme Delete Failed")
                pass
            
            # Open an Image
            path = img_path + ".jpg"
            print("\nMeme Image Opened")
             
            # Call draw Method to add 2D graphics in an image
            I1 = ImageDraw.Draw(img)

            # Add Text to an image
            font = ImageFont.truetype("impact.ttf", 125)
            I1.text((1500, 1500), t, (255, 255, 255), font, None, 5, "left")
            print("\nMeme Text Added")
             
            # Save the edited image
            img.save(img_path)
            print("\nMeme Saved")
            
            BotingTools.upload_img(driver, img_path)
    
    def create_youtube_trend(driver):
            trend1 = BotingTools.trend_script()

            script = BotingTools.ai_chat(trend1)
            # if script == "":
                # print("\nScript Empty")
                # continue

            BotingTools.create_video_trend(script)
            
            BotingTools.upload_video(driver, trend1, script)
    
    def create_info_video(driver, video_path, img_folder, clip1_path, img, clip2_path, font_path, out_folder, out_video_path):    
        t = 0
        
        #Delete Previous Folder:
        if os.path.exists(video_path):
            shutil.rmtree(video_path) 
            print("\nVideo Deleted")
            
        #Retrieve The Text From Stack Overflow:
        SITE = StackAPI('stackoverflow')
        SITE.max_pages=1
        SITE.page_size=100
        print("\nStack Overflow")
        
        #Create Anwsers
        time1 = random.randrange(1262304000, 1696118400)
        time2 = random.randrange(time1, 1696118400)
        question = SITE.fetch('questions', Key='4qArFpyh*TIw4)Man)R)7Q((', client_id=29098, fromdate=time1, todate=time2, max=1, pagesize=1, max_pages=1, sort='votes', filter='!9YdnSIN*P') #filter='quota_max'
        
        quest = []
        cont = 0
        for n in question['items']:
            quest = n
            if quest["is_answered"] == False:
                cont = 1
                #continue
            print(quest["title"])
        
        # if cont == 1:
            # print("\nBotingTools Continue")
            # continue
         
        #Make Sure Title Isn't to long for youtube
        titleQuest = quest['title']
        titleQuest = titleQuest[0:100]
            
        #Get Question Text and anwsers
        question = quest['body']
        question_id = quest['question_id']
        top_answer = SITE.fetch('questions/' + str(question_id) + '/answers', order = 'desc', sort='votes', filter='withbody')
        
        # ADD QUESTION TITLE TO VIDEO #
        #Format the Question Title:
        titleQuest2 = re.sub(r'\<a.+>', '', titleQuest)
        titleQuest2 = titleQuest2.replace('`', '"')
        question2 = re.sub(r'\<a.+>', '', question)
        question2 = question2.replace('`', '"')
        print("\nTitleQuest: " + titleQuest2)
        
        a = BotingTools.text_to_video_2s(titleQuest2, t, clip2_path, font_path)
        clip1 = a[0]
        t = a[1]
        
        # ADD QUESTION TEXT TO VIDEO #
        a = BotingTools.text_to_video_30s(question, t, img_folder, clip1_path, img, font_path)
        clip2 = a[0]
        t = a[1]
         
        # ADD ANWSERS TO VIDEO #
        k = 0
        anw = ""
        imports = ""
        txt_clips = [None] * 10
        clips = [None] * 10
        i = 0
        for n in range(10):
            clips[i] = VideoFileClip(clip2_path) 
            txt_clips[i] = TextClip(font_path, "", size=(1920, 1080), text_align='left', font_size=20, duration=1) 
            i += 1
        i = 0
        for index, an in zip(range(5), top_answer['items']):
            #Get Anwser Text
            AnwserText = an['body']
            k += 1
            
            #Format Answer Text
            AnwserText = re.sub(r'\<a.+>', '', AnwserText)
            AnwserText = AnwserText.replace('`', '"')
            print("\nAnwserText " + str(k) + " Formatted")
            
            anwserText1 = AnwserText
            
            #Create Anwser Title
            titleAnwser = "Anwser " + str(k) + ": "

            # ADD ANSWER TITLE TO VIDEO #
            a = BotingTools.text_to_video_2s(titleAnwser, t, clip2_path, font_path)
            clips[i] = a[0]
            t = a[1]
            i += 1
            
            # ADD ANSWER TEXT TO VIDEO #
            a = BotingTools.text_to_video_30s(AnwserText, t, img_folder, clip1_path, img, font_path)
            clips[i] = a[0]
            t = a[1]
            i += 1
                
        # Overlay the text clip with video 
        videos = [clip1, clip2]
        for clip in clips:
            videos.append(clip)
       
        clips = []
        
        i = 0
        for video in videos:
            p = out_folder + str(i) + ".mp4"
            if hasattr(video, "set_duration"):
                video = video.set_duration(30 if i % 2 else 2)
            elif hasattr(video, "with_duration"):
                video = video.with_duration(30 if i % 2 else 2)
            else:
                raise TypeError(f"Unknown clip type {type(video)} — cannot set duration")

            video.write_videofile(p, threads=4, audio = False, ffmpeg_params=['-crf','18', '-aspect', '16:9'])
            clips.append(VideoFileClip(p, target_resolution=(1080, 1920)))
            i += 1

        final_clip = concatenate_videoclips(clips)  # method="chain" by default. This is fine because all clips are the same size
        final_clip.write_videofile(out_video_path, threads=4, logger=None, audio = False, ffmpeg_params=['-crf','18', '-aspect', '16:9'])

        #Format Video Title
        titleQuest2 = titleQuest2.replace('&quot;', '"')
        titleQuest2 = titleQuest2.replace('&#vide39;', '"')
        print("\nTitleQuest Formatted")

        #   UPLOAD   #
        BotingTools.upload_video(driver, titleQuest2, out_video_path)
    
    def create_rot_short(driver, rot_video_path):
            
            k = 0
            script = BotingTools.ai_chat("Random Interesting Reddid Post With around 120 words, include only the reddit post text nothing else inclunding quotation marks", k)
            title = BotingTools.ai_chat("title for this script: " + script + ", include only the title nothing else", k)
            # if script == "":
                # continue
            
            print("\nTitle: " + title)
            print("\nScript: " + script)
            
            dur_final = 0
            clips, dur_final = BotingTools.create_video_Text(script)
            print("\nFinal Duration: " + str(dur_final))
            
            vid = concatenate_videoclips(clips)
            
            vid.duration = dur_final
            vid.write_videofile(rot_video_path, threads=4, ffmpeg_params=['-crf','18', '-aspect', '9:16'])
            print("\nVideo Created")
            
            title = script[0:90]
            
            BotingTools.upload_video(driver, title, script)
    
    def upload_video(driver, title, path):
        
        try:
            #Open Youtube Page
            driver.get("https://www.youtube.com/upload")
            
            #Upload Video
            driver.find_element(By.XPATH, "//input[@type='file']").send_keys(r"" + path + "")
            driver.implicitly_wait(5)
            
            sleep(2)

            #Add Title
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID, "textbox"))).clear()
            driver.implicitly_wait(5)
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID, "textbox"))).send_keys(title)
            driver.implicitly_wait(5)
        
            try: #Not Made For Kids Button
                driver.find_element(By.CSS_SELECTOR , "tp-yt-paper-radio-button.ytkc-made-for-kids-select:nth-child(2) > div:nth-child(1)").click()
                driver.implicitly_wait(5)
            except:
                pass    
            
            #Next Button
            driver.find_element(By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button").click()
            driver.implicitly_wait(5)
            driver.find_element(By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button").click()
            driver.implicitly_wait(5)
            driver.find_element(By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button").click()
            driver.implicitly_wait(5)      
            sleep(5)
            
            try:
                driver.find_element(By.XPATH, "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]/ytcp-button-shape/button").click()
                driver.implicitly_wait(5)
            except:
                pass
            
            #Publish Button
            try:
                driver.find_element(By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button").click()
                driver.implicitly_wait(5)
            except:
                pass
                
            #Wait for Video to load
            sleep(300)

            #Click Close Window Button
            driver.find_element(By.XPATH, "/html/body/ytcp-uploads-still-processing-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/ytcp-button/ytcp-button-shape/button").click()
            driver.implicitly_wait(5)
        
        except:
            pass
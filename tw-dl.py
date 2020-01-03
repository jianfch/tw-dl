import urllib.request
import urllib.parse
import sys
import time
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from getpass import getpass
from datetime import datetime
from datetime import timedelta


def contact():
    sys.stdout.write(
        '\nLooks like something went wrong. \n if you want to get to bottom of this, contact Jian#1737 '
        '@Discord')


def ask_then_check(valid_input, input_msg, error_msg, is_case_sensitive):
    # input has to be a list
    is_list = isinstance(valid_input, list)
    while True:
        final_input = input(f'{input_msg}')
        if is_case_sensitive:
            final_input = final_input.lower()
            if is_list:
                temp_input = []
                for val in valid_input:
                    temp_input.append(val.lower())
            else:
                valid_input = valid_input.lower()
        if is_list:
            if final_input not in valid_input:
                sys.stdout.write(f'{error_msg}\nInvalid input, please try again\n')
                continue
            else:
                break
        else:
            if valid_input not in final_input:
                sys.stdout.write(f'{error_msg}\nInvalid input, please try again\n')
                continue
            else:
                break

    return final_input

def ask_yes_no(input_msg):
    response = ask_then_check(['y', 'n'], f'{input_msg} (y/n):', 'enter only "y" or "n"', False)
    if response == 'y':
        return True
    return False


class Login:

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.user = ''
        self.pw = ''
        self.login_twitter()

    def login_twitter(self):
        while True:
            self.driver.get('https://twitter.com/login')
            try:
                WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located((By.TAG_NAME, 'nav')))
            except:
                display_msg('Ready to sign in')
                if self.user == '' and self.pw == '':
                    self.user = input('Enter email/username: ')
                    self.pw = getpass('Enter password (invisible): ')
                try:
                    self.driver.find_element_by_xpath('//*[@id="page-container"]/div/div[1]/form/fieldset/div[1]/input').click()
                except:
                    pass
                webdriver.ActionChains(self.driver).send_keys(self.user).perform()
                webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
                webdriver.ActionChains(self.driver).send_keys(self.pw).perform()
                webdriver.ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                time.sleep(2)
                try:
                    self.driver.find_element_by_id('message-drawer')
                except:
                    break
                else:
                    display_msg('Invalid login, please try again')

            else:
                break
        self.driver.back()


def scroll_to_bottom(driver):
    previous_height = driver.execute_script("return document.body.scrollHeight")
    final_list = []
    # sys.stdout.write('\nLoading pins...\n')
    fails = 0
    scroll_to_end = webdriver.ActionChains(driver).send_keys(Keys.END)
    while True:
        scroll_to_end.perform()
        time.sleep(0.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if previous_height != new_height:
            previous_height = new_height
            continue
        else:
            fails += 1
            if fails < 4:
                continue
            else:
                break


def assign_driver(options, driver_list):
    tests = 0
    for num in driver_list:
        try:
            driver = webdriver.Chrome(options=options, executable_path=f'drivers/chromedriver{num}.exe')
        except:
            tests += 1
            if tests < 3:
                continue
            else:
                sys.stdout.write('\nNot driver appears to work. This program requires chrome.')
                contact()
                break
        else:
            sys.stdout.write(f'\nChrome {num}')
            return driver


def get_soup(driver):
    return BeautifulSoup(driver.page_source, 'lxml')


def find_all_tweets(soup, is_signed_in):
    if is_signed_in:
        return soup.findAll('article')
    else:
        return soup.findAll(class_='js-stream-item stream-item stream-item')


def get_page_user(driver):
    return driver.current_url.split('/')[3]

# timeplus8 = convert_time(time, 8)

def scroll_find_tweets(driver, tweet_list, scroll_divider):
    previous_height = driver.execute_script("return document.body.scrollHeight")
    base_amount = driver.get_window_size()['height'] // scroll_divider
    scrolled_amount = base_amount
    sys.stdout.write('\nLoading tweets...\n')
    while True:
        driver.execute_script(f"window.scrollTo(0, {scrolled_amount})")
        time.sleep(0.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        scrolled_amount += base_amount
        twts = find_all_tweets(get_soup(driver), True)
        for twt in twts:
            if twt not in tweet_list:
                tweet_list.append(twt)
        if previous_height != new_height:
            previous_height = new_height
            continue
        else:
            if scrolled_amount < new_height:
                if (new_height - scrolled_amount) >= base_amount:
                    continue
                else:
                    scrolled_amount = new_height
                    continue
            else:
                return tweet_list


def get_date_from_text(tweet, typ='int'):
    try:
        date = tweet.find('time').text.split(', ')[0]
        # print('date: ' + date)
    except:
        date = ''
    text = str(tweet.text)
    text_split = text.split(' ')
    if len(text_split) > 1:
        if 'Retweeted' in text_split[1]:
            date += ', '
    date_from_text = text.split('·')
    if len(date_from_text) >= 2:
        # print(date)
        # print('b :' + date_in_text[1])
        date_from_text = date_from_text[1].replace(date, '') + ' '
        # print('a: ' + date_in_text)
        date_from_text = date_from_text.split(' ')[0] + 'x'*9
        # print(date_in_text + '1')
        date_from_text = date_from_text[:8]
        # print(date_in_text + '2')
    try:
        int(date_from_text)
        date_from_text = int(date_from_text[2:])
    except:
        try:
            test_val = date_from_text[:6]
            int(test_val)
            date_from_text = int(test_val)
        except:
            date_from_text = 0
    finally:
        if date_from_text < 100000:
            date_from_text = 0
        date_from_text = date_from_text * 1000000
        if typ == 'intlist' and date_from_text != 0:
            date_from_text = str(date_from_text)
            int_list = []
            for i in range(1, 7):
                end = i * 2
                start = end - 2
                int_list.append(int(date_from_text[start:end]))
            return int_list
        else:
            return date_from_text


def ask_location():
    while True:
        export_location = input('Please enter folder path for saving: ')
        if os.path.isdir(export_location):
            break
        else:
            sys.stdout.write('Invalid path, please try again. ')
            continue
    return export_location


def create_progress_file(file_path='logs/saved_presets.txt'):
    if not os.path.isdir('logs'):
        os.mkdir('logs')
    if not os.path.exists(file_path):
        file = open(file_path, 'w')
        file.close()
        return True
    else:
        return False


def get_current_time():
    return datetime.utcnow().strftime('%Y%m%d%H%M00')[2:]


def display_msg(msg, new_line=True, tbo=False, update=False):
    spacer = '\n'
    if not new_line:
        spacer = ''
    if update:
        sys.stdout.write(f'\r{msg}')
        sys.stdout.flush()
    else:
        if tbo:
            sys.stdout.write(spacer)
            sys.stdout.write(f'\r{msg}')
            sys.stdout.flush()
        else:
            sys.stdout.write(f'{msg}{spacer}')


class Tweet:

    @staticmethod
    def get_link(raw_tweet):
        link = ''
        raw_link = raw_tweet.findAll('a')
        if raw_link is None:
            return link
        else:
            for a in raw_link:
                href = a.get('href')
                if '/status/' in  href:
                    link = 'https://twitter.com/' + href
            return link

    @staticmethod
    def get_owner(raw_tweet):
        raw_owner = raw_tweet.findAll('a')
        if raw_owner is None:
            return ''
        else:
            return raw_owner[1].get('href')[1:]

    @staticmethod
    def get_text(raw_tweet):
        raw_text = raw_tweet.find(attrs={'lang':True})
        if raw_text is None:
            return ''
        else:
            return raw_text.text

    @staticmethod
    def get_date(raw_tweet):
        raw_date = raw_tweet.find('time')
        if raw_date is None:
            return -1
        else:
            return int(raw_date['datetime'].split('.')[0].replace('T', ':').replace('-', ':').replace(':', '')[2:])

    @staticmethod
    def convert_time_to_list(raw_time):
        raw_time = str(raw_time)
        time_list = []
        for i in range(1,(len(raw_time)//2)+1):
            end = i * 2
            start = end - 2
            time_list.append(int(raw_time[start:end]))
        return time_list

    @staticmethod
    def convert_timezone(initial_time, offset_hours):
        months_31 = [1, 3, 5, 7, 8, 10, 12]
        months_28 = [2]
        months_30 = [4, 6, 9, 11]

        def add_month(time_, months):
            temp_month = time_[1] + months
            if temp_month > 12:
                time_[1] = temp_month % 12
                time_[0] += temp_month // 12
            else:
                time_[1] = temp_month

        def add_day(time_, days):
            temp_days = time_[2] + days
            if time_[1] in months_31:
                if temp_days > 31:
                    time_[2] = temp_days % 31
                    add_month(time_, temp_days // 31)
                else:
                    time_[2] = temp_days
            if time_[1] in months_30:
                if temp_days > 30:
                    time_[2] = temp_days % 30
                    add_month(time_, temp_days // 30)
                else:
                    time_[2] = temp_days
            if time_[1] in months_28:
                if temp_days > 28:
                    time_[2] = temp_days % 28
                    add_month(time_, temp_days // 28)
                else:
                    time_[2] = temp_days

        def add_hour(time_, hours):
            temp_hour = time_[3] + hours
            if temp_hour > 24:
                time_[3] = temp_hour % 24
                add_day(time_, temp_hour // 24)
            else:
                time_[3] = temp_hour

        add_hour(initial_time, offset_hours)
        time_as_int = ''
        for val in initial_time:
            temp_val = '00' + str(val)
            time_as_int += temp_val[-2:]
        return int(time_as_int)

    @staticmethod
    def find_photos(raw_tweet):
        photo_list = []
        extras = []
        images = raw_tweet.findAll('img')
        if len(images) != 0:
            for image in images:
                link = image['src']
                if 'https://pbs.twimg.com/media' in link:
                    link = link.split('=')[:-1]
                    temp_link = ''
                    for sect in link:
                        temp_link += sect + '='
                    photo_list.append(temp_link + 'orig')
                elif 'https://pbs.twimg.com/profile_images' not in link:
                    extras.append(link)
                else:
                    continue
        return [photo_list,extras]

    @staticmethod
    def get_date_from_text(text=''):
        if text != '':
            text = text.replace('.', '').replace('-', '').replace('/', '').replace('\n', ' ').split(' ')[0]
        is_num = True
        try:
            int(text)
        except:
            is_num = False
        date = -1
        if is_num:
            length = len(text)
            if length == 6 or length == 8:
                if length == 8:
                    text = text[2:]
                date = int(text + '000000')
        return date

    @staticmethod
    def find_videos(raw_tweet):
        videos = raw_tweet.findAll('video')
        gif_list = []
        video_list = []
        for video in videos:
            video_src = video['src']
            if 'blob' in video_src:
                video_list.append(video_src)
            else:
                gif_list.append(video_src)
        return [gif_list, video_list]

    def __init__(self, raw_tweet, offset_hours, lapsed_hours):
        self.raw_tweet = raw_tweet
        self.link = self.get_link(self.raw_tweet)
        self.owner = self.get_owner(self.raw_tweet)
        self.offset_hours = offset_hours
        self.utc_date = self.get_date(self.raw_tweet)
        if self.utc_date > 0:
            self.is_ad = False
            self.utc_date_list = self.convert_time_to_list(self.utc_date)
            self.adjusted_date = self.convert_timezone(self.utc_date_list, self.offset_hours)
            self.adjusted_date_list = self.convert_time_to_list(self.adjusted_date)
        else:
            self.is_ad = True
            self.utc_date_list = []
            self.adjusted_date = -1
            self.adjusted_date_list = []
        img_list = self.find_photos(self.raw_tweet)
        self.photos = img_list[0]
        self.extras = img_list[1]
        self.text = self.get_text(self.raw_tweet)
        self.date_in_text = self.get_date_from_text(self.text)
        videos_list = self.find_videos(self.raw_tweet)
        self.gif = videos_list[0]
        self.video = videos_list[1]
        self.lapsed_hours = lapsed_hours
        self.content_type = self.type_of_content()
        if self.is_ad:
            self.identifier = ''
        else:
            self.identifier = self.owner + str(self.utc_date)

    def type_of_content(self):
        if self.date_in_text == -1:
            return 3  # miscellaneous
        else:
            post_date_kst = self.adjusted_date
            threshold_date = self.convert_timezone(self.convert_time_to_list(self.date_in_text), self.lapsed_hours)
            if threshold_date > post_date_kst:
                return 2  # preview
            else:
                return 1  # photo


class Preset:
    default_dict = {'page': None, 'category': 't', 'location': 'twitter', 'su': 0, 'start': 0, 'end': 0,
                    'finished': 0, 'wt': 0.25, 'speed': 0.5, 'oh': 9, 'lh': 36,
                    'mode': -1, 'gif': 1, 'us': 0, 'ds': 0, 'ps': 0, 'ts': 0, 'pd': 0, 'ap': 0, 'tp': 0}
    empty_dict = {'page': None, 'category': None, 'location': None, 'su': None, 'start': None, 'end': None,
                  'finished': None, 'wt': None, 'speed': None,  'oh': None, 'lh': None, 'mode': None,
                  'gif': None, 'us': None, 'ds': None, 'ps': None, 'ts': None, 'pd': None, 'ap': None, 'tp': None}
    valid_page_categories = ['t', 'r', 'm', 'l']
    valid_search_categories = ['t', 'l', 'p', 'v', 'c']
    preset_parameters_keys = {'-p': 'page', '-l': 'location', '-c': 'category', '-su': 'su', '-s': 'start', '-e': 'end',
                              '-f': 'finished', '-wt': 'wt', '-sp': 'speed',  '-oh': 'oh', '-lh': 'lh', '-g': 'gif',
                              '-m': 'mode', '-us': 'us', '-ds': 'ds', '-ps': 'ps', '-ts': 'ts', '-pd': 'pd', '-ap': 'ap',
                              '-tp': 'tp'}
    non_top_search = ['&f=live', '&f=image', '&f=video']

    @staticmethod
    def is_valid_date(d):
        d = str(d)
        length = len(d)
        try:
            int(d)
        except:
            return False
        if length != 6 and length != 12:
            if length == 1 and d == '0':
                return True
            # print('length')
            return False
        in_list_form = []
        if length == 6:
            d = d + '0'*6
        for i in range(1, 7):
            end = i * 2
            start = end - 2
            in_list_form.append(int(d[start:end]))
        if in_list_form[1] > 12:
            return False
        elif in_list_form[2] > 31:
            return False
        elif in_list_form[3] > 24:
            return False
        elif in_list_form[4] > 59:
            return False
        elif in_list_form[5] > 59:
            return False
        else:
            return True

    @staticmethod
    def is_int(line):
        try:
            int(line)
        except:
            return False
        else:
            return True

    @staticmethod
    def is_float(line):
        try:
            float(line)
        except:
            return False
        else:
            return True

    @staticmethod
    def overwrite_preset(old_preset_dict, new_preset_dict):
        for k in new_preset_dict.keys():
            if k in old_preset_dict.keys():
                old_preset_dict[k] = new_preset_dict[k]
        return old_preset_dict

    def __init__(self, preset_dict: dict, empty_base=False):
        base_dict = self.default_dict.copy()
        if empty_base:
            base_dict = self.empty_dict.copy()
        self.preset_dict = self.overwrite_preset(base_dict, preset_dict)
        self.page = self.preset_dict['page']
        self.category = self.preset_dict['category']
        self.location = self.preset_dict['location']
        self.su = self.preset_dict['su']
        self.start = self.process_raw_date(self.preset_dict['start'])
        self.end = self.process_raw_date(self.preset_dict['end'])
        self.done = self.preset_dict['finished']
        self.wt = self.preset_dict['wt']
        self.speed = self.preset_dict['speed']
        self.offset_hours = self.preset_dict['oh']
        self.lapsed_hours = self.preset_dict['lh']
        self.gif = self.preset_dict['gif']
        self.mode = self.preset_dict['mode']
        if self.is_top_category() and str(self.mode) == '-1':
            self.mode = 0
        self.by_post_date = self.preset_dict['pd']
        self.find_all_img = self.preset_dict['ap']
        self.user_sep = self.preset_dict['us']
        self.date_sep = self.preset_dict['ds']
        self.preview_sep = self.preset_dict['ps']
        self.type_sep = self.preset_dict['ts']
        self.temporary = self.preset_dict['tp']
        self.update_dates()

    def is_top_category(self):
        if self.page is not None:
            if self.is_search() or self.is_hashtag():
                for c in self.non_top_search:
                    if c in self.page:
                        return False
                return True
        return False

    def is_search(self):
        return self.page is not None and 'search?q=' in self.page

    def is_hashtag(self):
        return self.page is not None and 'hashtag/' in self.page

    def fill_in_preset(self, existing_preset: dict):
        for k in self.preset_dict.keys():
            if self.preset_dict[k] is None and k in existing_preset.keys():
                self.preset_dict[k] = existing_preset[k]
        self.update_preset()

    def get_list_empty(self):
        list_empty = []
        for k in self.preset_dict.keys():
            if self.preset_dict[k] == '' or self.preset_dict[k] is None:
                list_empty.append(k)
        return list_empty

    def get_link_from_dict(self, display_form=False):
        category = self.category
        if self.is_hashtag() or self.is_search():
            if category is None or category == 't':
                category = ''
            elif category == 'l':
                category = '&f=live'
            elif category == 'p':
                category = '&f=image'
            elif category == 'v':
                category = '&f=video'
            if display_form:
                return f'twitter.com/{self.page}{category}'
            else:
                return f'https://twitter.com/{self.page}{category}'
        else:
            if category is None or category == 't':
                category = ''
            elif category == 'r':
                category = '/with_replies'
            elif category == 'm':
                category = '/media'
            elif category == 'l':
                category = '/likes'
            if display_form:
                return f'twitter.com/{self.page}{category}'
            else:
                return f'https://twitter.com/{self.page}{category}'

    def finalize_non_nones(self):
        if self.su is not None:
            self.su = int(self.su)
        if self.start is not None:
            self.start = int(self.start)
            if len(str(self.start)) < 7:
                self.start = self.start*1000000
        if self.end is not None:
            self.end = int(self.end)
            if len(str(self.end)) < 7:
                self.end = self.end*1000000
        if self.done is not None:
            self.done = int(self.done)
        if self.wt is not None:
            self.wt = float(self.wt)
        if self.speed is not None:
            self.speed = float(self.speed)
        if self.offset_hours is not None:
            self.offset_hours = int(self.offset_hours)
        if self.lapsed_hours is not None:
            self.lapsed_hours = int(self.lapsed_hours)
        if self.mode is not None:
            if self.is_top_category() and str(self.mode) == '-1':
                self.mode = 0
            else:
                self.mode = int(self.mode)
        if self.by_post_date is not None:
            self.by_post_date = int(self.by_post_date)
        if self.find_all_img is not None:
            self.find_all_img = int(self.find_all_img)
        if self.user_sep is not None:
            self.user_sep = int(self.user_sep)
        if self.date_sep is not None:
            self.date_sep = int(self.date_sep)
        if self.preview_sep is not None:
            self.preview_sep = int(self.preview_sep)
        if self.type_sep is not None:
            self.type_sep = int(self.type_sep)
        if self.temporary is not None:
            self.temporary = int(self.temporary)
        if self.gif is not None:
            self.gif = int(self.gif)
        self.update_dict()

    def finalize_values(self):
        self.fill_in_preset(self.default_dict)
        self.finalize_non_nones()

    def update_dates(self):
        if self.start is None:
            if self.end is not None:
                self.set_start_max()
        else:
            if self.start == 0 and self.end != 0:
                self.set_start_max()

    def set_start_max(self):
        self.start = 900000000000

    def is_start_max(self):
        return self.start >= 900000000000

    def get_category_name(self):
        name = 'Top'
        if self.is_hashtag() or self.is_search():
            if self.category == 'l':
                name = 'Latest'
            elif self.category == 'p':
                name = 'Photos'
            elif self.category == 'v':
                name = 'Videos'
            elif self.category == 'c':
                name = 'Custom'
        else:
            name = 'Tweets'
            if self.category == 'r':
                name = 'Tweets & Replies'
            elif self.category == 'm':
                name = 'Media'
            elif self.category == 'l':
                name = 'Likes'
        return name

    def display_fmt(self):
        return f"-p:{self.page} -c:{self.get_category_name()} -l:'{self.location}' -su:{self.su} " \
               f"-s:{self.start} -e:{self.end} -f:{self.done} -wt:{self.wt} -sp:{self.speed} " \
               f"-oh:{self.offset_hours} -lh:{self.lapsed_hours} " \
               f"-m:{self.mode} -g:{self.gif} -us:{self.user_sep} -ds:{self.date_sep} " \
               f"-ps:{self.preview_sep} -ts:{self.type_sep} -pd:{self.by_post_date} -ap:{self.find_all_img} " \
               f"-tp:{self.temporary}"

    @staticmethod
    def process_raw_date(raw_date):
        if raw_date is not None:
            if isinstance(raw_date, str):
                try:
                    raw_date = int(raw_date.replace('.', ''))
                except:
                    pass
        return raw_date

    def update_preset(self, new_preset=''):
        if isinstance(new_preset, dict):
            for k in new_preset.keys():
                if k in self.preset_dict.keys():
                    self.preset_dict[k] = new_preset[k]
        self.page = self.preset_dict['page']
        self.category = self.preset_dict['category']
        self.location = self.preset_dict['location']
        self.su = self.preset_dict['su']
        self.start = self.process_raw_date(self.preset_dict['start'])
        self.end = self.process_raw_date(self.preset_dict['end'])
        self.done = self.preset_dict['finished']
        self.wt = self.preset_dict['wt']
        self.speed = self.preset_dict['speed']
        self.offset_hours = self.preset_dict['oh']
        self.lapsed_hours = self.preset_dict['lh']
        self.gif = self.preset_dict['gif']
        self.mode = self.preset_dict['mode']
        if self.is_top_category() and str(self.mode) == '-1':
            self.mode = 0
        self.by_post_date = self.preset_dict['pd']
        self.find_all_img = self.preset_dict['ap']
        self.user_sep = self.preset_dict['us']
        self.date_sep = self.preset_dict['ds']
        self.preview_sep = self.preset_dict['ps']
        self.type_sep = self.preset_dict['ts']
        self.temporary = self.preset_dict['tp']
        self.update_dates()
        self.update_dict()

    def meets_criteria(self, tweet: Tweet):
        if not tweet.is_ad:
            len_photos = len(tweet.photos)
            len_gif = len(tweet.gif)
            if len_photos == 0 and len_gif == 0:
                return False
            elif len_photos == 0 and len_gif != 0 and not self.gif:
                return False
            else:
                post_date = tweet.adjusted_date
                owner = tweet.owner
                if self.su != 0 and owner != self.su:
                    return False
                else:
                    if self.mode == -1:
                        if self.done:
                            if self.start > post_date > self.end:
                                return True
                        else:
                            if self.start == 0 or self.start < post_date or post_date < self.end:
                                return True
                            elif self.end == 0:
                                if post_date < self.start:
                                    return True
                    elif self.mode == 0:  # exclude
                        if self.start < post_date or post_date < self.end:
                            return True
                    else:  # mode == 1 include
                        if self.start > post_date > self.end:
                            return True
        return False

    def check_done_scrolling(self, post_date: int, mode: int):
        if mode == -1:
            if self.done:
                if post_date <= self.end:
                    self.completed()
                    return True
        elif mode == 1:
            if post_date <= self.end:
                return True
        return False

    def completed(self):
        self.done = 1
        self.end = self.start
        self.set_start_max()
        self.update_dict()

    def update_with_tweet(self, post_date: int):
        if self.mode == -1:
            if self.done:
                if self.is_start_max():
                    self.start = post_date
            else:
                if self.start == 0:
                    self.start = post_date
                    self.end = post_date
                else:
                    self.end = post_date
        self.update_dict()

    def update_dict(self):
        self.preset_dict = {'page': self.page, 'category': self.category, 'location': self.location, 'su': self.su,
                            'start': self.start, 'end': self.end, 'finished': self.done, 'wt': self.wt,
                            'speed': self.speed,  'oh': self.offset_hours, 'lh': self.lapsed_hours, 'mode': self.mode,
                            'gif': self.gif,  'us': self.user_sep, 'ds': self.date_sep, 'ps': self.preview_sep,
                            'ts': self.type_sep, 'pd': self.preview_sep, 'ap': self.find_all_img, 'tp': self.temporary}

    @staticmethod
    def is_int_0_1(val, name):
        report_line = ''
        if val is not None:
            if Preset.is_int(val):
                val = int(val)
                if val != 0 and val != 1:
                    report_line += f'{val} is invalid for {name}: Use: 1 or 0\n'
            else:
                report_line += f'{val} must be 1 or 0, You entered\n'
        return report_line

    def is_valid(self, report=False, allow_none_page=False):
        report_line = ''
        valid = True
        self.update_preset()
        if self.page is None and not allow_none_page:
            if report:
                report_line += f'No twitter page specified. If you used ">a" , ignore this\n'
                valid = False
            else:
                return False
        if self.category is not None:
            if self.is_hashtag() or self.is_search():
                if self.category not in self.valid_search_categories:
                    if report:
                        report_line += f'{self.category} is not a valid option. Valid categories are: {self.valid_search_categories}\n'
                        valid = False
                    else:
                        return False
            else:
                if self.category not in self.valid_page_categories:
                    if report:
                        report_line += f'{self.category} is not a valid option. Valid categories are: {self.valid_page_categories}\n'
                        valid = False
                    else:
                        return False
        if self.location is not None and not os.path.isdir(self.location) and self.location != self.default_dict['location']:
            if report:
                report_line += f'{self.location} does not exist.\n'
                valid = False
            else:
                return False
        if self.start is not None and not self.is_valid_date(self.start):
            if report:
                report_line += f'{self.start} is not a valid date. Use: YY.MM.DD.HH.MM.SS or YY.MM.DD\n'
                valid = False
            else:
                return False
        if self.end is not None and not self.is_valid_date(self.end):
            if report:
                report_line += f'{self.end} is not a valid date. Use: YY.MM.DD.HH.MM.SS or YY.MM.DD\n'
                valid = False
            else:
                return False
        if self.start is not None and self.end is not None:
            if self.start < self.end and self.start != 0 and self.start is not None:
                if report:
                    report_line += f'start date: {self.start_raw} must be not be less than end date{self.end_raw}\n'
                    valid = False
                else:
                    return False
        if self.wt is not None:
            if self.is_float(self.wt):
                self.wt = float(self.wt)
                if self.wt < 0.1:
                    if report:
                        report_line += f'-wt value less than 0.1 not allowed. You entered {self.wt}\n'
                        valid = False
                    else:
                        return False
            else:
                if report:
                    report_line += f'-wt must be a positive number. Recommend 0.5+\n'
                else:
                    return False
        if self.speed is not None:
            if self.is_float(self.speed):
                self.speed = float(self.speed)
                if self.speed < 0.1:
                    if report:
                        report_line += f'-sp value less than 0.1 not allowed. You entered {self.speed}\n'
                        valid = False
                    else:
                        return False
            else:
                if report:
                    report_line += f'-sp must be a number greater than 1. Recommend 2+\n'
                else:
                    return False
        if self.offset_hours is not None:
            if self.is_int(self.offset_hours):
                self.offset_hours = int(self.offset_hours)
                if 0 > self.offset_hours > 24:
                    if report:
                        report_line += f'-oh only 0 to 24. You entered {self.offset_hours}\n'
                        valid = False
                    else:
                        return False
            else:
                if report:
                    report_line += f'-oh must be an integer\n'
                else:
                    return False

        if self.lapsed_hours is not None:
            if self.is_int(self.lapsed_hours):
                self.lapsed_hours = int(self.lapsed_hours)
                if 0 > self.lapsed_hours:
                    if report:
                        report_line += f'-lh only positive integer. You entered {self.lapsed_hours}\n'
                        valid = False
                    else:
                        return False
            else:
                if report:
                    report_line += f'-lh must be an positive integer\n'
                else:
                    return False
        if self.mode is not None:
            if self.is_int(self.mode):
                self.mode = int(self.mode)
                if self.is_search() or self.is_hashtag():
                    if self.mode < 0:
                        if report:
                            report_line += f'-mode must be an integer 0 or 1 for "Top" category. You entered {self.mode}\n'
                            valid = False
                        else:
                            return False
                if self.mode < -1 or self.mode > 1:
                    if report:
                        report_line += f'-mode must be an integer -1 to 1. You entered {self.mode}\n'
                        valid = False
                    else:
                        return False
            else:
                if report:
                    report_line += f'-mode must be an integer -1 to 1. You entered {self.mode}\n'
                else:
                    return False
        done_report = self.is_int_0_1(self.done, '-f')
        if done_report != '':
            valid = False
            report_line += done_report
        gif_report = self.is_int_0_1(self.gif, '-g')
        if gif_report != '':
            valid = False
            report_line += gif_report
        us_report = self.is_int_0_1(self.user_sep, '-us')
        if us_report != '':
            valid = False
            report_line += us_report
        ts_report = self.is_int_0_1(self.type_sep, '-ts')
        if ts_report != '':
            valid = False
            report_line += ts_report
        ps_report = self.is_int_0_1(self.preview_sep, '-ps')
        if ps_report != '':
            valid = False
            report_line += ps_report
        ds_report = self.is_int_0_1(self.date_sep, '-ds')
        if ds_report != '':
            valid = False
            report_line += ds_report
        ap_report = self.is_int_0_1(self.find_all_img, '-ap')
        if ap_report != '':
            valid = False
            report_line += ap_report
        tp_report = self.is_int_0_1(self.temporary, '-tp')
        if tp_report != '':
            valid = False
            report_line += tp_report
        if report:
            return [valid, report_line]
        else:
            return valid


class LogFile:

    def __init__(self, location='', sub_folder='log', txt_file='saved_presets.txt', spacer = '#' * 5):
        self.spacer = spacer
        if location == '':
            location = os.getcwd()
        self.location = f'{location}\\{sub_folder}'
        self.full_path = f'{self.location}\\{txt_file}'
        is_new = False
        if not os.path.isdir(self.location):
            os.makedirs(self.location)
            is_new = True
        if not os.path.exists(self.full_path):
            file = open(self.full_path, 'w')
            file.close()
        self.is_new = self.is_saved_empty()
        self.temp_preset_list = []
        self.working_preset_num = -1

    def size(self):
        return len(self.temp_preset_list) + len(self.get_saved_preset_list())

    @staticmethod
    def open_file_as_lines(full_path):
        read_file = open(full_path, 'r')
        lines = read_file.read().split('|\n')
        read_file.close()
        if lines == ['']:
            return ''
        else:
            return lines

    @staticmethod
    def str_to_dict(line, spacer):
        final_dict = {}
        parts = line.replace('|', '').split(spacer)
        for i in range(1, ((len(parts)) // 2) + 1):
            k = i * 2
            start = k - 2
            end = k - 1
            final_dict[parts[start]] = parts[end]
        return final_dict

    @staticmethod
    def dict_to_str(preset_dict, spacer):
        final_line = ''
        count = 0
        for key in preset_dict.keys():
            key_str = str(key)
            val_str = str(preset_dict[key])
            if count == 0:
                final_line += key_str + spacer + val_str
            else:
                final_line += spacer + key_str + spacer + val_str
            count += 1
        return final_line

    @staticmethod
    def get_preset_list(saved_preset_list, page='', location=''):
        preset_list = []
        for i in range(len(saved_preset_list)):
            preset = saved_preset_list[i]
            if isinstance(preset, Preset):
                preset = preset.preset_dict
            if page != '' and location != '':
                if preset['page'] == page and preset['location'] == location:
                    preset_list.append([preset, i])
            elif location == '' and page != '':
                if preset['page'] == page:
                    preset_list.append([preset, i])
        # elif location != '' and page == '':
        #     for preset in saved_preset_list:
        #         if isinstance(preset, Preset):
        #             preset = preset.preset_dict
        #         if preset['location'] == location:
        #             preset_list.append(preset)
        return preset_list

    def update_log_with_tweet(self, preset):
        self.dict_to_file(preset, self.working_preset_num)

    def clear_temp_presets(self):
        if len(self.temp_preset_list) == 0:
            display_msg('Temporary Preset list is already empty')
        else:
            self.temp_preset_list = []
            display_msg('All Temporary Presets has been deleted')

    def clear_saved_presets(self):
        if self.is_saved_empty():
            display_msg('Saved Preset List is already empty')
        else:
            file = open(self.full_path, "w")
            file.close()
            display_msg('All Saved Presets has been deleted')

    def temp_preset_count(self):
        return len(self.temp_preset_list)

    def saved_preset_count(self):
        return len(self.open_file_as_lines(self.full_path))

    def is_saved_empty(self):
        empty = False
        file = open(self.full_path, 'r')
        if file.read() == '':
            empty = True
        file.close()
        return empty

    def is_temp_empty(self):
        return len(self.temp_preset_list) == 0

    def is_empty(self):
        return self.is_saved_empty() and self.is_temp_empty()

    def get_preset_dict_by_index(self, i):
        file_lines = self.open_file_as_lines(self.full_path)
        all_presets = []
        for line in file_lines:
            all_presets.append(self.str_to_dict(line, self.spacer))
        for preset in self.temp_preset_list:
            all_presets.append(preset.preset_dict)
        return all_presets[i]

    def dict_to_file(self, preset_dict, i=-1, overwrite_dict=(), delete=False, temporary=False):
        file_lines = self.open_file_as_lines(self.full_path)
        max_saved = len(file_lines)-1
        file_presets = []
        for line in file_lines:
            file_presets.append(self.str_to_dict(line, self.spacer))
        if i > max_saved:
            temp_i = i - (max_saved+1)
            if delete:
                self.temp_preset_list.pop(temp_i)
                display_msg(f'Preset {i} has been deleted')
            else:
                if isinstance(preset_dict, dict):
                    preset_dict = Preset(preset_dict)
                self.temp_preset_list[temp_i] = preset_dict
        elif temporary:
            self.temp_preset_list[i] = Preset(preset_dict)
        else:
            preset_dict_str = self.dict_to_str(preset_dict, self.spacer)
            if self.is_saved_empty() and not delete:
                file1 = open(self.full_path, 'a')
                file1.write(f'{preset_dict_str}')
                file1.close()
                self.is_new = False
            else:
                input_page = ''
                input_location = ''
                if i == -1:
                    input_page = preset_dict['page']
                    input_location = preset_dict['location']
                    if isinstance(overwrite_dict, dict):
                        input_page = overwrite_dict['page']
                        input_location = overwrite_dict['location']
                if not self.has_page(input_page, input_location) and not delete:
                    file = open(self.full_path, 'a')
                    file.write(f'|\n{preset_dict_str}')
                    file.close()
                else:
                    file = open(self.full_path, 'w')
                    adjustment = 0
                    for j in range(len(file_presets)):
                        if -1 < i == j and not delete:
                            final_line = preset_dict_str
                        else:
                            file_dict = file_presets[j]
                            file_page = file_dict['page']
                            file_location = file_dict['location']
                            if file_page == input_page and file_location == input_location:
                                if delete:
                                    if j == 0:
                                        adjustment = 1
                                    display_msg(f'Preset {j} has been deleted')
                                    continue
                                else:
                                    final_line = preset_dict_str
                            else:
                                if delete and -1 < i == j:
                                    if j == 0:
                                        adjustment = 1
                                    continue
                                final_line = file_lines[j]
                        next_line = ''
                        if j - adjustment > 0:
                            next_line = '|\n'''
                        file.write(f'{next_line}{final_line}')
                    file.close()

    def get_saved_preset_list(self, page='', location=''):
        saved_preset_list = []
        for line in self.open_file_as_lines(self.full_path):
            saved_preset_list.append(Preset(self.str_to_dict(line, self.spacer)))
        if page != '':
            return self.get_preset_list(saved_preset_list, page, location)
        else:
            return saved_preset_list

    def add_temp_preset(self, preset_dict):
        self.temp_preset_list.append(preset_dict)

    def get_temp_preset_list(self, page='', location=''):
        if page == '':
            return self.temp_preset_list
        else:
            return self.get_preset_list(self.temp_preset_list, page, location)

    def has_page(self, input_page='', input_location=''):
        if len(self.get_saved_preset_list(page=input_page, location=input_location)) == 0:
            return False
        else:
            return True

    def find_preset_to_overwrite(self, preset: Preset):
        page = preset.page
        if page is None:
            page = ''
        location = preset.location
        if location is None:
            location = ''
        preset_list = []
        value = -1
        if preset.temporary == 1:
            found_need_overwrite = self.get_temp_preset_list(page=page, location=location)
        else:
            found_need_overwrite = self.get_saved_preset_list(page=page, location=location)
        if len(found_need_overwrite) == 0:
            if preset.temporary == 1:
                found_same_page = self.get_temp_preset_list(page=preset.page)
            else:
                found_same_page = self.get_saved_preset_list(page=preset.page)
            found_page_count = len(found_same_page)
            if found_page_count > 0:
                value = 1
                if found_page_count < 2:
                    value = 0
                preset_list = found_same_page
        else:
            value = 0
            preset_list = found_need_overwrite

        return [value] + preset_list


class ProgressDisplay:

    def __init__(self, preset_count: int, working_path='', current_action='', on_count=0, on_page='', image_count=0, gif_count=0, tweet_count=0):
        self.preset_count = preset_count
        self.on_page = on_page
        self.on_count = on_count
        self.working_path = working_path
        self.current_action = current_action
        self.image_count = image_count
        self.gif_count = gif_count
        self.tweet_count = tweet_count
        self.first_line = True

    def update_progress(self, preset_count=None, working_path=None, current_action=None, on_count=None, on_page=None, image_count=None, gif_count=None, tweet_count=None):
        if preset_count is not None:
            self.preset_count = preset_count
        if on_page is not None:
            self.on_page = on_page
        if on_count is not None:
            self.on_count = on_count
        if working_path is not None:
            self.working_path = working_path
        if current_action is not None:
            self.current_action = current_action
        if image_count is not None:
            self.image_count += int(image_count)
        if gif_count is not None:
            self.gif_count += int(gif_count)
        if tweet_count is not None:
            self.tweet_count += int(tweet_count)
        self.display_progress()

    def display_progress(self):
        page = self.on_page
        if len(page) > 15:
            page = page[:12]+'...'
        page = page + (' '*15)
        t_count = str(self.tweet_count)
        if len(t_count) < 6:
            t_count = t_count + (' '*7)
        p_count = str(self.image_count)
        if len(p_count) < 5:
            p_count = p_count + (' '*6)
        g_count = str(self.gif_count)
        if len(g_count) < 4:
            g_count = g_count + (' '*5)
        update = f'{self.current_action}...{self.working_path}' + (' '*46)
        display_msg(
            f'Preset:{self.on_count}/{self.preset_count}  {page[:15]}  [Found Tweet(s):{t_count[:6]}]  [Images:{p_count[:5]} Gifs:{g_count[:4]}] {update[:45]}'
            ,
            tbo=self.first_line, update=not self.first_line)
        if self.first_line:
            self.first_line = False


class Downloader:

    @staticmethod
    def get_save_path(date, text_date, typ, main_folder, page: str, user_separation=0, date_separation=0, preview_separation=0,
                      type_separation=0, only_post_date=0):
        location = ''
        spacer = '/'
        file_name = ''
        date = str(date)
        text_date = str(text_date)
        final_date = date[:6]
        if only_post_date == 0 and len(text_date) > 5:
            final_date = text_date[:6]
        if '\\' in main_folder:
            spacer = '\\'
        location += main_folder
        # print('1 ' + location)
        if user_separation == 1:
            location += spacer + page
        # print('2 ' + location)
        if type_separation == 1:
            if preview_separation == 0:
                if typ == 2:
                    typ = 1
            if typ == 2:
                location += spacer + 'Previews'
            elif typ == 1:
                location += spacer + 'Photos'
            else:
                location += spacer + 'Miscellaneous'
        # print('4 ' + location)
        if date_separation == 1:
            location += spacer + final_date
        # print('5 ' + location)
        file_name += final_date
        # print('6 ' + location)
        return [location, file_name]

    def __init__(self, logfile: LogFile, driver, login: Login):
        self.log_file = logfile
        self.driver = driver
        self.saved_counts = {}
        self.login = login

    def finalize_path(self, save_path: list, ext):
        folder = save_path[0]
        file_name = save_path[1]
        slash = '/'
        if '\\' in folder:
            slash = '\\'
        if not os.path.isdir(folder):
            os.makedirs(folder)
        while True:
            if file_name not in self.saved_counts.keys():
                self.retrieve_count(folder, file_name, ext, slash)
            n = self.saved_counts[file_name]
            self.saved_counts[file_name] += 1
            return folder + slash + file_name + f'0000{n}'[-4:] + ext

    def retrieve_count(self, folder, file_name, ext, slash):
        n = 0
        while True:
            full_path = folder + slash + file_name + f'0000{n}'[-4:] + ext
            if os.path.exists(full_path):
                n += 1
                continue
            else:
                self.saved_counts[file_name] = n
                break

    def update(self, logfile: LogFile, driver):
        self.log_file = logfile
        self.driver = driver

    def is_signed_in(self):
        while True:
            try:
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.TAG_NAME, 'nav')))
            except:
                self.login.login_twitter(self.driver)
                # is_signed = False
            finally:
                return True

    def start_downloads(self):
        all_list = self.log_file.get_saved_preset_list()
        all_list += self.log_file.get_temp_preset_list()
        preset_count = len(all_list)
        progress_display = ProgressDisplay(preset_count, current_action='Starting')
        start_time = time.time()
        for i in range(preset_count):
            preset = all_list[i]
            preset.finalize_values()
            self.log_file.working_preset_num = i
            progress_display.update_progress(current_action='Starting Downloads', on_count=i+1, on_page=preset.page)
            self.scroll_while_saving(preset, progress_display)
            progress_display.update_progress(current_action='', working_path='')
            folder = preset.location
            if '\\' not in preset.location:
                folder = os.getcwd() + '\\' + folder.replace('/', '\\')
        total_sec = time.time() - start_time
        total_time = timedelta(seconds=round(total_sec))
        display_msg(f"\nCompleted in {total_time}. Your downloads are saved in: '{folder}'")

    def download_content(self, preset: Preset, tweet: Tweet, progress_display: ProgressDisplay):
        for photo in tweet.photos:
            save_path = self.get_save_path(date=tweet.adjusted_date, text_date=tweet.date_in_text, typ=tweet.type_of_content(),
                                           main_folder=preset.location, page=tweet.owner,
                                           user_separation=preset.user_sep, date_separation=preset.date_sep,
                                           preview_separation=preset.preview_sep, type_separation=preset.type_sep,
                                           only_post_date=preset.by_post_date)
            full_path = self.finalize_path(save_path, '.jpg')
            progress_display.update_progress(image_count=1)
            # print(full_path)
            # print(photo, full_path)
            urllib.request.urlretrieve(photo, full_path)
        if preset.gif:
            for mp4 in tweet.gif:
                slash = '/'
                if '\\' in preset.location:
                    slash = '\\'
                full_path = self.finalize_path([preset.location+slash+'gif', str(tweet.utc_date)[:6]], '.mp4')
                progress_display.update_progress(gif_count=1)
                # print(full_path)
                # print(mp4, full_path)
                urllib.request.urlretrieve(mp4, full_path)

    def scroll_while_saving(self, preset, progress_display):
        preset.finalize_values()
        driver = self.driver
        self.driver.get(preset.get_link_from_dict())
        time.sleep(preset.wt)
        tweet_list = []
        previous_height = driver.execute_script("return document.body.scrollHeight")
        base_amount = driver.get_window_size()['height'] // preset.speed
        scrolled_amount = base_amount
        is_finished = False
        is_signed = self.is_signed_in()
        first_time = True
        fail_count = 0
        while True:
            if not first_time:
                if scrolled_amount > previous_height:
                    scrolled_amount = previous_height
                driver.execute_script(f"window.scrollTo(0, {scrolled_amount})")
                scrolled_amount += base_amount
                time.sleep(preset.wt)
            new_height = driver.execute_script("return document.body.scrollHeight")
            tweets = find_all_tweets(get_soup(driver), is_signed)
            first_time = False
            for tweet in tweets:
                tweet = Tweet(tweet, preset.offset_hours, preset.lapsed_hours)
                post_date = tweet.utc_date
                if preset.check_done_scrolling(post_date, preset.mode):
                    is_finished = True
                    break
                if tweet.identifier not in tweet_list:
                    progress_display.update_progress(current_action='Processing tweet', working_path=tweet.identifier)
                    tweet_list.append(tweet.identifier)
                    progress_display.update_progress(tweet_count=1)
                    if preset.meets_criteria(tweet):
                        self.download_content(preset, tweet, progress_display)
                        preset.update_with_tweet(post_date)
                        self.log_file.update_log_with_tweet(preset.preset_dict)
                else:
                    continue

            if is_finished:
                break
            else:
                if previous_height != new_height:
                    previous_height = new_height
                    continue
                else:
                    if scrolled_amount < previous_height:
                        if (new_height - scrolled_amount) >= base_amount:
                            continue
                        else:
                            scrolled_amount = new_height
                            continue
                    else:
                        fail_count += 1
                        if fail_count < 4:
                            time.sleep(1)
                            continue
                        if preset.mode == -1:
                            preset.completed()
                            self.log_file.dict_to_file(preset.preset_dict)
                        break


class CustomCommand:

    @staticmethod
    def remove_blanks(lst):
        final_lst = []
        for val in lst:
            if val != '':
                final_lst.append(val)
        return final_lst

    @staticmethod
    def pop_val(line, begin, spacer=' '):
        pop = ''
        first_split = line.split(begin)
        if len(first_split) > 1:
            for v in first_split[1].split(spacer):
                if v != '':
                    pop = v
                    break
        return pop

    @staticmethod
    def display_found_presets(preset, i=''):
        title = '|Saved| '
        if isinstance(preset, dict):
            preset = Preset(preset)
            if preset.temporary == 1:
                title = '|Temporary| '
        display_msg(f'{title} {i}: {preset.display_fmt()}')

    @staticmethod
    def find_all_users(soup: BeautifulSoup):
        user_list = []
        followers = soup.find(attrs={"aria-label": "Timeline: Following"})
        if followers is None:
            followers = soup.find(attrs={"aria-label":"Timeline: Search timeline"})
        if followers is None:
            followers = soup.find(attrs={"aria-label":"Timeline: List members"})
        if followers is None:
            followers = soup.find(attrs={"aria-label":"Timeline: Followers"})
        if followers is not None:
            users = followers.findAll(attrs={'data-testid':'UserCell'})
            if users is not None:
                for f in users:
                    user_list.append(f.find('a').get('href')[1:])
        return user_list

    @staticmethod
    def cut_line(line, begin, end):
        temp_line_b = line.split(begin)[0]
        temp_line_e = line.split(end)
        fixed_line_e = ''
        for i in range(len(temp_line_e)):
            if i == 1:
                fixed_line_e += temp_line_e[i]
            elif i > 1:
                fixed_line_e += end + temp_line_e[i]

        return temp_line_b + fixed_line_e

    @staticmethod
    def is_int(line):
        try:
            int(line)
        except:
            return False
        else:
            return True

    @staticmethod
    def is_float(line):
        try:
            float(line)
        except:
            return False
        else:
            return True

    @staticmethod
    def begins_with_twitter_link(line):
        line = line.split(' ')
        if len(line) > 1:
            line = line[1]
        else:
            line = line[0]
        return len(line.split('twitter.com/')) == 2

    def __init__(self, driver, preset_parameters_keys, log_file=LogFile(), command_str=''):
        self.log_file = log_file
        self.command_str = command_str
        self.driver = driver
        self.exited = False
        self.preset_parameters_keys = preset_parameters_keys
        self.login = Login(main_driver)
        self.page_list_to_add = []

    def execute_commands(self):
        if self.command_str == '':
            self.display_presets()
        if self.has_add_list():
            self.add_list()
        if self.has_preset() or len(self.page_list_to_add) > 0:
            self.process_preset()
        if self.has_delete():
            self.delete_page()
        if self.has_run():
            if self.log_file.is_empty():
                display_msg('No Recorded Presets')
            else:
                Downloader(self.log_file, self.driver, self.login).start_downloads()
        if self.has_exit():
            self.driver.quit()
            self.exited = True

    def get_values_after(self, splitting_point, spacer=' '):
        input_values = self.command_str.split(splitting_point)
        values = []
        if len(input_values) > 1:
            for val in input_values[1].split(spacer):
                if val != '':
                    values.append(val)
        return values

    def add_list(self):
        input_values = self.get_values_after('>a')
        val_count = len(input_values)
        if val_count == 0:
            display_msg('Please provide values for >a:')
            self.command_str = ''
        else:
            user_list = input_values[0]
            if user_list == 'f':
                self.remove_from_command('>a', 'f')
                self.driver.get('https://twitter.com/home')
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.TAG_NAME, 'nav')))
                self.driver.get(f'https://twitter.com/{self.get_current_user()}/following')
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.TAG_NAME, 'section')))
                self.page_list_to_add = self.scroll_find_users()
            elif self.begins_with_twitter_link(user_list):
                self.remove_from_command('>a', user_list)
                self.driver.get(user_list)
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.TAG_NAME, 'section')))
                self.page_list_to_add = self.scroll_find_users()
            else:
                display_msg(f'{user_list} is invalid. Please provide a link to list of pages or use "f" following ">a "')
                self.command_str = ''

    def remove_from_command(self, param, val):
        previous_len = len(self.command_str)
        n = 0
        while True:
            spacer = ' '*n
            full_param = f'{param}{spacer}{val}'
            self.command_str = self.command_str.replace(full_param, '')
            if len(self.command_str) == previous_len:
                if n > 5:
                    break
                n += 1
                continue
            else:
                break

    def get_current_user(self):
        soup = get_soup(self.driver)
        return soup.find('nav').find(attrs={"aria-label": "Profile"}).get('href')[1:]

    def has_add_list(self):
        return '>a' in self.command_str

    def scroll_find_users(self, speed=1.5, wait_time=0.5):
        driver = self.driver
        user_list = []
        previous_height = driver.execute_script("return document.body.scrollHeight")
        base_amount = driver.get_window_size()['height'] // speed
        scrolled_amount = base_amount
        first_time = True
        fail_count = 0
        while True:
            if not first_time:
                driver.execute_script(f"window.scrollTo(0, {scrolled_amount})")
                time.sleep(wait_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            scrolled_amount += base_amount
            users = self.find_all_users(get_soup(driver))
            first_time = False
            for user in users:
                if user not in user_list:
                    user_list.append(user)
                    user_count = len(user_list)
                    user_count_display = '[' + 'Count:' + str(user_count) + ']' + ' '*17
                    user_display = '[' + str(user_list[-1]) + ']' + ' '*19
                    is_first = user_count == 1
                    display_msg(f'{user_count_display[:16]} {user_display[:18]}', tbo=is_first, update=not is_first)
                else:
                    continue
            if previous_height != new_height:
                previous_height = new_height
                continue
            else:
                if scrolled_amount < new_height:
                    if (new_height - scrolled_amount) >= base_amount:
                        continue
                    else:
                        scrolled_amount = new_height
                        continue
                else:
                    fail_count += 1
                    if fail_count < 4:
                        time.sleep(1)
                        continue
                    if len(user_list) == 0:
                        display_msg('Found no twitter pages.')
                    break
        display_msg('')
        return user_list

    def has_page_to_add(self):
        return len(self.page_list_to_add) != 0

    def process_preset(self):
        if self.command_str != '' or self.has_page_to_add():
            extract = self.extract_preset()
            preset = extract[0]
            index = extract[1]
            preset_list = []
            if isinstance(preset, dict):
                preset = Preset(preset, empty_base=True)
            if preset.is_valid(allow_none_page=self.has_page_to_add()) and isinstance(index, int):
                preset.finalize_non_nones()
                if self.has_page_to_add():
                    for page in self.page_list_to_add:
                        preset_dict = preset.preset_dict.copy()
                        preset_dict['page'] = page
                        preset_list.append(Preset(preset_dict))
                else:
                    preset_list = [preset]
                for preset in preset_list:
                    existing_presets = self.log_file.find_preset_to_overwrite(preset)
                    if existing_presets[0] == -1:
                        self.add_preset(preset)
                    elif existing_presets[0] == 0:
                        found_preset = existing_presets[1]
                        display_msg('An existing preset with same page and location has been found, you can only overwrite. "None" value will not overwrite.')
                        self.display_found_presets(found_preset[0])
                        display_msg(f'|overwrite| {preset.display_fmt()}')
                        overwrite = ask_then_check(['y', 'n'], 'y: overwrite with specified values; n: skip (y/n):', 'Enter "y" or "n":', False)
                        if overwrite == 'y':
                            if index == -1:
                                preset.fill_in_preset(found_preset[0])
                                self.log_file.dict_to_file(preset.preset_dict, overwrite_dict=found_preset[0])
                            else:
                                if preset.temporary == 1:
                                    self.log_file.dict_to_file(preset, i=found_preset[1], temporary=True)
                                else:
                                    self.log_file.dict_to_file(preset.preset_dict, index)
                    elif existing_presets[0] == 1:
                        display_msg('Existing preset(s) with same page has been found. "None" value will not overwrite')
                        for i in range(len(existing_presets[1:])):
                            found_preset = existing_presets[1:][i]
                            self.display_found_presets(found_preset[0], str(i))
                        display_msg(f'|overwrite| {preset.display_fmt()}')
                        overwrite = ask_then_check(['y', 'n', ''], 'y: overwrite with specified values; n: no overwrite just add preset; blank: skip (y/n/blank):', 'Enter "y" or "n" or blank:',
                                                   False)
                        if overwrite == 'y':
                            while True:
                                value = input('Which preset would you like to overwrite, enter corresponding number or blank to cancel: ')
                                if value == '':
                                    break
                                try:
                                    int(value)
                                except:
                                    display_msg('only integers please')
                                    continue
                                else:
                                    len_found = len(existing_presets[1:])
                                    input_val = int(value)
                                    max_val = len_found - 2
                                    if input_val > max_val:
                                        display_msg(f'must be from 0 to {max_val}. you entered: {value}')
                                        continue
                                    else:
                                        chosen_preset = existing_presets[input_val+1][0]
                                        preset.fill_in_preset(chosen_preset)
                                        self.log_file.dict_to_file(preset.preset_dict, overwrite_dict=chosen_preset)
                                        break
                        else:
                            preset.finalize_values()
                            self.log_file.dict_to_file(preset.preset_dict)
                self.page_list_to_add = []
            else:
                display_msg(preset.is_valid(True)[1])

    def has_exit(self):
        return self.command_str == '>e'

    def delete_page(self):
        if self.log_file.is_empty():
            display_msg('No preset are saved.')
        else:
            values = self.extract_del_values()
            delete_val = values[0].lower()
            if delete_val == 'all':
                val_count = len(values[1:])
                if val_count == 0:
                    if ask_yes_no('Are you sure you want to delete all Saved and Temporary Preset'):
                        self.log_file.clear_temp_presets()
                        self.log_file.clear_saved_presets()
            elif delete_val == 't':
                if ask_yes_no('Are you sure you want to delete all Temporary Preset'):
                    self.log_file.clear_temp_presets()
            elif delete_val == 's':
                if ask_yes_no('Are you sure you want to delete all Saved Presets'):
                    self.log_file.clear_saved_presets()
            else:
                valid = False
                for val in values:
                    try:
                        int(val)
                    except:
                        display_msg(f'{val} is not an integer corresponding with preset')
                    else:
                        val = int(val)
                        max_val = self.log_file.size()-1
                        if val > max_val:
                            display_msg(f'{max_val} is max value.You entered {val}')
                        else:
                            valid = True
                if valid:
                    for i in range(len(values)):
                        values[i] = int(values[i])
                    values = list(set(values))
                    values.sort()
                    for i in values[::-1]:
                        self.log_file.dict_to_file({}, i=i, delete=True)
        self.display_presets()

    def add_preset(self, preset: Preset):
        preset.finalize_values()
        if preset.temporary == 1:
            self.log_file.add_temp_preset(preset)
        else:
            self.log_file.dict_to_file(preset.preset_dict)
        display_msg(f'Added: {preset.display_fmt()}')

    def extract_del_values(self):
        try:
            return self.remove_blanks(self.command_str.replace('>d', '').split(' '))
        except:
            return 'No Value'

    @staticmethod
    def extract_page_location_list(preset_list):
        page_location_list = []
        for preset in preset_list:
            page_location_list.append(preset.page+preset.location)
        return page_location_list

    def display_presets(self):
        saved_list = self.log_file.get_saved_preset_list()
        saved_list_identifier = self.extract_page_location_list(saved_list)
        temp_list = self.log_file.get_temp_preset_list()
        temp_list_identifier = self.extract_page_location_list(temp_list)
        display_msg('\n____Saved Presets____')
        i = 0
        if len(saved_list) == 0:
            display_msg('None')
        else:
            for preset in saved_list:
                star = ''
                if (preset.page+preset.location) in temp_list_identifier:
                    star = '*'
                display_msg(f'{i}{star}: {preset.display_fmt()}')
                i += 1
        display_msg('____Temporary Presets____')
        if len(temp_list) == 0:
            display_msg('None\n')
        else:
            for preset in temp_list:
                star = ''
                if (preset.page+preset.location) in saved_list_identifier:
                    star = '*'
                display_msg(f'{i}{star}: {preset.display_fmt()}')
                i += 1
            display_msg('')

    def empty_line(self, line):
        return len(self.remove_blanks(line.split(' '))) == 0

    def empty_command_str(self):
        return self.empty_line(self.command_str)

    def update_command(self, command_str):
        self.command_str = command_str

    def has_preset(self):
        b = False
        for parameter in self.preset_parameters_keys.keys():
            if parameter in self.command_str:
                b = True
                break
        return b

    def extract_preset(self):
        index = -1
        overwrite_preset = []
        location = ''
        if "'" in self.command_str or '"' in self.command_str:
            if "'" in self.command_str and '"' in self.command_str:
                display_msg('Please use only \' or " around folder path')
            quotes = '"'
            if "'" in self.command_str:
                quotes = "'"
            cmd_split = self.command_str.split(quotes)
            if len(cmd_split) > 3:
                display_msg('There are more than two quotations marks found. Please use only two.')
            location = cmd_split[1]
            print(location)
            last_part = ''
            if len(cmd_split) > 2:
                last_part = cmd_split[2]
            self.command_str = f"{cmd_split[0].replace('-l', '')}{last_part}"
            print(self.command_str)
        if 'twitter.com' in self.command_str and '-p' in self.command_str:
            link = self.pop_val(self.command_str, '-p')
            if not self.empty_line(link):
                self.command_str = self.cut_line(self.command_str, '-p', link)
            else:
                self.command_str = self.command_str.replace('-p', '')
            custom = False
            if '-c' in self.command_str:
                c = self.pop_val(self.command_str, '-c')
                if c == 'c':
                    custom = True
            link_extract = self.convert_input_link(link, custom)
            front_preset = link_extract[0]
            if '-c' not in self.command_str and len(link_extract) > 1:
                front_preset += link_extract[1]
            self.command_str = front_preset + self.command_str
        preset_dict = {}
        if not self.empty_command_str():
            command_list = self.remove_blanks(self.command_str.split('-'))
            for i in range(len(command_list)):
                cmd = '-' + command_list[i]
                cmd_pair = self.remove_blanks(cmd.split(' '))
                if cmd_pair[0] == '-p':
                    if len(cmd_pair) < 2:
                        cmd_pair += ['']
                        if not self.has_page_to_add():
                            display_msg('no value provided for -p')
                    if '#' in cmd_pair[1]:
                        max_val = self.log_file.size()-1
                        if max_val < 0:
                            display_msg('there are no recorded presets')
                            index = ''
                            break
                        index = self.pop_val(cmd_pair[1], '#', ' ')
                        try:
                            int(index)
                        except:
                            display_msg('# must be followed by a corresponding integer')
                            index = ''
                        else:
                            index = int(index)
                            if index > max_val:
                                display_msg(f'Recorded preset option(s) only 0 to {max_val}. You entered {index}')
                                index = ''
                            else:
                                overwrite_preset = self.log_file.get_preset_dict_by_index(index)
                                cmd_pair[1] = overwrite_preset['page']
                if cmd_pair[0] == '-o':
                    cmd_pair[1] = cmd_pair[1:]
                for k in self.preset_parameters_keys.keys():
                    if k == cmd_pair[0]:
                        if len(cmd_pair) > 1:
                            if '*' in cmd_pair[1]:
                                cmd_pair[1] = cmd_pair[1].replace('*', '-')
                            preset_dict[self.preset_parameters_keys[k]] = cmd_pair[1]
                        else:
                            display_msg(f'{cmd_pair[0]} has not provided value\n')
                        break
            if location != '':
                preset_dict['location'] = location
            if len(overwrite_preset) != 0:
                temp_preset = Preset(overwrite_preset)
                temp_preset.update_preset(preset_dict)
                preset_dict = temp_preset
        return [preset_dict, index]

    def convert_input_link(self, link, custom=False):
        part = link.split('twitter.com')[1]
        finalized_parts = self.remove_blanks(part.split('/'))
        category = ''
        if custom:
            return [f'-p {link.split("twitter.com/")[1]}']
        elif 'search?' in finalized_parts[0] or 'src=typed_query' in finalized_parts[0]:
            search_split = finalized_parts[0].split('src=typed_query')
            category = 't'
            if search_split[1] == '&f=live':
                category = 'l'
            elif search_split[1] == '&f=image':
                category = 'p'
            elif search_split[1] == '&f=video':
                category = 'v'
            return [f'-p {search_split[0]}src=typed_query',  f'-c {category}']
        elif finalized_parts[0] == 'hashtag' and 'src=hashtag_click' in finalized_parts[1]:
            search_split = finalized_parts[1].split('src=hashtag_click')
            category = 't'
            if search_split[1] == '&f=live':
                category = 'l'
            elif search_split[1] == '&f=image':
                category = 'p'
            elif search_split[1] == '&f=video':
                category = 'v'
            return [f'-p {finalized_parts[0]}/{search_split[0]}src=hashtag_click', f'-c {category}']
        else:
            final_str = [f'-p {finalized_parts[0]}']
            if len(finalized_parts) == 2:
                category = 't'
                if finalized_parts[1] == 'media':
                    category = 'm'
                elif finalized_parts[1] == 'likes':
                    category = 'l'
                elif finalized_parts[1] == 'with_replies':
                    category = 'r'
                final_str.append(f'-c {category}')
            return final_str

    def has_run(self):
        if '>r' in self.command_str:
            return True
        else:
            return False

    def has_delete(self):
        if '>d' in self.command_str:
            return True
        else:
            return False


main_options = Options()
main_options.headless = True
main_options.add_argument('log-level=3')
sys.stdout.write('\nLoading...')
main_driver = assign_driver(main_options, ['78', '79', '77'])
display_msg('\nSince no login search isnt fully implemented yet, access would be too limited to do anything without login :(\nPlease sign in to a twitter account.')
command = CustomCommand(main_driver, Preset.preset_parameters_keys)
while True:
    cmd = input('Enter preset/commands/blank: ')
    command.update_command(cmd)
    command.execute_commands()
    if command.exited:
        display_msg('exiting')
        break
    else:
        continue

display_msg('Exit')
exit()

# scroll_while_saving(main_driver, 2, 'E:\Projects\Bots\Twitter\\test')

# scroll_to_bottom(main_driver)
# sys.stdout.write('\nLoading all tweets')
# main_soup = get_soup(main_driver)
# tweets = scroll_find_tweets(main_driver, [], 2)
# photos_list = find_all_photos(tweets, is_logged_in(main_driver), '', True, True)

# for img in photos_list:
#     print(img)
# print(f'Total Images: {len(photos_list)}')

# main_driver.quit()

# cookies = driver.get_cookies()
# for cookie in cookies:
#     driver.add_cookie({'name': cookie['name'],'value': cookie['value']})

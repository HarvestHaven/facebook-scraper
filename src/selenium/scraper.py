import time
from time import gmtime, strftime
import os
import re
import argparse

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin

from git import Repo
from git import Actor
from git.repo.fun import is_git_dir


class GitHelper:

  def __init__(self, folder):
    if is_git_dir(folder):
      self._repo = Repo(folder)
    else:
      self._repo = Repo.init(folder)

  def commit_changes(self):
    self._repo.git.add(all=True)
    time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    actor = Actor("FBPostScraper", "fbpostscraper@dummy.com")
    self._repo.index.commit(time_str, author=actor, committer=actor)


class FBPageProcessor:

  def __init__(self, folder, url):
    self.__main_folder = folder
    self.__images_folder = 'images'
    self.__style_folder = 'styles'
    self.__html_file = os.path.join(folder, 'index.html')
    self.__html_file_tmp = os.path.join(folder, 'index.tmp.html')
    self.__processor = self.__get_processor(url)


  def __get_processor(self, url):
    url_elems = url.split('/')
    print(url_elems)
    return
  
    if 'posts' in url_elems:
      return self.__process_post
    elif 'videos' in url_elems:
      return self.__process_video
    else:
      raise Exception('The page type is not supported!')


  def __create_folder(self, folder):
    try:
      os.mkdir(os.path.join(self.__main_folder, folder))
    except FileExistsError:
      # That's OK
      pass


  def __download_artifact(self, folder, url):
    url = urlparse(url)
    if url.scheme != 'http' and url.scheme != 'https':
      return None
    filepath = os.path.join(folder, url.path.split('/')[-1])
    full_filepath = os.path.join(self.__main_folder, filepath)
    if os.path.isfile(full_filepath):
      return filepath
    r = requests.get(url.geturl(), stream=True)
    if r.status_code == 200:
      with open(full_filepath, 'wb') as f:
        for chunk in r:
          f.write(chunk)
    return filepath      


  def __download_images(self, soup):
    self.__create_folder(self.__images_folder)
    for (i, img) in enumerate(soup.find_all('img')):
      filepath = self.__download_artifact(self.__images_folder, img['src'])
      if filepath:
        img['src'] = filepath


  def __download_styles(self, soup):
    self.__create_folder(self.__style_folder)
    links = soup.find_all('link', type='text/css')
    links.extend(soup.find_all('link', attrs={'as': 'style'}))
    for (i, link) in enumerate(links):
      filepath = self.__download_artifact(self.__style_folder, link['href'])
      if filepath:
        self.__get_images_from_style(filepath, link['href'])
        link['href'] = filepath


  def __get_images_from_style(self, style_filepath, style_url):
    pattern = re.compile(r'url\((.+?/([^/]+?))\)')
    full_style_filepath = '/'.join((self.__main_folder, style_filepath))
    with open(full_style_filepath, 'r') as f:
      content = f.read()
    matches = re.findall(pattern, content)
    for m in matches:
      if self.__download_artifact(self.__style_folder, urljoin(style_url, m[0])):
        content = content.replace(m[0], m[1])
    with open(full_style_filepath + '.bak', 'w') as out:
      out.write(content)
    os.rename(full_style_filepath + '.bak', full_style_filepath)


  def __process_post(self, soup):
    headerArea = soup.find(id='headerArea')
    headerArea.decompose()

    soup.find(id='rightCol').decompose()


  def __process_video(self, soup):
    contentArea = soup.find(id='contentArea')
    for sibling in contentArea.find_previous_siblings('div'):
      sibling.decompose()
    for sibling in contentArea.find_next_siblings('div'):
      sibling.decompose()

    related_videos = contentArea.find('span', text='Related Videos')
    if related_videos:
      related_videos.parent.parent.parent.decompose()
    else:
      sub_divs = list(contentArea.children)
      for ch in sub_divs[0:-2]:
        ch.decompose()
      for ch in list(sub_divs[-1].children)[1:]:
        ch.decompose()

    video = contentArea.find('video')
    img_div = video.next_sibling
    img_div['style'] = 'display: block; z-index: auto'
    img_div.img['style'] = 'opacity: 1; -webkit-filter: none'
    for sibling in img_div.find_next_siblings():
      sibling.decompose()
    video.decompose()


  def get_tmp_html_page_path(self):
    return self.__html_file_tmp


  def process_page_source(self):
    with open(self.__html_file_tmp, 'r') as f:
      soup = BeautifulSoup(f, 'html.parser')

      for script in soup.find_all('script'):
        script.decompose()
      for link in soup.find_all('link', attrs={'as': 'script'}):
        link.decompose()

      self.__processor(soup)

      referer = soup.find('iframe', src='/common/referer_frame.php')
      if referer:
        referer.decompose()

      self.__download_images(soup)
      self.__download_styles(soup)
      
      with open(self.__html_file, 'w') as out:
        out.write(soup.prettify(formatter="html"))


def expand_all(driver, xpath):
  wait = WebDriverWait(driver, 2)
  while True:
    elements = None
    try:
      elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    except TimeoutException as e:
      # The element was not found
      break
    if not elements:
      break
    for e in elements:
      driver.execute_script("arguments[0].click();", e)
    time.sleep(1)


def expand_and_download_page(main_folder, html_file_path, url):
  options = webdriver.ChromeOptions()
  options.add_argument('--no-sandbox')
  options.add_argument('--start-maximized')
  options.add_argument('--headless')
  options.add_argument('--disable-gpu')
  options.add_argument('--incognito')
  options.add_argument('--disable-extensions')
  options.add_argument('--disable-plugins')
  options.add_argument('--disable-default-apps')
  options.add_argument('--disable-infobars')
  options.add_argument('--disable-browser-side-navigation')
  options.add_argument('--dns-prefetch-disable')
  options.add_argument('--disable-features=VizDisplayCompositor')
  # options.add_argument('--disable-dev-shm-usage')

  driver = webdriver.Chrome(options=options)
  driver.get(url)

  wait = WebDriverWait(driver, 10)
  try:
    not_now_button = wait.until(EC.element_to_be_clickable((By.ID, 'expanding_cta_close_button')))
    driver.execute_script("arguments[0].click();", not_now_button)
  except TimeoutException:
    # The log-in dialog did not pop up
    pass

  try:
    comments = driver.find_element_by_xpath("//div[@id='contentArea']//span/a[contains(text(), 'Comment')]")
    driver.execute_script("arguments[0].click();", comments)

    most_relevant_xpath = "//div[@id='contentArea']//a[contains(text(), 'Most relevant') or contains(text(), 'Most Relevant')]"
    all_comments_menu = wait.until(EC.presence_of_element_located((By.XPATH, most_relevant_xpath)))
    driver.execute_script("arguments[0].click();", all_comments_menu)

    all_comments = wait.until(EC.presence_of_element_located((By.XPATH, "//a[.//div[contains(text(), 'Show all comments, including potential spam')]]")))
    driver.execute_script("arguments[0].click();", all_comments)

    more_replies_xpath = "//div[@id='contentArea']//a[div/span[contains(text(),'View') and (contains(text(),'more replies') or contains(text(),'more comment'))]]"
    expand_all(driver, more_replies_xpath)
    replies_xpath = "//div[@id='contentArea']//a[div/span[contains(text(),'Repl') and not(contains(text(),'Hide'))]]"
    expand_all(driver, replies_xpath)
    expand_all(driver, more_replies_xpath)
    expand_all(driver, "//div[@id='contentArea']//a[text()='See More']")
  except NoSuchElementException:
    # No comments
    pass

  with open(html_file_path, 'w') as f:
    f.write(driver.page_source)

  body = driver.find_element_by_xpath('//body')
  total_height = body.size["height"] + 200
  total_width = body.size["width"] * 1.5
  driver.set_window_size(total_width, total_height)
  driver.save_screenshot("{}/{}.png".format(main_folder, strftime("%Y-%m-%d_%H:%M:%SZ", gmtime())))

  driver.quit()


def expand_and_process_post(root_folder = "", post_url = ""):
  # if root_folder == "" or root_folder == Null:
  # if(len(root_folder) == 0):
    # raise Exception('The root_folder cannot be empty!')
  main_folder = os.path.join(os.path.abspath(root_folder), post_url.split('/')[-1])
  git = GitHelper(main_folder)
  proc = FBPageProcessor(main_folder, post_url)
  expand_and_download_page(main_folder, proc.get_tmp_html_page_path(), post_url)
  proc.process_page_source()
  git.commit_changes()


if __name__== "__main__":
  parser = argparse.ArgumentParser(description='The script expends a FB page on the given URL and downloads the page for offline use.')
  parser.add_argument('--root', metavar='rootfolder', help='Root folder for the downloaded resources')
  parser.add_argument('--url', metavar='url', help='FB resource URL')
  args = parser.parse_args()

  # print(args);
  expand_and_process_post(args.root, args.url)

import sched
import time
import json
import os
import math
import argparse

import multiprocessing as mp

from scraper import expand_and_process_post

SCHEDULER_FREQ_SEC = 30
POST_FREQ_SEC = 10 * 60 # 10 min


class FBScraperScheduler:

  def __init__(self, root_folder, url_file):
    self._root_folder = root_folder
    self._url_file = url_file
    self._sched = sched.scheduler(time.time, time.sleep)
    self._count = 0
    self._posts = []
    self._counts_per_slots = []
    self._ctx = mp.get_context('fork')


  def __read_links_from_file(self):
    with open(self._url_file) as f:
      self.links_json = json.load(f)

    self._posts = self.links_json['posts']
    self._count = len(self._posts)
    print(f"count: {self._count}")
    self.slots = math.ceil(POST_FREQ_SEC / SCHEDULER_FREQ_SEC)
    print(f"slots: {self.slots}")

    self._counts_per_slots = self.__build_schedule(self._count, self.slots)
    print(self._counts_per_slots)


  def __build_schedule(self, count, slots):
    urls_per_slot = int(count / slots)
    counts_per_slots = [urls_per_slot for i in range(slots)]
    remaining = count % slots
    if remaining > 0:
      hop = round(slots / remaining)
      i = 0
      while i < slots and remaining > 0:
        counts_per_slots[i] += 1
        i += hop
        remaining -= 1
    return counts_per_slots


  def __do_something(self, index):
    start = time.time()
    print(self._counts_per_slots[index])

    for i in range(self._counts_per_slots[index]):
      p = self._ctx.Process(
        target=expand_and_process_post,
        args=(self._root_folder, self._posts[index]['url'],))
      p.start()
      index += 1

    if index >= self.slots:
      return
      self.__read_links_from_file()
      index = 0
    elapsed = time.time() - start
    delay = max(0, (SCHEDULER_FREQ_SEC - elapsed))
    self._sched.enter(delay, 1, self.__do_something, (index,))


  def set_up_schedule(self):
    self.__read_links_from_file()
    self._sched.enter(SCHEDULER_FREQ_SEC, 1, self.__do_something, (0,))
    self._sched.run()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='The script schedules individual FB post scrapings based on the provided JSON file containing the FB posts.')
  parser.add_argument('rootfolder', metavar='root', help='Root folder for the downloaded files')
  parser.add_argument('urlfile', metavar='json-file', help='JSON file containing the FB post links')
  args = parser.parse_args()

  FBScraperScheduler(args.rootfolder, args.urlfile).set_up_schedule()
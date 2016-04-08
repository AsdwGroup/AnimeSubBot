Skip to content
This repository
Search
Pull requests
Issues
Gist
 @TheRedFireFox
 Unwatch 1
  Star 0
 Fork 0 TheRedFireFox/AnimeSubBot
 Code  Issues 1  Pull requests 0  Wiki  Pulse  Graphs  Settings
Tree: ba33372781 Find file Copy pathAnimeSubBot/temp.py
66dee98  2 days ago
@TheRedFireFox TheRedFireFox upload
1 contributor
RawBlameHistory     57 lines (46 sloc)  1.6 KB
import multiprocessing
import time
import threading

class Worker(threading.Thread):#multiprocessing.Process): #threading.Thread):
    
    def __init__(self, e, k = None):
        super().__init__()
        self.e = e
        self.k = k
        
    def run(self):
        #self.wait_for_event()
        self.wait_for_event_timeout(2)
        
        i = 0
        while not self.e.is_set():
            i += 1
            print(i)
            #time.sleep(0.1)
        """print('wait_for_event: starting')
        self.e.wait()
        print('wait_for_event: e.is_set()->', self.e.is_set())
        """
        
    def wait_for_event(self):
        """Wait for the event to be set before doing anything"""
        print('wait_for_event: starting')
        self.e.wait()
        print('wait_for_event: e.is_set()->', self.e.is_set())

    def wait_for_event_timeout(self, t):
        """Wait t seconds and then timeout"""
        print('wait_for_event_timeout: starting')
        self.e.wait(t)
        print('wait_for_event_timeout: e.is_set()->', self.e.is_set())


if __name__ == '__main__':
    e = multiprocessing.Event()
    """w1 = multiprocessing.Process(name='block', 
                                 target=wait_for_event,
                                 args=(e,))
    w1.start()
    w2 = multiprocessing.Process(name='non-block', 
                                 target=wait_for_event_timeout, 
                                 args=(e, 2))
    w2.start()"""
    
    w = Worker(e, None)
    w.start()
    print('main: waiting before calling Event.set()')
    time.sleep(10)
    e.set()
    print('main: event is set')
Status API Training Shop Blog About
© 2016 GitHub, Inc. Terms Privacy Security Contact Help
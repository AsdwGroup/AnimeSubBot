import multiprocessing
import time
import threading

class Ing2Base64(multiprocessing.Process): #threading.Thread):
    
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
    
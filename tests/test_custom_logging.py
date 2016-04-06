#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

'''
    This module defines a test for the custom logging system.
'''
import time
import multiprocessing

from importlib.machinery import SourceFileLoader

custom_logging = SourceFileLoader("custom_logging", "../src/custom_logging.py").load_module()

# decomment to work
def TestCustomLogging(l, n, s):
    for i in range(n):
        l.info("Info - {}- {}".format(multiprocessing.current_process().name, time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime())))
        l.error("Error - {} - {}".format(multiprocessing.current_process().name, time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime())))
        time.sleep(0.2)
    if not s.is_set():
        s.set()
  
   
if __name__ == '__main__':
    

    print("Online")
    log_to = True
    c = custom_logging.Logger(LogToConsole = log_to)

    ShutdownEvent1 = multiprocessing.Event()
    ShutdownEvent1.set()
    
    ShutdownEvent2 = multiprocessing.Event()
    
    c = custom_logging.LoggingProcessSender(LogToConsole = log_to, ShutdownEvent = ShutdownEvent1)
    process = c._GetSubProcessPid_()
    for i in range(2):
        c.info("Hallo?")
        c.error("Test")
    
    f = multiprocessing.Process(name='worker1', target = TestCustomLogging, args=(c, 100, ShutdownEvent2, ))
    f2 = multiprocessing.Process(name='worker2', target = TestCustomLogging, args=(c, 100, ShutdownEvent2, ))
    
    f.start()
    f2.start()
    time.sleep(2)
    for i in range(20):
        c.info("Hallo?")
        c.error("Test")
    #time.sleep(0.01)
    print("Stop in the name of love")
    ShutdownEvent2.wait()
    ShutdownEvent1.clear()
    f.join()
    f2.join()
    process.join()
    print("offline")
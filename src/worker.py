#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
import time
import queue
import multiprocessing

import gobjects
import telegram
import messages.msg_processor

class MainWorker(multiprocessing.Process):
    '''
    This class is responsable for all the management of the other 
    processes except the console interpreter. It will initialise the
    input and output queue as well as the subworker processes.
    '''
    
    DEFAULT_WORKER_NAME = "Worker-" 
    """
    Default worker process name => Worker-{Number}
    """
    def __init__(self, 
                 MaxWorker,
                 ShutDownEvent,
                 Configuration,
                 Logging,
                 LanguageObject,
                 SqlObject,
                 BotName = None):
        '''
        Constructor
        '''
        super().__init__(name = "MainWorker")
        
        self.OutputAPI = {
                          "Object": None,
                          "WorkerQueue": None,
                          "ControlQueue": None,
                          "ShutdownEvent": None,
                          "WorkloadEvent":None,
                          "ConnectionEvent":None
                          }
        self.InputAPI = {
                         "Object": None,
                         "WorkerQueue": None,
                         "ControlQueue": None,
                         "ShutdownEvent": None,
                         "WorkloadEvent":None,
                         "ConnectionEvent":None
                         }
        
        self.MaxWorker = MaxWorker
        self.ShutdownEvent = ShutDownEvent
        self.Configuration = Configuration
        self.Logging = Logging
        self.LanguageObject = LanguageObject
        self._ = LanguageObject.CreateTranslationObject()
        self.ConnectionEvent = None
        self.WorkloadDoneEvent = None
        if BotName is not None:
            self.BotName = BotName
        else:
            self.BotName = gobjects.__AppName__
        
        self.WorkerList = {}
        """
        WorkerList = {
            WorkerName: {
                "WorkerName": WorkerName
                "WorkerShutDownEvent": EventObject,
                "WorkerObject": ProcessObject,
            }
        }
        """
        self.WorkerCount = 1
        
    
    def _ShutdownWorker_(self, Worker):
        """
        This method will shutdown a worker and end the process.
        
        Variables:
            Worker                        ``directory``
                it's a part of the objects workerlist, it will be 
                shutdown overtime.
        """
        Worker["WorkerShutDownEvent"].set()
        Worker["WorkerObject"].join()
        del self.WorkerList[Worker["WorkerName"]]
        self.WorkerCount -= 1
        
    def _ShutdownAll_(self):
        self.InputAPI["ShutdownEvent"].set()
        self.InputAPI["WorkloadEvent"].wait()
        self.InputAPI["Object"].join()
        while not self.InputAPI["WorkerQueue"].empty():
            time.sleep(0.1)
        # signalising all the worker that the system is shutting down.            
        for Worker in self.WorkerList.keys():
            self._ShutdownWorker_(Worker)
    
        self.OutputAPI["WorkloadEvent"].set()
        self.OutputAPI[""]
    
    def _StartWorker_(self,):
        
        WorkerName = "{}{}".format(DEFAULT_WORKER_NAME, 
                                   self.WorkerCount
                                   )
        ProcessShutdownEvent = multiprocessing.Event()
        #ProcessShutdownEvent.set()
        Worker = SubWorker(
                           # Whatever
                        BotName = self.BotName,
                        InternalName = WorkerName,
                        ShutDownEvent = ProcessShutdownEvent,
                        Configuration = self.Configuration,
                        Logging = self.Logging,
                        LanguageObject = self.LanguageObject,
                        InputQueue = self.InputAPI["WorkerQueue"],
                        OutputQueue = self.OutputAPI["WorkerQueue"],
                           )
        
        Worker.start()
        
        self.WorkerList[WorkerName] = {
                            "WorkerName": WorkerName,
                            "WorkerShutDownEvent":ProcessShutdownEvent,
                            "WorkerObject":Worker            
                                         }
        self.WorkerCount += 1
                
    def _InitialiseAPI_(self):
        self.ConnectionEvent = multiprocessing.Event()
        self.WorkloadDoneEvent = multiprocessing.Event()

        self.InputAPI["ShutdownEvent"] = multiprocessing.Event()
        self.InputAPI["WorkerQueue"] = multiprocessing.Queue()
        self.InputAPI["ControlQueue"] = multiprocessing.Queue()
        
        self.InputAPI["Object"] = telegram.InputTelegramAPI(
                                                          # whatever
                ApiToken = self.Configuration["Secure"]["ApiToken"],
                RequestTimer = self.Configuration["Telegram"]["RequestTimer"],
                ShutDownEvent = self.InputAPI["WorkerQueue"],
                ConnectionEvent = self.ConnectionEvent,
                                                          )
        self.OutputAPI["ShutdownEvent"] = multiprocessing.Event()
        self.OutputAPI["WorkerQueue"] = multiprocessing.Queue()
        self.OutputAPI["ControlQueue"] = multiprocessing.Queue()
        
        self.OutputAPI["Object"] = telegram.InputTelegramAPI(
                                                          # whatever
                ApiToken = self.Configuration["Secure"]["ApiToken"],
                RequestTimer = self.Configuration["Telegram"]["RequestTimer"],
                 LoggingObject = self.Logging,
                 LanguageObject = self.LanguageObject,
                 ControllerQueue = self.OutputAPI["ControlQueue"],
                 WorkloadQueue = self.OutputAPI["WorkerQueue"],
                 ConnectionEvent = self.ConnectionEvent,
                 WorkloadDoneEvent = self.WorkloadDoneEvent,
                 ShutDownEvent = self.OutputAPI["ShutdownEvent"],
                                                          )
        
    def run(self):
        self.InitialiseAPI()
        LastLoad = None
        self.StartWorker()
        while self.ShutdownEvent.is_set():
            WorkloadAmount = self.InputAPI["WorkerQueue"].qsize()
            Workload = (WorkloadAmount / 30)
            LastLoad = Workload
            
            WorkerAmmount = len(self.WorkerList.keys())
            
            if Workload > WorkerAmmount:
                # creat a new worker.
                self.StartWorker()
            elif Workload < WorkerAmmount:
                # shutdown the yongest worker if needed
                if Workload > 1:
                    self._ShutdownWorker_(sorted(self.WorkerList.keys(),
                                                  reverse=True)
                                          )
            
            time.sleep(0.5)    
        # shutting down all the subprocesses.
        self._ShutdownAll_()
        
class SubWorker(multiprocessing.Process):

    def __init__(self, 
                 BotName,
                 InternalName,
                 ShutDownEvent,
                 Configuration,
                 Logging,
                 LanguageObject,
                 SqlObject,
                 InputQueue,
                 OutputQueue,
                 ):
        '''
        Constructor
        '''
        super().__init__(name = InternalName)
        self.BotName = BotName
        self.InternalName = InternalName
        self.ShutdownEvent = ShutDownEvent
        self.Configuration = Configuration
        self.Logging = Logging
        self.LanguageObject = LanguageObject
        self.SqlObject = SqlObject
        self.InputQueue = InputQueue
        self.OutputQueue = OutputQueue
    
    def _GetWorkFromQueue(self, Timeout = 0.05):
        Work = None
        try:
            Work = self.InputQueue.get(
                                       block = True,
                                       timeout = Timeout
                                       )
        except queue.Empty:
            pass
        except:
            raise
        
        return Work
            
    def _SendToQueue(self, Object):
        self.OutputQueue.put(Object)
    
    def run(self):
        while self.ShutdownEvent.is_clear():
            Timeout = 0.05
            while not self.InputQueue.empty():
                Work = self._GetWorkFromQueue(Timeout)
                MessageProcessor = messages.msg_processor(
                                Work,
                                LanguageObject = self.LanguageObject,
                                SqlObject = self.SqlObject,
                                ConfigurationObject = self.Configuration        
                                                          )
                InterpretedMessage = MessageProcessor.InterpretMessage()
                
                if InterpretedMessage is not None:
                    if isinstance(InterpretedMessage, list):
                        for Message in InterpretedMessage:
                            self._SendToQueue(Message)
                    elif isinstance(InterpretedMessage, dict):
                        self._SendToQueue(InterpretedMessage)
            
        
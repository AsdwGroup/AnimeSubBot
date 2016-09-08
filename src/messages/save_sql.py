#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

"""
This module defines a process to save somethings to the database.
"""


import json
import queue
import datetime
import multiprocessing


class MessageToSql(multiprocessing.Process):
    """
    This class is responsable to add the messages to the database.
    """
    def __init__(self, 
                 SqlObject, 
                 WorkloadQueue, 
                 ShutdownEvent,
                 WorkloadEvent):
        
        self.SqlObject = SqlObject
        self.WorkloadQueue = WorkloadQueue
        self.ShutdownEvent = ShutdownEvent
        self.WorkloadEvent = WorkloadEvent
        super().__init__(name="MessageToSql")
    
    def _GetWork_(self, TimeOut):
        """
        This method will get the workload from the queue and return it
        if there is work.
        """
        Workload = None
        try:
            Workload = self.WorkloadQueue.get(block = True, 
                                              timeout = TimeOut)
        except queue.Empty:
            return False
        return Workload
    
    def _InsertInto_(self, Message, From):
        """
        This method is responsable to insert the messages into the 
        database after resiving them.
        """
        # create cursor object
        DMessage = None
        SMessage = None

        if isinstance(Message, dict):
            DMessage = Message
            SMessage = json.dumps(Message)
            
        elif isinstance(Message, str):
            DMessage = json.loads(Message)
            SMessage = Message

        
        SqlCursor = self.SqlObject.CreateCursor()
        Time = datetime.datetime.fromtimestamp(DMessage["message"]["date"])
        
        Columns = {
                   "Creation_Date":Time,
                   "Message": SMessage
                   }
        if From == "Input":
            # add message to the input server
            self.SqlObject.InsertEntry(
                    Cursor = SqlCursor,
                    TableName = "Input_Messages_Table",
                    Columns=Columns,
                    AutoCommit = True
                                      )
        elif From == "Output":
            # add message to the output table
            self.SqlObject.InsertEntry(
                    Cursor = SqlCursor,
                    TableName = "Output_Messages_Table",
                    Columns=Columns,
                    AutoCommit = True
                                      )
        self.SqlObject.DestroyCursor(SqlCursor)
    
    def run(self):
        # create the connection to the database
        self.SqlObject = self.SqlObject.New()

        # main loop 
        while not self.ShutdownEvent.is_set():
            Workload = self._GetWork_(1)
            if isinstance(Workload, tuple):
                Message, From = Workload
                self._InsertInto_(Message, From)
        # finish the workload         
        while True:
            Workload = self._GetWork_(0.1)
            if isinstance(Workload, tuple):
                Message, From = Workload
                self._InsertInto_(Message, From)
            else:
                if self.WorkloadEvent.is_set():
                    break
#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

# python standard library
import os
import ssl
import json
import gzip
import zlib
import time
import queue
import pickle
import platform
import urllib.parse
import urllib.request
import multiprocessing

import gobjects  # the global variables
import language  # imports the _() function! (the translation feature)
import clogging


class TelegramApi(object):
    """
    This class is responsible for contacting the telegram bot servers.
    
    From the documentation:
    
        The Bot API is an HTTP-based interface created for developers 
        keen on building bots for Telegram.
        To learn how to create and set up a bot
    
        Authorizing your bot
    
        Each bot is given a unique authentication token when it is 
        created. The token looks something like 
        ``123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11``, but we'll use simply 
        ``<token>`` in this document instead. You can learn about obtaining
        tokens and generating new ones in this document.
        
        Making requests
        
        All queries to the Telegram Bot API must be served over HTTPS 
        and need to be presented in this form: 
        ``https://api.telegram.org/bot<token>/METHOD_NAME``. 
        
        Like this for example:
        ``https://api.telegram.org/bot<token>/getMe``
        
        We support GET and POST HTTP methods. We support four ways of 
        passing parameters in Bot API requests:
        
            * URL query string
            * application/x-www-form-urlencoded
            * application/json (except for uploading files)
            * multipart/form-data (use to upload files)
        
        The response contains a JSON object, which always has a Boolean 
        field ‘ok’ and may have an optional String field ‘description’ 
        with a human-readable description of the result. If ‘ok’ equals 
        true, the request was successful and the result of the query 
        can be found in the ‘result’ field. In case of an unsuccessful 
        request, ‘ok’ equals false and the error is explained in the 
        ‘description’. An Integer ‘error_code’ field is also returned, 
        but its contents are subject to change in the future.
        
            * All methods in the Bot API are case-insensitive.
            * All queries must be made using UTF-8.
    
        the documentation is online under:
            https://core.telegram.org/bots/api
    """
    BASE_URL = r"https://api.telegram.org/bot"
    """
    The main url for the telegram API.
    """
    def __init__(self,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ):
        """
        The init method...
        
        Here we set the variables like the header send to the API:
        Example:
            .. code-block:: python
            
                Header
                {
                'Content-Type': 
                'application/x-www-form-urlencoded;charset=utf-8', 
                'User-agent': 
                "BetterPollBot/0.1 (Windows; 8; 6.2.9200)"\\
                " Python-urllib/('v3.4.3:9b73f1c3e601', "\\
                "'Feb 24 2015 22:43:06') "\\
                "from https://github.com/TheRedFireFox/AnimeSubBot"
                }
        
        Variables:
            ApiToken                      ``string``
                contains the token to contact the background information
                of the bot\n
                Each bot is given a unique authentication token when it 
                is created.
            
            RequestTimer                  ``integer``
                set's the sleeping time between requests to the bot API

            LanguageObject        ``object``
                contains the translation object
                        
            LoggingObject         ``object``
                contains the logging object needed to log
                        
        """
        
        self.ApiToken = ApiToken
        self.BotApiUrl = "{}{}".format(TelegramApi.BASE_URL,
                                       self.ApiToken
                                       )
        
        # Predefining attribute so that it later can be used for evil.
        self.LanguageObject = LanguageObject.CreateTranslationObject()
        # Here we are initialising the function for the translations.
        self._ = self.LanguageObject.gettext
        self.LoggingObject = LoggingObject

        # Test if the content can be compressed or not
        self.Compressed = True
        
        # This variables are in normal situations not used.
        # They are only used when the connection to telegram is being 
        # tested (at the start of the program).
        self.Connection = True
        
        # This timer is needed to see if there is a problem with the
        # telegram server. If so the interval should be bigger (1 min 
        # instead given time 1 sec)
        self.RequestTimer = RequestTimer
        self.GivenRequestTimer = RequestTimer
        
        # ssl encryption protocol
        self.SSLEncryption = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) 

#         this looks like this:
#         {
#         'Content-Type':
#             'application/x-www-form-urlencoded;charset=utf-8',
#         'User-agent': "AnimeSubBot/0.1 (Windows; 8; 6.2.9200) \
#       Python-urllib/('v3.4.3:9b73f1c3e601', 'Feb 24 2015 22:43:06') \
#       from https://github.com/TheRedFireFox/AnimeSubBot"
#         }

        self.Headers = {
            'User-agent': (("{AppName}/{Version}({Platform})"
                            "Python-urllib/{PythonBuild} from {Hosted}"
                            ).format(
                                AppName=gobjects.__AppName__,
                                Version=gobjects.__version__,
                                Platform=('; '.join(
                                                platform.system_alias(
                                                    platform.system(),
                                                    platform.release(),
                                                    platform.version()
                                                    )
                                                      )
                                            ),
                                PythonBuild=platform.python_build(),
                                Hosted=gobjects.__hosted__
                                )
                           ),
            "Content-Type":
                "application/x-www-form-urlencoded;charset=utf-8",
            "Accept-Encoding": "gzip,deflate"
        }

        self.BotName = self.GetMe()

    def GetBotName(self):
        """
        This method returns the given bot name from the API.
        
        Variables:
            \-
        """
        return self.BotName

    def SendRequest(self, Request):
        """
        This method will send the request to the telegram server.
        
        It will return the in the end the response from the servers.
        
        Variables:
            Request                       ``object``
                this variable is generated before the request is being
                send to the telegram bot API

        """

        # Reset the request timer if needed.
        if self.RequestTimer != self.GivenRequestTimer:
            self.RequestTimer = self.GivenRequestTimer
        try:
            with urllib.request.urlopen(
                                        Request,
                                        context=self.SSLEncryption
                                        ) as Request:
                # setting the compression rate of the system
                if self.Compressed is True:
                    RequestEncoding = Request.info().get("Accept-Encoding")
                    if RequestEncoding == "gzip":
                        self.Headers["Accept-Encoding"] = "gzip"
                        TheResponse = gzip.decompress(Request.read())
                    elif RequestEncoding == "deflate":
                        self.Headers["Accept-Encoding"] = "deflate"
                        Decompress = zlib.decompressobj(-zlib.MAX_WBITS)
                        TheResponse = Decompress.decompress(Request.read())
                        TheResponse += Decompress.flush()
                    else:
                        # setting the compression to false
                        self.Compressed = False
                        # deleting the Accept-Encoding header since neither of the encodings where accepted
                        del self.Headers["Accept-Encoding"]
                        TheResponse = Request.read()
                else:
                    TheResponse = Request.read()
            return json.loads(TheResponse.decode("utf-8"))

        except urllib.error.HTTPError as Error:
            if Error.code == 400:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )
                                    ) + " " + 
                    self._("The server cannot or will not process the request "
                           "due to something that is perceived to be a client "
                           "error (e.g., malformed request syntax, invalid "
                           "request message framing, or deceptive request "
                           "routing)."
                           ),
                )
            elif Error.code == 401:
                self.LoggingObject.critical(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " + 
                    self._("The ApiToken you are using has not been found in "
                           "the system. Try later or check the ApiToken for "
                           "spelling errors."),
                )
            elif Error.code == 403:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error="{} {}".format(Error.code, Error.reason)
                                           ) + " " + 
                    self._("The address is forbidden to access, please try "
                           "later."),
                )
            elif Error.code == 404:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=" {} {} ".format(Error.code, Error.reason)
                                           ) + 
                    self._("The requested resource was not found. This status "
                           "code can also be used to reject a request without "
                           "closer reason. Links, which refer to those error "
                           "pages, also referred to as dead links."),
                )
            elif Error.code == 429:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\".") + 
                    "{} {}".format(Error.code, Error.reason) +
                    self._("My bot is hitting limits, how do I avoid this?\n"
                    "When sending messages inside a particular chat, "
                    "avoid sending more than one message per second. "
                    "We may allow short bursts that go over this limit,"
                    " but eventually you'll begin receiving 429 errors.\n"
                    "If you're sending bulk notifications to multiple"
                    " users, the API will not allow more than 30"
                    " messages per second or so. Consider spreading out"
                    " notifications over large intervals of 8—12 hours"
                    " for best results.\nAlso note that your bot will"
                    " not be able to send more than 20 messages per"
                    " minute to the same group."
                                           )
                                         )
            elif Error.code == 502:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " + 
                    self._("The server could not fulfill its function as a "
                           "gateway or proxy, because it has itself obtained "
                           "an invalid response. Please try later."),
                )
            elif Error.code == 504:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " + 
                    self._("The server could not fulfill its function as a "
                           "gateway or proxy, because it has not received a "
                           "reply from it's servers or services within a "
                           "specified period of time.")
                )
            raise
        except:
            raise
        
    def GetMe(self):
        """
        A method to confirm the ApiToken exists.
        
        It returns the response from the request, this includes the
        bot name.
        
        Variables:
           \ -
        """
        request = urllib.request.Request(
            "{}/getMe".format(self.BotApiUrl),
            headers=self.Headers
        )

        return self.SendRequest(request)

    def GetUpdates(self, CommentNumber=None):
        """
        A method to get the Updates from the Telegram API.
        
        It does as well to confirm the old comments so that only 
        new responses have to be processed.
        
        Notes:\n
        1. This method will not work if an outgoing web hook is set up.
        2. In order to avoid getting duplicate updates, recalculate offset
           after each server response.
        
        Variables:
            CommentNumber                 ``None or integer``
                this variable set's the completed request id
                
        """

        DataToBeSend = {
                        # "limit": 1,
                        "timeout": 0
                        }

        if CommentNumber:
            DataToBeSend["offset"] = CommentNumber
        # data have to be bytes
        MessageData = urllib.parse.urlencode(DataToBeSend).encode('utf-8')

        Request = urllib.request.Request("{}/getUpdates".format(self.BotApiUrl),
                                              data=MessageData,
                                              headers=self.Headers)

        # send Request and get JSONData    
        JSONData = self.SendRequest(Request,)

        if JSONData is not None:
            if JSONData["ok"]:
                return JSONData

        return None

    def SendMessage(self, MessageObject):
        """
        A method to send messages to the TelegramApi
        
        Variables:
            MessageObject                 ``object``
                this variable is the object with the content of the
                message to be send, as well as other options.
        """

        # data have to be bytes
        MessageData = urllib.parse.urlencode(
            MessageObject.GetMessage()).encode('utf-8')

        Request = urllib.request.Request("{}/sendMessage".format(self.BotApiUrl),
                                         data=MessageData,
                                         headers=self.Headers
                                         )

        return self.SendRequest(Request,)

    def ForwardMessage(self, 
                       ChatId, FromChatId, 
                       MessageId, DisableNotification=False):
        """
        A method to forward a received message
        
        This function will maybe be build in the future for now
        it's not doing anything.
        """
        # MessageData = {}
        raise NotImplementedError
    
    def SendPhoto(self, ):
        raise NotImplementedError
    
class _TelegramApiServer(multiprocessing.Process):

    def __init__(self,
                 Name,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ControllerQueue,
                 WorkloadQueue,
                 SendMessagesQueue,
                 ConnectionEvent,
                 WorkloadDoneEvent,
                 ShutDownEvent,):
                 
        super().__init__(name=Name)
        self.Name = Name
        self.ControllerQueue = ControllerQueue
        self.WorkloadQueue = WorkloadQueue
        self.ConnectionEvent = ConnectionEvent
        self.ShutDownEvent = ShutDownEvent
        self.Timeout = RequestTimer
        self.WorkloadDoneEvent = WorkloadDoneEvent
        self.SendMessagesQueue = SendMessagesQueue
        self.Data = {
                     "ApiToken": ApiToken,
                     "RequestTimer":RequestTimer,
                     "LoggingObject": LoggingObject,
                     "LanguageObject": LanguageObject,
                     }
        
        self.Run = True
        self.WorkloadFileDirectory = os.path.abspath("SavedWorkload")
        self.TelegramApi = None
    
    def _SaveMessages_(self, Message):
        """
        This method will send the finished message to the orgniser 
        
        Variable:
            Message                       ``tuple``
                something to send, should look like this:
                ..code-block::python\n
                    (MessageJson, Type,)
        """
        try:
            self.SendMessagesQueue.put(item = Message, 
                                       block = True, 
                                       timeout = 0.5)
        except queue.Empty:
            return False
        return True

    def _StartApi_(self):
        """
        This method will create the TelegeramApi object and return it.
        """
        return TelegramApi(
                 ApiToken = self.Data["ApiToken"],
                 RequestTimer = self.Data["RequestTimer"],
                 LoggingObject = self.Data["LoggingObject"],
                 LanguageObject = self.Data["LanguageObject"],

        )
    
    def _CheckDirectory_(self):
        """
        This method will check if the workload directory exsits or not.
        If it doesn't exist it will create it.
        """
        
        # check if exists or else...
        if not os.path.isdir(self.WorkloadFileDirectory):
            os.mkdir(self.WorkloadFileDirectory)
        
        ReadMe = os.path.join(self.WorkloadFileDirectory, "ReadMe.txt")
        
        if not os.path.isfile(ReadMe):
            
            Text = ("Please do not delete anyfiles from this directory\n"
                    "This directory is needed for temporary saving the"
                    "workload, so that the bot may be shut down.")
            
            with open(ReadMe, "w") as File:
                File.write(Text)
        
    def _GetCommand_(self):
        """
        This method will get the command given by the command queue.
        """
        Command = None
        try:
            Command = self.ControllerQueue.get(False)
        except queue.Empty:
            pass
        except:
            raise
        
        return Command
        
    def _SendOverConnection_(self, ConnectionObject, Object):
        """
        In this method sends an object over a preinitialised connection 
        object.
        
        Variables:
            ConnecionObject               ``multiprocessing.Pipe object``
                This is the connection object needed to communicate,
                with the server.
                
            Object                        ``object``
                This can be everything.
        """
        ConnectionObject.send(Object)
    
    def _GetOverConnection_(self, ConnectionObject):
        """
        In this method sends an object over a preinitialised connection 
        object.
        
        Variables:
            ConnecionObject               ``multiprocessing.Pipe object``
                This is the connection object needed to communicate,
                with the server.

        """
        return ConnectionObject.recv()
        
    def _InterpretCommand_(self, Command):
        """
        This method is here as a placeholder and has to be overriden by
        the children instances.
        
        In this method the command send by the input queue will be 
        interpretet.
        """
        raise NotImplemented
    
    def run(self):
        """
        This method is here as a placeholder and has to be overriden by
        the children instances.
        
        In this method the main logic will be run.
        """
        raise NotImplementedError
     
class InputTelegramApiServer(_TelegramApiServer):
    
    def __init__(self,
                 Name,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ControllerQueue,
                 WorkloadQueue,
                 SendMessagesQueue,
                 ConnectionEvent,
                 WorkloadDoneEvent,
                 ShutDownEvent,):
        """
        Just initialising the subserver.
        """  
        super().__init__(
                 Name,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ControllerQueue,
                 WorkloadQueue,
                 SendMessagesQueue,
                 ConnectionEvent,
                 WorkloadDoneEvent,
                 ShutDownEvent,)
        
        self.ApiOffset = None
            
        self.WorkloadSaveFile = "ApiWorkload.psi"    
        self.WorkloadSaveFileFull = os.path.join(self.WorkloadFileDirectory,
                                                 self.WorkloadSaveFile)  
    
    def _SaveMessages_(self, Message):
        """
        This is an extention of the in the super class defined method.
        """
        Message = (Message, "Input",)
        if super()._SaveMessages_(Message):
            return True
        else:
            return False
        
        
    def _AddToWorkQueue_(self, ElementToAdd):
        """
        This method will add an element to the worker queue
        """
        self.WorkloadQueue.put(ElementToAdd)
        
    def GetBotName(self):
        """
        This methode gets the bot name from the Api
        """
        BotName = self.TelegramApi.GetBotName()
        return BotName
        
    def _InterpretCommand_(self, Command):
        Order = None
        ConnectionObject = None
        if "Order" in Command:
            Order = Command["Order"]
            
        if ConnectionObject in Command:
            ConnectionObject = Command["ConnectionObject"]
        
        if Order == "GetBotName":
            BotName = self.GetBotName()
            self._SendOverConnection_(ConnectionObject, BotName)
        elif Order == "SendApiOffset":
            ApiOffset = self.APIOffset
            self._SendOverConnection_(ConnectionObject, ApiOffset)
        elif Order == "GetApiOffset":
            self.ApiOffset = self._GetOverConnection_(ConnectionObject)
        elif Order == "Stop":
            self.Run = False
            self.ConnectionEvent.set()
            self._SaveApiOffset_()
        elif Order == "Run":
            self.Run = True
            self.ConnectionEvent.clear()      
        
    def _LoadApiOffset_(self):
        """
        This class will get the ApiOffset from the filesystem.
        
        Variables:
            \-
        """
        APIOffset = None
        if os.path.isdir(self.WorkloadSaveFileFull):
            Inputdata = None
            with open(self.WorkloadSaveFileFull, "r") as InputFile:
                Inputdata = InputFile.read()
            os.remove(self.WorkloadSaveFileFull)
            if isinstance(Inputdata, dir) is True:
                if "ApiOffset" in Inputdata:
                    APIOffset = APIOffset["ApiOffset"]
                return APIOffset
        return APIOffset
    
    def _SaveApiOffset_(self,):
        """
        Saves the telegram offest to the filesystem, so that the next 
        time the system starts it can directly restart getting the next 
        workload.
        
        Variables:
            \-
        """
        
        self._CheckDirectory_()
        
        DataToDump = {
                      "ApiOffset": self.ApiOffset
                      }
        
        with open(self.WorkloadSaveFileFull, "wb") as OutputFile:
            pickle.dump(DataToDump, OutputFile)
    
    def _GetCommentNumber_(self, MessageObject):
        """
        This method is responsable for getting the heighest update_id
        from the system.
        """
        
        CommentList = []
        for Message in MessageObject["result"]:
            CommentList.append(Message["update_id"])

        return (max(CommentList) + 1)
    
    def _GetUpdates_(self, CommentNumber):
        """
        This method will run the get update method from the API.
        it will return whatever the API gets.
        
        Variables:
            CommentNumber                 ``integer``
                is the number of the telegram user.
        """
        Update = None
        while Update is None:
            try:
                Update = self.TelegramApi.GetUpdates(CommentNumber)
            except urllib.error.HTTPError:
                Update = None
            time.sleep(0.5)
        return Update
    
    def run(self):
        """
        The method where the action happens
        
        Variables:
            \-
        """
  
        # Start the telegram API.
        self.TelegramApi = self._StartApi_()
        # Times the system  will retry to build a connection to the
        # telegram server.
        TryAgain = 3
        Save = False
        # Try to get the telegram offset from the filesystem.
        self.ApiOffset = self._LoadApiOffset_()
        
        while not self.ShutDownEvent.is_set():
            # check the input queue for orders
            
            Input = self._GetCommand_()
            
            if Input is not None:
                self._InterpretCommand_(Input)
            
            # only run if it's allowed 
            if self.Run is True:
                MessageObject = self._GetUpdates_(self.ApiOffset)

                if MessageObject is not None:
                    if not isinstance(MessageObject, int):
                        # if the messageObject is no error message or
                        # empty.
                        
                        
                        if "result" in MessageObject:
                            if MessageObject["result"]:
                                self.ApiOffset = self._GetCommentNumber_(MessageObject)
                                for Result in MessageObject["result"]:
                                    self._AddToWorkQueue_(Result)
                                    self._SaveMessages_(Result)
                        if self.ConnectionEvent.is_set() and TryAgain == 0:
                            self.ConnectionEvent.clear()
                            TryAgain = 3
                            Save = False
                            
                    elif isinstance(MessageObject, int):
                        if TryAgain > 0:
                            TryAgain -= 1
                        elif TryAgain == 0 and Save is False:
                            Save = True
                            self.ConnectionEvent.set()
                            
        self.WorkloadDoneEvent.set()             
        self._SaveApiOffset_()    

class OutputTelegramApiServer(_TelegramApiServer):
    
    def __init__(self,
                 Name,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ControllerQueue,
                 WorkloadQueue,
                 SendMessagesQueue,
                 ConnectionEvent,
                 WorkloadDoneEvent,
                 ShutDownEvent,):
        """
        Just initialising the subserver.
        ""        """        
        super().__init__(
                 Name,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ControllerQueue,
                 WorkloadQueue,
                 SendMessagesQueue,
                 ConnectionEvent,
                 WorkloadDoneEvent,
                 ShutDownEvent,
                 )
        
        self.Timeout = 1/28
        self.WorkloadSaveFile = "Workload.psi"
        self.WorkloadSaveFileFull = os.path.join(self.WorkloadFileDirectory,
                                                 self.WorkloadSaveFile)
        self.WorkloadDoneEvent = WorkloadDoneEvent         
    
    def _SaveMessages_(self, Message):
        """
        This is an extention of the in the super class defined method.
        """
        Message = (Message, "Output",)
        if super()._SaveMessages_(Message):
            return True
        else:
            return False             
        
    def _GetWorkload_(self, TimeOut = 0.1):
        """
        This method will get an element from the input queue.
        """
        ElementFromQueue = None
        try:
            if TimeOut < 0:
                ElementFromQueue = self.WorkloadQueue.get(block = True,
                                                       timeout = TimeOut)
            else:
                ElementFromQueue = self.WorkloadQueue.get()                
        except queue.Empty:
            pass
        except:
            raise
        
        return ElementFromQueue  
      
    def _SaveWorkload_(self, PreviousWorkload = None):
        """
        Save the remaning workload to the filesystem to send them later.
        
        Variables:
            PreviousWorkload              
        """
        Workload = []
        # if there was some waiting work to do
        if PreviousWorkload:
            Workload = PreviousWorkload
        
        # wait for the worker process finished  its workload.   
        self.WorkloadDoneEvent.wait()

        # check if workload exists
        while self.InputQueue.qsize() > 0:
            Element = None
            try:
                Element = self.GetElementsFromQueue(0.5)
            except queue.Empty:
                pass
            except:
                raise
            
            if Element is not None:
                Workload.append(Element)
        
        if Workload:
            # check if exists or else...
            if not os.path.isdir(self.WorkloadFileDirectory):
                os.mkdir(self.WorkloadFileDirectory)
            
            with open(self.WorkloadSaveFileFull, "wb") as OutputFile:
                pickle.dump(Workload, OutputFile)
    
    def _ReadWorkload_(self):
        """
        Check if the worload file exist and return the content, if it 
        does. Else return an empty list.
        """
        Workload = []
        if os.path.isdir(self.WorkloadFileDirectory):
            if os.path.isfile(self.WorkloadSaveFileFull):
                with open(self.WorkloadSaveFileFull, "rb") as InputFile:
                    Workload = pickle.load(self.WorkloadSaveFileFull, 
                                           InputFile)
                os.remove(self.WorkloadSaveFileFull)
            return Workload
        else:
            return Workload
        
    def _InterpretCommand_(self, Command):
        """
        This method will interpret all the commands send to the sever.
        It overrides the parent method.
        
        Variables:
            Command                      ``directory``
                contains the command and the possible addidtional 
                options.
        """
        raise NotImplemented

    def _SendToTelegram_(self, MessageObject):
        returnMessage = None
        attempts = 0
        while returnMessage is None and attempts < 3:
            try:
                returnMessage = self.TelegramApi.SendMessage(MessageObject)
            except  urllib.error.HTTPError:
                returnMessage = None
                attempts += 1
        return returnMessage            
                
    def run(self):
        # Start the telegram API.
        self.TelegramApi = self._StartApi_()
        # Check if there was any work from last start up.
        #Workload = self._ReadWorkload_()
        Run = True
        while not self.ShutDownEvent.is_set():
            while self.WorkloadQueue.qsize() > 0 and Run is True:
                """if not self.ConnectionEvent.is_set():
                    self._SaveWorkload_(Workload)
                    self.ConnectionEvent.wait()
                    Workload = self._ReadWorkload_()"""
                    
                
                Command = self._GetCommand_()
                
                if Command is not None:
                    if isinstance(Command, dir):
                        self._InterpretCommand_(Command)
                
                Work = self._GetWorkload_(self.Timeout)
                if Work is not None:
                    
                    ReturnMessage = self._SendToTelegram_(Work)
                    self._SaveMessages_({"message":ReturnMessage["result"]})

      
        while not self.WorkloadDoneEvent.is_set():
            Work = self._GetWorkload_(self.Timeout)
            if Work is not None:
                ReturnMessage = self._SendToTelegram_(Work)
                self._SaveMessages_(ReturnMessage)
        
class _TelegramApiServerComunicator(object):
    """
    The parent object that will first initialise the workers and 
    then be used to comunicate with the workers.
    """
    def __init__(self,
                 Name,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ControllerQueue,
                 WorkloadQueue,
                 SendMessagesQueue,
                 ConnectionEvent,
                 WorkloadDoneEvent,
                 ShutDownEvent,
                 ):
                
        self.ControllerQueue = ControllerQueue
        self.WorkloadQueue = WorkloadQueue  
        self.ConnectionEvent = ConnectionEvent
        
        self.Name = Name
        self._BotName = None
        
        self.TelegramApiServer = None

        self.ApiToken = ApiToken
        self.RequestTimer = RequestTimer
        self.LoggingObject = LoggingObject
        self.LanguageObject = LanguageObject
        self.ControllerQueue = ControllerQueue
        self.WorkloadQueue = WorkloadQueue
        self.SendMessagesQueue = SendMessagesQueue
        self.ConnectionEvent = ConnectionEvent
        self.WorkloadDoneEvent = WorkloadDoneEvent
        self.ShutdownEvent = ShutDownEvent
    
    def join(self):
        self.TelegramApiServer.join()
    
    def _PrepareServerCommand_(self, Order, ConnectionObject = None): 
        """
        This method will prepare the order for the server.
        
        Variables:
            Order                         ``string``
                This is the order the Server has to understand.
                
            ConnectionObject              ``object or None``
                This object is for possible communication with the 
                server process
        """
        Directory = {
                     "Order": Order}
        
        if ConnectionObject is not None:
            Directory["ConnectionObject"] = ConnectionObject
            
        return Directory
    
    def _InitTelegramServer_(self):
        """
        This method will be overwritten by the child obejcts.
        """
        raise NotImplementedError
    
    def _GetSubProcessPid_(self):
        """
        This methode will return the subprocess object.
        """
        return self.TelegramApiServer
    
    def _SendCommandToServer_(self, Object,):
        """
        This method will send the send a command to the server.
        
        Variables
            Object                        ``object``
                Can be everything that is pickable
        """
        self.ControllerQueue(Object)
    
    def _SendWorkToServer_(self, Object):
        """
        This method will send the send work to the server.
        
        Variables
            Object                        ``object``
                Can be everything that is pickable
        """
        self.WorkloadQueue.put(Object)

class InputTelegramAPI(_TelegramApiServerComunicator):
    """
    The child object that will either override or extend the parent 
    class. 
    It initialise the process that will recive the bot messages from the
    telegram server. As well as to communicate with that process.
    """ 
    def __init__(self,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ControllerQueue,
                 WorkloadQueue,
                 SendMessagesQueue,
                 ConnectionEvent,
                 WorkloadDoneEvent,
                 ShutDownEvent,):
        
        super().__init__(
                 Name="InputTelegramApiServer",
                 ApiToken = ApiToken,
                 RequestTimer = RequestTimer,
                 LoggingObject = LoggingObject,
                 LanguageObject = LanguageObject,
                 ControllerQueue = ControllerQueue,
                 WorkloadQueue = WorkloadQueue,
                 SendMessagesQueue = SendMessagesQueue,
                 ConnectionEvent = ConnectionEvent,
                 WorkloadDoneEvent = WorkloadDoneEvent,
                 ShutDownEvent = ShutDownEvent,
        ) 

        self._InitTelegramServer_()
        
    def _InitTelegramServer_(self):
        """
        This method is an override of the parent method.
        
        It simply starts the serverprocess.
        """
        self.TelegramApiServer = InputTelegramApiServer(
            Name=self.Name,
            ApiToken=self.ApiToken,
            RequestTimer=self.RequestTimer,
            LoggingObject = self.LoggingObject,
            LanguageObject = self.LanguageObject,
            ControllerQueue = self.ControllerQueue,
            WorkloadQueue = self.WorkloadQueue,
            SendMessagesQueue = self.SendMessagesQueue,
            ConnectionEvent = self.ConnectionEvent,
            WorkloadDoneEvent = self.WorkloadDoneEvent,
            ShutDownEvent = self.ShutdownEvent,
        )  
        
        self.TelegramApiServer.start()
                           
    def GetBotName(self):
        """
        This method will first get the bot name from the server process
        and then return it.
        """
        if self._BotName is None:
            LocalPipe, ServerPipe = multiprocessing.Pipe(False)
            self._SendToServer_(self._PrepareServerCommand_("GetBotName", 
                                                            ServerPipe)
                                )
            self._BotName = LocalPipe.recv()
            LocalPipe.close()
            ServerPipe.close()
            
        return self._BotName
            
    def SendApiOffset(self, Offset):
        """
        This method will send the send the api offset command, so that
        the server gets the new api offset.
        
        Variables:
            Offset                        ``integer``
                This is the telegram server offset.
        """
        LocalPipe, ServerPipe = multiprocessing.Pipe(True)
        self._SendCommandToServer_(
                            self._PrepareServerCommand_("SendApiOffset",
                                                         ServerPipe)
                                   )
        LocalPipe.send(Offset)
        LocalPipe.recv()
        LocalPipe.close()
        ServerPipe.close()
        
    def PauseProcess(self):
        """
        This method will send a process stop command to the server, that
        will filter down to the other workers.
        """
        self._SendCommandToServer_(self._PrepareServerCommand_("Stop"))
    
    def RunProcess(self):
        """
        This method will send a process run command to the server, so
        that the process may run.
        """
        self._SendCommandToServer_(self._PrepareServerCommand_("Run"))
            
class OutputTelegramAPI(_TelegramApiServerComunicator):
    """
    The child object that will either override or extend the parent 
    class. 
    It initialise the process that send the processed messages to the
    telegram server. As well as to communicate with that process.
    """
    def __init__(self,
                 ApiToken,
                 RequestTimer,
                 LoggingObject,
                 LanguageObject,
                 ControllerQueue,
                 WorkloadQueue,
                 SendMessagesQueue,
                 ConnectionEvent,
                 WorkloadDoneEvent,
                 ShutDownEvent,):
        
        super().__init__(
                 Name="OutputTelegramApiServer",
                 ApiToken = ApiToken,
                 RequestTimer = RequestTimer,
                 LoggingObject = LoggingObject,
                 LanguageObject = LanguageObject,
                 ControllerQueue = ControllerQueue,
                 WorkloadQueue = WorkloadQueue,
                 SendMessagesQueue = SendMessagesQueue,
                 ConnectionEvent = ConnectionEvent,
                 WorkloadDoneEvent = WorkloadDoneEvent,
                 ShutDownEvent = ShutDownEvent,
                         )
        
        
        
        self._InitTelegramServer_()
    
    def _InitTelegramServer_(self):
        """
        This method is an override of the parent method.
        
        It simply starts the serverprocess.
        
        Variables:
            \-
        """
        self.TelegramApiServer = OutputTelegramApiServer(
            Name = self.Name,
            ApiToken = self.ApiToken,
            RequestTimer = self.RequestTimer,
            LoggingObject = self.LoggingObject,
            LanguageObject = self.LanguageObject,
            ControllerQueue = self.ControllerQueue,
            WorkloadQueue = self.WorkloadQueue,
            SendMessagesQueue = self.SendMessagesQueue,
            ConnectionEvent = self.ConnectionEvent,
            WorkloadDoneEvent = self.WorkloadDoneEvent,
            ShutDownEvent = self.ShutdownEvent
        )
        
        self.TelegramApiServer.start()
    
    def SaveWorkload(self):
        """
        This method will send the save the workload command to the 
        server, to force a save to the filesystem.
        
        
        Variables:
            \-
        """
        InputPipe, OutputPipe = multiprocessing.Pipe(False)
        self._SendToServer_(self._PrepareServerCommand_("SaveWorkload", 
                                                        OutputPipe
                                                        )
                            )
        self.ConnectionEvent.clear()
        Answser = InputPipe.recv()
        if Answser is True:
            self.ConnectionEvent.set()
        InputPipe.close()
        OutputPipe.close()


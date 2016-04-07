    #!/usr/bin/python3.4
    # -*- coding: utf-8 -*-

# python standard library
import ssl
import json
import gzip
import zlib
import queue
import platform
import urllib.parse
import urllib.request
import multiprocessing

import gobjects  # my own classes
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
    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self,
                 ApiToken,
                 RequestTimer,   
                 **OptionalObjects
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

            InputQueue                     ``object``
                The data input queue to the main process.
            
            OutputQueue                   ``object``
                The data output queue to the main process.
                
            OptionalObjects               ``dictionary``
                contains the optional objects
                like:
                    LanguageObject        ``object``
                        contains the translation object
                        
                    LoggingObject         ``object``
                        contains the logging object needed to log
                        
                    ExitOnError           ``boolean``
                        Determines if the system should shut down
                        if an exception or error occurs.
                        The default value is False.
                        
        """
        
        self.ApiToken = ApiToken
        self.BotApiUrl = "{}{}".format(TelegramApi.BASE_URL, 
                                       self.ApiToken
                                       )
        
        # Predefining attribute so that it later can be used for evil.
        self.LanguageObject = None
        self.LoggingObject = None
        self.ExitOnError = False
        
        # This variables are in normal situations not used.
        # They are only used when the connection to telegram is being 
        # tested (at the start of the program).
        self.IsTest = False
        self.TestQueue = None
        self.Connection = True
        
        # This timer is needed to see if there is a problem with the
        # telegram server. If so the interval should be bigger (1 min 
        # instead given time 1 sec)
        self.RequestTimer = RequestTimer
        self.GivenRequestTimer = RequestTimer
        
        if "OptionalObjects" in OptionalObjects:
            OptionalObjects = OptionalObjects["OptionalObjects"]
            
        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
        else:
            self.LanguageObject = (
                language.Language().CreateTranslationObject()
            )

            
        if "LoggingObject" in OptionalObjects:
            self.LoggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LoggingObject = clogging.Logger()

        if "ExitOnError" in OptionalObjects:
            self.ExitOnError = OptionalObjects["ExitOnError"]
        
        if "IsTest" in OptionalObjects:
            self.IsTest = True
        
        # Here we are initialising the function for the translations.
        self._ = self.LanguageObject.gettext

        self.SSLEncryption = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) 

#         this looks like this:
#         {
#         'Content-Type':
#             'application/x-www-form-urlencoded;charset=utf-8',
#         'User-agent': "BetterPollBot/0.1 (Windows; 8; 6.2.9200) \
#       Python-urllib/('v3.4.3:9b73f1c3e601', 'Feb 24 2015 22:43:06') \
#       from https://github.com/apmzideas/BetterPollBot"
#         }

        self.Headers = {
            'User-agent': (("{AppName}/{Version}({Platform})"
                            "Python-urllib/{PythonBuild} from {Hosted}"
                            ).format(
                                AppName = gobjects.__AppName__,
                                Version = gobjects.__version__,
                                Platform = ('; '.join(
                                                platform.system_alias(
                                                    platform.system(),
                                                    platform.release(),
                                                    platform.version()
                                                    )
                                                      )
                                            ),
                                PythonBuild = platform.python_build(),
                                Hosted = gobjects.__hosted__
                                )
                           ),
            "Content-Type":
                "application/x-www-form-urlencoded;charset=utf-8",
            "Accept-Encoding": "gzip,deflate"
        }

        # Test if the content can be compressed or not
        self.Compressed = True

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
                        
                        TheResponse = gzip.decompress(Request.read())
                    elif RequestEncoding == "deflate":
                        Decompress = zlib.decompressobj(
                                                        -zlib.MAX_WBITS  # see above
                                                        )
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
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " +
                    self._("The address is forbidden to access, please try "
                           "later."),
                )
            elif Error.code == 404:
                self.LoggingObject.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " +
                    self._("The requested resource was not found. This status "
                           "code can also be used to reject a request without "
                           "closer reason. Links, which refer to those error "
                           "pages, also referred to as dead links."),
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
                self.RequestTimer = 60000.0
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

            # For the recursive loop, so that the system can handel itself
            # better
            if self.ExitOnError:
                self.LoggingObject.info(self._("Exiting the system!"))
                raise SystemExit

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
            headers = self.Headers
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

        Request = urllib.request.Request(self.BotApiUrl + "/getUpdates",
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

        Request = urllib.request.Request(self.BotApiUrl + "/sendMessage",
                                         data=MessageData,
                                         headers=self.Headers
                                         )

        return self.SendRequest(Request,)

    def ForwardMessage(self, ChatId, FromChatId, MessageId):
        """
        A method to forward a received message
        
        This function will maybe be build in the future for now
        it's not doing anything.
        """
        #MessageData = {}
        raise NotImplementedError

class TelegramApiServer(multiprocessing.Process):

    def __init__(self,
                 Name, 
                 ApiToken,
                 RequestTimer,
                 InputQueue,
                 OutputQueue,
                 ConnectionEvent,
                 ShutDownEvent,
                 **OptionalObjects):
                 
        super().__init__(name = Name)
        self.Name = Name
        self.InputQueue = InputQueue
        self.OutputQueue = OutputQueue
        self.ConnectionEvent = ConnectionEvent
        self.ShutDownEvent = ShutDownEvent
        
        self.Data = {
                     "ApiToken": ApiToken,
                     "RequestTimer":RequestTimer,
                     "OptionalObjects": OptionalObjects
                     }
        
        self.TelegramApi = None
    
    def _StartApi_(self):
        """
        This method will create the TelegeramApi object
        """
        self.TelegramApi = TelegramApi(
                 ApiToken = self.Data["ApiToken"],
                 RequestTimer = self.Data["RequestTimer"],   
                 OptionalObjects = self.Data["OptionalObjects"]
        )
    
    def AddToQueue(self, ElementToAdd):
        """
        This method will add an element to the worker queue
        """
        self.OutputQueue.put(ElementToAdd, True)
    
    def GetElementsFromQueue(self,):
        ElementFromQueue = None
        try:
            ElementFromQueue = self.InputQueue.get_nowait()
        except queue.Empty:
            pass
        
        return ElementFromQueue
            
    def run(self):
        raise NotImplementedError
     
class InputTelegramApiServer(TelegramApiServer):
    
    def __init__(self,
                 Name,
                 ApiToken,
                 RequestTimer,
                 InputQueue,
                 OutputQueue,
                 ConnectionEvent,
                 ShutDownEvent,
                 OptionalObjects):
                 
        super().__init__(name = Name)
           
    def GetBotName(self):
        """
        This methode gets the bot name from the Api
        """
        BotName = self.TelegramApi.GetBotName()
        return BotName
    
    def InterpretCommand(self, Command):
        Order, ConnectionObject = Command
                
        if Order == "GetBotName":
            BotName = self.GetBotName()
            ConnectionObject.send(BotName)
            ConnectionObject.close()
        else:
            pass
       
    def run(self):
        """
        The method where the action happens
        """
        while self.ShutDownEvent.is_set():
            # check the input queue for orders
            Input = None

            try:
                Input = self.InputQueue.get_nowait()
            except queue.Empty:
                pass
            
            if Input is not None:
                self.InterpretCommand(Input)
                       
        """
        InternalQueue = multiprocessing.Queue()
        InternalQueue.put(None)

        run = True
        while run:
            if self.MasterQueue.empty():
                run = False
            # Get the updates from the telegram serves.
            if self.SqlObject.DetectConnection() is True:
                # check if queue has something for us in it
                CommentNumber = []
                while True:
                    if self.MasterQueue.empty() is False:
                        CommentNumber.append((self.MasterQueue.get()))
                    else:
                        break
                if len(CommentNumber) == 1:
                    CommentNumber = CommentNumber[0]
                elif len(CommentNumber) > 1:
                    CommentNumber = max(CommentNumber)
                else:
                    CommentNumber = None

                Results = self.TelegramObject.GetUpdates(CommentNumber)

                # Do
                if Results is not None:
                    for Message in Results["result"]:
                        MessageProcessor = (
                            messages.msg_processor.MessageProcessor(
                                Message,
                                LanguageObject=self.LanguageMasterObject,
                                SqlObject=self.SqlObject,
                                LoggingObject=self.MasterLogger,
                                ConfigurationObject=self.Configuration,
                                BotName=self.BotName
                            )
                        )

                         # This command sends the message to the user
                        InterpretedMessage = (
                            MessageProcessor.InterpretMessage()
                        )
                        if InterpretedMessage != None:
                            #print(TelegramObject.SendMessage(
                            # InterpretedMessage))
                            self.TelegramObject.SendMessage(InterpretedMessage)
                        # Set the CommentNumber to a actual ChatId number,
                        # so that the incoming list is always actual.
                        # This number has to be 1 bigger than the oldest unit
                        self.MasterQueue.put(MessageProcessor.UpdateId + 1)
                        
        """

class OutputTelegramApiServer(TelegramApiServer):
        pass
        
class TelegramApiServerComunicator(object):
    """
    The parent object that will first initialise the workers and 
    then be used to comunicate with the workers.
    """
    def __init__(self,
                 Name,
                 ApiToken,
                 RequestTimer,
                 ConnectionEvent,
                 ShutDownEvent,
                 OptionalObjects
                 ):
                
        self.InputQueue = multiprocessing.Queue()
        self.OutputQueue = multiprocessing.Queue()  
        self.Name = Name
        self._BotName = None
        
        self.TelegramApiServer = None
        self.Data = {
                     "ApiToken": ApiToken,
                     "RequestTimer":RequestTimer,
                     "ConnectionEvent":ConnectionEvent,
                     "ShutDownEvent":ShutDownEvent,
                     "OptionalObjects": OptionalObjects
                     }    

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
    
    def _SendToServer_(self, Object, ):
        """
        This method will send the send the Object to the server.
        
        Variables
            Object                        ``object``
                Can be everything that is pickable
        """
        self.InputQueue.put(Object)
              
class OutputToTelegram(TelegramApiServerComunicator):

    def __init__(self,
                 ApiToken,
                 RequestTimer,
                 ConnectionEvent,
                 ShutDownEvent,
                 **OptionalObjects):
        
        super().__init__(
                         Name = "OutputTelegramApiServer",
                         ApiToken = ApiToken,
                         RequestTimer = RequestTimer,
                         InputQueue = self.InputQueue,
                         OutputQueue = self.OutputQueue,
                         ConnectionEvent = ConnectionEvent,
                         ShutDownEvent = ShutDownEvent,
                         OptionalObjects = OptionalObjects    
                         )
            
        self._InitTelegramServer_()
    
    def _InitTelegramServer_(self):
        """
        This method is an override of the parent method.
        
        It simply starts the serverprocess.
        """
        self.TelegramApiServer = OutputTelegramApiServer(
            Name = self.Name,
            ApiToken = self.ApiToken,
            RequestTimer = self.RequestTimer,
            InputQueue = self.InputQueue,
            OutputQueue = self.OutputQueue,
            ConnectionEvent = self.ConnectionEvent,
            ShutDownEvent = self.ShutDownEvent,
            OptionalObjects = self.OptionalObjects
        )
    
    def SaveWorkload(self):
        InputPipe, OutputPipe = multiprocessing.Pipe(False)
        self._SendToServer_(("SaveWorkload",OutputPipe,))
        self._BotName = InputPipe.recv()
        InputPipe.close()
        OutputPipe.close()
        
    
class InputFromTelegram(TelegramApiServerComunicator):
     
    def __init__(self,
                 ApiToken,
                 RequestTimer,
                 ShutDownEvent,
                 ConnectionEvent,
                 **OptionalObjects
                 ):
        
        super().__init__(
            Name = "InputTelegramApiServer",
            ApiToken = ApiToken,
            RequestTimer = RequestTimer,
            ConnectionEvent = ConnectionEvent,
            ShutDownEvent = ShutDownEvent,
            OptionalObjects = OptionalObjects
        ) 
          
        self._InitTelegramServer_()
        
    def _InitTelegramServer_(self):
        """
        This method is an override of the parent method.
        
        It simply starts the serverprocess.
        """
        self.TelegramApiServer = InputTelegramApiServer(
            Name = self.Name,
            ApiToken = self.ApiToken,
            RequestTimer = self.RequestTimer,
            InputQueue = self.InputQueue,
            OutputQueue = self.OutputQueue,
            ConnectionEvent = self.ConnectionEvent,
            ShutDownEvent = self.ShutDownEvent,
            OptionalObjects = self.OptionalObjects
        )  
                             
    def GetBotName(self):
        """
        This method will first get the bot name from the server process
        and then return it.
        """
        if self._BotName is None:
            InputPipe, OutputPipe = multiprocessing.Pipe(False)
            self._SendToServer_(("GetBotName",OutputPipe,))
            self._BotName = InputPipe.recv()
            InputPipe.close()
            OutputPipe.close()
        return self._BotName
            
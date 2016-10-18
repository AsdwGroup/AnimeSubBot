#!/usr/bin/python
# -*- coding: utf-8 -*-

# standard lib
import re
import json
import datetime

# The custom modules
from . import message # imports in the same folder (module)
from . import emojis

class MessagePreProcessor(object):
    """
    This class is used as the user message preanalyser.
    This class will primary be used so that the code will
    be easily reusable.
    
    The MessageObject will only contains a single message object, 
    so that this class will be thread save and so that we can run
    multiple instances per unit.    
    
    The message object will contain all the following parts.\n
    .. code-block:: python\n
        {
                       'message': {
                                   'date': 1439471738, 
                                   'text': '/start',
                                   'from': {
                                            'id': 3xxxxxx6,
                                            'last_name': 'Sample',
                                            'first_name': 'Max',
                                            'username': 'TheUserName'
                                            }, 
                                   'message_id': 111, 
                                   'chat': {
                                            'id': -xxxxxxx,
                                            'title': 'Drive'
                                            }
                                   },
                        'update_id': 469262057
                        }
        }
    
    """

    def __init__(self, 
                 MessageObject,
                 OutputQueue,
                 SqlObject,
                 Cursor,
                 LanguageObject,
                 LoggingObject,
                 ConfigurationObject,):
        """
        Variables:
            MessageObject                 ``object``
                the message to be analysed message
                

        """

        self.LastSendCommand = None
        self.LastSendCommand = None
        self.LastUsedId = None
        # This variable will stop the system if the message was send during process
        self.MessageSend = False

        # Predefining attributes so that it later can be used for evil.
        self.LoggingObject = None
        self.ConfigurationObject = None

        # output queue
        self._OutputQueue_ = OutputQueue
        # SqlObjects
        self.SqlObject = SqlObject
        self.SqlCursor = Cursor

        self.LoggingObject = LoggingObject

        self.ConfigurationObject = ConfigurationObject

        # This variable is needed for the logger so that the log end up 
        # getting printed in the correct language.
        self.M_ = LanguageObject.CreateTranslationObject().gettext



        if "update_id" in MessageObject:
            # The update‘s unique identifier. Update identifiers start from a
            # certain positive number and increase sequentially. This ID
            # becomes especially handy if you’re using web hooks, since it
            # allows you to ignore repeated updates or to restore the correct
            # update sequence, should they get out of order.
            self.UpdateId = MessageObject["update_id"]

        if "message_id" in MessageObject["message"]:
            # Unique message identifier
            self.MessageID = MessageObject["message"]["message_id"]

        # get the user of the message
        # get user data from the message
        if "first_name" in MessageObject["message"]["from"]:
            # User‘s or bot’s first name
            self.UserFirstName = MessageObject["message"]["from"]["first_name"]
        else:
            self.UserFirstName = ""

        if "last_name" in MessageObject["message"]["from"]:
            # Optional. User‘s or bot’s last name
            self.UserLastName = MessageObject["message"]["from"]["last_name"]
        else:
            self.UserLastName = ""

        if "username" in MessageObject["message"]["from"]:
            # Optional. User‘s or bot’s username
            self.UserName = MessageObject["message"]["from"]["username"]
        else:
            self.UserName = ""

        if "id" in MessageObject["message"]["from"]:
            # Unique identifier for this user or bot
            self.UserId = MessageObject["message"]["from"]["id"]

        # Add user to the system if not exists
        if self.UserExists() is False:
            self.AddUser()
        
        # Get the Internal user id
        self.InternalUserId, self.IsAdmin = self.GetUserData()

        # Here we are initialising the function for the translations.
        # Get the user settings from the user that has send the message
        Query = ("SELECT User_Setting_Table.User_String FROM "
                 "User_Setting_Table INNER JOIN Setting_Table ON "
                 "User_Setting_Table.Master_Setting_Id="
                 "Setting_Table.Id WHERE Setting_Table.Setting_Name=%s"
                 " AND User_Setting_Table.Set_By_User=%s;"
                 )

        Data = ("Language", self.InternalUserId)

        self.LanguageName = (
            self.SqlObject.ExecuteTrueQuery(
                self.SqlCursor,
                Query,
                Data
            )[0]["User_String"])
        
        self.LanguageObject = LanguageObject
        
        Language = self.LanguageObject.CreateTranslationObject(
            Languages=[self.LanguageName]
        )

        # create the translator        
        self._ = Language.gettext

        # Get the text message with the command
        if "text" in MessageObject["message"]:
            self.Text = MessageObject["message"]["text"]
        else:
            self.Text = None

        # where was the message send from the user or the group
        # Get the chat id
        if "id" in MessageObject["message"]["chat"]:
            # Unique identifier for this group chat
            self.ChatId = MessageObject["message"]["chat"]["id"]

        # Check if message is from a group or not.
        if self.ChatId == self.UserId:
            self.InGroup = False
        else:
            self.InGroup = True
            self.GroupName = MessageObject["message"]["chat"]["title"]
            # Check if group exists
            if self.GroupExists() is False:
                self.AddGroup()
            self.InternalGroupId = self.GetInternalGroupId()

        if "date" in MessageObject["message"]:
            # changing the arrival time to a python understandable time
            # as well as a MySql understandable format
            self.MessageDate =  datetime.datetime.fromtimestamp(
                                    int(MessageObject["message"]["date"])
                                    ).strftime('%Y-%m-%d %H:%M:%S')

        if "forward_from" in MessageObject["message"]:
            self.ForwardedFrom = MessageObject["message"]["forward_from"]

        if "forward_date" in MessageObject["message"]:
            # Optional. For forwarded messages, date the original
            # message was sent in Unix time
            self.forward_date = MessageObject["message"]["forward_from"]

        if "reply_to_message" in MessageObject["message"]:
            # Optional. For replies, the original message. Note that
            # the Message object in this field will not contain further
            # reply_to_message fields even if it itself is a reply.
            self.ReplyToMessage = MessageObject["message"]["reply_to_message"]

        if "audio" in MessageObject["message"]:
            # Optional. Message is an audio file, information about the file
            self.MessageAudio =  MessageObject["message"]["audio"]

        if "document" in MessageObject["message"]:
            # Optional. Message is a general file, information about the file
            self.MEssageDocument = MessageObject["message"]["document"]

        if "photo" in MessageObject["message"]:
            # Optional. Message is a photo, available sizes of the photo
            self.MessagePhoto = MessageObject["message"]["photo"]

        if "sticker" in MessageObject["message"]:
            # Optional. Message is a sticker, information about the sticker
            self.MessageSticker = MessageObject["message"]["sticker"]

        if "video" in MessageObject["message"]:
            # Optional. Message is a video, information about the video
            self.MessageVideo = MessageObject["message"]["video"]

        if "caption" in MessageObject["message"]:
            # Optional. Caption for the photo or video
            self.MessageCaption = MessageObject["message"]["caption"]

        if "contact" in MessageObject["message"]:
            # Optional. Message is a shared contact, information about
            # the contact
            self.MessageContact = MessageObject["message"]["contact"]

        if "location" in MessageObject["message"]:
            # Optional. Message is a shared location, information about
            # the location
            self.MessageLocation = MessageObject["message"]["location"]
        
        if "venue" in MessageObject["message"]:
            # Optional. Message is a venue, information about the venue
            self.Venue = MessageObject["message"]["venue"]
        
        if "new_chat_participant" in MessageObject["message"]:
            # Optional. A new member was added to the group, information
            #  about them (this member may be bot itself)
            self.MessageNewChatParticipant = (
                MessageObject["message"]["new_chat_participant"]
            )

        if "left_chat_participant" in MessageObject["message"]:
            # Optional. A member was removed from the group, information
            # about them (this member may be bot itself)
            self.MessageLeftChatParticipant = (
                MessageObject["message"]["left_chat_participant"]
            )

        if "new_chat_title" in MessageObject["message"]:
            # Optional. A group title was changed to this value
            self.MessageNewChatTitle = (
                MessageObject["message"]["new_chat_title"]
            )

        if "new_chat_photo" in MessageObject["message"]:
            # Optional. A group photo was change to this value
            self.MessageNewChatPhoto = (
                MessageObject["message"]["new_chat_photo"]
            )

        if "delete_chat_photo" in MessageObject["message"]:
            # Optional. Informs that the group photo was deleted
            self.MessageDeleteChatPhoto = (
                MessageObject["message"]["delete_chat_photo"]
            )

        if "group_chat_created" in MessageObject["message"]:
            # Optional. Informs that the group has been created
            self.MessageGroupChatCreated = (
                MessageObject["message"]["group_chat_created"]
            )
            
        if "supergroup_chat_created" in MessageObject["message"]:
            # Optional. Service message: the supergroup has been created
            self.SupergroupChatCreated = MessageObject["message"]["supergroup_chat_created"]
        
        if "channel_chat_created" in MessageObject["message"]:
            # Optional. Service message: the channel has been created
            self.ChannelChatCreated = MessageObject["message"]["channel_chat_created"] 
        
        if "migrate_to_chat_id" in MessageObject["message"]:
            # Optional. The group has been migrated to a supergroup with
            # the specified identifier, not exceeding 1e13 by absolute 
            # value
            self.MigrateToChatId = MessageObject["message"]["migrate_to_chat_id"]
        
        if "migrate_from_chat_id" in MessageObject["message"]:
            # Optional. The supergroup has been migrated from a group 
            # with the specified identifier, not exceeding 1e13 by 
            # absolute value
            self.migrate_from_chat_id = MessageObject["message"]["migrate_from_chat_id"]
        
        if "pinned_message" in MessageObject["message"]:
            # Optional. Specified message was pinned. Note that the 
            # Message object in this field will not contain further 
            # reply_to_message fields even if it is itself a reply.
            self.PinnedMessage = MessageObject["message"]["pinned_message"]       
    
    def _SendToQueue_(self, MessageObject):
        """
        This methode will be a private function with the task to send the finished message to the postprocessing and shipping class. 

        Variables:
            - MessageObject                    ``object``
                is the message object that has to be send
        """

        MessageObjectList = []

        if  MessageObject is not None:
            if len(MessageObject.Text) > 4096:
                TemporaryObjectHolder = MessageObject
                for TextPart in MessageProcessor.Chunker(MessageObject.Text, 4095):
                    TemporaryObjectHolder.Text = TextPart
                    MessageObjectList.append(TemporaryObjectHolder)
            else:
                MessageObjectList.append(MessageObject)

        if self.MessageSend is False:
            Workload = []

            if isinstance(MessageObject, list):
               Workload.extend(MessageObject)
            elif isinstance(MessageObject, dict):
                Workload.append(MessageObject)  
        
            for Message in MessageObjectList:
                self._OutputQueue_.put(Message)
                       
    def UserExists(self, ):
        """
        This method will detect if the use already exists or not.
        
        The following query will return 1 if a user with the specified 
        username exists a 0 otherwise.
        
        .. code-block:: sql\n
            SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'username')
        
        It will return a True if the database returns a 1 and a False
        if the database a 0.
        Variables:
            \-
        """

        exists = self.SqlObject.ExecuteTrueQuery(
            self.SqlObject.CreateCursor(Dictionary=False),
            Query=("SELECT EXISTS(SELECT 1 FROM User_Table WHERE"
                   " External_Id = %s);"
                   ),
            Data=self.UserId
        )[0][0]
        if exists == 0:
            return False
        else:
            return True

    def AddUser(self, ):
        """
        This method will add a new user to the database.
        
        Variables:
            \-
        """
        # Insert into user
        TableName = "User_Table"
        Columns = {
            "External_Id": self.UserId,
            "User_Name": self.UserName,
            "First_Name": self.UserFirstName,
            "Last_Name": self.UserLastName
        }

        self.SqlObject.InsertEntry(self.SqlCursor, TableName, Columns)
        self.SqlObject.Commit()

        # insert default settings
        # get default values

        # get the default settings
        # get the default language
        FromTable = "Setting_Table"
        Columns = ["Id", "Default_String"]
        Where = [["Setting_Name", "=", "%s"]]
        Data = ("Language")
        MasterSetting = self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable=FromTable,
            Columns=Columns,
            Where=Where,
            Data=Data
        )[0]

        TableName = "User_Setting_Table"
        self.InternalUserId = self.GetUserData()[0]
        Columns = {
            "Master_Setting_Id": MasterSetting["Id"],
            "Set_By_User": self.InternalUserId,
            "User_String": MasterSetting["Default_String"]
        }

        self.SqlObject.InsertEntry(
            self.SqlCursor,
            TableName,
            Columns
        )

        self.SqlObject.Commit()

    def GetUserData(self):
        """
        This method will get the internal user id and the admin state 
        from the database.
        
        Variables:
            \-
        """
        # first the internal user id
        FromTable = "User_Table"
        Columns = ["Internal_Id", "Is_Admin"]
        Where = [["External_Id", "=", "%s"]]
        Data = (self.UserId,)

        temp = self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable=FromTable,
            Columns=Columns,
            Where=Where,
            Data=Data
        )[0]
        internalUserId = temp["Internal_Id"]
        
        Is_Admin = temp["Is_Admin"]
        if Is_Admin == 0:
            Is_Admin = False
        else:
            Is_Admin = True
            
        return internalUserId, Is_Admin
    
    def GetMessageObject(self,):
        """
        This method will generate a default message object to work with.
        
        Variables:
            \-
        """
        MessageObject = message.MessageToBeSend(ToChatId=self.ChatId)
        MessageObject.Text = self._("Sorry, but this command could not be"
                                    " interpreted.")
        
        return MessageObject

    @staticmethod
    def Chunker(ListOfObjects, SizeOfChunks):
        """
        Yield successive n-sized (SizeOfChunks) chunks from the list (ListOfObjects).
        
        This methode will not return anything, but act as a generator object.
        
        Variables:
            - ListOfObjects               ``generator, list or string``
                This variable holds all the stuff to split.
            
            - SizeOfChunks                ``integer``
                Holds the size of the chunks to turn the ListOfObjects 
                into.
                
        """
        for i in range(0, len(ListOfObjects), SizeOfChunks):
            yield ListOfObjects[i:i+SizeOfChunks]
    
    @staticmethod
    def SpacedChunker(String, SizeOfChunks):
        """
        This method will split a sting by the spaces inside and will separate them correctly.

        Variables:
            - String               ``string``
                This variable holds all the stuff to split.
            
            SizeOfChunks                ``integer``
                Holds the size of the chunks to turn the ListOfObjects 
                into.
        """
        
        EndList = []
        StringSize = 0
        TempString = ""
        for i in String.split(" "):
           
            StringSize += len(i)
            if StringSize > SizeOfChunks:
                TempString += i
            else:
                EndList.append(TempString)
                StringSize = 0
                TempString = ""
                StringSize += len(i)

            StringSize = 0
            pass 

        return EndList
                       
    def GroupExists(self):
        """
        This method checks if the group exists or not.
        
        The following query will return a 1 if a user with the 
        specified username exists a 0 otherwise. From that on
        the system will return True if the group exists and if it
        doesn't False.\n
        .. code-block:: sql\n
            SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'username')
        
        Variables:
            \-
        """

        # This method checks in the database if the group (if it is one)
        # exists.


        Exists = self.SqlObject.ExecuteTrueQuery(
            self.SqlObject.CreateCursor(Dictionary=False),
            Query="SELECT EXISTS(SELECT 1 FROM Group_Table WHERE"
                  " External_Group_Id = %s);",
            Data=self.ChatId
        )[0][0]

        if Exists == True:
            return True
        else:
            return False

    def AddGroup(self):
        """
        This method will add an not existing group to the database.
        
        Variables:
            \-
        """
        # This method will add the group if it doen't exit.
        self.SqlObject.InsertEntry(
            self.SqlCursor,
            TableName="Group_Table",
            Columns={
                "External_Id": self.ChatId,
                "Group_Name": self.GroupName
            },
        )
        self.SqlObject.Commit(self.SqlCursor)

    def GetInternalGroupId(self):
        """
        This method will get the user internal group id.
        
        This method will return the the internal group id directly from
        the database.
        Variables:
            \-
        """

        return self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable="Group_Table",
            Columns=["Internal_Group_Id"],
            Where=[["External_Group_Id", "=", "%s"]],
            Data=self.ChatId
        )

    def SetLastSendCommand(self, Command, LastUsedId=None, LastUsedData = None):
        """
        This method will save the last user command into the database.
        
        The commands used can be set manually from the programmer
        so that it can be user for flow control.
        
        Example:\n
        .. code-block:: guess\n
            /Command option
            
        Variables:
            Command                     ``string``
                This is the used command with the option, that was 
                used.
                
            LastUsedId                  ``integer``
                This is the last used id, it can be every id, depending 
                the situation.
        """

        TableName = "Session_Table"
        Columns = {
            "Command_By_User": self.InternalUserId,
            "Command": Command,

        }

        Duplicate = {
            "Command": Command,

        }
        if LastUsedId is not None:
            Columns["Last_Used_Id"] = LastUsedId
            Duplicate["Last_Used_Id"] = LastUsedId
        
        if LastUsedData is not None:
            Columns["Last_Used_Data"] = LastUsedData
            Duplicate["Last_Used_Data"] = LastUsedData

        SetLastSendCommand = self.SqlObject.InsertEntry(
            self.SqlCursor,
            TableName=TableName,
            Columns=Columns,
            Duplicate=Duplicate)
        self.SqlObject.Commit()

    def GetLastSendCommand(self):
        """
        This method will get the last user command.
        
        This method will get the last user command from the database,
        so that the last command can be used for flow control.
        The command are mostly set by the system and not by the user,
        at least not direct.
        
        Example:\n
        .. code-block:: guess\n
            /command option
            
        Variables:
            \-
        
        Return:
            - LastSendCommand["Last_Used_Id"]
            - LastSendCommand["Command"]
           
        """

        FromTable = "Session_Table"
        Columns = ["Command", "Last_Used_Id", "Last_Used_Data"]
        Where = [["Command_By_User", "=", "%s"]]
        Data = (self.InternalUserId,)
        LastSendCommand = self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable=FromTable,
            Columns=Columns,
            Where=Where,
            Data=Data
        )

        if len(LastSendCommand) > 0:
            LastSendCommand =  LastSendCommand[0]
        else:
            LastSendCommand["Last_Used_Id"] = None
            LastSendCommand["Command"] = None
            LastSendCommand["Last_Used_Data"] = none
        return LastSendCommand

    def ClearLastCommand(self):
        """
        This method clears the last set command if the process finished.
        
        Variables:
            \-
        """

        self.SqlObject.UpdateEntry(
            Cursor=self.SqlCursor,
            TableName="Session_Table",
            Columns={
                "Command": "0",
                "Last_Used_Id": 0
            },
            Where=[["Command_By_User", self.InternalUserId]],
            Autocommit=True
        )

    def ChangeUserLanguage(self, Language):
        """
        This method changes the user language.
        
        This method is responsible for initialising the language change, 
        as well as activating the new language. It will return True
        if the new language could be initialised and False if there has
        been an error.
        
        Variables:
            Language                    ``string``
                should be a string with the new language file
        """

        if Language == "English":
            Language = "en_US"
        elif Language == "Deutsch":
            Language = "de_DE"

        self.SqlObject.UpdateEntry(
            Cursor=self.SqlCursor,
            TableName="User_Setting_Table",
            Columns={"User_String": Language},
            Where=[["Master_User_Id", self.InternalUserId]],
            Autocommit=True
        )
        try:
            self.LanguageName = Language
            Language = self.LanguageObject.CreateTranslationObject(self.LanguageName)


            self._ = self.LanguageObject.gettext
            if self.LanguageObject.info()["language"] != Language:
                raise ImportError(
                    self.M_("Unknown language error")
                )
            return True
        except ImportError as Error:
            self.LoggingObject.error("{} {}".format(
                self.M_("There has been an error with the changing of the "
                        "language class, this error has been returned: {Error}"
                        ).format(Error=Error), 
                self.M_("Please, contact your administrator.")
                                                    )
                                     )
            return False

    def InterpretMessage(self):
        """
        This method is here to be overriden by a child class.
        
        Variables:
            \-
        """
        raise NotImplementedError
        
class MessageProcessor(MessagePreProcessor):
    """
    This class is used as the user message analyser. 
    It extends the MessagePreProcessor class with the needed
    methodes for analysing the message object.
    
    The MessageObject will only contains a single message object, 
    so that this class will be thread save and so that we can run
    multiple instances per unit.    
    
    The message object will contain all the following parts.\n
    .. code-block:: python\n
        {
                       'message': {
                                   'date': 1439471738, 
                                   'text': '/start',
                                   'from': {
                                            'id': 3xxxxxx6,
                                            'last_name': 'Sample',
                                            'first_name': 'Max',
                                            'username': 'TheUserName'
                                            }, 
                                   'message_id': 111, 
                                   'chat': {
                                            'id': -xxxxxxx,
                                            'title': 'Drive'
                                            }
                                   },
                        'update_id': 469262057
                        }
        }
    
    """
    
    def InterpretMessage(self):
        """
        This method interprets the user text.

        This method is used as an pre interpreter of the user send text.
        It primarily chooses if the user send text is a command or not.
        It will choose the correct interpretation system, if the text has
        been send by a group or not.
        It returns the MessageObject after letting it get modified.

        Variables:
            \-
        """
        MessageObject = self.GetMessageObject()

        # check if message is a command
        if self.Text is not None:
            # Analyse the text and do your stuff.
            
            # delete the annoying bot command from the text to analyse
            # If the name of the bot is used in the
            # command delete the @NameOfBot
            self.Text = re.sub(r"^(@\w+[bB]ot\s+)?", "", self.Text)

            if self.Text.startswith("/"):

                if self.InGroup is False:
                    MessageObject = self.InterpretUserCommand(MessageObject)
                else:
                    MessageObject = self.InterpretGroupCommand(MessageObject)
            else:
                # Get the last send command and the last used id
                LastSendCommand = self.GetLastSendCommand()
                self.LastUsedId = LastSendCommand["Last_Used_Id"]
                self.LastSendCommand = LastSendCommand["Command"]
                self.LastSendData = LastSendCommand["Last_Used_Data"]

                if self.InGroup is False:
                    MessageObject = self.InterpretUserNonCommand(MessageObject)
                #else:
                #    MessageObject = self.InterpretGroupNonCommand(MessageObject) 
        else:
            MessageObject = None
            
        # checking that the lenght of the message never will be longer then 
        # 4096 characters long
                

        self._SendToQueue_(MessageObject)

    def InterpretUserCommand(self, MessageObject):
        """
        This method interprets the commands form the user text.

        This method is used as an interpreter of the user send
        commands. It returns the MessageObject
        after analysing and modifying the MessageObject to respond
        the user Text.

        Variables:
            - MessageObject                    ``object``
                is the message object that has to be modified
        """
        # register the command in the database for later use
        if self.Text.startswith("/start"):
            MessageObject.Text = self._("Welcome.\nWhat can I do for you?"
                                            "\nPress /help for all my commands"
                                            )
            Markup = [
                        ["/help"],
                        ["/list"]
                    ]
            if self.IsAdmin is True:
                Markup[0].append("/admin")
                    
            MessageObject.ReplyKeyboardMarkup(Markup,
                 OneTimeKeyboard=True
            )
                
            self.ClearLastCommand()

        # this command will list the anime content on the server
        elif self.Text == "/list":
            # this command will send the anime list
            MessageObject.Text = self._("Sorry\nAt the moment this command is not supported")
            
        elif self.Text == "/done":
            self.Text = "/start"
            MessageObject = self.InterpretUserCommand(MessageObject)

        elif self.Text == "/help":
            MessageObject.Text = self._(
                "Work in progress! @AnimeSubBot is a bot."
            )

        elif self.Text == "/admin":
            # if that person is an administrator.
            if self.IsAdmin:
                self.InterpretAdminCommands(MessageObject)
                self.SetLastSendCommand("/admin", None)
            else:
                MessageObject.Text = self._("You don't have the right to use that command.")
            
        # the settings are right now not supported, maybe later.
            """elif self.Text == "/settings":
                # This command will send the possible setting to the user
                self.SetLastSendCommand("/settings", None)
                MessageObject.Text = self._("Please, choose the setting to change:"
                                            )
                MessageObject.ReplyKeyboardMarkup(
                    [
                        ["/language"],
                        ["/comming soon"]
                    ],
                    OneTimeKeyboard=True
                )
                
            elif self.Text == "/language":
                # This option will change the user language
                # Set the last send command
    
                self.SetLastSendCommand("/language")
    
                MessageObject.Text = self._(
                    "Please choose your preferred language:"
                )
                MessageObject.ReplyKeyboardMarkup([
                    ["English"],
                    ["Deutsch"],
                    ["Français"]
                ],
                    OneTimeKeyboard=True
                )
            """

        else:
            # send that the command is unknown
            MessageObject.Text = self._("I apologize, but this command is not supported.\n"
                                        "Press or enter /help to get help.")

        return MessageObject

    def InterpretUserNonCommand(self, MessageObject):
        """
        This method interprets the non commands from user text.

        This method is used as an interpreter of the system set
        commands and the user send text. It returns the MessageObject
        after modifying it.

        Variables:
            MessageObject                 ``object``
                is the message object that has to be modified
        """

        if self.LastSendCommand is None:
            # if there is nothing return the default.
            return MessageObject

        """
        if LastSendCommand == "/language":
            self.ChangeUserLanguage(self.Text)
            MessageObject.Text = self._("Language changed successfully.")
            MessageObject.ReplyKeyboardHide()
            self.ClearLastCommand()
        """
        
        if self.LastSendCommand.startswith("/admin"):
            # see that the admin commands are interpreted correctly
            MessageObject = self.InterpretAdminCommands(MessageObject)
        
        
        return MessageObject

    def InterpretGroupCommand(self, MessageObject):
        """
        This command will interpret all the group send commands.

        Variables:
            MessageObject                 ``object``
                is the message object that has to be modified
        """
        

        if self.Text == "/help":
            MessageObject.Text = self._(
                "Work in progress! @AnimeSubBot is a bot"
            )
        
        return MessageObject

    def InterpretAdminCommands(self, MessageObject):
        """
        This command will interpret all the admin send commands.

        Variables:
            MessageObject                 ``object``
                is the message object that has to be modified
                
        Commands:
            Channel
            - add channel
            - change description
            - send description
            - delete channel
            
            Anime list
            - publish list
            - add anime 
            - configure anime
            - remove Anime 
        """
        if self.Text != "/admin":
            if self.LastSendCommand == "/admin":
                # the default screen
                if self.Text.startswith(self._("anime")):
                    MessageObject.Text = self._("What do you want to do?")
                    MessageObject.ReplyKeyboardMarkup(
                        [
                            [self._("publish list")],
                            [self._("add anime")],
                            [self._("configure anime")],
                            [self._("remove anime")],                        
                            [self._("back")],
                        ],
                        OneTimeKeyboard=True
                    )
                    self.SetLastSendCommand("/admin anime", None)
                        
                elif self.Text.startswith(self._("channel")):
                    MessageObject.Text = self._("What do you want to do?")
                    MessageObject.ReplyKeyboardMarkup(
                        [
                            [self._("add channel")],
                            [self._("change description")],
                            [self._("send description")],
                            [self._("delete channel")],
                            [self._("back")],
                        ],
                        OneTimeKeyboard=True
                    )
                    self.SetLastSendCommand("/admin channel", None)
                elif self.Text == self._("back"):
                    self.Text = "/start"

                    MessageObject = self.InterpretUserCommand(MessageObject)
                    
            elif self.LastSendCommand.startswith("/admin anime"):
                # the anime commands
                if self.Text == "publish list":
                    # 1) publish to channel
                    pass
                elif self.Text == "add anime":
                    # Please enter the url and be patient while the program extracts the information. To cancel please write CANCEL. -- ;:; -> delimeter
                    # 1) automatic (a) vs manual entry (b)
                    # 2a) extract URL =?> CANCEL -> to admin
                    # 3a) confirm Yes -> save data / No -> to admin
                    # 4a) add telegram url
                    # 2b) enter name
                    # 3b) enter publish date
                    # 4b) enter myanimelist.net url
                    # 5b) enter telegram url
                    pass
                elif self.Text == "configure anime":
                    # 1) search by name
                    # 2) show possible names (repeats until correct)
                    # 3) change by data => Telegram URL; Date; Name;
                    pass
                elif self.Text == "remove anime":
                    # 1) search by name
                    # 2) show possible names (repeats until correct)
                    # 3) check if user is sure and then delete anime
                    pass
                elif self.Text == "back":
                    self.Text = "/admin"
                    self.ClearLastCommand()
                    self.InterpretUserCommand(MessageObject)
                    
            elif self.LastSendCommand.startswith("/admin channel"):
                # the channel commands
                ChannelObject = Channel(self.SqlObject, self.SqlCursor)
                if self.LastSendCommand.startswith("/admin channel"):
                    if self.Text == "add channel" or self.LastSendCommand.startswith("/admin channel"):
                        # add new channel
                        # 1) Please enter the name of the channel - enter CANSEL to exit
                        # 1a) back to admin hub
                        # 2) check if channel exists - save (a) or error (b)
                        # 2a) save channel name
                        # 2b) back to admin channnel
                        # 3a) enter description 
                        # 3b) chancel => return to admin hub
                        # 3ab) is the text ok Yes / No
                        # 4a) enter buttons to use with description YES / NO
                        # 4b) chancel => return to admin hub
                        # 5a) success
                        if self.Text == "add channel":
                            MessageObject.Text = self._("Please send the name of the channel in this form @example_channel or send /done")
                            self.SetLastSendCommand("/admin channel add", None)
                        if self.LastSendCommand.startswith("/admin channel add"):
                            if self.LastSendCommand == "/admin channel add":
                                # 2) check if channel exists - save (a) or error (b)
                                if self.Text.startswith("@"):
                                    # enter the channel name into the database if the channel doesnt't exists yet
                                    if ChannelObject.ChannelExists(self.Text) is True:
                                        # 2b) back to admin channnel
                                        MessageObject.Text = self._("The channel already exists.\nTo change the description choose \"change description\" in the options.")
                                        self.SetLastSendCommand("/admin channel")
                                    else:
                                        # 3a) enter description 
                                        ChannelObject.AddChannel(self.Text, ByUser = self.InternalUserId)
                                        MessageObject.Text = self._("Please enter the channel description, to chancel send CANCEL")
                                        self.SetLastSendCommand("/admin channel add channel description", LastUsedData = self.Text)

                            elif self.LastSendCommand == "/admin channel add description":
                                if self.Text != "CANCEL":
                                    
                                    
                                                
                                    MessageObject.Text = self._("Is the description to your liking?")
                                    MessageObject.ReplyKeyboardMarkup([
                                        [self._("YES")],
                                        [self._("NO")]
                                    ],
                                        OneTimeKeyboard=True
                                    )
                                # 4a) enter buttons to use with description
                                if self.Text != "CANCEL":
                                
                                    MessageObject.Text = self._("Do you wish to add buttons?")
                                    MessageObject.ReplyKeyboardMarkup([
                                        [self._("YES")],
                                        [self._("NO")]
                                    ],
                                        OneTimeKeyboard=True
                                    )
                                    # saving the description without buttons
                                    ChannelObject.ChangeDescription(self.LastSendData, self.Text, ByUser = self.InternalUserId)
                                    # saving the description without buttons                            
                                    self.SetLastSendCommand("/admin channel add description buttons unsure", LastUsedData = self.LastSendData) 
                                else:
                                    MessageObj.Text = self._("To change the description choose \"change description\" in the options.")
                                    self.SetLastSendCommand("/admin channel")
                            elif self.LastSendCommand == "/admin channel add description buttons unsure":
                                if self.Text == self._("YES"):
                                    # 4a) enter buttons to use with description YES
                                    MessageObject.Text = self._("Please send the buttons like this:\nText;Url\nText;Url")
                                    self.SetLastSendCommand("/admin channel add description buttons sure", LastUsedData = self.LastSendData) 
                                else:
                                    # 4b) no => return to admin hub
                                    self.SetLastSendCommand("/admin channel")
                            elif self.LastSendCommand == "/admin channel add description buttons sure":
                                ChannelObject.ChangeDescriptionButton(self.LastSendData, self.Text, self.InternalUserId)
                                Description, Buttons = ChannelObject.GetDescription()

                                MessageObject.Text = Description
                                if Buttons is not None:
                                    for Line in Buttons.split("\n"):
                                        Text, Url = Line.split(";")
                                        MessageObject.AddInlineButton(Text, Url)
                                
                                self._SendToQueue_(MessageObject)

                                

                    elif self.Text == "change description":
                        pass
                    elif self.Text == "send description":
                        MessageObject.Text = Description
                        if Buttons is not None:
                            for Line in Buttons.split("\n"):
                                Text, Url = Line.split(";")
                                MessageObject.AddInlineButton(Text, Url)

                    elif self.Text == "delete channel":
                        pass
                    elif self.Text == "back":
                        self.Text = "/admin"
                        self.ClearLastCommand()
                        self.InterpretUserCommand(MessageObject)

        else:               
            MessageObject.Text = self._("How can I help you?")
            MessageObject.ReplyKeyboardMarkup(
                [
                    [self._("anime")],
                    [self._("channel")],
                    [self._("back")],
                ],
                OneTimeKeyboard=True
            )
            self.SetLastSendCommand("/admin", None)
        return MessageObject

class Channel(object):
    
    def __init__(self,
                 SqlObject,
                 Cursor):
        self.SqlObject = SqlObject 
        self.Cursor = Cursor
    
    def AddChannel(self, Name, Description = None, ByUser = None):
        """
        This methode will insert the channel into the database.

        Variables:
            - Name                   ``string``
                the true name of the channnel, this will be used as autifications methode.
            - Desciption             ``string``
                the channnel description   
            - ByUser                 ``integer``
                the user by which the channel was created by
        """
        Data = {"True_Name": Name}

        if Description is not None:
            Data["Description"] =  Description

        if ByUser is not None:
            Data["By_User"] = ByUser
            Data["Last_Changes"] = ByUser

        self.SqlObject.InsertEntry(self.Cursor,
                                   "Channel_Table",
                                    Data,
                                   )
        self.SqlObject.Commit()
    
    def ChangeDescription(self, Name, Description, ByUser = None):
        """
        This methode will change the description of the channel.

        Variables:
            - Name                   ``string``
                the true name of the channnel, this will be used as autifications methode.
            - Desciption             ``string``
                the channnel description   
            - ByUser                 ``string``
                the user that changed the value 
        """
        Data = {"Description": Description}
        if ByUser is not None:
            Data["Last_Changes"] = ByUser
        
        Where = [
            [
                 "True_Name", 
                 "=", 
                 Name,
                ],
            ]

        self.SqlObject.UpdateEntry(self.Cursor,
                                  "Channel_Table",
                                  Data,
                                  Where
                                  )
        self.SqlObject.Commit()
    
    def ChangeDescriptionButton(self, Name, Buttons, ByUser = None):
        """
        This methode will change the description buttons of the channel.

        Variables:
            - Name                   ``string``
                the true name of the channnel, this will be used as autifications methode.
            - Desciption             ``string``
                the channnel description   
            - ByUser                 ``string``
                the user that changed the value   
        """
        Data = {"Description_Buttons": Buttons}

        if ByUser is not None:
            Data["Last_Changes"] = ByUser
        
        Where = [
            [
                 "True_Name", 
                 "=", 
                 Name,
                ],
            ]

        self.SqlObject.UpdateEntry(self.Cursor,
                                  "Channel_Table",
                                  Data,
                                  Where
                                  )
        self.SqlObject.Commit()

    def ChannelExists(self, Name):
        """
        This method will detect if the use already exists or not.
        
        The following query will return 1 if a user with the specified 
        username exists a 0 otherwise.
        
        .. code-block:: sql\n
            SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'username')
        
        It will return a True if the database returns a 1 and a False
        if the database a 0.
        Variables:
            \-
        """

        exists = self.SqlObject.ExecuteTrueQuery(
            self.SqlObject.CreateCursor(Dictionary=False),
            Query=("SELECT EXISTS(SELECT 1 FROM Channel_Table WHERE"
                   " True_Name = %s);"
                   ),
            Data=Name
        )[0][0]
        if exists == 0:
            return False
        else:
            return True

    def GetChannels(self):
        """
        this method will get all the channels 
        """
        Channels = None
        Columns = ("True_Name",)
        ChannelsTemp = self.SqlObject.Select(
                    Cursor = self.Cursor,
                    FromTable = "Channel_Table",
                    Columns = Columns,)
        return Channels
    
    def GetDescription(self, Name):
        pass
    
class Anime(object):
    
    def __init__(self,
                 SqlObject,
                 Cursor):
        self.SqlObject = SqlObject 
        self.Cursor = Cursor
    

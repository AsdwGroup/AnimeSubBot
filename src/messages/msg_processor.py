#!/usr/bin/python
# -*- coding: utf-8 -*-

# standard lib
import re
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

        # Predefining attributes so that it later can be used for evil.
        self.LoggingObject = None
        self.ConfigurationObject = None

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
        else:
            # Get the Internal user id
            self.InternalUserId = self.GetInternalUserId()

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
        self.InternalUserId = self.GetInternalUserId()
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

    def GetInternalUserId(self):
        """
        This method will get the internal user id from the database.
        
        This method will return the internal user id directly.
        
        Variables:
            \-
        """
        # first the internal user id
        FromTable = "User_Table"
        Columns = ["Internal_Id"]
        Where = [["External_Id", "=", "%s"]]
        Data = (self.UserId,)

        return self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable=FromTable,
            Columns=Columns,
            Where=Where,
            Data=Data
        )[0]["Internal_Id"]
    
    @staticmethod
    def Chunker(ListOfObjects, SizeOfChunks):
        """
        Yield successive n-sized (SizeOfChunks) chunks from the list (ListOfObjects).
        
        This methode will not return anything, but act as a generator object.
        
        Variables:
            ListOfObjects               ``generator, list or string``
                This variable holds all the stuff to split.
            
            SizeOfChunks                ``integer``
                Holds the size of the chunks to turn the ListOfObjects 
                into.
                
        """
        for i in range(0, len(ListOfObjects), SizeOfChunks):
            yield ListOfObjects[i:i+SizeOfChunks]
            
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

    def SetLastSendCommand(self, Command, LastUsedId=None):
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
        if LastUsedId != None:
            Columns["Last_Used_Id"] = LastUsedId
            Duplicate["Last_Used_Id"] = LastUsedId

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
        """

        FromTable = "Session_Table"
        Columns = ["Command", "Last_Used_Id"]
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
            return LastSendCommand[0]

        return None

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
    
    def SaveMessages(self, Input, Output):
        """
        This method saves the message into the database 
        
        Variables:
            Input                         ``list``
                input messages
            
            Output                        ``list``
                output messages
        """
        
        if not isinstance(Input, list):
            Input = [Input]
        
        if not isinstance(Output, list):
            Output = [Output]
            
        for Element in Input:
            Columns = {
                       "By_User": self.UserId,
                       "Message": Element
                       }
            self.SqlObject.InsertEntry(
                    Cursor = self.SqlCursor,
                    TableName = "Input_Messages_Table",
                    Columns=Columns,
                   )
        
        for Element in Output:
            Columns = {
                       "By_User": self.UserId,
                       "Message": Element
                       }
            self.SqlObject.InsertEntry(
                    Cursor = self.SqlCursor,
                    TableName = "Output_Messages_Table",
                    Columns=Columns,
                   )
        
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

        MessageObject = message.MessageToBeSend(ToChatId=self.ChatId)
        MessageObject.Text = self._("Sorry, but this command could not be"
                                    " interpreted.")
        # check if message is a command

        if self.Text is not None:
            # Analyse the text and do your stuff.
            
            # delete the annoying bot command from the text to analyse
            # If the name of the bot is used in the
            # command delete the @NameOfBot
            self.Text = re.sub(r"^(@\w+[bB]ot\s+)?", "", self.Text)

            if self.InGroup is False:
                if self.Text.startswith("/"):
                    MessageObject = self.InterpretUserCommand(MessageObject)
                else:
                    MessageObject = self.InterpretUserNonCommand(MessageObject)
            else:
                if self.Text.startswith("/"):
                    MessageObject = self.InterpretGroupCommand(MessageObject)
                else:
                    MessageObject = self.InterpretGroupNonCommand(
                        MessageObject
                    )
        else:
            MessageObject = None
            
        # checking that the leght of the message never will be longer then 
        # 4096 characters long
                
        MessageObjectList = []
        
        if  MessageObject is not None:
            if len(MessageObject.Text) > 4095:
                TemporaryObjectHolder = MessageObject
                for TextPart in MessageProcessor.Chunker(MessageObject.Text, 4095):
                    TemporaryObjectHolder.Text = TextPart
                    MessageObjectList.append(TemporaryObjectHolder)
            else:
                MessageObjectList.append(MessageObject)
        return MessageObjectList

    def InterpretUserCommand(self, MessageObject):
        """
        This method interprets the commands form the user text.

        This method is used as an interpreter of the user send
        commands. It returns the MessageObject
        after analysing and modifying the MessageObject to respond
        the user Text.

        Variables:
            MessageObject                 ``object``
                is the message object that has to be modified
        """
        # register the command in the database for later use
        if self.Text.startswith("/start"):
            Parts = self.Text.split(" ")
            if len(Parts) <= 1:
                MessageObject.Text = self._("Welcome.\nWhat can I do for you?"
                                            "\nPress /help for all my commands"
                                            )
        elif self.Text == "/list":
            pass
        elif self.Text == "/done":
            LastSendCommand = self.GetLastSendCommand()
            LastUsedId = LastSendCommand["Last_Used_Id"]
            LastCommand = LastSendCommand["Command"]
            
        elif self.Text == "/help":
            MessageObject.Text = self._(
                "Work in progress! @AnimeSubBot is a bot."
            )
        
        elif self.Text == "/settings":
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
        else:
            # send that the command is unknown
            pass

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

        # Get the last send command and the last used id
        LastSendCommand = self.GetLastSendCommand()
        LastUsedId = LastSendCommand["Last_Used_Id"]
        LastCommand = LastSendCommand["Command"]

        if LastCommand is None:
            # if there is nothing return de default.
            return MessageObject

        if LastCommand == "/language":
            self.ChangeUserLanguage(self.Text)
            MessageObject.Text = self._("Language changed successfully.")
            MessageObject.ReplyKeyboardHide()
            self.ClearLastCommand()


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
        """
        raise NotImplementedError
        
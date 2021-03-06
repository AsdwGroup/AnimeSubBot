#!/usr/bin/python
# -*- coding: utf-8 -*-

import json


class MessageToBeSend(object):
    """
    A class to create and configure the message to be send.
    
    From the bot api under keyboard:
    One of the coolest things about our Bot API are the new 
    custom keyboards. Whenever your bot sends a message, it can pass 
    along a special keyboard with predefined reply options 
    (see ReplyKeyboardMarkup). Telegram apps that receive the message
    will display your keyboard to the user. Tapping any of the buttons
    will immediately send the respective command. This way you can 
    drastically simplify user interaction with your bot.

    We currently support text and emoji for your buttons. Here are some 
    custom keyboard examples:
        https://core.telegram.org/bots#keyboards
    The markup is build on the telegram bot api.
    See here for the main bot api:
        https://core.telegram.org/bots/api
    """
    
    def __init__(
                 self, 
                 ToChatId,
                 Text = None,
                 ParseMode = None,
                 DisableWebPagePreview=False,
                 DisableNotification = False,
                 ReplyToMessageId=None,
                 ):
        """
        The init of the class.
        
        The Api defines the following parameters:
           +----------------------------+-----------+------------+ 
           | Parameters                 |   Type    |  Required  |
           +============================+===========+============+ 
           |**chat_id**                 |Integer or |Yes         |  
           |  Unique identifier for     |String     |            |  
           |  the message recipient     |           |            | 
           |  (User or GroupChat id)    |           |            |
           +----------------------------+-----------+------------+     
           |**text**                    |String     |Yes         |      
           |  Text of the message       |           |            |
           |  to be sent                |           |            |
           +----------------------------+-----------+------------+
           |**parse_mode**              |String     |Optional    |
           |Send Markdown or HTML, if   |           |            |
           |you want Telegram apps to   |           |            |
           |show bold, italic,          |           |            |
           |fixed-width text or inline  |           |            |
           |URLs in your bot's message. |           |            |
           +----------------------------+-----------+------------+ 
           |**disable_web_page_preview**|Boolean    |Optional    |     
           |  Disables link previews    |           |            |
           |  for links in this message |           |            |
           +----------------------------+-----------+------------+ 
           |**disable_notification**    |Boolean    |Optional    |
           |Sends the message silently. |           |            |
           |iOS users will not receive a|           |            |
           |notification, Android users |           |            |
           |will receive a notification |           |            |
           |with no sound. Other apps   |           |            |
           |coming soon.                |           |            |
           +----------------------------+-----------+------------+        
           |**reply_to_message_id**     |integer    |Optional    |     
           |  if the message is a       |           |            |  
           |  reply, ID of the          |           |            |
           |  original message          |           |            | 
           +----------------------------+-----------+------------+     
           |**reply_markup**            |string     |Optional    |
           |**ReplyKeyboardMarkup**     |           |            |
           |**or**                      |           |            |
           |**ReplyKeyboardHide**       |           |            |
           |**or**                      |           |            |  
           |**ForceReply**              |           |            |    
           |  Additional interface      |           |            |
           |  options. A JSON-serialized|           |            |
           |  object for a custom reply |           |            | 
           |  keyboard, instructions to |           |            |   
           |  hide keyboard or to force |           |            |
           |  a reply from the user.    |           |            |
           +----------------------------+-----------+------------+
       
        Variables:
            ToChatId              ``integer``
                contains the receiver of the message
            
            Text                  ``None or string``
                contains the text to be send to the api
            
            ParseMode             ``None or string``
                defines if the text shall be interpreted by Markdown or
                HTML
            DisableNotification   ``boolean``
                defines if a user shall be notificed by the message
                
            DisableWebPagePreview ``boolean``
                defines if a web page should be preloaded
            
            ReplyToMessageId      ``None or integer``
                if this is an id the message will a reply to the message
                id given
                read more:
                    https://telegram.org/blog/replies-mentions-hashtags      
                    
        """
        
        self.ToChatId = ToChatId
        self.Text = Text
        self.ParseMode = ParseMode
        self.DisableWebPagePreview = DisableWebPagePreview
        self.DisableNotification = DisableNotification
        self.ReplyToMessageId = ReplyToMessageId
        self.ReplyMarkup = {}
    
    def SetParserMode(self, Parser="HTML"):
        """
        Send Markdown or HTML, if you want Telegram apps to show bold, 
        italic, fixed-width text or inline URLs in your bot's message.
        
        .. code-block:: Markdown\n
            *bold text*
            _italic text_
            [text](URL)
            `inline fixed-width code`
            ```pre-formatted fixed-width code block```
            
        .. code-block:: HTML\n
            <b>bold</b>, <strong>bold</strong>
            <i>italic</i>, <em>italic</em>
            <a href="URL">inline URL</a>
            <code>inline fixed-width code</code>
            <pre>pre-formatted fixed-width code block</pre>
            
        Variables:
            Parser                       ``string``
                The parser type either html or markdown
        
        """
        if Parser in ("Markdown", "HTML"):
            self.ReplyMarkup["parse_mode"] = Parser
               
    def ReplyKeyboardMarkup(self, 
                            Keyboard,
                            ResizeKeyboard = False, 
                            OneTimeKeyboard = False, 
                            Selective = False
                            ):
        """
        A method to create a custom keyboard.
        
        This object represents a custom keyboard with reply options.
        
        Variables:
        Keyboard                          ``array (list or tuple)``
            This variable contains the keyboard layout to be send
            Example:\n
            .. code-block:: python\n
                list
                    [
                        [
                            "Yes"
                        ],
                        [
                            "No"
                        ]
                    ]
                tuple
                    (
                        (
                            "Yes", 
                            # Don't forget this comma or else the tuple
                            # will collapse
                        ),
                        (
                            "No",
                        )
                    )
        
        ResizeKeyboard                    ``boolean``
            From the api:
                Optional. Requests clients to resize the keyboard 
                vertically for optimal fit (e.g., make the keyboard 
                smaller if there are just two rows of buttons).
                Defaults to false, in which case the custom keyboard is 
                always of the same height as the app's standard 
                keyboard.
             
        OneTimeKeyboard                   ``boolean``
            From the api:
                Optional. Requests clients to hide the keyboard as 
                soon as it's been used. Defaults to false.
                
        Selective                         ``boolean``
            From the api:
                Optional. Use this parameter if you want to show the 
                keyboard to specific users only. Targets: 1) users that 
                are @mentioned in the text of the Message object; 2) if 
                the bot's message is a reply (has ``reply_to_message_id``), 
                sender of the original message.
    
                Example: A user requests to change the bot‘s language, 
                bot replies to the request with a keyboard to select 
                the new language. Other users in the group don’t see 
                the keyboard.
         
        """
        
        self.ReplyMarkup["keyboard"] = Keyboard
        if ResizeKeyboard:
            self.ReplyMarkup["resize_keyboard"] = True
        if OneTimeKeyboard:
            self.ReplyMarkup["one_time_keyboard"] = True
        if Selective and not "selective"  in self.ReplyMarkup:
            self.ReplyMarkup["selective"] = Selective

    def ReplyKeyboardHide(self, 
                          Selective=False
                          ):
        """
        A method to tell the api to hide the custom keyboard.
        
        From the api:
            Upon receiving a message with this object, Telegram clients
            will hide the current custom keyboard and display the 
            default letter-keyboard. By default, custom keyboards are 
            displayed until a new keyboard is sent by a bot. An 
            exception is made for one-time keyboards that are hidden 
            immediately after the user presses a button 
            (see ReplyKeyboardMarkup).
        
        Variables:          
            Selective                     ``boolean``
                Determines if the keyboard shall be hidden by a single
                user only.
        """
           
        self.ReplyMarkup["hide_keyboard"] = True
        
        if Selective and "selective" not in self.ReplyMarkup:
            self.ReplyMarkup["selective"] = Selective
            
    def ForceReply(self,
                   Selective=False
                   ):
        """
        This method will add the tag to that will force a reply.
        
        From the api:
            Upon receiving a message with this object, Telegram clients 
            will display a reply interface to the user (act as if the 
            user has selected the bot‘s message and tapped ’Reply'). 
            This can be extremely useful if you want to create 
            user-friendly step-by-step interfaces without having to 
            sacrifice privacy mode.
        
        Variables:          
            Selective                     ``boolean``
                Determines if the keyboard shall be hidden by a single
                user only.
        """

        
        self.ReplyMarkup["force_reply"] = True
        
        if Selective and "selective" not in self.ReplyMarkup:
            self.ReplyMarkup["selective"] = Selective
    
    """def InlineKeyboardButton(self, Text, Url = None,
                             callback_data = None, 
                             switch_inline_query = None, 
                             switch_inline_query_current_chat = None, 
                             callback_game = None):
        ""
        This method will add a inline keyboard button 

        From the api:
           This object represents one button of an inline keyboard. You
           must use exactly one of the optional fields.

           +--------------------------------+------------+----------------------------------------------+ 
           |Field	                        |Type	     |Description                                   |
           +================================+============+==============================================+ 
           |text	                        |String      |Label text on the button                      |
           +--------------------------------+------------+----------------------------------------------+
           |url	                            |String      |Optional. HTTP url to be opened when button is|
           |                                |            |pressed                                       |
           +--------------------------------+------------+----------------------------------------------+ 
           |callback_data                   |String      |Optional. Data to be sent in a callback query |
           |                                |            |to the bot when button is pressed, 1-64 bytes |
           +--------------------------------+------------+----------------------------------------------+ 
           |switch_inline_query	            |String      |Optional. If set, pressing the button will    |
           |                                |            |prompt the user to select one of their chats, |
           |                                |            |open that chat and insert the bot‘s username  |
           |                                |            |and the specified inline query in the input   |
           |                                |            |field. Can be empty, in which case just the   |
           |                                |            |bot’s username will be inserted.              |
           |                                |            |Note: This offers an easy way for users to    |
           |                                |            |start using your bot in inline mode when they |
           |                                |            |are currently in a private chat with it.      |
           |                                |            |Especially useful when combined with          |
           |                                |            |switch_pm… actions – in this case the user    |
           |                                |            |will be automatically returned to the chat    |
           |                                |            |they switched from, skipping the chat         |
           |                                |            |selection screen.                             |
           +--------------------------------+------------+----------------------------------------------+ 
           |switch_inline_query_current_chat|String	     |Optional. If set, pressing the button will    |
           |                                |            |insert the bot‘s username and the specified   |
           |                                |            |inline query in the current chat's input      |
           |                                |            |field. Can be empty, in which case only the   |
           |                                |            |bot’s username will be inserted.              |
           |                                |            |                                              |
           |                                |            |This offers a quick way for the user to open  |
           |                                |            |your bot in inline mode in the same chat –    |
           |                                |            |good for selecting something from multiple    |
           |                                |            |options.                                      |
           +--------------------------------+------------+----------------------------------------------+
           |callback_game	                |CallbackGame|Optional. Description of the game that        |
           |                                |            |will be launched when the user presses the    |
           |                                |            |button.                                       |
           |                                |            |                                              |
           |                                |            |NOTE: This type of button must always be      |
           |                                |            |the first button in the first row.            |
           +--------------------------------+------------+----------------------------------------------+

        Variables: (see above)
            - text 
            - url                              ``list``
            - callback_data                    ``list``
            - switch_inline_query              ``list``
            - switch_inline_query_current_chat ``list``
            - callback_game                    ``list``
        "" 

        List_Of_Buttons = []

        if url is not None:
            List_Of_Buttons.extend(urls)
        

        self.ReplyMarkup["inline_keyboard"]  = List_Of_Buttons
        pass     """
    

    def AddInlineButton(self, Text, ButtonType, ButtonData, ButtonLine = None):
        """
        This method will add a inline keyboard button to an array of buttons.

        From the api:
           This object represents one button of an inline keyboard. You
           must use exactly one of the optional fields.

           +--------------------------------+------------+----------------------------------------------+ 
           |Field	                        |Type	     |Description                                   |
           +================================+============+==============================================+ 
           |text	                        |String      |Label text on the button                      |
           +--------------------------------+------------+----------------------------------------------+
           |url	                            |String      |Optional. HTTP url to be opened when button is|
           |                                |            |pressed                                       |
           +--------------------------------+------------+----------------------------------------------+ 
           |callback_data                   |String      |Optional. Data to be sent in a callback query |
           |                                |            |to the bot when button is pressed, 1-64 bytes |
           +--------------------------------+------------+----------------------------------------------+ 
           |switch_inline_query	            |String      |Optional. If set, pressing the button will    |
           |                                |            |prompt the user to select one of their chats, |
           |                                |            |open that chat and insert the bot‘s username  |
           |                                |            |and the specified inline query in the input   |
           |                                |            |field. Can be empty, in which case just the   |
           |                                |            |bot’s username will be inserted.              |
           |                                |            |Note: This offers an easy way for users to    |
           |                                |            |start using your bot in inline mode when they |
           |                                |            |are currently in a private chat with it.      |
           |                                |            |Especially useful when combined with          |
           |                                |            |switch_pm… actions – in this case the user    |
           |                                |            |will be automatically returned to the chat    |
           |                                |            |they switched from, skipping the chat         |
           |                                |            |selection screen.                             |
           +--------------------------------+------------+----------------------------------------------+ 
           |switch_inline_query_current_chat|String	     |Optional. If set, pressing the button will    |
           |                                |            |insert the bot‘s username and the specified   |
           |                                |            |inline query in the current chat's input      |
           |                                |            |field. Can be empty, in which case only the   |
           |                                |            |bot’s username will be inserted.              |
           |                                |            |                                              |
           |                                |            |This offers a quick way for the user to open  |
           |                                |            |your bot in inline mode in the same chat –    |
           |                                |            |good for selecting something from multiple    |
           |                                |            |options.                                      |
           +--------------------------------+------------+----------------------------------------------+
           |callback_game	                |CallbackGame|Optional. Description of the game that        |
           |                                |            |will be launched when the user presses the    |
           |                                |            |button.                                       |
           |                                |            |                                              |
           |                                |            |NOTE: This type of button must always be      |
           |                                |            |the first button in the first row.            |
           +--------------------------------+------------+----------------------------------------------+

        Variables:
            - Text                             ``string``
            - ButtonType                       ``string``
            - ButtonData                       ``string`` 
            - ButtonLine                       ``integer`` 
                sets the line in that the button will rest in (startswith 1);
                a None type equals to automatic assigment

        available types:
            - url                              ``string``
            - callback_data                    ``string``
            - switch_inline_query              ``string``
            - switch_inline_query_current_chat ``string``
            - callback_game (not supported)    ``string``
        """
        
        if "inline_keyboard" not in self.ReplyKeyboardMarkup:
            self.ReplyMarkup["inline_keyboard"] = []
        
        if ButtonType not in ("url", "callback_data", "switch_inline_query", "switch_inline_query_current_chat", "callback_game"):
            raise NotImplementedError("The button type {bType} is not supported".format(bType = ButtonType))

        Data = {
            "text": Text,
            ButtonType: ButtonData
            }

        # get the lenght of the ReplyKeyboardMarkup["inline_keyboard"] array
        Lenght = len(self.ReplyKeyboardMarkup["inline_keyboard"])

        if ButtonLine is not None:
            # extend the array to fit the need
            if Lenght < ButtonLine:
                self.ReplyKeyboardMarkup["inline_keyboard"].extend([[] for y in range(ButtonLine - Lenght)])

            self.ReplyKeyboardMarkup["inline_keyboard"][ButtonLine].append(Data)
             
        else:
            self.ReplyKeyboardMarkup["inline_keyboard"].append([Data])
                 
    def GetMessage(self):
        """
        This method will assemble the final message.
        
        This method will return the final data that will be send to the
        telegram bot api.
        
        Variables:
            \-
        """
        DataToBeSend = { 
                        "chat_id": self.ToChatId,
                        }
                        
        if self.Text != None:
            DataToBeSend["text"] = bytes(self.Text.encode("utf-8"))
        
        if self.ParseMode is not None:
            DataToBeSend["parse_mode"] = self.ParseMode
        
        if self.DisableWebPagePreview is True:
            DataToBeSend["disable_web_page_preview"] = True
        
        if self.DisableNotification is True:
            DataToBeSend["disable_notification"] = True
        
        if self.ReplyToMessageId is not None:
            DataToBeSend["reply_to_message_id"] = self.ReplyToMessageId
            
        if self.ReplyMarkup != {}:
            DataToBeSend["reply_markup"] = json.JSONEncoder(
                separators=(',', ':')).encode(self.ReplyMarkup)
            
        return DataToBeSend
    
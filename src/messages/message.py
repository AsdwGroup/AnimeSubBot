#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
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
    
if __name__ == "__main__":
    raise NotImplementedError
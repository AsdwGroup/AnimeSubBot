#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module defines and configures the custom configuration parser.
As well as an securer version of the parser build
"""

import os
import re
import json
import pickle
import base64
import collections
import configparser
import Crypto.Cipher.AES
import Crypto.Hash.SHA256
import Crypto.Random

class ConfigurationParser(configparser.RawConfigParser):
    """
    This class is an extension of the configparser.RawConfigParser
    class set by the standard python library, it add an ability to 
    automatically read the configuration file on object creation as
    well as some default configuration.
    """

    def __init__(self,
                 FileName="config.ini",
                 **Configuration):
        """
        This init method extends the original one with multiple 
        variables.
        
        Variables:
            FileName                      ``string``
                contains the name of the configuration file
                
            Configuration                 ``directory``
                contains the option to reconfigure the default 
                super values.
        """

        # Custom configurable filename
        self.FileName = FileName
        self.ResetConfigurationFile = False
        self.Encoding = "utf-8"

        # variables needed for the configparser
        self.Default = None
        self.DictType = collections.OrderedDict
        self.AllowNoValue = False
        self.Delimiters = ("=", ":")
        self.CommentPrefixes = ("#", ";")
        self.InlineCommentPrefixes = None
        self.Strict = True
        self.EmtyLineInValues = True
        self.DefaultSelection = configparser.DEFAULTSECT
        self.Interpolation = configparser.ExtendedInterpolation()

        # the Configuration directory is to be filled with the
        # parameters of the configparser
        if 0 < len(Configuration):
            # for the own class
            if "reset_configuration" in Configuration:
                self.ResetConfigurationFile = (
                    Configuration["reset_configuration"]
                )

            # for the super class the configparser
            if "defaults" in Configuration:
                self.Default = Configuration["defaults"]
            if "dict_type" in Configuration:
                self.DictType = Configuration["dict_type"]
            if "allow_no_value" in Configuration:
                self.AllowNoValue = Configuration["allow_no_value"]
            if "delimiters" in Configuration:
                self.Delimiters = Configuration["delimiters"]
            if "comment_prefixes" in Configuration:
                self.CommentPrefixes = Configuration["comment_prefixes"]
            if "inline_comment_prefixes" in Configuration:
                self.InlineCommentPrefixes = (
                    Configuration["inline_comment_prefixes"]
                )
            if "strict" in Configuration:
                self.Strict = Configuration["strict"]
            if "empty_lines_in_values" in Configuration:
                self.EmtyLineInValues = Configuration["empty_lines_in_values"]
            if "default_section" in Configuration:
                self.DefaultSelection = Configuration["default_section"]
            if "interpolation" in Configuration:
                self.Interpolation = Configuration["interpolation"]

        # This method initializes the superclass with all the possible
        # parameters.
        super(ConfigurationParser, self).__init__(
            defaults=self.Default,
            dict_type=self.DictType,
            allow_no_value=self.AllowNoValue,
            delimiters=self.Delimiters,
            comment_prefixes=self.CommentPrefixes,
            inline_comment_prefixes=self.InlineCommentPrefixes,
            strict=self.Strict,
            empty_lines_in_values=self.EmtyLineInValues,
            default_section=self.DefaultSelection,
            interpolation=self.Interpolation
        )

        # This commands sets the parser sensitive to upper- and lowercase.
        self.optionxform = lambda option: option

        # check if configfile exists
        if os.path.isfile(self.FileName) is not True:
            self.WriteDefaultConfigurationFile()

        elif self.ResetConfigurationFile is True:
            self.WriteDefaultConfigurationFile()

        # Read the configuration from the init
        self.ReadConfigurationFile()

    def WriteDefaultConfigurationFile(self):
        """
        A method to write the default configuration to the .ini file.
        
        Variables:
            \-
        """

        # The Title of the file
        self["CONFIGURATION"] = collections.OrderedDict(())

        self["Telegram"] = collections.OrderedDict((
            # This is the value needed for the main loop it states how long we
            # need to wait
            # until to state a request the telegram server.
            # It's in milliseconds
            ("RequestTimer", 1000),
            ("DefaultLanguage", "en_US"),
            ("MaxWorker", 5),
            #("ApiToken", "")
        ))

        self["MySQLConnectionParameter"] = collections.OrderedDict(
            (
                ("ReconnectionTimer", 3000),
                ("DatabaseName", "AnimeSubBotDatabase"),
                ("DatabaseHost", "127.0.0.1"),
                ("DatabasePort", 3306),
                #("DatabaseUser", ""),
                #("DatabasePassword", "")
            )
        )

        self["Logging"] = collections.OrderedDict((
            ("LogToConsole", True),
            ("LoggingFileName", "log.txt"),
            ("LoggingFormat", "[%(asctime)s] - [%(levelname)s] - %(message)s"),
            ("DateFormat", "%d.%m.%Y %H:%M:%S")
        ))

        # Writes the default configuration in to the correct file
        with open(self.FileName, "w") as configfile:
            self.write(configfile)

    def ReadConfigurationFile(self):
        """
        This method will read the configuration form the self.file.
        
        This method will read the configuration file into the buffer
        of the object directory. 
        
        Variables:
            \-
        """

        self.read(self.FileName, )

class SecureConfigurationParser(configparser.ConfigParser):
    '''
    This class is build for the "securer" configuration file.
    '''

    def __init__(self, 
                 NameOfConfigurationFile = "Conf.pcl",
                 # this is a dummy key for testing
                 InternalKey = r"PuN?~kDr39s+FT'*YQ}-j}~]>ke#3VmE", 
                 **Configuration):
        """
        The __init__ method.
        
        Variables:
            NameOfConfigurationFile       ``string``
                contains the name of the configuration file
        """
        
        # variables needed for the encryption  
        self.InternalKey = InternalKey
        SHA256Enc = Crypto.Hash.SHA256.new()
        SHA256Enc.update(InternalKey.encode("utf-8"))
        self.HashKey = SHA256Enc.digest()
                                    
        self.NameOfConfigurationFile = NameOfConfigurationFile
        self.Padding = b"|"

        self.Mode = Crypto.Cipher.AES.MODE_CBC
        
        # variables needed for the configparser
        self.Default = None
        self.DictType = collections.OrderedDict
        self.AllowNoValue = False
        self.Delimiters = ("=", ":")
        self.CommentPrefixes = ("#", ";")
        self.InlineCommentPrefixes = None
        self.Strict = True
        self.EmtyLineInValues = True
        self.DefaultSelection = configparser.DEFAULTSECT
        self.Interpolation = configparser.ExtendedInterpolation()

        # the Configuration directory is to be filled with the
        # parameters of the configparser
        if 0 < len(Configuration):
            # for the own class
            if "reset_configuration" in Configuration:
                self.ResetConfigurationFile = (
                    Configuration["reset_configuration"]
                )

            # for the super class the configparser
            if "defaults" in Configuration:
                self.Default = Configuration["defaults"]
            if "dict_type" in Configuration:
                self.DictType = Configuration["dict_type"]
            if "allow_no_value" in Configuration:
                self.AllowNoValue = Configuration["allow_no_value"]
            if "delimiters" in Configuration:
                self.Delimiters = Configuration["delimiters"]
            if "comment_prefixes" in Configuration:
                self.CommentPrefixes = Configuration["comment_prefixes"]
            if "inline_comment_prefixes" in Configuration:
                self.InlineCommentPrefixes = (
                    Configuration["inline_comment_prefixes"]
                )
            if "strict" in Configuration:
                self.Strict = Configuration["strict"]
            if "empty_lines_in_values" in Configuration:
                self.EmtyLineInValues = Configuration["empty_lines_in_values"]
            if "default_section" in Configuration:
                self.DefaultSelection = Configuration["default_section"]
            if "interpolation" in Configuration:
                self.Interpolation = Configuration["interpolation"]

        # This method initializes the superclass with all the possible
        # parameters.
        super().__init__(
            defaults=self.Default,
            dict_type=self.DictType,
            allow_no_value=self.AllowNoValue,
            delimiters=self.Delimiters,
            comment_prefixes=self.CommentPrefixes,
            inline_comment_prefixes=self.InlineCommentPrefixes,
            strict=self.Strict,
            empty_lines_in_values=self.EmtyLineInValues,
            default_section=self.DefaultSelection,
            interpolation=self.Interpolation
        )

        # This commands sets the parser sensitive to upper- and lowercase.
        self.optionxform = lambda option: option  
    
    def GetNewIV(self):
        """
        This method will generate a random initialization vector (IV)
        that will be used for the encryption.
        """
        return Crypto.Random.get_random_bytes(16)
    
    def WriteConfigurationFile(self, 
                               TelegramToken, DatabaseUser, 
                               DatabasePassword):
        """
        
        """
        Configuration = {"TelegramToken": TelegramToken,
                         "DatabaseUser": DatabaseUser,
                         "DatabasePassword": DatabasePassword
                         }
        print(Configuration)
        Configuration = self.StringToBase64(json.dumps(Configuration))
        Components = self._Encode_(self.HashKey, Configuration)
        self.SaveToConfigFile(Components)
    
    def ReadConfigurationFile(self,):
        Components = self.GetFromConfigFile()
        Configuration = self._Decode_(self.HashKey, Components[0], Components[1])
        Text = self.Base64ToString(Configuration)
        self["Security"] = json.loads(Text)
        
    def StringToBase64(self, String, Encoding = "utf-8"):
        """
        Will encode a string to base64 configuration.
        """
        return base64.b64encode(String.encode(Encoding))
    
    def Base64ToString(self, String, Encoding="utf-8"):
        """
        Will decode a string from base64 configuration.
        """
        return base64.b64decode(String).decode("utf-8")
          
    def _Encode_(self, Key, String):
        """
        Will encode a string with the given key to AES confuguration.
        
        Variables:
            Key                           ``string``
                a string of lenght n*16 
            
            String                        ``string or bytes``
                a string to encode
        """
        if isinstance(String, str):
            String = String.encode("utf-8")
            
        if len(String) % 16 != 0:
            String = b"{}{}".format(String, 
                                   (16 - (len(String) % 16)) * b"|"
                                   )
        IV = self.GetNewIV()
        Encryptor = Crypto.Cipher.AES.new(self.HashKey, 
                                          self.Mode, IV=IV)
        
        return IV, Encryptor.encrypt(String)
    
    def _Decode_(self, Key, IV, Ciphertext):
        """
        Will decode a text encryped with the AES encryption.
        
        Variables:
            Key                           ``string``
                a string of lenght n*16
            
            Ciphertext                        ``string``
                a string to decode
        """
        Decryptor = Crypto.Cipher.AES.new(Key, self.Mode, IV=IV)
        Text = Decryptor.decrypt(Ciphertext)
        Text = re.sub(r"(\|*)$","", Text.decode("utf-8")).encode("utf-8")
        
        return Text
        
    def SaveToConfigFile(self, Object):
        with open(self.NameOfConfigurationFile, "wb") as File:
            pickle.dump(Object, File, protocol = pickle.HIGHEST_PROTOCOL)
    
    def GetFromConfigFile(self):
        temp = None
        with open(self.NameOfConfigurationFile, "rb") as File:
            temp = pickle.load(File,)
            
        return temp  
    
if __name__ == "__main__":
    print("Online")
    a = ConfigurationParser(reset_configuration=False)
    a.ReadConfigurationFile()
    #print(a["Telegram"]["DefaultLanguage"].split(","))

    a = SecureConfigurationParser(InternalKey = r"PuN?~kDr39s+FT'*YQ}-j}~]>ke#3VmE")
    a.WriteConfigurationFile(
                             r"219513013:AAFmVgd2PG_fblbWysfGKY-ZAy70tMBhNYY",
                             "MySql@DatabaseUser24",
                             "Em#NYcGb7+GGXSg4\'F_c:a]cw'qzZ5fQe@X9f"
                             )
    
    a.ReadConfigurationFile()
    #print(a["Security"]["TelegramToken"])
    print("Offline")

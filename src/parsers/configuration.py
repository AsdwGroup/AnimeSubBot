#!/usr/bin/env python3.4
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
import Cryptodome.Cipher.AES
import Cryptodome.Hash.SHA256
import Cryptodome.Random



class DefaultConfigurationParser(configparser.RawConfigParser):
    """
    This class is an extension of the configparser.RawConfigParser
    class set by the standard python library, it add an ability to 
    automatically read the configuration file on object creation as
    well as some default configuration.
    
    From the python documentation:
        This module provides the ConfigParser class which implements a 
        basic configuration language which provides a structure similar 
        to what’s found in Microsoft Windows INI files. You can use this
        to write Python programs which can be customized by end users 
        easily.
    
    Link to the documentation:
        https://docs.python.org/3/library/configparser.html
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
            
            **Configuration               ``diretory``
                contains all the options needed for the parent
                class
        """

        # Custom configurable filename
        self.FilePath= os.path.abspath("config")
        
        self.FileName = os.path.join(self.FilePath, FileName)
        self.ResetConfigurationFile = False
        self.Encoding = "utf-8"
        
        # default variables needed for the configparser
        self.Default = None
        self.DictType = collections.OrderedDict
        self.AllowNoValue = False
        self.Delimiters = ("=", ":",)
        self.CommentPrefixes = ("#", ";",)
        self.InlineCommentPrefixes = None
        self.Strict = True
        self.EmtyLineInValues = True
        self.DefaultSelection = configparser.DEFAULTSECT
        self.Interpolation = configparser.ExtendedInterpolation()
        
        # the Configuration directory is to be filled with the
        # parameters of the configparser
        if 0 < len(Configuration):
            # for the own class
            
            if "Configuration" in Configuration:
                Configuration = Configuration["Configuration"]
            
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

        
    def CheckIfExists(self):
        # check if configfile exists
        if os.path.isfile(self.FileName) is True:
            return True
        else:
            return False  
    
    def ReadConfigurationFile(self):
        raise NotImplementedError
    
    def WriteConfigurationFile(self):
        raise NotImplementedError
    
    def ReturnClean(self):
        """
        This method will return a clean version of the configuration 
        parser, so that the class is pickleable again.
        """
        config = configparser.RawConfigParser(
                                           defaults=self.Default,
            dict_type=self.DictType,
            allow_no_value=self.AllowNoValue,
            delimiters=self.Delimiters,
            comment_prefixes=self.CommentPrefixes,
            inline_comment_prefixes=self.InlineCommentPrefixes,
            strict=self.Strict,
            empty_lines_in_values=self.EmtyLineInValues,
            default_section=self.DefaultSelection,
            interpolation=self.Interpolation)
        
        dictionary = {}
        for section in self.sections():
            config.add_section(section)
            for option in self.options(section):
                config.set(section,option, self.get(section, option))
        
        return config
    
class ConfigurationParser(DefaultConfigurationParser):
    """
    This class is an extension of the configparser.RawConfigParser
    class set by the standard python library, it add an ability to 
    automatically read the configuration file on object creation as
    well as some default configuration.
    
    From the python documentation:
        This module provides the ConfigParser class which implements a 
        basic configuration language which provides a structure similar 
        to what’s found in Microsoft Windows INI files. You can use this
        to write Python programs which can be customized by end users 
        easily.
    
    Link to the documentation:
        https://docs.python.org/3/library/configparser.html
    """   
        
    def WriteConfigurationFile(self):
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
            ("DefaultLanguage", "en_US,"),
            ("MaxWorker", 5),
        ))

        self["MySQL"] = collections.OrderedDict((
            ("ReconnectionTimer", 3000),
            ("DatabaseName", ""), # AnimeSubBotDatabase
            ("DatabaseHost", "127.0.0.1"),
            ("DatabasePort", 3306),
            ))

        self["Logging"] = collections.OrderedDict((
            ("LogToConsole", True),
            ("LoggingFileName", "log.txt"),
            ("MaxLogs", 20),
            ("LoggingFormat", "[%(asctime)s] - [%(levelname)s] - %(message)s"),
            ("DateFormat", "%d.%m.%Y %H:%M:%S")
        ))
        
        if not os.path.isdir(self.FilePath):
            os.mkdir(self.FilePath)

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

    def AddSecureConfigurationParser(self, ParserObject):
        """
        This method is needed to combine the sections of the 
        SecureConfigurationParser with the ones of the 
        ConfigurationParser class.
        
        Variables:
            ParserObject                  ``object``
                The parser that will be combined.
        """
        for Section in ParserObject.sections():
            self.add_section(Section)
            for Configuration in ParserObject[Section]:
                self.set(Section, 
                        Configuration,
                        ParserObject[Section][Configuration]
                        )

class SecureConfigurationParser(DefaultConfigurationParser):
    """
    This class is an extension of the custom DefaultConfigurationParser
    class it adds an AES-type encryption to the configuration for a bit 
    more security. It forces the .psi extention that stands for 
    pickled secured ini.
    """
                  
    def __init__(self, 
                 InternalKey,
                 FileName = "config.psi",
                 **Configuration):
        """
        The __init__ method.
        
        Variables:

                
            InternalKey                   ``string``
                contains the internal password needed to en- and decrypt
                the configuration file.
            
            FileName                      ``string``
                contains the name of the configuration file
                
            Configuration                 ``directory``
                contains the option to reconfigure the default 
                super values.
        """
        self.HashKey = SecureConfigurationParser.HashString(InternalKey)
        self.BlockSize = Cryptodome.Cipher.AES.block_size
        self.Padding = "|"
        self.Mode = Cryptodome.Cipher.AES.MODE_CBC
        # force the .psi extention
        self.FileName = FileName
        FileInfo = os.path.splitext(FileName)
        if FileInfo[1] != ".psi":
            self.FileName = "{}{}".format(FileInfo[0], ".psi")

        super().__init__(FileName = FileName,
                         Configuration = Configuration
                         )              
    
    def GetNewIV(self):
        """
        This method will generate a random initialization vector (IV)
        that will be used for the encryption.
        
        Variables:
            \-
        """
        return Cryptodome.Random.new().read(self.BlockSize)
        
    def WriteConfigurationFile(self, 
                               TelegramToken, DatabaseUser, 
                               DatabasePassword):
        """
        This method is a override of the parent method.
        
        It enables the writting of the encrypted configuration file.
        
        Variables:
            TelegramToken                 ``string``
                This is the TelegramToken that should be secured.
            
            DatabaseUser                  ``string``
                This is the DatabaseUser that should be secured.
                
            DatabasePassword              ``string``
                This is the DatabaseUser that should be secured.
        """
        if not os.path.isdir(self.FilePath):
            os.mkdir(self.FilePath)
            
        Configuration = {"TelegramToken": TelegramToken,
                            "DatabaseUser": DatabaseUser,
                            "DatabasePassword": DatabasePassword
                        } 
            
        self["Security"] = Configuration

        jsonDump = json.dumps({"Security": Configuration})
        Configuration = self.StringToBase64(jsonDump)
        Components = self._Encrypt_(self.HashKey, Configuration)
        self._SaveToConfigFile_(Components)
    
    def ReadConfigurationFile(self,):
        """
        This method is a override of the parent method.
        
        It enables reading the secure configuration file.
        
        Variables:
            \-
        """
        if self.CheckIfExists() is True:
            Components = self._GetFromConfigFile_()
            Configuration = self._Decrypt_(self.HashKey, 
                                           Components[0], 
                                           Components[1]
                                           )
            Text = self.Base64ToString(Configuration)
            Directory = json.loads(Text)
            for Entry in Directory.keys():
                self[Entry] = Directory[Entry]
            
            return True
        else:
            return False
    
    @staticmethod
    def HashString(String):
        # variables needed for the encryption  
        SHA256Enc = Cryptodome.Hash.SHA256.new()
        SHA256Enc.update(String.encode("utf-8"))
        return SHA256Enc.digest()
    
    @staticmethod    
    def StringToBase64(String, Encoding = "utf-8"):
        """
        Will encode a string to base64 configuration.
        
        
        """
        return base64.b64encode(String.encode(Encoding))
    
    @staticmethod
    def Base64ToString(String, Encoding="utf-8"):
        """
        Will decode a string from base64 configuration.
        """
        return base64.b64decode(String).decode("utf-8")
          
    def _Encrypt_(self, Key, String):
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
            String = String + ((16 - (len(String) % 16)) * self.Padding.encode("utf-8"))
        IV = self.GetNewIV()
        Encryptor = Cryptodome.Cipher.AES.new(self.HashKey, 
                                          self.Mode, IV=IV)
        
        return IV, Encryptor.encrypt(String)
    
    def _Decrypt_(self, Key, IV, Ciphertext):
        """
        Will decode a text encryped with the AES encryption.
        
        Variables:
            Key                           ``string``
                a string of lenght n*16
            
            Ciphertext                    ``string``
                a string to decode
        """
        Decryptor = Cryptodome.Cipher.AES.new(Key, self.Mode, IV=IV)
        Text = Decryptor.decrypt(Ciphertext)
        # This regex will search for all padding instances that have 
        # between 1-15 times at the end of the text.
        Text = re.sub(r"(\{Padding}{Limit})$".format(
                                            Padding = self.Padding,
                                            Limit = "{1,15}"
                                            ),
                      "", Text.decode("utf-8")
                      )

        return Text.encode("utf-8")
        
    def _SaveToConfigFile_(self, Object):
        """
        This method will save a pickled object to the file system.
        
        Variables:
            Object                        ``object``
                this should be a picklable object
        """
        with open(self.FileName, "wb") as File:
            pickle.dump(Object, 
                        File, 
                        protocol = pickle.DEFAULT_PROTOCOL
                        )
    
    def _GetFromConfigFile_(self):
        """
        This method will load the pickeled data from the configuration
        file.
        """
        with open(self.FileName, "rb") as File:
            temp = pickle.load(File,)
            
        return temp  
    


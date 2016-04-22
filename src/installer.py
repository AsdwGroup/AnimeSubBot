#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
import os
import sys
import getpass
import subprocess

import sql

class Installer(object):
    """
    This class will install the bot.
    """
    
    def __init__(self, 
                 Configuration,
                 SConfiguration,
                 Language, 
                 Logger,):
        self.Configuration = Configuration
        self.SConfiguration = SConfiguration
        self.Language = Language
        self.Logger = Logger       
        
    @staticmethod
    def OpenFileDefaultApp(FileName):
        '''
        Opens the File with the default set program. Depending on the operation system.
        @param FileName:    The file path to be opened.
        '''
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', FileName))
        elif os.name == 'nt':
            os.startfile(FileName)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', FileName)) 
    
    @staticmethod
    def ClearScreen():
        ClearScreen = input("clear the screen [y]/n")
        ClearScreen = ClearScreen.upper()
        
        if ClearScreen == "Y" or ClearScreen == "":
            if sys.platform.startswith('darwin'):
                os.system("clear")
            elif os.name == 'nt':
                os.system("cls")
    
    def _InstallDatabase_(self,):
        """
        This method will install the database 
        """
        _ = self.Language.CreateTranslationObject().gettext
        SqlInstaller = sql.SqlDatabaseInstaller(
            User = self.Configuration["Security"]["DatabaseUser"],
            Password = self.Configuration["Security"]["DatabasePassword"],
            DatabaseName =  self.Configuration["MySQL"]["DatabaseName"],
            Language = self.Language,
            Logging = self.Logger,
            Host = self.Configuration["MySQL"]["DatabaseHost"],
            Port = self.Configuration["MySQL"]["DatabasePort"],
            ReconnectTimer = float(self.Configuration["MySQL"]["ReconnectionTimer"]),
                                                )
        DB = False
        InstallDB = input("%s " % _("Do you wish to create the database? [n]/y"))
        if InstallDB.upper == "Y":
            DB = True
        SqlInstaller.Install(DB)
    
    def _InstallConfiguration_(self,):
        """
        This method will install the configuration file (if needed).
        
        Variables:
            
        """

        _ = self.Language.CreateTranslationObject().gettext
        RRun = True
        if os.path.isfile(self.Configuration.FileName) is True:

            RRun = False
            DoWork = input("%s " % _("Do you wish to override the existing "
                             "configuration file with the default settings"
                             " [n]/y:"))
            if DoWork.upper() == "Y":
                RRun = True
          
        if RRun is True:
            self.Configuration.WriteConfigurationFile()

            self.OpenFileDefaultApp(self.Configuration.FileName)
            self.Logger.info(_("The configuration file has been written, please"
                          " configure the values and then press enter")
                            )
            while True:
                Enter = input()
                if Enter == "":
                    break
    
    def _InstallSecureConfiguration_(self,):
        """
        This method will install and get the secure configuration data.
        """
        _ = self.Language.CreateTranslationObject().gettext
        TelegramToken = None
        DatabaseUser = None
        DatabasePassword = None
        
        if os.path.isfile(self.SConfiguration.FileName) is True:
            self.SConfiguration.ReadConfigurationFile()
            TelegramToken = self.SConfiguration["Security"]["TelegramToken"]
            DatabaseUser = self.SConfiguration["Security"]["DatabaseUser"]
            DatabasePassword = self.SConfiguration["Security"]["DatabasePassword"]
            
            SetTTocken = input("%s " % _("Do you wish to set the telegram token? [n]/y:"))
            if SetTTocken.upper() == "Y":
                TelegramToken = input("%s " % _("Please insert the telegram token:"))
                
            SetDUser = input("%s " % _("Do you wish to set the database username? [n]/y:"))
            if SetDUser.upper() == "Y":
                DatabaseUser = input("%s " % _("Please enter the database username:"))
            
            SetDPassword = input("%s " % _("Do you wish to set the database password? [n]/y:"))
            if SetDPassword.upper() == "Y":
                DatabasePassword = getpass.getpass("%s " % _("Please enter the database password:"))
            
        else:
            TelegramToken = input("%s " % _("Please insert the telegram token:"))
            DatabaseUser = input("%s " % _("Please enter the database username:"))
            DatabasePassword = getpass.getpass("%s " % _("Please enter the database password:"))
        
        self.ClearScreen()
        
        self.SConfiguration.WriteConfigurationFile(TelegramToken, 
                                                      DatabaseUser, 
                                                      DatabasePassword
                                                      )
        return True
    
    def Install(self, TypeOfInstallation=None):
        """
        This method will install either the database or the configurations
        to the system.
        
        Variables:
            TypeOfInstallation            ``string or None``
                sets the type of installation to do
        """
        _ = self.Language.CreateTranslationObject().gettext
        if TypeOfInstallation is None:
            TypeOfInstallation = input("%s " % _("Please input the type of "
                                         "installation or changes\npossible"
                                         " options:\nall a\t database d"
                                         "\tconfiguration c\tsecure"
                                         " configuration sc\tquit [q]")
                                   )
        TypeOfInstallation = TypeOfInstallation.upper()
        if TypeOfInstallation == "":
            TypeOfInstallation = "Q"
        
        if TypeOfInstallation == "Q":
            pass
        elif TypeOfInstallation == "D":
            self.Configuration.ReadConfigurationFile()
            self.SConfiguration.ReadConfigurationFile()
            self.Configuration.AddSecureConfigurationParser(self.SConfiguration)
            self._InstallDatabase_()

        elif TypeOfInstallation == "C":
            self._InstallConfiguration_()
            self.Configuration.ReadConfigurationFile()
            self.SConfiguration.ReadConfigurationFile()
            self.Configuration.AddSecureConfigurationParser(self.SConfiguration)
        elif TypeOfInstallation == "SC":
            self.Configuration.ReadConfigurationFile()
            self.InstallSecureConfiguration()
            self.SConfiguration.ReadConfigurationFile()
            self.Configuration.AddSecureConfigurationParser(self.SConfiguration)
        elif TypeOfInstallation == "A":
            #install all
            self._InstallConfiguration_()
            self.Configuration.ReadConfigurationFile()
            self._InstallSecureConfiguration_()
            self.SConfiguration.ReadConfigurationFile()
            self.Configuration.AddSecureConfigurationParser(self.SConfiguration)
            self._InstallDatabase_()
                    
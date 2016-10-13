#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

"""
The main.py this file is the entry to the programs execution.

This will initialise the main classes and hold (for now) the main loop this
will be changed as soon as multipossessing is implemented.
"""

# standard modules import 
import os
import sys
import time
import getpass
import platform
import multiprocessing
# if only windows is supported else use the curses module on linux (-.-)
try:
    import msvcrt
except ImportError:
    try:
        import curses
    except ImportError:
        raise


# personal imports
import sql
import installer
import gobjects
import language
import clogging
import parsers.commandline
import parsers.configuration
import worker

def RestartProgram():
    """
    Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function.
    """
    python = sys.executable
    os.execl(python, python, * sys.argv)

def Install(Configuration, 
            SConfiguration, 
            MasterLanguage, 
            MasterLogger):
    import installer
    Install = installer.Installer(
                                  Configuration = Configuration,
                                  SConfiguration = SConfiguration,
                                  Language = MasterLanguage, 
                                  Logging = MasterLogger,
                                  )
    Install.Install()

def TestSql(Configuration, MasterLogger, MasterLanguage):

    SqlObject = None

    NoConnection = True
    NrTry = 0
    while NrTry < 3:
        SqlObject = sql.Api(
            User = Configuration["Security"]["DatabaseUser"],
            Password = Configuration["Security"]["DatabasePassword"],
            DatabaseName = Configuration["MySQL"]["DatabaseName"],
            Host=Configuration["MySQL"]["DatabaseHost"],
            Port=Configuration["MySQL"]["DatabasePort"],
            ReconnectTimer=int(Configuration["MySQL"]
                               ["ReconnectionTimer"]),
            LoggingObject = MasterLogger,
            LanguageObject = MasterLanguage
        )
        if SqlObject.DatabaseConnection is None:
            NrTry += 1
        else:
            break
    
    SqlObject.CloseConnection()

    if NrTry == 3:
        return False
    else:
        return True

def Main():
    """
    The main function that let's the application roll.

    This function will initialise all the needed objects
    and see that there will be always something to do.
    """
    # this module is needed for the curses module for all unix distributions
    CursesMasterObject = None
    CursesObject = None
    # if program is run not on a windows system:
    if platform.system() != "Windows":
        # init the curses screen
        CursesMasterObject = curses.initscr()
        # Use cbreak to not require a return key press
        # The system will not be waiting so but continue to work.
        curses.cbreak()
        curses.noecho()
        CursesMasterObject.nodelay(1)
        maxy, maxx = CursesMasterObject.getmaxyx()
        begin_x = 0
        begin_y = 0
        height = maxy
        width = maxx
        CursesObject = curses.newwin(height, width, begin_y, begin_x)
        CursesObject.nodelay(1)
        curses.setsyx(-1, -1)
        CursesMasterObject.refresh()
        CursesObject.refresh()
        CursesObject.scrollok(True)
        CursesObject.idlok(True)
        CursesObject.leaveok(True)

    # This object in needed for the main process to interact with the
    # subprocess (the worker).
    # SecondQueue = multiprocessing.Queue(1)
    
    # This object is the event to shutdown all the subprocesses
    # it defaults to true and will be set to false in the end.
    ShutdownEventObject = multiprocessing.Event()

    try:
        # initialising the first logger and the language master object
        # this object will be recreated later on
        MasterLogger = clogging.Logger()
        MasterLanguage = language.Language()

        Language = MasterLanguage.CreateTranslationObject()

        _ = Language.gettext

        # Create the configuration class and read the configuration class.
        Configuration = parsers.configuration.ConfigurationParser()
        SConfiguration = parsers.configuration.SecureConfigurationParser(INTERNAL_KEY)
        # check if default files exist if not install them
        if ((Configuration.CheckIfExists() is False) or 
            (SConfiguration.CheckIfExists() is False)):
            
            import installer
            installer.Installer(Configuration,
                SConfiguration, 
                MasterLanguage, 
                MasterLogger).Install("A")
            
        else:
            Configuration.ReadConfigurationFile()         
            SConfiguration.ReadConfigurationFile()    
            Configuration.AddSecureConfigurationParser(SConfiguration)
        # deleting the object so that it will be garbage collected 
        del SConfiguration
        Configuration = Configuration.ReturnClean()
        
        # Create the language processor
        MasterLanguage = language.Language()
        Language = MasterLanguage.CreateTranslationObject(
            Configuration["Telegram"]["DefaultLanguage"].split(","))

        # This is the language object that will call the translation 
        # function.
        _ = Language.gettext

        # init parser

        Parser = parsers.commandline.CustomParser(ConfigurationObject=Configuration,
                                            LanguageObject=MasterLanguage
                                            )
        Parser.RunParser()
        ParserArguments = Parser.GetArguments()
        
        if ParserArguments.Installer is True:
            # checking the installation
            # reseting the configurations
            import installer
            Configuration = parsers.configuration.ConfigurationParser()
            SConfiguration = parsers.configuration.SecureConfigurationParser(INTERNAL_KEY)
            installer.Installer(Configuration, 
                    SConfiguration,
                    MasterLanguage,
                    MasterLogger).Install()
            # deleting the object so that it will be garbage collected 
            del SConfiguration
            Configuration = Configuration.ReturnClean()
        
        # Initialise the rest of the objects.
        # first the multiprocess logger 
        MasterLogger.CloseHandlers()

        MasterLogger = clogging.LoggingProcessSender(
            LogToConsole = ParserArguments.PrintToConsole,
            FileName = Configuration["Logging"]["LoggingFileName"],
            MaxLogs = Configuration["Logging"]["MaxLogs"],
            LoggingFormat = Configuration["Logging"]["LoggingFormat"],
            Dateformat = Configuration["Logging"]["DateFormat"],
            LoggingLevel = "debug",
            CursesObject = CursesObject,
            ShutdownEvent = ShutdownEventObject
        )

        MasterLogger.info(_("{AppName} has been started.").format(
            AppName=gobjects.__AppName__
        ))

        # test if there is a MySql connection
        if TestSql(Configuration, MasterLogger, MasterLanguage) is False:
            MasterLogger.critical(
                 _("{AppName} has been stopped, because you didn't "
                   "input the correct user name or password.").format(
                    AppName=gobjects.__AppName__)
                                  )
            time.sleep(0.5)
            raise  SystemExit
        
        # starting the Worker
        MainWorker = worker.MainWorker(
                 MaxWorker = Configuration["Telegram"]["MaxWorker"],
                 ShutDownEvent = ShutdownEventObject,
                 Configuration = Configuration,
                 Logging = MasterLogger,
                 Language = MasterLanguage,
                 BotName = None)
        
        MainWorker.start()
        
        # Initialise the main loop (it's a endless loop, it breaks when a
        # key is pressed.)
        MasterLogger.info(_("Exit loop by pressing <Esc>, <q> or <Space>"))
        MasterLogger.info(_("Getting updates from the telegram api."))
        # Add a comment number to the telegram request, so that the old
        # messages will be sorted out.

        while True:
            # check if a key is pressed by user and stop if pressed.
            # if windows use msvcrt
            if platform.system() == "Windows":
                if msvcrt.kbhit():
                    PressedKey = ord(msvcrt.getch())
                    if PressedKey == 27 or PressedKey == 113 or \
                                    PressedKey == 32:
                        MasterLogger.info(_("A user shutdown was requested "
                                            "will now shutdown."))
                        break
                
            # use curses
            else:
                PressedKey = CursesObject.getch()
                if (PressedKey == 27 or PressedKey == 113 or  
                        PressedKey == 32):
                    MasterLogger.info(_("A user shutdown was requested will "
                                        "now shutdown.")
                                      )
                    break
                else:
                    pass
        
            time.sleep(0.5)
            
        MasterLogger.info(_("The system is shutting down, please be patient"
                       " until all the workload has been cleared."))

    finally:
        ShutdownEventObject.set()
        try:
            MainWorker.join()   
        except UnboundLocalError:
            pass
        except:
            raise
        MasterLogger.join()
        
        if platform.system() != "Windows":
            # clean after the curses module
            time.sleep(1)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            # Raise the terror of the curses module for a second time.
            # (It's correctly formatted now)
            try:
                raise
            except RuntimeError:
                pass


if __name__ == "__main__":
    INTERNAL_KEY = r"2#<&Sd8!upX.jm(n"
    multiprocessing.freeze_support()
    Main()

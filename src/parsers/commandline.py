#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module defines and configures the custom build argumentParser.
"""

import argparse
import gobjects


class CustomParser(argparse.ArgumentParser):
    """
    This module it a preconfigured extended version of the argparser.
    
    From the documentation.
    The argparse module makes it easy to write user-friendly 
    command-line interfaces. The program defines what arguments it 
    requires, and argparse will figure out how to parse those out of 
    sys.argv. The argparse module also automatically generates help and 
    usage messages and issues errors when users give the program 
    invalid arguments.
    
    link to the documentation:
        https://docs.python.org/3.4/library/argparse.html
    """

    def __init__(self,
                 ConfigurationObject,
                 LanguageObject,):
        """
        This method is an init, never seen one before?
        
        Variables:

            ConfigurationObject           ``object``
                Contains the configuration for the program
                    
            LanguageObject                ``object``
                Contains the language object needed for automatic string
                translation.
        """


        self.Configuration = ConfigurationObject

        self.LanguageObject = LanguageObject.CreateTranslationObject()
        self._ = self.LanguageObject.gettext


        Description = self._(
            "A in python written telegram bot, called {ProgramName}."
        ).format(ProgramName = gobjects.__AppName__)

        Epilog = (
            self._(
                "Author:\t\t\t{Author}\nCredits:\t\t{Credits}\nVersion:"
                "\t\t{Version}\nRelease:\t\t{Release}\nLicense:\t\t"
                "{License}\nCopyright:\t\t{Copyright}"
            ).format(
                Author=gobjects.__author__,
                Credits=", ".join(gobjects.__credits__),
                Version=gobjects.__version__,
                Release=gobjects.__release__,
                License=gobjects.__license__,
                Copyright=gobjects.__copyright__)
        )

        super().__init__(
            prog=gobjects.__AppName__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=Description,
            epilog=Epilog
        )

    def RunParser(self):
        """
        This method add the parser arguments to the system.
        
        With the here defined parser arguments can the system 
        understand the ``sys.args`` values better.
        This method will set the command line arguments like this:\n


            usage: BetterPollBot [-h] [-v] [-c] [-f FILE] [-l LANGUAGE] 
                                 [-t TIME] [-at APITOKEN] 
                                 [-dn DATABASENAME] [-du DATABASEUSER]
                                 [-dp DATABASEPASSWORD] 
                                 [-dh DATABASEHOST]
                                 [-dhp DATABASEHOSTPORT]
            
            An in python written telegram bot, called BetterPollBot.
            
            optional arguments:\n
            +---------------------+------------------------------------+
            |  -h, --help         |show this help message and exit     |
            +---------------------+------------------------------------+ 
            |  -v, --version      |show program's version number and   |
            |                     |exit                                |
            +---------------------+------------------------------------+
            |  -c, --console      | Toggles the type of logging from   |
            |                     |the set settings in the config.ini. | 
            +---------------------+------------------------------------+
            |  -i,--installer     |toggels the installation process    |
            +---------------------+------------------------------------+         
            
        Variables:
            \-
        """
        # adding parser arguments to the system
        self.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " + str(gobjects.__version__)
        )

        self.add_argument(
            "-c",
            "--console",
            help=self._(
                "Toggles the type of logging from the set settings in the "
                "config.ini."
            ),
            action=(
                "store_false"
                if self.Configuration.getboolean("Logging", "LogToConsole")
                else "store_true"
            ),
            dest="PrintToConsole"
        )

        # A hidden option to install the Database
        self.add_argument(
            '-i',               
            '--installer',
            help=self._(
                "Toggles the installation process."
                        ),
            dest="Installer",
            action="store_true",
            default=False,
        )

    def GetArguments(self):
        """
        This method will return the parser arguments as a directory. 
        
        This method is an alias of ``Parser.parse_args()``.
        
        Variables:
            \-
        """
        return self.parse_args()

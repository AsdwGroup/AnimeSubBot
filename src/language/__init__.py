#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This file contains a class to create the translation object.

In this file the function _() or self._() will be initialised.
"""


import gettext
import multiprocessing


class Language(object):
    """
    The purpose of this class is to keep the CreateTranslationObject 
    function multiprocessing safe.
    """
    
    def __init__(self,
                 DefaultLanguages = ["en_US"],):
        """
        Variables:
            DefaultLanguages              ``list``
                the default languages of the bot.
        """

        self.RLock = multiprocessing.RLock() 
        self.DefaultLanguages = DefaultLanguages
        self.Localedir = "language"
        self.Domain = "Telegram"

        
    def CreateTranslationObject(self,
                                Languages = None,
                                ):
        """
        This function returns a gettext object.

        Variables:
            Languages            ``array of strings or None``
                contains the language string
        """
        LanguageObject = None
        
        # if Language has been given 
        if isinstance(Languages, str):
            Languages = [Languages]
        elif isinstance(Languages, list):
            pass
        elif Languages is None:
            Languages = self.DefaultLanguages
        else:
            raise TypeError

        with self.RLock:
            LanguageObject = gettext.translation(
                                    domain = self.Domain,
                                    localedir=self.Localedir,
                                    languages=Languages
                                )

        return LanguageObject

if __name__ == "__main__":
    i = Language()
    
    LanguageObject = i.CreateTranslationObject("en_US",Localedir="../language")
    _ = LanguageObject.gettext
    print(_("YES")=="JA")
    print(_("YES"), "JA")



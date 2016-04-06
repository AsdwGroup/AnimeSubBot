#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This file contains a function to create the translation object.

In this file the function _() or self._() will be initialised.
"""


import gettext
import multiprocessing

class Language(object):
    """
    The purpose of this class is to keep the CreateTranslationObject 
    function multiprocessing safe.
    """
    
    def __init__(self):
        """
        Variables:
            \-
        """
        self.RLock = multiprocessing.RLock() 

    def CreateTranslationObject(
                                Languages = ("de_DE", "en_US"),
                                Localedir="language",
                                ):
        """
        This function returns a gettext object.

        Variables:
            Languages            array of string
                contains the language string
            Localedir            string
                contains the Language location
        """
        if type(Languages) == type('str'):
            Languages = [Languages]
        
        with self.RLock:
            LanguageObject = gettext.translation("Telegram",
                                       localedir=Localedir,
                                       languages=Languages
                                       )

        return LanguageObject

if __name__ == "__main__":
    i = CreateTranslationObject("en_US",Localedir="../language")
    _ = i.gettext
    print(_("YES")=="JA")
    print(_("YES"), "JA")



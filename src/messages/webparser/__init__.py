#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
An data extractor modul build for the webpage http://myanimelist.net .
"""
import gzip
import zlib
import platform
import urllib.request

import bs4 
import gobjects

class Extractor(object):
    """
    This class will extract data from the webpage http://myanimelist.net
    """
    def __init__(self, url, logging_object, language_object):
        """
        This is the __init__ methode... Nothing more information needed.
        
        Variables:
            - url                    ``string``
                the url from which the data will be extracted from.
        """
        self.url = url
        self.logging_object = logging_object
        self.language_object = language_object
        self.webpage = ""
        self._get_webpage_()
        
        # the headers for the webrequest
        self._headers = {
            'User-agent': (("{AppName}/{Version}({Platform})"
                            "Python-urllib/{PythonBuild} from {Hosted}"
                            ).format(
                                AppName=gobjects.__AppName__,
                                Version=gobjects.__version__,
                                Platform=('; '.join(
                                                platform.system_alias(
                                                    platform.system(),
                                                    platform.release(),
                                                    platform.version()
                                                    )
                                                      )
                                            ),
                                PythonBuild=platform.python_build(),
                                Hosted=gobjects.__hosted__
                                )
                           ),
            "Content-Type":
                "application/x-www-form-urlencoded;charset=utf-8",
            "Accept-Encoding": "gzip,deflate"
        }
        
    def _get_webpage_(self):
        url_request = urllib.request.Request(self.url,
            headers=self._headers
        )
        try:
            with urllib.request.urlopen(
                                        url_request,
                                        context=self.SSLEncryption
                                        ) as web_source:
                # setting the compression rate of the system
                if self.Compressed is True:
                    request_encoding = web_source.info().get("Accept-Encoding")
                    if request_encoding == "gzip":
                        response = gzip.decompress(web_source.read())
                    elif request_encoding == "deflate":
                        decompressed = zlib.decompressobj(-zlib.MAX_WBITS)
                        response = decompressed.decompress(web_source.read())
                        response += decompressed.flush()
                    else:
                        response = web_source.read()
                else:
                    response = web_source.read()
                
                self.webpage = response.decode("utf-8", "replace")
            #return json.loads(response.decode("utf-8"))

        except urllib.error.HTTPError as Error:
            if Error.code == 400:
                self.logging_object.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )
                                    ) + " " + 
                    self._("The server cannot or will not process the request "
                           "due to something that is perceived to be a client "
                           "error (e.g., malformed request syntax, invalid "
                           "request message framing, or deceptive request "
                           "routing)."
                           ),
                )
            elif Error.code == 401:
                self.logging_object.critical(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " + 
                    self._("The ApiToken you are using has not been found in "
                           "the system. Try later or check the ApiToken for "
                           "spelling errors."),
                )
            elif Error.code == 403:
                self.logging_object.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error="{} {}".format(Error.code, Error.reason)
                                           ) + " " + 
                    self._("The address is forbidden to access, please try "
                           "later."),
                )
            elif Error.code == 404:
                self.logging_object.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=" {} {} ".format(Error.code, Error.reason)
                                           ) + 
                    self._("The requested resource was not found. This status "
                           "code can also be used to reject a request without "
                           "closer reason. Links, which refer to those error "
                           "pages, also referred to as dead links."),
                )
            elif Error.code == 429:
                self.logging_object.error(
                    self._("The web server returned the HTTPError \"{Error}\".") + 
                    "{} {}".format(Error.code, Error.reason) +
                    self._("My bot is hitting limits, how do I avoid this?\n"
                    "When sending messages inside a particular chat, "
                    "avoid sending more than one message per second. "
                    "We may allow short bursts that go over this limit,"
                    " but eventually you'll begin receiving 429 errors.\n"
                    "If you're sending bulk notifications to multiple"
                    " users, the API will not allow more than 30"
                    " messages per second or so. Consider spreading out"
                    " notifications over large intervals of 8—12 hours"
                    " for best results.\nAlso note that your bot will"
                    " not be able to send more than 20 messages per"
                    " minute to the same group."
                                           )
                                         )
            elif Error.code == 502:
                self.logging_object.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " + 
                    self._("The server could not fulfill its function as a "
                           "gateway or proxy, because it has itself obtained "
                           "an invalid response. Please try later."),
                )
            elif Error.code == 504:
                self.logging_object.error(
                    self._("The web server returned the HTTPError \"{Error}\"."
                           ).format(Error=(str(Error.code) + " " + Error.reason
                                           )) + " " + 
                    self._("The server could not fulfill its function as a "
                           "gateway or proxy, because it has not received a "
                           "reply from it's servers or services within a "
                           "specified period of time.")
                )
            raise
        except:
            raise
    
    def extract_data(self):
        """
        This methode will extract all the needed data. 
        The Data that will be extracted is: 
            - name of the anime 
            - the description 
            - and the date of aired 
            
        """
        name = None
        description = None
        aired = None # This is the date the anime has been premiered
        
        # get the webpage 
        source = urllib.request
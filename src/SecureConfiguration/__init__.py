#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
'''
Created on 07.04.2016

@author: Adrian
'''
import re
import pickle
import base64
import hashlib
from Crypto.Cipher import AES

class SecureConfiguration(object):
    '''
    classdocs
    '''


    def __init__(self, 
                 NameOfConfigurationFile = "Conf.pcl",):
        self.InternalKey = r"Kqfpj9NhVL9TDbvwBBzw6Njs"
        self.HashKey = hashlib.sha256(self.InternalKey.encode("utf-8")).digest()
        self.NameOfConfigurationFile = NameOfConfigurationFile
        self.Padding = "|".encode("utf-8")
        self.IV = 16 * '\x00'           # Initialization vector
        self.Mode = AES.MODE_CBC
    
    def StringToBase64(self, String):
        return base64.b64encode(String.encode("UTF-8", "replace"))
    
    def _Encode_(self, Key, String):
        if len(String) % 16 != 0:
            String = "{}{}".format(String, 
                                   (16 - (len(String.encode("utf-8", "replace")) % 16)) * "|"
                                   )
                                   
        String = String.encode("utf-8", "replace")
        Encryptor = AES.new(Key, self.Mode, IV=self.IV)
        return Encryptor.encrypt(String)
    
    def _Decode_(self, key, Ciphertext):
        Decryptor = AES.new(key, self.Mode, IV=self.IV)
        Text = Decryptor.decrypt(Ciphertext)
        Text = Text.decode("utf-8")
        Text = re.sub(r"(\|*)$","", Text)
        return Text
        
    def SaveToConfigFile(self, Object):
        with open(self.NameOfConfigurationFile, "wb") as File:
            pickle.dump(Object, File, protocol = pickle.HIGHEST_PROTOCOL)
    
    def GetFromConfigFile(self):
        temp = None
        with open(self.NameOfConfigurationFile, "rb") as File:
            temp = pickle.load(File,)
            
        return temp  
       
a = SecureConfiguration()
a.SaveToConfigFile(a._Encode_(a.InternalKey, "root"))

print(a._Decode_(a.InternalKey, a.GetFromConfigFile()))

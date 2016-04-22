from importlib.machinery import SourceFileLoader
import pickle
configuration = SourceFileLoader("configuration", "../src/parsers/configuration.py").load_module()


if __name__ == "__main__":
    print("Online")
    b = configuration.ConfigurationParser(reset_configuration=False)
    b.ReadConfigurationFile()
    print(b["Telegram"]["DefaultLanguage"].split(","))
    
    
    # this is a dummy key for testing
    a = configuration.SecureConfigurationParser(InternalKey = r"PuN?~kDr39s+FT'*YQ}-j}~]>ke#3VmE")
    a.WriteConfigurationFile(
                             r"TelegramKeasdfasdfsdfasdy",
                             "MySql@DatabaseUser24",
                             "Em#NYcGb7+GGXSg4\'F_c:a]cw'qzZ5fQe@X9f"
                             )
    
    a.ReadConfigurationFile()
    print(a["Security"]["TelegramToken"])
    b.AddSecureConfigurationParser(a)
    with open("FileName", "wb") as File:
        pickle.dump()
    del a
    print(a["Security"]["TelegramToken"])
    print(b["Security"]["DatabasePassword"])
    print("Offline")
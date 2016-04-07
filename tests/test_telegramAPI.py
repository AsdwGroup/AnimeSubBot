from importlib.machinery import SourceFileLoader

custom_logging = SourceFileLoader("telegram", "../src/telegram.py").load_module()

if __name__ == "__main__":
    print('online')
    import pprint

    OrgTok = "80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY"
    FalTok = "80578257:AAEt5aH64bD6P3hqumKYFJAyHTGWEgcyEY"
    a = TelegramApi(OrgTok,
                    500)

    Update = a.GetUpdates(469262639 + 1)
    print(Update)
    try:
        print(Update["result"][len(Update["result"]) - 1]["update_id"])

        MessageObject = messages.message.MessageToBeSend(
            Update["result"][len(Update["result"]) - 1]["message"]
            ["chat"]["id"], "1"
        )
        MessageObject.ReplyKeyboardMarkup(
                                          Keybord=[["Top Left",
                                                    "Top Right"],
                                                   ["Bottom Left",
                                                    "Bottom Right" ]
                                                   ],
                                          ResizeKeyboard=True,
                                          OneTimeKeyboard=True,
                                          Selective=False
                                          )
        # MessageObject.ForceReply()
        MessageObject.ReplyKeyboardHide(Selective=True)

        print(a.SendMessage(MessageObject))
    except:
        pass
#     if a:
#         pprint.PrettyPrinter(indent=4).pprint((a.GetMe()))
#         pprint.PrettyPrinter(indent=4).pprint((a.GetUpdates()))
#     else:
#         print("None")
    print('offline')
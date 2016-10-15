def SpacedChunker(String, SizeOfChunks):

        
    EndList = []
    TempList = []
    StringSize = 0
    TempString = ""
    for i in String.split(" "):
        print(i)
        StringSize += len(i)
        if StringSize < SizeOfChunks:
            print(TempString)
            TempString += i
        else:
            print(TempString)
            EndList.append(TempString)
            StringSize = 0
            TempString = ""
            StringSize += len(i)
            StringSize = 0
            TempString += i
        if String.split(" ")[-1]:
            EndList.append(" ".join(TempList))
    return EndList
print(SpacedChunker("Hier am I.", 6))

import pickle
import os
fileName = "afile.pickle"

a = [os.urandom(i) for i in range(100, 1000)]

with open(fileName, "wb") as File:
    pickle.dump(a, File)
    
with open(fileName, "rb") as File:
    print(pickle.load(File))
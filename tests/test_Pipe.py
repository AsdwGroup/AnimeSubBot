import multiprocessing
import multiprocessing.connection
import time

def SendShit(connection): 
    time.sleep(2)
    connection.send(["Gone?", 42])
    connection.close()
    



if __name__ == '__main__':
    print("online")
    multiprocessing.freeze_support()
    InputPipe, OutputPipe = multiprocessing.Pipe(False)

    p = multiprocessing.Process(target= SendShit, args = (OutputPipe,))
    p.start()
    print("print Wait")
    print(InputPipe.recv())
    InputPipe.close()
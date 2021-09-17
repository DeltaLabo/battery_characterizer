import concurrent.futures
import threading
import time

start = time.perf_counter()

def do_something(seconds): #Definiendo el argumento de seconds
    print(f'Sleeping {seconds} second(s)')
    time.sleep(seconds)
    return f'Done sleeping...{seconds}'

with concurrent.futures.ThreadPoolExecutor() as executor:
    secs = [5, 4, 3, 2, 1]
    #results = [executor.submit(do_something, sec) for sec in secs] #List comprehension (for sirve)
    
    #for f in concurrent.futures.as_completed(results):
    #    print(f.result())
    
    results = executor.map(do_something, secs)#map returns results in the order that were started
    for result in results:
        print(result)

def hello():
    print("hello, world")


t = threading.Timer(8.0, hello)
t.start() #after 30 seconds, the message will be printed     
print('Finished in {round(finish-start, 2)} second(s)')   
# print(f1.result()) #Imrpimiendo the return value
# print(f2.result()) #Imrpimiendo the return value

# threads = [] #lista vacía de threads

# for _ in range(10):
#     t = threading.Thread(target=do_something, args=[1.5])
#     t.start()
#     threads.append(t)
# for thread in threads:
#     thread.join()

finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2)} second(s)')

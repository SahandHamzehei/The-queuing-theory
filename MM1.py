#!/usr/bin/python3

import random
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt
import numpy as np
# ******************************************************************************
# Constants
# ******************************************************************************
LOAD = 0.85 #
SERVICE = 10.0 # av service time
ARRIVAL = SERVICE/LOAD # av inter-arrival time

'''
Structure	of	the	simulator:
    The	simulation	time
    The	events and their attributes
    State variables
'''

'''
The	event type is needed to	identify which kind of	
event must happen, and, hence, which specific	
function should	be	executed	
'''
TYPE1 = 1 #
SIM_TIME = 500000

arrivals = 0
users = 0
temp_st = []
BusyServer = False  # True: server is currently busy; False: server is currently idle
in_service = 0
MM1 = [] # insert or get value from the queue
loss = 0

# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay):
        self.arr = Narr
        self.dep = Ndep # data.dep = number of departures
        self.ut = NAveraegUser # data.ut = number of average users
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.utq = 0 # data.ut = number of average users in waiting line
        self.st = 0 # st = service time
        self.delays = []
        self.delayed = []
        self.delay_w = 0
        self.st_w = 0
        self.count = 0
        self.dep_w = 0


# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self, type, arrival_time):
        self.type = type
        self.arrival_time = arrival_time

# ******************************************************************************
# Server
# ******************************************************************************


class Server(object):

    # constructor
    def __init__(self):

        # whether the server is idle or not
        self.idle = True


# ******************************************************************************

# arrivals *********************************************************************
def arrival(time, FES, queue):
    global users, in_service
    global loss
    # print("users in queue last time", users,
    #       ",Arrival no.", data.arr+1, " at time ", time)

    # cumulate statistics
    data.arr += 1
    data.utq += (users-in_service) * (time - data.oldT)  
    data.ut += users*(time-data.oldT) 
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)

    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    users += 1
    client = Client(TYPE1, time)
    
    # insert the record in the queue
    queue.append(client)
    data.delayed.append(client.arrival_time)
    # if the server is idle start the service
    if users == 1:
        data.delayed.remove(client.arrival_time)
        data.count += 1
        
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)
        # service_time = random.uniform(0.1, SERVICE)
        data.st += service_time

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))

        in_service += 1

# ******************************************************************************

# departures *******************************************************************


def departure(time, FES, queue):
    global users
    global temp_st, in_service

    # print("Departure no. ",data.dep+1," at time ",time," with ",users," users in queue" )

    # cumulate statistics
    data.dep += 1
    data.ut += users*(time-data.oldT)
    data.utq += (users - in_service) * (time - data.oldT)
    users -= 1
    in_service -= 1
    data.oldT = time
    # print (f"\n data.ut depratrue= {data.ut}\n data.oldTdepratrue= {data.oldT}")
    
    # get the first element from the queue
    client = queue.pop(0)

    # do whatever we need to do when clients go away
    data.delay += (time-client.arrival_time)
    data.delays.append(time-client.arrival_time)
    
    #for those who experienced delay [waiting line]
    if client.arrival_time in data.delayed:
        data.delay_w += (time - client.arrival_time)
        data.dep_w += 1
        data.st_w += temp_st[0]
        temp_st.pop(0)

    # see whether there are more clients to in the line
    if users > 0:
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)
        # service_time = random.uniform(0.1, SERVICE)

        data.st += service_time
        temp_st.append(service_time)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
        in_service += 1

# ******************************************************************************
# plots
# ******************************************************************************
def plot(c1,c2,c3):
    print('arrival rate',c1)  
    print('expected',c3)  
    print('obtained',c2)
    
    plt.figure()
    plt.plot(c1,c2,'c')
    plt.plot(c1,c3,'r')
    # plt.plot(c1,c4,'g')
    plt.xlabel("Arrival rate")
    plt.ylabel("average waiting delay case 1")
    plt.legend(('obtained result','expected result'),loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************


random.seed(42)
data = Measure(0, 0, 0, 0, 0) # Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay

# the simulation time
time = 0

# the list of events in the form: (time, type)
# FES = Future-Event Set
# Ordered list, based on the first attribute of the items
FES = PriorityQueue()

# schedule the first arrival at t=0
FES.put((0, "arrival"))

# simulate until the simulated time reaches a constant
# Event Loop
while time < SIM_TIME:
    (time, event_type) = FES.get()

    if event_type == "arrival":
        arrival(time, FES, MM1)

    elif event_type == "departure":
        departure(time, FES, MM1)


landa = round(1/ARRIVAL, 3)
mu = round(1/SERVICE, 3)
rho = round(landa/mu, 3)

# --------------------------------------------
print('\n ========= M/M/1 =========')
print("\n Number of arrivals:",data.arr)
print("\n Number of transmited packets: ", data.dep)
print("\n Number of dropped packets:", loss)
print("\n Average number of packets: ", round(data.ut/time, 3)) # obtained E[N]
print("\n Expected average number of packets: ", round(rho/(1-rho), 3)) # expected E[N]
print("\n Average system delay:",round(data.delay/data.dep, 3) ,"ms") # obtained E[T]
print("\n Expected average system delay:", round(1/(mu - landa),3) ,"ms") # expected E[T]
print("\n time",time)
# --------------------------------------------


# --------------------------------------------
fig = plt.figure()
plt.hist(data.delays, density=False, bins = 1000)
plt.xlabel("queue delay (ms)")
plt.ylabel("frequency")
plt.title("distribution of the queuing delay")
plt.xlim(0.1000)
plt.grid()
plt.show()
# --------------------------------------------

# --------------------------------------------
print("\n Average queue delay", round(((data.delay - data.st)/data.dep),3),"ms" ) #obtained E[Tw]
print("\n Expected average queue delay", round(rho / (mu - landa),3),"ms") # expected E[Tw]
print("\n Average queue delay of packets experianced delay", round(((data.delay_w - data.st_w)/data.dep_w),3),"ms" )   
print("\n Average number of packets in queue", round(data.utq / time,3)) #obtained E[Nw] 
print("\n Expected Average number of packets in queue", round((rho * rho) / (1 - rho),3)) #expected E[Nw]
print("\n loss probability:",round((loss/data.arr)*100,3),"%")
print("\n busy time:", round(data.st / time * 100, 3),"%")
print("\n Expected busy time:", round(rho * 100, 3),"%")
print("\n")


# --------------------------------------------
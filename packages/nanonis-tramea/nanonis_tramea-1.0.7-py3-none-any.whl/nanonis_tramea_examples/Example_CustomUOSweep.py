#This example performs a custom user output (UO) sweep. You can create an array of
#UO voltages and it will record the selected channels at each UO voltage.

import nanonis_tramea
import time
import socket

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect(("localhost",6501))

nanonisInstance = nanonis_tramea.Nanonis(connection)
nanonisInstance.returnDebugInfo(1)

Sweep_UO_Index=1        #index of UO to sweep (User Output 1)
Sweep_UO_Start=-1
Sweep_UO_Stop=1
Sweep_NrPoints=10
Sweep_UO_Incr=(Sweep_UO_Stop-Sweep_UO_Start)/(Sweep_NrPoints-1)
Sweep_SettlingTime=0.2  #seconds to wait after sweeping to a point
Sweep_AcqSignals=[0,24] #signals to acquire, Uset Input 1 & User Output 1
AcqSignal_1=[]
AcqSignal_2=[]

#Create array with Sweep UO values
Sweep_UO_Values=[]
for point in range(Sweep_NrPoints):
    UOValue=point*Sweep_UO_Incr+Sweep_UO_Start
    Sweep_UO_Values.append(UOValue)
    
#Set UO to Sweep Start value
nanonisInstance.UserOut_ValSet(Sweep_UO_Index,Sweep_UO_Start)
    
#Sweep UO & acquire signals
for point in range(Sweep_NrPoints):
    nanonisInstance.UserOut_ValSet(Sweep_UO_Index,Sweep_UO_Values[point])
    time.sleep(Sweep_SettlingTime)
    AcqSignal_1.append(nanonisInstance.Signals_ValsGet(Sweep_AcqSignals, True)[2][1][0])
    AcqSignal_2.append(nanonisInstance.Signals_ValsGet(Sweep_AcqSignals, True)[2][1][1])

print("ACQUIRED SIGNAL 1")
print(AcqSignal_1)
print("ACQUIRED SIGNAL 2")
print(AcqSignal_2)

nanonisInstance.close()

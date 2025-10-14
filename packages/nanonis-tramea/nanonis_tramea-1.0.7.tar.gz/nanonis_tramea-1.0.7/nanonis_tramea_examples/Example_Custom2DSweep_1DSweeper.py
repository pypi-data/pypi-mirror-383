#This example performs a 2D sweep using a User output and the 1D Sweeper.
#For each value of the User output (y axis)
#it will perform a 1D Sweep (x axis). 

import nanonis_tramea
import numpy
import socket

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect(("localhost",6501))

nanonisInstance = nanonis_tramea.Nanonis(connection)
nanonisInstance.returnDebugInfo(1)

#Configuration variables of the 1D Sweeper
#The acquired signals are configured in the 1D Sweeper module for this example
Sweep_X_Start=1
Sweep_X_Stop=2
Sweep_X_NrPoints=10
Sweep_X_InitSettling=300 #miliseconds
Sweep_X_Settling=200 #miliseconds
Sweep_X_Period=100 #miliseconds
Sweep_X_MaxSlewRate=20 #units/second
Sweep_X_Autosave=0
Sweep_X_ShowSaveDialog=0
Sweep_X_Basename=""

#Configuration variables of the 2nd dimension
Sweep_Y_UserOutputIndex=3
Sweep_Y_Start=3
Sweep_Y_Stop=4
Sweep_Y_NrPoints=2
Sweep_Y_Incr=(Sweep_Y_Stop-Sweep_Y_Start)/(Sweep_Y_NrPoints-1)

#Create array with Sweep values for the 2nd dimension
Sweep_Y_Values=[]
for point in range(Sweep_Y_NrPoints):
    Y_Value=point*Sweep_Y_Incr+Sweep_Y_Start
    Sweep_Y_Values.append(Y_Value)
    
#Configure the 1D Sweeper properties
nanonisInstance.OneDSwp_PropsSet(
    Sweep_X_InitSettling,
    Sweep_X_MaxSlewRate,
    Sweep_X_NrPoints,
    Sweep_X_Period,
    Sweep_X_Autosave,
    Sweep_X_ShowSaveDialog,
    Sweep_X_Settling
    )

#Configure the 1D Sweeper limits
nanonisInstance.OneDSwp_LimitsSet(Sweep_X_Start,Sweep_X_Stop)

#Run the 2D Sweep & acquire signals
Sweep_Data_ForOneYValue=[]
Sweep_NrAcqChannels=nanonisInstance.OneDSwp_AcqChsGet()[2][0]+1 #the swept channel is part of the acquired data
Sweep_Data_Total=[[]]*Sweep_NrAcqChannels

for point in range(Sweep_Y_NrPoints):
    #Set the user output value configured for the 2nd dimension
    nanonisInstance.UserOut_ValSet(Sweep_Y_UserOutputIndex,Sweep_Y_Values[point])
    #Run the 1D Sweeper
    Sweep_Data_ForOneYValue=nanonisInstance.OneDSwp_Start(1,1,Sweep_X_Basename,0,0)[2]
    for SignalIdx in range(Sweep_NrAcqChannels):
        Sweep_Data_Total[SignalIdx]=Sweep_Data_Total[SignalIdx]+Sweep_Data_ForOneYValue[5][SignalIdx].tolist()
        
print(Sweep_Data_Total)

nanonisInstance.close()

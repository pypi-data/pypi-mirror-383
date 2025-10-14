"""
Created on Wed Feb 24 19:32:05 2021 (Markus A. Huber)

@author: Markus A. Huber

@license: MIT Copyright 2021 Markus A. Huber Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the
following conditions: The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import socket
import struct
import numpy as np


class Nanonis:
    displayInfo = 0

    def close(self):
        self.connection.close()

    def returnDebugInfo(self, displayInfo):
        self.displayInfo = displayInfo

    def printDebugInfo(self, responseTypes, bodyParts):
        i = 0
        for responseType in responseTypes:
            if (responseType[0] != '2'):
                print(responseType + ": " + str(bodyParts[i]))
            i = i + 1

    def __init__(self, connection):
        self.connection = connection


    # Handles parsing of strings from Client to Server
    def handleString(self, BodyElement, BodyType, BodyPart):
        BodyElement = bytes(BodyElement, 'utf-8')
        BodyType = str(len(BodyElement)) + 's'
        BodyPart = BodyPart + struct.pack('>i', len(BodyElement))
        BodyPart = BodyPart + struct.pack('>' + BodyType, BodyElement)
        return BodyPart

    # Handles parsing of arrays form Client to Server (w. length prepended)
    def handleArrayPrepend(self, Array, BodyType, BodyPart):
        arrayLength = len(Array)

        BodyPart = BodyPart + struct.pack('>i', arrayLength)
        for i in range(0, arrayLength):
            if BodyType[2] == "c":
                Entry = bytes(str(Array[i]), "utf-8")
            else:
                Entry = Array[i]

            BodyPart = BodyPart + (struct.pack('>' + BodyType[2], Entry))  # NEED ALSO BODYTYPE FOR SINGULAR
            # ELEMENTS

        return BodyPart

    #Handles parsing of strings arrays from Client to Server (w. length prepended)
    def handleArrayString(self, Array, BodyType, BodyPart):
        arrayLength = len(Array)
        nrbytes=4*arrayLength
        BodyPart = BodyPart + struct.pack('>i', nrbytes)
        BodyPart = BodyPart + struct.pack('>i', arrayLength)
        for i in range(0, arrayLength):
            Entry = self.handleString(Array[i],BodyType,bytearray())
            BodyType = str(len(Entry)) + 's'
            BodyPart = BodyPart + (struct.pack('>' + BodyType, Entry))  
        return BodyPart

    #Handles parsing of 2D arrays of floats
    def handle2DArray(self, Array, BodyType, BodyPart):
        arrayRows = len(Array) #number of rows
        BodyPart = BodyPart + struct.pack('>i', arrayRows)
        arrayColumns=len(Array[0]) #number of columns
        BodyPart = BodyPart + struct.pack('>i', arrayColumns)
        for i in range(0, arrayRows):
            for j in range(0, arrayColumns):
                Entry = float(Array[i][j])
                BodyPart = BodyPart + (struct.pack('>' + BodyType[1], Entry))
        return BodyPart

    # Handles parsing of arrays form Client to Server
    def handleArray(self, Array, BodyType, BodyPart):
        arrayLength = len(Array)
        for i in range(0, arrayLength):
            Entry = Array[i]
            BodyPart = BodyPart + (struct.pack('>' + BodyType[1], Entry))  
        return BodyPart

    def correctType(self, BodyType, Body):
        if BodyType == 'H' and isinstance(Body, np.uint16) is False:
            Body = np.uint16(Body)
        elif BodyType == 'h' and isinstance(Body, np.int16) is False:
            Body = np.int16(Body)
        elif BodyType == 'I' and isinstance(Body, np.uint32) is False:
            Body = np.uint32(Body)
        elif BodyType == 'i' and isinstance(Body, np.int32) is False:
            Body = np.int32(Body)
        elif BodyType == 'f' and isinstance(Body, np.float32) is False:
            Body = np.float32(Body)
        elif BodyType == 'd' and isinstance(Body, np.float64) is False:
            Body = np.float64(Body)

        return Body

    def send(self, Command, Body, BodyType):
        BodyPart = bytearray()

        for i in range(0, len(Body)):
            if "*" in BodyType[i]:
                instance = Body[i]
                type = BodyType[i]
                if "c" in BodyType[i]:
                    if isinstance(Body[i], str)==True:
                        #Array of chars (i.e. string)
                        BodyPart = self.handleString(Body[i], BodyType[i], BodyPart)
                    else:
                        #array of strings
                        BodyPart = self.handleArrayString(Body[i], BodyType[i], BodyPart)
                elif "-" in BodyType[i]:
                    for j in range(0, len(Body[i])):
                        instance[j] = self.correctType(type[2], instance[j])
                        Body[i] = instance
                    BodyPart = self.handleArray(Body[i], BodyType[i], BodyPart)
                elif "+" in BodyType[i]:
                    for j in range(0, len(Body[i])):
                        instance[j] = self.correctType(type[2], instance[j])
                        Body[i] = instance
                    BodyPart = self.handleArrayPrepend(Body[i], BodyType[i], BodyPart)
                else:
                    BodyPart = self.handleArray(Body[i], BodyType[i], BodyPart) 
            else:
                if "2" in BodyType[i]:
                    BodyPart = self.handle2DArray(Body[i], BodyType[i], BodyPart)
                else:
                    Body[i] = self.correctType(BodyType[i], Body[i])
                    BodyPart = BodyPart + struct.pack('>' + BodyType[i], Body[i])

        SendResponseBack = True

        BodySize = len(BodyPart)
        ZeroBuffer = bytearray(2)

        Message = bytearray(str(Command).ljust(32, '\0').encode()) + \
                  BodySize.to_bytes(4, byteorder='big') + \
                  SendResponseBack.to_bytes(2, byteorder='big') + \
                  ZeroBuffer + \
                  BodyPart
        if (self.displayInfo == 1):
            print('Send message: ')
            print(Message)

        self.connection.send(Message)

        Recv_Header = self.connection.recv(40)  # read header - always 40 bytes
        Recv_BodySize = struct.unpack('>I', Recv_Header[32:36])[0]  # get body size
        Recv_Body = b'\x3e\x35\x79\x8e\xe2\x30\x8c\x3a\xbe\x35\x79\x8e\xe2\x30\x8c\x3a\x00\x00\x00\x00\x00\x00\x00\x00'
        Recv_Body = self.connection.recv(Recv_BodySize)  # read whole body
        Recv_Command = Recv_Header[0:32].decode().strip('0').replace('\x00', '')
        if (self.displayInfo == 1):
            print("BodySize:", Recv_BodySize)
            print("Received Body:", len(Recv_Body))
        counter = 0
        while (Recv_BodySize != len(Recv_Body) or counter < 1000):  # Making sure all the data is received
            Recv_Body = Recv_Body + self.connection.recv(Recv_BodySize - len(Recv_Body))
            counter += 1
        if (self.displayInfo == 1):
            print("BodySize2:", Recv_BodySize)
            print("Received Body2:", len(Recv_Body))
        (self.connection.settimeout(1000))

        if (self.displayInfo == 1):
            print('Received data:')
            print(Recv_Header)
            print(Recv_Body)
        if Recv_Command == Command:
            if (self.displayInfo == 1):
                print('Correct Command.')
            return Recv_Body
        else:
            print('Wrong Command')
            return []


    #Parses Array coming back from Server
    def decodeArray(self, response, index, numOfElements, responseType):
        decoded_nums = []
        decoded_num = 0
        if isinstance(numOfElements, list):
            return []
        for i in range(0, numOfElements):
            decoded_num = response[index:(index + 4)]
            decoded_num = struct.unpack('>' + responseType, decoded_num)
            decoded_nums.append(decoded_num)
            index += 4
        return decoded_nums

    #Parses String Array coming back from Server (with length prepended)
    def decodeStringPrepended(self, response, index, numOfStrings):
        decoded_strings = []
        decoded_string = ""
        for j in range(0, numOfStrings):
            decoded_num = ""
            for i in range(0, 4):
                decoded_num = decoded_num + str(response[index + i])
            decoded_num = int(decoded_num)
            for i in range(index + 4, (index + 4) + decoded_num):
                decoded_string = decoded_string + chr(response[i])
            decoded_strings.append(decoded_string)
            index = index + decoded_num + 4

            decoded_string = ""

        return decoded_strings


    #Parses singular String coming back from Server
    def decodeSingularString(self, response, index, stringLength):  # Now need to make discinction in *c
        decoded_string = ""
        for i in range(0, stringLength):
            decoded_string = decoded_string + chr(response[index + i])
        return decoded_string


    #Parses Array coming back form Server (with length of each element prepended)
    def decodeArrayPrepended(self, response, index, numOfElements, responseType):
        decoded_nums = []
        if(responseType == 'd'):
            increment = 8
        else:
            increment = 4
        if isinstance(numOfElements, list):
            return []
        for i in range(0, numOfElements):
            decoded_num = response[index:(index + increment)]
            decoded_num = struct.unpack('>' + responseType, decoded_num)
            decoded_nums.append(decoded_num)
            index = index + increment
        return decoded_nums

    def parseError(self, response, index):
        #if(index == 8):
            #margin = 4
        #else:
            #margin = 8
        margin = 8  #4 bytes (error status) + 4 bytes (error description size)
        errorIndex = index + margin
        jumpDistance = len(response) - errorIndex
        errorString = response[errorIndex:(errorIndex + jumpDistance)].decode()
        return errorString

    def parseGeneralResponse(self, Response, ResponseTypes):
        counter = 0
        Variables = []
        universalLength = 0
        for ResponseType in ResponseTypes:
            if ResponseType[0] != '*':
                if ResponseType[0] == '2':
                    NoOfRows = Variables[-2]  # no of rows must be directly before cols
                    NoOfCols = Variables[-1]  # no of cols must be directly before array
                    SentArray = []
                    Datasize = struct.calcsize('>' + ResponseType[1])
                    for i in range(NoOfRows * NoOfCols):
                        Value = struct.unpack('>' + ResponseType[1], Response[counter:(counter + Datasize)])
                        counter = counter + Datasize
                        SentArray.append(Value)
                    Variables.append(np.reshape(SentArray, (NoOfRows, NoOfCols)))  # !!!!!
                    if (self.displayInfo == 1):
                        print(ResponseType, '  : ', np.reshape(SentArray, (NoOfRows, NoOfCols)))

                else:
                    Datasize = struct.calcsize('>' + ResponseType)
                    Value = struct.unpack('>' + ResponseType, Response[counter:(counter + Datasize)])
                    # print(ResponseType, '   : ', Value[0])
                    Variables.append(Value[0])
                    counter = counter + Datasize
            else:
                if ResponseType[1] == '+':
                    NoOfChars = Variables[-1]
                    String = self.decodeStringPrepended(Response, counter, NoOfChars)  # Nano
                    # print(ResponseType, '  : ', String)
                    counter = counter + Variables[-2]
                    Variables.append(String)
                elif ResponseType[1] == '-':
                    NoOfChars = Variables[-1]
                    String = self.decodeSingularString(Response, counter, NoOfChars)  # Nano
                    # print(ResponseType, " : ", String)
                    counter = counter + NoOfChars
                    Variables.append(String)
                elif ResponseType[1] == '*':
                    #if universalLength == 0:
                    #    universalLength = Variables[-1]
                    universalLength = Variables[0]
                    if ResponseType[2] == 'c':
                        Result = self.decodeStringPrepended(Response, counter, universalLength)
                        #counter = counter + universalLength 
                        if len(Result)!=0:
                            for item in Result:
                                counter=counter+4+len(item)
                    else:
                        Result = self.decodeArray(Response, counter, universalLength, ResponseType[2])  # Nano
                        # print(ResponseType, ' : ', Result)
                        counter = counter + (universalLength * 4)
                    Variables.append(Result)
                else:  # ResponseType[1] == 'w':
                    Result = self.decodeArrayPrepended(Response, counter, Variables[-1], ResponseType[1])# Nano
                    if (ResponseType[1]=='d'):
                        increment = 8
                    else:
                        increment = 4
                    if (Variables[-1] != 0): #here lies the problem
                        counter = counter + (Variables[-1] * increment)
                    #else:
                        #counter = counter + increment
                    Variables.append(Result)
                    # print(ResponseType, '  : ', Result)
        ErrorString = self.parseError(Response, counter)#Response[12:(12 + ErrorLength)].decode()
        if(len(ErrorString) != 0):
            print('The following error appeared:', "\n", ErrorString)
            return [ErrorString, Response, Variables]
        else:
            if (self.displayInfo == 1):
                print('No error messages. Error status was: 0')
            return [ErrorString, Response, Variables]

    def quickSend(self, Command, Body, BodyType, ResponseTypes):

        '''

        quickSend(self, Command, Body, BodyType,ResponseTypes)

        Parameters for quicksend:
            Command : as written in documentation
            Body: Body to send as array [] - use [] when no argument should be sent!
            BodyType: Array of [Type of data] - see also ResponseTypes
            ResponseTypes: Array of Types to decode response

            IDENTIFIERS:

            --> "+" --> Array with length of array prepended
            --> "-" --> Array without length of array prepended

            H  : unsigned int16
            h  : int16
            I  : unsigned int32
            i  : int32
            f  : float32
            d  : float64 (double)

            Arrays (1D):
            Start with *
            length taken from directly before the array

            (+  or -) *I : array of unsigned int32
            (+ or -) *i : array of int32
            (+ or -) *f : array of float32
            (+ or -) *d : array of float64
            (+ or -) *c : String! (Array of chars - interpreted as string!)
            NEED TO UPDATE WITHOUT "*"!!!!

            Arrays (2D):
            start with 2
            width and height taken from the two variables before the array

            (+ or -) 2f : 2d array of float32

            UNIQUE FOR RETURN TYPES:

            "**" Identifier for arrays whose size is defined by the first argument as int

        '''

        response = self.send(Command, Body, BodyType)
        if response != []:
            ResponseData = self.parseGeneralResponse(response, ResponseTypes)
            if self.displayInfo == 1:
                self.printDebugInfo(ResponseTypes, ResponseData[2])
            return tuple(ResponseData)
        else:
            print('No data returned.')
            return tuple([])

    def ThreeDSwp_AcqChsSet(self, Channel_Indexes):
        """

    Sets the list of recorded channels of the 3D Sweeper.
    Arguments:

    - Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
    - Channel indexes (1D array int) are the indexes of recorded channels. The indexes are comprised between 0 and 127, and it corresponds to the full list of signals available in the system.
    To get the signal name and its corresponding index in the list of the 128 available signals in the Nanonis Controller, use the Signal.NamesGet function, or check the RT Idx value in the Signals Manager module.

    Return arguments (if Send response back flag is set to True when sending request message):

    - Error described in the Response message>Body section

        """

        return self.quickSend("3DSwp.AcqChsSet", [Channel_Indexes], ["+*i"], [])

    def ThreeDSwp_AcqChsGet(self):
        """
        Returns the list of recorded channels of the 3D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        - Channel indexes (1D array int) are the indexes of the recorded channels. The indexes are comprised between 0 and 127, and it corresponds to the full list of signals available in the system
        - Channels names size (int) is the size in bytes of the channels names array
        - Channels names number (int) is the number of elements of the channels names array
        - Channels names (1D array string) returns an array of channel names strings, where each string comes
        prepended by its size in bytes
        - Error described in the Response message>Body section
        """

        return self.quickSend("3DSwp.AcqChsGet", [], [], ["i", "*i", "i", "i", "*+c"])

    def ThreeDSwp_SaveOptionsSet(self, Series_Name, Create_Date_Time_Folder, Comment, Modules_Names):
        """
        Sets the saving options of the 3D Sweeper. Arguments:

    - Series name size (int) is the size (number of characters) of the series name string
    - Series name (string) is the base name used for the saved sweeps. If empty string, there is no change
    - Create Date&Time Folder (int) defines if this feature is active, where 0=no change, 1=On, 2=Off.
    If On, it creates a subfolder within the Session folder whose name is a combination of the basename and
    current date&time of the sweep, every time a sweep finishes.
    - Comment size (int) is the size (number of characters) of the comment string
    - Comment (string) is the comment saved in the header of the files. If empty string, there is no change
    - Modules names size (int) is the size in bytes of the modules array. These are the modules whose
    parameters are saved in the header of the files
    - Modules names number (int) is the number of elements of the modules names array
    - Modules names (1D array string) is an array of modules names strings, where each string comes
    prepended by its size in bytes

    Return arguments (if Send response back flag is set to True when sending request message to the server):

    - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.SaveOptionsSet", [Series_Name, Create_Date_Time_Folder, Comment, Modules_Names], ["+*c", "i", "+*c", "+*c"], [])

    def ThreeDSwp_SaveOptionsGet(self):
        """
        Returns the saving options of the 3D Sweeper.
        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message to the server):

        - Series name size (int) is the size of the series name string
        - Series name (string) is the base name used for the saved sweeps
        - Create Date&Time Folder (unsigned int32) returns if this feature is active, where 0=Off, 1=On
        - Fixed parameters size (int) is the size in bytes of the Fixed parameters string array
        - Number of fixed parameters (int) is the number of elements of the Fixed parameters string array
        - Fixed parameters (1D array string) returns the fixed parameters of the sweep. The size of each string item
        comes right before it as integer 32.
        - Comment size (int) is the size (number of characters) of the comment string
        - Comment (string) is the comment saved in the header of the files
        - Modules parameters size (int) is the size in bytes of the modules parameters array. These are the modules
        parameters saved in the header of the files
        - Modules parameters number (int) is the number of elements of the modules parameters array
        - Modules parameters (1D array string) is an array of modules parameters strings, where each string comes
        prepended by its size in bytes.
        Each item displays the module name followed by the “>” character followed by the parameter name followed by the “=” character followed by the parameter value
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.SaveOptionsGet", [], [], ["i", "*-c", "I", "i", "i", "*+c", "i", "*-c", "i", "i", "*-c"])

    def ThreeDSwp_Start(self, Wait_until_finished):
        """
    Starts a sweep in the 3D Sweeper module.
    When Send response back is set to True, it returns immediately afterwards.
    Arguments: 
    -	Wait until finished (unsigned int32) determines if the function returns immediately after starting a sweep (=0), or if the function waist until the sweep finishes (=1)
    Return arguments (if Send response back flag is set to True when sending request message):
    - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.Start", [Wait_until_finished], ["I"], [])

    def ThreeDSwp_Stop(self):
        """

        3DSwp.Stop
        Stops the sweep in the 3D Sweeper module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.Stop", [], [], [])

    def ThreeDSwp_Open(self):
        """
        3DSwp.Open
        Opens the 3D Sweeper module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.Open", [], [], [])


    def ThreeDSwp_StatusGet(self):
        """
    Returns the status of the 3D Sweeper.
    Arguments: None
    Return arguments (if Send response back flag is set to True when sending request message):
    - Status (unsigned int32) is status of the 3D Sweep, where 0=Stopped, 1=Running, 2=Paused
    - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StatusGet", [], [], ["I"])

    def ThreeDSwp_SwpChSignalSet(self, Swp_Channel_Index):
        """
        3DSwp.SwpChSignalSet
        Sets the Sweep Channel signal in the 3D Sweeper. Arguments:
        - Sweep channel index (int) is the index of the Sweep Channel, where -1 sets the Unused option Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.SwpChSignalSet", [Swp_Channel_Index], ["i"], [])

    def ThreeDSwp_SwpChSignalGet(self):
        """

        3DSwp.SwpChSignalGet
        Returns the selected Sweep Channel signal in the 3D Sweeper.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        - Sweep channel index (int) is the index of the Sweep Channel, where -1 is the Unused option
        - Channels names size (int) is the size in bytes of the Channels names string array
        - Number of channels (int) defines the number of elements of the Channels names string array
        - Channels names (1D array string) returns the list of channels names. The size of each string item comes
        right before it as integer 32.
        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.SwpChSignalGet", [], [], ["i", "i", "i", "*+c"])

    def ThreeDSwp_SwpChLimitsSet(self, Start, Stop):
        """
        3DSwp.SwpChLimitsSet
        Sets the limits of the Sweep Channel in the 3D Sweeper.
        Arguments:

        - Start (float32) defines the value where the sweep starts
        - Stop (float32) defines the value where the sweep stops

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.SwpChLimitsSet", [ Start, Stop], ["f","f"], [])

    def ThreeDSwp_SwpChLimitsGet(self):
        """
        3DSwp.SwpChLimitsGet
        Returns the limits of the Sweep Channel in the 3D Sweeper.
        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Start (float32) defines the value where the sweep starts
        - Stop (float32) defines the value where the sweep stops
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.SwpChLimitsGet", [], [], ["f", "f"])

    def ThreeDSwp_SwpChPropsSet(self, NumOfPoints, NumOfSweeps, BwdSweep, EndOfSweep, EndOfSweepArbVal, SaveAll):
        """
        3DSwp.SwpChPropsSet
    Sets the configuration of the Sweep Channel parameters in the 3D Sweeper. $
    Arguments:

    - Number of points (int) sets the number of points of the sweep. 0 points means no change
    - Number of sweeps (int) sets the total number of sweeps. 0 sweeps means no change
    - Backward sweep (int) defines if the backward sweep is active, where 0=no change, 1=On, 2=Off
    - End of sweep action (int) defines the behavior of the signal at the end of the sweep, where 0=no change, 1=no action, 2=reset signal to the original value, 3=go to arbitrary value
    - End of sweep arbitrary value (float32) sets the arbitrary value to go at the end of the sweep if Go to
    arbitrary value is configured
    - Save all (int) defines if all the configured sweeps are saved or only the averaged sweep, where 0=no change, 1=On, 2=Off

    Return arguments (if Send response back flag is set to True when sending request message):

    - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.SwpChPropsSet", [NumOfPoints, NumOfSweeps, BwdSweep, EndOfSweep, EndOfSweepArbVal, SaveAll], ["i","i", "i", "i", "f", "i"], [])

    def ThreeDSwp_SwpChPropsGet(self):
        """
        3DSwp.SwpChPropsGet
    Returns the configuration of the Sweep Channel parameters in the 3D Sweeper.
    Arguments: None

    Return arguments (if Send response back flag is set to True when sending request message):

    - Number of points (int) returns the number of points of the sweep
    - Number of sweeps (int) returns the total number of sweeps
    - Backward sweep (unsigned int32) returns if the backward sweep is active, where 0=Off, 1=On
    - End of sweep action (unsigned int32) returns the behavior of the signal at the end of the sweep, where
    0=no action, 1=reset signal to the original value, 2=go to arbitrary value
    - End of sweep arbitrary value (float32) returns the arbitrary value to go at the end of the sweep if Go to
    arbitrary value is configured
    - Save all (unsigned int32) returns if all the configured sweeps are saved or only the averaged sweep, where
    0=Off, 1=On
    - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.SwpChPropsGet", [], [], ["i", "i", "I", "I", "f", "I"])


    def ThreeDSwp_SwpChTimingSet(self, InitSettlingTime, SettlingTime, IntegrationTime, EndSettlingTime, MaxSlewRate):
        """
        3DSwp.SwpChTimingSet
        Sets the timing parameters of the Sweep Channel in the 3D Sweeper.
        Arguments:

        - Initial settling time (s) (float32)
        - Settling time (s) (float32)
        - Integration time (s) (float32)
        - End settling time (s) (float32)
        - Maximum slew rate (units/s) (float32)

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.SwpChTimingSet", [InitSettlingTime, SettlingTime, IntegrationTime, EndSettlingTime, MaxSlewRate], ["f","f","f","f","f"], [])


    def  ThreeDSwp_SwpChTimingGet(self):
        """
        3DSwp.SwpChTimingGet
        Returns the timing parameters of the Sweep Channel in the 3D Sweeper.
        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Initial settling time (s) (float32)
        - Settling time (s) (float32)
        - Integration time (s) (float32)
        - End settling time (s) (float32)
        - Maximum slew rate (units/s) (float32)
        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.SwpChTimingGet", [], [], ["f","f","f","f","f"])

    def  ThreeDSwp_SwpChModeSet(self, Segments_Mode):
        """
        3DSwp.SwpChModeSet
        Sets the segments mode of the Sweep Channel signal in the 3D Sweeper.
        Arguments:

        - Segments mode (int) is the number of characters of the segments mode string.
        If the segments mode is Linear, this value is 6. If the segments mode is MLS, this value is 3
        - Segments mode (string) is Linear in Linear mode or MLS in MultiSegment mode

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.SwpChModeSet", [Segments_Mode], ["+*c"], [])

    def  ThreeDSwp_SwpChModeGet(self):
        """
        3DSwp.SwpChModeGet
        Returns the segments mode of the Sweep Channel signal in the 3D Sweeper.
        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Segments mode (int) is the number of characters of the segments mode string.
        If the segments mode is Linear, this value is 6. If the segments mode is MLS, this value is 3
        - Segments mode (string) is Linear in Linear mode or MLS in MultiSegment mode
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.SwpChModeGet", [], [], ["i", "*-c"])

    def  ThreeDSwp_SwpChMLSSet(self, NumOfSegments, StartVals, StopVals, SettlingTimes, IntegrationTimes, NoOfSteps, LastSegmentArray):
        """
        3DSwp.SwpChMLSSet
        Sets the MultiSegment values of the Sweep Channel in the 3D Sweeper.
        Arguments:

        - Number of segments (int) is the total number of segments
        - Segment Start values (1D array float32) are the start values of the segments of the Sweep Channel
        - Segment Stop values (1D array float32) are the stop values of the segments of the Sweep Channel
        - Segment Settling times (1D array float32) are the settling times of the segments in seconds
        - Segment Integration times (1D array float32) are the integration times of the segments in seconds
        - Segment Number of steps (1D array int) are the number of steps of each segment
        - Last segment? array (1D array unsigned int32) defines if the segments are the last one (1) or not (0)

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.SwpChMLSSet", [ NumOfSegments, StartVals, StopVals, SettlingTimes, IntegrationTimes, NoOfSteps, LastSegmentArray], ["i", "*f","*f","*f","*f","*i", "*I"], [])

    def  ThreeDSwp_SwpChMLSGet(self):
        """
        3DSwp.SwpChMLSGet
        Returns the MultiSegment values of the Sweep Channel in the 3D Sweeper.
        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Number of segments (int) is the total number of segments. It defines the size of the following arrays
        - Segment Start values (1D array float32) are the start values of the segments of the Sweep Channel
        - Segment Stop values (1D array float32) are the stop values of the segments of the Sweep Channel
        - Segment Settling times (1D array float32) are the settling times of the segments in seconds
        - Segment Integration times (1D array float32) are the integration times of the segments in seconds
        - Segment Number of steps (1D array int) are the number of steps of each segment
        - Last segment? array (1D array unsigned int32) defines if the segments are the last one (1) or not (0)
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.SwpChMLSGet", [], [], ["i", "**f", "**f", "**f", "**f", "**i", "**I"])

    def  ThreeDSwp_StpCh1SignalSet(self, StepChannelOneIndex):
        """
        3DSwp.StpCh1SignalSet
        Sets the Step Channel 1 signal in the 3D Sweeper.
         Arguments:

        - Step channel 1 index (int) is the index of the Step Channel 1, where -1 sets the Unused option

         Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh1SignalSet", [StepChannelOneIndex], ["i"], [])

    def ThreeDSwp_StpCh1SignalGet(self):
        """
        3DSwp.StpCh1SignalGet
        Returns the selected Step Channel 1 signal in the 3D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Step channel 1 index (int) is index of the Step Channel 1, where -1 is the Unused option
        - Channels names size (int) is the size in bytes of the Channels names string array
        - Number of channels (int) is the number of elements of the Channels names string array
        - Channels names (1D array string) returns the list of channels names. The size of each string item comes
        right before it as integer 32.
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh1SignalGet", [], [], ["i", "i", "i", "*+c"])

    def ThreeDSwp_StpCh1LimitsSet(self, Start, Stop):
        """
        3DSwp.StpCh1LimitsSet
        Sets the limits of the Step Channel 1 in the 3D Sweeper.

        Arguments:

        - Start (float32) defines the value where the sweep starts
        - Stop (float32) defines the value where the sweep stops

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.StpCh1LimitsSet", [Start, Stop], ["f", "f"], [])

    def  ThreeDSwp_StpCh1LimitsGet(self):
        """
        3DSwp.StpCh1LimitsGet
        Returns the limits of the Step Channel 1 in the 3D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Start (float32) defines the value where the sweep starts
        - Stop (float32) defines the value where the sweep stops
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh1LimitsGet", [], [], ["f", "f"])

    def ThreeDSwp_StpCh1PropsSet(self, NoOfPoints, BwdSweep, EndOfSweep, EndOfSweepVal):
        """
        3DSwp.StpCh1PropsSet
        Sets the configuration of the Step Channel 1 parameters in the 3D Sweeper.

        Arguments:

        - Number of points (int) sets the number of points of the sweep. 0 points means no change
        - Backward sweep (int) defines if the backward sweep is active, where 0=no change, 1=On, 2=Off
        - End of sweep action (int) defines the behavior of the signal at the end of the sweep, where 0=no change, 1=no action, 2=reset signal to the original value, 3=go to arbitrary value
        - End of sweep arbitrary value (float32) sets the arbitrary value to go at the end of the sweep if Go to
        arbitrary value is configured

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh1PropsSet", [NoOfPoints, BwdSweep, EndOfSweep, EndOfSweepVal], ["i", "i", "i", "f"], [])

    def  ThreeDSwp_StpCh1PropsGet(self):
        """
        3DSwp.StpCh1PropsGet
        Returns the configuration of the Step Channel 1 parameters in the 3D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Number of points (int) returns the number of points of the sweep
        - Backward sweep (unsigned int32) returns if the backward sweep is active, where 0=Off, 1=On
        - End of sweep action (unsigned int32) returns the behavior of the signal at the end of the sweep, where
        0=no action, 1=reset signal to the original value, 2=go to arbitrary value
        - End of sweep arbitrary value (float32) returns the arbitrary value to go at the end of the sweep if Go to
        arbitrary value is configured
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh1PropsGet", [], [], ["i", "I", "I", "f"])

    def  ThreeDSwp_StpCh1TimingSet(self, InitSettlingTime, EndSettlingTime, MaxSlewRate):
        """
        3DSwp.StpCh1TimingSet
        Sets the timing parameters of the Step Channel 1 in the 3D Sweeper.

        Arguments:

        - Initial settling time (s) (float32)
        - End settling time (s) (float32)
        - Maximum slew rate (units/s) (float32)

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.StpCh1TimingSet", [InitSettlingTime, EndSettlingTime, MaxSlewRate], ["f", "f", "f"], [])

    def  ThreeDSwp_StpCh1TimingGet(self):
        """
        3DSwp.StpCh1TimingGet
        Returns the timing parameters of the Step Channel 1 in the 3D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Initial settling time (s) (float32)
        - End settling time (s) (float32)
        - Maximum slew rate (units/s) (float32)
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh1TimingGet", [], [], ["f", "f", "f"])

    def ThreeDSwp_StpCh2SignalSet(self, StepChannel2Name):
        """
        3DSwp.StpCh2SignalSet
        Sets the Step Channel 2 signal in the 3D Sweeper.

        Arguments:

        - Step Channel 2 name (string) is the name of the signal selected for the Step Channel 2

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh2SignalSet", [StepChannel2Name], ["+*c"], [])

    def ThreeDSwp_StpCh2SignalGet(self):
        """
        3DSwp.StpCh2SignalGet
        Returns the selected Step Channel 2 signal in the 3D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Step Channel 2 name size (int) is the number of characters of the Step Channel 2 name string
        - Step Channel 2 name (string) is the name of the signal selected for the Step Channel 2
        - Channels names size (int) is the size in bytes of the Channels names string array
        - Number of channels (int) is the number of elements of the Channels names string array
        - Channels names (1D array string) returns the list of channels names. The size of each string item comes right before it as integer 32.
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh2SignalGet", [], [], ["i", "*-c", "i", "i", "*+c"])


    def ThreeDSwp_StpCh2LimitsSet(self, Start, Stop):
        """

        3DSwp.StpCh2LimitsSet

        Sets the limits of the Step Channel 2 in the 3D Sweeper.

         Arguments:

        - Start (float32) defines the value where the sweep starts
        - Stop (float32) defines the value where the sweep stops

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh2LimitsSet", [Start, Stop], ["f", "f"], [])

    def ThreeDSwp_StpCh2LimitsGet(self):
        """
        3DSwp.StpCh2LimitsGet
        Returns the limits of the Step Channel 2 in the 3D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Start (float32) defines the value where the sweep starts
        - Stop (float32) defines the value where the sweep stops
        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.StpCh2LimitsGet", [], [], ["f", "f"])

    def ThreeDSwp_StpCh2PropsSet(self, NumOfPoints, BwdSweep, EndOfSweep, EndOfSweepVal):
        """

        3DSwp.StpCh2PropsSet

        Sets the configuration of the Step Channel 2 parameters in the 3D Sweeper.

        Arguments:

        - Number of points (int) sets the number of points of the sweep. 0 points means no change
        - Backward sweep (int) defines if the backward sweep is active, where 0=no change, 1=On, 2=Off
        - End of sweep action (int) defines the behavior of the signal at the end of the sweep, where 0=no change, 1=no action, 2=reset signal to the original value, 3=go to arbitrary value
        - End of sweep arbitrary value (float32) sets the arbitrary value to go at the end of the sweep if Go to
        arbitrary value is configured

        Return arguments (if Send response back flag is set to True when sending request message):
         Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.StpCh2PropsSet", [NumOfPoints, BwdSweep, EndOfSweep, EndOfSweepVal], ["i", "i", "i", "f"], [])

    def ThreeDSwp_StpCh2PropsGet(self):
        """
        3DSwp.StpCh2PropsGet
        Returns the configuration of the Step Channel 2 parameters in the 3D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Number of points (int) returns the number of points of the sweep
        - Backward sweep (unsigned int32) returns if the backward sweep is active, where 0=Off, 1=On
        - End of sweep action (unsigned int32) returns the behavior of the signal at the end of the sweep, where
        0=no action, 1=reset signal to the original value, 2=go to arbitrary value
        - End of sweep arbitrary value (float32) returns the arbitrary value to go at the end of the sweep if Go to
        arbitrary value is configured
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh2PropsGet", [], [], ["i", "I", "I", "f"])

    def ThreeDSwp_StpCh2TimingSet(self, InitSettlingTime, EndSettlingTime, MaxSlewRate):
        """
        3DSwp.StpCh2TimingSet
        Sets the timing parameters of the Step Channel 2 in the 3D Sweeper.

        Arguments:

        - Initial settling time (s) (float32)
        - End settling time (s) (float32)
        - Maximum slew rate (units/s) (float32)

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh2TimingSet", [ InitSettlingTime, EndSettlingTime, MaxSlewRate], ["f", "f", "f"], [])

    def ThreeDSwp_StpCh2TimingGet(self):
        """
        3DSwp.StpCh2TimingGet
        Returns the timing parameters of the Step Channel 2 in the 3D Sweeper
        .
        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Initial settling time (s) (float32)
        - End settling time (s) (float32)
        - Maximum slew rate (units/s) (float32)
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.StpCh2TimingGet", [], [], ["f", "f", "f"])
    def ThreeDSwp_TimingRowLimitSet(self, RowIndex, MaxTime, ChannelIndex):
        """
        3DSwp.TimingRowLimitSet
        Sets the maximum time (seconds) and channel of the selected row in the Advanced Timing section of the 3D Sweeper.

        Arguments:

        - Row index (int) starting from 0 index
        - Maximum time (seconds) (float32) defines the ultimate stop condition which is required since certain
        signal types can result in a target SNR or StdDev never being reached (infinite integration).
        Setting it to the minimum essentially switches off that set (limits to a single RT Cycle). NaN means no change
        - Channel index (int) defines the channel to which the advanced configuration of the selected row is applied. -1 means no change

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.TimingRowLimitSet", [RowIndex, MaxTime, ChannelIndex], ["i", "f", "i"], [])

    def ThreeDSwp_TimingRowLimitGet(self, RowIndex):
        """
        3DSwp.TimingRowLimitGet
        Returns the maximum time (seconds) and channel of the selected row in the Advanced Timing section of the 3D Sweeper.

        Arguments:

        - Row index (int) starting from 0 index

        Return arguments (if Send response back flag is set to True when sending request message):

        - Maximum time (seconds) (float32) defines the ultimate stop condition which is required since certain signal types can result in a target SNR or StdDev never being reached (infinite integration).
        - Setting it to the minimum essentially switches off that set (limits to a single RT Cycle).
        - Channel index (int) defines the channel to which the advanced configuration of the selected row is applied
        - Channels names size (int) is the size in bytes of the Channels names string array
        - Number of channels (int) is the number of elements of the Channels names string array
        - Channels names (1D array string) returns the list of channels names. The size of each string item comes
        right before it as integer 32.
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.TimingRowLimitGet", [RowIndex], ["i"], ["f", "i", "i", "i", "*+c"])

    def ThreeDSwp_TimingRowMethodsSet(self, RowIndex, MethodLower, MethodMiddle, MethodUpper, MethodAlt):
        """
        3DSwp.TimingRowMethodsSet
        Sets the methods of the selected row in the Advanced Timing section of the 3D Sweeper.
        The possible values are -1=no change, 0=None, 1=Time, 2=Standard Deviation, 3=Signal to Noise Ratio.

        Arguments:
        - Row index (int) starting from 0 index
        - Method lower (int) defines the method in the lower range of the selected row
        - Method middle (int) defines the method in the middle range of the selected row
        - Method upper (int) defines the method in the upper range of the selected row
        - Method alternative (int) defines the method in the alternative range of the selected row

        Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.TimingRowMethodsSet", [RowIndex, MethodLower, MethodMiddle, MethodUpper, MethodAlt], ["i","i","i","i","i"], [])


    def ThreeDSwp_TimingRowMethodsGet(self, RowIndex):
        """
        3DSwp.TimingRowMethodsGet
        Returns the methods of the selected row in the Advanced Timing section of the 3D Sweeper. The possible values are 0=None, 1=Time, 2=Standard Deviation, 3=Signal to Noise Ratio.

        Arguments:

        - Row index (int) starting from 0 index

        Return arguments (if Send response back flag is set to True when sending request message):

        - Method lower (int) gets the method in the lower range of the selected row
        - Method middle (int) gets the method in the middle range of the selected row
        - Method upper (int) gets the method in the upper range of the selected row
        - Method alternative (int) gets the method in the alternative range of the selected row
        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.TimingRowMethodsGet", [RowIndex], ["i"], ["i","i","i","i"])


    def ThreeDSwp_TimingRowValsSet(self, RowIndex, MiddleRangeFrom, LowerRangeVal, MiddleRangeVal, MiddleRangeTo, UpperRangeVal, AltRangeVal):
        """
        3DSwp.TimingRowValsSet
        Sets the ranges of the selected row in the Advanced Timing section of the 3D Sweeper.

        Arguments:

        - Row index (int) starting from 0 index
        - Middle range: from (float64) is the upper limit of the lower range of the selected row
        - Lower range: value (float64) is the value in the lower range of the selected row
        - Middle range: value (float64) is the value in the middle range of the selected row
        - Middle range: to (float64) is the lower limit of the upper range of the selected row
        - Upper range: value (float64) is the value of the upper range of the selected row
        - Alternative range: value (float64) is the value of the alternative range of the selected row

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.TimingRowValsSet", [RowIndex, MiddleRangeFrom, LowerRangeVal, MiddleRangeVal,
                                                         MiddleRangeTo, UpperRangeVal, AltRangeVal], ["i", "d", "d", "d", "d", "d", "d"], [])

    def ThreeDSwp_TimingRowValsGet(self, RowIndex):
        """
        3DSwp.TimingRowValsGet
        Returns the ranges of the selected row in the Advanced Timing section of the 3D Sweeper.

        Arguments:

        - Row index (int) starting from 0 index

        Return arguments (if Send response back flag is set to True when sending request message):

        - Middle range: from (float64) is the upper limit of the lower range of the selected row
        - Lower range: value (float64) is the value in the lower range of the selected row
        - Middle range: value (float64) is the value in the middle range of the selected row
        - Middle range: to (float64) is the lower limit of the upper range of the selected row
        - Upper range: value (float64) is the value of the upper range of the selected row
        - Alternative range: value (float64) is the value of the alternative range of the selected row
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.TimingRowValsGet", [RowIndex], ["i"], ["d","d","d","d","d","d"])


    def ThreeDSwp_TimingEnable(self, Enable):
        """
        3DSwp.TimingEnable
        Enables/disables the Advanced Timing in the 3D Sweeper module.

        Arguments:
        - Enable (unsigned int32) where 0=Disable, 1=Enable

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("3DSwp.TimingEnable", [Enable], ["I"], [])

    def ThreeDSwp_TimingSend(self):
        """
        3DSwp.TimingSend
        Sends the Advanced Timing configuration of the 3D Sweeper module to the real time controller.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.TimingSend", [], [], [])


    def ThreeDSwp_FilePathsGet(self):
        """
        3DSwp.FilePathsGet
        Returns the list of file paths for the data saved by one single measurement (i.e. 1D and 2D sweeps save one single file, whereas a 3D sweep saves as many files as points configured for Step Channel 2).

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - File paths size (int) is the size in bytes of the File paths string array
        - Number of file paths (int) defines the number of elements of the File paths string array
        - File paths (1D array string) returns the list of file paths. The size of each string item comes right before it
        as integer 32.
        - Error described in the Response message>Body section
        """
        return self.quickSend("3DSwp.FilePathsGet", [], [], ["i", "i", "*+c"])


    def OneDSwp_AcqChsSet(self, Channel_indexes: list, Channel_names: list):
        """
        1DSwp.AcqChsSet

        Arguments:

        - Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        - Channel indexes (1D array int) are the indexes of recorded channels. The indexes correspond to the list of Measurement in the Nanonis software.
        To get the Measurements names use the Signals.MeasNamesGet function

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("1DSwp.AcqChsSet", [Channel_indexes, Channel_names], ["+*i", "*+c"], [])


    def OneDSwp_AcqChsGet(self):
        """
        GenSwp.AcqChsGet
        Returns the list of recorded channels of the Generic Sweeper.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        -- Channel indexes (1D array int) are the indexes of the recorded channels. The indexes correspond to the list of Measurement in the Nanonis software.
        -	Channels names size (int) is the size in bytes of the Channels names string array
        -	Number of channels (int) is the number of elements of the Channels names string array
        -	Channels names (1D array string) returns the list of recorded channels names. The size of each string item comes right before it as integer 32
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("1DSwp.AcqChsGet", [], [], ["i", "*i", "i", "i", "*+c"])

    def OneDSwp_SwpSignalSet(self, SweepChannelName):
        """
        1DSwp.SwpSignalSet
        Sets the Sweep signal in the 1D Sweeper.

        Arguments:

        - Sweep channel name size (int) is the number of characters of the sweep channel name string
        - Sweep channel name (string) is the name of the signal selected for the sweep channel

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("1DSwp.SwpSignalSet", [SweepChannelName], ["+*c"], [])

    def OneDSwp_SwpSignalGet(self):
        """
        1DSwp.SwpSignalGet
        Returns the selected Sweep signal in the Generic Sweeper.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Sweep channel name size (int) is the number of characters of the sweep channel name string
        -- Sweep channel name (string) is the name of the signal selected for the sweep channel
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("1DSwp.SwpSignalGet", [], [], ["i", "*-c"])

    def OneDSwp_SwpSignalListGet(self):
        """
        1DSwp.SwpSignalListGet
        Returns the list of names of available signals to sweep in the Generic Sweeper.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -	Channels names size (int) is the size in bytes of the Channels names string array
        -	Number of channels (int) is the number of elements of the Channels names string array
        -	Channels names (1D array string) returns the list of channels names. The size of each string item comes right before it as integer 32
        -	Error described in the Response message>Body section

        """
        return self.quickSend("1DSwp.SwpSignalListGet", [], [], ["i", "i", "*+c"])

    def OneDSwp_LimitsSet(self, LowerLimit, UpperLimit):
        """
        1DSwp.LimitsSet
        Sets the limits of the Sweep signal in the 1D Sweeper.

        Arguments:
        - Lower limit (float32) defines the lower limit of the sweep range
        - Upper limit (float32) defines the upper limit of the sweep range

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("1DSwp.LimitsSet", [LowerLimit, UpperLimit], ["f", "f"], [])


    def OneDSwp_LimitsGet(self):
        """
        1DSwp.LimitsGet
        Returns the limits of the Sweep signal in the 1D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Lower limit (float32) defines the lower limit of the sweep range
        - Upper limit (float32) defines the upper limit of the sweep range
        - Error described in the Response message>Body section
        """
        return self.quickSend("1DSwp.LimitsGet", [], [], ["f", "f"])


    def OneDSwp_PropsSet(self, Initial_Settling_time_ms, Maximum_slew_rate_unitsdivs, Number_of_steps, Period_ms,
                        Autosave, Save_dialog_box, Settling_time_ms):
        """
        1DSwp.PropsSet
        Sets the configuration of the parameters in the 1D Sweeper.
        Arguments: 
        -- Initial Settling time (ms) (float32) 
        -- Maximum slew rate (units/s) (float32) 
        -- Number of steps (int) defines the number of steps of the sweep. 0 points means no change
        -- Period (ms) (unsigned int16) where 0 means no change
        -- Autosave (int) defines if the sweep is automatically saved, where 0=no change, 1=On, 2=Off
        -- Save dialog box (int) defines if the save dialog box shows up or not, where 0=no change, 1=On, 2=Off
        -- Settling time (ms) (float32) 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("1DSwp.PropsSet",
                              [Initial_Settling_time_ms, Maximum_slew_rate_unitsdivs, Number_of_steps, Period_ms,
                               Autosave, Save_dialog_box, Settling_time_ms], ["f", "f", "i", "H", "i", "i", "f"], [])


    def OneDSwp_PropsGet(self):
        """
        1DSwp.PropsGet
        Returns the configuration of the parameters in the 1D Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Initial Settling time (ms) (float32)
        - Maximum slew rate (units/s) (float32)
        - Number of steps (int) defines the number of steps of the sweep
        - Period (ms) (unsigned int16)
        - Autosave (unsigned int32) defines if the sweep is automatically saved, where 0=Off, 1=On
        - Save dialog box (unsigned int32) defines if the save dialog box shows up or not, where 0=Off, 1=On
        - Settling time (ms) (float32)
        - Error described in the Response message>Body section
        """
        return self.quickSend("1DSwp.PropsGet", [], [], ["f", "f", "i", "H", "I", "I", "f"])


    def OneDSwp_Start(self, GetData, SweepDirection, SaveBaseName, ResetSignal, DummyValue):
        """
        1DSwp.Start
        Starts the sweep in the 1D Sweeper.

        Arguments:

        - Get data (unsigned int32) defines if the function returns the sweep data (1=True) or not (0=False)
        - Sweep direction (unsigned int32) defines if the sweep starts from the lower limit (=1) or from the upper
        limit (=0)
        - Save base name string size (int) defines the number of characters of the Save base name string
        - Save base name (string) is the basename used by the saved files. If empty string, there is no change
        - Reset signal (unsigned int32) where 0=Off, 1=On
        - Dummy value (unsigned int16) used internally by the Nanonis software. It must be set to 0


        Return arguments (if Send response back flag is set to True when sending request message):


        - Channels names size (int) is the size in bytes of the Channels names string array
        - Number of channels (int) is the number of elements of the Channels names string array
        - Channels names (1D array string) returns the list of channels names. The size of each string item comes
        right before it as integer 32
        - Data rows (int) defines the numer of rows of the Data array
        - Data columns (int) defines the numer of columns of the Data array
        - Data (2D array float32) returns the sweep data
        - Error described in the Response message>Body section
        """
        return self.quickSend("1DSwp.Start", [GetData, SweepDirection, SaveBaseName, ResetSignal, DummyValue], ["I", "I", "+*c", "I", "H"], ["i", "i", "*+c", "i", "i", "2f"])


    def OneDSwp_Stop(self):
        """
        1DSwp.Stop
        Stops the sweep in the 1D Sweeper module.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("1DSwp.Stop", [], [], [])


    def OneDSwp_Open(self):
        """
        1DSwp.Open
        Opens the 1D Sweeper module.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("1DSwp.Open", [], [], [])

    def OneDSwp_ModeSet(self, Sweep_Mode):
        """
        1DSwp.ModeSet
        Sets the sweep mode in the 1D Sweeper, which defines how the sweeper should react to each new data point set during the sweep.
........Timed: Waits the amount of time set by the user (Settling Time) after setting a new sweep value using the Slew rate specified on the UI of the Sweeper.  Does not explicitly wait for the target device to reach the value set.
........Value Reached: Waits for feedback from the target device that the value set has actually been reached before starting integration.  Does not require a Sweeper Slew Rate setting.
........Continuous: After moving to start value, final value is set in one step and the measurement is performed continuously until the target has reached the specified value.

        Arguments:
        - Sweep mode (unsigned int16) where 0=Timed, 1=Value Reached, and 2=Continuous

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("1DSwp.ModeSet", [Sweep_Mode], ["H"], [])

    def OneDSwp_ModeGet(self):
        """
        1DSwp.ModeGet
        Returns the sweep mode in the 1D Sweeper, which defines how the sweeper should react to each new data point set during the sweep.
........Timed: Waits the amount of time set by the user (Settling Time) after setting a new sweep value using the Slew rate specified on the UI of the Sweeper.  Does not explicitly wait for the target device to reach the value set.
........Value Reached: Waits for feedback from the target device that the value set has actually been reached before starting integration.  Does not require a Sweeper Slew Rate setting.
........Continuous: After moving to start value, final value is set in one step and the measurement is performed continuously until the target has reached the specified value.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):
        - Sweep mode (unsigned int16) where 0=Timed, 1=Value Reached, and 2=Continuous
        - Error described in the Response message>Body section
        
        """
        return self.quickSend("1DSwp.ModeGet", [], [], ["H"])

    def LockIn_ModOnOffSet(self, Modulator_number, Lock_In_OndivOff):
        """
        LockIn.ModOnOffSet
        Turns the specified Lock-In modulator on or off.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        -- Lock-In On/Off (unsigned int32) turns the specified modulator on or off, where 0_Off and 1_On  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("LockIn.ModOnOffSet", [Modulator_number, Lock_In_OndivOff], ["i", "I"], [])

    def LockIn_ModOnOffGet(self, Modulator_number):
        """
        LockIn.ModOnOffGet
        Returns if the specified Lock-In modulator is turned on or off.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Lock-In On/Off (unsigned int32) returns if the specified modulator is turned on or off, where 0_Off and 1_On  
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModOnOffGet", [Modulator_number], ["i"], ["I"])

    def LockIn_ModSignalSet(self, Modulator_number, Modulator_Signal_Index):
        """
        LockIn.ModSignalSet
        Selects the modulated signal of  the specified Lock-In modulator.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        -- Modulator Signal Index (int) is the signal index out of the list of 128 signals available in the software.  
        To get a list of the available signals, use the <i>Signals.NamesGet</i> function.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        
        """
        return self.quickSend("LockIn.ModSignalSet", [Modulator_number, Modulator_Signal_Index], ["i", "i"], [])

    def LockIn_ModSignalGet(self, Modulator_number):
        """
        LockIn.ModSignalGet
        Returns the modulated signal of  the specified Lock-In modulator.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Modulator Signal Index (int) is the signal index out of the list of 128 signals available in the software.  
        To get a list of the available signals, use the <i>Signals.NamesGet</i> function 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModSignalGet", [Modulator_number], ["i"], ["i"])

    def LockIn_ModPhasRegSet(self, Modulator_number, Phase_Register_Index):
        """
        LockIn.ModPhasRegSet
        Sets the phase register index of the specified Lock-In modulator.
        Each modulator can work on any phase register (frequency). Use this function to assign the modulator to one of the 8 available phase registers (index 1-8). 
        Use the <i>LockIn.ModPhaFreqSet</i> function to set the frequency of the phase registers.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        -- Phase Register Index (int) is the index of the phase register of the specified Lock-In modulator. Valid values are index 1 to 8.  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModPhasRegSet", [Modulator_number, Phase_Register_Index], ["i", "i"], [])

    def LockIn_ModPhasRegGet(self, Modulator_number):
        """
        LockIn.ModPhasRegGet
        Returns the phase register index of the specified Lock-In modulator.
        Each modulator can work on any phase register (frequency generator). 
        Use the <i>LockIn.ModPhaseRegFreqGet</i> function to get the frequency of the phase registers.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Phase Register Index (int) is the index of the phase register of the specified Lock-In modulator. Valid values are index 1 to 8 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModPhasRegGet", [Modulator_number], ["i"], ["i"])

    def LockIn_ModHarmonicSet(self, Modulator_number, Harmonic_):
        """
        LockIn.ModHarmonicSet
        Sets the harmonic of the specified Lock-In modulator.
        The modulator is bound to a phase register (frequency generator), but it can work on harmonics. Harmonic 1 is the base frequency (the frequency of the frequency generator).
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        -- Harmonic  (int) is the harmonic of the specified Lock-In modulator. Valid values start from 1 (_base frequency)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModHarmonicSet", [Modulator_number, Harmonic_], ["i", "i"], [])

    def LockIn_ModHarmonicGet(self, Modulator_number):
        """
        LockIn.ModHarmonicGet
        Returns the harmonic of the specified Lock-In modulator.
        The modulator is bound to a phase register (frequency generator), but it can work on harmonics. Harmonic 1 is the base frequency (the frequency of the frequency generator).
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Harmonic  (int) is the harmonic of the specified Lock-In modulator. Valid values start from 1 (_base frequency)
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModHarmonicGet", [Modulator_number], ["i"], ["i"])

    def LockIn_ModPhasSet(self, Modulator_number, Phase_deg_):
        """
        LockIn.ModPhasSet
        Sets the modulation phase offset of the specified Lock-In modulator.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        -- Phase (deg)  (float32) is the modulation phase offset of the specified Lock-In modulator
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModPhasSet", [Modulator_number, Phase_deg_], ["i", "f"], [])

    def LockIn_ModPhasGet(self, Modulator_number):
        """
        LockIn.ModPhasGet
        Returns the modulation phase offset of the specified Lock-In modulator.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Phase (deg)  (float32) is the modulation phase offset of the specified Lock-In modulator
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModPhasGet", [Modulator_number], ["i"], ["f"])

    def LockIn_ModAmpSet(self, Modulator_number, Amplitude_):
        """
        LockIn.ModAmpSet
        Sets the modulation amplitude of the specified Lock-In modulator.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        -- Amplitude  (float32) is the modulation amplitude of the specified Lock-In modulator
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModAmpSet", [Modulator_number, Amplitude_], ["i", "f"], [])

    def LockIn_ModAmpGet(self, Modulator_number):
        """
        LockIn.ModAmpGet
        Returns the modulation amplitude of the specified Lock-In modulator.
        Arguments:
        -- Modulator number (int) is the number that specifies which modulator to use. It starts from number 1 (_Modulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Amplitude  (float32) is the modulation amplitude of the specified Lock-In modulator
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModAmpGet", [Modulator_number], ["i"], ["f"])

    def LockIn_ModPhasFreqSet(self, Modulator_number, Frequency_Hz_):
        """
        LockIn.ModPhasFreqSet
        Sets the frequency of the specified Lock-In phase register/modulator.
        The Lock-in module has a total of 8 frequency generators / phase registers. Each modulator and demodulator can be bound to one of the phase registers.
        This function sets the frequency of one of the phase registers.
        Arguments:
        -- Modulator number (int) is the number that specifies which phase register/modulator to use. It starts from number 1 (_Modulator 1)
        -- Frequency (Hz)  (float64) is the frequency of the specified Lock-In phase register
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        """
        return self.quickSend("LockIn.ModPhasFreqSet", [Modulator_number, Frequency_Hz_], ["i", "d"], [])

    def LockIn_ModPhasFreqGet(self, Modulator_number):
        """
        LockIn.ModPhasFreqGet
        Returns the frequency of the specified Lock-In phase register/modulator.
        The Lock-in module has a total of 8 frequency generators / phase registers. Each modulator and demodulator can be bound to one of the phase registers.
        This function gets the frequency of one of the phase registers.
        Arguments:
        -- Modulator number (int) is the number that specifies which phase register/modulator to use. It starts from number 1 (_Modulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Frequency (Hz)  (float64) is the frequency of the specified Lock-In phase register
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.ModPhasFreqGet", [Modulator_number], ["i"], ["d"])

    def LockIn_DemodSignalSet(self, Demodulator_number, Demodulator_Signal_Index):
        """
        LockIn.DemodSignalSet
        Selects the demodulated signal of  the specified Lock-In demodulator.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        -- Demodulator Signal Index (int) is the signal index out of the list of 128 signals available in the software.  
        To get a list of the available signals, use the <i>Signals.NamesGet</i> function.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodSignalSet", [Demodulator_number, Demodulator_Signal_Index], ["i", "i"], [])

    def LockIn_DemodSignalGet(self, Demodulator_number):
        """
        LockIn.DemodSignalGet
        Returns the demodulated signal of  the specified Lock-In demodulator.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Demodulator Signal Index (int) is the signal index out of the list of 128 signals available in the software.  
        To get a list of the available signals, use the <i>Signals.NamesGet</i> function 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodSignalGet", [Demodulator_number], ["i"], ["i"])

    def LockIn_DemodHarmonicSet(self, Demodulator_number, Harmonic_):
        """
        LockIn.DemodHarmonicSet
        Sets the harmonic of the specified Lock-In demodulator.
        The demodulator demodulates the input signal at the specified harmonic overtone of the frequency generator. Harmonic 1 is the base frequency (the frequency of the frequency generator).
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        -- Harmonic  (int) is the harmonic of the specified Lock-In demodulator. Valid values start from 1 (_base frequency)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodHarmonicSet", [Demodulator_number, Harmonic_], ["i", "i"], [])

    def LockIn_DemodHarmonicGet(self, Demodulator_number):
        """
        LockIn.DemodHarmonicGet
        Returns the harmonic of the specified Lock-In demodulator.
        The demodulator demodulates the input signal at the specified harmonic overtone of the frequency generator. Harmonic 1 is the base frequency (the frequency of the frequency generator).
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Harmonic  (int) is the harmonic of the specified Lock-In demodulator. Valid values start from 1 (_base frequency)
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("LockIn.DemodHarmonicGet", [Demodulator_number], ["i"], ["i"])

    def LockIn_DemodHPFilterSet(self, Demodulator_number, HP_Filter_Order, HP_Filter_Cutoff_Frequency_Hz):
        """
        LockIn.DemodHPFilterSet
        Sets the properties of the high-pass filter applied to the demodulated signal of the specified demodulator.
        The high-pass filter is applied on the demodulated signal before the actual demodulation. It is used to get rid of DC or low-frequency components which could result in undesired components close to the modulation frequency on the demodulator output signals (X,Y).
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        -- HP Filter Order (int) is the high-pass filter order. Valid values are from -1 to 8, where -1_no change, 0_filter off.
        -- HP Filter Cutoff Frequency (Hz) (float32) is the high-pass filter cutoff frequency in Hz, where 0 _ no change.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodHPFilterSet",
                              [Demodulator_number, HP_Filter_Order, HP_Filter_Cutoff_Frequency_Hz], ["i", "i", "f"], [])

    def LockIn_DemodHPFilterGet(self, Demodulator_number):
        """
        LockIn.DemodHPFilterGet
        Returns the properties of the high-pass filter applied to the demodulated signal of the specified demodulator.
        The high-pass filter is applied on the demodulated signal before the actual demodulation. It is used to get rid of DC or low-frequency components which could result in undesired components close to the modulation frequency on the demodulator output signals (X,Y).
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- HP Filter Order (int) is the high-pass filter order. Valid values are from 0 to 8, where 0_filter off
        -- HP Filter Cutoff Frequency (Hz) (float32) is the high-pass filter cutoff frequency in Hz
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodHPFilterGet", [Demodulator_number], ["i"], ["i", "f"])

    def LockIn_DemodLPFilterSet(self, Demodulator_number, LP_Filter_Order, LP_Filter_Cutoff_Frequency_Hz):
        """
        LockIn.DemodLPFilterSet
        Sets the properties of the low-pass filter applied to the demodulated signal of the specified demodulator.
        The low-pass filter is applied on the demodulator output signals (X,Y) to remove undesired components. Lower cut-off frequency means better suppression of undesired frequency components, but longer response time (time constant) of the filter. 
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        -- LP Filter Order (int) is the low-pass filter order. Valid values are from -1 to 8, where -1_no change, 0_filter off.
        -- LP Filter Cutoff Frequency (Hz) (float32) is the low-pass filter cutoff frequency in Hz, where 0 _ no change.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodLPFilterSet",
                              [Demodulator_number, LP_Filter_Order, LP_Filter_Cutoff_Frequency_Hz], ["i", "i", "f"], [])

    def LockIn_DemodLPFilterGet(self, Demodulator_number):
        """
        LockIn.DemodLPFilterGet
        Returns the properties of the low-pass filter applied to the demodulated signal of the specified demodulator.
        The low-pass filter is applied on the demodulator output signals (X,Y) to remove undesired components. Lower cut-off frequency means better suppression of undesired frequency components, but longer response time (time constant) of the filter. 
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- LP Filter Order (int) is the low-pass filter order. Valid values are from -1 to 8, where -1_no change, 0_filter off.
        -- LP Filter Cutoff Frequency (Hz) (float32) is the low-pass filter cutoff frequency in Hz, where 0 _ no change.
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodLPFilterGet", [Demodulator_number], ["i"], ["i", "f"])

    def LockIn_DemodPhasRegSet(self, Demodulator_number, Phase_Register_Index):
        """
        LockIn.DemodPhasRegSet
        Sets the phase register index of the specified Lock-In demodulator.
        Each demodulator can work on any phase register (frequency). Use this function to assign the demodulator to one of the 8 available phase registers (index 1-8). 
        Use the <i>LockIn.ModPhaFreqSet</i> function to set the frequency of the phase registers.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        -- Phase Register Index (int) is the index of the phase register of the specified Lock-In demodulator. Valid values are index 1 to 8.  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodPhasRegSet", [Demodulator_number, Phase_Register_Index], ["i", "i"], [])

    def LockIn_DemodPhasRegGet(self, Demodulator_number):
        """
        LockIn.DemodPhasRegGet
        Returns the phase register index of the specified Lock-In demodulator.
        Each demodulator can work on any phase register (frequency). Use the <i>LockIn.ModPhaFreqSet</i> function to set the frequency of the phase registers.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Phase Register Index (int) is the index of the phase register of the specified Lock-In demodulator. Valid values are index 1 to 8.  
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodPhasRegGet", [Demodulator_number], ["i"], ["i"])

    def LockIn_DemodPhasSet(self, Demodulator_number, Phase_deg_):
        """
        LockIn.DemodPhasSet
        Sets the reference phase of the specified Lock-In demodulator.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        -- Phase (deg)  (float32) is the reference phase of the specified Lock-In demodulator
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodPhasSet", [Demodulator_number, Phase_deg_], ["i", "f"], [])

    def LockIn_DemodPhasGet(self, Demodulator_number):
        """
        LockIn.DemodPhasGet
        Returns the reference phase of the specified Lock-In demodulator.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Phase (deg)  (float32) is the reference phase of the specified Lock-In demodulator
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodPhasGet", [Demodulator_number], ["i"], ["f"])

    def LockIn_DemodSyncFilterSet(self, Demodulator_number, Sync_Filter_):
        """
        LockIn.DemodSyncFilterSet
        Switches the synchronous (Sync) filter of the specified demodulator On or Off.
        The synchronous filter is applied on the demodulator output signals (X,Y) after the low-pass filter. It is very good in suppressing harmonic components (harmonics of the demodulation frequency), but does not suppress other frequencies.
        The sync filter does not output a continuous signal, it only updates the value after each period of the demodulation frequency.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        -- Sync Filter  (unsigned int32) switches the synchronous filter of the specified demodulator on or off, where 0_Off and 1_On  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodSyncFilterSet", [Demodulator_number, Sync_Filter_], ["i", "I"], [])

    def LockIn_DemodSyncFilterGet(self, Demodulator_number):
        """
        LockIn.DemodSyncFilterGet
        Returns the status (on/off) of the synchronous (Sync) filter of the specified demodulator.
        The synchronous filter is applied on the demodulator output signals (X,Y) after the low-pass filter. It is very good in suppressing harmonic components (harmonics of the demodulation frequency), but does not suppress other frequencies.
        The sync filter does not output a continuous signal, it only updates the value after each period of the demodulation frequency.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Sync Filter  (unsigned int32) is the synchronous filter of the specified demodulator, where 0_Off and 1_On  
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodSyncFilterGet", [Demodulator_number], ["i"], ["I"])

    def LockIn_DemodRTSignalsSet(self, Demodulator_number, RT_Signals_):
        """
        LockIn.DemodRTSignalsSet
        Sets the signals available for acquisition on the real-time system from the specified demodulator.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        -- RT Signals  (unsigned int32) sets which signals from the specified demodulator should be available on the Real-time system. 0 sets the available RT Signals to X/Y, 1 sets them to R/phi.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockIn.DemodRTSignalsSet", [Demodulator_number, RT_Signals_], ["i", "I"], [])

    def LockIn_DemodRTSignalsGet(self, Demodulator_number):
        """
        LockIn.DemodRTSignalsGet
        Returns which the signals are available for acquisition on the real-time system from the specified demodulator.
        Arguments:
        -- Demodulator number (int) is the number that specifies which demodulator to use. It starts from number 1 (_Demodulator 1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        -- RT Signals  (unsigned int32) returns which signals from the specified demodulator are available on the Real-time system. 0 means X/Y, and 1 means R/phi.
        -- Error described in the Response message&gt;Body section
        
        Lock-In Frequency Sweep
        """
        return self.quickSend("LockIn.DemodRTSignalsGet", [Demodulator_number], ["i"], ["I"])

    def LockInFreqSwp_Open(self):
        """
        LockInFreqSwp.Open
        Opens the Transfer function (Lock-In Frequency Sweep) module.
        The transfer function does not run when its front panel is closed. To automate measurements it might be required to open the module first using this VI.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockInFreqSwp.Open", [], [], [])

    def LockInFreqSwp_Start(self, Get_Data, Direction):
        """
        LockInFreqSwp.Start
        Starts a Lock-In frequency sweep.
        Arguments:
        -- Get Data (unsigned int32) defines if the function returns the recorder channels and data
        -- Direction (unsigned int32) sets the direction of the frequency sweep. 0 means sweep down (from upper limit to lower limit) and 1 means sweep up (from lower limit to upper limit)
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Channels names size (int) is the size in bytes of the recorder channels  names array
        -- Channels names number (int) is the number of elements of the recorded channels names array
        -- Channels names (1D array string) returns the array of recorded channel names (strings), where each string comes prepended by its size in bytes
        -- Data rows (int) is the number of rows of the returned data array (the first row is the swept frequency, and each additional row contains the data of each recorded channel )
        -- Data columns (int) is the number of recorded points (number of steps plus 1)
        -- Data (2D array float32) returns the recorded data. The number of rows is defined by <i>Data rows</i>, and the number of columns is defined by <i>Data columns</i>
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("LockInFreqSwp.Start", [Get_Data, Direction], ["I", "I"],
                              ["i", "i", "*+c", "i", "i", "2f"])

    def LockInFreqSwp_SignalSet(self, Sweep_signal_index):
        """
        LockInFreqSwp.SignalSet
        Sets the sweep signal used in the Lock-In frequency sweep module.
        Arguments:
        -- Sweep signal index (int) sets the sweep signal index out of the list of sweep signals to use, where -1 means no signal selected
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockInFreqSwp.SignalSet", [Sweep_signal_index], ["i"], [])

    def LockInFreqSwp_SignalGet(self):
        """
        LockInFreqSwp.SignalGet
        Returns the sweep signal used in the Lock-In frequency sweep module.
        Arguments:
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Sweep signal index (int) is the sweep signal index selected out of the list of sweep signals, where -1 means no signal selected
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockInFreqSwp.SignalGet", [], [], ["i"])

    def LockInFreqSwp_LimitsSet(self, Lower_limit_Hz, Upper_limit_Hz):
        """
        LockInFreqSwp.LimitsSet
        Sets the frequency limits in the Lock-In frequency sweep module.
        Arguments:
        -- Lower limit (Hz) (float32) sets the lower frequency limit in Hz
        -- Upper limit (Hz) (float32) sets the lower frequency limit in Hz
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockInFreqSwp.LimitsSet", [Lower_limit_Hz, Upper_limit_Hz], ["f", "f"], [])

    def LockInFreqSwp_LimitsGet(self):
        """
        LockInFreqSwp.LimitsGet
        Returns the frequency limits in the Lock-In frequency sweep module.
        Arguments:
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Lower limit (Hz) (float32) is the lower frequency limit in Hz
        -- Upper limit (Hz) (float32) is the lower frequency limit in Hz
        -- Error described in the Response message&gt;Body section
        """
        return self.quickSend("LockInFreqSwp.LimitsGet", [], [], ["f", "f"])

    def LockInFreqSwp_PropsSet(self, Number_of_steps, Integration_periods, Minimum_integration_time_s, Settling_periods,
                               Minimum_Settling_time_s, Autosave, Save_dialog, Basename):
        """
        LockInFreqSwp.PropsSet
        Sets the configuration of the Transfer Function (Lock-In frequency sweep) module.
        Arguments:
        -- Number of steps (unsigned int16) is the number of frequency steps over the sweep range (logarithmic distribution). The number of data points _ number of steps + 1. If set to 0, the number of steps is left unchanged
        -- Integration periods (unsigned int16) is the number of Lock in periods to average for one measurement. 
        -- Minimum integration time (s) (float32) is the minimum integration time in seconds to average each measurement
        -- Settling periods (unsigned int16) is the number of Lock in periods to wait before acquiring data at each point of the sweep
        -- Minimum Settling time (s) (float32) is the minimum settling time in seconds to wait before acquiring data at each point of the sweep
        -- Autosave (unsigned int32) automatically saves the data at end of sweep
        -- Save dialog (unsigned int32) will open a dialog box when saving the data
        -- Basename size (int) is the size (number of characters) of the basename string
        -- Basename (string) is the basename of the saved files
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("LockInFreqSwp.PropsSet",
                              [Number_of_steps, Integration_periods, Minimum_integration_time_s, Settling_periods,
                               Minimum_Settling_time_s, Autosave, Save_dialog, Basename],
                              ["H", "H", "f", "H", "f", "I", "I", "+*c"], [])

    def LockInFreqSwp_PropsGet(self):
        """
        LockInFreqSwp.PropsGet
        Returns the configuration of the Transfer Function (Lock-In frequency sweep) module.
        Arguments:
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Number of steps (unsigned int16) is the number of frequency steps over the sweep range (logarithmic distribution). The number of data points _ number of steps + 1
        -- Integration periods (unsigned int16) is the number of Lock in periods to average for one measurement. 
        -- Minimum integration time (s) (float32) is the minimum integration time in seconds to average each measurement
        -- Settling periods (unsigned int16) is the number of Lock in periods to wait before acquiring data at each point of the sweep
        -- Minimum Settling time (s) (float32) is the minimum settling time in seconds to wait before acquiring data at each point of the sweep
        -- Autosave (unsigned int32) automatically saves the data at end of sweep
        -- Save dialog (unsigned int32) will open a dialog box when saving the data
        -- Basename size (int) is the size (number of characters) of the basename string
        -- Basename (string) is the basename of the saved files
        -- Error described in the Response message&gt;Body section
        
        PLL modules
        """
        return self.quickSend("LockInFreqSwp.PropsGet", [], [], ["H", "H", "f", "H", "f", "I", "I", "i", "*-c"])

    def Script_Open(self):
        """
        Script.Open
        Opens the Script module.
        Arguments: None
        
        Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section
        
        
        """
        return self.quickSend("Script.Open", [], [], [])

    def Script_Load(self, Script_index, Script_file_path, Load_session):
        """
        Script.Load
        Loads a script in the script module.
        Arguments:
        -- Script index (int) sets the slot where the script will be loaded and covers a range from 1 (first script) to the 
            total number of scripts. A value of -1 sets the currently selected script slot.
        -- Script file path size (int) is the number of characters of the script file path string
        -- Script file path (string) is the path of the script file to load
        -- Load session (unsigned int32) automatically loads the scripts from the session file bypassing the script file path argument, where 0_False and 1_True  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("Script.Load", [Script_index, Script_file_path, Load_session], ["i","+*c", "I"],
                              [])

    def Script_Save(self, Script_index, Script_file_path, Save_session):
        """
        Script.Save
        Saves the current script in the specified .ini file.
        Arguments:
        -- Script index (int) sets the slot where the script will be loaded and covers a range from 1 (first script) to the 
            total number of scripts. A value of -1 sets the currently selected script slot.
        -- Script file path size (int) is the number of characters of the script file path string
        -- Script file path (string) is the path of the script file to save
        -- Save session (unsigned int32) automatically saves the current script into the session file bypassing the script file path argument, where 0_False and 1_True  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("Script.Save", [Script_index, Script_file_path, Save_session], ["i","+*c", "I"],
                              [])

    def Script_Deploy(self, Script_index):
        """
        Script.Deploy
        Deploys a script in the script module.
        Arguments: 
        -- Script index (int) sets the script to deploy and covers a range from 1 (first script) to the total number of scripts. A value of -1 sets the currently selected script to deploy.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Script.Deploy", [Script_index], ["i"], [])

    def Script_Undeploy(self, Script_index):
        """
        Script.Undeploy
        Undeploys a script in the script module.
        Arguments: 
        -- Script index (int) sets the script to undeploy and covers a range from 1 (first script) to the total number of scripts. A value of -1 sets the currently selected script to undeploy.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Script.Undeploy", [Script_index], ["i"], [])

    def Script_Run(self, Script_index, Wait_until_script_finishes):
        """
        Script.Run
        Runs a script in the script module.
        Arguments: 
        -- Script index (int) sets the script to run and covers a range from 1 (first script) to the total number of scripts. A value of -1 sets the currently selected script to run.
        -- Wait until script finishes (unsigned int32), where 0_False and 1_True 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Script.Run", [Script_index, Wait_until_script_finishes], ["i", "I"], [])

    def Script_Stop(self):
        """
        Script.Stop
        Stops the running script in the script module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("Script.Stop", [], [], [])

    def Script_ChsGet(self, Acquire_buffer):
        """
        Script.ChsGet
        Returns the list of acquired channels in the Script module.
        Arguments: 
        -- Acquire buffer (unsigned int16) sets the Acquire Buffer number from which to read the list of channels. Valid values are 1 (_Acquire Buffer 1) and 2 (_Acquire Buffer 2).
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        -- Channel indexes (1D array int) are the indexes of recorded channels. The indexes are comprised between 0 and 23 for the 24 signals assigned in the Signals Manager.
        To get the signal name and its corresponding index in the list of the 128 available signals in the Nanonis Controller, use the <i>Signals.InSlotsGet</i> function
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("Script.ChsGet", [Acquire_buffer], ["H"], ["i", "*i"])

    def Script_ChsSet(self, Acquire_buffer, Channel_indexes):
        """
        Script.ChsSet
        Sets the list of acquired channels in the Script module.
        Arguments: 
        -- Acquire buffer (unsigned int16) sets the Acquire Buffer number from which to set the list of channels. Valid values are 1 (_Acquire Buffer 1) and 2 (_Acquire Buffer 2).
        -- Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        -- Channel indexes (1D array int) are the indexes of recorded channels. The indexes are comprised between 0 and 23 for the 24 signals assigned in the Signals Manager.
        To get the signal name and its corresponding index in the list of the 128 available signals in the Nanonis Controller, use the <i>Signals.InSlotsGet</i> function
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Script.ChsSet", [Acquire_buffer, Channel_indexes], ["H", "+*i"],
                              [])

    def Script_DataGet(self, Acquire_buffer, Sweep_number):
        """
        Script.DataGet
        Returns the data acquired in the Script module.
        Arguments: 
        -- Acquire buffer (unsigned int16) sets the Acquire Buffer number from which to read the acquired data. Valid values are 1 (_Acquire Buffer 1) and 2 (_Acquire Buffer 2).
        -- Sweep number (int) selects the sweep this function will return the data from. Each sweep is configured as such in the script and it corresponds to each plot displayed in the graphs of the Script module. The sweep numbers start at 0.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Data rows (int) defines the number of rows of the Data array
        -- Data columns (int) defines the number of columns of the Data array
        -- Data (2D array float32) returns the script data
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("Script.DataGet", [Acquire_buffer, Sweep_number], ["H", "i"], ["i", "i", "2f"])

    def Script_Autosave(self, Acquire_buffer, Sweep_number, All_sweeps_to_same_file, Folder_path, Basename):
        """
        Script.Autosave
        Saves automatically to file the data stored in the Acquire Buffers after running a script in the Script module.
        Arguments: 
        -- Acquire buffer (unsigned int16) sets the Acquire Buffer number from which to save the data. 
        Valid values are 0 (_Acquire Buffer 1 & Acquire Buffer 2), 1 (_Acquire Buffer 1), and 2 (_Acquire Buffer 2).
        -- Sweep number (int) selects the sweep this function will save the data for. 
        Each sweep is configured as such in the script and it corresponds to each plot displayed in the graphs of the Script module. 
        The sweep numbers start at 0. A value of -1 saves all acquired sweeps.
        -- All sweeps to same file (unsigned int32) decides if all sweeps defined by the Sweep number parameter are saved to the same file (_1) or not (_0).
        - Folder path path size (int) is the number of characters of the folder path string
        - Folder path (string) is the folder where the file will be saved. If nothing is sent, the saving routine uses the 
            last used path.
        - Basename path size (int) is the number of characters of the basename string
        - Basename (string) is the basename of the file to save. If nothing is sent, the saving routine uses the last 
            used basename.

        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        Interferometer
        """
        return self.quickSend("Script.Autosave", [Acquire_buffer, Sweep_number, All_sweeps_to_same_file, Folder_path, Basename],
                              ["H", "i", "I", "+*c", "+*c"], [])

    def Script_LUTOpen(self):
        """
        Script.LUTOpen
        Opens the LUT (Look Up Table) Editor from the Script module.
        Arguments: None
        
        Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section
        
        
        """
        return self.quickSend("Script.LUTOpen", [], [], [])

    def Script_LUTLoad(self, Script_index, Script_file_path, LUT_Values):
        """
        Script.LUTLoad
        Loads a LUT from file or directly by setting an array of values into the LUT Editor in the script module.
        Arguments: 
        - LUT index (int) sets the LUT to load and covers a range from 1 (first LUT) to the total number of LUTs
        - File path size (int) is the number of characters of the File path string
        - File path (string) is the path of the file containing a list of values to load into the selected LUT. The 
            extension of the file must be .luts. If nothing is sent, it will use the values sent by the LUT values argument.
        - LUT values size (int) is the size of the LUT values array
        - LUT values (1D array float32)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("Script.LUTLoad", [Script_index, Script_file_path, LUT_Values], ["i","+*c", "*f"],
                              [])

    def Script_LUTSave(self, Script_index, Script_file_path):
        """
        Script.LUTSave
        Saves a LUT to file.
        Arguments: 
        - LUT index (int) sets the LUT to save and covers a range from 1 (first LUT) to the total number of LUTs
        - File path size (int) is the number of characters of the File path string
        - File path (string) is the path of the file where the selected LUT will be saved. The extension of the file 
            must be .luts
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("Script.LUTSave", [Script_index, Script_file_path], ["i","+*c"],
                              [])

    def Script_LUTDeploy(self, Script_index, Wait_until_finished, Timeout_ms):
        """
        Script.LUTDeploy
        Deploys a LUT from the LUT Editor in the script module.
        Arguments: 
        - LUT index (int) sets the LUT to deploy and covers a range from 1 (first LUT) to the total number of LUTs
        - Wait until finished (unsigned int32) decides if the function waits until the LUT is fully deployed, as it 
            might take some time.
        - Timeout (ms) (int) sets the number of milliseconds to wait until the LUT is fully deployed. -1 waits 
            forever.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Script.LUTDeploy", [Script_index, Wait_until_finished, Timeout_ms], ["i", "I", "i"], [])

    def HSSwp_AcqChsSet(self, Channel_Indexes:list):
        """
        HSSwp.AcqChsSet
        Sets the list of recorded channels of the High-Speed Sweeper.

        Arguments:

        - Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        - Channel indexes (1D array int) are the indexes of recorded channels.
        To obtain a list of the available channels, use the HSSwp.AcqChsGet function.

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("HSSwp.AcqChsSet", [Channel_Indexes], ["+*i"], [])

    def HSSwp_AcqChsGet(self):
        """
        HSSwp.AcqChsGet
        Returns the list of recorded channels of the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        - Channel indexes (1D array int) are the indexes of the recorded channels. The indexes correspond to the indices in the Available Channels indexes array.
        - Available Channels names size (int) is the size in bytes of the available channels names array
        - Available Channels names number (int) is the number of elements of the available channels names array
        - Available Channels names (1D array string) returns an array of channel names strings, where each string
        comes prepended by its size in bytes
        - Number of available channels (int) is the number of available channels. It defines the size of the
        Available Channels indexes array
        - Available Channels indexes (1D array int) are the indexes of channels available for acquisition.
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.AcqChsGet", [], [], ["i", "*I", "i", "i", "*+c", "i", "*i"])

    def HSSwp_AutoReverseSet(self, OnOff, Condition, Signal, Threshold, LinkToOne, Condition2, Signal2, Threshold2):
        """
        HSSwp.AutoReverseSet
        Sets the auto-reverse configuration of the sweep axis in the High-Speed Sweeper.

        Arguments:

        - On/Off (int) defines if the auto-reverse functionality is on or off, where 0=Off, 1=On
        - Condition (int) defines if the signal must be greater or less than the threshold for the reverse condition to
        activate, where 0 = >, 1 = <
        - Signal (int) sets the signal for the reverse condition. The list of available signals is the same as the
        acquisition signals (see HSSwp.AcqChsGet function).
         - Threshold (float32) defines the threshold to which the signal is compared.
        - Linkage to 1 (int) defines the linkage of the 2nd reverse condition to the first condition. Possible values: 0 =
        Off (no 2nd condition), 1 = OR (condition 1 or 2 must be met), 2 = AND (conditions 1 and 2 must be met at
        the same time), 3 = THEN (condition 1 must be met first, then condition 2).
        - Condition 2 (int) defines if the signal must be greater or less than the threshold for the 2nd reverse condition
        to activate, where 0 = >, 1 = <
        - Signal 2 (int) sets the signal for the 2nd reverse condition. The list of available signals is the same as the
        acquisition signals (see HSSwp.AcqChsGet function).
        - Threshold 2 (float32) defines the threshold to which the signal 2 is compared.

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("HSSwp.AutoReverseSet",
                              [OnOff, Condition, Signal, Threshold, LinkToOne, Condition2, Signal2, Threshold2],
                              ["i", "i", "i", "f", "i", "i", "i", "f"], [])

    def HSSwp_AutoReverseGet(self):
        """
        HSSwp.AutoReverseGet
        Returns the auto-reverse configuration of the sweep axis in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - On/Off (int) specifies if the auto-reverse functionality is on or off, where 0=Off, 1=On
        - Condition (int) specifies if the signal must be greater or less than the threshold for the reverse condition to
        activate, where 0 = >, 1 = <
        - Signal (int) is the signal for the reverse condition. The list of available signals is the same as the acquisition
        signals (see HSSwp.AcqChsGet function).
        - Threshold (float32) is the threshold to which the signal is compared.
        - Linkage to 1 (int) specifies the linkage of the 2nd reverse condition to the first condition. Possible values: 0
        = Off (no 2nd condition), 1 = OR (condition 1 or 2 must be met), 2 = AND (conditions 1 and 2 must be met
        at the same time), 3 = THEN (condition 1 must be met first, then condition 2).
        - Condition 2 (int) specifies if the signal must be greater or less than the threshold for the 2nd reverse
        condition to activate, where 0 = >, 1 = <
        - Signal 2 (int) is the signal for the 2nd reverse condition. The list of available signals is the same as the
        acquisition signals (see HSSwp.AcqChsGet function).
        - Threshold 2 (float32) is the threshold to which the signal 2 is compared.
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.AutoReverseGet", [], [], ["i", "i", "i", "f", "i", "i", "i", "f"])

    def HSSwp_EndSettlSet(self, Threshold):
        """
        HSSwp.EndSettlSet
        Sets the end settling time in the High-Speed Sweeper.

        Arguments:

        - Threshold (float32) defines the end settling time in seconds

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.EndSettlSet", [Threshold], ["f"], [])

    def HSSwp_EndSettlGet(self):
        """
        HSSwp.EndSettlGet
        Returns the end settling time in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Threshold (float32) is the end settling time in seconds
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.EndSettlGet", [], [], ["f"])

    def HSSwp_NumSweepsSet(self, Number_Of_Sweeps, Continuous):
        """
        HSSwp.NumSweepsSet
        Sets the number of sweeps in the High-Speed Sweeper.

        Arguments:
        - Number of sweeps (unsigned int32) sets the number of sweeps (ignored when continuous is set)
        - Continuous (int) sets the continuous sweep mode, where 0=Off, 1=On

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.NumSweepsSet", [Number_Of_Sweeps, Continuous], ["I", "i"], [])

    def HSSwp_NumSweepsGet(self):
        """
        HSSwp.NumSweepsGet
        Returns the number of sweeps in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Number of sweeps (unsigned int32) is the number of sweeps
        - Continuous (int) specifies the continuous sweep mode, where 0=Off, 1=On
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.NumSweepsGet", [], [], ["I", "i"])

    def HSSwp_ResetSignalsSet(self, ResetSignals):
        """
        HSSwp.ResetSignalsSet
        Specifies if the sweep and step signals should be reset to their initial values at the end of the sweep in the High- Speed Sweeper.

        Arguments:

        - Reset Signals (int) defines if the sweep and step signals are reset at the end of the sweep, where 0=Off, 1=On

        Return arguments (if Send response back flag is set to True when sending request message):

         - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.ResetSignalsSet", [ResetSignals], ["i"], [])

    def HSSwp_ResetSignalsGet(self):
        """
        HSSwp.ResetSignalsGet
        Returns if the sweep and step signals are reset to their initial values at the end of the sweep in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Reset Signals (int) returns if the sweep and step signals are reset at the end of the sweep, where 0=Off, 1=On
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.ResetSignalsGet", [], [], ["i"])

    def HSSwp_SaveBasenameSet(self, Basename, Path):
        """
        HSSwp.SaveBasenameSet
        Sets the save basename in the High-Speed Sweeper.

        Arguments:

        - Basename size (int) is the size (number of characters) of the basename string
        - Basename (string) is the base name used for the saved sweeps
        - Path size (int) is the size (number of characters) of the path string
        - Path (string) is the path used for the saved sweeps


        Return arguments (if Send response back flag is set to True when sending request message to the server):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SaveBasenameSet", [Basename, Path], ["+*c", "+*c"], [])

    def HSSwp_SaveBasenameGet(self):
        """

        HSSwp.SaveBasenameGet
        Returns the save basename in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message to the server):

        - Basename size (int) is the size (number of characters) of the basename string
        - Basename (string) is the base name used for the saved sweeps
        - Path size (int) is the size (number of characters) of the path string
        - Path (string) is the path used for the saved sweeps
        - Error described in the Response message>Body section

        """
        return self.quickSend("HSSwp.SaveBasenameGet", [], [], ["i", "*-c", "*-c"])

    def HSSwp_SaveDataSet(self, SaveData):
        """
        HSSwp.SaveDataSet

        Specifies if the data acquired in the High-Speed Sweeper is saved or not.

        Arguments:

        - Save Data (int) defines if the data is saved, where 0=Off, 1=On

         Return arguments (if Send response back flag is set to True when sending request message):

         - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SaveDataSet", [SaveData], ["i"], [])

    def HSSwp_SaveDataGet(self):
        """
        HSSwp.SaveDataGet
        Returns if the data acquired in the High-Speed Sweeper is saved or not.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Save Data (int) returns if the data is saved, where 0=Off, 1=On
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SaveDataGet", [], [], ["i"])

    def HSSwp_SaveOptionsSet(self, Comment, ModulesNames):
        """
        HSSwp.SaveOptionsSet
        Sets save options in the High-Speed Sweeper.

        Arguments:
        - Comment size (int) is the size (number of characters) of the comment string
        - Comment (string) is the comment saved in the header of the files. If empty string, there is no change
        - Modules names size (int) is the size in bytes of the modules array. These are the modules whose
        parameters are saved in the header of the files
        - Modules names number (int) is the number of elements of the modules names array
        - Modules names (1D array string) is an array of modules names strings, where each string comes
        prepended by its size in bytes

        """
        return self.quickSend("HSSwp.SaveOptionsSet", [Comment, ModulesNames], ["+*c", "+*c"], [])

    def HSSwp_SaveOptionsGet(self):
        """
        HSSwp.SaveOptionsGet
        Returns the saving options of the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message to the server):

        - Comment size (int) is the size (number of characters) of the comment string
        - Comment (string) is the comment saved in the header of the files
        - Modules parameters size (int) is the size in bytes of the modules parameters array. These are the modules
        parameters saved in the header of the files
        - Modules parameters number (int) is the number of elements of the modules parameters array
        - Modules parameters (1D array string) is an array of modules names strings, where each string comes
        prepended by its size in bytes.
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SaveOptionsGet", [], [], ["i", "*-c", "i", "i", "*+c"])

    def HSSwp_Start(self, Wait_Until_Done, Timeout):
        """
        HSSwp.Start
        Starts a sweep in the High-Speed Sweeper module.
        When Send response back is set to True, it returns immediately afterwards.

        Arguments:

        - Wait until done (int) specifies whether the function waits with sending back the return arguments until the sweep is finished, where 0=Off (don’t wait), 1=On (wait)
        - Timeout (int) sets the wait timeout in milliseconds. Use -1 for indefinite wait. The Timeout is ignored when wait until done is off.

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.Start", [Wait_Until_Done, Timeout], ["i", "i"], [])

    def HSSwp_Stop(self):
        """
        HSSwp.Stop
        Stops the sweep in the High-Speed Sweeper module.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.Stop", [], [], [])

    def HSSwp_StatusGet(self):
        """
        HSSwp.StatusGet
        Returns the status of the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Status (unsigned int32) is status of the High-Speed Sweeper, where 0=Stopped, 1=Running
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.StatusGet", [], [], ["I"])

    def HSSwp_SwpChSigListGet(self):
        """
        HSSwp.SwpChSigListGet
        Returns the list of available signals for the Sweep channel of the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message to the server):

        - Signal names size (int) is the size in bytes of the signal names array
        - Signal names number (int) is the number of elements of the signal names array
         - Signal names (1D array string) is an array of signal names strings, where each string comes prepended by its size in bytes.
        - Number of signals (int) is the number of available sweep signals. It defines the size of the Available Channels indexes array
        - Signal indexes (1D array int) are the indexes of signals available for the sweep channel.
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChSigListGet", [], [], ["+*c", "+*i"])

    def HSSwp_SwpChSignalSet(self, Sweep_Signal_Index, Timed_Sweep):
        """
        HSSwp.SwpChSignalSet
        Sets the Sweep Channel signal in the High-Speed Sweeper.

        Arguments:

        - Sweep signal index (int) is the index of the Sweep Signal. Use the HSSwp.SwpChSigListGet function to obtain a list of available sweep signals.
        - Timed Sweep (int) enables or disables timed sweep mode. When on, the Sweep channel is ignored. 0=Off (sweep signal), 1=On (timed sweep)

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChSignalSet", [Sweep_Signal_Index, Timed_Sweep], ["i", "i"], [])

    def HSSwp_SwpChSignalGet(self):
        """
        HSSwp.SwpChSignalGet
        Returns the Sweep Channel signal in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Sweep signal index (int) is the index of the Sweep Signal. Use the HSSwp.SwpChSigListGet function to obtain a list of available sweep signals.
        - Timed Sweep (int) specifies if timed sweep mode is enabled, where 0=Off (sweep signal), 1=On (timed sweep)
        - Error described in the Response message>Body section

        """
        return self.quickSend("HSSwp.SwpChSignalGet", [], [], ["i", "i"])

    def HSSwp_SwpChLimitsSet(self, Relative_Limits, Start, Stop):
        """
        HSSwp.SwpChLimitsSet
        Sets the limits of the Sweep Channel in the High-Speed Sweeper.

        Arguments:

        - Relative Limits (int) specifies if the limits are absolute or relative to the current sweep signal value. Possible values are 0=Absolute limits, 1=Relative limits.
        - Start (float32) defines the value where the sweep starts
        - Stop (float32) defines the value where the sweep stops

        Return arguments (if Send response back flag is set to True when sending request message):

         - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChLimitsSet", [Relative_Limits, Start, Stop], ["i", "f", "f"], [])

    def HSSwp_SwpChLimitsGet(self):
        """
        HSSwp.SwpChLimitsGet
        Returns the limits of the Sweep Channel in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Relative Limits (int) specifies if the limits are absolute or relative to the current sweep signal value. Possible values are 0=Absolute limits, 1=Relative limits.
        - Start (float32) defines the value where the sweep starts
        - Stop (float32) defines the value where the sweep stops
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChLimitsGet", [], [], ["i", "f", "f"])

    def HSSwp_SwpChNumPtsSet(self, Number_Of_Points):
        """
        HSSwp.SwpChNumPtsSet
        Sets the number of points for the Sweep Channel in the High-Speed Sweeper.

        Arguments:

        - Number of points (unsigned int32) sets the number of points of the sweep.

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChNumPtsSet", [Number_Of_Points], ["I"], [])

    def HSSwp_SwpChNumPtsGet(self):
        """
        HSSwp.SwpChNumPtsGet
        Returns the number of points for the Sweep Channel in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Number of points (int) returns the number of points of the sweep
        - Error described in the Response message>Body section

        """
        return self.quickSend("HSSwp.SwpChNumPtsGet", [], [], ["i"])

    def HSSwp_SwpChTimingSet(self, Initial_Settling_Time, Settling_Time, Integration_Time, Max_Slew_Time):
        """
        HSSwp.SwpChTimingSet
        Sets the timing parameters of the Sweep Channel in the High-Speed Sweeper.

        Arguments:

        - Initial settling time (s) (float32)
        - Settling time (s) (float32)
         - Integration time (s) (float32)
        - Maximum slew rate (units/s) (float32)

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChTimingSet", [Initial_Settling_Time, Settling_Time, Integration_Time, Max_Slew_Time],
                              ["f", "f", "f", "f"], [])

    def HSSwp_SwpChTimingGet(self):
        """
        HSSwp.SwpChTimingGet
        Returns the timing parameters of the Sweep Channel in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Initial settling time (s) (float32)
        - Settling time (s) (float32)
        - Integration time (s) (float32)
        - Maximum slew rate (units/s) (float32)
        - Error described in the Response message>Body section

        """
        return self.quickSend("HSSwp.SwpChTimingGet", [], [], ["f", "f", "f", "f"])

    def HSSwp_SwpChBwdSwSet(self, Bwd_Sweep):
        """
        HSSwp.SwpChBwdSwSet
        Enables or disables the backward sweep for the sweep channel in the High-Speed Sweeper.

        Arguments:

        - Bwd Sweep (unsigned int32) defines if the backward sweep is enabled, where 0=Off, 1=On

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChBwdSwSet", [Bwd_Sweep], ["I"], [])

    def HSSwp_SwpChBwdSwGet(self):
        """
        HSSwp.SwpChBwdSwGet
        Returns if the backward sweep of the sweep channel in the High-Speed Sweeper is enabled or not.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Bwd Sweep (unsigned int32) specifies if the backward sweep is enabled, where 0=Off, 1=On
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChBwdSwGet", [], [], ["I"])

    def HSSwp_SwpChBwdDelaySet(self, Bwd_Delay):
        """
        HSSwp.SwpChBwdDelaySet
        Sets the delay between forward and backward sweep of the sweep channel in the High-Speed Sweeper.
         Arguments:

        - Bwd Delay (float32) sets the delay between forward and backward sweep in seconds.

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChBwdDelaySet", [Bwd_Delay], ["f"], [])

    def HSSwp_SwpChBwdDelayGet(self):
        """
        HSSwp.SwpChBwdDelayGet
        Returns the delay between forward and backward sweep of the sweep channel in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Bwd Delay (float32) is the delay between forward and backward sweep in seconds
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.SwpChBwdDelayGet", [], [], ["f"])

    def HSSwp_ZCtrlOffSet(self, Z_Controller_Off, Z_Controller_Index, Z_Averaging_Time, Z_Offset, Z_Control_Time):
        """
        HSSwp.ZCtrlOffSet
        Sets the Z-Controller behavior for the duration of the sweep in the High-Speed Sweeper.

        Arguments:
        - Z-Controller Off (int) defines if the Z-Controller should be switched off during the sweep, where -1=no change, 0=switch off, 1=don’t switch
        - Z-Controller index (int) specifies which Z-Controller to switch off, where 0=no change, 1=Z-Controller of tip 1, 2-4=Z-Controllers tips 2-4 (multiprobe systems only)
        - Z Averaging Time (float32) sets the time (in seconds) to average the Z position before switching off the Z- controller
        - Z Offset (float32) sets the Z offset (in meters) by which the tip is retracted after switching off the controller
        - Z Control Time (float32) sets the time (in seconds) to wait after switching the Z-Controller back on (in
        case it was switched off)

        Return arguments (if Send response back flag is set to True when sending request message):

        - Error described in the Response message>Body section

        """
        return self.quickSend("HSSwp.ZCtrlOffSet",
                              [Z_Controller_Off, Z_Controller_Index, Z_Averaging_Time, Z_Offset, Z_Control_Time],
                              ["i", "i", "f", "f", "f"], [])

    def HSSwp_ZCtrlOffGet(self):
        """
        HSSwp.ZCtrlOffGet
        Returns the Z-Controller behavior for the duration of the sweep in the High-Speed Sweeper.

        Arguments: None

        Return arguments (if Send response back flag is set to True when sending request message):

        - Z-Controller Off (int) defines if the Z-Controller is switched off during the sweep, where 0=switch off, 1=don’t switch
        - Z-Controller Index (int) defines which Z-Controller is switched off during the sweep, where 1=Z- Controller of tip 1, 2-4=Z-Controllers tips 2-4 (multiprobe systems only)
        - Z Averaging Time (float32) is the time (in seconds) to average the Z position before switching off the Z- controller
        - Z Offset (float32) is the Z offset (in meters) by which the tip is retracted after switching off the controller
        - Z Control Time (float32) is the time (in seconds) to wait after switching the Z-Controller back on (in case
        it was switched off)
        - Error described in the Response message>Body section
        """
        return self.quickSend("HSSwp.ZCtrlOffGet", [], [], ["i", "i", "f", "f", "f"])

    def Signals_NamesGet(self):
        """
        Signals.NamesGet
        Returns the signals names list of the 128 signals available in the software.
        The 128 signals are physical inputs, physical outputs and internal channels. By searching in the list the channel’s name you are interested in, you can get its index (0-127).
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Signals names size (int) is the size in bytes of the signals names array
        -- Signals names number (int) is the number of elements of the signals names array
        -- Signals names (1D array string) returns an array of signals names strings, where each string comes prepended by its size in bytes
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Signals.NamesGet", [], [], ["i", "i", "*+c"])

    def Signals_CalibrGet(self, Signal_index):
        """
        Signals.CalibrGet
        Returns the calibration and offset of the selected signal.
        Arguments: 
        -- Signal index (int) is comprised between 0 and 127
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Calibration per volt (float32) 
        -- Offset in physical units (float32) 
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("Signals.CalibrGet", [Signal_index], ["i"], ["f", "f"])

    def Signals_RangeGet(self, Signal_index):
        """
        Signals.RangeGet
        Returns the range limits of the selected signal.
        Arguments: 
        -- Signal index (int) is comprised between 0 and 127
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Maximum limit (float32) 
        -- Minimum limit (float32) 
        -- Error described in the Response message&gt;Body section
        """
        return self.quickSend("Signals.RangeGet", [Signal_index], ["i"], ["f", "f"])

    def Signals_ValGet(self, Signal_index, Wait_for_newest_data):
        """
        Signals.ValGet
        Returns the current value of the selected signal (oversampled during the Acquisition Period time, Tap).
        Signal measurement principle:
        The signal is continuously oversampled with the Acquisition Period time, Tap, specified in the TCP receiver module. Every Tap second, the oversampled data is "published". This VI function waits for the next oversampled data to be published and returns its value. Calling this function does not trigger a signal measurement; it waits for data to be published! Thus, this function returns a value 0 to Tap second after being called.
        An important consequence is that if you change a signal and immediately call this function to read a measurement you might get "old" data (i.e. signal data measured before you changed the signal). The solution to get only new data is to set Wait for newest data to True. In this case, the first published data is discarded and only the second one is returned.
        Arguments: 
        -- Signal index (int) is comprised between 0 and 127
        -- Wait for newest data (unsigned int32) selects whether the function returns the next available signal value or if it waits for a full period of new data. If False, this function returns a value 0 to Tap seconds after being called. If True, the function discard the first oversampled signal value received but returns the second value received. Thus, the function returns a value Tap to 2*Tap seconds after being called. It could be 0_False or 1_True
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Signal value (float32) is the value of the selected signal in physical units
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Signals.ValGet", [Signal_index, Wait_for_newest_data], ["i", "I"], ["f"])

    def Signals_ValsGet(self, Signals_indexes, Wait_for_newest_data):
        """
        Signals.ValsGet
        Returns the current values of the selected signals (oversampled during the Acquisition Period time, Tap).
        Arguments: 
        -- Signals indexes size (int) is the size of the Signals indexes array
        -- Signals indexes (1D array int) sets the selection of signals indexes, comprised between 0 and 127
        -- Wait for newest data (unsigned int32) selects whether the function returns the next available signal value or if it waits for a full period of new data. If False, this function returns a value 0 to Tap seconds after being called. If True, the function discard the first oversampled signal value received but returns the second value received. Thus, the function returns a value Tap to 2*Tap seconds after being called. It could be 0_False or 1_True
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Signals values size (int) is the size of the Signals values array
        -- Signals values (1D array float32) returns the values of the selected signals in physical units
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Signals.ValsGet", [Signals_indexes, Wait_for_newest_data],
                              ["+*i", "I"], ["i", "*f"])

    def Signals_MeasNamesGet(self):
        """
        Signals.MeasNamesGet
        Returns the list of measurement channels names available in the software.
        Important Note: The Measurement channels don't correspond to the Signals. Measurement channels are used in sweepers whereas the Signals are used by the graphs and other modules.
        By searching in the list the channels's names you are interested in, you can know its index. This index is then used e.g. to get/set the recorded channels in Sweepers, for example by using the <i>GenSwp.ChannelsGet</i> and <i>GenSwp.ChannelsSet</i> functions for the 1D Sweeper.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Measurement channels list size (int) is the size in bytes of the Measurement channels list array
        -- Number of Measurement channels (int) is the number of elements of the Measurement channels list array
        -- Measurement channels list (1D array string) returns an array of names, where each array element is preceded by its size in bytes
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Signals.MeasNamesGet", [], [], ["i", "i", "*+c"])

    def Signals_AddRTGet(self):
        """
        Signals.AddRTGet
        Returns the list of names of additional RT signals available, and the names of the signals currently assigned to the Internal 23 and 24 signals.
        This can be found in the Signals Manager. But this assignment does not mean that they are available in the software. 
        In order to have them in the list of 24 signals to display in the graphs and to acquire in some modules, Internal 23 and 24 must be in turn assigned to one of the 24 slots of the Signals Manager. This can be done programmatically through the <i>Signals.InSlotSet</i> function.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Additional RT signals names size (int) is the size in bytes of the Additional RT signals names array
        -- Number of Additional RT signals (int) is the number of elements of the Additional RT signals names array
        -- Additional RT signals names (1D array string) returns the list of additional RT signals which can be assigned to Internal 23 and 24. Each array element is preceded by its size in bytes
        -- Additional RT signal 1 (string) is the name of the RT signal assigned to the Internal 23 signal
        -- Additional RT signal 2 (string) is the name of the RT signal assigned to the Internal 24 signal
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Signals.AddRTGet", [], [], ["i", "i", "*+c", "i", "*-c", "i", "*-c"])

    def Signals_AddRTSet(self, Additional_RT_signal_1, Additional_RT_signal_2):
        """
        Signals.AddRTSet
        Assigns additional RT signals to the Internal 23 and 24 signals in the Signals Manager.
        This function links advanced RT signals to Internal 23 and Internal 24, but in order to have them in the list of 24 signals to display in the graphs and to acquire in the modules, Internal 23 and 24 must be assigned to one of the 24 slots of the Signals Manager. This can be done programmatically through the <i>Signals.InSlotSet</i> function.
        Arguments:
        -- Additional RT signal 1 (int) is the index of the RT signal assigned to the Internal 23 signal
        -- Additional RT signal 2 (int) is the index of the RT signal assigned to the Internal 24 signal
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        User Inputs
        """
        return self.quickSend("Signals.AddRTSet", [Additional_RT_signal_1, Additional_RT_signal_2], ["i", "i"], [])

    def UserIn_CalibrSet(self, Input_index, Calibration_per_volt, Offset_in_physical_units):
        """
        UserIn.CalibrSet
        Sets the calibration of the selected user input.
        Arguments: 
        -- Input index (int) sets the input to be used, where index could be any value from 1 to the available inputs
        -- Calibration per volt (float32) 
        -- Offset in physical units (float32) 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        User Outputs
        """
        return self.quickSend("UserIn.CalibrSet", [Input_index, Calibration_per_volt, Offset_in_physical_units],
                              ["i", "f", "f"], [])

    def UserOut_ModeSet(self, Output_index, Output_mode):
        """
        UserOut.ModeSet
        Sets the mode (User Output, Monitor, Calculated signal) of the selected user output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        -- Output mode (unsigned int16) sets the output mode of the selected output, where 0_User Output, 1_Monitor, 2_Calc.Signal
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("UserOut.ModeSet", [Output_index, Output_mode], ["i", "H"], [])

    def UserOut_ModeGet(self, Output_index):
        """
        UserOut.ModeGet
        Returns the mode (User Output, Monitor, Calculated signal) of the selected user output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Output mode (unsigned int16) returns the output mode of the selected output, where 0_User Output, 1_Monitor, 2_Calc.Signal, 3_Override
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("UserOut.ModeGet", [Output_index], ["i"], ["H"])

    def UserOut_MonitorChSet(self, Output_index, Monitor_channel_index):
        """
        UserOut.MonitorChSet
        Sets the monitor channel of the selected output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        -- Monitor channel index (int) sets the index of the channel to monitor. The index is comprised between 0 and 127 for the physical inputs, physical outputs, and internal channels. To see which signal has which index, see <i>Signals.NamesGet</i> function
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("UserOut.MonitorChSet", [Output_index, Monitor_channel_index], ["i", "i"], [])

    def UserOut_MonitorChGet(self, Output_index):
        """
        UserOut.MonitorChGet
        Returns the monitor channel of the selected output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Monitor channel index (int) returns the index of the channel to monitor. The index is comprised between 0 and 127 for the physical inputs, physical outputs, and internal channels. To see which signal has which index, see <i>Signals.NamesGet</i> function
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("UserOut.MonitorChGet", [Output_index], ["i"], ["i"])

    def UserOut_ValSet(self, Output_index, Output_value):
        """
        UserOut.ValSet
        Sets the value of the selected user output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        -- Output value (float32) is the value applied to the selected user output in physical units
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("UserOut.ValSet", [Output_index, Output_value], ["i", "f"], [])

    def UserOut_CalibrSet(self, Output_index, Calibration_per_volt, Offset_in_physical_units):
        """
        UserOut.CalibrSet
        Sets the calibration of the selected user output or monitor channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        -- Calibration per volt (float32) 
        -- Offset in physical units (float32) 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("UserOut.CalibrSet", [Output_index, Calibration_per_volt, Offset_in_physical_units],
                              ["i", "f", "f"], [])

    def UserOut_CalcSignalNameSet(self, Output_index, Calculated_signal_name):
        """
        UserOut.CalcSignalNameSet
        Sets the Calculated Signal name of the selected output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        -- Calculated signal name size (int) is the number of characters of the Calculated signal name string
        -- Calculated signal name (string) is the name of the calculated signal configured for the selected output
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("UserOut.CalcSignalNameSet",
                              [Output_index, Calculated_signal_name], ["i", "+*c"], [])

    def UserOut_CalcSignalNameGet(self, Output_index):
        """
        UserOut.CalcSignalNameGet
        Returns the Calculated Signal name of the selected output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Calculated signal name size (int) is the number of characters of the Calculated signal name string
        -- Calculated signal name (string) is the name of the calculated signal configured for the selected output
        -- Error described in the Response message&gt;Body section
        
        
        
        """
        return self.quickSend("UserOut.CalcSignalNameGet", [Output_index], ["i"], ["i", "*-c"])

    def UserOut_CalcSignalConfigSet(self, Output_index, Operation_1, Value_1, Operation_2, Value_2, Operation_3, Value_3, Operation_4, Value_4):
        """
        UserOut.CalcSignalConfigSet
        Sets the configuration of the Calculated Signal for the selected output channel.
        The configuration is a combination of 4 parts that creates a formula. Each part of the formula is a parameter/math 
        operation and a value (which depending on the parameter/math operation is applicable or not).
        The possible values for the parameter/math operation of part 1 are: 
        0=None, 5=Constant, 10=Signal Index
        The possible values for the parameter/math operation of parts 2, 3 and 4 are: 
        0=None, 1=Add Constant, 1=Subtract Constant, 3=Multiply Constant, 4=Divide Constant, 6=Add Signal, 
        7=Subtract Signal, 8=Multiply Signal, 9=Divide Signal, 11=Exponent, 12=Absolute, 13= Negate, 14= Log 
        There is no mathematical operator precedence in operation here; the equations are executed in a strict left-to-right 
        (part 1 to part 4) fashion. 
        This is equivalent to defining the calculations as ((((Part 1) Part 2) Part 3) Part 4).
        For example:
        The average of Input 1 and Input 2 is defined as “Input 1 + Input 2 / 2”.
        The sum of Input 1 plus half of Input 2 is defined as “Input 2 / 2 + Input 1”.
        The reciprocal of Input 1 is defined as “1 / Input 1”.
        Arguments: 
        - Output index (int) sets the output to be used, where index could be any value from 1 to the number of 
        available outputs
        - Operation 1 (unsigned int16) is the parameter or math operation selected as the 1st part of the configuration 
        formula. 
        - Value 1 (float32) is a constant value or signal index, depending on the precedent operation
        - Operation 2 (unsigned int16) is the parameter or math operation selected as the 2nd part of the 
        configuration formula. 
        - Value 2 (float32) is a constant value or signal index, depending on the precedent operation
        - Operation 3 (unsigned int16) is the parameter or math operation selected as the 3rd part of the 
        configuration formula. 
        - Value 3 (float32) is a constant value or signal index, depending on the precedent operation
        - Operation 4 (unsigned int16) is the parameter or math operation selected as the 4th part of the 
        configuration formula. 
        - Value 4 (float32) is a constant value or signal index, depending on the precedent operation
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        -- 
        
        """
        return self.quickSend("UserOut.CalcSignalConfigSet", [Output_index, Operation_1, Value_1, Operation_2, Value_2, Operation_3, Value_3, Operation_4, Value_4],
                              ["i", "H", "f", "H", "f", "H", "f", "H", "f"], [])

    def UserOut_CalcSignalConfigGet(self, Output_index):
        """
        UserOut.CalcSignalConfigGet
        Returns the configuration of the Calculated Signal for the selected output channel.
        The configuration is a combination of 4 parts that creates a formula. Each part of the formula is a parameter/math 
        operation and a value (which depending on the parameter/math operation is applicable or not).
        The possible values for the parameter/math operation of part 1 are: 
        0=None, 5=Constant, 10=Signal Index
        The possible values for the parameter/math operation of parts 2, 3 and 4 are: 
        0=None, 1=Add Constant, 1=Subtract Constant, 3=Multiply Constant, 4=Divide Constant, 6=Add Signal, 
        7=Subtract Signal, 8=Multiply Signal, 9=Divide Signal, 11=Exponent, 12=Absolute, 13= Negate, 14= Log 
        There is no mathematical operator precedence in operation here; the equations are executed in a strict left-to-right 
        (part 1 to part 4) fashion. 
        This is equivalent to defining the calculations as ((((Part 1) Part 2) Part 3) Part 4).
        For example:
        The average of Input 1 and Input 2 is defined as “Input 1 + Input 2 / 2”.
        The sum of Input 1 plus half of Input 2 is defined as “Input 2 / 2 + Input 1”.
        The reciprocal of Input 1 is defined as “1 / Input 1”.
        
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        - Operation 1 (unsigned int16) is the parameter or math operation selected as the 1st part of the configuration 
        formula. 
        - Value 1 (float32) is a constant value or signal index, depending on the precedent operation
        - Operation 2 (unsigned int16) is the parameter or math operation selected as the 2nd part of the 
        configuration formula. 
        - Value 2 (float32) is a constant value or signal index, depending on the precedent operation
        - Operation 3 (unsigned int16) is the parameter or math operation selected as the 3rd part of the 
        configuration formula. 
        - Value 3 (float32) is a constant value or signal index, depending on the precedent operation
        - Operation 4 (unsigned int16) is the parameter or math operation selected as the 4th part of the 
        configuration formula. 
        - Value 4 (float32) is a constant value or signal index, depending on the precedent operation
        -- Error described in the Response message&gt;Body section
        
        
        
        
        
        """
        return self.quickSend("UserOut.CalcSignalConfigGet", [Output_index], ["i"], ["H", "f", "H", "f", "H", "f", "H", "f"])

    def UserOut_LimitsSet(self, Output_index, Upper_limit, Lower_limit, Raw_limits):
        """
        UserOut.LimitsSet
        Sets the physical limits (in calibrated units) of the selected output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        -- Upper limit (float32) defines the upper physical limit of the user output
        -- Lower limit (float32) defines the lower physical limit of the user output
        -- Raw limits? (unsigned int32) selects whether to set the physical limits (0) or the raw limits (1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("UserOut.LimitsSet", [Output_index, Upper_limit, Lower_limit, Raw_limits], ["i", "f", "f", "I"], [])

    def UserOut_LimitsGet(self, Output_index, Raw_limits):
        """
        UserOut.LimitsGet
        Returns the physical limits (in calibrated units) of the selected output channel.
        Arguments: 
        -- Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        -- Raw limits? (unsigned int32) selects whether to set the physical limits (0) or the raw limits (1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Upper limit (float32) defines the upper physical limit of the user output
        -- Lower limit (float32) defines the lower physical limit of the user output
        -- Error described in the Response message&gt;Body section 
        
        
        
        
        
        Digital Lines
        """
        return self.quickSend("UserOut.LimitsGet", [Output_index, Raw_limits], ["i", "I"], ["f", "f"])

    def UserOut_SlewRateSet(self, Output_Index, Slew_Rate):
        """
        Sets the slew rate (in calibrated units) of the selected output channel.
        Arguments:
        - Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs
        - Slew Rate (float64) defines the calibrated slew rate of the user output

        Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section
        """

        return self.quickSend("UserOut.SlewRateSet", [Output_Index, Slew_Rate], ["i", "d"], [])

    def UserOut_SlewRateGet(self):
        """
        Returns the slew rate (in calibrated units) of the selected output channel.
        Arguments:
        - Output index (int) sets the output to be used, where index could be any value from 1 to the number of available outputs

        Return arguments (if Send response back flag is set to True when sending request message):
        - Slew Rate (float64) is the calibrated slew rate of the user output
        - Error described in the Response message>Body section
        """

        return self.quickSend("UserOut.SlewRateGet", [], [], ["d"])

    def DigLines_PropsSet(self, Digital_line, Port, Direction, Polarity):
        """
        DigLines.PropsSet
        Configures the properties of a digital line.
        Arguments: 
        -- Digital line (unsigned int32) defines the line to configure, from 1 to 8
        -- Port (unsigned int32) selects the digital port, where 0=Port A, 1=Port B, 2=Port C, 3=Port D, 4=Expanded Port 0, 5=Expanded Port 1, 6=Expanded Port 2, etc
        The expanded DIO ports are available on selected systems through a dedicated DIO card.
        -- Direction (unsigned int32) is the direction of the selected digital line, where 0_Input, 1_Output
        -- Polarity (unsigned int32), where 0_Low active, 1_High active
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("DigLines.PropsSet", [Digital_line, Port, Direction, Polarity], ["I", "I", "I", "I"], [])

    def DigLines_OutStatusSet(self, Port, Digital_line, Status):
        """
        DigLines.OutStatusSet
        Sets the status of a digital output line.
        Arguments: 
        -- Port (unsigned int32) selects the digital port, where 0=Port A, 1=Port B, 2=Port C, 3=Port D, 4=Expanded Port 0, 5=Expanded Port 1, 6=Expanded Port 2, etc
        The expanded DIO ports are available on selected systems through a dedicated DIO card.
        -- Digital line (unsigned int32) defines the output line to configure, from 1 to 8
        -- Status (unsigned int32) sets whether the output is active or inactive, where 0_Inactive, 1_Active
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("DigLines.OutStatusSet", [Port, Digital_line, Status], ["I", "I", "I"], [])

    def DigLines_TTLValGet(self, Port):
        """
        DigLines.TTLValGet
        Reads the actual TTL voltages present at the pins of the selected port.
        Arguments: 
        -- Port (unsigned int16) selects the digital port, where 0=Port A, 1=Port B, 2=Port C, 3=Port D, 4=Expanded Port 0, 5=Expanded Port 1, 6=Expanded Port 2, etc
        The expanded DIO ports are available on selected systems through a dedicated DIO card.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- TTL voltages size (int) is the size of the TTL voltages array
        -- TTL voltages (1D array unsigned int32) sets whether the output is active or inactive, where 0_Inactive, 1_Active
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("DigLines.TTLValGet", [Port], ["H"], ["i", "*I"])

    def DigLines_Pulse(self, Port, Digital_lines, Pulse_width_s, Pulse_pause_s, Number_of_pulses,
                       Wait_until_finished):
        """
        DigLines.Pulse
        Configures and starts the pulse generator on the selected digital outputs.
        Arguments: 
        -- Port (unsigned int16) selects the digital port, where 0=Port A, 1=Port B, 2=Port C, 3=Port D, 4=Expanded Port 0, 5=Expanded Port 1, 6=Expanded Port 2, etc
        The expanded DIO ports are available on selected systems through a dedicated DIO card.
        -- Digital lines size (int) is the size of the Digital lines array
        -- Digital lines (1D array unsigned int8) defines the output lines to pulse, from 1 to 8
        -- Pulse width (s) (float32) defines how long the outputs are active
        -- Pulse pause (s) (float32) defines how long the outputs are inactive
        -- Number of pulses (int) defines how many pulses to generate, where valid values are from 1 to 32767
        -- Wait until finished (unsigned int32), if True this function waits until all pulses have been generated before the response is sent back, where 0_False, 1_True
         
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        Data Logger
        """
        return self.quickSend("DigLines.Pulse",
                              [Port, Digital_lines, Pulse_width_s, Pulse_pause_s, Number_of_pulses,
                               Wait_until_finished], ["H", "+*b", "f", "f", "i", "I"], [])

    def DataLog_Open(self):
        """
        DataLog.Open
        Opens the Data Logger module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("DataLog.Open", [], [], [])

    def DataLog_Start(self):
        """
        DataLog.Start
        Starts the acquisition in the Data Logger module.
        Before using this function, select the channels to record in the Data Logger.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("DataLog.Start", [], [], [])

    def DataLog_Stop(self):
        """
        DataLog.Stop
        Stops the acquisition in the Data Logger module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("DataLog.Stop", [], [], [])

    def DataLog_StatusGet(self):
        """
        DataLog.StatusGet
        Returns the status parameters from the Data Logger module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Start time size (int) returns the number of bytes corresponding to the Start time string
        -- Start time (string) returns a timestamp of the moment when the acquisition started
        -- Acquisition elapsed hours (unsigned int16) returns the number of hours already passed since the acquisition started
        -- Acquisition elapsed minutes (unsigned int16) returns the number of minutes displayed on the Data Logger
        -- Acquisition elapsed seconds (float32) returns the number of seconds displayed on the Data Logger
        -- Stop time size (int) returns the number of bytes corresponding to the Stop time string
        -- Stop time (string) returns a timestamp of the moment when the acquisition Stopped
        -- Saved file path size (int) returns the number of bytes corresponding to the Saved file path string
        -- Saved file path (string) returns the path of the last saved file
        -- Saved points (int) returns the number of points (averaged samples) already saved into file. 
        This parameter updates while running the acquisition, every time a file is saved
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("DataLog.StatusGet", [], [], ["i", "*-c", "H", "H", "f", "i", "*-c", "i", "*-c", "i"])

    def DataLog_ChsSet(self, Channel_indexes):
        """
        DataLog.ChsSet
        Sets the list of recorded channels in the Data Logger module.
        Arguments: 
        -- Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        -- Channel indexes (1D array int) are the indexes of recorded channels. The indexes are comprised between 0 and 23 for the 24 signals assigned in the Signals Manager.
        To get the signal name and its corresponding index in the list of the 128 available signals in the Nanonis Controller, use the <i>Signals.InSlotsGet</i> function
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("DataLog.ChsSet", [Channel_indexes], ["+*i"], [])

    def DataLog_ChsGet(self):
        """
        DataLog.ChsGet
        Returns the list of recorded channels in the Data Logger module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        -- Channel indexes (1D array int) are the indexes of recorded channels. The indexes are comprised between 0 and 23 for the 24 signals assigned in the Signals Manager.
        To get the signal name and its corresponding index in the list of the 128 available signals in the Nanonis Controller, use the <i>Signals.InSlotsGet</i> function
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("DataLog.ChsGet", [], [], ["i", "*i"])

    def DataLog_PropsSet(self, Acquisition_mode, Acquisition_duration_hours, Acquisition_duration_minutes,
                         Acquisition_duration_seconds, Averaging, Basename, Comment, List_of_modules):
        """
        DataLog.PropsSet
        Sets the acquisition configuration and the save options in the Data Logger module.
        Arguments:
        -- Acquisition mode (unsigned int16) means that if Timed (_2), the selected channels are acquired during the acquisition duration time or until the user presses the Stop button. 
        If Continuous (_1), the selected channels are acquired continuously until the user presses the Stop button.
        If 0, the is no change in the acquisition mode.
        The acquired data are saved every time the averaged samples buffer reaches 25.000 samples and when the acquisition stops
        -- Acquisition duration( hours) (int) sets the number of hours the acquisition should last. Value -1 means no change
        -- Acquisition duration (minutes) (int) sets the number of minutes. Value -1 means no change
        -- Acquisition duration (seconds) (float32) sets the number of seconds. Value -1 means no change
        -- Averaging (int) sets how many data samples (received from the real-time system) are averaged for one data point saved into file. By increasing this value, the noise might decrease, and fewer points per seconds are recorded.
        Use 0 to skip changing this parameter
        -- Basename size (int) is the size in bytes of the Basename string
        -- Basename (string) is base name used for the saved images
        -- Comment size (int) is the size in bytes of the Comment string
        -- Comment (string) is comment saved in the file
        -- Size of the list of moduless (int) is the size in bytes of the List of modules string array
        -- Number of modules (int) is the number of elements of the List of modules string array
        -- List of modules (1D array string) sets the modules names whose parameters will be saved in the header of the files. The size of each string item should come right before it as integer 32
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("DataLog.PropsSet",
                              [Acquisition_mode, Acquisition_duration_hours, Acquisition_duration_minutes,
                               Acquisition_duration_seconds, Averaging, Basename, Comment,
                               List_of_modules],
                              ["H", "i", "i", "f", "i", "+*c", "+*c", "+*c"], [])

    def DataLog_PropsGet(self):
        """
        DataLog.PropsGet
        Returns the acquisition configuration and the save options in the Data Logger module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Acquisition mode (unsigned int16) means that if Timed (_1), the selected channels are acquired during the acquisition duration time or until the user presses the Stop button. 
        If Continuous (_0), the selected channels are acquired continuously until the user presses the Stop button.
        The acquired data are saved every time the averaged samples buffer reaches 25.000 samples and when the acquisition stops
        -- Acquisition duration( hours) (int) returns the number of hours the acquisition lasts
        -- Acquisition duration (minutes) (int) returns the number of minutes
        -- Acquisition duration (seconds) (float32) returns the number of seconds
        -- Averaging (int) returns how many data samples (received from the real-time system) are averaged for one data point saved into file
        -- Basename size (int) returns the size in bytes of the Basename string
        -- Basename (string) returns the base name used for the saved images
        -- Comment size (int) returns the size in bytes of the Comment string
        -- Comment (string) returns the comment saved in the file
        -- Error described in the Response message&gt;Body section
        
        TCP Logger
        """
        return self.quickSend("DataLog.PropsGet", [], [], ["H", "i", "i", "f", "i", "i", "*-c", "i", "*-c"])

    def TCPLog_Start(self):
        """
        TCPLog.Start
        Starts the acquisition in the TCP Logger module.
        Before using this function, select the channels to record in the TCP Logger.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("TCPLog.Start", [], [], [])

    def TCPLog_Stop(self):
        """
        TCPLog.Stop
        Stops the acquisition in the TCP Logger module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("TCPLog.Stop", [], [], [])

    def TCPLog_ChsSet(self, Num_channels, Channel_indexes):
        """
        TCPLog.ChsSet
        Sets the list of recorded channels in the TCP Logger module.
        Arguments: 
        -- Number of channels (int) is the number of recorded channels. It defines the size of the Channel indexes array
        -- Channel indexes (1D array int) are the indexes of recorded channels. The indexes are comprised between 0 and 23 for the 24 signals assigned in the Signals Manager.
        To get the signal name and its corresponding index in the list of the 128 available signals in the Nanonis Controller, use the <i>Signals.InSlotsGet</i> function
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        
        """
        return self.quickSend("TCPLog.ChsSet", [Num_channels, Channel_indexes], ["i", "*i"], [])

    def TCPLog_OversamplSet(self, Oversampling_value):
        """
        TCPLog.OversamplSet
        Sets the oversampling value in the TCP Logger.
        Arguments: 
        -- Oversampling value (int) sets the oversampling index, where index could be any value from 0 to 1000
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        
        """
        return self.quickSend("TCPLog.OversamplSet", [Oversampling_value], ["i"], [])

    def TCPLog_StatusGet(self):
        """
        TCPLog.StatusGet
        Returns the current status of the TCP Logger.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Status (int) returns an index which corresponds to one of the following status: 0_disconnected, 1_idle, 2_start, 3_stop, 4_running, 5_TCP connect, 6_TCP disconnect, 7_buffer overflow
        
        -- Error described in the Response message&gt;Body section
        
        Oscilloscope High Resolution
        """
        return self.quickSend("TCPLog.StatusGet", [], [], ["i"])

    def OsciHR_ChSet(self, Osci_index, Signal_index):
        """
        OsciHR.ChSet
        Sets the measured signal index of the selected channel from the Oscilloscope High Resolution.
        Arguments: 
        -- Osci index (int) sets the oscilloscope channel to be used, where index could be any value from 1 to 4 when the Oscilloscope supports 4 channels. 
           Otherwise the channel index should be set to 0 for the 1-channel version of this graph
        -- Signal index (int) sets the signal to be measured, where index could be any value from 0 to 15
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.ChSet", [Osci_index, Signal_index], ["i", "i"], [])

    def OsciHR_ChGet(self, Osci_index):
        """
        OsciHR.ChGet
        Returns the measured signal index of the selected channel from the Oscilloscope High Resolution.
        Arguments: 
        -- Osci index (int) sets the oscilloscope channel to be used, where index could be any value from 1 to 4 when the Oscilloscope supports 4 channels. 
           Otherwise the channel index should be set to 0 for the 1-channel version of this graph
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Signal index (int) returns the measured signal index
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.ChGet", [Osci_index], ["i"], ["i"])

    def OsciHR_OversamplSet(self, Oversampling_index):
        """
        OsciHR.OversamplSet
        Sets the oversampling index of the Oscilloscope High Resolution.
        Choosing to acquire data at lower rate than the maximum 1MS/s allows for an improved S/N ratio and also increases the time window for the acquisition for a given number of samples.
        Arguments: 
        -- Oversampling index (int) sets the oversampling index, where index could be any value from 0 to 10
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.OversamplSet", [Oversampling_index], ["i"], [])

    def OsciHR_OversamplGet(self):
        """
        OsciHR.OversamplGet
        Returns the oversampling index of the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Oversampling index (int) gets the oversampling index, where index could be any value from 0 to 10
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.OversamplGet", [], [], ["i"])

    def OsciHR_CalibrModeSet(self, Osci_index, Calibration_mode):
        """
        OsciHR.CalibrModeSet
        Sets the calibration mode of the selected channel from the Oscilloscope High Resolution.
        Select between Raw Values or Calibrated Values. This setting affects the data displayed in the graph, and trigger level and hysteresis values. 
        Arguments: 
        -- Osci index (int) sets the oscilloscope channel to be used, where index could be any value from 1 to 4 when the Oscilloscope supports 4 channels. 
           Otherwise the channel index should be set to 0 for the 1-channel version of this graph
        -- Calibration mode (unsigned int16), where 0_Raw values and 1_Calibrated values
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.CalibrModeSet", [Osci_index, Calibration_mode], ["i", "H"], [])

    def OsciHR_CalibrModeGet(self, Osci_index):
        """
        OsciHR.CalibrModeGet
        Returns the calibration mode of the selected channel from the Oscilloscope High Resolution.
        Arguments: 
        -- Osci index (int) sets the oscilloscope channel to be used, where index could be any value from 1 to 4 when the Oscilloscope supports 4 channels. 
           Otherwise the channel index should be set to 0 for the 1-channel version of this graph
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Calibration mode (unsigned int16), where 0_Raw values and 1_Calibrated values
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.CalibrModeGet", [Osci_index], ["i"], ["H"])

    def OsciHR_SamplesSet(self, Number_of_samples):
        """
        OsciHR.SamplesSet
        Sets the number of samples to acquire in the Oscilloscope High Resolution.
        Arguments: 
        -- Number of samples (int)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.SamplesSet", [Number_of_samples], ["i"], [])

    def OsciHR_SamplesGet(self):
        """
        OsciHR.SamplesGet
        Returns the number of samples to acquire in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Number of samples (int)
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.SamplesGet", [], [], ["i"])

    def OsciHR_PreTrigSet(self, Pre_Trigger_samples, Pre_Trigger_s):
        """
        OsciHR.PreTrigSet
        Sets the Pre-Trigger Samples or Seconds in the Oscilloscope High Resolution.
        If Pre-Trigger (s) is NaN or Inf or below 0, Pre-Trigger Samples is taken into account instead of seconds.
        Arguments: 
        -- Pre-Trigger samples (unsigned int32)
        -- Pre-Trigger (s) (float64)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PreTrigSet", [Pre_Trigger_samples, Pre_Trigger_s], ["I", "d"], [])

    def OsciHR_PreTrigGet(self):
        """
        OsciHR.PreTrigGet
        Returns the Pre-Trigger Samples in the Oscilloscope High Resolution.
        If Pre-Trigger (s) is NaN or Inf or below 0, Pre-Trigger Samples is taken into account instead of seconds.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Pre-Trigger samples (int)
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PreTrigGet", [], [], ["i"])

    def OsciHR_Run(self):
        """
        OsciHR.Run
        Starts the Oscilloscope High Resolution module.
        The Oscilloscope High Resolution module does not run when its front panel is closed. To automate measurements it might be required to run the module first using this function.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.Run", [], [], [])

    def OsciHR_OsciDataGet(self, Osci_index, Data_to_get, Timeout_s):
        """
        OsciHR.OsciDataGet
        Returns the graph data of the selected channel from the Oscilloscope High Resolution.
        Arguments: 
        -- Osci index (int) sets the oscilloscope channel to be used, where index could be any value from 1 to 4 when the Oscilloscope supports 4 channels. 
           Otherwise the channel index should be set to 0 for the 1-channel version of this graph
        -- Data to get (unsigned int16), where 0_Current returns the currently displayed data and 1_Next trigger waits for the next trigger to retrieve data
        -- Timeout (s) (float64), tip
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Data t0 size (int) is the number of characters of the Data t0 string
        -- Data t0 (string) is the timestamp of the 1st acquired point
        -- Data dt (float64) is the time distance between two acquired points
        -- Data Y size (int) is the number of data points in Data Y
        -- Data Y (1D array float32) is the data acquired in the oscilloscope
        -- Timeout (unsigned int32) is 0 when no timeout occurred, and 1 when a timeout occurred
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.OsciDataGet", [Osci_index, Data_to_get, Timeout_s], ["i", "H", "d"],
                              ["i", "*-c", "d", "i", "*f", "I"])

    def OsciHR_TrigModeSet(self, Trigger_mode):
        """
        OsciHR.TrigModeSet
        Sets the trigger mode in the Oscilloscope High Resolution.
        Arguments: 
        -- Trigger mode (unsigned int16), 0_Immediate means triggering immediately whenever the current data set is received by the host software, 1_Level where the trigger detection is performed on the non-averaged raw channel data (1MS/s), and 2_Digital where the trigger detection on the LS-DIO channels is performed at 500kS/s. Trigger detection on the HS-DIO channels is performed at 10MS/s
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigModeSet", [Trigger_mode], ["H"], [])

    def OsciHR_TrigModeGet(self):
        """
        OsciHR.TrigModeGet
        Returns the trigger mode in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Trigger mode (unsigned int16), where 0_Immediate, 1_Level, and 2_Digital
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigModeGet", [], [], ["H"])

    def OsciHR_TrigLevChSet(self, Level_trigger_channel_index):
        """
        OsciHR.TrigLevChSet
        Sets the Level Trigger Channel index in the Oscilloscope High Resolution.
        Trigger detection is performed on the non-averaged raw channel data.
        Arguments: 
        -- Level trigger channel index (int) 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigLevChSet", [Level_trigger_channel_index], ["i"], [])

    def OsciHR_TrigLevChGet(self):
        """
        OsciHR.TrigLevChGet
        Returns the Level Trigger Channel index in the Oscilloscope High Resolution.
        Trigger detection is performed on the non-averaged raw channel data.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Level trigger channel index (int) 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigLevChGet", [], [], ["i"])

    def OsciHR_TrigLevValSet(self, Level_trigger_value):
        """
        OsciHR.TrigLevValSet
        Sets the Level Trigger value in the Oscilloscope High Resolution.
        Arguments: 
        -- Level trigger value (float64) 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        """
        return self.quickSend("OsciHR.TrigLevValSet", [Level_trigger_value], ["d"], [])

    def OsciHR_TrigLevValGet(self):
        """
        OsciHR.TrigLevValGet
        Returns the Level Trigger value in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Level trigger value (float64) 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigLevValGet", [], [], ["d"])

    def OsciHR_TrigLevHystSet(self, Level_trigger_Hysteresis):
        """
        OsciHR.TrigLevHystSet
        Sets the Level Trigger Hysteresis in the Oscilloscope High Resolution.
        Arguments: 
        -- Level trigger Hysteresis (float64) 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigLevHystSet", [Level_trigger_Hysteresis], ["d"], [])

    def OsciHR_TrigLevHystGet(self):
        """
        OsciHR.TrigLevHystGet
        Returns the Level Trigger Hysteresis in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Level trigger Hysteresis (float64) 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigLevHystGet", [], [], ["d"])

    def OsciHR_TrigLevSlopeSet(self, Level_trigger_slope):
        """
        OsciHR.TrigLevSlopeSet
        Sets the Level Trigger Slope in the Oscilloscope High Resolution.
        Arguments: 
        -- Level trigger slope (unsigned int16), where 0_Rising and 1_Falling 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigLevSlopeSet", [Level_trigger_slope], ["H"], [])

    def OsciHR_TrigLevSlopeGet(self):
        """
        OsciHR.TrigLevSlopeGet
        Returns the Level Trigger Slope in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Level trigger slope (unsigned int16), where 0_Rising and 1_Falling 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigLevSlopeGet", [], [], ["H"])

    def OsciHR_TrigDigChSet(self, Digital_trigger_channel_index):
        """
        OsciHR.TrigDigChSet
        Sets the Digital Trigger Channel in the Oscilloscope High Resolution.
        Trigger detection on the LS-DIO channels is performed at 500kS/s. Trigger detection on the HS-DIO channels is performed at 10MS/s.
        Arguments: 
        -- Digital trigger channel index (int), where index can be any value from 0 to 35. Low Speed Port A lines are indexes 0 to 7, Low Speed Port B lines are indexes 8 to 15, Low Speed Port C lines are indexes 16 to 23, Low Speed Port D lines are indexes 24 to 31, and High Speed Port lines are indexes 32 to 35
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigDigChSet", [Digital_trigger_channel_index], ["i"], [])

    def OsciHR_TrigDigChGet(self):
        """
        OsciHR.TrigDigChGet
        Returns the Digital Trigger Channel in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Digital trigger channel index (int), where index can be any value from 0 to 35. Low Speed Port A lines are indexes 0 to 7, Low Speed Port B lines are indexes 8 to 15, Low Speed Port C lines are indexes 16 to 23, Low Speed Port D lines are indexes 24 to 31, and High Speed Port lines are indexes 32 to 35
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigDigChGet", [], [], ["i"])

    def OsciHR_TrigArmModeSet(self, Trigger_arming_mode):
        """
        OsciHR.TrigArmModeSet
        Sets the Trigger Arming Mode in the Oscilloscope High Resolution.
        Arguments: 
        -- Trigger arming mode (unsigned int16), where 0_Single shot means recording the next available data and stopping acquisition. and 1_Continuous means recording every available data and automatically re-triggers the acquisition
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigArmModeSet", [Trigger_arming_mode], ["H"], [])

    def OsciHR_TrigArmModeGet(self):
        """
        OsciHR.TrigArmModeGet
        Returns the Trigger Arming Mode in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Trigger arming mode (unsigned int16), where 0_Single shot means recording the next available data and stopping acquisition. and 1_Continuous means recording every available data and automatically re-triggers the acquisition
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigArmModeGet", [], [], ["H"])

    def OsciHR_TrigDigSlopeSet(self, Digital_trigger_slope):
        """
        OsciHR.TrigDigSlopeSet
        Sets the Digital Trigger Slope in the Oscilloscope High Resolution.
        Arguments: 
        -- Digital trigger slope (unsigned int16), where 0_Rising and 1_Falling 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigDigSlopeSet", [Digital_trigger_slope], ["H"], [])

    def OsciHR_TrigDigSlopeGet(self):
        """
        OsciHR.TrigDigSlopeGet
        Returns the Digital Trigger Slope in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Digital trigger slope (unsigned int16), where 0_Rising and 1_Falling 
        -- Error described in the Response message&gt;Body section
        """
        return self.quickSend("OsciHR.TrigDigSlopeGet", [], [], ["H"])

    def OsciHR_TrigRearm(self):
        """
        OsciHR.TrigRearm
        Rearms the trigger in the Oscilloscope High Resolution module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.TrigRearm", [], [], [])

    def OsciHR_PSDShow(self, Show_PSD_section):
        """
        OsciHR.PSDShow
        Shows or hides the PSD section of the Oscilloscope High Resolution.
        Arguments: 
        -- Show PSD section (unsigned int32), where 0_Hide and 1_Show 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        
        """
        return self.quickSend("OsciHR.PSDShow", [Show_PSD_section], ["I"], [])

    def OsciHR_PSDWeightSet(self, PSD_Weighting):
        """
        OsciHR.PSDWeightSet
        Sets the PSD Weighting in the Oscilloscope High Resolution.
        Arguments: 
        -- PSD Weighting (unsigned int16), where 0_Linear means that the averaging combines Count spectral records with equal weighting and then stops, whereas 1_Exponential means that the averaging process is continuous and new spectral data have a higher weighting than older ones
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PSDWeightSet", [PSD_Weighting], ["H"], [])

    def OsciHR_PSDWeightGet(self):
        """
        OsciHR.PSDWeightGet
        Returns the PSD Weighting in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- PSD Weighting (unsigned int16), where 0_Linear means that the averaging combines Count spectral records with equal weighting and then stops, whereas 1_Exponential means that the averaging process is continuous and new spectral data have a higher weighting than older ones
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PSDWeightGet", [], [], ["H"])

    def OsciHR_PSDWindowSet(self, PSD_window_type):
        """
        OsciHR.PSDWindowSet
        Sets the PSD Window Type in the Oscilloscope High Resolution.
        Arguments: 
        -- PSD window type (unsigned int16) is the window function applied to the timed signal before calculating the power spectral density, where 0_None, 1_Hanning, 2_Hamming, etc
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        """
        return self.quickSend("OsciHR.PSDWindowSet", [PSD_window_type], ["H"], [])

    def OsciHR_PSDWindowGet(self):
        """
        OsciHR.PSDWindowGet
        Returns the PSD Window Type in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- PSD window type (unsigned int16) is the window function applied to the timed signal before calculating the power spectral density, where 0_None, 1_Hanning, 2_Hamming, etc
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PSDWindowGet", [], [], ["H"])

    def OsciHR_PSDAvrgTypeSet(self, PSD_averaging_type):
        """
        OsciHR.PSDAvrgTypeSet
        Sets the PSD Averaging Type in the Oscilloscope High Resolution.
        Arguments: 
        -- PSD averaging type (unsigned int16), where 0_None, 1_Vector, 2_RMS, 3_Peak hold
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PSDAvrgTypeSet", [PSD_averaging_type], ["H"], [])

    def OsciHR_PSDAvrgTypeGet(self):
        """
        OsciHR.PSDAvrgTypeGet
        Returns the PSD Averaging Type in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- PSD averaging type (unsigned int16), where 0_None, 1_Vector, 2_RMS, 3_Peak hold
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PSDAvrgTypeGet", [], [], ["H"])

    def OsciHR_PSDAvrgCountSet(self, PSD_averaging_count):
        """
        OsciHR.PSDAvrgCountSet
        Sets the PSD Averaging Count used by the RMS and Vector averaging types in the Oscilloscope High Resolution.
        Arguments: 
        -- PSD averaging count (int)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PSDAvrgCountSet", [PSD_averaging_count], ["i"], [])

    def OsciHR_PSDAvrgCountGet(self):
        """
        OsciHR.PSDAvrgCountGet
        Returns the PSD Averaging Count used by the RMS and Vector averaging types in the Oscilloscope High Resolution.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- PSD averaging count (int)
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PSDAvrgCountGet", [], [], ["i"])

    def OsciHR_PSDAvrgRestart(self):
        """
        OsciHR.PSDAvrgRestart
        Restarts the PSD averaging process in the Oscilloscope High Resolution module.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("OsciHR.PSDAvrgRestart", [], [], [])

    def OsciHR_PSDDataGet(self, Data_to_get, Timeout_s):
        """
        OsciHR.PSDDataGet
        Returns the Power Spectral Density data from the Oscilloscope High Resolution.
        Arguments: 
        -- Data to get (unsigned int16), where 0_Current returns the currently displayed data and 1_Next trigger waits for the next trigger to retrieve data
        -- Timeout (s) (float64), where -1 means waiting forever
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Data f0 (float64) is the x coordinate of the 1st acquired point
        -- Data df (float64) is the frequency distance between two acquired points
        -- Data Y size (int) is the number of data points in Data Y
        -- Data Y (1D array float64) is the PSD data acquired in the oscilloscope
        -- Timeout (unsigned int32) is 0 when no timeout occurred, and 1 when a timeout occurred
        -- Error described in the Response message&gt;Body section
        """
        return self.quickSend("OsciHR.PSDDataGet",
                              [Data_to_get, Timeout_s],
                              ["H", "d"],
                              ["d", "d", "i", "*d", "I"])

    def Util_SessionPathGet(self):
        """
        Util.SessionPathGet
        Returns the session path.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Session path size (int) is the number of characters of the Session path string
        -- Session path (string) 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.SessionPathGet", [], [], ["i", "*-c"])

    def Util_SettingsLoad(self, Settings_file_path, Load_session_settings):
        """
        Util.SettingsLoad
        Loads the settings from the specified .ini file.
        Arguments:
        -- Settings file path size (int) is the number of characters of the Settings file path string
        -- Settings file path (string) is the path of the settings file to load
        -- Load session settings (unsigned int32) automatically loads the current settings from the session file bypassing the settings file path argument, where 0_False and 1_True  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.SettingsLoad", [Settings_file_path, Load_session_settings],
                              ["+*c", "I"], [])

    def Util_SettingsSave(self, Settings_file_path, Save_session_settings):
        """
        Util.SettingsSave
        Saves the current settings in the specified .ini file.
        Arguments:
        -- Settings file path size (int) is the number of characters of the Settings file path string
        -- Settings file path (string) is the path of the settings file to save
        -- Save session settings (unsigned int32) automatically saves the current settings into the session file bypassing the settings file path argument, where 0_False and 1_True  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.SettingsSave", [Settings_file_path, Save_session_settings],
                              ["+*c", "I"], [])

    def Util_LayoutLoad(self, Layout_file_path, Load_session_layout):
        """
        Util.LayoutLoad
        Loads a layout from the specified .ini file.
        Arguments:
        -- Layout file path size (int) is the number of characters of the layout file path string
        -- Layout file path (string) is the path of the layout file to load
        -- Load session layout (unsigned int32) automatically loads the layout from the session file bypassing the layout file path argument, where 0_False and 1_True  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.LayoutLoad", [Layout_file_path, Load_session_layout],
                              ["+*c", "I"], [])

    def Util_LayoutSave(self, Layout_file_path, Save_session_layout):
        """
        Util.LayoutSave
        Saves the current layout in the specified .ini file.
        Arguments:
        -- Layout file path size (int) is the number of characters of the layout file path string
        -- Layout file path (string) is the path of the layout file to save
        -- Save session layout (unsigned int32) automatically saves the current layout into the session file bypassing the layout file path argument, where 0_False and 1_True  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.LayoutSave", [Layout_file_path, Save_session_layout],
                              ["+*c", "I"], [])

    def Util_Lock(self):
        """
        Util.Lock
        Locks the Nanonis software.
        Launches the Lock modal window, preventing the user to interact with the Nanonis software until unlocking it manually or through the <i>Util.UnLock</i> function.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.Lock", [], [], [])

    def Util_UnLock(self):
        """
        Util.UnLock
        Unlocks the Nanonis software.
        Closes the Lock modal window which prevents the user to interact with the Nanonis software.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.UnLock", [], [], [])

    def Util_RTFreqSet(self, RT_frequency):
        """
        Util.RTFreqSet
        Sets the Real Time controller frequency.
        Arguments:
        -- RT frequency (float32) is the Real Time frequency in Hz
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.RTFreqSet", [RT_frequency], ["f"], [])

    def Util_RTFreqGet(self):
        """
        Util.RTFreqGet
        Gets the Real Time controller frequency.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- RT frequency (float32) is the Real Time frequency in Hz
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.RTFreqGet", [], [], ["f"])

    def Util_AcqPeriodSet(self, Acquisition_Period_s):
        """
        Util.AcqPeriodSet
        Sets the Acquisition Period (s) in the TCP Receiver.
        Arguments:
        -- Acquisition Period (s) (float32)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.AcqPeriodSet", [Acquisition_Period_s], ["f"], [])

    def Util_AcqPeriodGet(self):
        """
        Util.AcqPeriodGet
        Gets the Acquisition Period (s) in the TCP Receiver.
        Arguments: None
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Acquisition Period (s) (float32) 
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.AcqPeriodGet", [], [], ["f"])

    def Util_RTOversamplSet(self, RT_oversampling):
        """
        Util.RTOversamplSet
        Sets the Real-time oversampling in the TCP Receiver.
        The 24 signals are oversampled on the RT engine before they are sent to the host. The oversampling affects the maximum Spectrum Analyzer frequency and other displays.
        Arguments:
        -- RT oversampling (int)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("Util.RTOversamplSet", [RT_oversampling], ["i"], [])

    def Util_RTOversamplGet(self):
        """
        Returns the Real-time oversampling in the TCP Receiver.
        Arguments:
        None
        Return arguments (if Send response back flag is set to True when sending request message):

        - RT oversampling (int)
        - Error described in the Response message>Body section
        """
        return self.quickSend("Util.RTOversamplGet", [], [], ["i"])

    def Util_Quit(self, Use_Stored_Values, Settings_Name, Layout_Name, Save_Signals):
        """
        Quits the Nanonis software with the option to save settings, layout and signals (same functionality provided by the dialog window that pops-up when quitting the software through the File menu).
        Arguments:

        - Use the stored values (unsigned int32) automatically ignores the rest of the arguments (0=False and 1=True) and saves settings, layout, and signals according to the last time the software quit.
        This configuration is stored in the Main-Options settings.ini file located in the Certificate folder.
        - Settings name size (int) is the number of characters of the Settings name string
        - Settings name (string) is the name of the settings file to save when quitting. The list of settings can be
        found in the Settings section of the Main Options under the File menu.
        If left empty, no settings are saved (unless the argument “Use the stored values” is 1).
        - Layout name size (int) is the number of characters of the Layout name string
        - Layout name (string) is the name of the layout file to save when quitting. The list of layouts can be found
        in the Layouts section of the Main Options under the File menu.
        If left empty, no layout is saved (unless the argument “Use the stored values” is 1).
        - Save signals (unsigned int32) automatically saves (0=False and 1=True) the signal configuration currently
        set in the Signals Manager if it has been changed.
        The signals configuration is stored in the Signals settings.ini file located in the Certificate folder.

        Return arguments (if Send response back flag is set to True when sending request message):
        - Error described in the Response message>Body section
        """

        return self.quickSend("Util.Quit", [Use_Stored_Values, Settings_Name, Layout_Name, Save_Signals], ["I", "+*c", "+*c", "I"], [])

    def Util_VersionGet(self):
        """
        Returns the version information of the Nanonis software.
        Arguments:
        None
        Return arguments (if Send response back flag is set to True when sending request message):
        - Product Line size (int) is the number of characters of the Product Line string
        - Product Line (string) returns “Nanonis SPM Control Software” or “Nanonis Tramea Software”.
        - Version size (int) is the number of characters of the Version string
        - Version (string) returns the software version (e.g. Generic 5)
        - Host App. Release (unsigned int32) returns the host application release number.
        - RT Engine release (unsigned int32) returns the RT Engine application release number.
        - Error described in the Response message>Body section
        """
        return self.quickSend("Util.VersionGet", [], [], ["+*c", "+*c", "I", "I"])

    def MCVA5_UserInSet(self, Preamp_Nr, Channel_Nr, User_Input):
        """
        MCVA5.UserInSet
        Assigns a user input to one of the four channels of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Channel Nr. (unsigned int16) is the channel number out of the four available channels in the MCVA5 preamplifier, where valid values are 1, 2, 3, 4
        - User Input (unsigned int32) is the user input number that will be assigned to the selected channel of the selected preamplifier  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("MCVA5.UserInSet", [Preamp_Nr, Channel_Nr, User_Input], ["H", "H", "I"], [])

    def MCVA5_UserInGet(self, Preamp_Nr, Channel_Nr):
        """
        MCVA5.UserInGet
        Returns the user input assigned to the selected channel of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Channel Nr. (unsigned int16) is the channel number out of the four available channels in the MCVA5 preamplifier, where valid values are 1, 2, 3, 4
        Return arguments (if Send response back flag is set to True when sending request message):
        - User Input (unsigned int32) is the user input number that is currently assigned to the selected channel of the selected preamplifier  )
        - Error described in the Response message>Body section
        """
        return self.quickSend("MCVA5.UserInGet", [Preamp_Nr, Channel_Nr], ["H", "H"], ["I"])

    def MCVA5_GainSet(self, Preamp_Nr, Channel_Nr, Gain):
        """
        MCVA5.GainSet
        Sets the gain of one of the four channels of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Channel Nr. (unsigned int16) is the channel number out of the four available channels in the MCVA5 preamplifier, where valid values are 1, 2, 3, 4
        - Gain (unsigned int16) is the gain that will be applied to the selected channel of the selected preamplifier, where 0=1, 1=10, 2=100, 3=1000  
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("MCVA5.GainSet", [Preamp_Nr, Channel_Nr, Gain], ["H", "H", "H"], [])

    def MCVA5_GainGet(self, Preamp_Nr, Channel_Nr):
        """
        MCVA5.GainGet
        Returns the gain applied to one of the four channels of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Channel Nr. (unsigned int16) is the channel number out of the four available channels in the MCVA5 preamplifier, where valid values are 1, 2, 3, 4
        Return arguments (if Send response back flag is set to True when sending request message):
        - Gain (unsigned int16) is the gain currently applied to the selected channel of the selected preamplifier, where 0=1, 1=10, 2=100, 3=1000    
        - Error described in the Response message>Body section
        """
        return self.quickSend("MCVA5.GainGet", [Preamp_Nr, Channel_Nr], ["H", "H"], ["H"])

    def MCVA5_InputModeSet(self, Preamp_Nr, Channel_Nr, Input_Mode):
        """
        MCVA5.InputModeSet
        Sets the input mode of one of the four channels of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Channel Nr. (unsigned int16) is the channel number out of the four available channels in the MCVA5 preamplifier, where valid values are 1, 2, 3, 4
        - Input mode (unsigned int16) is the input mode that will be applied to the selected channel of the selected preamplifier, where 0=A-B, 1=A, 2=GND
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("MCVA5.InputModeSet", [Preamp_Nr, Channel_Nr, Input_Mode], ["H", "H", "H"], [])

    def MCVA5_InputModeGet(self, Preamp_Nr, Channel_Nr):
        """
        MCVA5.InputModeGet
        Returns the input mode applied to one of the four channels of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Channel Nr. (unsigned int16) is the channel number out of the four available channels in the MCVA5 preamplifier, where valid values are 1, 2, 3, 4
        Return arguments (if Send response back flag is set to True when sending request message):
        - Input mode (unsigned int16) is the input mode currently applied to the selected channel of the selected preamplifier, where 0=A-B, 1=A, 2=GND
        - Error described in the Response message>Body section
        """
        return self.quickSend("MCVA5.InputModeGet", [Preamp_Nr, Channel_Nr], ["H", "H"], ["H"])


    def MCVA5_CouplingSet(self, Preamp_Nr, Channel_Nr, Coupling):
        """
        MCVA5.CouplingSet
        Sets the coupling mode of one of the four channels of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Channel Nr. (unsigned int16) is the channel number out of the four available channels in the MCVA5 preamplifier, where valid values are 1, 2, 3, 4
        - Coupling (unsigned int16) is the coupling mode that will be applied to the selected channel of the selected preamplifier, where 0=DC and 1=AC
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("MCVA5.CouplingSet", [Preamp_Nr, Channel_Nr, Coupling], ["H", "H", "H"], [])

    def MCVA5_CouplingGet(self, Preamp_Nr, Channel_Nr):
        """
        MCVA5.CouplingGet
        Returns the coupling mode of one of the four channels of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Channel Nr. (unsigned int16) is the channel number out of the four available channels in the MCVA5 preamplifier, where valid values are 1, 2, 3, 4
        Return arguments (if Send response back flag is set to True when sending request message):
        - Coupling (unsigned int16) is the coupling mode that applied to the selected channel of the selected preamplifier, where 0=DC and 1=AC
        - Error described in the Response message>Body section
        """
        return self.quickSend("MCVA5.CouplingGet", [Preamp_Nr, Channel_Nr], ["H", "H"], ["H"])

    def MCVA5_SingleStateUpdate(self, Preamp_Nr):
        """
        MCVA5.SingleStateUpdate
        Reads once the state of the selected preamplifier and returns the Ready and Overload states of all channels.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        Return arguments (if Send response back flag is set to True when sending request message):
        - Channel 1 Ready (unsigned int32) where 0=no ready, 1=ready
        - Channel 1 Overload (unsigned int32) where 0=not overload, 1=overload
        - Channel 2 Ready (unsigned int32) where 0=no ready, 1=ready
        - Channel 2 Overload (unsigned int32) where 0=not overload, 1=overload
        - Channel 3 Ready (unsigned int32) where 0=no ready, 1=ready
        - Channel 3 Overload (unsigned int32) where 0=not overload, 1=overload
        - Channel 4 Ready (unsigned int32) where 0=no ready, 1=ready
        - Channel 4 Overload (unsigned int32) where 0=not overload, 1=overload
        - Error described in the Response message>Body section
        """
        return self.quickSend("MCVA5.SingleStateUpdate", [Preamp_Nr], ["H"], ["i", "i", "i", "i", "i", "i", "i", "i"])

    def MCVA5_ContStateUpdateSet(self, Preamp_Nr, Continuous_Read):
        """
        MCVA5.ContStateUpdateSet
        Configures the selected preamplifier to read continuously the state of all channels.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Continuous Read (unsigned int32) where 0=false, 1=true
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("MCVA5.ContStateUpdateSet", [Preamp_Nr, Continuous_Read], ["H", "I"], [])

    def MCVA5_ContStateUpdateGet(self, Preamp_Nr):
        """
        MCVA5.ContStateUpdateGet
        Returns if the selected preamplifier is configured to read continuously the state of all channels.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        Return arguments (if Send response back flag is set to True when sending request message):
        - Continuous Read (unsigned int32) where 0=false, 1=true
        - Error described in the Response message>Body section
        """
        return self.quickSend("MCVA5.ContStateUpdateGet", [Preamp_Nr], ["H"], ["I"])

    def MCVA5_SingleTempUpdate(self, Preamp_Nr):
        """
        MCVA5.SingleTempUpdate
        Reads once the temperatures of all channels of the selected preamplifier.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        Return arguments (if Send response back flag is set to True when sending request message):
        - Channel 1 (unsigned int16) is the temperature in °C of Channel 1
        - Channel 2 (unsigned int16) is the temperature in °C of Channel 2
        - Channel 3 (unsigned int16) is the temperature in °C of Channel 3
        - Channel 4 (unsigned int16) is the temperature in °C of Channel 4
        - Error described in the Response message>Body section
        """
        return self.quickSend("MCVA5.SingleTempUpdate", [Preamp_Nr], ["H"], ["H", "H", "H", "H"])

    def MCVA5_ContTempUpdateSet(self, Preamp_Nr, Continuous_Read):
        """
        MCVA5.ContTempUpdateSet
        Configures the selected preamplifier to read continuously the temperature of all channels.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        - Continuous Read (unsigned int32) where 0=false, 1=true
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("MCVA5.ContTempUpdateSet", [Preamp_Nr, Continuous_Read], ["H", "I"], [])

    def MCVA5_ContTempUpdateGet(self, Preamp_Nr):
        """
        MCVA5.ContTempUpdateGet
        Returns if the selected preamplifier is configured to read continuously the temperature of all channels.
        Arguments:
        - Preamplifier Nr. (unsigned int16) is the preamplifier module number, where valid values are 1, 2, 3, 4
        Return arguments (if Send response back flag is set to True when sending request message):
        - Continuous Read (unsigned int32) where 0=false, 1=true
        - Error described in the Response message>Body section
        """
        return self.quickSend("MCVA5.ContTempUpdateGet", [Preamp_Nr], ["H"], ["I"])

    def PICtrl_OnOffSet(self, Controller_Index, Controller_Status):
        """
        PICtrl.OnOffSet
        Switches the Generic PI Controller On or Off.
        Arguments:
        - Controller index (int32) is the index of the controller. Valid values are 1 to 8.
        - Controller status (unsigned int32) switches the controller Off (=0) or On (=1)
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("PICtrl.OnOffSet", [Controller_Index, Controller_Status], ["i", "I"], [])

    def PICtrl_OnOffGet(self, Controller_Index):
        """
        PICtrl.OnOffGet
        Returns the status of the Generic PI Controller.
        Arguments:
        - Controller index (int32) is the index of the controller. Valid values are 1 to 8.
        Return arguments (if Send response back flag is set to True when sending request message):
        - Controller status (unsigned int32) indicates if the controller is Off (=0) or On (=1)
        - Error described in the Response message>Body section
        """
        return self.quickSend("PICtrl.OnOffGet", [Controller_Index], ["i"], ["I"])

    def PICtrl_CtrlChSet(self, Controller_Index, CtrlSignal_Index):
        """
        PICtrl.CtrlChSet
        Sets the index of the output controlled by the Generic PI controller.
        Arguments:
        - Controller index (int) is the index of the controller. Valid values are 1 to 8.
        - Control signal index (int) sets the output index to be used.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("PICtrl.CtrlChSet", [Controller_Index, CtrlSignal_Index], ["i", "i"], [])

    def PICtrl_CtrlChGet(self, Controller_Index):
        """
        PICtrl.CtrlChGet
        Gets the index of the output controlled by the Generic PI controller.
        Arguments:
        - Controller index (int) is the index of the controller. Valid values are 1 to 8.
        Return arguments (if Send response back flag is set to True when sending request message):
        - Control signal index (int) returns the output index to be used.
        - Control signals names size (int) is the size in bytes of the Control Signals Names array
        - Number of Control signals names (int) is the number of elements of the Control Signals Names array
        - Control signals names (1D array string) returns an array of Control Signals Names. Each element of the array is preceded by its size in bytes
        - Number of Control signals indexes (int) is the number of elements of the Control Signals Indexes array
        - Control signals indexes (1D array int) returns an array of Control Signals Indexes
        - Error described in the Response message>Body section
        """
        return self.quickSend("PICtrl.CtrlChGet", [Controller_Index], ["i"], ["i", "i", "i", "*+c", "i", "*i"])

    def PICtrl_InputChSet(self, Controller_Index, Input_Index):
        """
        PICtrl.InputChSet
        Sets the index of the input channel in the Generic PI controller.
        Arguments:
        - Controller index (int) is the index of the controller. Valid values are 1 to 8.
        - Input index (int) sets the input index to be used.
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("PICtrl.InputChSet", [Controller_Index, Input_Index], ["i", "i"], [])

    def PICtrl_InputChGet(self, Controller_Index):
        """
        PICtrl.InputChGet
        Gets the index of the input channel in the Generic PI controller.
        Arguments:
        - Controller index (int) is the index of the controller. Valid values are 1 to 8.
        Return arguments (if Send response back flag is set to True when sending request message):
        - Input index (int) returns the input index to be used.
        - Input signals names size (int) is the size in bytes of the Input Signals Names array
        - Number of Input signals names (int) is the number of elements of the Input Signals Names array
        - Input signals names (1D array string) returns an array of Input Signals Names. Each element of the array is preceded by its size in bytes
        - Number of Input signals indexes (int) is the number of elements of the Input Signals Indexes array
        - Input signals indexes (1D array int) returns an array of Input Signals Indexes
        - Error described in the Response message>Body section
        """
        return self.quickSend("PICtrl.InputChGet", [Controller_Index], ["i"], ["i", "i", "i", "*+c", "i", "*i"])

    def PICtrl_PropsSet(self, Controller_Index, Setpoint, P_Gain, I_Gain, Slope):
        """
        PICtrl.PropsSet
        Sets the properties of the Generic PI controller.
        Arguments:
        - Controller index (int32) is the index of the controller. Valid values are 1 to 8.
        - Setpoint (float32) 
        - P gain (float32) 
        - I gain (float32) 
        - Slope (unsigned int16) where 0 means no change, 1 means Positive, and 2 means Negative
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("PICtrl.PropsSet", [Controller_Index, Setpoint, P_Gain, I_Gain, Slope], ["i", "f", "f", "f", "H"], [])

    def PICtrl_PropsGet(self, Controller_Index):
        """
        PICtrl.PropsGet
        Gets the properties of the Generic PI controller.
        Arguments:
        - Controller index (int32) is the index of the controller. Valid values are 1 to 8.
        Return arguments (if Send response back flag is set to True when sending request message):
        - Setpoint (float32) 
        - P gain (float32) 
        - I gain (float32) 
        - Slope (unsigned int16) where 0 means Positive, and 1 means Negative
        - Error described in the Response message>Body section
        """
        return self.quickSend("PICtrl.PropsGet", [Controller_Index], ["i"], ["f", "f", "f", "H"])

    def PICtrl_CtrlChPropsSet(self, Controller_Index, Lower_Limit, Upper_Limit):
        """
        PICtrl.CtrlChPropsSet
        Sets the properties of the control signal in the Generic PI controller.
        Arguments:
        - Controller index (int32) is the index of the controller. Valid values are 1 to 8.
        - Lower_Limit (float32) 
        - Upper_Limit (float32) 
        
        Return arguments (if Send response back flag is set to True when sending request message):
        
        -- Error described in the Response message&gt;Body section
        
        """
        return self.quickSend("PICtrl.CtrlChPropsSet", [Controller_Index, Lower_Limit, Upper_Limit], ["i", "f", "f"], [])

    def PICtrl_CtrlChPropsGet(self, Controller_Index):
        """
        PICtrl.CtrlChPropsGet
        Gets the properties of the control signal in the Generic PI controller.
        Arguments:
        - Controller index (int32) is the index of the controller. Valid values are 1 to 8.
        Return arguments (if Send response back flag is set to True when sending request message):
        - Lower_Limit (float32) 
        - Upper_Limit (float32) 
        - Error described in the Response message>Body section
        """
        return self.quickSend("PICtrl.CtrlChPropsGet", [Controller_Index], ["i"], ["f", "f"])



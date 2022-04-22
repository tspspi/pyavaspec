import usb
import usb.core as usbcore

from matplotlib import pyplot as plt


# Only used for testing
import sys

# SIglent SiglentSDG1032X
import socket
import time

class NetworkException(Exception):
    pass

def close_event():
    # Only used during testing (remove from final code)
    plt.close()

class PyAvaSpecDeviceNotFoundException(Exception):
    pass

class PyAvaSpec_2048_2:
    CMD_GET_IDENT     = [ 0x0F ]
    CMD_2             = [ 0x10, 0x01 ]
    CMD_3             = [ 0x07, 0x01, 0x01 ]
    CMD_4             = [ 0x07, 0x08, 0x01 ]
    CMD_5             = [ 0x07, 0x09, 0x00 ]
    CMD_6             = [ 0x07, 0x0A, 0x01 ]
    CMD_7             = [ 0x10, 0x01 ]
    CMD_8             = [ 0x0A, 0x00 ]
    CMD_9             = [ 0x08, 0x00, 0x00, 0x00, 0xF1, 0x07 ]
    CMD_10            = [ 0x08, 0x01, 0x01, 0x00, 0x00, 0x00 ]
    CMD_READ_SPECTRUM = [ 0x03, 0xD2, 0x04, 0x0D, 0x00 ]
    CMD_STOP          = [ 0x07, 0x08, 0x00 ]

    def __init__(self):
        self.Device = usbcore.find(idVendor=0x1992, idProduct=0x0666)
        if(self.Device == None):
            raise PyAvaSpecDeviceNotFoundException("No AvaSpec-2048-2 device found")
        self.timeout = 120000
        self.adrWrite = 0x02
        self.adrRead = 0x82

        self.getVersionInformation()

    def writeDevice(self, payload):
        if self.Device == None:
            raise PyAvaSpecDeviceNotFoundException("Device is not connected")
        byteswritten = self.Device.write(self.adrWrite, payload, self.timeout)
        if byteswritten != len(payload):
            raise PyAvaSpecCommunicationError("Failed to transmit full payload ({} of {} bytes written)".format(byteswritten, len(payload)))
        return None

    def readDevice(self, numbytes = 0):
        if self.Device == None:
            raise PyAvaSpecDeviceNotFoundException("Device is not connected")
        if(numbytes == 0):
            # Try to read a full packet till we see a packet smaller than 64 bytes
            data = None
            while True:
                datablock = self.Device.read(self.adrRead, 64, self.timeout)
                if data == None:
                    data = datablock
                else:
                    data = data + datablock
                if len(datablock) != 64:
                    break
            if len(data) == 0:
                return None
            return data
        else:
            data = None
            while len(data) < numbytes:
                datablock = self.Device.read(self.adrRead, 64, self.timeout)
                if data == None:
                    data = datablock
                else:
                    data = data + datablock
            if len(data) != numbytes:
                return None
            return data

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if self.Device != None:
            usb.util.dispose_resources(self.Device)
            self.Device = None

    def close(self):
        if self.Device != None:
            self.writeDevice(self.CMD_STOP)
            self.readDevice()
            usb.util.dispose_resources(self.Device)
            self.Device = None

    def cmdMeasure(self, integrationTime = 1000, averageCount = 1):
        cmd = [ 0x03, integrationTime % 256, (integrationTime // 256) % 256, averageCount % 256, (averageCount // 256) % 256 ]
        self.writeDevice(cmd)
        readData = self.readDevice()
#        print(readData)
        dataBaseOffset = len(readData) - 2048*2
        newData = [ None ] * 2048
        for i in range(2048):
            pxFrequency = 280 + i * 0.546875 + 19.67
            pxValue = readData[dataBaseOffset + 2*i + 1] * 256 + readData[dataBaseOffset + 2*i]
            newData[i] = pxValue
        return newData

    def cmdMeasureSoftAverages(self, integrationTime = 1000, softAverages = 1, hardAverages = 1):
        data = None

        for iCapture in range(softAverages):
            newData = self.cmdMeasure(integrationTime, hardAverages)
            if data == None:
                data = newData
            else:
                for iData in range(len(data)):
                    data[iData] = ((float(data[iData]) * float(iCapture)) + float(newData[iData])) / float(iCapture + 1)
        return data

    def loadData(self, filename):
        data = []

        if not filename:
            raise ValueError("Missing filename")
        with open(filename, 'r') as f:
            lns = f.readlines()
            for line in lns:
                parts = line.strip().split()
                if len(parts) != 2:
                    continue
                data.append(int(parts[1]))
        return data


    def dumpData(self, data, filename = None, calibration = [0.546875, 299.67]):
        if not filename:
            for i in range(len(data)):
                pxFrequency = calibration[1] + i * calibration[0]
                pxVal = data[i]
                print("{} {}".format(pxFrequency, pxVal))
        else:
            with open(filename, 'w') as f:
                for i in range(len(data)):
                    pxFrequency = calibration[1] + i * calibration[0]
                    pxVal = data[i]
                    f.write("{} {}\n".format(pxFrequency, pxVal))

    def plotData(self, data, peaks = [], peakFwhmLine = False, xrange = None, calibration = [ 0.546875, 299.67 ], filename = None, fileformat = 'png', title = "Spectrometer output", showtimeout = 0):
        freqs = [ None ] * len(data)
        for i in range(len(data)):
            freqs[i] = calibration[1] + i * calibration[0]

        plt.clf()
        plt.title(title)
        plt.xlabel("Wavelength [nm]")
        plt.ylabel("Counts")

        if xrange:
            plt.xlim(xrange)

        plt.plot(freqs, data)
        if peaks:
            for pk in peaks:
                plt.plot(freqs[pk['idx']], data[pk['idx']], marker = "H")
                if peakFwhmLine:
                    plt.plot([freqs[pk['fwhm_leftidx']], freqs[pk['fwhm_rightidx']]], [data[pk['fwhm_leftidx']], data[pk['fwhm_rightidx']]])

        if filename:
            plt.savefig(filename, format = fileformat)
        else:
            if showtimeout > 0:
                fig = plt.figure()
                time = fig.canvas.new_timer(interval = showtimeout)
                timer.add_callback(close_event)
                timer.start()
            plt.show()

    def indexToWavelength(self, pixelIndex, calibration = [ 0.546875, 299.67 ]):
        return calibration[1] + calibration[0] * pixelIndex

    def applyMovingAverage(self, data, windowSize = 10):
        avgData = [ None ] * (len(data) - windowSize)
        for i in range(len(data) - windowSize):
            avgData[i] = data[i]
            for j in range(1, windowSize):
                avgData[i] = avgData[i] + data[i + j]
            avgData[i] = avgData[i] / windowSize
        return avgData

    def searchPeaks(self, data, maxPeaks = 10):
        peaks = []
        while len(peaks) < maxPeaks:
            maxPixelV = data[0]
            maxPixelI = 0

            # Plain linear maximum search
            for i in range(1, len(data)-1):
                if (data[i-1] < data[i]) and (data[i+1] < data[i]):
                    if maxPixelV < data[i]:
                        isPeak = True
                        # Check if we already found that peak ...
                        for pk in peaks:
                            if pk["idx"] == i:
                                isPeak = False
                                break
                        if isPeak:
                            maxPixelV = data[i]
                            maxPixelI = i
            # Check if this peak is over peak threshold ... (ToDo)
            peaks.append({ 'idx' : maxPixelI, 'counts' : maxPixelV, 'peak' : self.indexToWavelength(maxPixelI) })

        # For each peak determine FWHM
        for pk in peaks:
            halfMaxValid = True
            halfMax = pk['counts'] / 2.0
            halfMaxLeftI = pk['idx']
            halfMaxRightI = pk['idx']
            while (data[halfMaxLeftI] > halfMax) and (halfMaxLeftI > 0):
                halfMaxLeftI = halfMaxLeftI - 1
            while (data[halfMaxRightI] > halfMax) and (halfMaxRightI < (len(data) - 1)):
                halfMaxRightI = halfMaxRightI + 1

            if (halfMaxLeftI == 0) or (halfMaxRightI == len(data) - 1):
                halfMaxValid = False
            else:
                pk['fwhm_leftidx'] = halfMaxLeftI
                pk['fwhm_rightidx'] = halfMaxRightI
                pk['fwhm_left'] = self.indexToWavelength(halfMaxLeftI)
                pk['fwhm_right'] = self.indexToWavelength(halfMaxRightI)
                pk['fwhm'] = pk['fwhm_right'] - pk['fwhm_left']

        return peaks

    def getVersionInformation(self):
        self.writeDevice(self.CMD_GET_IDENT)
        self.readDevice()
        self.writeDevice(self.CMD_2)
        self.readDevice()
        self.writeDevice(self.CMD_3)
        self.readDevice()
        self.writeDevice(self.CMD_4)
        self.readDevice()
        self.writeDevice(self.CMD_5)
        self.readDevice()
        self.writeDevice(self.CMD_6)
        self.readDevice()
        self.writeDevice(self.CMD_7)
        self.readDevice()
        self.writeDevice(self.CMD_8)
        self.readDevice()
        self.writeDevice(self.CMD_9)
        self.readDevice()
        self.writeDevice(self.CMD_10)
        self.readDevice()
    def getDeviceConfig(self):
        pass

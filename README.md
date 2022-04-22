# Python script to access AvaSpec 2048-2 spectrometer

This is a (unofficial) library and tool to access basic functions (not all data types
are supported) of the Avaspec 2048-2 spectrometer from Python on platforms that are
not supported by the software supplied by the manufacturer. This has been developed
for a project where I wanted to use the spectrometer on FreeBSD (note that no reverse
engineering of the original software took place so I can not be sure this is
the proper way to talk to the spectrometer - the results just make sense). This
project is in no way associated with the manufacturer of this device!

__Warning__: This project currently applies a fixed calibration to the
spectrometers data. This might not be suited to any other spectrometer than the
one used by the original author of this software. There will be a configuration
option some time in future.

## The library interface

The spectrometer is exposed by the ```PyAvaSpec_2048_2``` class from
the ```pyavaspec.pyavaspec``` module. To use this class use

```
from pyavaspec.pyavaspec import PyAvaSpec_2048_2
```

To connect to a device one can simply instantiate the ```PyAvaSpec_2048_2```
class. This tries to locate the USB spectrometer by the vendor id ```0x1992```
and product ID ```0x0666```.

```
with PyAvaSpec_2048_2() as spec:
```

When not using the ```with``` construct one should close the spectrometer
manually in the end to prevent lingering resources:

```
spec = PyAvaSpec_2048_2()

# ...

spec.close()
```

| Function                                                                                                                                                                                    | Description                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ```cmdMeasure(integrationTime = 1000, averageCount = 1)```                                                                                                                                  | Performs a measurement                                                                                                                                                                                                          |
| ```cmdMeasureSoftAverages(integrationTime = 1000, softAverages = 1, hardAverages = 1)```                                                                                                    | Performs a measurement and applies software averaging                                                                                                                                                                           |
| ```dumpData(data, filename = None, calibration = [0.546875, 299.67])```                                                                                                                     | Dump the supplied data into a data file or to stdout                                                                                                                                                                            |
| ```plotData(data, peaks = [], peakFwhmLine = False, xrange = None, calibration = [ 0.546875, 299.67 ], filename = None, fileformat = 'png', title = "Spectrometer output", showtimeout = 0) | Plots the supplied data. One can add peaks previously found via ```searchPeaks```, zoom into a specific area via ```xrange```, supply ones own plot title, store the result in a file or display the plot only for a given time |
| ```indexToWavelength(pixelIndex, calibration = [ 0.546875, 299.67 ])```                                                                                                                     | Converts an index in the data array to a wavelength                                                                                                                                                                             |
| ```applyMovingAverage(data, windowSize = 10)```                                                                                                                                             | Applies a moving average filter to the data and returns a new data array.                                                                                                                                                       |
| ```searchPeaks(data, maxPeaks = 10)```                                                                                                                                                      | Performs peak search in the supplied data. One should already have done background subtraction and applied a moving average filter for this to work. Returns a list of peaks.                                                   |
| ```loadData(filename)```                                                                                                                                                                    | Loads a datafile and returns the data array                                                                                                                                                                                     |
| ```getVersionInformation()```                                                                                                                                                               | Will later be used to query version information from the spectrometer. Currently not functional                                                                                                                                 |

## The CLI utility

The CLI utility supports a set of options that one can supply:

### Commands

The spectrometer is controlled via a sequence of arbitrary commands that set
the status and execute actions.

| Command                    | Action                                                                                                                                                              |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| measure                    | Performs a measurement with the previous supplied settings as foreground data                                                                                       |
| measurebg                  | Performs a measurement with previous supplied settings as background data                                                                                           |
| inttime N                  | Sets the integration time (in milliseconds, default 1000)                                                                                                           |
| avgsoft N                  | Sets the number of software averages (default 1)                                                                                                                    |
| avghard N                  | Sets the number of hardware averages (default 1)                                                                                                                    |
| peakmaxcount N             | Sets the maximum number of peaks (default 10) to search while performing peak search                                                                                |
| peakavgwindow N            | Sets the size of the averaging window (default 10) while performing peak search                                                                                     |
| dump                       | Dump data of foreground signal to stdout                                                                                                                            |
| dumpbg                     | Dump data of background signal to stdout                                                                                                                            |
| dumppeak                   | Dump peak data to stdout                                                                                                                                            |
| dumpf [filename]           | Dumps the foreground data (corrected or uncorrected) into the supplied data file                                                                                    |
| dumpfbg [filename]         | Dumps the background data into the supplied data file                                                                                                               |
| dumpfpeak [filename]       | Dumps information about peaks into the supplied data file                                                                                                           |
| loadf [filename]           | Loads the specified datafile into the foreground data buffer                                                                                                        |
| loadfbg [filename]         | Loads the specified datafile into the background data buffer                                                                                                        |
| loadfpeaks [filename]      | Loads peak data from the specified data file                                                                                                                        |
| plotformat [svg,png]       | Selects the plot format to be ```png``` or ```svg```                                                                                                                |
| plotf [filename] [title]   | Plots the current available foreground data (corrected or uncorrected, found peaks if available) into the specified (PNG or SVG) file                               |
| plot [title]               | Plots the current available foreground data and shows it to the user                                                                                                |
| plotfbg [filename] [title] | Plots the current available background data into the specified (PNG or SVG) file                                                                                    |
| plotbg [title]             | Plots the current available background data and shows it to the user                                                                                                |
| moveavg                    | Apply a moving average filter to the foreground data                                                                                                                |
| bgsub                      | Performs background subtraction on the currently available foreground data if background data is available and background subtraction has not happened up until now |
| peaks                      | Performs peak search using the previously set parameters and stores information for the current foreground data (discarded on next foreground measurement)          |
| gateon                     | Enabled the external gate (for ex. SDG1032X)                                                                                                                        |
| gateoff                    | Disable the external gate (for ex. SDG1032X)                                                                                                                        |

### Settings: External SDG1032X control

The software allows one to control an external function generator (SDG1032X)
to enable or disable a light source. The communication is handled via
the [sdg1032x](https://github.com/tspspi/pysdg1032x) Python library. It's assumed
that most parameters (such as waveform, etc.) have already been set up since it
does not make much sense to scan those parameters while running the spectrometer
in most cases. This might be extended in later versions.

| Option           | Description                                                                      |
| ---------------- | -------------------------------------------------------------------------------- |
| --sdg1032xdev    | Supplies the hostname or IP address of the SDG1032X, enabled the SDG1032X module |
| --sdg1032xch     | Selects the channel (1 or 2) to gate, default 1                                  |
| --sdg1032xfrq    | Sets the frequency of the selected channel (in Hz)                               |
| --sdg1032xperiod | Sets the period of the selected channel (in Hz)                                  |

## Sample invocations

### Simple measurement and display

To simply run a measurement with default settings and display the result run:

```
avacli measure plot
```

### Measurement with background supression, store everything

The following command:

* Uses channel 2 of a SDG1032X function generator on 10.0.0.14 as gate
* Measures background
   * Stores the background data in ```background.dat```
   * Stores a plot of the background in ```background.png```
* Measures the signal
   * Stores the uncorrected raw signal in ```dataraw.dat```
   * Plots the uncorrected raw signal in ```dataraw.png```
* Performs background subtraction
   * Stores the intermediate result in ```datasub.dat```
   * Plots the intermediate result in ```datasub.png```
* Applies a moving average filter
   * Stores the intermediate result in ```dataavg.dat```
   * Plots the intermediate result in ```dataavg.png```
* Performs peak search
   * Stores peak data in ```peaks.dat```
   * Plots the corrected signal including the found peak in ```peaks.png```
   * Shows the plot to the user

```
avacli --sdg1032xdev 10.0.0.14 --sdg1032xch 2 gateoff measurebg dumpfbg background.dat plotfbg background.png "Background" gateon measure gateoff dumpf dataraw.dat plotf dataraw.png "Raw signal" bgsub dumpf datasub.dat plotf datasub.png "Background subtracted" moveavg dumpf dataavg.dat plotf dataavg.png "Averaged and subtracted signal" peaks plotf peaks.png "Peaks" dumpfpeak peaks.dat plot "Peaks"
```

### Loading previous data and generating SVGs

```
avacli loadfbg background.dat loadf dataraw.dat plotformat svg plotf dataraw.svg "Raw signal" plotfbg background.svg "Background" bgsub plotf datasub.svg "Background subtracted" moveavg plotf dataavg.svg "Averaged and subtracted signal" peaks plotf peaks.svg "Peaks"
```

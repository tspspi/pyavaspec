import sys
from pyavaspec.pyavaspec import PyAvaSpec_2048_2
from sdg1032x.sdg1032x import SDG1032X


class PyAvaSpecCliException(Exception):
    pass

class PyAvaSpecCli:
    def parsevalidate_inttime(self, i):
        try:
            inttime = int(sys.argv[i+1])
            if (inttime <= 0) or (inttime > 1000):
                raise PyAvaSpecCliException("Integration time should be in range from 1 to 1000ms")
        except ValueError:
            raise PyAvaSpecCliException("Integration time {} is not a valid numeric expression".format(sys.argv[i+1]))

    def parsevalidate_avgcount_soft(self, i):
        try:
            n = int(sys.argv[i+1])
            if (n < 1) or (n > 1000):
                raise PyAvaSpecCliException("Software average count should be at least 1 and maximum 1000 times")
        except ValueError:
            raise PyAvaSpecCliException("Software average count {} is not a valid numeric expression".format(sys.argv[i+1]))
    def parsevalidate_avgcount_hard(self, i):
        try:
            n = int(sys.argv[i+1])
            if (n < 1) or (n > 1):
                raise PyAvaSpecCliException("Hardware average count should be at least 1 and maximum 1 times")
        except ValueError:
            raise PyAvaSpecCliException("Hardware average count {} is not a valid numeric expression".format(sys.argv[i+1]))
    def parsevalidate_avgcount(self, i):
        try:
            n1 = int(sys.argv[i+1])
            n2 = int(sys.argv[i+2])
            if (n2 < 1) or (n2 > 1):
                raise PyAvaSpecCliException("Hardware average count should be at least 1 and maximum 1 times")
            if (n1 < 1) or (n1 > 1000):
                raise PyAvaSpecCliException("Software average count should be at least 1 and maximum 1000 times")
        except ValueError:
            raise PyAvaSpecCliException("Software average count {} or hardware average count {} is not a valid numeric expression".format(sys.argv[i+1], sys.argv[i+2]))
    def parsevalidate_peakmaxcount(self, i):
        try:
            n = int(sys.argv[i+1])
            if (n < 1) or (n > 100):
                raise PyAvaSpecCliException("Maximum peak count should be at least 1 and maximum 100 times")
        except ValueError:
            raise PyAvaSpecCliException("Maximum peak count {} is not a valid numeric expression".format(sys.argv[i+1]))
    def parsevalidate_peakavgwindow(self, i):
        try:
            n = int(sys.argv[i+1])
            if (n < 1) or (n > 100):
                raise PyAvaSpecCliException("Maximum average window size should be at least 1 and maximum 100 times")
        except ValueError:
            raise PyAvaSpecCliException("Maximum average window size {} is not a valid numeric expression".format(sys.argv[i+1]))
    def parsevalidate_plotformat(self, i):
        fmt = sys.argv[i+1]
        if (fmt != "png") and (fmt != "svg"):
            raise PyAvaSpecCliException("Plot format has to be either png or svg, format {} is unknown".format(fmt))

    def parsevalidate_sdg1032xCh(self, i):
        try:
            n = int(sys.argv[i+1])
            if (n < 1) or (n > 2):
                raise PyAvaSpecCliException("SDG1032X only supplied channels 1 and 2")
        except ValueError:
            raise PyAvaSpecCliException("SDG1032X channel {} is not a valid channel number".format(sys.argv[i+1]))
    def parsevalidate_sdg1032xFrq(self, i):
        try:
            n = float(sys.argv[i+1])
            if n < 0:
                raise PyAvaSpecCliException("SDG1032X frequency has to be positive")
        except ValueError:
            raise PyAvaSpecCliException("SDG1032X frequency {} is not a valid floating point expression".format(sys.argv[i+1]))
    def parsevalidate_sdg1032xPeriod(self, i):
        try:
            n = float(sys.argv[i+1])
            if n < 0:
                raise PyAvaSpecCliException("SDG1032X frequency has to be positive")
        except ValueError:
            raise PyAvaSpecCliException("SDG1032X frequency {} is not a valid floating point expression".format(sys.argv[i+1]))


    def exec_inttime(self, state, i):
        newinttime = int(sys.argv[i+1])
        state['cfg']['inttime'] = newinttime
        if state['cfg']['verbose']:
            print("Setting integration time to {} ms".format(newinttime))
        return state
    def exec_avgsoft(self, state, i):
        newsoftavg = int(sys.argv[i+1])
        state['cfg']['avgsoft'] = newsoftavg
        if state['cfg']['verbose']:
            print("Setting software averaging count to {}".format(newsoftavg))
        return state
    def exec_avghard(self, state, i):
        newhardavg = int(sys.argv[i+1])
        state['cfg']['avghard'] = newhardavg
        if state['cfg']['verbose']:
            print("Setting hardware averaging count to {}".format(newhardavg))
        return state
    def exec_avg(self, state, i):
        newsoftavg = int(sys.argv[i+1])
        newhardavg = int(sys.argv[i+2])
        state['cfg']['avghard'] = newhardavg
        state['cfg']['avgsoft'] = newsoftavg
        if state['cfg']['verbose']:
            print("Setting hardware averaging count to {}".format(newhardavg))
            print("Setting software averaging count to {}".format(newsoftavg))
        return state
    def exec_maxpeaks(self, state, i):
        newpeaks = int(sys.argv[i+1])
        state['cfg']['peakmaxcount'] = newpeaks
        if state['cfg']['verbose']:
            print("Setting maximum peak count to {}".format(newpeaks))
        return state
    def exec_peakavgwindow(self, state, i):
        newpeaks = int(sys.argv[i+1])
        state['cfg']['peakavgwindow'] = newpeaks
        if state['cfg']['verbose']:
            print("Setting peak search averaging window to {}".format(newpeaks))
        return state

    def exec_measure(self, state, i):
        # Run a measurement using out spectrometer and store in foreground data
        if state['cfg']['verbose']:
            print("Acquiring foreground data ...")
        if state['cfg']['avgsoft'] == 1:
            state['fgdata'] = self.spec.cmdMeasure(integrationTime = state['cfg']['inttime'], averageCount = state['cfg']['avghard'])
        else:
            state['fgdata'] = self.spec.cmdMeasureSoftAverages(integrationTime = state['cfg']['inttime'], softAverages = state['cfg']['avgsoft'], hardAverages = state['cfg']['avghard'])
        state['bgsubtracted'] = False
        if state['cfg']['verbose']:
            print("... done")
        return state

    def exec_measurebg(self, state, i):
        # Run a measurement using out spectrometer and store in background data
        if state['cfg']['verbose']:
            print("Acquiring background data ...")
        if state['cfg']['avgsoft'] == 1:
            state['bgdata'] = self.spec.cmdMeasure(integrationTime = state['cfg']['inttime'], averageCount = state['cfg']['avghard'])
        else:
            state['bgdata'] = self.spec.cmdMeasureSoftAverages(integrationTime = state['cfg']['inttime'], softAverages = state['cfg']['avgsoft'], hardAverages = state['cfg']['avghard'])
        if state['cfg']['verbose']:
            print("... done")
        return state

    def exec_dump(self, state, i):
        if state['cfg']['verbose']:
            print("Foreground data:")
        self.spec.dumpData(state['fgdata'])
        return state
    def exec_dumpbg(self, state, i):
        if state['cfg']['verbose']:
            print("Background data:")
        self.spec.dumpData(state['bgdata'])
        return state
    def exec_dumpf(self, state, i):
        if state['cfg']['verbose']:
            print("Dumping foreground data in {}".format(sys.argv[i+1]))
        self.spec.dumpData(state['fgdata'], filename = sys.argv[i+1])
        return state

    def exec_dumppeak(self, state, i):
        if not state['peaks']:
            if state['cfg']['verbose']:
                print("Cannot dump peak data - no peaks acquired")
            return state
        print("# peak fwhm idx counts fwhm_leftidx fwhm_rightidx fwhm_left fwhm_right")
        for pk in state['peaks']:
            print("{} {} {} {} {} {} {} {}".format(
                pk['peak'],
                pk['fwhm'],
                pk['idx'],
                pk['counts'],
                pk['fwhm_leftidx'],
                pk['fwhm_rightidx'],
                pk['fwhm_left'],
                pk['fwhm_right']
            ))
        return state

    def exec_dumpfpeak(self, state, i):
        if not state['peaks']:
            if state['cfg']['verbose']:
                print("Cannot dump peak data - no peaks acquired")
            return state
        if state['cfg']['verbose']:
            print("Dumping peak data into {}".format(sys.argv[i+1]))
        with open(sys.argv[i+1], 'w') as f:
            f.write("# peak fwhm idx counts fwhm_leftidx fwhm_rightidx fwhm_left fwhm_right\n")
            for pk in state['peaks']:
                f.write("{} {} {} {} {} {} {} {}\n".format(
                    pk['peak'],
                    pk['fwhm'],
                    pk['idx'],
                    pk['counts'],
                    pk['fwhm_leftidx'],
                    pk['fwhm_rightidx'],
                    pk['fwhm_left'],
                    pk['fwhm_right']
                ))
        return state

    def exec_loadfpeak(self, state, i):
        peaks = []

        if state['cfg']['verbose']:
            print("Loading peak data from {}".format(sys.argv[i+1]))
        with open(sys.argv[i+1], 'r') as f:
            lns = f.readlines()
            for i in range(1, len(lns)):
                parts = lns[i].split()
                if len(parts) != 8:
                    continue

                peaks.append({
                    'peak' : float(parts[0]),
                    'fwhm' : float(parts[1]),
                    'idx' : int(parts[2]),
                    'counts' : float(parts[3]),
                    'fwhm_leftidx' : int(parts[4]),
                    'fwhm_rightidx' : int(parts[5]),
                    'fwhm_left' : float(parts[6]),
                    'fwhm_right' : float(parts[7])
                })
        state['peaks'] = peaks
        return state

    def exec_loadf(self, state, i):
        if state['cfg']['verbose']:
            print("Loading foreground data from {}".format(sys.argv[i+1]))
        state['fgdata'] = self.spec.loadData(sys.argv[i+1])
        return state

    def exec_loadfbg(self, state, i):
        if state['cfg']['verbose']:
            print("Loading background data from {}".format(sys.argv[i+1]))
        state['bgdata'] = self.spec.loadData(sys.argv[i+1])
        return state


    def exec_dumpfbg(self, state, i):
        if state['cfg']['verbose']:
            print("Dumping background data in {}".format(sys.argv[i+1]))
        self.spec.dumpData(state['bgdata'], filename = sys.argv[i+1])
        return state
    def exec_plotfmt(self, state, i):
        newfmt = sys.argv[i+1]
        state['cfg']['plotformat'] = newfmt
        if state['cfg']['verbose']:
            print("Setting plot format to {}".format(newfmt))
        return state

    def exec_plot(self, state, i):
        self.spec.plotData(
            state['fgdata'],
            xrange = state['cfg']['xrange'],
            showtimeout = state['cfg']['plottimeout'],
            peaks = state['peaks'],
            title = sys.argv[i+1]
        )
        return state
    def exec_plotf(self, state, i):
        if state['cfg']['verbose']:
            print("Storing foreground data in plot {}".format(sys.argv[i+1]))
        self.spec.plotData(
            state['fgdata'],
            xrange = state['cfg']['xrange'],
            filename = sys.argv[i+1],
            fileformat = state['cfg']['plotformat'],
            peaks = state['peaks'],
            title = sys.argv[i+2]
        )
        return state
    def exec_plotbg(self, state, i):
        self.spec.plotData(
            state['bgdata'],
            xrange = state['cfg']['xrange'],
            showtimeout = state['cfg']['plottimeout'],
            title = sys.argv[i+1]
        )
        return state
    def exec_plotfbg(self, state, i):
        if state['cfg']['verbose']:
            print("Storing background data in plot {}".format(sys.argv[i+1]))
        self.spec.plotData(
            state['bgdata'],
            xrange = state['cfg']['xrange'],
            filename = sys.argv[i+1],
            fileformat = state['cfg']['plotformat'],
            title = sys.argv[i+2]
        )
        return state
    def exec_subbg(self, state, i):
        # Perform background subtraction
        if state['bgsubtracted']:
            if state['cfg']['verbose']:
                print("Skipping background subtraction - already performed")
            return state
        if not state['bgdata']:
            if state['cfg']['verbose']:
                print("Skipping background subtraction - no background data available")
            return state
        if not state['fgdata']:
            if state['cfg']['verbose']:
                print("Skipping background subtraction - no foreground data available")
            return state

        if state['cfg']['verbose']:
            print("Performing background subtraction")

        for i in range(len(state['fgdata'])):
            state['fgdata'][i] = state['fgdata'][i] - state['bgdata'][i]

        state['bgsubtracted'] = True

        return state
    def exec_moveavg(self, state, i):
        wndsize = state['cfg']['peakavgwindow']

        if not state['fgdata']:
            if state['cfg']['verbose']:
                print("Cannot perform moving average - no data present")
            return state
        if state['cfg']['verbose']:
            print("Performing moving average filtering on data (window size {})".format(wndsize))

        state['fgdata'] = self.spec.applyMovingAverage(state['fgdata'], windowSize = wndsize)
        return state

    def exec_peaks(self, state, i):
        if not state['fgdata']:
            if state['cfg']['verbose']:
                print("Cannot perform peak search - no data present")
            return state

        state['peaks'] = self.spec.searchPeaks(state['fgdata'], maxPeaks = state['cfg']['peakmaxcount'])
        return state

    def exec_SDG1032XDEV(self, state, i):
        if state['sdg1032x']:
            state['sdg1032x'].close()
            state['sdg1032x'] = None
            state['cfg']['sdg1032xdev'] = None

        if state['cfg']['verbose']:
            print("Connecting to SDG1032X at {}".format(sys.argv[i+1]))

        state['cfg']['sdg1032xdev'] = sys.argv[i+1]
        state['sdg1032x'] = SDG1032X(sys.argv[i+1])
        return state
    def exec_SDG1032XChannel(self, state, i):
        newchan = int(sys.argv[i+1])
        state['cfg']['sdg1032xch'] = newchan
        if state['cfg']['verbose']:
            print("Setting SDG1032X channel to {}".format(newchan))
        return state
    def exec_SDG1032XFrequency(self, state, i):
        newfreq = float(sys.argv[i+1])
        if not state['sdg1032x']:
            if state['cfg']['verbose']:
                print("Failed to set frequency on SDG1032X, not connected")
            return state
        if state['cfg']['verbose']:
            print("Setting SDG1032X frequency on channel {} to {} Hz".format(state['cfg']['sdg1032xch'], newfreq))
        state['sdg1032x'].setWaveFrequency(newfreq, state['cfg']['sdg1032xch'])
        return state
    def exec_SDG1032XPeriod(self, state, i):
        newfreq = float(sys.argv[i+1])
        if not state['sdg1032x']:
            if state['cfg']['verbose']:
                print("Failed to set period on SDG1032X, not connected")
            return state
        if state['cfg']['verbose']:
            print("Setting SDG1032X period on channel {} to {} s".format(state['cfg']['sdg1032xch'], newfreq))
        state['sdg1032x'].setWavePeriod(newfreq, channel = state['cfg']['sdg1032xch'])
        return state
    def exec_GateOn(self, state, i):
        if state['sdg1032x']:
            if state['cfg']['verbose']:
                print("Enabling channel {} on SDG1032X".format(state['cfg']['sdg1032xch']))
            state['sdg1032x'].outputEnable(channel = state['cfg']['sdg1032xch'])
        else:
            if state['cfg']['verbose']:
                print("Failed to enable gate, no control device connected")
        return state
    def exec_GateOff(self, state, i):
        if state['sdg1032x']:
            if state['cfg']['verbose']:
                print("Disabling channel {} on SDG1032X".format(state['cfg']['sdg1032xch']))
            state['sdg1032x'].outputDisable(channel = state['cfg']['sdg1032xch'])
        else:
            if state['cfg']['verbose']:
                print("Failed to disable gate, no control device connected")
        return state


    commandsAndOptions = {
        'inttime'          : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_inttime",       'exec' : "exec_inttime",           'desc' : "Set integration time in milliseconds"                                          },
        'avgsoft'          : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_avgcount_soft", 'exec' : "exec_avgsoft",           'desc' : "Set software averaging times (default 1)"                                      },
        'avghard'          : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_avgcount_hard", 'exec' : "exec_avghard",           'desc' : "Set hardware averaging times (default 1)"                                      },
        'avg'              : { 'nargs' : 2, 'parsevalidate' : "parsevalidate_avgcount",      'exec' : "exec_avg",               'desc' : "Set SOFTWARE and HARDWARE average (default 1 and 1)"                           },
        'peakmaxcount'     : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_peakmaxcount",  'exec' : "exec_maxpeaks",          'desc' : "Set maximum peak count during peak search (default 1)"                         },
        'peakavgwindow'    : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_peakavgwindow", 'exec' : "exec_peakavgwindow",     'desc' : "Set moving average window size (default 10)"                                   },
        'measure'          : { 'nargs' : 0,                                                  'exec' : "exec_measure",           'desc' : "Acquire signal"                                                                },
        'measurebg'        : { 'nargs' : 0,                                                  'exec' : "exec_measurebg",         'desc' : "Acquire background"                                                            },
        'loadf'            : { 'nargs' : 1,                                                  'exec' : "exec_loadf",             'desc' : "Load signal (foreground) from specified file"                                  },
        'loadfbg'          : { 'nargs' : 1,                                                  'exec' : "exec_loadfbg",           'desc' : "Load background from specified file"                                           },
        'loadfpeaks'       : { 'nargs' : 1,                                                  'exec' : "exec_loadfpeak",         'desc' : "Load peaks from specified file"                                                },
        'dump'             : { 'nargs' : 0,                                                  'exec' : "exec_dump",              'desc' : "Dump foreground to stdout"                                                     },
        'dumpbg'           : { 'nargs' : 0,                                                  'exec' : "exec_dumpbg",            'desc' : "Dump background to stdout"                                                     },
        'dumpf'            : { 'nargs' : 1,                                                  'exec' : "exec_dumpf",             'desc' : "Dump foreground data into supplied filename"                                   },
        'dumpfbg'          : { 'nargs' : 1,                                                  'exec' : "exec_dumpfbg",           'desc' : "Dump background data into supplied filename"                                   },
        'dumppeak'         : { 'nargs' : 0,                                                  'exec' : "exec_dumppeak",          'desc' : "Dump peak data on stdout"                                                      },
        'dumpfpeak'        : { 'nargs' : 1,                                                  'exec' : "exec_dumpfpeak",         'desc' : "Dump peak data into supplied filename"                                         },
        'plotformat'       : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_plotformat",    'exec' : "exec_plotfmt",           'desc' : "Select plot format png or svg"                                                 },
        'plotf'            : { 'nargs' : 2,                                                  'exec' : "exec_plotf",             'desc' : "Plot foreground (including subbg, moveavg, peaks) signal into specified file"  },
        'plotfbg'          : { 'nargs' : 2,                                                  'exec' : "exec_plotfbg",           'desc' : "Plot background into file with supplied filename"                              },
        'plot'             : { 'nargs' : 1,                                                  'exec' : "exec_plot",              'desc' : "Plot and display the recorded (and subbg / moveavg / peaks) foreground signal" },
        'plotbg'           : { 'nargs' : 1,                                                  'exec' : "exec_plotbg",            'desc' : "Plot and display the recorded background signal"                               },
        'bgsub'            : { 'nargs' : 0,                                                  'exec' : "exec_subbg",             'desc' : "Subtract recorded background"                                                  },
        'moveavg'          : { 'nargs' : 0,                                                  'exec' : "exec_moveavg",           'desc' : "Apply moving average filter"                                                   },
        'peaks'            : { 'nargs' : 0,                                                  'exec' : "exec_peaks",             'desc' : "Perform peak search (usually requires subbg and moveavg)"                      },
        'gateon'           : { 'nargs' : 0,                                                  'exec' : "exec_GateOn",            'desc' : "Enable attached gate (SDG1032X or similar) - enable light source"              },
        'gateoff'          : { 'nargs' : 0,                                                  'exec' : "exec_GateOff",           'desc' : "Disable attached gate (SDG1032X or similar) - i.e. disable light source"       },

        '--sdg1032xdev'    : { 'nargs' : 1,                                                  'exec' : "exec_SDG1032XDEV",       'desc' : "Select hostname or IP of SDG1032X function generator for gating"               },
        '--sdg1032xch'     : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_sdg1032xCh",    'exec' : "exec_SDG1032XChannel",   'desc' : "Set channel of SDG1032X function generator for gate function"                  },
        '--sdg1032xfrq'    : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_sdg1032xFrq",   'exec' : "exec_SDG1032XFrequency", 'desc' : "Set frequency of the SDG1032X function generator"                              },
        '--sdg1032xperiod' : { 'nargs' : 1, 'parsevalidate' : "parsevalidate_sdg1032xPeriod",'exec' : "exec_SDG1032XPeriod",   'desc' : "Sets the wave period of the SDG1032X function generator"                       }
    }

    def printUsage(self):
        print("Simple AvaSpec-2048-2 CLI tool")
        print("")
        print("This is an inofficial utility not related to the manufacturer")
        print("in any way! There is no guarantee this tool works correct and")
        print("it will only work in some specific modes (datatypes)!")
        print("")
        print("Supported commands:")
        print("")
        for cmd in self.commandsAndOptions:
            print("{}\t{}".format(cmd, self.commandsAndOptions[cmd]['desc']))

    def getDefaultConfiguration(self):
        return {
            'inttime'       : 1000,
            'avgsoft'       : 1,
            'avghard'       : 1,
            'peakmaxcount'  : 1,
            'peakavgwindow' : 10,
            'plotformat'    : 'png',
            'plottitle'     : 'Spectrometer output',
            'plottimeout'   : 0,

            'xrange'        : None,

            'sdg1032xdev'   : None,
            'sdg1032xch'    : 1,

            'verbose'       : True
        }
    def initializeState(self):
        return {
            'cfg'          : self.getDefaultConfiguration(),
            'bgdata'       : None,
            'fgdata'       : None,
            'peaks'        : None,
            'bgsubtracted' : False,
            'sdg1032x'     : None
        }

    def parseCommandOptions_Validation(self):
        skipEntries = 0
        for i in range(1, len(sys.argv)):
            if skipEntries > 0:
                skipEntries = skipEntries - 1
                continue
            cmd = sys.argv[i].strip()

            if not cmd in self.commandsAndOptions:
                raise PyAvaSpecCliException("Unknown command {}".format(cmd))

            if 'parsevalidate' in self.commandsAndOptions[cmd]:
                getattr(self, self.commandsAndOptions[cmd].get("parsevalidate"))(i)
            skipEntries = self.commandsAndOptions[cmd]['nargs']

    def executeCommands(self):
        state = self.initializeState()
        skipEntries = 0
        for i in range(1, len(sys.argv)):
            if skipEntries > 0:
                skipEntries = skipEntries - 1
                continue
            cmd = sys.argv[i].strip()
            if 'exec' in self.commandsAndOptions[cmd]:
                state = getattr(self, self.commandsAndOptions[cmd].get("exec"))(state, i)
            skipEntries = self.commandsAndOptions[cmd]['nargs']

    def __init__(self):
        self.spec = PyAvaSpec_2048_2()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self.spec:
            self.spec.close()
            self.spec = None

def mainProg():
    with PyAvaSpecCli() as cli:
        if len(sys.argv) < 2:
            cli.printUsage()
            return
        cli.parseCommandOptions_Validation()
        cli.executeCommands()

if __name__ == "__main__":
    mainProg()

# Measurement of SZYTF near UV LED

```
avacli plotformat svg measurebg dumpfbg background.dat plotfbg background.svg "Background" plotbg "Background" measure dumpf raw.dat plotf raw.svg "Raw signal" plot "Raw signal" bgsub moveavg peaks plotf peaks.svg "LED spectrum" plot "LED spectrum"
```

Later on generated the peaks data file:

```
avacli loadfbg background.dat loadf raw.dat bgsub moveavg peaks dumpfpeak peaks.dat
```

## Background

![Measured background](./background.svg)

## Raw signal

![Raw measured signal](./raw.svg)

## Peak detector

![Detected peaks](./peaks.svg)

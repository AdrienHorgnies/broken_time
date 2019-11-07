# broken_time

A python module to do maths with time !
It handles time mostly as a duration and not as a date (internally, it converts everything to seconds with midnight as a reference).

Very limited features as I had very limited needs (that were'nt met by standard packages though).

## Features

- Comparisons : <, <=, >, >=, ==, !=
- Arithmetic : +, -, *, /, //, %
- Parsing : BrokenTime.from_string('08:00:00') == '08:00:00'
- Iterable : BrokenTime.since('08:00:00').to('12:00:00').by('0:30:00')
- OverFlow : BrokenTime(23, 58, 59) + '1:00:61' == '25:00:00'

## Note

Much more complete solutions exists out there (panda with datetime64 being my recommendation).
I still coded it because I wanted to experiment and I required to be able to represent times such as '25:00:00'.
Such representations are used in some asian countries.
This specific instance means 1AM the day after.


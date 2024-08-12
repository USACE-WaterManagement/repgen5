# Basic Usage Guide

Learn how to run `repgen5` and use its basic features.

## Running the Program

To run `repgen5`, simply execute the following command in your terminal:

```bash
repgen5 --input <input_file> --output <output_file> -a https://cwms-data.usace.army.mil -O SWT
```

## Repgen5 Help Menu
```bash
usage: . [-h] [-V] [-i REPFILE] [-o REPOUTPUT] [-f DATAFILE] [-d DDMMMYYYY] [-t HHMM] [-z Time Zone Name] [-O OFFICE_ID] [-a IP_or_hostname:port[/basepath]] [-A IP_or_hostname:port[/basepath]] [-c] [-p] [--timeout TIMEOUT] [KEY=VALUE ...]
```

### Positional Arguments:
```bash
  KEY=VALUE             Additional key=value pairs. e.g. `DBTZ=UTC DBOFC=HEC`
    options:
    -h, --help            show this help message and exit
    -V, --version         print version number
    -i REPFILE, --in REPFILE
                            INput report file
    -o REPOUTPUT, --out REPOUTPUT
                            OUTput file with filled report
    -f DATAFILE, --file DATAFILE
                            Variable data file
    -d DDMMMYYYY, --date DDMMMYYYY
                            base date for data
    -t HHMM, --time HHMM  base time for data
    -z Time Zone Name, --tz Time Zone Name
                            default timezone; equivalent to `TZ=timezone`
    -O OFFICE_ID, --office OFFICE_ID
                            default office to use if not specified in report; equivalent to `DBOFC=OFFICE_ID`
    -a IP_or_hostname:port[/basepath], --address IP_or_hostname:port[/basepath]
                            location for data connections; equivalent to `DB=hostname:port/path`
    -A IP_or_hostname:port[/basepath], --alternate IP_or_hostname:port[/basepath]
                            alternate location for data connections, if the primary is unavailable (only for RADAR)
    -c, --compatibility   repgen4 compatibility; case-insensitive labels
    -p, --parallel        When this flag is setup Repgen5 will process requests in parallel with 10 threads.
    --timeout TIMEOUT     Socket timeout, in seconds
```
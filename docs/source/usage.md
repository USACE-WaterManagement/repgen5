# Program Use

Learn how to run `repgen5` and use its basic features.

## Running the Program

To run `repgen5`, simply execute the following command in your terminal:

```bash
repgen5 --input <input_file> --output <output_file> -a https://cwms-data.usace.army.mil -O SWT
```
Where `<input_file>` is a relative or absolute path to a text file with your repgen report input

**Note:** If you do not specify an `--output` argument the report will be appear in the terminal (standard output - stdout). Which can also be piped other places!

## Repgen5 Help Menu
```bash
usage: . [-h] [-V] [-i REPFILE] 
[-o REPOUTPUT] [-f DATAFILE] [-d DDMMMYYYY] 
[-t HHMM] [-z Time Zone Name] [-O OFFICE_ID] 
[-a IP_or_hostname:port[/basepath]] 
[-A IP_or_hostname:port[/basepath]] [-c] [-p]
[--timeout TIMEOUT] [KEY=VALUE ...]
Additional key=value pairs. e.g. `DBTZ=UTC DBOFC=HEC`
```

### Positional Arguments:
```bash          

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
    --timeout TIMEOUT     Socket timeout, in seconds
```
# E-SOH

## EURODEO

The RODEO project develops a user interface and Application Programming Interfaces (API) for accessing meteorological datasets declared as High Value Datasets (HVD) by the EU Implementing Regulation (EU) 2023/138 under the EU Open Data Directive (EU) 2019/1024. The project also fosters the engagement between data providers and data users for enhancing the understanding of technical solutions being available for sharing and accessing the HVD datasets.
This project provides a sustainable and standardized system for sharing real-time surface weather observations in line with the HVD regulation and WMO WIS 2.0 strategy. The real-time surface weather observations are made available through open web services, so that they can be accessed by anyone.

## Near real-time observational data

E-SOH is part of the RODEO project. The goal for this project is to make near real-time weather observations from land based station easily available. The data will be published on both a message queue using [MQTT](https://mqtt.org/) and [EDR](https://ogcapi.ogc.org/edr/) compliant APIs. Metadata will also be made available through [OGC Records](https://ogcapi.ogc.org/records/) APIs. The system architecture is portable, scalable and modular for taking into account possible future extensions to existing networks and datasets (e.g. 3rd party surface observations).

## RODEO BUFR Library

This tool handles the BUFR messages:
* ecoding the messages for E-SOH/openradardata ingestion
* providing E-SOH API output in BUFR format

The library suports [ECMWF ecCodes](https://confluence.ecmwf.int/display/ECC), [WMO](https://github.com/wmo-im/BUFR4/) and [OPERA](https://www.eumetnet.eu/observations/weather-radar-network/) BUFR tables.

## Installation
### Clone the repo

```shell
git clone https://github.com/EUMETNET/rodeo-bufr-library.git
```
### Compiling

Install requirements:
- make
- g++
- rapidjson-dev
- libeccodes-data
- python3-dev
- pybind11-dev
- python3-pybind11
```shell
cd rodeo-bufr-library/src/bufr_tools
make
```
### Usage

### Setting up BUFR table directory
#### ecCodes tables

To use the ecCodes table definitions you need to install libeccodes-data package on Debian based systems. In this case you don't have to set the BUFR_TABLE_DIR environment variable.

#### WMO tables
Download WMO tables with the script:
```shell
cd rodeo-bufr-library/src/tables/wmo
./get_wmo_tables.sh
export BUFR_TABLE_DIR=path_to_the_repo/rodeo-bufr-library/bufr/tables/wmo/
```
#### OPERA tables
```shell
export BUFR_TABLE_DIR=path_to_the_repo/rodeo-bufr-library/bufr/tables/opera/
```

### Printing BUFR content
Set Timezone to UTC
```shell
export TZ=UTC
```

#### Basic print
```shell
./bufrprint path_to_the_bufr_file(s)
```
#### Detail print
```shell
./printbufr detail path_to_the_bufr_file(s)
```
#### Log print
```shell
./printbufr log_print path_to_the_bufr_file(s)
```
### Making E-SOH json message
#### Set RODEO BUFR library Paths
Set RODEO BUFR path:
```shell
export RODEO_BUFR_DIR=path_to_the_repo/rodeo-bufr-library/
```
BUFR_TABLE_DIR is optional the default value is the eccodes: /usr/share/eccodes/definitions/bufr/tables/0/wmo/ .

ESOH_SCHEMA is optional, the default path:
```shell
${RODEO_BUFR_DIR}"/src/schemas/bufr_to_e_soh_message.json"
```
OSCAR_DUMP is the WMO Oscar database in json format. This is optional, the default value is:
```shell
${RODEO_BUFR_DIR}/"src/oscar/oscar_stations_all.json"
```

#### Set Time interval
The default time interval is the last 24 hours. The program skips the subsets from this interval. See the error message:
```shell
LOG: 2025-05-19T09:31:44.773387+00:00,Warning,msg,SurfaceLand_subset_1.buf,Skip subset 0, datetime too late or too early: 2023-08-22T22:00:00+00:00
```
Set the following environmental variables to disable the 24h interval:
```shell
export DYNAMICTIME=false
export LOTIME=1000-01-01T00:00:00Z
export HITIME=9999-12-31T23:59:59Z
```

#### Print E-SOH message
```shell
python3 ./create_mqtt_message_from_bufr.py path_to_the_bufr_file(s)
```

#### Dump BUFR content
```shell
python3 ./bufr2txt.py path_to_the_bufr_file(s)
```
#### Encode BUFR content from Coverage json
```shell
python3 ./covjson2bufr.py path_to_the_coverage_json_file(s)
```
The "default" BUFR unexpanded descriptors:
- 301150: WIGOS identifier
- 301090: Surface station identification; time, horizontal and vertical coordinates
- 302031: Pressure information
- 302035: Basic synoptic “instantaneous” data
- 302036: Clouds with bases below station leve
- 302042: Precipitation measurement
- 302040: Wind data
- 101002:
  - 302045: Radiation data


The encoded BUFR file name is test_out.bufr.

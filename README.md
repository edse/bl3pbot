# Bl3pBot
Bitcoin trading bot


## Requirements
- Python
- Virtualend
- Docker
- InfluxDB
- Graphana


## Install
git clone https://github.com/edse/bl3pbot.git


## Running
$ cd bl3pbot
$ make build
$ make up


## Running on Raspberry Pi
$ cd bl3pbot
$ make build-amr
$ make up


## TODO
    - Write unit tests
    - Add warmup period setting
    - Add trend threshold setting
    - Add trading sessions
        - Start session
        - Resume session
        - End session
        - report
    - Add Balance logs and charts
    - Add Performance logs and charts
    - Add buy and sell profit marging

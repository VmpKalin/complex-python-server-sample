# Local System Setup

## Requirements
- Docker and Docker compose
  - Installation instructions can be found [here](https://argentics.atlassian.net/wiki/spaces/LAST/pages/86310930/Install+Docker+Desktop+for+Windows)
- Python 3.11 (or newer)
  - Install 3.11 through the Microsoft App Store
- Pip

  `python -m ensurepip`

- VirtualEnv

  `pip install virtualenv`

# Project Setup
## 1. Virtual Env
Set up a virtual environment in this directory

`python -m venv venv`

Activate your virtualevn. This allows all packages installed in step 2 to be dedicated to this virtual workspace.

`.\venv\Scripts\activate.bat`

To deactivate your virtualenv

`deactivate`

## 2. Install Necessary Packages
Install all current package requirements

`python -m pip install -r requirements.txt`

## 3. Start the localdev observabiliy services

```
cd ..\imageTileServer & docker build -t imagetileserver --no-cache .
cd ..\deploy
docker-compose -f docker-compose.local.yml up -d
cd ..\..\demo
```

# Observe Some Logs

## 1. Open the Grafana web interface
1. View [this](http://localhost:3000/explore) url in a web browser
1. For viewing log messaging...
    1. Choose `Loki` from the dropdown next to the `Outline` button
    2. Add a `Label filter` of `application` `=` `DEMO`
    3. Run the query

## 2. Log some stuff
```
python demo.py -l DEBUG "debug log message"
python demo.py -l INFO "info log message"
python demo.py -l WARNING "warning log message"
python demo.py -l ERROR "error log message"
```

## 3. Observe those logs
(run the query again from the Grafana web interface)


# Prometheus Metrics
You can find two apps that can create dummy metrics
1. demo_prometheus_client_sample.py
  This app will create seperate server to which you should point you prometheus and prometheus will collect data from it. In this case, this app will be prometheus target to collect data from
2. demo_prometheus.py
  This app will push data to push_gateway service that will be up in docker, and prometheus will collect data from push_gateway service. In this case, push_gateway will be prometheus target to collect data from

![alt text](image.png)

You can find how it generally looks like on that picture.

1. Configuration
    1. To use demo_prometheus_client_sample.py app, you will need to replace ip with your IPv4 address for job: 'clientsample' in .\observability\deploy\prometheus.yml file
    2. After that you will need to up docker-compose
    3. View [this](http://localhost:9090/targets?search=) url in a web browser and you can see your targets

2. Metric creation
    1. Run any of these app to create metric: demo_prometheus_client_sample.py or demo_prometheus.py
    2. Depending on job you run, you will see different values in UI, see app comments to understand how it works

3. For viewing metrics...
    1. View [this](http://localhost:3000/explore) url in a web browser
    2. Choose `Prometheus` from the dropdown next to the `Outline` button
    3. Select a `Metric`, possible values: 'dummy_gauge_simple_metric', 'dummy_gauge_metrics', 'dummy_summary_metrics', 'request_processing_seconds'. Value will depend on app that you will run
    4. Run the query and play with filtration
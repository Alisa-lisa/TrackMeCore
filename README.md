# TrackMeCore
Main is an experimental branch with more analysis and some BE features, that are not yet on stable
Back-end functionality to collect personal data and run initial analysis
this is the back-end part of the app to track different aspects of the personal life 
and identify some useful patterns, correlations and trends to better adjust habits, routines and such


## Local setup

### Local DATABASE 
1. if you have PostgresDB running on your host machine, make sure you have `trackme` database created and given privileges to `root`:
```
CREATE DATABASE trackme;
CREATE USER root;
GRANT ALL PRIVELEGES ON DATABASE trackme TO root;
```
2. Adjust .env file (rename `.env.example` to `.env` or create it), use `.env.example` as a reference for needed values 
3. Create a configuration file for topics and attributes to track in the app. You can use `configuration_example.json` as a reference or read wiki for default setup (no configuration file supplied)

#### Docker start
1. (MacOS and Linux) run `make build`
2. in case you want to supply your own structure, run `make docker-migrate-own-config PATH=absolute_path_to_the_host_file`
3. in case you want to run default structure, run `make docker-migrate.default`
4. to start the backend app run `make run` and navigate to `localhost:5000/docs`

#### Local start
1. you will need python 3.9+ and [poetry](https://python-poetry.org/docs/#installation) installed
2. to setup dependencies for local run or development: `make local-setup`
3. to start the backend app run `make local-run` and navigate to `localhost:5000/docs`


## Container setup
TBD


## Development
within active poetry environment (after running `make local-setup` run `poetry shell` to activate python environment)
1. run linters: `make linter`
3. to generate openapi client for this server:
```
- save newest opeanpi.json to openapiclient folder
- run: make generate-client laguage=<deisred_language>
```
make sure you have [openapi-generator](https://github.com/OpenAPITools/openapi-generator) installed. Preferred way of installation is a package with OS specific package manager.


## Tests
!! tests are run on default data seeding !!
run: `make test`

## Motivation behind the project

This program is designed to combine several approaches from psychological research as well as ease of tracing.
Several information classes are predefined for an easier and more granular analysis. Although this split can cerate 
an information bias, where people have to choose slightly wrong form for their thoughts. 
I believe, that with categories held as abstract as possible and a possibility to customize this information, the bias will be insufficient.

More documentation about ideas and default structure can be found here: [wiki](https://github.com/Alisa-lisa/TrackMeCore/wiki)



## Future steps


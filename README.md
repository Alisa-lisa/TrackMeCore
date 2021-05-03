# TrackMeCore
Back-end functionality to collect personal data and run initial analysis
this is the back-end part of the app to track different aspects of the personal life 
and identify some useful patterns, correlations and trends to better adjust habits, routines and such


## Local setup
1. you will need python 3.9+ and [poetry](https://python-poetry.org/docs/#installation) installed
2. rename `.env.example` to `.env` and adjust the variables to your system configuration
3. to setup dependencies for local run or development: `make local-setup`
4. to run locally: `make local-run` and go to `localhost:5000/docs` to see OpenAPI docs 
5. to run locally-built docker: `make docker-run`

## Development
1. run linters: `make linter`
2. enable pre-commit hook: `pre-commit init` - now on `git commit` all linters will check the code


## Tests
run: `make test`

## Motivation behind the project


## Future steps


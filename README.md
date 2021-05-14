# TrackMeCore
Back-end functionality to collect personal data and run initial analysis
this is the back-end part of the app to track different aspects of the personal life 
and identify some useful patterns, correlations and trends to better adjust habits, routines and such


## Local setup

### DB
1. make sure you have postgres instance running
2. to prepare db access run:
```
CREATE DATABASE trackme;
CREATE USER root;
GRANT ALL PRIVELEGES ON DATABASE trackme TO root;
```

### Local dev
1. you will need python 3.9+ and [poetry](https://python-poetry.org/docs/#installation) installed
2. rename `.env.example` to `.env` and adjust the variables to your system configuration
3. to setup dependencies for local run or development: `make local-setup`
4. run `make db-up` to prepare db
4. to run locally: `make local-run` and go to `localhost:5000/docs` to see OpenAPI docs 


### Docker setup
1. run `make build`
2. to prepare db: `ocker run --rm --env-file .env --network="host" --name tb trackme alembic upgrade head`
3. and to run the app: `make run`

## Development
1. run linters: `make linter`
2. enable pre-commit hook: `pre-commit init` - now on `git commit` all linters will check the code


## Tests
run: `make test`

## Motivation behind the project

This program is designed to combine several approaches from psychological research as well as ease of tracing.
Several information classes are predefined for an easier and more granular analysis. Although this split can cerate 
an information bias, where people have to choose slightly wrong form for their thoughts. 
I believe, that with categories held as abstract as possible and a possibility to customize this information, the bias will be insufficient.

### Main topics and default attributes

#### MENTAL
Feelings, emotions, mood, etc.. Anything that can mainly be subjectively assessed by a person.

Default attributes:
* mood
* pain (psychosomatic or objectively non-identifyable)
* anxiety
* joy
* happiness
* calmness
* excitement
* fear
* motivation (this is a hard one, but would be nice to collect some initial data on a complex composite feature in a form of a self-provided proxy)

#### SOCIAL
All interactions with at least 2 "live" entities including yourself (family, pets, strangers, forums, etc.)

Default attributes:
* family
* pet
* friends
* online communication
* social events
* sport  (does not matter if you are an active participant)


#### PHYSICAL
Time consuming activities from simple to complex: routines, chores, common time spending and some healthy "suggestions"

Default attributes:
* sport
* sleep
* hygine procedures
* pain (physically evident)
* meditation
* walk
* chores

#### CONSUMMABLE
Everything a person can devour.

Default attributes:
* food
* alcohol
* soft drinks
* water (non-sweetened water is linked to multiple health benefits in contrast to other beverages)
* coffee (same reason as water to keep it separately)
* nicotine 
* meds (general term, ideally requires a comment for dosage/unit specification)





## Future steps


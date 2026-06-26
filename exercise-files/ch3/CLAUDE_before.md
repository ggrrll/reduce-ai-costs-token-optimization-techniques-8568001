# Project Guidelines for paykit

## Introduction and Background
Welcome to the paykit repository. This document is intended to give the assistant
a complete and thorough understanding of the project, its history, its goals, and
the way we like to work. Please read it carefully before making any changes.

paykit started in 2024 as a small internal experiment to wrap the Stripe API. Over
time it grew into the payments service that powers checkout across several of our
products. It is written in Python and has been maintained by the platform team.

## Detailed Architecture Description
The service is organized into modules. The payments module, located at the path
src/payments.py, contains the handlers for creating charges, issuing refunds, and
reading the status of a transaction. The cache module, located at src/cache.py, is
a thin wrapper around Redis that we use to cache transaction status so that we do
not have to call Stripe repeatedly. We use a time to live of sixty seconds.

## Coding Conventions (please follow these exactly)
We use Python version 3.12. We require type hints on all functions. We use ruff as
our linter and you should run it before finishing. We use pytest for testing and you
should run pytest -q before finishing. All monetary amounts must be represented as
integer cents, never as floating point numbers, because floating point math is not
safe for money. Every handler function should return a tuple of a status code and a
dictionary. For errors, raise a PayError with a code and a message, and the API layer
will translate that into an HTTP response. Always use the log helper for logging and
never use print statements anywhere in the codebase.

## How to Set Up Your Environment
First install the dependencies by running pip install -r requirements.txt. Then set
the STRIPE_KEY environment variable and the REDIS_URL environment variable. Then you
can run the tests with pytest -q. If you want to run the service locally you can use
the run script in the scripts directory.

## Notes, Tips, and Reminders for the Assistant
Please prefer editing existing functions over adding new files. Please keep your diffs
small and focused. Please match the existing style of the code exactly. Please do not
add any new dependencies without asking first. Please remember to run the linter and
the tests. Please be careful with money and always use integer cents. Please remember
that every handler returns a status code and a dictionary. Thank you very much.

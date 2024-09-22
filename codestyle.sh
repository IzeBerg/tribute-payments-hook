#!/usr/bin/env bash

black .
isort .
mypy .
ruff check .

#!/bin/bash

python3 manage.py runserver 0.0.0.0:8000 --noreload &

python3 home/api_search.py

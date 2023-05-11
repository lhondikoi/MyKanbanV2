#!/bin/bash

echo "Intializing celery workers"
celery -A main.celery worker -l info
#!/bin/bash

# Start celery beat
echo "Starting Celery Beat"
celery -A main.celery beat --max-interval 1 -l info
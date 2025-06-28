#!/bin/sh

celery -A scheduler.main worker --loglevel=info &
celery -A scheduler.main beat --loglevel=info
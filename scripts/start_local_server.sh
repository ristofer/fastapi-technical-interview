#!/bin/bash

HOST="127.0.0.1"
PORT="8008"
RELOAD="--reload"

uvicorn app.main:app --host $HOST --port $PORT $RELOAD

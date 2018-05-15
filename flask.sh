#!/bin/bash

export FLASK_APP=beefdeets/app.py
export FLASK_DEBUG=true
flask $@

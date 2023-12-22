#!/usr/bin/env bash
#PYTHONPATH=$HOME/mws/easyeda2kicad.py:$PYTHONPATH
#python3 -m easyeda2kicad --full --output ./libs/easyeda --lcsc_id="$1" --name="$2"
easyeda2kicad --full --output ./libs/easyeda --lcsc_id="$1"

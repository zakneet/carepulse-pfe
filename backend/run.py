#!/usr/bin/env python
"""Run Flask app without debug mode."""
import os
import sys

# Ensure debug mode is completely off
os.environ['FLASK_DEBUG'] = '0'
os.environ['FLASK_ENV'] = 'production'

from app import app, socketio, start_travel_notice_worker

start_travel_notice_worker()

if __name__ == '__main__':
    # Force no debug, no reloader
    socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False)

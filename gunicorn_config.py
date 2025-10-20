#!/usr/bin/env python3
"""
Gunicorn configuration file for CapCutAPI production deployment
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:9002"  # Production port
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 120
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "capcut_api"

# Server mechanics
daemon = False
pidfile = "/tmp/capcut_api.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in the future)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Performance tuning
worker_tmp_dir = "/dev/shm"
max_requests = 1000
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Graceful shutdown
graceful_timeout = 30

# Monitor workers (if needed)
# statsd_host = "localhost:8125"
# statsd_prefix = "capcut_api"

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'PYTHONUNBUFFERED=1'
]

def when_ready(server):
    """Called just before the master process is initialized."""
    server.log.info("CapCutAPI server is ready. Starting on %s", server.address)

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)
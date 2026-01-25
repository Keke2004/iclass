# Gunicorn config file
# Command to run: gunicorn --config gunicorn.conf.py iclass_server.wsgi

# The socket to bind to.
# A path to a Unix socket is recommended for security and performance.
bind = "unix:/tmp/gunicorn.sock"

# The number of worker processes for handling requests.
# A good starting point is (2 x $num_cores) + 1.
workers = 3

# The user and group to run as.
# user = "www-data"
# group = "www-data"

# The location of log files.
accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
loglevel = "info"

# Daemonize the Gunicorn process (run in background)
# daemon = True

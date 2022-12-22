export PATH=/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl:/home/ilya/.local/bin/
export PYTHONDONTWRITEBYTECODE=1
waitress-serve --port=5000 --threads=16 --call scutwork:create_app
#flask run --host=0.0.0.0

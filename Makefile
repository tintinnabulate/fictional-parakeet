all: local
deploy:
	appcfg.py -A foobar-1164 update app.yaml
local:
	dev_appserver.py --enable_sendmail True .

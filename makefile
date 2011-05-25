all:
	@echo "Install me baby: apxs -i -a -L/usr/local/lib -I/usr/local/include -lGeoIP -c mod_geoip.c"
#install:
#	apxs -i -a -L/usr/local/lib -I/usr/local/include -lGeoIP -c mod_geoip.c
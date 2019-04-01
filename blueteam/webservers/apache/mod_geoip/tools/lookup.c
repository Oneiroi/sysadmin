//#include <GeoIP.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/*int main (int argc, char **argv){
	char *datPath = NULL;
	char *lookupName = NULL;
	int c;
	int option_index = 0;
	
	while ((c = getopt(argc, argv, "fn:")) != -1) {
		switch (c) {
			case 'f':
				datPath = optarg;
				break;
			case 'n':
				lookupName = optarg;
				break;
			case '?':
				if (optopt == 'f')
					fprintf(stderr, "Option -%c requires an argument, a path to GeoIP.dat\n", optopt);
				else if (optopt == 'n')
					fprintf(stderr, "Option -%c requires an argument, an IP address or FQDN\n", optopt);
				return 1;
			default:
				abort();
		}
	}
	if(lookupName == NULL)
		fprintf(stderr,"Option -n is a required argument, i.e. %s -n google.com.\n", argv[0]);
		return 1;
	return 0;
}*/

// Quick hack by D.Busby 

int main (int argc, char *argv[]) {
  GeoIP * gi;
  gi = GeoIP_open("/root/GeoIP.dat", GEOIP_MEMORY_CACHE);
  printf("code %s\n",
    GeoIP_country_code_by_name(gi, argv[1]));
}


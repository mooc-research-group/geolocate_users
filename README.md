geolocate_users
===============

This Python script takes a .csv file containing IP addresses and appends geolocation data.


About
-----

Coursera allows users to fill in personal profiles where they can specify their geographic location. However, response rates are generally low (in our experience ~4.9%). Instead, by utilizing IP addresses which are recorded for each user in the "last_access_ip" field of the Coursera users table, we can obtain geolocation information for ~69.6% of users. In addition, we can also get city and zip code information as well as country data.

Files
-----

### GeoIP
This folder contains the free MaxMind GeoIP databases (http://www.maxmind.com/en/geolocation_landing) used to match IP addresses to geolocations:
* GeoIPCountryWhois
* GeoLiteCity-Blocks
* GeoLiteCity-Location
* region

#### users.csv

This input .csv file must contain a "last_access_ip" field in the header (it may contain as many other fields as desired). IP address entries must follow the same formatting practices as the "last_access_ip" field in the Coursera users export table, for example:
* 82.66.88.100
* 101.212.146.148, 37.228.105.209
* unknown, 93.186.30.243, 217.212.230.80

Results will be outputted to "users_ip.csv" and will contain all of the information in the original "users.csv" file along with additional geolocation data fields appended after the "last_access_ip" field. The following additional fields are added: 
* countryName
* locID
* country
* region
* city
* postalCode
* latitute
* longitude
* metroCode
* areaCode

#### geolocate_users.py

Run this file to generate "users_ip.csv"
* "users.csv" and the "GeoIP" folder must be in the same directory as "geolocate_users.py"
* The following Python libraries must be installed: csv, glob, os
* The script will first load all of the GeoIP databases into memory
* It will then sort "users.csv" by "last_access_ip" and output the results to a temporary file called "tmpfile.csv"
* Finally, the script will read in "tmpfile.csv" row-by-row and append geolocation data based on IP address, outputting the results to "users_ip.csv"

License
-------

Licensed under GPLv3. See LICENSE file for more details.

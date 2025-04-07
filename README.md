# User IP History

Queries Azure/Entra via GraphAPI to find the following:

- List of IP addresses signed into from a given user
- List of Users who have signed in from a given IP Address

Can accept single user or IP as an argument, or you can provide a text file of UserPrincipalNames (joe@example.com) or a text file of IP addresses

When providing text file inputs, the format is a simple text file, one entry per line.


## Installation
Install requirements, either as user or inside a virtual env

Obtain Maxmind Lite (free) databases - requires making a free account at maxmind.com:
https://dev.maxmind.com/geoip/geolite2-free-geolocation-data/


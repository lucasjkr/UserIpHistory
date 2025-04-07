import geoip2.database, json

class Maxmind:

    def __init__(self):
        pass

    def maxmind_geo(self):
        reader = geoip2.database.Reader('sources/GeoLite2-City_20250131/GeoLite2-City.mmdb', locales="[en]")
        return reader.city(self.ip).to_dict()

    def maxmind_asn(self):
        reader = geoip2.database.Reader('sources/GeoLite2-ASN_20250204/GeoLite2-ASN.mmdb')
        return reader.asn(self.ip).to_dict()

    def all(self, ip):
        self.ip = ip
        return {
            'entry':  ip,
            'continent_code': self.maxmind_geo()['continent']['code'],
            'continent': self.maxmind_geo()['continent']['names']['en'],

            'country_code': self.maxmind_geo()['country']['iso_code'],
            'country': self.maxmind_geo()['country']['names']['en'],

            'registered_country_code': self.maxmind_geo()['registered_country']['iso_code'],
            'registered_country': self.maxmind_geo()['registered_country']['names']['en'],

            'subdivision': self.maxmind_geo()['subdivisions'][0]['names']['en'],

            'city': self.maxmind_geo()['city']['names']['en'],
            'postal': self.maxmind_geo()['postal']['code'],

            'timezone': self.maxmind_geo()['location']['time_zone'],
            'longitude': self.maxmind_geo()['location']['longitude'],
            'latitude': self.maxmind_geo()['location']['latitude'],
            'accuracy': self.maxmind_geo()['location']['accuracy_radius'],

            'asn_id': self.maxmind_asn()['autonomous_system_number'],
            'an_org': self.maxmind_asn()['autonomous_system_organization'],
            'asn_network': self.maxmind_asn()['network']
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    maxmind = Maxmind()
    parser.add_argument('ip',
                        nargs='?',
                        help="IP address")

    arg = parser.parse_args()
    result = maxmind.all(arg.ip)

    print(json.dumps(result, indent=4))
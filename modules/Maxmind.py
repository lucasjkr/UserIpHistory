import geoip2.database, json

def __maxmind_geo(ip):
    reader = geoip2.database.Reader('sources/GeoLite2-City_20250131/GeoLite2-City.mmdb', locales="[en]")
    return reader.city(ip).to_dict()

def __maxmind_asn(ip):
    reader = geoip2.database.Reader('sources/GeoLite2-ASN_20250204/GeoLite2-ASN.mmdb')
    return reader.asn(ip).to_dict()

def geolookup(ip):

    result = {
        'ip': ip,
        'continent': "",
        'country': "",
        'subdivision': "",
        'city': "",
        'postal_code': "",
        'asn_id': "",
        'asn_org': "",
        'asn_network': ""
    }

    try:
        geocity = __maxmind_geo(ip)
        if 'continent' in geocity:
            result['continent'] = geocity['continent']['names']['en']

        if 'country' in geocity:
            result['country'] = geocity['country']['names']['en']

        if 'subdivisions' in geocity:
            result['subdivision'] = geocity['subdivisions'][0]['names']['en']

        if 'city' in geocity:
            result['city'] = geocity['city']['names']['en']

        if 'postal' in geocity:
            result['postal_code'] = geocity['postal']['code']

    except Exception:
        result['country'] = "NOT FOUND"

    try:
        asn = __maxmind_asn(ip)
        result['asn_id'] = asn['autonomous_system_number']
        result['asn_org'] = asn['autonomous_system_organization']
        result['asn_network'] = asn['network']
    except Exception:
        result['asn_org'] = "NOT FOUND"

    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('ip',
                        nargs='?',
                        help="IP address")

    arg = parser.parse_args()

    result = geolookup(arg.ip)

    print(json.dumps(result, indent=4))
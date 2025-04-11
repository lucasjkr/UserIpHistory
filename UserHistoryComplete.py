import argparse
from openpyxl import Workbook
from modules import ListOfDicts2Excel
from modules import MsGraphAuthenticator
from modules import Maxmind
from dotenv import dotenv_values
from pathlib import Path
import requests
import json

class UserHistory:
    def __init__(self):
        self.config = dotenv_values()
        self.user = None
        self.file = None
        self.result = []

    def bearer_token(self):
        return MsGraphAuthenticator.graph_bearer_token(
            tenant_id=self.config['TENANT_ID'],
            client_id=self.config['CLIENT_ID'],
            client_secret=self.config['SECRET'],
            scope=["https://graph.microsoft.com/.default"])

    def user_hunting_query(self, user):
        hunt = {
            'Query': f"""SigninLogs
                 | where UserPrincipalName == "{user}"
                 | where TimeGenerated > ago(90d)
                 | project TimeGenerated, UserDisplayName, UserPrincipalName, IPAddress, Identity, AppDisplayName, ResultType, ResultDescription, ResultSignature, AuthenticationDetails, DeviceDetail, MfaDetail, IsInteractive, Status, UserAgent
                 """
        }

        headers= {
            'Content-Type': 'application/json',
            'Authorization': self.bearer_token()
        }

        return requests.post("https://graph.microsoft.com/v1.0/security/runHuntingQuery",
            headers=headers,
            data=json.dumps(hunt)
        ).json()

    def geoip(self, ip):
        return Maxmind.geolookup(ip)

    def ips_by_user(self, user):
        logins = self.user_hunting_query(user)

        if 'results' not in logins:
            pass
        else:
            for login in logins['results']:
                ip = login['IPAddress']
                geo = self.geoip(ip)

                login['continent'] = geo['continent']
                login['country'] = geo['country']
                login['city'] = geo['city']
                login['state'] = geo['state']
                login['asn_id'] = geo['asn_id']
                login['asn_network'] = geo['asn_network']
                login['asn_org'] = geo['asn_org']
                if login not in self.result:
                    self.result.append(login)

    def process_users_file(self):
        i = 0

        # open input text file and break into lines (1 URL per line)
        # Url's can just be fqdn or entire fqdn with protocol and may include an optional port number
        with open(self.file, 'r') as file:
            users = [line.rstrip() for line in file]
            for user in users:
                # print which line of input you're on:
                i = i + 1
                print(f"\rRow: {i}", end='', flush=True)
                self.ips_by_user(user)

    def main(self):

        self.process_users_file()
        output = f"{Path(self.file).stem}.xlsx"

        if len(self.result) == 0:
            print("No results found.")
        else:
            # write results to a text file
            ListOfDicts2Excel.write_to_excel(self.result, output)

if __name__ == "__main__":
    user_history = UserHistory()

    args = argparse.ArgumentParser()
    args.add_argument("-uf", "--userfile",
                      nargs='?',
                      default=None,
                      help="File to look up users from")

    arg = args.parse_args()
    if arg.userfile:
        user_history.file = arg.userfile
        user_history.main()
    else:
        print("""you must run this program with --userfile argument:
        python3 UserHistory.ph --userfile input_file.txt""")
    print("done!")
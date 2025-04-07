import argparse
from openpyxl import Workbook
from modules import MsGraphAuthenticator
from modules import Maxmind
from dotenv import dotenv_values
import requests
import json

class UserIps:
    def __init__(self):
        self.config = dotenv_values()
        self.user = None
        self.file = None
        self.ip = None
        self.ip_file = None
        self.result = []

    def bearer_token(self):
        return MsGraphAuthenticator.graph_bearer_token(
            tenant_id=self.config['TENANT_ID'],
            client_id=self.config['CLIENT_ID'],
            secret=self.config['SECRET'],
            scope=["https://graph.microsoft.com/.default"])

    def user_hunting_query(self, user):
        hunt = {
            'Query': f"""SigninLogs
                 | where UserPrincipalName == "{user}"
                 | where TimeGenerated > ago(3d)
                 | distinct UserPrincipalName, IPAddress, ResultSignature
                 """
        }

        headers= {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.bearer_token()
        }

        response = requests.post("https://graph.microsoft.com/v1.0/security/runHuntingQuery",
            headers=headers,
            data=json.dumps(hunt)
        ).json()
        return response

    def ip_hunting_query(self, ip):
        hunt = {
            'Query': f"""SigninLogs
                 | where IPAddress == "{ip}"
                 | where TimeGenerated > ago(3d)
                 | distinct UserPrincipalName, IPAddress
                 """
        }

        headers= {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.bearer_token()
        }

        response = requests.post("https://graph.microsoft.com/v1.0/security/runHuntingQuery",
            headers=headers,
            data=json.dumps(hunt)
        ).json()
        return response

    def geoip(self, ip):
        mm = Maxmind.Maxmind()
        return mm.all(ip)

    def ips_by_user(self, user):
        logins = self.user_hunting_query(user)['results']
        for login in logins:
            ip = login['IPAddress']
            geo = self.geoip(ip)

            login['continent'] = geo['continent']
            login['country'] = geo['country']
            login['city'] = geo['city']
            login['state'] = geo['subdivision']
            login['asn_id'] = geo['asn_id']
            login['asn_network'] = geo['asn_network']
            login['asn_org'] = geo['asn_org']
            if login not in self.result:
                self.result.append(login)

    def users_by_ip(self, ip):
        logins = self.ip_hunting_query(ip)['results']
        for login in logins:
            ip = login['IPAddress']
            geo = self.geoip(ip)

            login['continent'] = geo['continent']
            login['country'] = geo['country']
            login['city'] = geo['city']
            login['state'] = geo['subdivision']
            login['asn_id'] = geo['asn_id']
            login['asn_network'] = geo['asn_network']
            login['asn_org'] = geo['asn_org']
            if login not in self.result:
                self.result.append(login)

    def process_users_file(self):
        # create empty list to insert all results into
        result = []
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

    def process_ip_file(self):
        # create empty list to insert all results into
        result = []
        i = 0

        # open input text file and break into lines (1 URL per line)
        # Url's can just be fqdn or entire fqdn with protocol and may include an optional port number
        with open(self.ip_file, 'r') as file:
            ips = [line.rstrip() for line in file]
            for ip in ips:
                # print which line of input you're on:
                i = i + 1
                print(f"\rRow: {i}", end='', flush=True)
                self.users_by_ip(ip)

    def write_to_excel(self, results):
        workbook = Workbook()

        for result in results:
            if result is None:
                continue
            else:
                # If sheet named 'Data' does not exist, create it
                if 'Data' not in workbook:
                    worksheet = workbook.create_sheet(title='Data')
                    worksheet.append([key for key in result])

                # Insert the row of values that need to be inserted (action happens whether header row was created or not
                if result is not None:
                    worksheet = workbook['Data']
                    worksheet.append(list(result.values()))

        # format the resulting spreadsheet
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.0
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # Freeze top rows
        worksheet.freeze_panes = 'A2'
        workbook.remove(workbook['Sheet'])
        workbook.save("output.xlsx")

    def main(self):
        if self.file is not None:
            self.process_users_file()
        elif self.user is not None:
            self.ips_by_user(self.user)
        elif self.ip_file is not None:
            self.process_ip_file()
        elif self.ip is not None:
            self.users_by_ip(self.ip)

        if len(self.result) == 0:
            print("No results found.")
        else:
            # write results to a text file
            self.write_to_excel(self.result)


if __name__ == "__main__":
    test = UserIps()

    args = argparse.ArgumentParser()
    args.add_argument("-u", "--user",
                      nargs='?',
                      default=None,
                      help="User to lookup")
    args.add_argument("-uf", "--userfile",
                      nargs='?',
                      default=None,
                      help="File to look up users from")
    args.add_argument("-i", "--ip",
                      nargs='?',
                      default=None,
                      help="IP to lookup sign-ins from")
    args.add_argument("--ipfile",
                      nargs='?',
                      default=None,
                      help="IP list to lookup sign-ins from")

    arg = args.parse_args()
    if arg.user:
        test.user = arg.user
        test.main()
    elif arg.userfile:
        test.file = arg.userfile
        test.main()
    elif arg.ip:
        test.ip = arg.ip
        test.main()
    elif arg.ipfile:
        test.ip_file = arg.ipfile
        test.main()

    else:
        print("""you must run this program with --file or --user arguments:
        --file input_file.txt
        --user user@example.com""")
    print("done!")
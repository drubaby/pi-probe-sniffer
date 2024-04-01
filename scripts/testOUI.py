import csv
import json
import os
import sys

# needed to find db module
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import supabase_utils

# load_dotenv()
# url = os.getenv("SUPABASE_URL")
# key = os.getenv("SUPABASE_SECRET_KEY")
client = supabase_utils.create_supabase_client()


# def get_known_devices(supabase):
#     data = supabase.table("known_devices").select("mac", "name", "is_trusted").execute()
#     return json.dumps(data.data)


"""
Debugging script which tests that knownlist.json is getting added to the OUIMEM dictionary.
Probably don't need to keep this in final package
"""

# OUIMEM = {}
# # KNOWN_LIST = json.load('knownlist.json')
# with open("knownlist.json", "r") as known_list:
#     known_dict = json.load(known_list)
#     for item in known_dict.items():
#         key = item[0].replace("-", ":").lower()
#         OUIMEM[key] = item[1]
# with open(
#     "OUI.txt",
#     "r",
# ) as OUILookup:

#     # for line in csv.reader(OUILookup, delimiter='\t'):
#     #     if not line or line[0][0] == "#":
#     #         continue
#     #     else:
#     #         # print("line", line)
#     #         # print('stripped', line[0].rstrip(" "))
#     #         OUIMEM[line[0].rstrip(" ")] = line[2]
#     #         # break
#     print(OUIMEM)
#     # print(OUIMEM.get('84:B8:66'))
#     print("Upper case: ", OUIMEM.get("8E:D1:34:B3:31:D3"))
#     print("Lower case: ", OUIMEM.get("8e:d1:34:b3:31:d3"))
#     print("mac: ", OUIMEM.get("Ac:c9:06:26:2b:9c".lower()))

#     # Write OUIMEM to file for testing
#     # with open("OUIMEM.txt", "w") as newfile:
#     #     json.dump(OUIMEM, newfile)
#     #     newfile.close()

known_devs = supabase_utils.get_trusted_devices(client)
print(type(known_devs))

OUIMEM = {}
known_dict = json.loads(known_devs)
print("Known dict type: ", type(known_dict))
print("Known dict: ", known_dict)
for item in known_dict:
    OUIMEM[item["mac"].lower()] = item["name"]

print("OUIMEM: ", OUIMEM)

print("Upper case: ", OUIMEM.get("8E:D1:34:B3:31:D3"))
print("Lower case: ", OUIMEM.get("8e:d1:34:b3:31:d3"))
print("mac: ", OUIMEM.get("Ac:c9:06:26:2b:9c".lower()))

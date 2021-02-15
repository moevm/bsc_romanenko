import json

nameFile = input("File path: \n")

with open(nameFile, 'r') as sfm:
    data = sfm.read()

obj = json.loads(data)

for landmark in obj["structure"]:
    if landmark["descType"] == "cctag3":
        print(landmark["X"])
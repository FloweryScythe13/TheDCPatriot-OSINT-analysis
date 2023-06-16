import argparse
import json
import base64
from typing import List
from nullsafe import undefined, _

def parse_graphql_file(file: str) -> List[dict]:
    arr = []
    with open(file, "r") as f:
        splitted = f.readlines()
        for line in splitted:
            if line.startswith('{"data":{"group":'):
                try:
                    a = json.loads(line) 
                    for i in a['data']['group']['group_admin_profiles']['edges']: 
                        arr.append({"name":i['node']['name'],"link":i['node']['url'],"profile_pic":i['node']['profile_picture']['uri'],"role":'admin/moderator'})

                except Exception as ex:
                    print(ex)
                    
            elif line.startswith('{"data":{"node":'):
                try:
                    a = json.loads(line) 
                    for i in a['data']['node']['new_forum_members']['edges']: 
                        description = _(i['node']['bio_text'])['text'] 
                        arr.append(
                            {
                                "name":i['node']['name'],
                                "link":i['node']['url'],
                                "profile_pic":i['node']['profile_picture']['uri'],
                                "joined":i['membership']['join_status_text']['text'],
                                "description":description if description is not undefined else None
                            }
                        )

                except Exception as ex:
                    print(ex)
                    
    return arr

def parse_and_save_files(source_files: List[str], dest_files: List[str], group_names: List[str]):
    for source_file, dest_file, group_name in zip(source_files, dest_files, group_names):
        members_arr = {group_name: []}
        members_arr[group_name].extend(parse_graphql_file(source_file))

        with open(dest_file, 'w') as f:
            json.dump(members_arr, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--source_files', nargs='+', help='Source file paths')
    parser.add_argument('--dest_files', nargs='+', help='Destination file paths')
    parser.add_argument('--group_names', nargs='+', help='Group names')

    args = parser.parse_args()

    parse_and_save_files(args.source_files, args.dest_files, args.group_names)

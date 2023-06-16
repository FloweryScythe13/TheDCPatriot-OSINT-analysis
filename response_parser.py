import json
import base64
import argparse


def parse_responses(source_file: str, dest_file: str, mode: str):
    arr = {f'{dest_file.split(".")[0]}':[]} if mode == 'json' else None
    decoded_resp_arr = []
    end_json = {"name":"","info":"","profile_pic":""}

    with open (source_file, 'r') as f:
        splitted = f.readlines()
        for line in splitted:
            if line.strip().startswith('<response base64="true">') and not line.strip().startswith('<response base64="true"></response'):
                try:
                    resp = line.strip().removeprefix('<response base64="true"><![CDATA[').split("]]><")
                    resp_line = base64.b64decode(resp[0]).decode('utf-8')            
                    resp_splitted = resp_line.split("\r\n\r\n")

                
                    for line2 in resp_splitted:
                        if line2.startswith('{"data":'):
                            next = line2.split("]]><")
                            try:
                                if mode == 'jsonl': 
                                    decoded_resp_arr.append(next[0] + '\n')
                                elif mode == 'json':                            
                                    a = json.loads(next[0]) #a['data']['node']['group_member_discovery']['edges']   i['node']['name']/['url']/['profile_picture']['uri']/['bio_text']['text'](OR ['timeline_context_items']['edges'] i['node']['title']['text'])
                                    for i in a['data']['node']['new_forum_members']['edges']: # a['data']['node']['comet_hovercard_renderer']['user']  ['name']/['url']/[profile_picture]['uri']
                                        _ = [x['text'] for x in i['node']['bio_text'] if x is not None]
                                        description = _[0] if _ else None
                                        arr[f'{dest_file.split(".")[0]}'].append({"name":i['node']['name'],"link":i['node']['url'],"profile_pic":i['node']['profile_picture']['uri'],"joined":i['membership']['join_status_text']['text'], "description": description})
                            except Exception as e:
                                print(e)
                except Exception as ex:
                    print(ex)

    if mode == 'jsonl':
        with open(dest_file, 'w') as f:
            for item in decoded_resp_arr:
                f.write(item)
    elif mode == 'json':
        with open(dest_file, 'w') as f:
            json.dump(arr, f, indent=4)


    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--source_file', type=str, help='Source file path')
    parser.add_argument('--dest_file', type=str, help='Destination file path')
    parser.add_argument('--mode', type=str, choices=['json', 'jsonl'], help='Output mode')
    

    args = parser.parse_args()

    parse_responses(args.source_file, args.dest_file, args.mode)
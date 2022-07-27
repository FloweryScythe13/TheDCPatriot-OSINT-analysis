from cgi import print_exception
import json
import base64

arr = {'TrumpPOTUS1':[]}
decoded_resp_arr = []
end_json = {"name":"","info":"","profile_pic":""}

with open ('data/fb_group_scraped_data/Woo the People GraphQL members HTTP response data - full (encoded)', 'r') as f:
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
                            decoded_resp_arr.append(next[0] + '\n')                            
                            #a = json.loads(next[0]) #a['data']['node']['group_member_discovery']['edges']   i['node']['name']/['url']/['profile_picture']['uri']/['bio_text']['text'](OR ['timeline_context_items']['edges'] i['node']['title']['text'])
                            # for i in a['data']['node']['new_forum_members']['edges']: # a['data']['node']['comet_hovercard_renderer']['user']  ['name']/['url']/[profile_picture]['uri']
                            #     #description = _[0] if (_:= [x['text'] for x in i['node']['bio_text'] if x is not None]) else None
                            #     arr['TrumpPOTUS1'].append({"name":i['node']['name'],"link":i['node']['url'],"profile_pic":i['node']['profile_picture']['uri'],"joined":i['membership']['join_status_text']['text']})
                        except Exception as e:
                            print(e)
            except Exception as ex:
                print(ex)

with open('data/fb_group_scraped_data/Woo the People response data - full.jsonl', 'w') as f:
    for item in decoded_resp_arr:
        f.write(item)

# with open('data/fb_group_scraped_data/TrumpPOTUS1.json', 'w') as f:
#     json.dump(arr, f, indent=4)
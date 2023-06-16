import pandas as pd
import httpx
import asyncio
from typing import Dict, List, Any
import json
import numpy as np
from nullsafe import undefined, _


'''
Task: Extract geocoordinates from the dataframe and enhance the dataframe with the resulting geospatial information. 

Step 1: For each record or group of records, make a call out to an external API provider. The API provider response should 
        include a latitude and longitude coordinate for the supplied location description. Add it to a list of processed
        responses. 
Step 2: When the list of response coordinates is complete, join it back onto the dataframe.
Step 3: With the expanded dataframe of coordinates, save it to another intermediary CSV file for creating a new spatially-enabled dataframe that includes the Shape data 
        object for each lat-long coordinate pair. 
'''



# groupings = df.loc[:, ["type", "description", "lang", "location", "occupation", "misc_ents"]].groupby("location")

url = "https://knowledgeminingcustomskills-dev.azurewebsites.net/api/geo-point-from-name?code=qmgxu3nOgRj-3_GTz6khNvNpXjjh1FNj_kYu8cMQKy7IAzFuz8muiQ=="


async def get_geocoordinates(name: str):
    '''Get the geocoordinates for a given location name from an Azure Function API.'''
    if name and not name.isspace():
        input = {"values": [{"recordId": "something", "data": {"address": name}}]}
        try:
            resp = await httpx.post(url, json=input)
            resp.raise_for_status()
            response = resp.json()
        except httpx.HTTPError as http_err:
            print(f"Error has occurred: {http_err}")
        except json.decoder.JSONDecodeError as json_err:
            print(f"Error has occurred: {json_err}")
        finally: 
            return response
    return

async def get_geocooordinates_batched_values(request: Dict):
    try:
        resp = httpx.post(url, json=request, timeout=httpx.Timeout(15.0))
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as http_err:
        print(f"Error has occurred: {http_err}")
    except json.decoder.JSONDecodeError as json_err:
        print(f"Error has occurred: {json_err}")


async def get_geocoordinates_batched(names: pd.Series): #change the parameter type to Series 
    '''Get the geocoordinates for a list of location names from an Azure Function API.'''
    input_values = []
    for index, name in names.items():
        if (name and name is not np.nan and not name.isspace()):
            input_values.append({"recordId": index, "data": {"address": name}})
    input = {"values": input_values}
    response = await get_geocooordinates_batched_values(input)
    if response is not None: 
        response_values = response["values"]
        parsed_records = pd.DataFrame.from_records(response_values, index="recordId")
        parsed_records.index = parsed_records.index.astype(np.int64)
        coord_df = pd.json_normalize(parsed_records["data"])
        coords = [x if isinstance(x, list) else [x] for x in coord_df["mainGeoPoint.coordinates"]]
        split_df = pd.DataFrame(coords, index=parsed_records.index, columns=['latitude', 'longitude'])
        parsed_records = pd.concat([parsed_records, split_df], axis=1)
        return parsed_records
    
async def find_lat_longs(locations: pd.Series):
    temp_list = pd.DataFrame(columns=["latitude", "longitude"])
    batchsize = 50
    for i in range(0, len(locations), batchsize):
        batch = locations.iloc[i:i+batchsize]
        resp = await get_geocoordinates_batched(batch)
        if resp is not None:
            temp_list = temp_list.combine_first(resp[['latitude', 'longitude']])
           
     
    return temp_list

        
async def main():
    df = pd.read_csv("data-temp/fb_data_langid_semiprocessed_v2.csv", sep="\t")
    #df = df.drop(columns=["members"])
    long_lat_list = await find_lat_longs(df["location"])
    
    output = df.join(long_lat_list)
    output.to_csv("data-temp/fb_data_geocoordinates.csv", sep="\t", encoding="utf-8-sig")

    
if __name__ == "__main__":
    asyncio.run(main())
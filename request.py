import http.client
import json

def get_exercises():
    conn = http.client.HTTPSConnection("exercisedb.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "530d3829afmsh6bb473518d9464fp17031ejsn994684d294d5",
        'x-rapidapi-host': "exercisedb.p.rapidapi.com"
    }

    conn.request("GET", "/exercises/dumbell curl/%7Bname%7D?offset=0&limit=10", headers=headers)

    res = conn.getresponse()
    data = res.read()

    if res.status == 200:
        exercises_data = json.loads(data.decode("utf-8"))
        
        # Print the first item in the response to check the structure
        if exercises_data:
            print("Keys in the response data:", exercises_data[0].keys())  # Print keys of the first exercise in the response
            
        return exercises_data
    else:
        print(f"Error: {res.status} - {res.reason}")
        return []

# Example call to get exercises with a sample equipment type and muscle group
get_exercises()

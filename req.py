import http.client
import urllib.parse

conn = http.client.HTTPSConnection("exercisedb.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "530d3829afmsh6bb473518d9464fp17031ejsn994684d294d5",
    'x-rapidapi-host': "exercisedb.p.rapidapi.com"
}

# Exercise name you want to search for (e.g., "Dumbbell Alternate Seated Hammer Curl")
exercise_name = "Dumbbell Alternate Seated Hammer Curl"

# URL-encode the exercise name to ensure it's safe for use in the URL
encoded_exercise_name = urllib.parse.quote(exercise_name)

# Update the endpoint to search by exercise name
conn.request("GET", f"/exercises/name/{encoded_exercise_name}?offset=0&limit=10", headers=headers)

res = conn.getresponse()
data = res.read()

print(data)

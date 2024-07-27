import requests
import json

# For recommendations
response = requests.post('http://localhost:8000/recommend', 
                         json={'book_title': 'Harry Potter and the Chamber of Secrets'})
print(json.dumps(response.json(), indent=2))

# For updating data
# response = requests.post('http://localhost:8000/update_data', 
#                          json={'csv_path': 'path/to/new_data.csv'})

# print(response.json())
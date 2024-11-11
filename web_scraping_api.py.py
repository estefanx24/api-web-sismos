import requests
from bs4 import BeautifulSoup
import boto3
import json
import os

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

def scrape_earthquakes():
    url = 'https://ultimosismo.igp.gob.pe/ultimosismo/sismos-reportados'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Parse the data (Assume the table structure and adjust accordingly)
    earthquakes = []
    table = soup.find('table')  # Identify the correct table structure
    rows = table.find_all('tr')[1:11]  # Get the last 10 entries (adjust if necessary)

    for row in rows:
        cols = row.find_all('td')
        data = {
            'date': cols[0].text.strip(),
            'latitude': cols[1].text.strip(),
            'longitude': cols[2].text.strip(),
            'depth': cols[3].text.strip(),
            'magnitude': cols[4].text.strip(),
            'location': cols[5].text.strip()
        }
        earthquakes.append(data)

    return earthquakes

def store_in_dynamodb(earthquakes):
    table = dynamodb.Table('Earthquakes')  # Replace with your table name

    for eq in earthquakes:
        response = table.put_item(
            Item={
                'date': eq['date'],
                'latitude': eq['latitude'],
                'longitude': eq['longitude'],
                'depth': eq['depth'],
                'magnitude': eq['magnitude'],
                'location': eq['location']
            }
        )
        print(f"Stored item: {response}")

# Lambda entry point
def lambda_handler(event, context):
    earthquakes = scrape_earthquakes()
    store_in_dynamodb(earthquakes)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully stored the last 10 earthquakes')
    }

from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests


def flag(input):
  r = requests.post(
      "https://api.deepai.org/api/summarization",
      data={
          'text': input,
      },
      headers={'api-key': 'd3424c20-42c6-4b82-85d6-9938daf5fe97'}
  )
  return r.json()
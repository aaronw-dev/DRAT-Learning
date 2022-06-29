#Credits: https://www.youtube.com/watch?v=IBhdLRheKyM
from googleapiclient.discovery import build

def search(query):
  #get results from Google Search
  resource = build("customsearch", 'v1', developerKey='AIzaSyCpw_um7zkU0RAXpVQhVcfL6E9-yInEx8s').cse()
  result = resource.list(q=query, cx='28de70885b9e1e446').execute()
  returnresult = ""
  return result
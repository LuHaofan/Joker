from editor import util
from neomodel import config

config.DATABASE_URL = 'neo4j+s://neo4j:9cRp7C_4p8ty1f_5XYlXorAtqM3OlksojlNGA9k7RlU@44305d6f.databases.neo4j.io:7687'
print(util.recommend("WiFi Says \"Hi!\" Back to Strangers!"))
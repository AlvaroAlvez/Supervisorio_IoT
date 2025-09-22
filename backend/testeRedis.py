import redis
import json

# Connect to Redis
r = redis.Redis(
    host='iotito.com.br',  # Change to your Redis server if needed
    port=6379,
    password='0591aed20b36a22a3d815107f398905b7c137ec90dfaa657ba7a4ea117c555fe',  # Add your password if needed
    decode_responses=True  # Makes sure Redis returns strings instead of bytes
)

# Test data
test_data = {
    "device": "raspi_teste",
    "status": "OK",
    "temperature": 25
}

# Key to store data
key = "raspi:test"

# Send data to Redis
try:
    r.set(key, json.dumps(test_data))
    print(f"? Data sent to Redis key: {key}")
except Exception as e:
    print(f"? Failed to send data to Redis: {e}")

# Read data from Redis
try:
    redis_data = r.get(key)
    if redis_data:
        redis_data = json.loads(redis_data)
        print(f"? Data received from Redis: {redis_data}")
    else:
        print(f"? No data found for key: {key}")
except Exception as e:
    print(f"? Failed to read data from Redis: {e}")

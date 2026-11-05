
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

print("Available Claude models:\n")

for model in client.models.list(limit=100):
    print(model.id)

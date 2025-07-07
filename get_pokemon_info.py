import sys
import requests

def get_pokemon_info(dex_number):
    url = f"https://pokeapi.co/api/v2/pokemon/{dex_number}/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Could not retrieve data for dex number {dex_number}.")
        return
    data = response.json()
    name = data.get('name', 'N/A').capitalize()
    height = data.get('height', 'N/A')
    weight = data.get('weight', 'N/A')
    types = [t['type']['name'] for t in data.get('types', [])]
    print(f"Name: {name}")
    print(f"Height: {height}")
    print(f"Weight: {weight}")
    print(f"Types: {', '.join(types) if types else 'N/A'}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python get_pokemon_info.py <dex_number>")
        sys.exit(1)
    try:
        dex_number = int(sys.argv[1])
    except ValueError:
        print("Dex number must be an integer.")
        sys.exit(1)
    get_pokemon_info(dex_number)

if __name__ == "__main__":
    main() 
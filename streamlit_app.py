import streamlit as st
import requests
import pandas as pd
import datetime
import hashlib

st.title("Pokémon Birthday Generator")

st.write("Enter your birthday to discover your Pokémon!")

birthday = st.date_input(
    "Enter your birthday",
    value=datetime.date(2000, 1, 1),
    min_value=datetime.date(1950, 1, 1)
)

# PokeAPI currently supports up to 1010 Pokémon (as of Gen 9)
MAX_DEX_NUMBER = 1010
SALAMENCE_DEX_NUMBER = 373
MILOTIC_DEX_NUMBER = 350
SPECIAL_DATE_SALAMENCE = datetime.date(1995, 9, 23)
SPECIAL_DATE_MILOTIC = datetime.date(1995, 5, 8)

# Helper to get Pokémon image by name or id
def get_pokemon_image(pokemon_id_or_name):
    poke_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id_or_name}"
    poke_resp = requests.get(poke_url)
    if poke_resp.status_code == 200:
        poke_data = poke_resp.json()
        return poke_data['sprites']['other']['official-artwork']['front_default']
    return None

if birthday:
    #st.write(f"DEBUG: birthday={birthday}, SPECIAL_DATE_MILOTIC={SPECIAL_DATE_MILOTIC}, eq={birthday == SPECIAL_DATE_MILOTIC}")
    if birthday == SPECIAL_DATE_SALAMENCE:
        dex_number = SALAMENCE_DEX_NUMBER
    elif birthday == SPECIAL_DATE_MILOTIC:
        dex_number = MILOTIC_DEX_NUMBER
    else:
        # Convert date to string and hash it to get a deterministic number
        date_str = birthday.strftime('%Y-%m-%d')
        hash_object = hashlib.sha256(date_str.encode())
        hash_int = int(hash_object.hexdigest(), 16)
        dex_number = (hash_int % MAX_DEX_NUMBER) + 1  # Ensure 1 <= dex_number <= MAX_DEX_NUMBER

    url = f"https://pokeapi.co/api/v2/pokemon/{dex_number}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name = data.get('name', 'N/A').capitalize()
        height = data.get('height', 'N/A')
        weight = data.get('weight', 'N/A')
        types = [t['type']['name'].capitalize() for t in data.get('types', [])]
        sprite_url = data['sprites']['other']['official-artwork']['front_default']
        stats = {stat['stat']['name'].capitalize(): stat['base_stat'] for stat in data['stats']}

        # Fetch Pokédex description and evolution chain
        species_url = f"https://pokeapi.co/api/v2/pokemon-species/{dex_number}"
        species_response = requests.get(species_url)
        pokedex_description = "Description not available."
        evolution_chain = []
        if species_response.status_code == 200:
            species_data = species_response.json()
            # Find the first English flavor text entry
            for entry in species_data.get('flavor_text_entries', []):
                if entry['language']['name'] == 'en':
                    pokedex_description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                    break
            # Get evolution chain
            evo_chain_url = species_data['evolution_chain']['url']
            evo_resp = requests.get(evo_chain_url)
            if evo_resp.status_code == 200:
                evo_data = evo_resp.json()['chain']
                # Traverse the evolution chain
                def traverse_chain(chain, evo_list):
                    evo_list.append(chain['species']['name'])
                    for evo in chain.get('evolves_to', []):
                        traverse_chain(evo, evo_list)
                evo_names = []
                traverse_chain(evo_data, evo_names)
                evolution_chain = evo_names

        st.markdown(f"### Your Birthday Pokémon: {name} (Dex #{dex_number})")
        st.markdown(f"*{pokedex_description}*")
        col1, col2 = st.columns([1,2])
        with col1:
            if sprite_url:
                st.image(sprite_url, caption=name, width=200)
            st.markdown(f"**Height:** {height}")
            st.markdown(f"**Weight:** {weight}")
            st.markdown(f"**Types:** {', '.join(types) if types else 'N/A'}")
        with col2:
            st.subheader("Base Stats")
            stats_df = pd.DataFrame(list(stats.items()), columns=["Stat", "Value"])
            st.bar_chart(stats_df.set_index("Stat")["Value"])

        st.subheader("Evolution Line")
        if evolution_chain:
            evo_cols = st.columns(len(evolution_chain))
            for idx, evo_name in enumerate(evolution_chain):
                evo_img = get_pokemon_image(evo_name)
                highlight = (evo_name.lower() == name.lower())
                with evo_cols[idx]:
                    if evo_img:
                        st.image(evo_img, width=100)
                    if highlight:
                        st.markdown(f"<span style='color:gold;font-weight:bold'>{evo_name.capitalize()}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(evo_name.capitalize())
        else:
            st.write("No evolution data available.")

        st.subheader("Type Information")
        st.write(f"This Pokémon has {len(types)} type(s): {', '.join(types)}.")
        
        st.subheader("Stat Distribution")
        st.write("Below is the distribution of this Pokémon's base stats:")
        st.dataframe(stats_df)
    else:
        st.error("Pokémon not found. Please try another date.") 
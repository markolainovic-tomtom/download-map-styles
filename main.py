# This is a sample Python script.
import json
import os
import re
import shutil
import sys

import requests as requests

api_major_version = "22"
base_url = "https://api.tomtom.com/style/1"

TT_API_KEY = os.getenv("TT_API_KEY")

map_styles = [
    "2/basic_street"
]

modes = [
    "light",
    "dark"
]

flavors = [
    "browsing",
    "driving"
]

sprite_sizes = [
    "1x",
    "2x"
]

sprite_types = [
    "json",
    "png"
]

root_folder_name = "styles"


def make_dirs():
    if os.path.exists(root_folder_name):
        shutil.rmtree(root_folder_name)
    for mode in modes:
        os.makedirs(f"{root_folder_name}/{mode}", exist_ok=True)


def get_styles():
    base_style_url = f"{base_url}/style/{api_major_version}.*"
    res = {}
    for style in map_styles:
        for mode in modes:
            res[mode] = {}
            for flavor in flavors:
                params = {
                    "map": f"{style}-{mode}" if flavor == "browsing" else f"{style}-{mode}-{flavor}",
                    "key": TT_API_KEY
                }
                response = requests.get(base_style_url, params)
                if response.status_code != 200:
                    raise Exception(
                        f"Error: Something went wrong during the style download."
                        f"Response status code: {response.status_code}")
                res[mode][flavor] = response.json()
    return res


def save_styles(styles):
    def find_key_and_remove(txt):
        match = re.search(r"\??key=\w+(?=\?)?", txt)
        return txt[:match.regs[0][0]] + txt[match.regs[0][1]:] if match else txt

    def remove_all_key_mentions(json):
        json["glyphs"] = find_key_and_remove(json["glyphs"])
        for key, value in enumerate(json["sources"]["vectorTiles"]["tiles"]):
            json["sources"]["vectorTiles"]["tiles"][key] = find_key_and_remove(value)

    def adapt_for_onboard(json):
        json["sprite"] = f"asset://styles/{mode}/sprite"

    for mode in modes:
        for flavor in flavors:
            style = styles[mode][flavor]
            adapt_for_onboard(style)
            remove_all_key_mentions(style)
            with open(f"{root_folder_name}/{mode}/style-{flavor}.json", "w") as outfile:
                json.dump(style, outfile)


def get_sprites():
    def get_sprite(base, file_type, params):
        r = requests.get(base + f".{file_type}", params)
        if r.status_code != 200:
            raise Exception(
                f"Error: Something went wrong during the sprite download."
                f"Response status code: {r.status_code}")
        return r

    base_sprite_url = f"{base_url}/sprite/{api_major_version}.*"
    res = {}
    for style in map_styles:
        for mode in modes:
            res[mode] = {}
            params = {
                "map": f"{style}-{mode}",
                "key": TT_API_KEY
            }
            for size in sprite_sizes:
                res[mode][size] = {}
                base = f"{base_sprite_url}/sprite" if size == "1x" else f"{base_sprite_url}/sprite@{size}"
                for type in sprite_types:
                    response = get_sprite(base, type, params)
                    if type == "json":
                        res[mode][size][type] = response.json()
                    elif type == "png":
                        res[mode][size][type] = response.content
                    else:
                        raise Exception(f"Error: not supported type: {type}.")
    return res


def save_sprites(sprites):
    for mode in modes:
        for size in sprite_sizes:
            for type in sprite_types:
                sprite = sprites[mode][size][type]
                base_name = f"{root_folder_name}/{mode}/sprite" if size == "1x" else f"{root_folder_name}/{mode}/sprite@{size}"
                if type == "json":
                    with open(f"{base_name}.{type}", "w") as outfile:
                        json.dump(sprite, outfile)
                elif type == "png":
                    with open(f"{base_name}.{type}", "wb") as outfile:
                        outfile.write(bytes(sprite))
                else:
                    raise Exception(f"Error: not supported type: {type}.")


def check_prerequisites():
    if not TT_API_KEY:
        print("Error: TT_API_KEY not found. Define your API key as TT_API_KEY environment variable. Aborting.")
        sys.exit()


if __name__ == '__main__':
    print(f"""
    APi major version used: {api_major_version}
    
    Define your API key as TT_API_KEY environment variable prior to running.
    Consult https://developer.tomtom.com/map-display-api/documentation/mapstyles/map-styles-v2
    if any changes are needed.
    
    I'll download {[style for style in map_styles]} map style(s),
    for {[mode for mode in modes]} mode(s),
    in {[flavor for flavor in flavors]} flavor(s).
    """)
    check_prerequisites()
    make_dirs()
    save_styles(get_styles())
    save_sprites(get_sprites())
    print(f"Done. Check the {root_folder_name} folder.")

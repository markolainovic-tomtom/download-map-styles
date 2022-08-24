# download-map-styles

### Download the map styles from TomTom Map Styles API
See more about the map styles [here](https://developer.tomtom.com/map-display-api/documentation/mapstyles/map-styles-v2).

The script downloads the styles and sprites and makes the changes to accomodate for placing it in the GO SDK repo, such as:
* Removing the API key mentions.
* Changing certain URL(s) to their `asset://` variants.

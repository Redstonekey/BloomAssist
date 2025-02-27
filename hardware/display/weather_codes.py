def get_weather_description(weather_code):
    """
    Returns the weather description for a given weather code.

    Args:
        weather_code (int): The weather code.

    Returns:
        str: The weather description, or "Unknown weather code" if not found.
    """

    weather_descriptions = {
        1000: "Sonnig",
        1003: "Teilweise bewölkt",
        1006: "Bewölkt",
        1009: "Bedeckt",
        1030: "Nebel",
        1063: "Vereinzelter leichter Regen möglich",
        1066: "Vereinzelter leichter Schneefall möglich",
        1069: "Vereinzelter leichter Schneeregen möglich",
        1072: "Vereinzelter leichter gefrierender Nieselregen möglich",
        1087: "Gewitterartige Ausbrüche möglich",
        1114: "Schneeverwehungen",
        1117: "Schneesturm",
        1135: "Nebel",
        1147: "Gefrierender Nebel",
        1150: "Vereinzelter leichter Nieselregen",
        1153: "Leichter Nieselregen",
        1168: "Gefrierender Nieselregen",
        1171: "Starker gefrierender Nieselregen",
        1180: "Vereinzelter leichter Regen",
        1183: "Leichter Regen",
        1186: "Zeitweise mäßiger Regen",
        1189: "Mäßiger Regen",
        1192: "Zeitweise starker Regen",
        1195: "Starker Regen",
        1198: "Leichter gefrierender Regen",
        1201: "Mäßiger oder starker gefrierender Regen",
        1204: "Leichter Schneeregen",
        1207: "Mäßiger oder starker Schneeregen",
        1210: "Vereinzelter leichter Schneefall",
        1213: "Leichter Schneefall",
        1216: "Vereinzelter mäßiger Schneefall",
        1219: "Mäßiger Schneefall",
        1222: "Vereinzelter starker Schneefall",
        1225: "Starker Schneefall",
        1237: "Eisgranulat",
        1240: "Leichter Regenschauer",
        1243: "Mäßiger oder starker Regenschauer",
        1246: "Starkregen-Schauer",
        1249: "Leichte Schneeregenschauer",
        1252: "Mäßige oder starke Schneeregenschauer",
        1255: "Leichte Schneeschauer",
        1258: "Mäßige oder starke Schneeschauer",
        1261: "Leichte Schauer von Eisgranulat",
        1264: "Mäßige oder starke Schauer von Eisgranulat",
        1273: "Vereinzelter leichter Regen mit Donner",
        1276: "Mäßiger oder starker Regen mit Donner",
        1279: "Vereinzelter leichter Schneefall mit Donner",
        1282: "Mäßiger oder starker Schneefall mit Donner",
    }

    return weather_descriptions.get(weather_code, "Unbekannter Wettercode")
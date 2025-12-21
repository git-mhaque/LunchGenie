"""
Location resolution utilities for LunchGenie.
Decides location/latitude/longitude to use given user input and config.
"""

def resolve_location(config, location, latitude, longitude):
    """
    Prefer explicit lat/lon, then config defaults if not overridden.
    """
    use_lat = latitude
    use_lon = longitude
    use_loc = location
    if use_lat is None or use_lon is None:
        cfg_lat = getattr(config, "default_latitude", None)
        cfg_lon = getattr(config, "default_longitude", None)
        if (cfg_lat and cfg_lon) and (not location or location == "Melbourne"):
            try:
                use_lat = float(cfg_lat)
                use_lon = float(cfg_lon)
                use_loc = None
            except Exception:
                pass
    return use_loc, use_lat, use_lon

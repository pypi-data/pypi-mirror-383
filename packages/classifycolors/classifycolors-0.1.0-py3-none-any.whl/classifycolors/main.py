import webcolors as wc


# build a CSS3 palette: {name -> (r,g,b)}
palette = {n: tuple(wc.name_to_rgb(n, spec=wc.CSS3)) for n in wc.names(wc.CSS3)}


def rgb_to_name(rgb, normalized=False):
    """Convert an RGB iterable to the nearest CSS3 color name by computing the Euclidean distance."""
    
    try:
        r, g, b = rgb
    except ValueError:
        raise ValueError("rgb must be an iterable of three numeric values")
    
    assert all(isinstance(v, (int, float)) for v in rgb), "rgb values must be numeric"
    assert all(v<=255 for v in rgb), "rgb values must be in [0,255]"
    
    if normalized:
        assert all(0 <= v <= 1 for v in (r, g, b)), "normalized rgb values must be in [0,1]"
        r, g, b = r*255, g*255, b*255

    # Compute distances to each color in the palette
    distances = [(r-cr)**2+(g-cg)**2+(b-cb)**2 for cr,cg,cb in palette.values()]

    return list(palette.keys())[distances.index(min(distances))]
from geopatterns import GeoPattern

pattern = GeoPattern('string', generator='squares')
with open(f'image.svg', 'w') as f:
    f.write(pattern.svg_string)

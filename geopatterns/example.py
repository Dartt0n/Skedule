from geopatterns import GeoPattern


pattern = GeoPattern(8, 8)
with open(f'image.svg', 'w') as f:
    f.write(pattern.svg_string)

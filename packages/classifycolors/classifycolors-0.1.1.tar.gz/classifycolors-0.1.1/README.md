# classifycolors

Convert any RGB value to the **nearest CSS3 color name** using simple Euclidean distance.

## Installation
```bash
pip install classifycolors
```

## How it works
The package calculates the Euclidean distance between the input RGB value and all CSS3 color values, returning the name of the closest match.

## Usage
```python
from classifycolors import rgb_to_name

print(rgb_to_name((120, 200, 30)))  # → 'yellowgreen'
print(rgb_to_name((0.4, 0.2, 0.7), normalized=True))  # → 'slateblue'
```

## License
MIT © Elie Fares
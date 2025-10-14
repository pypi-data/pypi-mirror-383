# sgrain

Tells if it's currently raining at a given latitude and longitude in
Singapore. The data comes from rain radar images at
https://www.weather.gov.sg/weather-rain-area-50km/. The image is
updated every 5 minutes.


**Link to project:** https://github.com/nlannuzel/sgrain

## Package installation
### From Github:
```
pip install git+https://github.com/nlannuzel/sgrain
```

### ... or from Pypi:
```
pip install nlannuzel.sgrain
```

## Package usage
For example:
```python
#!/usr/bin/env python3

from nlannuzel.sgrain.rain import RainAreas
from nlannuzel.sgrain.geo import Location

rain = RainAreas()

# Download the latest radar image from https://www.weather.gov.sg/weather-rain-area-50km/
rain.load_image()

# https://maps.app.goo.gl/9aA7i8chryYwuhUT8
picnic_spot = Location(1.313383, 103.815203)

# Returns a number from 0 to 31
intensity = rain.intensity_at(picnic_spot)

message = f"At location {picnic_spot}, time {rain.rounded_dt}: "
if intensity == 0:
	message += "it's not raining."
elif intensity < 10:
	msg += "it's raining a little bit ({intensity}), bring a umbrella."
else:
	msg += "it's raining a lot ({intensity}), cancel the picnic."
print(message)
```

One liner:
python -m 

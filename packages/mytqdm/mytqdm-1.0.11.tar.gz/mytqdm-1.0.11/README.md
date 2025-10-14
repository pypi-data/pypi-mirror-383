# MyTqdm
See and share your tqdm state everywhere with everyone on [mytqdm.app](https://mytqdm.app)!

## Support
Writing software takes time. I'd be happy to get your support.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y8Y11M25J7)

## Installation
```pip install mytqdm```

## Obtain api key
Enter your email on [mytqdm.app](https://mytqdm.app) to receive a custom api key. Use this key to upload your progress automatically via your mytqdm instance in your python code.

## Usage
- Import via ```from mytqdm import mytqdm``` and use ```mytqdm``` instead of ```tqdm```.
- Provide your ```api_key``` in the mytqdm constructor. Optionally provide a ```title```.

Example:
```
from mytqdm import mytqdm

MY_API_KEY = "..."
for i in mytqdm(range(10000), api_key=MY_API_KEY, title="Our progress to make POs happy."):
    ...
```

See [mytqdm.app/docs](https://mytqdm.app/docs) for detailed instructions and how to obtain your current progress.

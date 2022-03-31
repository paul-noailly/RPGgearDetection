# Gear Detection OCR


## Why this project ?

**Problem:**

ACE is an rpg game with equipable gears. Like any other game of this genra, improving a character is an optimization problem: Getting the best relevant stats by equiping gears with some constraints (cannot equip 2 pairs boots, ...).

Optimization goals can be:
- maximizing overall damage output
- maximizing overall tankiness
- maximizing a specific stat (speed, ...)

Unfortunatly before tackling any optimization, we need data. 
This data is not publicly available so we need to find a way to scrape it.
We want the scrapping process to be as fast as possible while minimizing the user inputs.

**Solution:**

We can screenshot a targeted area of the game inside an emulator.
Apply computer vision OCR models on the images of the gear to detect aal text and numbers on the screenshot.
Extract relevant information from the model output into an easy to understand json file.

The input required from the user come down to:
- calibrate the screening process by indicating the area the screenshot.
- click on each gear during the screening process

## How to use

**Setup a GCP account:**
- use a google account and go on [google cloud plateform](https://console.cloud.google.com/)
- activate free try
- create a new project
  - activate google vision app [here](https://console.cloud.google.com/apis/library/vision.googleapis.com)
  - create serve account and extract key as json file [here](https://console.cloud.google.com/iam-admin/serviceaccounts)
  - rename this file `service-account-file.json` and put it in the root of the repo

**First scrape the gears pictures**

```ssh
python main_scraper.py
```

**Then run OCR model and decoder algorithm on pictures**

```ssh
python main_decoder.py
```

## Contribute

```ssh
git add . && git commit -m "name commit" && git push -u origin master
```



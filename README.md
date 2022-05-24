# How to use

Run these commands in your terminal:

```
git clone ...
cd gscraper
python3 -m pip install --upgrade pip
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

After the installation is finished, edit the `params.json` file to include your scraping parameters.

Save the file and run the script:

```
python3 scrape.py
```

To exit the virtual environment:

```
deactivate
```

And to reactivate the virtual environment:

```
source venv/bin/activate
```

Notes:
1. To build or test your regex expression head over to https://regex101.com/
2. To find the css class, search anything on Google and inspect the results. Find the class that is the parent of the a tag containing the search URLs.
3. This script enforces a random 35-45s timeout upon each successful request to avoid Google blocking the scraper.
4. Outputs will be saved in the same directory as the input csv.
5. If you need to stop the process (because it's taking too long), simply Ctrl+C to exit the terminal process. Don't worry - your results will still be saved, but you may need to remove the rows from the input csv before you run the script again to avoid duplicate scraping.

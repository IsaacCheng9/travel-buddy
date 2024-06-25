# Travel Buddy

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![CI](https://github.com/IsaacCheng9/travel-buddy/actions/workflows/main.yml/badge.svg)

**UPDATE (25th June 2024):** The application is no longer fully functional due
to outdated code for scraping data from websites.

**UPDATE (30th August 2022):** The route analysis and related features such as
location autocomplete are currently unavailable as our key for the Google Maps
API has expired.

<img width="488" alt="image" src="https://user-images.githubusercontent.com/47993930/157455295-10e79608-0b29-4446-bc05-cf2e3cbfc662.png">

A travel companion to help plan your journey while saving both money and the
planet by providing route analysis and a carpool marketplace.

## Screenshots

<img width="2056" alt="image" src="https://user-images.githubusercontent.com/47993930/160259708-872d9827-c011-4e3f-9492-13b3dd6876d9.png">
<img width="2056" alt="image" src="https://user-images.githubusercontent.com/47993930/160259721-6ae304aa-d6da-4b1b-bef6-20968e55006d.png">
<img width="2056" alt="image" src="https://user-images.githubusercontent.com/47993930/160259727-5bda8093-7a97-498a-b338-8806284647eb.png">
<img width="2056" alt="image" src="https://user-images.githubusercontent.com/47993930/160259626-7fe98e35-d7b0-4a2e-abf8-a2faa9b0e492.png">

## Usage

### Installing Dependencies

Run the following command from the [project root](./) directory:

```bash
poetry install
```

### Running the Application

Run the following command from the [project root](./) directory:

```bash
poetry run app
```

### Running Tests

Run the following command from the [project root](./) directory:

```bash
poetry run pytest
```

## Demo Instructions

A demo database has been set up by default (`db.sqlite3`), with some sample user
accounts to save the hassle of registration and make it easy to get started:

- Username: `johndoe` | Password: `P@ssword01`
- Username: `janedoe` | Password: `P@ssword01`

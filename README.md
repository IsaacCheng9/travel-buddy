# Travel Buddy

[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![CI](https://github.com/IsaacCheng9/travel-buddy/actions/workflows/main.yml/badge.svg)

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

## Installation

### Python Version

The application has been developed and tested to work on _Python 3.8_ and
onwards.

### Running the Application Locally

To run the application, you should follow the following steps:

1. Clone this GitHub repository.
2. Ensure that you're in the root directory: `travel-buddy`
3. Install the required Python libraries: `pip install -r requirements.txt`
4. Install the code as a package on your local machine with the command:
   `pip install -e .`
5. Run the application with the command: `python -m travel_buddy.app`
6. Navigate to <http://127.0.0.1:5000/> in your web browser.

### Running Tests Locally

1. Clone this GitHub repository.
2. Ensure that you're in the root directory: `travel-buddy`
3. Install the required Python libraries: `pip install -r requirements.txt`
4. Install the code as a package on your local machine with the command:
   `pip install -e .`
5. Run all tests with the command `python -m pytest`
6. View test results in the terminal.

## Demo Instructions

A demo database has been set up by default (`db.sqlite3`), with some sample user
accounts to save the hassle of registration and make it easy to get started:

- Username: `johndoe` | Password: `P@ssword01`
- Username: `janedoe` | Password: `P@ssword01`

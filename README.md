# Mercaphydona-app

## Overview

Mercaphydona-app is a little software developed with Python that is capable of recover all of mails sent by Mercadona platform to your mail address, analyze them and show you the total spent in a customizable time range. 

NOTE: to use this software you will have to set up the Gmail API access to the google user that contains the mails in it's gmail.

## Prerequisites

- Python installed on your machine ([Download Python](https://www.python.org/downloads/))
- Google account with access to the Gmail API

## Getting Started

1. **Enable the Gmail API**:
   - Go to the [Google API Console](https://console.developers.google.com/).
   - Select a project or create a new one.
   - In the sidebar on the left, expand "APIs & Services" and select "Library".
   - Search for "Gmail API" and enable it for your project.

2. **Create Credentials**:
   - In the sidebar on the left, expand "APIs & Services" and select "Credentials".
   - Click on "Create credentials" and select "OAuth client API ID".
   - Select the appropriate service account or create a new one, choose the role "Project > Editor", and select JSON as the key type.
   - Click "Create" to generate and download your credentials JSON file, rename it to 'credentials.json'.

3. **Configure Credentials**:
   - Place the downloaded `credentials.json` file into the appropriate directory in your project.

4. **Install Dependencies**:
   - Run `pip install -r requirements.txt` in the root directory of your project to install any required dependencies.

5. **Run Your Software**:
   - Open the root app folder with yout favorite Python IDE and debug the python file names 'main.py' to init the program, when you'll press the "Search tickets" button, if you have the correct credencials.json file placed in the root of the app, a navigator will give you instructions to login with given google account, askint to give the program permissions to recover the data from it, if you continue, the program will create the "token.json" and will search all the mercadona mails from that account gmail and display the results.

## Resources

- [Google API Console](https://console.developers.google.com/)
- [Gmail API Documentation](https://developers.google.com/gmail/api/)

## Support

If you encounter any issues or have questions, please reach out to .

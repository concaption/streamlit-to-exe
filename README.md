 # Converting a Streamlit App to an Executable

To convert your Streamlit app to a Windows executable, follow these steps:

## Setting up the Environment
1. Start the GitHub Codespace by clicking on the badge below:

   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/concaption/streamlit-to-exe)
2. Wait for the environment to be set up. You are halfway done when the screen color changes from white to purple. Wait until your terminal is ready.

## Copy Your Streamlit App
1. Copy your Streamlit app into the `app/` folder. Ensure all necessary files are placed in this folder.
2. Remove anything that you are using under `if __name__ == "__main__"`. Also, ensure that you are not importing `from streamlit.web import cli as stcli`, etc. Only import ` import streamlit as st` in the app.

## Create the Executable
You can create the executable using the following command:
```sh
make
```
If you want to change the name according to your app, run the following command:

```sh
make app name=your_app_name_here
```

### Download the Files
The output files will be in the `dist/` directory. You can right click on the file and download it. The file that have Setup in its name is the setup file.

### Message me

You can message me on Upwork.

[![Hire concaption on upwork: https://www.upwork.com/freelancers/concaption](https://img.shields.io/badge/UpWork-6FDA44?style=for-the-badge&logo=Upwork&logoColor=white)](https://www.upwork.com/freelancers/concaption)

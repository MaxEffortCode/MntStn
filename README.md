# How to configure the development environment for this project

## 1. Setup weasyprint's required libraries
Weasyprint is a library we use to process HTML pages into PDFs. The easiest way is to use homebrew. If you don’t want to use homebrew and/or use Windows, stop reading this section and go look at their [documentation](https://brew.sh/). This is because homebrew’s Python to create a virtual environment avoids the need to link libraries, and these homebrew libraries that are automatically configured are required by weasyprint. Once homebrew is installed, install Python, Mango, and libffi. If you don’t install the required libraries needed for weasyprint before installing weasyprint, you will receive some errors about libraries not being found, probably about gobject. You can test that you did this correctly by creating a virtual environment, pip installing weasyprint, and performing a “weasyprint —info” command and can proceed on.

## 2. Create your virtual environment and activate it
```
python3 -m venv venv
```

It is recommended that you activate your virtual environment with the script provided in the binary directory which is usually the bin folder or Scripts folder for Windows. Technically you can get away without this though.
```
source venv/bin/activate
```

## 3. Configure Postgres & PATH (Work in Progress - Max if you read this can you pls update this section since you configured Postgres)
There is no PostgresSQL packages/db natively installed on Mac OS (For Linux/Windows, you’ll need to view their documentation), and a package in this project psycopg2 needs to look for Postgres files. You’ll need to install the Postgres database (outside of a virtual env) and you’ll need to make sure the executable “pg_config” is in your path, otherwise you’ll get psycopg2 library errors.

For Mac OS (out of many solutions I am sure, note I didn’t use homebrew for this):
After installing Postgres app and dragging it your Applications folder, you now have the pg_config executable. perform the following command to find the executable:
```
sudo find / -name pg_config 
```

It should point you to the exec and you will now need to put its containing directory into your PATH like so (I like to put this inside the virtual env since I care about clutter on my system path) I also want to note that the location may change after a PC reboot, as mine did but haven't looked into how it works yet, this part will be updated later when more is learned about it:
```
export PATH=/path/to/postgresql/bin/:$PATH
```

Woohoo! Run the form scraper script. You can now run the main script of this project with the following command:
```
python3 -m Apps.Collection.src.sec_form_crawler
```

We run it this way so that we don’t ever have to resort to path hacks, as launching scripts directly from where they are located will set the Python “path” to that directory. Doing it like above gives us consistent and predictable imports to use in each module.

## 4. Deactivate your virtual environment when all is done (technically optional but is advised)
```
Deactivate
```

# TLDR; - Configuring the Development Environment
1. Install Python, weasyprint’s required libraries, Postgres, and configure PATH properly
2. Create virtual environment and activate it
3. Launch the form scraper script with the command: “python3 -m Apps.Collection.src.sec_form_crawler”
4. Deactivate your virtual environment

# Running the test suite
We are using the pytest framework for testing. It is the goal to have unit and integration tests for ALL modules that are written. To setup, please refer to configuring the Development Environment above, but instead of running the form scraper script after steps 1 and 2, you just need to run the following in your virtual environment:
```
python3 -m pytest
```

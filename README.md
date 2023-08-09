# How to configure the development environment for this project

## 1. Setup weasyprint's required libraries
Weasyprint is a library we use to process HTML pages into PDFs. The easiest way is to use homebrew. If you don’t want to use homebrew and/or use Windows, stop reading this section and go look at their [documentation](https://brew.sh/). This is because homebrew’s Python to create a virtual environment avoids the need to link libraries, and these homebrew libraries that are automatically configured are required by weasyprint. Once homebrew is installed, install Python, Mango, and libffi. If you don’t install the required libraries needed for weasyprint before installing weasyprint, you will receive some errors about libraries not being found, probably about gobject. You can test that you did this correctly by creating a virtual environment, pip installing weasyprint, and performing a “weasyprint —info” command and can proceed on.

## 1.1 Installing HomeBrew (Linux):
```
sudo apt update
sudo apt upgrade
```
installing curl:
```
sudo apt install curl
```
Installing homebrew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
enabling HomeBrew on PATH:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

Gettin the build essentials fo brew
```
sudo apt-get install build-essential
```

Installing GCC (recommended)
```
brew install gcc
```

## 2. Create your virtual environment and activate it
```
python3 -m venv venv
```
## (additional step for linux users)
you may need to install virtualenv using:
```
pip install virtualenv
```
and runing:
```
source <local direcrtory path to file>/MntStn/venv/bin/activate
```
It is recommended that you activate your virtual environment with the script provided in the binary directory which is usually the bin folder or Scripts folder for Windows. Technically you can get away without this though.
```
source venv/bin/activate
```

Woohoo! Run the form scraper script. You can now run the main script of this project with the following command:
```
python3.10 -m Apps.Collection.src.sec_form_crawler
```

d37096232ed8: Waiting . Deactivate your virtual environment

# Running the test suite
## Install pytest
```
pip install pytest
```

We are using the pytest framework for testing. It is the goal to have unit and integration tests for ALL modules that are written. To setup, please refer to configuring the Development Environment above, but instead of running the form scraper script after steps 1 and 2, you just need to run the following in your virtual environment:
```
python3.10 -m pytest
```
To run individual tests:
```
python3.10 -m pytest <path_to_repo>/MntStn/Apps/Collection/tests/test_helper.py::<test_function_to_run>
```

# How to set up a Docker container:

```
sudo dockerd
sudo docker build -t myapp:latest .
sudo docker run -it -p 8000:8000 myapp:latest
docker push gcr.io/tester-391021/myapp:latest
docker build -t gcr.io/tester-391021/myapp:latest .
docker run -it -p 8000:8000 gcr.io/tester-391021/myapp:latest
exec(open("Apps/Collection/src/api/file_request.py").read())
```
you can promote an epherial IP to a static IP 
https://console.cloud.google.com/networking/addresses/list?project=tester-391021

Using 0.0.0.0:22 ()

To log into gcloud from local:
gcloud compute ssh --zone "us-west4-b" "instance-4" --project "tester-391021"\


///////
#How to deploy to google cloud:

1. <local> sudo docker build -t myapp:<tag> .

2. <local> docker push gcr.io/tester-391021/myapp:<tag>

3. <gcloud> go to "Container Registry"

4. <gcloud> click most recent image

5. <gcloud> Click "Deploy" on the top nav button

6. 


///////

docker run -it -p 443:443 gcr.io/tester-391021/myapp:latest <----- FIX

## the reason this works is its the https gateway assigned to the container by gcloud
///
Need to update requirements to get the g-dang gzip package installed
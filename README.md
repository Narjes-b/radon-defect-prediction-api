# Welcome to the Receptor documentation

Modern software relies massively on the use of automation at both development and operations levels, and engineering strategy known as **DevOps**.
The software code driving such automations is collectively known as Infrastructure-as-Code (IaC).

While IaC represents an ever increasing widely-adopted practice nowadays,little is known how to best mantain, speedily evolve, and continuously improve the code behing the IaC strategy.

<div style="text-align:center"><span style="color:red; font-family:Georgia; font-size:1.25em;">
As any other source code artifact, IaC blueprints can be defect-prone!
</span></div>

<br>

**Receptor** represents a step forward towards closing the gap for the implementation of software quality instruments to support DevOps engineers when developing and maintaining infrastructure code.
It provides functionality for quantifying the characteristic of a IaC blueprint and predicting its defect proneness.
Although it currently supports only Ansible, it is supposed to be soon extended to the OASIS Topology and Orchestration Specification for Cloud Applications (TOSCA) ecosystem. 

<div style="text-align:center"><span style="color:black; font-family:Georgia; font-size:1.25em;">
Effective prediction of defect-prone IaC blueprints may enable DevOps to focus on such critical scripts duging Quality Assurance activities, and allocate effort and resources more efficiently!
</span></div>

<br>

Ultimately, this enables continuous deloyment and accelerates the expected Return on Investment.



# How to use

Clone
```text
git clone https://github.com/radon-h2020/radon-defect-prediction-api.git
```
```text
cd radon-defect-prediction-api
```

Install requirements
```text
pip install -r requirements.txt
```

Create migrations
```text
python manage.py makemigrations apis
python manage.py migrate apis
```

Export Github and Gitlab access tokens to mine repositories
```
export GITHUB_ACCESS_TOKEN=*************************
export GITLAB_ACCESS_TOKEN=***************
```

Run server
```text
python manage.py runserver
```

Open your browser and go to `http://127.0.0.1:8000/web/repositories/` to start using the web-app.


**Note:** a MongoDB must be installed. A db called `testing_iac_miner` will be created automatically.

**A DETAILED DOCUMENTATION WILL BE AVAILABLE SOON**

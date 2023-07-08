# task-mgt

## Description
It is a User Task Management API built on a PostgreSQL database. It uses JWT for user authentication and authorization with full CRUD capabilty for tasks. 

### Dependencies
* FastAPI
* Python version 3.11 


### Executing program

On the terminal execute the below command to create the projects' working directory and move into that directory.

 
```python
$ mkdir task-mgt
cd task-mgt
```

In the projects' working directory execute the below command to create a virtual environment for our project. Virtual environments make it easier to manage packages for various projects separately.

 
```python
$ virtualenv venv
```

To activate the virtual environment, execute the below command.

```python
$ source venv/Script/activate
```
Clone this repository in the projects' working directory by executing the command below.

```python
$ git clone https://github.com/ajaoooluseyi/task-mgt.git
$ cd task-mgt
```

To install all the required dependencies execute the below command.

```python
$ pip install -r requirements.txt
```

To run the app, navigate to the app folder in your virtual environment and execute the command below
```python
$ uvicorn main:app --reload
```
To build the image on docker run the following code
```cmd
$ docker-compose up
```


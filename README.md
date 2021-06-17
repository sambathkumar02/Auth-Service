# Auth Micro Service
  This Project is a Basic Authentication microservice using Flask,Postgres and SQLAlchemy as ORM.
  
## Features
- Forgot password feature
- SQL Injection FIltering
- Basic Email and Input Filtering
- Hash Password using salt

## Endpoints

|Endpoints | Methods |
|----------|---------|    
|/Login |POST|
/signup |POST|
/Forgotpass|POST|
/changepasss/<token>|POST|

import datetime
from logging import exception
from os import EX_CONFIG
from flask import Flask
from flask_sqlalchemy import SQLAlchemy,Model
from flask_restful import Resource,Api,reqparse,marshal_with
import bcrypt
from sqlalchemy.orm import selectin_polymorphic
from sqlalchemy.sql.elements import Null
import random_generator
import mailer

request=reqparse.RequestParser()
request.add_argument("email",type=str,help="invalid Email",required=True)
request.add_argument("password",type=str,help="password",required=True)

forgot_pass_req=reqparse.RequestParser()
forgot_pass_req.add_argument("email",type=str,help="email Needed",required=True)

password_parser=reqparse.RequestParser()
password_parser.add_argument("password",type=str,help="password Needed",required=True)


app=Flask(__name__)
api=Api(app)

app.config['SQLALCHEMY_DATABASE_URI']="postgresql://postgres:0000@localhost:5432/crud"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db=SQLAlchemy(app)


class Login_Details(db.Model):
    __tablename__="LoginDetails"

    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    email=db.Column(db.String(60),primary_key=True)
    password=db.Column(db.String(500))

    def __init__(self,email,password):
        self.email=email
        self.password=password

class ForgotRequest(db.Model):
    __tablename__="ForgotRequest"
    Id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    Time=db.Column(db.Time(),nullable=False)
    UserId=db.Column(db.Integer(),nullable=False)
    Email=db.Column(db.String(60),nullable=False)
    Token=db.Column(db.String(50),nullable=False)

    def __init__(self,time,userid,email,token):
        self.Time=time
        self.UserId=userid
        self.Email=email
        self.Token=token



db.create_all()
        

def EmailInputFilter(input):
    data=input.strip()
    if data=='':
        return Null
    else:
        try:
            username,url=data.split('@')
            try:
                website,tld1,tld2=url.split('.')
            except:
                website,tld1=url.split('.')
                tld2=""
            print(username,url,website,tld1,tld2)
        except ValueError:
            return Null
        if username.isalnum() == False or website.isalpha() == False or tld1.isalpha()==False or tld2.isalpha()==False:
            return Null
        elif len(tld1) > 3 or len(tld2) > 3:
            return Null
        else:
            return data



class Login(Resource):
    def post(self):
        args=request.parse_args()
        passwd=args['password']
        try:
            result=db.session.query(Login_Details).filter_by(email=args['email']).first()

            if not result:
                return {"Auth":"False","messgae":"User not Found"}
            hash=result.password
            #As the DB colum is String encode to binary before check it
            if bcrypt.checkpw(passwd.encode('utf-8'),result.password.encode('utf-8')):
                return {"Auth":"True","messgae":"Authentication sucess"}
            else:
                return {"Auth":"False","messgae":"Incorrect Password"}
        except Exception:
            print(Exception)
            return {"Auth":"False","messgae":"Authentication Failed"}


class Signup(Resource):
    def post(self):
        args=request.parse_args()
        email=args['email']
        if email is Null:
            return {"messsgae":"Invalid Email"}
        try:
            #Column in db is String so create a hash in bytes and decode and save it so it avoids futher encoding of database
            hash=bcrypt.hashpw(args['password'].encode('utf-8'),bcrypt.gensalt())
            password_hash=hash.decode('utf-8')
            data=Login_Details(email=args['email'],password=password_hash)
            db.session.add(data)
            db.session.commit()
            return {"message":"Sucess"}  
        except Exception:
            return {"message":"Email already Exists"}

class ForgotPass(Resource):
    def post(self):
        args=forgot_pass_req.parse_args()
        email_unchecked=args["email"]
        email_result=email_unchecked
        if email_result is Null:
            return {"message":"Invalid Email"}
        
        result=db.session.query(Login_Details).filter_by(email=email_result).first()
        if not result:
            return {"message":"If you have an account ,The link had been sent to your Email!"}
        else:
            try:
                password_change_token=random_generator.GenerateString()
                mailer.SendEmail(email_result,password_change_token)  
                store_request=ForgotRequest(time=datetime.datetime.now(),userid=result.id,email=email_result,token=password_change_token)
                db.session.add(store_request)
                db.session.commit()
            except Exception as e:
                print(e)
            return {"message":"If you have an account ,The link had been sent to your Email!"}


class ChangePass(Resource):
    def post(self,token):
        try:
            result=db.session.query(ForgotRequest).filter_by(Token=token).first()
            userid=result.UserId
            if not result:
                return {"message":"invalid token"}
            password=password_parser.parse_args()['password']
            hash=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            password_hash=hash.decode('utf-8')
            data={
                "password":password_hash
            }
            print(password_hash)
            update_record=db.session.query(Login_Details).filter_by(id=userid).update(data)
            db.session.commit()
            return {"message":"password changed"}
        except Exception as e:
            return {"message":"Password change Failed"}




api.add_resource(Login,"/login")
api.add_resource(Signup,"/signup")
api.add_resource(ForgotPass,"/forgotpass")
api.add_resource(ChangePass,"/changepass/<string:token>")



if __name__=="__main__":
    app.run(debug=True)

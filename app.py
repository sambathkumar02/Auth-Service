from flask import Flask
from flask_sqlalchemy import SQLAlchemy,Model
from flask_restful import Resource,Api,reqparse,marshal_with
import bcrypt
from sqlalchemy.sql.elements import Null


request=reqparse.RequestParser()
request.add_argument("email",type=str,help="invalid Email",required=True)
request.add_argument("password",type=str,help="password",required=True)


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
        except ValueError:
            return Null
        if username.isalpha() == False or website.isalpha() == False or tld1.isalpha()==False or tld2.isalpha()==False:
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
        email=EmailInputFilter(args['email'])
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
    pass

api.add_resource(Login,"/login")
api.add_resource(Signup,"/signup")
api.add_resource(ForgotPass,"/forgotpass/{id}")





if __name__=="__main__":
    app.run(debug=True)

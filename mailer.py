import smtplib

def SendEmail(reciever_addresss,token):
    s=smtplib.SMTP('smtp.gmail.com',587)
    s.starttls()
    s.login('cringemax123@gmail.com','developmentpurpose@123')
    message=f"Link for Password Reset\n URL=localhost:5000/changepass/{token}"
    s.sendmail('cringemax123@gmail.com',reciever_addresss,message)
    print("Mail Sent")
    s.quit()




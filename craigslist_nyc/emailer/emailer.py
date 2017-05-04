import os
from flask import Flask, jsonify, abort, make_response, request, render_template
from flask.ext.mail import Mail, Message

app = Flask("craiglist_email")
app.config.from_pyfile('%s/settings.py' % os.path.dirname(os.path.abspath(__file__)))

mail = Mail(app)
app.mail = mail    

@app.route('/send', methods = ['GET'])
def send_email():
    url = request.args.get('cl')
    recipient = request.args.get('email')
    print recipient
    print url
    msg = Message(
            'Young professional interested in your apartment!',
            sender = 'testname.zhehao@gmail.com',
            reply_to = 'Zhehao Wang <zhehao@cs.ucla.edu>',
            recipients = [recipient])
    msg.body = """
Hi there!

This is Zhehao. I'm planning to move to NYC in mid June, and saw your post (""" + url + """) on Craigslist. 
I'm very interested in learning more!

Something about myself:
 - I'm going to work as a software engineer at Bloomberg starting 06/19/17 (ideally looking to move in around that date but flexible)
 - I'm a clean, easy going, and respectful guy turning 24 soon. No habit of partying and won't have guests staying over night.
 - I'm currently living in Los Angeles, and just finished my masters program in Computer Science at UCLA. I'm originally from China but have been living in the US for 4 years.
 - I've a good credit record (720+), and can show proof of income (company offer letter) if required.
 - My LinkedIn profile (https://www.linkedin.com/in/zhehao-wang-15739869/).
 - I'll be out of the apartment working most of the time between 9A-8P on weekdays.

If the apartment's still available and I might be a good fit, would it be possible to do a FaceTime / Skype call and go over more details?
My email address is zhehao@cs.ucla.edu, and phone number is 424-333-8516.

Thank you very much and please let me know!

Thanks,
Zhehao
"""
    mail.send(msg)
    return "Sent"

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')

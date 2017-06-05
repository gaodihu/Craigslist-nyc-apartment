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
            sender = 'your.name@gmail.com',
            reply_to = 'Your Other Email <your.prefered.email@gmail.com>',
            recipients = [recipient])
    msg.body = """
Hi there!

This is your.name. I'm planning to move to NYC in mid June, and saw your post (""" + url + """) on Craigslist. 
I'm very interested in learning more!

If the apartment's still available and I might be a good fit, would it be possible to do a FaceTime / Skype call and go over more details?
My email address is your.name@gmail.com, and phone number is your.phone.number.

Thank you very much and please let me know!

Thanks,
your.name
"""
    mail.send(msg)
    return "Sent"

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')

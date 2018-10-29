import json, qrcode
from flask import Flask, redirect, url_for, request, jsonify, render_template

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import imgkit

def SendMail(receiver, body, ImgFileName):
	img_data = open(ImgFileName, 'rb').read()
	msg = MIMEMultipart()
	msg['Subject'] = 'Carteirinha'
	msg['From'] = 'trabalhoredes20182@gmail.com'
	msg['To'] = receiver

	text = MIMEText(body)
	msg.attach(text)
	image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
	msg.attach(image)

	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login('trabalhoredes20182@gmail.com', 'redes123')
	s.sendmail(msg['From'], msg['To'], msg.as_string())
	s.quit()


app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
	"""
		Backend. Envia dados por JSON
	"""
	with open("database/db.json") as outfile:
		data = json.load(outfile)

	if request.method == "POST":

		user 	 = request.form["cpf"]
		password = request.form["password"]

		if user not in data:
			return redirect(url_for("carteirinha",messages={"status" : 1}))

		data = {str(field) : str(data[user][field]) for field in data[user]}

		if data["pass"] != password:
			data["status"] = 2
			data["msg"] = "Wrong password"

		elif data["atividade"] == "inativo":
			data["status"] = 3
			data["msg"] = "Inactive user"

		elif data["foto"] == "":
			data["status"] = 4
			data["msg"] = "No photo"

		elif any("" == data[field] for field in data):
			data["status"] = 5
			data["msg"] = "Missing atribute"

		else:
			data["status"] = 0

			qr = qrcode.QRCode(
				    version = 1,
				    error_correction = qrcode.constants.ERROR_CORRECT_H,
				    box_size = 3,
				    border = 4,)

			qr.add_data(data)

			img = qr.make_image() 
		 	img.save("./static/"+data["nome"]+".png")

		del data['pass']
		return redirect(url_for("carteirinha",messages=data))


@app.route("/carteirinha", methods=["GET"])
def carteirinha():
	"""
		Parte do front-end que renderiza a carteirinha
	"""
	user = request.args.get('messages')
	user = json.loads(user.replace("'",'"'))

	if not user['status']:

		html = '<img src="'+user["foto"]+'" height="250" width="400">'
		for field in user:
			print field
			print user[field]
			html += '<p>'+ user[field] +'</p>' if field not in ('foto','status') else ''

		html += '<img src="'+user["nome"]+'.png" height="100" width="100">'

		with open('./static/out.html','w') as out:
			out.write(html)	

		imgkit.from_file('./static/out.html','./static/out.jpg')

		html = '<img src="static/out.jpg">'

		SendMail(user['email'],'Carteirinha emitida!', 'static/out.jpg')

		return html

	else: 
		return "<p>Error "+ str(user["status"])	+" : "+user["msg"]+"</p>"


if __name__ == "__main__":
	app.run(debug=True)
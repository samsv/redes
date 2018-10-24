import json, qrcode
from flask import Flask, redirect, url_for, request, jsonify, render_template

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
			return redirect(url_for("carteirinha",messages={"status" : "1"}))

		data = {str(field) : str(data[user][field]) for field in data[user]}

		if data["pass"] != password:
			data["status"] = "2"

		elif data["atividade"] == "inativo":
			data["status"] = "3"

		elif data["foto"] == "":
			data["status"] = "4"

		elif any("" == data[field] for field in data):
			data["status"] = "5"

		else:
			data["status"] = "0"

			qr = qrcode.QRCode(
				    version = 1,
				    error_correction = qrcode.constants.ERROR_CORRECT_H,
				    box_size = 3,
				    border = 4,)

			qr.add_data(data)

			img = qr.make_image() 
		 	img.save("./static/"+data["nome"]+".png")

		return redirect(url_for("carteirinha",messages=data))


@app.route("/carteirinha", methods=["GET"])
def carteirinha():
	"""
		Parte do front-end que renderiza a carteirinha
	"""
	return render_template("index.html")

if __name__ == "__main__":
	app.run(debug=True)
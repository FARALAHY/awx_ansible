from flask import Flask, render_template, request, redirect
import subprocess
import os

app = Flask(__name__)

INVENTAIRE = "/home/tangarien/awx-automatisation/inventories/prod/hosts.ini"
PLAYBOOK = "/home/tangarien/awx-automatisation/site.yml"

if not os.path.exists(INVENTAIRE):
    with open(INVENTAIRE, "w") as f:
        f.write("[mes_serveurs]\n")

def lire_serveurs():
    with open(INVENTAIRE, "r") as f:
        lignes = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("[")]
    return lignes

@app.route("/")
def index():
    serveurs = lire_serveurs()
    return render_template("index.html", serveurs=serveurs)

@app.route("/ajouter", methods=["POST"])
def ajouter():
    ip = request.form["ip"].strip()
    host_id = request.form["host_id"].strip()
    serveurs = lire_serveurs()
    for s in serveurs:
        if s.startswith(ip) or f"host_id={host_id}" in s:
            return "IP ou host_id déjà existant !", 400
    with open(INVENTAIRE, "a") as f:
        f.write(f"{ip} host_id={host_id}\n")
    return redirect("/")

@app.route("/supprimer/<ip>")
def supprimer(ip):
    lignes = lire_serveurs()
    with open(INVENTAIRE, "w") as f:
        f.write("[mes_serveurs]\n")
        for l in lignes:
            if not l.startswith(ip):
                f.write(l + "\n")
    return redirect("/")

@app.route("/modifier/<ip>", methods=["POST"])
def modifier(ip):
    new_ip = request.form["new_ip"].strip()
    new_id = request.form["new_id"].strip()
    lignes = lire_serveurs()
    with open(INVENTAIRE, "w") as f:
        f.write("[mes_serveurs]\n")
        for l in lignes:
            if l.startswith(ip):
                f.write(f"{new_ip} host_id={new_id}\n")
            else:
                f.write(l + "\n")
    return redirect("/")

@app.route("/configurer_tous")
def configurer_tous():
    subprocess.run(["ansible-playbook", "-i", INVENTAIRE, PLAYBOOK])
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

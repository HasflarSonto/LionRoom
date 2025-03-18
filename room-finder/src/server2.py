from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/get_room_availability')
def get_room_availability():
    with open('room_availability.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/get_room_names')
def get_room_names():
    with open('room_id.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

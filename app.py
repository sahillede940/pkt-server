from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
from mongoengine import StringField, FloatField, DateTimeField, EmbeddedDocumentListField, Document, EmbeddedDocument
from datetime import datetime
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'pratik',
    'host': 'localhost',
    'port': 27017
}
CORS(app, resources={r"/*": {"origins": "*"}})
db = MongoEngine(app)

class Item(EmbeddedDocument):
    title = StringField()
    cost = FloatField()

class Data(Document):
    date = DateTimeField()
    items = EmbeddedDocumentListField(Item)

    def to_json(self):
        return {
            "date": self.date.strftime('%Y-%m-%d'),
            "items": [{"title": item.title, "cost": item.cost} for item in self.items]
        }

@app.route('/add_data', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def add_data():
    data = request.json

    # Validate and parse date
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d')
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid or missing date. Format should be YYYY-MM-DD."}), 400

    # Validate items
    items = []
    for item in data.get('items', []):
        try:
            items.append(Item(title=item['title'], cost=float(item['cost'])))
        except (KeyError, ValueError):
            return jsonify({"error": "Invalid items format."}), 400

    # Check if document with the same date exists
    existing_data = Data.objects(date=date).first()
    
    if existing_data:
        # Update existing document
        existing_data.items = items
        existing_data.save()
        return jsonify({"message": "Data updated in MongoDB", "data": existing_data.to_json()}), 200
    else:
        # Create a new Data instance
        new_data = Data(date=date, items=items)
        new_data.save()
        return jsonify({"message": "Data added to MongoDB", "data": new_data.to_json()}), 201

@app.route("/get_data", methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_data():
    if request.method == 'GET':
        data = Data.objects().all()
        if not data:
            return jsonify({"error": "No data found"}), 404
        return jsonify(data), 200
    
    if request.method == "POST":
        data = request.json
        # get date from data
        date = data['date']
        # search for particular date
        try:
            data = Data.objects().get(date=date)
            return jsonify(data)
        except:
            return {"message" : "error"}
    
    return {
        "message": "Invalid request method."
    }
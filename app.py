import csv
import json

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MY_FILE = 'diamond.csv'
MY_FILE_ID = 'dimond_with_id.csv'


def load_data():
    json_data = []
    with open(MY_FILE, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            json_data.append(row)
        return json_data


def add_id():
    with open(MY_FILE) as inp, open(MY_FILE_ID, 'w') as out:
        reader = csv.reader(inp)
        writer = csv.writer(out, delimiter=',')
        # No need to use `insert(), `append()` simply use `+` to concatenate two lists.
        writer.writerow(['ID'] + next(reader))
        # Iterate over enumerate object of reader and pass the starting index as 1.
        writer.writerows([i] + row for i, row in enumerate(reader, 1))

def remove_id():
    cols_to_remove = [0] # Column indexes to be removed (starts at 0)

    cols_to_remove = sorted(cols_to_remove, reverse=True) # Reverse so we remove from the end first
    row_count = 0 # Current amount of rows processed

    with open(MY_FILE_ID, "r") as source:
        reader = csv.reader(source)
        with open(MY_FILE, "w", newline='') as result:
            writer = csv.writer(result)
            for row in reader:
                row_count += 1
                for col_index in cols_to_remove:
                    del row[col_index]
                writer.writerow(row)

def load_data_id():
    add_id()
    json_data = []
    with open(MY_FILE_ID, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            json_data.append(row)
        return json_data


def get_headers():
    with open(MY_FILE, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        return next(csv_reader)

def get_headers_id():
    with open(MY_FILE_ID, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        return next(csv_reader)

@app.route('/diamond', methods=['POST'])
def new_diamond():
    data = request.get_json()   # request data as dict
    existing_data_array = load_data()   # 
    existing_data_array.append(data)
    row = []
    headers = get_headers()
    for l in headers:
        row.append(data[l])
    
    with open(MY_FILE, 'a') as f:
       writer = csv.writer(f)
       writer.writerow(row)
    return data

@ app.route('/diamond', methods=['GET'])
@ app.route('/diamond/<int:diamond_id>', methods=['GET'])
def read_diamond(diamond_id = -1):
    json_data = load_data_id()
    if (diamond_id == -1):
        return json_data
    else:
        for x in json_data:
            if int(x['ID']) == diamond_id:
                return x
        return {"msg": "not such diamond "}

@app.route('/diamond/<int:diamond_id>', methods=['PUT'])
def update_diamond(diamond_id):
    json_data = load_data_id()
    input_data = request.get_json()   
    diamond_found = False
    for diamond in json_data:
        if (str(diamond_id) == diamond['ID']):
            diamond_found = True
            diamond.update(input_data)
            break
    if not diamond_found: 
        return {"msg": "no such diamond "}
    headers = get_headers_id()
    with open(MY_FILE_ID, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(json_data)
    remove_id()
    return input_data

@app.route('/diamond/<int:diamond_id>', methods=['DELETE'])
def delete_diamond(diamond_id):
    json_data = load_data_id()
    index = 0
    for diamond in json_data:
        if (str(diamond_id) == diamond['ID']):
            json_data.pop(index)
            break
        else:
            index = index + 1

    headers = get_headers_id()
    with open(MY_FILE_ID, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(json_data)
    remove_id()

    return jsonify({'message': diamond_id})




if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)

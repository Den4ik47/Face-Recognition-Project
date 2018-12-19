# This is a _very simple_ example of a web service that recognizes faces in uploaded images.
# Upload an image file and it will check if the image contains a picture of Barack Obama.
# The result is returned as json. For example:
#
# $ curl -XPOST -F "file=@obama2.jpg" http://127.0.0.1:5001
#
# Returns:
#
# {
#  "face_found_in_image": true,
#  "is_picture_of_obama": true
# }
#
# This example is based on the Flask file upload example: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

# NOTE: This example requires flask to be installed! You can install it with pip:
# $ pip3 install flask

import face_recognition
from flask import Flask, jsonify, request, redirect
from pymongo import MongoClient
# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
client = MongoClient('localhost', 27017)
db = client['Users']
collection = db['Data']


app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return detect_faces_in_image(file)

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Is this a picture of Obama?</title>
    <h1>Upload a picture and see if it's a picture of Obama!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''


def detect_faces_in_image(file_stream):

    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False
    is_obama = False
    listForImages=[]
    values=collection.distinct("value")
    images=collection.distinct("Images")
    if len(unknown_face_encodings) > 0:
        for unknown in range(len(unknown_face_encodings)):
           if values: 
            for faces in range(len(values)):
              res=collection.find_one(({"value": str(unknown_face_encodings[unknown])}))
              print(res)
              if res:
                 print(res['Images'])
              else:
                 collection.insert({"value":str(unknown_face_encodings[unknown]),"Name and Surname":"","Images":file_stream.filename})
        # See if the first face in the uploaded image matches the known face of Obama
                 helplist=[]
                 pureList=[]
                 result=values[faces].replace('\n','')
                 result=result.replace('[','')
                 result=result.replace(']','')
                 helplist=result.split(' ')
                 for point in range(len(helplist)):
                     if helplist[point] is not '':
                        pureList.append(float(helplist[point]))
                 print(pureList)       
                 match_results = face_recognition.compare_faces([pureList], unknown_face_encodings[unknown])
                 if match_results[0]:
                    is_obama = True
                    face_found = True
           else:                 
               collection.insert({"value":str(unknown_face_encodings[unknown]),"Name and Surname":"","Images":file_stream.filename})
    # Return the result as json
    result = {
        "face_found_in_image": face_found,
        "is_picture_of_obama": is_obama
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

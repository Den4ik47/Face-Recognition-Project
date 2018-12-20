import os
import face_recognition
from flask import Flask, jsonify, request, redirect,send_file,render_template
from pymongo import MongoClient
# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

client = MongoClient('localhost', 27017)
db = client['Users']
collection = db['Data']

UPLOAD_FOLDER = '/home/deni/Documents/Diploma/UPLOAD_FOLDER'
TEMPLATE='/home/deni/Documents/Diploma/templates'
app = Flask(__name__,template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATE'] = TEMPLATE
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
    <title>Detect faces on similar photos</title>
    <h1>Upload a picture and see result!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''


def detect_faces_in_image(file_stream):
    file_stream.save(os.path.join(app.config['UPLOAD_FOLDER'], file_stream.filename))
    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False
    is_obama = False
    listForImages=[]
    values=collection.distinct("value")
    if values: 
      if len(unknown_face_encodings) > 0:
        for unknown in range(len(unknown_face_encodings)):
              res=collection.find_one(({"value": str(unknown_face_encodings[unknown])}))
              if res:
                 print(res['Images'])
              else:
                collection.insert({"value":str(unknown_face_encodings[unknown]),"Name and Surname":"","Images":file_stream.filename})
                for faces in range(len(values)):
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
                 match_results = face_recognition.compare_faces([pureList], unknown_face_encodings[unknown])
                 if match_results[0]:
                    record=collection.find_one({"value":values[faces]})
                    print(record['Images'])
                    if file_stream.filename not in listForImages:
                       listForImages.append(file_stream.filename)
                    if record not in listForImages:
                        listForImages.append(record['Images'])
                    print(listForImages)
                    is_obama = True
                    face_found = True
    else:
        for unknown in range(len(unknown_face_encodings)):                 
            collection.insert({"value":str(unknown_face_encodings[unknown]),"Name and Surname":"","Images":file_stream.filename})                
    # Return the result as json
    result = {
        "face_found_in_image": face_found,
        "is_picture_of_obama": is_obama,
        "pictures where we observed faces":listForImages
    }
    if is_obama:
       return render_template('response.html',listForImages=listForImages)
       
       # send_file(os.path.join(app.config['UPLOAD_FOLDER'], listForImages[0]), mimetype='image/gif')
    #jsonify(result)
    else:
        return jsonify(result)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

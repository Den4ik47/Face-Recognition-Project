import os
import face_recognition
from flask import Flask, jsonify, request, redirect,send_file,render_template
from pymongo import MongoClient
# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

client = MongoClient('localhost', 27017)
db = client['Users']
collection = db['Data']

UPLOAD_FOLDER = '/home/deni/Documents/Diploma/static/UPLOAD_FOLDER'
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
            return DetectFacesinImage(file)

    # If no valid image file was uploaded, show the file upload form:
    return render_template('main.html')
    #Clean data from spaces and other symbols. Preparing for Convert to Float list 
def CleanDataFromDB(datafromdb):
    result=datafromdb.replace('\n','')
    result=result.replace('[','') 
    result=result.replace(']','')
    return result

def ComparingFaces(listFromDb,listFromPhoto):
    match_results = face_recognition.compare_faces([listFromDb], listFromPhoto)
    return match_results

def DetectFacesinImage(file_stream):
    file_stream.save(os.path.join(app.config['UPLOAD_FOLDER'], file_stream.filename))
    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False
    faceExist = False
    RequireName=False
    listForImages=[]
    #Get values from Database
    values=collection.distinct("value")
    if values: 
      if len(unknown_face_encodings) > 0:
        for unknown in range(len(unknown_face_encodings)):
              #Check if exist such value 
              res=collection.find_one(({"value": str(unknown_face_encodings[unknown])}))
              if res:
                 print(res['Images'])
              else:
                collection.insert({"value":str(unknown_face_encodings[unknown]),"Name and Surname":"","Images":file_stream.filename})
                for faces in range(len(values)):
                #Convert string to float list
                 helplist=[]
                 pureList=[]
                 helplist=CleanDataFromDB(values[faces]).split(' ')
                 for point in range(len(helplist)):
                     if helplist[point] is not '':
                        pureList.append(float(helplist[point])) 
                #Compare faces from Database and photo
                 if ComparingFaces(pureList,unknown_face_encodings[unknown])[0]:
                #Add path to photos to list
                    record=collection.find_one({"value":values[faces]})
                    print(record['Images'])
                    if file_stream.filename not in listForImages:
                       listForImages.append(file_stream.filename)
                    if record not in listForImages:
                        listForImages.append(record['Images'])
                    print(listForImages)
                    faceExist = True
                    face_found = True
                    if len(listForImages)>4:
                         RequireName=True                        
      else:
        for unknown in range(len(unknown_face_encodings)):                 
            collection.insert({"value":str(unknown_face_encodings[unknown]),"Name and Surname":"","Images":file_stream.filename})                
    # Return the result as json{"value":values[faces]}
    
    result = {
        "face_found_in_image": face_found,
        "is_picture_of_obama": faceExist,
        "pictures where we observed faces":listForImages
    }
    print(RequireName)
    if faceExist:
       return render_template('response.html',listForImages=listForImages)
       
       # send_file(os.path.join(app.config['UPLOAD_FOLDER'], listForImages[0]), mimetype='image/gif')
    #jsonify(result)
    else:
        return jsonify(result)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

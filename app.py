from flask import Flask, request, url_for, render_template, send_from_directory
from datetime import datetime
import os
from werkzeug.utils import secure_filename


ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'static', 'img')

app = Flask(__name__)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(ROOT_DIRECTORY, 'static', 'img')
app.config['UPLOAD_EXTS'] = ['.jpg', '.JPG']

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['GET','POST'])
def upload_image():
    if request.method=="GET":
        return render_template('upload.html')

    if not os.path.isdir(IMAGE_DIRECTORY):
        app.logger.debug('Creating directory ' + IMAGE_DIRECTORY)
        os.mkdir(IMAGE_DIRECTORY) 

    for image in request.files.getlist("imageFile"): 
        # returns a sanitized filename
        filename = secure_filename(image.filename) 
        
        # check that we have a valid file to upload
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTS']:
                app.logger.debug('Invalid file was specified for upload: ' + filename)
                return 'An invalid file was specified. Only .jpg or .JPG files are permitted!', 400
            
            # check that the filename does not already exist
            # if it exists we will append the current timestamp to the filename
            image_names = os.listdir(IMAGE_DIRECTORY)
            
            if (filename in image_names):
               
                name = os.path.splitext(filename)[0]
                file_ext = os.path.splitext(filename)[1]

                dt = datetime.now()
                ts = datetime.timestamp(datetime.now())
                
                app.logger.debug('Filename ' + filename + ' exists on the server. Appending timestamp to filename.')
                filename = name+str(int(ts))+file_ext 
            
            app.logger.debug('Attempting to upload ' + filename)
            destination = "\\".join([IMAGE_DIRECTORY, filename])
            image.save(destination)

    return render_template("upload_complete.html")

@app.route('/static/img/<filename>', methods=['GET'])
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/image/<current_image>',methods=['GET'])
def image_page(current_image):
    
    app.logger.debug('Currently viewing: ' + str(current_image or 'None'))
    
    images = get_sorted_image_list()
    total = len(images)

    if len(images)>0:
        if current_image == 'first':
            current_image = images[0]
        elif current_image == 'last':
            current_image = images[-1]

        try:
            current_index = images.index(current_image)
        except:
            return "The page you are trying to reach does not exist.", 404

        if current_index == 0:
            previous_image = None
        else:
            previous_image = url_for_image(images[current_index-1])

        app.logger.debug('Previous image: ' + str(previous_image or 'None'))

        if current_index == len(images)-1:
            next_image = None
        else:
            next_image = url_for_image(images[current_index+1])

        app.logger.debug('Next image: ' + str(next_image or 'None'))

        return render_template('image_viewer.html', image = current_image,
                                                    current = current_index, 
                                                    previous = previous_image, 
                                                    next = next_image, 
                                                    total = total)

    return render_template('image_viewer.html')

@app.errorhandler(413)
def image_too_large(e):
    return "The image you tried to upload is too large.", 413

@app.errorhandler(404)
def page_not_exists(e):
    return "The page you tried to navigate to does not exist.", 404

def get_sorted_image_list():
    image_names = filter(lambda file: os.path.isfile(os.path.join(IMAGE_DIRECTORY, file)), os.listdir(IMAGE_DIRECTORY))
    image_names = filter(lambda image: image.endswith('jpg') or image.endswith('JPG'), image_names)
    image_names = sorted(image_names, key = lambda x: os.path.getctime(os.path.join(IMAGE_DIRECTORY, x)))
    return image_names

def url_for_image(current_image):
    return url_for('image_page', current_image=current_image)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
#import library
import re
import pandas as pd

from flask import Flask, jsonify, request

from flask import request
import flask
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

class CustomFlaskAppWithEncoder(Flask):
    json_provider_class = LazyJSONEncoder

#memanggil flask objek dan menyimpannya via variable app
app = CustomFlaskAppWithEncoder(__name__)

# menuliskan judul dan input host lazystring untuk random url
swagger_template = dict(
    info = {
        'title' : LazyString(lambda: "API Documentation for Processing and Cleansing"),
        'version' : LazyString(lambda: "1.0.0"),
        'description' : LazyString(lambda: "**Dokumentasi API untuk Processing dan Cleansing Data** \n API BY ALIF"),
    },
    host = LazyString(lambda: request.host)
)


# mendefinisikan endpoint 
swagger_config = {
    "headers" : [],
    "specs" : [
        {
            "endpoint": "docs",
            "route" : "/docs.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/docs/"
}


#membuat fungsi untuk text cleansing dari data upload 
swagger = Swagger(app, template=swagger_template, config = swagger_config)

 #remove_variabel tidak perlu  
def cleansing(text):
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    text = re.sub('.g\\n\\n', ' ', text) # menghilangkan '.g\\n\\n'
    text = re.sub('xf  x f x   x', ' ', text) #menghilangkan string xf
    text = re.sub('\xf0\x9f\x99\x88\xf0\x9f\x99\x88\xf0\x9f', ' ', text) #menghilangkan string \XF0 dst.
    text = re.sub('xe x x', ' ', text)
    text = re.sub('\n',' ',text) # menghilangkan '\n'
    text = re.sub('rt',' ',text) # menghilangkan retweet symbol
    text = re.sub('user',' ',text) # menghilangkan username
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # menghilangkan URL
    text = re.sub('  +', ' ', text) # Remove extra spaces 
    return text
   

# membuat endpoint untuk text clean route text_processing.yml 
@swag_from("docs/text_processing.yml", methods = ['POST'])
@app.route('/text_processing', methods=['POST'])
def text():

    text = request.form['text']
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data' : re.sub(r'[^a-zA-Z0-9]', ' ', text),
    }
    response_data = jsonify(json_response)
    return response_data


#membuat endpoint untuk upload file
@swag_from("docs/csv_processing.yml", methods = ['POST'])
@app.route('/upload', methods=['POST'])
def file_processing():
    
    file_input = request.files['file']

    #readcsvfile
    df=pd.read_csv(file_input, encoding='latin1')

    df_tweet = pd.DataFrame(df[['Tweet']])
    

    #apply cleansing function from data 'cleansing'
    df['Tweet'] = df['Tweet'].apply(cleansing)

    #save data
    result_file_path = 'data_afterpreprocessing.csv'
    df.to_csv(result_file_path, index=False, encoding='utf-8')

    #apply cleansing

    json_response = {
        'status_code': 200,
        'description': "Teks cleansing",
        'data' : 'sukses upload',
        'result_file_path': result_file_path #menambahkan path file hasil cleansing
    }    

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()






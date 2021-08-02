from flask import Flask, render_template, url_for, session, flash, \
    redirect, request, send_from_directory, make_response

from modules.pseu import pseudonymization
from modules.aggregation import calculate_statistics
from modules.GANs import gans

from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed

from flask_dropzone import random_filename
from jinja2.utils import generate_lorem_ipsum

import uuid
import os
import pandas as pd

app = Flask(__name__, template_folder='templates', static_folder="", static_url_path="")

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config["SECRET_KEY"] = uuid.uuid4().hex

user = {
    'username': ' Grev Li',
    'bio': 'A boy who loves movies and music.'
}

movies = [
    {'name': ' My Neiqhbor Totoro', 'year': '1988'},
    {'name': ' Three Colours trilogy', 'year': '1993'},
    {'name': ' Forrest Gump', 'year': '1994'},
    {'name': ' perfect Blue', 'year': '1997'},
    {'name': ' The Matrix', 'year': '1999'},
    {'name': ' Memento', 'year': '2000'},
    {'name': ' The Bucket list', 'year': '2007'},
    {'name': ' Black Swan', 'year': '2010'},
    {'name': ' Gone Girl', 'year': '2014'},
    {'name': ' Coco', 'year': '2017'},
]


class UploadForm(FlaskForm):
    dataset = FileField('Upload Dataset', validators=[FileRequired(),
                                                      FileAllowed(['csv'])])
    submit = SubmitField('Upload')


class AggregationForm(FlaskForm):
    def __init__(self, columns):
        super(FlaskForm, self).__init__()
        self.columns = columns

    numerical_methods = ["max", "min", "median", "mean", "sum", "std", "quantile", "var"]
    other_methods = ["count", "nunique"]
    submit = SubmitField('Run!')


class NeuralNetworkForm(FlaskForm):
    def __init__(self, columns):
        super(FlaskForm, self).__init__()
        self.columns = columns

    nn_methods = ['GANs', 'VAE']
    submit = SubmitField('Run!')


class PseuForm(FlaskForm):
    def __init__(self, columns):
        super(FlaskForm, self).__init__()
        self.columns = columns

    pseu_methods = ['Base64']
    submit = SubmitField('Run!')


app.config["UPLOAD_PATH"] = os.path.join(app.root_path, 'uploads')
app.config["DOWNLOAD_PATH"] = os.path.join(app.root_path, 'downloads')


@app.route('/', methods=['GET', 'POST'])
def index():
    # return render_template('watchlist.html', user=user, movies=movies)
    form = UploadForm()

    if form.validate_on_submit():
        f = form.dataset.data
        random_name = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], random_name))
        flash('Upload success.')
        session['filename'] = [random_name][0]
        session['original_name'] = str(f.filename)
        return redirect(url_for('uploaded_status', file_name=random_name.split('.')[0]))
    return render_template('index.html', form=form)


@app.route('/uploaded/<file_name>', methods=['GET', 'POST'])
def uploaded_status(file_name):
    # load_file_info
    original_name = session['original_name']
    data_path = 'uploads/' + session['filename']
    columns = list(pd.read_csv(data_path))

    pseu_form = PseuForm(columns)
    nn_form = NeuralNetworkForm(columns)
    aggregation_form = AggregationForm(columns)

    return render_template('uploaded.html', original_name=original_name, pseu_form=pseu_form, nn_form=nn_form,
                           aggregation_form=aggregation_form)


@app.route('/get_aggregation_result', methods=["POST"])
def get_aggregation_result():
    file_name = session['filename'].split('.')[0]
    data_path = 'uploads/' + session['filename']

    group_by_column = request.values.getlist("group_by_column")[0]
    statistics_column = request.values.getlist("statistics_column")[0]
    selected_method = request.values.getlist("numerical_method")
    selected_method.extend(request.values.getlist("other_method"))
    result = calculate_statistics(data_path, group_by_column, selected_method, statistics_column)
    selected_method = list(result)[1:]
    random_name = random_filename(file_name)
    result.to_csv(os.path.join(app.config['DOWNLOAD_PATH'], random_name) + ".csv", index=0)
    session['download_file_name'] = [random_name][0]

    display = """<table id="aggregation_result"><tr>"""
    display = display + "<th>" + str(group_by_column) + "</th>"
    for column in selected_method:
        display = display + "<th>" + str(column) + "</th>"
    display = display + "</tr>"
    for i in range(min(result.shape[0], 20)):
        display = display + "<tr>"
        display = display + "<td>" + str(result[group_by_column][i]) + "</td>"
        for column in selected_method:
            display = display + "<td>" + str(result[column][i]) + "</td>"
        display = display + "</tr>"
    display = display + "</table>"

    return render_template('result.html', function="Aggregation", selected_method=selected_method,
                           display=display,
                           download_file_name=session['download_file_name'] + ".csv")

@app.route('/get_nn_result', methods=["POST"])
def get_nn_result():
    file_name = session['filename'].split('.')[0]
    data_path = 'uploads/' + session['filename']

    selected_method = request.values.getlist("pseu_method")[0]
    selected_columns = request.values.getlist("pseu_column")
    result = pseudonymization(selected_method, data_path, selected_columns)
    random_name = random_filename(file_name)
    result.to_csv(os.path.join(app.config['DOWNLOAD_PATH'], random_name) + ".csv", index=0)
    session['download_file_name'] = [random_name][0]

    display = """<table id="pseu_result"><tr>"""
    for column in selected_columns:
        display = display + "<th>" + str(column) + "</th>"
    display = display + "</tr>"
    for i in range(min(result.shape[0], 20)):
        display = display + "<tr>"
        for column in selected_columns:
            display = display + "<td>" + str(result[column][i]) + "</td>"
        display = display + "</tr>"
    display = display + "</table>"

    # return render_template('result.html', function="Pseudonymization", selected_method=selected_method,
    #                        display=display,
    #                        download_file_name=session['download_file_name'] + ".csv")


@app.route('/get_pseu_result', methods=["POST"])
def get_pseu_result():
    file_name = session['filename'].split('.')[0]
    data_path = 'uploads/' + session['filename']

    selected_method = request.values.getlist("pseu_method")[0]
    selected_columns = request.values.getlist("pseu_column")
    result = pseudonymization(selected_method, data_path, selected_columns)
    random_name = random_filename(file_name)
    result.to_csv(os.path.join(app.config['DOWNLOAD_PATH'], random_name) + ".csv", index=0)
    session['download_file_name'] = [random_name][0]

    display = """<table id="pseu_result"><tr>"""
    for column in selected_columns:
        display = display + "<th>" + str(column) + "</th>"
    display = display + "</tr>"
    for i in range(min(result.shape[0], 20)):
        display = display + "<tr>"
        for column in selected_columns:
            display = display + "<td>" + str(result[column][i]) + "</td>"
        display = display + "</tr>"
    display = display + "</table>"

    return render_template('result.html', function="Pseudonymization", selected_method=selected_method,
                           display=display,
                           download_file_name=session['download_file_name'] + ".csv")


@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)
    return '''
    <h1>A very long post</h1>
    <div class="body">%s</div>
    <button id="load">Load More</button>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script type="text/javascript">
            $(function(){
                $('#load').click(function(){
                 $.ajax(
                 {
                 url: '/more',
                 type: 'get',
                 success: function(data){
                     $('.body').append(data);
                 }
                 }
                 )
                })
             })
    </script>
    ''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        file_name = request.args.get('file_name')
        # 　fullfilename = '/root/allfile/123.txt'
        file_path = "downloads"
        # response = make_response(send_from_directory(file_path, file_name + ".csv", as_attachment=True))
        # response.headers["Content-Disposition"] = "attachment; file_name={}".format(
        #     file_path.encode().decode('latin-1'))
        return send_from_directory(file_path, file_name, as_attachment=True)

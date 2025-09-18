from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from pandas import concat
from pandas import DataFrame
import math

app = Flask(__name__)

# Load your trained model
model = tf.keras.models.load_model(r"C:\Users\Venkat Kumar\OneDrive\Desktop\final 1\Water Idea Project Website\Water Idea Project Website\flask1 main\templates\SIH2024.keras")

# Load and preprocess data
df = pd.read_csv(r'C:\Users\Venkat Kumar\OneDrive\Desktop\final 1\Water Idea Project Website\Water Idea Project Website\flask1 main\templates\Water Audit final 100 years data.csv', header=0, index_col=0)
values = df.values.astype('float32')

# Scale the data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)

def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
    agg = concat(cols, axis=1)
    agg.columns = names
    if dropnan:
        agg.dropna(inplace=True)
    return agg

reframed = series_to_supervised(scaled, n_in=1, n_out=1)
n_features = df.shape[1]
reframed.drop(reframed.columns[range(n_features, n_features * 2 - 1)], axis=1, inplace=True)

# Split into train and test sets
n_train_months = 36
values = reframed.values
train = values[:n_train_months, :]
test = values[n_train_months:, :]
train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

def forecast_next_steps(model, last_obs, scaler, steps=1):
    forecasts = []
    current_input = last_obs

    for _ in range(steps):
        yhat = model.predict(current_input, verbose=0)
        forecasts.append(yhat[0, 0])
        current_input = np.concatenate((current_input[:, :, 1:], yhat[:, np.newaxis, :]), axis=2)

    forecasts_scaled = np.concatenate((np.zeros((len(forecasts), scaler.n_features_in_ - 1)), np.array(forecasts).reshape(-1, 1)), axis=1)
    forecasts_rescaled = scaler.inverse_transform(forecasts_scaled)[:, -1]

    return forecasts_rescaled

# MySQL configurations (use XAMPP's MySQL connection details)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Default XAMPP user
app.config['MYSQL_PASSWORD'] = ''  # Default password (empty in XAMPP)
app.config['MYSQL_DB'] = 'new data'  # Name of the database you created

mysql = MySQL(app)

#1st page
@app.route('/Home')
def Home():
    return render_template('Home_page.html')

#2nd page
@app.route('/Expect_sol')
def Expect_sol():
    return render_template('Expect_sol.html')

#3rd page
@app.route('/Data_set', methods=['GET', 'POST'])
def Data_set():
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        # Fetch the selected district from the form
        district_1 = request.form['did']
        
        # Query to fetch data for the selected district
        cursor.execute("SELECT * FROM `water_audit_dataset` WHERE did = %s", (district_1,))
    else:
        # Default query to fetch all data
        cursor.execute("SELECT * FROM `water_audit_dataset`")
    
    data = cursor.fetchall()
    cursor.close()

    return render_template('Dataset.html', data=data)

#4th Page
@app.route('/Reservoir_data', methods=['GET', 'POST'])
def Reservoir_data():
    cursor = mysql.connection.cursor()

    # Pagination settings
    per_page = 100  # Number of rows per page
    page = request.args.get('page', 1, type=int)  # Get the current page (default to 1)

    if request.method == 'POST':
        # Fetch the selected district from the form
        district = request.form['rid']
        
        # Query to fetch data for the selected district with pagination
        offset = (page - 1) * per_page
        cursor.execute("SELECT * FROM `chemmbarambakkam` WHERE rid = %s LIMIT %s OFFSET %s", (district, per_page, offset))
    else:
        # Default query to fetch all data with pagination
        offset = (page - 1) * per_page
        cursor.execute("SELECT * FROM `chemmbarambakkam` LIMIT %s OFFSET %s", (per_page, offset))

    data = cursor.fetchall()

    # Count total rows for pagination
    cursor.execute("SELECT COUNT(*) FROM `chemmbarambakkam`")
    total_rows = cursor.fetchone()[0]
    total_pages = math.ceil(total_rows / per_page)

    cursor.close()

    return render_template('Reservoir.html', data=data, page=page, total_pages=total_pages)

@app.route('/imdb')
def imdb():
    return render_template('imdb.html')

@app.route('/forecast', methods=['POST'])
def forecast():
    global test_X
    try:
        years = request.form.get('years')
        months = request.form.get('months')
        
        if years is None or months is None:
            return jsonify({"error": "Both 'years' and 'months' parameters are required."})
        
        years = int(years)
        months = int(months)

        if len(test_X.shape) == 2:
            test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

        last_obs = test_X[-1].reshape((1, test_X.shape[1], test_X.shape[2]))
        
        total_months_to_forecast = (years - 2024) * 12 + months
        stepz = (years - 2024) * 12
        next_steps = forecast_next_steps(model, last_obs, scaler, steps=stepz)
        start = stepz-12
        end=months+start
        result=next_steps[start:end]
        return jsonify({"forecast": result.tolist()})

    except ValueError:
        return jsonify({"error": "Please enter valid numeric values."})
    except Exception as e:
        return jsonify({"error": str(e)})
    
#4th page
@app.route('/ML_Algorithms')
def ML_Algorithms():
    return render_template('ML-Algorithms.html')

#6th page
@app.route('/Res_con')
def Res_con():
    return render_template('Res-con.html')

@app.route('/Dashboard')
def Dashboard():
    return render_template('Dashboard.html')

#7th page
@app.route('/Water_demo_video')
def Water_demo_video():
    return render_template('Demo_video.html')

if __name__ == '__main__':
    app.run(debug=True)
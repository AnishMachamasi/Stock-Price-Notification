from flask import Flask, render_template, request
import requests
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import schedule
import time
from twilio.rest import Client
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    # Retrieve the form data
    receipient = request.form['user_email']
    phone = request.form['phone']
    symbol = request.form['ticker']
    threshold = float(request.form['threshold'])
    frequency = request.form['frequency']
    notification_type = request.form.get('notification_type')
    print(f"Notification Type: {notification_type}")
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    print(start_date)
    print(end_date)
    
    # Insert the data into the new table
    conn = sqlite3.connect('requests.db')
    c = conn.cursor()
    
    # # Create table
    # c.execute('''CREATE TABLE requests (
    #                 id INTEGER PRIMARY KEY,
    #                 recipient TEXT,
    #                 phone TEXT,
    #                 symbol TEXT,
    #                 threshold REAL,
    #                 frequency TEXT,
    #                 notification_type TEXT,
    #                 start_date DATE,
    #                 end_date DATE)''')
    
    #c.execute("INSERT INTO requests (recipient, phone, symbol, threshold, frequency, notification_type, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (receipient, phone, symbol, threshold, frequency, notification_type, start_date, end_date))
    #c.execute("DELETE FROM requests WHERE recipient=?", (receipient,))

    conn.commit()
    conn.close()


    # Retrieve stock data
    def get_stock_data():
        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v3/get-historical-data"
        region = "US"
        # end_date = datetime.now().strftime("%Y-%m-%d")
        # start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        end_date = end_date
        start_date = start_date
        print(end_date)
        print(start_date)
        querystring = {"symbol": symbol, "region": region, "from": start_date, "to": end_date}
        headers = {
            # "X-RapidAPI-Key": "52ceb5a784msh9c0e480a52d97ecp1dd28ejsn40bcebde0cae",
            # "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
            "X-RapidAPI-Key": "977ca49af4msh65debae086d8b56p12be33jsn2c3e18631aeb",
	        "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        df = pd.DataFrame(data["prices"])
        df["date"] = pd.to_datetime(df["date"], unit="s").dt.date
        print(df)
        
        # Filter the data frame to only show rows where the price is above the threshold
        df_filtered = df[df["close"] >= threshold]

        if df_filtered.empty:
            df_filtered = df[df["close"] < threshold]
            given_threshold = False

        else:
            given_threshold = True

        # Send notification if the filtered dataframe is not empty
        send_notification(symbol, threshold, given_threshold, df_filtered, receipient, phone, notification_type)

    # Schedule the job to run at the specified frequency
    if frequency == "hourly":
        schedule.every().hour.do(get_stock_data)
    elif frequency == "daily":
        schedule.every().day.at("09:00").do(get_stock_data)
    elif frequency == "weekly":
        schedule.every().week.at("09:00").do(get_stock_data)
    elif frequency == "second":
        schedule.every().second.do(get_stock_data)

    # # Start the schedule loop
    while True:
        schedule.run_pending()
        time.sleep(1)

    return render_template('subscribe.html', symbol=symbol, threshold=threshold, frequency=frequency)

def send_notification(symbol, threshold, given_threshold, df_filtered, reciepient, phone, notification_type):
    if notification_type == "mail":
        # Replace the placeholders with your email and password
        email = 'aneeshmacha11@gmail.com'
        password = 'umorpgvkivkpgxrx'
        recipient = reciepient

        if given_threshold:
            subject = f"Stock Price Notification for {symbol}"
            body = f"Stock {symbol} has reached the price threshold of {threshold}.\n\n{df_filtered}"
            
        else:
            subject = f"Stock Price Notification for {symbol}\n"
            body = f"Stock {symbol} has reached the price below threshold of {threshold}.\n\n{df_filtered}"
            

        
        sender = email
        recipients = [recipient]

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        smtp_server.quit()
        
    elif notification_type == "text_message":
        account_sid = 'AC762b1613ee198ceb5815658ca5a44101'
        auth_token = '510755a6aebd1995442dbaacb05d26dd'
        client = Client(account_sid, auth_token)
        if given_threshold:
            body = f"Stock {symbol} has reached the price {threshold}."
        else:
            body = f"Stock {symbol} has reached the price below threshold of {threshold}."
        message = client.messages.create(
        from_='+16074007412',
        body=body,
        to=phone
        )
        print(message.sid)
        
if __name__ == '__main__':
    app.run()
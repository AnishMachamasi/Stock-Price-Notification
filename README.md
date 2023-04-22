## Stock Price Notification System

In this project, we have developed a stock price notification system using Flask, and Yahoo Finance API.

## Requirements
- Python
- Flask
- Yahoo Finance API
  
## Installation
`pip install -r requirements.txt`

## Web Framework
In this project, we used Flask web framework to create the application.
ii. Web Application
For web application, we used HTML and CSS to create a form which allows the user to enter following things:
- stock ticker symbol
- price threshold
- notification frequency(hourly, daily, monthly)
- notification type(email, text message)

## Yahoo Finance API
For this project, we have used API of Yahoo Finance to retrieve the stock market data for the specific stock ticker symbol. We acquire the API from the website https://rapidapi.com/. We specifically chose API of Yahoo Finance which is available on https://rapidapi.com/apidojo/api/yahoo-finance1/.

## Retrieving Data
For retrieving the stock market data for different ticker symbol, we first scheduled a job to run at the specified frequency in a loop. For this, we used Schedule library.

## Detail documentaion
Available at https://drive.google.com/file/d/1f7bh-zyZ1F89piTwkAs6CORcUY2CIK7a/view?usp=share_link

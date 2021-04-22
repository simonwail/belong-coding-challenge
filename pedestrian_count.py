'''
Created on 22/04/2021

@author: Simon Wail

Belong coding challenge to implement pedestrian counting from City of Melbourne data
'''

import argparse
import datetime as dt
import calendar
import pandas as pd
import boto3
import io
from urllib.parse import urlparse

DATA_SOURCE="/Users/simonw/Downloads/Pedestrian_Counting_System_-_Monthly__counts_per_hour_.csv"
COL_NAMES=['ID','Date_Time','Year','Month','Mdate','Day','Time','Sensor_ID','Sensor_Name','Hourly_Counts']
ACCESS_KEY_ID="AKIAZXFQUCNOSLKGLNBT"
SECRET_ACCESS_KEY="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"

NUM_SENSORS=78
HOURS=24

def load_day(df, day):
    '''
    Function to filter Pandas dataframe for a specific day
    
    :param df: Existing dataframe to filter
    :type df: pandas.DataFrame
    :param day: Day to load
    :type day: integer
    
    :rtype: pandas.DataFrame
    '''
    
    return df[df['Mdate']==day]

    
def load_month(year, month):
    '''
    Function to load data into Pandas dataframe for a specific month
    Filter data at read time to avoid loading entire dataset

    :param year: Year to load
    :type year: integer
    :param month: Month to load
    :type month: integer
    :param day: Day to load
    :type day: integer
    
    :rtype: pandas.DataFrame
    '''
    
    global args

    mn_name = calendar.month_name[month]
    
    if args.s3 is None:
        ped_iter = pd.read_csv(DATA_SOURCE, iterator=True, chunksize=NUM_SENSORS * HOURS)
        return pd.concat([chunk[(chunk['Year']==year) & (chunk['Month']==mn_name)] for chunk in ped_iter])
    else:
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)

        s3obj = urlparse(args.s3, allow_fragments=False)

        resp = s3.select_object_content(
            Bucket=s3obj.netloc,
            Key=s3obj.path.lstrip('/'),
            ExpressionType='SQL',
            Expression=f'SELECT s.* FROM s3object s where s."Year"=\'{year}\' and s."Month"=\'{mn_name}\'',
            InputSerialization = {'CSV': {"FileHeaderInfo": "Use"}},
            OutputSerialization = {'CSV': {}},
            )

        records = []
        for event in resp['Payload']:
            if 'Records' in event:
                records.append(event['Records']['Payload'])
                
        file_str = ''.join(r.decode('utf-8') for r in records)

        return pd.read_csv(io.StringIO(file_str), header=0, names=COL_NAMES)
        

def top_n(df, n):
    '''
    Function to aggregate data and calculate top n pedestrian BDistMSITestCase
    
    :param df: dataframe with data to aggregate
    :type df: pandas.dataframe
    :param n: number to top sites to Return
    :type n: Integer
    
    :rtype: pandas.DataFrame
    '''
    
    return df.groupby("Sensor_Name", sort=False)["Hourly_Counts"].sum().sort_values(ascending=False).head(n)
    

def main():
    global args
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", "-d", help="Date to count pedestrians - dd/mm/yyyy")
    parser.add_argument("--month", "-m", help="Month to count pedestrians - mm/yyyy")
    parser.add_argument("--topn", "-n", default=10, help="Top n pedestrian sites to list")
    parser.add_argument("--s3", "-s", help="S3 URL to data source file")
    args = parser.parse_args()

    if args.topn is not None:
        try:
            top = int(args.topn)
        except ValueError:
            print("Invalid top sites number provided.  Setting to default of 10")
            top = 10
        if (top < 1):
            print("Positive number of top sites required.  Setting to default of 10")
            top = 10
    if args.month is not None:
        try:
            dt.datetime.strptime(args.month, '%m/%Y')
        except ValueError:
            print("Incorrect month selection format, should be mm/yyyy")
            parser.print_usage()
            exit(1)
        month, year = args.month.split('/')
        df = load_month(int(year), int(month))
    elif args.date is not None:
        try:
            dt.datetime.strptime(args.date, '%d/%m/%Y')
        except ValueError:
            print("Incorrect date selection format, should be dd/mm/yyyy")
            parser.print_usage()
            exit(1)
        day, month, year = args.date.split('/')
        df = load_month(int(year), int(month))
        df = load_day(df, int(day))
    else:
        today = dt.date.today()
        df = load_month(today.year, today.month)
        df = load_day(df, today.day)
    
    if df.size == 0:
        print("No data available for date selected")
        exit(1)
            
    result = top_n(df, top)
    print(result)
    

if __name__ == "__main__":
    main()

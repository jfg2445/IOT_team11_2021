import aioblescan as aiobs
from aioblescan.plugins import EddyStone
import asyncio
from datetime import date
import paho.mqtt.client as mqtt
import time
import numpy as np
import csv
from random import randrange
print()


### START OF MILESTONE 6 ###

'''
def getFile(file_name):
    data = [] # All the csv data
    X = [] # Max, Min, Humidity
    y = [] # Steps
    file = open(file_name, 'r')

    with file:
        reader = csv.reader(file, delimiter=",")
        for row in reader:
            data.append([", ".join(row)])
            X.append([row[2], row[3], row[4]])
            y.append([row[5]])
        
    X = np.array(X[1::])
    y = np.array(y[1::])
    
    return X, y

def GetWeights(X, y):
    
    ones_x = np.ones((X.shape[0], 1))
    X_ = np.concatenate((ones_x, X), axis = 1) # (644, 4)
    
    X_new = []
    # Convert values from str to float
    for row in X_:
        row_new = []
        for value in row:
            row_new.append(value.astype(np.float32))
        X_new.append(row_new)
    X_ = np.array(X_new)

    y = np.reshape(y,(y.shape[0]*y.shape[1], 1))
    y = np.asfarray(y, float)
    
    #define learning rate
    alpha = 0.0001
    #define the total number of iterations 
    iters = 1000
    #define initial weights
    theta = np.array([[1.0,1.0,1.0,1.0]])

    #compute the mean squared error
    def computecost(X, y, theta):
        inner = np.power((np.matmul(X, theta.T) - y), 2)
        return np.sum(inner)/ (2* len(X))

    #compute the gradient and update the cost
    def gradientDescent(X, y, theta, alpha, iters):
        for i  in range(iters):
            theta = theta - (alpha/len(X)) *np.sum((X@theta.T-y) *X, axis = 0)
            cost = computecost(X, y, theta)
        return (theta, cost)

    g,cost = gradientDescent(X_, y, theta, alpha, iters)
    #print(g, cost)
    # g contains W0, W1, W2 and W3 in order
    
    W0 = g[0][0]
    W1 = g[0][1]
    W2 = g[0][2]
    W3 = g[0][3]
    
    return [[W0, W1, W2, W3], cost]

def PredictSteps(weights, weather):
    y_pred = round((float(weights[1])*float(weather[0])) + (float(weights[2])*float(weather[1])) + (float(weights[3])*float(weather[2])) + float(weights[0]))         
    
    return y_pred

print("----- Milestone 6 -----")
X, y = getFile('steps.csv')
X_test, y_test = getFile('steps_test.csv')
y_pred = []
weights_all = []
cost_all = []

weights_initial = GetWeights(X, y)
W0_initial, W1_initial, W2_initial, W3_initial = weights_initial[0]
cost_all.append(weights_initial[1])
print("Initial weights for the model are:")
print("W0:", W0_initial)
print("W1:", W1_initial)
print("W2:", W2_initial)
print("W3:", W3_initial)
print("")

# Loop through test data
for i in range(len(X_test)):
    # Append new data to existing data
    X_new = np.array([X_test[i][0], X_test[i][1], X_test[i][2]])
    y_new = np.array([y_test[i][0]])
    
    X = np.vstack((X, X_new))
    y = np.vstack((y, y_new))
    
    # Retrain model with new row
    weights_after = GetWeights(X, y)
    weights = weights_after[0]
    weights_all.append(weights)
    cost_all.append(weights_after[1])
    
    # Get predicted steps
    steps = PredictSteps(weights, X_new)
    y_pred.append(steps)
    
    # Print a report
    print("Iteration {}:".format(i+1))
    print("W0:", weights[0])
    print("W1:", weights[1])
    print("W2:", weights[2])
    print("W3:", weights[3])
    print("Actual steps:", y_test[i][0])
    print("Predicted steps:", steps)
    
    print()    
'''
### END OF MILESTONE 6 ###

def _process_packet(data):
    ev = aiobs.HCI_Event()
    xx = ev.decode(data)
    xx = EddyStone().decode(ev)
    if xx:
        url = xx['url'] # URL will be in the format: team11-steps?#
        steps = int(url.split('?',1)[1]) # This will get just the number at the end of the URL
        print("----- Milestone 2 -----")
        print("Step count received on {} is {}.".format(date.today(), steps))
        print()
        
        # From the client.py file, this will get the steps to the Android device
        broker_address = "192.168.4.1" #enter your broker address here
        subscribetopic = "weather"
        publishtopic = "steps"

        def on_message(client, userdata, message):
            values = (message.payload.decode("utf-8")).split(", ")
            weights = []
            weather_today = []
            weather_tomorrow = []
            regr_today = 0
            regr_tomorrow = 0
            goal_met = ""
            
            if len(values) == 1:
                print("----- Milestone 4 -----")
                print(str(message.payload.decode("utf-8")))
                print()
            else:
                weights = values[:4]
                weather_today = values[4:7]
                weather_tomorrow = values[7:]
                
                regr_today = round((float(weights[1])*float(weather_today[0])) + (float(weights[2])*float(weather_today[1])) + (float(weights[3])*float(weather_today[2])) + float(weights[0]))
                regr_tomorrow = round((float(weights[1])*float(weather_tomorrow[0])) + (float(weights[2])*float(weather_tomorrow[1])) + (float(weights[3])*float(weather_tomorrow[2])) + float(weights[0]))
            
                print("----- Milestone 5 -----")
                print("Today's high, low, and humidity: {}, {}, {}".format(weather_today[0], weather_today[1], weather_today[2]))
                print("Tomorrows's high, low, and humidity: {}, {}, {}".format(weather_tomorrow[0], weather_tomorrow[1], weather_tomorrow[2]))
                print()
                
                if (int(steps) >= int(regr_today)):
                    goal_met = "Goal achieved, keep going!"
                    print("GOAL MET! Predicted steps: {}. Actual steps: {}.".format(regr_today, steps))
                else:
                    goal_met = "Work harder"
                    print("Goal not met :( Predicted steps: {}. Actual steps: {}.".format(regr_today, steps))
                    print()
                    
                ### MILESTONE 7 CALORIE COUNTER ###
                bucket = 0
                # Calculate calories burned based on steps * a constant
                calories = round(steps * 0.045)
                print("----- Milestone 7 -----")
                print("Calories burned:", calories)
                
                # Determine bucket that calorie count falls in
                if calories <= 100:
                    bucket = 1
                elif (calories > 100) and (calories <= 150):
                    bucket = 2
                elif (calories > 150) and (calories <= 200):
                    bucket = 3
                elif calories > 200:
                    bucket = 4
                
            time.sleep(5)
            
            client.publish(publishtopic, bucket) # Send the message to the Android device

        client = mqtt.Client("P1")
        client.on_message = on_message
        client.connect(broker_address)
        client.loop_start()
        client.subscribe(subscribetopic)
        time.sleep(10)
        client.loop_stop()
        
if __name__ == '__main__':
    mydev = 0
    event_loop = asyncio.get_event_loop()
    mysocket = aiobs.create_bt_socket(mydev)
    fac = event_loop._create_connection_transport(mysocket,aiobs.BLEScanRequester,None,None)
    conn, btctrl = event_loop.run_until_complete(fac)
    btctrl.process = _process_packet
    btctrl.send_scan_request()
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        print('keyboard interrupt')
    finally:
        print('closing event loop')
        btctrl.stop_scan_request()
        conn.close()
        event_loop.close()
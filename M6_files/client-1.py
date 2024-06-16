import aioblescan as aiobs
from aioblescan.plugins import EddyStone
import asyncio
from datetime import date
import paho.mqtt.client as mqtt
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def getWeights():
    print("WEIGHTS FUNCTION")
    
    df = pd.read_csv(r"step.csv")

    # Normalization
    X = df[["max", "min", "humidity"]].values #28 days data, 23 unique user id steps
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    y = df["steps"].values
    y = y.reshape(y.shape[0],1)

    print(X.shape)  # (644, 3)
    print(y.shape) # (644, 1)

    ones_x = np.ones((28*23, 1))
    X_ = np.concatenate((ones_x, X), axis = 1) # (644, 4)

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
    print(g, cost)
    # g contains W0, W1, W2 and W3 in order

    X1 = df[["max"]].values
    X2 = df[["min"]].values
    X3 = df[["humidity"]].values

    ### Steps = W0 + W1* Max + W2 * Min + W3 * Humidity
    #y_pred = 343.31046642 + 12.71992071*X1 + 30.79605817*X2 -20.79486607*X3
    #print("Max step:", y_pred.max(), ", Min step: ", y_pred.min())
    
    return g

def _process_packet(data):
    ev = aiobs.HCI_Event()
    xx = ev.decode(data)
    xx = EddyStone().decode(ev)
    if xx:
        url = xx['url'] # URL will be in the format: team11-steps?#
        steps = int(url.split('?',1)[1]) # This will get just the number at the end of the URL
        print("Step count received on {} is {}.".format(date.today(), steps))
        
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
                print("")
                print(str(message.payload.decode("utf-8")))
            else:
                #weights = values[:4]
                weights = getWeights()
                print("NEW WEIGHTS")
                print(weights)
                weather_today = values[4:7]
                weather_tomorrow = values[7:]
                
                regr_today = round((float(weights[1])*float(weather_today[0])) + (float(weights[2])*float(weather_today[1])) + (float(weights[3])*float(weather_today[2])) + float(weights[0]))
                regr_tomorrow = round((float(weights[1])*float(weather_tomorrow[0])) + (float(weights[2])*float(weather_tomorrow[1])) + (float(weights[3])*float(weather_tomorrow[2])) + float(weights[0]))
                
                print("Today's high, low, and humidity: {}, {}, {}".format(weather_today[0], weather_today[1], weather_today[2]))
                print("Tomorrows's high, low, and humidity: {}, {}, {}".format(weather_tomorrow[0], weather_tomorrow[1], weather_tomorrow[2]))
                print("")
                
                if (steps >= regr_today):
                    goal_met = "Goal achieved, keep going!"
                    print("GOAL MET! Predicted steps: {}. Actual steps: {}.".format(regr_today, steps))
                else:
                    goal_met = "Work harder"
                    print("Goal not met :( Predicted steps: {}. Actual steps: {}.".format(regr_today, steps))
                
            time.sleep(5)
            
            client.publish(publishtopic, goal_met) # Send the message to the Android device

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
        


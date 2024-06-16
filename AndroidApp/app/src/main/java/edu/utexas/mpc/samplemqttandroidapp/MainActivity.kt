package edu.utexas.mpc.samplemqttandroidapp

import android.content.DialogInterface
import android.content.Intent
import android.os.Bundle
import android.support.v7.app.AlertDialog
import android.support.v7.app.AppCompatActivity
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import com.android.volley.RequestQueue
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import com.google.gson.Gson
import com.squareup.picasso.Picasso
import kotlinx.android.synthetic.main.activity_main.*
import org.eclipse.paho.android.service.MqttAndroidClient
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended
import org.eclipse.paho.client.mqttv3.MqttMessage

class MainActivity : AppCompatActivity() {

    lateinit var queue: RequestQueue
    lateinit var gson: Gson
    lateinit var mostRecentWeatherResult: WeatherResult

    var w0 = 3697.766801
    var w1 = 64.69992133
    var w2 = 283.57456519
    var w3 = -109.19405416

    var tempHighToday = 0.0
    var tempLowToday = 0.0
    var humidityToday = 0

    var tempHighTomorrow = 0.0
    var tempLowTomorrow = 0.0
    var humidityTomorrow = 0

    // I'm doing a late init here because I need this to be an instance variable but I don't
    // have all the info I need to initialize it yet
    lateinit var mqttAndroidClient: MqttAndroidClient

    // you may need to change this depending on where your MQTT broker is running
    val serverUri = "tcp://192.168.4.1"
    // you can use whatever name you want to here
    val clientId = "EmergingTechMQTTClient"

    //these should "match" the topics on the "other side" (i.e, on the Raspberry Pi)
    val subscribeTopic = "steps"
    val publishTopic = "weather"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // when button is clicked, show the alert
        btnShowAlert.setOnClickListener {
            // build alert dialog
            val dialogBuilder = AlertDialog.Builder(this)

            println("****** INSIDE OF THE BUTTON DIALOG")

            /* GET WEATHER */
            queue = Volley.newRequestQueue(this)
            gson = Gson()

            requestWeather()

            // initialize the paho mqtt client with the uri and client id
            mqttAndroidClient = MqttAndroidClient(getApplicationContext(), serverUri, clientId);

            val openWirelessSettings: Intent = Intent("android.settings.WIFI_SETTINGS")
            startActivity(openWirelessSettings)

            // set message of alert dialog
            dialogBuilder.setMessage("Click \"PROCEED\" to switch networks. Once you return to the screen, you will be connected to the Raspberry Pi!")
                    // if the dialog is cancelable
                    .setCancelable(false)
                    // positive button text and action
                    .setPositiveButton("Proceed", DialogInterface.OnClickListener {
                        dialog, id -> syncWithPi()

                        // when things happen in the mqtt client, these callbacks will be called
                        mqttAndroidClient.setCallback(object: MqttCallbackExtended {

                            // when the client is successfully connected to the broker, this method gets called
                            override fun connectComplete(reconnect: Boolean, serverURI: String?) {
                                println("Connection Complete!!")
                                // this subscribes the client to the subscribe topic
                                mqttAndroidClient.subscribe(subscribeTopic, 0)
                                val message = MqttMessage()
                                val str: String = weatherText.text.toString()
                                message.payload = (str).toByteArray()

                                val weatherMessage = MqttMessage()
                                val weatherStr: String = "$w0, $w1, $w2, $w3, $tempHighToday, $tempLowToday, $humidityToday, $tempHighTomorrow, $tempLowTomorrow, $humidityTomorrow"
                                weatherMessage.payload = (weatherStr).toByteArray()

                                // this publishes a message to the publish topic
                                mqttAndroidClient.publish(publishTopic, message)
                                mqttAndroidClient.publish(publishTopic, weatherMessage)
                            }

                            // this method is called when a message is received that fulfills a subscription
                            override fun messageArrived(topic: String?, message: MqttMessage?) {
                                println(message)
                                val bucket1 = listOf(Pair("Lemon Garlic Hummus","https://emilybites.com/2019/07/lemon-garlic-hummus.html"),Pair("Zucchini Parmesan","https://recipes.sparkpeople.com/recipe-detail.asp?recipe=2718"),Pair("Stuffed Mushrooms","https://recipes.sparkpeople.com/recipe-detail.asp?recipe=60501"))
                                val bucket2 = listOf(Pair("Fried Cauliflower with Vegetables","https://www.womendailymagazine.com/vegetable-dishes-under-100-calories/"),Pair("Tortilla Chips & Guacamole","https://www.mealswithmaggie.com/healthy-baked-tortilla-chips/"),Pair("Celery Soup","https://www.bbcgoodfood.com/recipes/celery-soup"))
                                val bucket3 = listOf(Pair("Boom Bang-a-Bang Chicken Cups","https://www.bbcgoodfood.com/recipes/boom-bang-bang-chicken-cups"),Pair("Crab & Sweetcorn Chowder","https://www.bbcgoodfood.com/recipes/crab-sweetcorn-chowder"),Pair("Mediterranean Vegetables with Lamb","https://www.bbcgoodfood.com/recipes/mediterranean-vegetables-lamb"))
                                val bucket4 = listOf(Pair("Spicy Moroccan Eggs","https://www.bbcgoodfood.com/recipes/spicy-moroccan-eggs"),Pair("Teriyaki Salmon Parcels","https://www.bbcgoodfood.com/recipes/teriyaki-salmon-parcels"),Pair("Tomato & Crispy Crumb Chicken","https://www.bbcgoodfood.com/recipes/tomato-crispy-crumb-chicken"))

                                val textView : TextView = findViewById(R.id.textView) // Get the TextView on the app display
                                val textViewLink : TextView = findViewById(R.id.textViewLink)

                                if ((message.toString()).toInt() == 1) {
                                    val (recipeName, recipeLink) = bucket1.shuffled().take(1)[0]
                                    println(recipeName)
                                    println(recipeLink)

                                    val string = "You burned less than 100 calories today. Your selected recipe is: $recipeName"
                                    textView.text = string
                                    textViewLink.text = recipeLink
                                }
                                else if ((message.toString()).toInt() == 2) {
                                    val (recipeName, recipeLink) = bucket2.shuffled().take(1)[0]
                                    println(recipeName)
                                    println(recipeLink)

                                    val string = "You burned between 100 and 150 calories today. Your selected recipe is: $recipeName"
                                    textView.text = string
                                    textViewLink.text = recipeLink
                                }
                                else if ((message.toString()).toInt() == 3) {
                                    val (recipeName, recipeLink) = bucket3.shuffled().take(1)[0]
                                    println(recipeName)
                                    println(recipeLink)

                                    val string = "You burned between 150 and 200 calories today! Your selected recipe is: $recipeName"
                                    textView.text = string
                                    textViewLink.text = recipeLink
                                }
                                else if ((message.toString()).toInt() == 4) {
                                    val (recipeName, recipeLink) = bucket4.shuffled().take(1)[0]
                                    println(recipeName)
                                    println(recipeLink)

                                    val string = "You burned more than 200 calories today!! Your selected recipe is: $recipeName"
                                    textView.text = string
                                    textViewLink.text = recipeLink
                                }
                            }

                            override fun connectionLost(cause: Throwable?) {
                                println("Connection Lost")
                            }

                            // this method is called when the client succcessfully publishes to the broker
                            override fun deliveryComplete(token: IMqttDeliveryToken?) {
                                println("Delivery Complete")
                            }
                        })
                    })
                    // negative button text and action
                    .setNegativeButton("Cancel", DialogInterface.OnClickListener {
                        dialog, id -> dialog.cancel()
                    })

            // create dialog box
            val alert = dialogBuilder.create()
            // set title for alert dialog box
            alert.setTitle("Switch Networks")
            // show alert dialog
            alert.show()
        }

    }

    private fun requestWeather(){
        //val url = StringBuilder("https://api.openweathermap.org/data/2.5/weather?q=Austin&units=Imperial&appid=c8b7d0cddf29f7eec67f66420104f4b9").toString()
        val url = StringBuilder("https://api.openweathermap.org/data/2.5/onecall?lat=30.2672&lon=-97.7431&units=Imperial&exclude=current,minutely,hourly&appid=fdcb0b20a021369b9f2466b1dbc14df1").toString()
        val stringRequest = object : StringRequest(com.android.volley.Request.Method.GET, url,
                com.android.volley.Response.Listener<String> { response ->
                    mostRecentWeatherResult = gson.fromJson(response, WeatherResult::class.java)
                    val weatherText = this.findViewById<TextView>(R.id.weatherText)
                    weatherText.text = "Current weather for Austin is: " + mostRecentWeatherResult.daily[0].weather[0].main

                    // Get today's weather
                    tempHighToday = mostRecentWeatherResult.daily[0].temp.max
                    tempLowToday = mostRecentWeatherResult.daily[0].temp.min
                    humidityToday = mostRecentWeatherResult.daily[0].humidity

                    // Get tomorrow's weather
                    tempHighTomorrow = mostRecentWeatherResult.daily[1].temp.max
                    tempLowTomorrow = mostRecentWeatherResult.daily[1].temp.min
                    humidityTomorrow = mostRecentWeatherResult.daily[1].humidity

                    // Show weather icon
                    val weather_icon_iv = findViewById<ImageView>(R.id.imageView)
                    val icon_code = mostRecentWeatherResult.daily[0].weather[0].icon
                    val icon_url = "https://openweathermap.org/img/wn/" + icon_code + "@2x.png"
                    Picasso.with(this).load(icon_url).into(weather_icon_iv)

                    println("****** WEATHER RECEIVED")
                },
                com.android.volley.Response.ErrorListener { error->

                    println("****** That didn't work!")
                    println(error)
                }) {}
        // Add the request to the RequestQueue.
        queue.add(stringRequest)
    }

    // this method just connects the paho mqtt client to the broker
    private fun syncWithPi(){
        println("+++++++ Connecting...")
        mqttAndroidClient.connect()
    }

}

class WeatherResult(val daily: ArrayList<Daily>)

class Daily(val temp: Temp, val humidity: Int, val weather: ArrayList<Weather>)
class Temp(val min: Double, val max: Double)
class Weather(val main: String, val icon: String)
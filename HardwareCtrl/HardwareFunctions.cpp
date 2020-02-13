/*
  HardwareFunctions.cpp - Secondary
    Dependents: ActuatorCtrl.h, LoadComp.h, InfraredSensor.h

  Arch2
  Version: 0.2.0 - 12/09/19
  INCOMPLETE - CHECK FILE
*/

#include "HardwareFunctions.h"
#include "ActuatorCtrl.h"
#include "LoadComp.h"
#include <Arduino.h>
#include "InfraredSensor.h"

//#include "SparkFun_MLX90632_Arduino_Library.h"
//#define MLX90632_DEFAULT_ADDRESS 0x3B 
//MLX90632 myTempSensor;

//  TODO - OPTIMIZE MAX_TIME VALUE FOR LOWER AND RAISE HEAD METHODS

ActuatorCtrl a;
LoadComp l;
InfraredSensor infraredThermal;


/*
    setup()
    Sets up all the components.
*/
void HardwareFunctions::setup() {
    //  BUTTON SETUP
    {
        pinMode(BUTTON_1, INPUT);
        pinMode(BUTTON_1, OUTPUT); 
        pinMode(BUTTON_2, INPUT);
        pinMode(BUTTON_2, OUTPUT);
    }
    a.setup();
    l.setup();
    infraredThermal.setup();

}

void HardwareFunctions::logging() {

  Serial.print("pressure value: ");
  Serial.println(l.quickRead());
}

/*
    lowerHead()
    Lowers the Head.
*/
int HardwareFunctions::lowerHead(bool debug, int critical_force) {
    //bool isTimeout = false;
    long startTime;
    const int MAX_TIME = 2500;  // 1550 CONSTANTS NEED TO BE SET IN A UNIVERSAL SPACE

    l.tare();
    startTime = millis();
    a.retract();
    
    while( a.isMoving() && (millis()-startTime < MAX_TIME) ){
        
//        if(l.quickRead() >= critical_force){
//            a.stop();
//            Serial.println(l.quickRead());
//            return 202;
//        }   //  end if-statement
    
    }   //  end while-loop
    a.stop();

    
    /*
    debug = false;
    if (debug){
        //  DEBUGGING INFO HERE -- REDUCED CHARACTERS PRINTED TO DECREASE SERIAL PRINT BLOAT
        Serial.print("\tto: ");         //  Timeout?
        //Serial.println(isTimeout);
        Serial.print("\tto_v: ");       //  preset Timeout value
        Serial.println(MAX_TIME);
        Serial.print("\tcf: ");         //  Current force
        Serial.println(l.calibratedRead(10));
        Serial.print("\tctclf: ");      //  preset critical force
        Serial.println(critical_force);
    }
    //  RETURN RESPONSE ID
    */
    if ((millis()-startTime >= MAX_TIME)){
        return 201; //  "Head state unknown, timeout."
    }
    //return 202; //  "Head Lowered, Critical Force reached."

}   //  end lowerHead()


/*
    raiseHead()
    Raises the head.
*/
int HardwareFunctions::raiseHead() {
    const int MAX_TIME = 2500;  //1500  CONSTANTS NEED TO BE SET IN A UNIVERSAL SPACE
    long init_time;

    a.extend();
    init_time = millis();
    while ((millis()-init_time < MAX_TIME)){
        // should be lowering
        //  if the actuators have feedback capabilities, add that check to this method

    }   //  end while-loop

    a.stop();
    return 201;

}   //  end raiseHead()


/*
    buttonWait()
    Waits for both hardware buttons to be held simultaneously for 2 seconds when called.
*/
int HardwareFunctions::buttonWait() {
    const int MAX_TIME = 15000;  //1500  CONSTANTS NEED TO BE SET IN A UNIVERSAL SPACE
    long init_timeout;
    bool completed = false;

    while(!completed or (millis() - init_timeout < MAX_TIME) ){

        long init_time = millis();
        while(digitalRead(BUTTON_1) && digitalRead(BUTTON_2) && !completed ){

            if (millis()-init_time >= 2000){
                completed = true;
                break;  //  necessary?

            }   //  end if-statement

        }   //  end while-loop

    }   //  end while-loop

    if (completed) {
      return 201;
    } else {
      return 202;
    }

}   //  end buttonWait()

//int HardwareFunctions::autoMode() {
//    return 201;
//}

float HardwareFunctions::readObjTempF() {
    return float(infraredThermal.getObjTempF());

}   //  end read object temperature()

float HardwareFunctions::readAmbTempC() {
    return float(infraredThermal.getAmbTempC());

}   //  end read ambient temperature()
//int HardwareFunctions::readObjTemp() {
//    float objectTemp_F = myTempSensor.getObjectTempF(); //Get the temperature of the object we're looking at
//
//    return 5*(objectTemp_F-32)/9;
//}
//
//int HardwareFunctions::readAmbTemp() {
//
////    float /sensorTemp_C = myTempSensor.getSensorTemp(); //Get the temperature of the sensor
//
//    return myTempSensor.getSensorTemp();;
//}

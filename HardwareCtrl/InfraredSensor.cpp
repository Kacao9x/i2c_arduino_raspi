/*
  InfraredSensor.cpp - Tertiary
    Dependents: MLX90632.h
    
  Arch1
  ...
*/


#include "SparkFun_MLX90632_Arduino_Library.h"
#include "Wire.h"
#include "Arduino.h"
#include "InfraredSensor.h"
#define MLX90632_DEFAULT_ADDRESS 0x3B

MLX90632 myTempSensor;

void InfraredSensor::setup() {
    
    /* init Temp sensor */
  MLX90632::status errorFlag; //Declare a variable called errorFlag that is of type 'status'
  myTempSensor.begin(MLX90632_DEFAULT_ADDRESS, Wire, errorFlag);

  if(errorFlag == MLX90632::SENSOR_SUCCESS)
  {
    Serial.println("MLX90632 online!");
  }
  else
  {
    //Something went wrong
    if(errorFlag == MLX90632::SENSOR_ID_ERROR) Serial.println("Sensor ID did not match the sensor address. Probably a wiring error.");
    else if(errorFlag == MLX90632::SENSOR_I2C_ERROR) Serial.println("Sensor did not respond to I2C properly. Check wiring.");
    else if(errorFlag == MLX90632::SENSOR_TIMEOUT_ERROR) Serial.println("Sensor failed to respond.");
    else Serial.println("Other Error");
  }
}

float InfraredSensor::getObjTempF() {
    return float(myTempSensor.getObjectTempF());
}

float InfraredSensor::getObjTemp() {
    return float(5*(myTempSensor.getObjectTempF()-32)/9);
}

float InfraredSensor::getAmbTempC(){
    return float(myTempSensor.getSensorTemp());
}

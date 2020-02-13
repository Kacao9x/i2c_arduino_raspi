/*
  InfraredSensor.h
    Dependents: MLX90632 adafruit.h

  Arch1
  ---
*/

#ifndef InfraredSensor_h
#define InfraredSensor_h

#include "Arduino.h"
#include "Wire.h"

class InfraredSensor
{
  public:

    void setup();

    float InfraredSensor::getObjTempF();

    float InfraredSensor::getObjTemp();

    float InfraredSensor::getAmbTempC();

};

#endif

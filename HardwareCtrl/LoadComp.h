/*
  LoadComp.h - Tertiary
    Dependents: HX711.h

  Arch1
  ---
*/

#ifndef LoadComp_h
#define LoadComp_h

#include "HX711.h"
#include "Arduino.h"

class LoadComp
{
  public:

    void setup();

    float calibratedRead(int sample);

    float quickRead();

    void tare();

    void sleep();

    void wake();

};

#endif

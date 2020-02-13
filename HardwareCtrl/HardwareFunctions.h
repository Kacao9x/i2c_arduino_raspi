/*
  HardwareFunctions.h - Secondary

  Arch2
  Version: 0.2.0 - 12/09/19
  INCOMPLETE - CHECK FILE
*/

#ifndef HardwareFunctions_h
#define HardwareFunctions_h

#include "Arduino.h"

class HardwareFunctions
{
  private:
    const int BUTTON_1 = 5;
    const int BUTTON_2 = 6;

  public:

    void setup();

    //  default critical force is 250g (subject to change)
    int lowerHead(bool debug = true, int critical_force = 3500); //250 is default value

    int raiseHead();

    int buttonWait();

    void softwareReset();

    int autoMode();

    float readObjTempF();

    float readAmbTempC();

    void logging();

};

#endif

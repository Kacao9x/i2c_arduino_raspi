/*
  ActuatorCtrl.h - Tertiary

  Arch2
  Version: 0.1.1 - 11/27/19
*/

#define ActuatorCtrl_h

#include "Arduino.h"

class ActuatorCtrl
{
  private:
    const int STD_RELAY = 7;
    const int NEG_RELAY = 8;
    bool inMotion = false;

  public:

    void setup();

    void extend();

    void retract();

    void stop();

    bool isMoving();

};

/*
  ActuatorCtrl.cpp - Tertiary
    Dependents: ActuatorCtrl.h

  Arch2
  Version: 0.1.1 - 11/27/19
*/

#include "ActuatorCtrl.h"


/*
    setup()
    Sets up the linear actuator.
*/
void ActuatorCtrl::setup() {
    pinMode(STD_RELAY, OUTPUT);         //  set pinmode of standard relay ctrl pin to OUTPUT
    pinMode(NEG_RELAY, OUTPUT);         //  set pinmode of negative relay ctrl pin to OUTPUT
    stop();

}   //  end setup()


/*
    extend()
    Toggles the actuator to extend, sets inMotion to TRUE.
*/
void ActuatorCtrl::extend() {
    inMotion = true;                    //  set var 'inMotion' to TRUE
    digitalWrite(NEG_RELAY, LOW);       //  set power of negative relay ctrl to LOW
    digitalWrite(STD_RELAY, HIGH);      //  set power of standard relay ctrl to HIGH

}   //  end extend()


/*
    retract()
    Toggles the actuator to retract, sets inMotion to TRUE.
*/
void ActuatorCtrl::retract() {
    inMotion = true;                    //  set var 'inMotion' to TRUE
    digitalWrite(STD_RELAY, LOW);       //  set power of standard relay ctrl to LOW
    digitalWrite(NEG_RELAY, HIGH);      //  set power of negative relay ctrl to HIGH

}   //  end retract()


/*
    stop()
    Stops any actuator movement, sets inMotion to FALSE.
*/
void ActuatorCtrl::stop() {
    inMotion = false;                   //  set var 'inMotion' to TRUE
    digitalWrite(STD_RELAY, LOW);       //  set power of standard relay ctrl to LOW
    digitalWrite(NEG_RELAY, LOW);       //  set power of negative relay ctrl to LOW

}   //  end stop()


/*
    isMoving()
    Returns if the actuator is currently in a motion state.
*/
bool ActuatorCtrl::isMoving() {
    return inMotion;                        //  return var 'inMotion'

}   //  end isMoving()

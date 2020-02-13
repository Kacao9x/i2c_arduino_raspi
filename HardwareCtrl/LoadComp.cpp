/*
  LoadComp.cpp - Tertiary
    Dependents: ActuatorCtrl.h, LoadComp.h

  Arch1
  ...
*/

#include "LoadComp.h"

const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

HX711 scale;

void LoadComp::setup() {
    
    scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
    scale.set_scale(8);                     
    scale.tare();

    if (calibratedRead(32) > 0.25){
        scale.tare();
    }
}

float LoadComp::calibratedRead(int sample) {
    return scale.get_units(sample);
}

float LoadComp::quickRead(){
  //Serial.println(scale.fast_read());
    return scale.fast_read();
}

void LoadComp::sleep() {
    scale.power_down();  
}

void LoadComp::wake() {
    scale.power_up();
}

void LoadComp::tare() {
    scale.tare();    
}

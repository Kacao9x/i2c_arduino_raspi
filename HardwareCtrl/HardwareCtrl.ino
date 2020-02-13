/*
  SystemCtrl.ino - Primary
    Dependents: HardwareFunctions.h, ActuatorCtrl.h, LoadComp.h

  Arch2
  Version: 0.2.0 - 12/09/19
*/

#include <Wire.h>
#include "HardwareFunctions.h"
#include "ActuatorCtrl.h"
#include "LoadComp.h"

#define SLAVE_ADDRESS 0x04
#define RESPONSE_WIRE 9

//volatile byte b[3] = {3, 3, 3};
// volatile byte b[4] = {4, 4, 4, -1};
DATA_CHUNK_SIZE = 4
volatile float b[DATA_CHUNK_SIZE];
volatile byte request[2] = {0, 0};
volatile bool inProcess;

typedef struct {
  byte status_code;     // code status responding to raspi command
  float objTemp;
  float ambientTemp;
} enclosureData;

enclosureData returnData;

HardwareFunctions sys;

void(* resetFunc) (void) = 0;

void interruptProcess(){
  digitalWrite(RESPONSE_WIRE, HIGH);
  delay(100);                                 //  SENSITIVE VALUE
  digitalWrite(RESPONSE_WIRE, LOW);
  inProcess = false;
} //  end interruptProcess()

void receiveData(int byteCount) {
  int ct = 0;
  while (Wire.available()) {
    byte temp = Wire.read();
    if (temp != 0){
      request[ct] = temp;
      inProcess = true;
      ct++;

    } //  end if-statement

  } //  end while-loop

} //  end receiveData()

void sendData() {
  //b = {current_request, request_variable, response};
  // Wire.write((byte*)b, 4);
  Wire.write((byte*)b, DATA_CHUNK_SIZE * sizeof(float));
  b[0], b[1], b[2], b[3], request[0], request[1] = 0;
  // Wire.write( (byte*) &returnData, sizeof(returnData))
  inProcess = false;

} //  end sendData()

void init_comms() {
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

  pinMode(RESPONSE_WIRE, OUTPUT);
  digitalWrite(RESPONSE_WIRE, LOW);
  inProcess = false;

} //  end init_comms()

void setup() {
  Serial.begin(9600);
  while (!Serial){//do nothing}

  returnData.ambientTemp = -1;
  returnData.objTemp = -1;
  returnData.status_code = -1;

  init_comms();
  sys.setup();
  sys.raiseHead();
  Serial.println("Transmission Ready");

} //  end setup()

void loop() {
  if (inProcess){
    b[0] = request[0];
    b[1] = request[1];
    switch (b[0]){
      case 100:   //  "test communication"
        b[2] = 201;
        
        break;
    
      case 101:   //  "RPi is done with setup/ready"
        b[2] = 201;
        break;

      case 102:   //  "RPi is waiting for button hold"
        b[2] = sys.buttonWait();
        break;
  
      case 103:   //  "RPi is waiting for arm to be lowered"
        b[2] = sys.lowerHead();
        break;

      case 104:   //  "capture complete"
        b[2] = sys.raiseHead();
        break;

      case 105:
        b[2] = sys.readObjTempF();
        b[3] = sys.readAmbTempC();
        break;
        
      /* */
      case 20:
        Serial.println("software reset");
        b[2] = 201;
        resetFunc();
        break;
      
      default:    //  "unknown request id"
        //  TODO: ERROR HANDLING
        break;
      
    } //  end switch-statement
    delay(10);
    interruptProcess();

  } //  end if-statement
  
} //  end loop()

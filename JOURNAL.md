## july 6 & 7

got inpsiration for this project from this reel: https://www.instagram.com/p/DKDFd3nS-c8/
other inspiration: https://circuitdigest.com/microcontroller-projects/DIY-wifi-controlled-drone

goals of this drone:

- can fly reliably
- wireless controller
- PID control
- 4 ish minute flight time
- usb c charging
- can have semi reliable autonomous paths (can create one to takeoff, fly from my room to couch, and land, reliably)

the guy uses NewBeeDrone BDR GOLD Edition - 6mm Brushed Motor, so i'll be basing my design off of these motors

shoutout to this blog article for being quite helpful in esp selection: https://eitherway.io/posts/esp32-buyers-guide/
i will go with the esp-32 c3 for its bluetooth 5.0 and efficiency

parts v1:
NewBeeDrone BDR GOLD Edition - 6mm Brushed Motor (https://newbeedrone.com/products/newbeedrone-bdr-gold-edition-6mm-brushed-motor)
Bitcraze Crazyflie Nano Quadcopter Replacement Propellers (https://ca.robotshop.com/products/crazyflie-nano-quadcopter-replacement-propellers)
Fytoo 5pcs 3.7V 500mAh 25C Li Battery (https://www.amazon.ca/dp/B0794ZPVSX)
ESP32-C3 (https://www.digikey.ca/en/products/detail/espressif-systems/ESP32-C3/14115579)
GY-87 (https://x2robotics.ca/gy-87-10dof-mpu6050-hmc5883l-bmp180-sensor-module)
TYPE-C-31-M-12 (https://lcsc.com/product-detail/USB-Type-C_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.html)
TP4056 (https://www.aliexpress.com/item/1005005838857868.html)
SPX3819M5-L-3-3 (https://www.aliexpress.com/item/1005007348027539.html)
IRLZ44N (https://www.aliexpress.com/item/1005006228628494.html)

- figure out how to implement tp4056 with battery protection or figure out if its not necessary
- figure out how to add breakout board to custom pcb

components left: motor driver, battery charge terminal, controller components (oled screen etc)

+4 hours; lot of research :( 

making a choice not to use usb uart bc im using esp32 c3 and will just use the native usb support

## july 8th

first schematic: the powering (2.5 hours)

components:
usb_c_receptable_usb2.0_16p
AO3401A
SS34
SPX3819M5-L-3-3
4 capacitors, 3 resistors, and 1 led

![power](assets/image1.png)

circuit explanation for later me:
- cc1 and cc2 have resistors to let chargers know to supply power, not take in power
- vbus is 5v, the goal of the circuit is to convert it into stable 3v
- power goes to ss34 where cathode is toward vbus, prevents reverse current
- r3 ensures mosfet is on when usb isnt connected due to gnd connection, and turns mosfet off when usb is connected
- ao3401A (mosfet) allows for battery power when usb isnt connected
- EN is to turn the ldo on, which acts as the power switch for the entire device
- BP is for noise reduction, adding a capacitor does this
- two more capaicitors to add stabalization on the 3v3 rail, connected in parallel and will supply voltage in drops
- green led for on status

second schematic: battery (0.5 hour)

components:
TP4056
2 resistor, 3 resistor, 1 capacitor
51005-0200 molex female housing

![battery](assets/image2.png)

circuit explanation: 
- power comes from vcc
- ce turns on charging, connected to 5v so always charging
- epad is for cooling
- temp is for temp monitoring (not doing that)
- prog is to set charging amps (1amp at 1.2k resistor)
- capicitor smooths out charging

third schematic: on/off and voltage monitoring (battery control)

components:
3 resistors
MST22D18G2_125 (https://www.amazon.ca/100Pcs-MSS22D18-Miniature-Switch-Handle/dp/B093LBLK6D)

![batterycontrol](assets/image3.png)
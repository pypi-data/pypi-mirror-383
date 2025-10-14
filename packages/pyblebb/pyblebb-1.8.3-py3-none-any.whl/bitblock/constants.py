from enum import Enum


__all__ = [
    "SYMBOL",
    "COLOR",
    "NOTE",
    "PIN",

    "BBPACKET",
    "BBRETURN",
    "ACTION_CODE",
    "ACTION_MODE",
    "NULL_COMMAND_PACKET",
    "LENGTH_OF_PACKET",
    "BLEUUID",
    "ERROR"
]

class PIN:
    P0 = 10
    P1 = 4
    P2 = 8
    P3 = 2
    P4 = 47  # 9
    P7 = 39
    P11 = 48  #7
    P12 = 18
    P13 = 12
    P14 = 13
    P15 = 11
    P16 = 46
    SERVO = 16
    DCMOTOR = 46

class SYMBOL:
    CHAR_A= 'A'
    CHAR_B= 'B'
    CHAR_C= 'C'
    CHAR_D= 'D'
    CHAR_E= 'E'
    CHAR_F= 'F'
    CHAR_G= 'G'
    CHAR_H= 'H'
    CHAR_I= 'I'
    CHAR_J= 'J'
    CHAR_K= 'K'
    CHAR_L= 'L'
    CHAR_M= 'M'
    CHAR_N= 'N'
    CHAR_O= 'O'
    CHAR_P= 'P'
    CHAR_Q= 'Q'
    CHAR_R= 'R'
    CHAR_S= 'S'
    CHAR_T= 'T'
    CHAR_U= 'U'
    CHAR_V= 'V'
    CHAR_W= 'W'
    CHAR_X= 'X'
    CHAR_Y= 'Y'
    CHAR_= 'Z'
    NUM_0= '0'
    NUM_1= '1'
    NUM_2= '2'
    NUM_3= '3'
    NUM_4= '4'
    NUM_5= '5'
    NUM_6= '6'
    NUM_7= '7'
    NUM_8= '8'
    NUM_9= '9'


class COLOR:
    BLACK=      [0, 0, 0]
    WHITE=      [255, 255, 255]
    BLUE=       [0, 0, 255]
    YELLOW=     [255, 255, 0]
    RED=        [255, 0, 0]
    VIOLET=     [181, 126, 220]
    ORANGE=     [255, 165, 0]
    GREEN=      [0, 128, 0]
    GRAY=       [128, 128, 128]

    IVORY=      [255, 255, 240]
    BEIGE=      [245, 245, 220]
    WHEAT=      [245, 222, 179]
    TAN=        [210, 180, 140]
    KHAKI=      [195, 176, 145]
    SILVER=     [192, 192, 192]
    CHARCOAL=   [70, 70, 70]
    NAVYBLUE=   [0, 0, 128]
    ROYALBLUE=  [8, 76, 158]
    MEDIUMBLUE= [0, 0, 205]
    AZURE=      [0, 127, 255]
    CYAN=       [0, 255, 255]
    AQUAMARINE= [127, 255, 212]
    TEAL=       [0, 128, 128]
    FORESTGREEN= [34, 139, 34]
    OLIVE=      [128, 128, 0]
    LIME=       [191, 255, 0]
    GOLD=       [255, 215, 0]
    SALMON=     [250, 128, 114]
    HOTPINK=    [252, 15, 192]
    FUCHSIA=    [255, 119, 255]
    PUCE=       [204, 136, 153]
    PLUM=       [132, 49, 121]
    INDIGO=     [75, 0, 130]
    MAROON=     [128, 0, 0]
    CRIMSON=    [220, 20, 60]
    DEFAULT=    [0, 0, 0]

class NOTE:
    B0=     0
    C1=     1
    CS1=    2
    D1=     3
    DS1=    4
    E1=     5
    F1=     6
    FS1=    7
    G1=     8
    GS1=    9
    A1=     10
    AS1=    11
    B1=     12
    C2=     13
    CS2=    14
    D2=     15
    DS2=    16
    E2=     17
    F2=     18
    FS2=    19
    G2=     20
    GS2=    21
    A2=     22
    AS2=    23
    B2=     24
    C3=     25
    CS3=    26
    D3=     27
    DS3=    28
    E3=     29
    F3=     30
    FS3=    31
    G3=     32
    GS3=    33
    A3=     34
    AS3=    35
    B3=     36
    C4=     37
    CS4=    38
    D4=     39
    DS4=    40
    E4=     41
    F4=     42
    FS4=    43
    G4=     44
    GS4=    45
    A4=     46
    AS4=    47
    B4=     48
    C5=     49
    CS5=    50
    D5=     51
    DS5=    52
    F5=     53
    FS5=    54
    G5=     55
    GS5=    56
    A5=     57
    AS5=    58
    B5=     59
    C6=     60
    CS6=    61
    D6=     62
    DS6=    63
    E6=     64
    F6=     65
    G6=     66
    GS6=    67
    A6=     68
    AS6=    69
    B6=     70
    C7=     71
    CS7=    72
    D7=     73
    DS7=    74
    E7=     75
    F7=     76
    FS7=    77
    G7=     78
    GS7=    79
    A7=     80
    AS7=    81
    B7=     82
    C8=     83
    CS8=    84
    DS8=    85


class ACTION_CODE:
    NOTHING=        0x00
    RESET_BOARD=    0xc0
    MATRIX_LED=     0xc1
    BUTTON=         0xc2
    BUZZER=         0xc3
    MPU_ACTION=     0xc4
    DIGITAL=        0xc5
    ANALOG=         0xc6
    ULTRASONIC=     0xc7
    SERVO=          0xc8
    TOUCH=          0xc9
    DCMOTOR=        0xca
    TMPHUM=         0xcb
    LIGHT_SENSOR=   0xcc
    MIC_SENSOR=     0xcd
    RCCAR=          0xce
    MAIN_SERVO=     0xd0
    BOARD_SET=      0xd1 
    TCS34725=       0xd2
    OLED=           0xd3
    COLORLED=       0xd4
    JOYSTIC=        0xd5
    # BOARD_RESET= 0xaa
    ACT_OK=         0xfe
    ERROR=          0xff


class ACTION_MODE: 
    COLORLED_ON=      0x01
    COLORLED_OFF=     0x02
    COLORLED_BRIGHT=  0x03

    JOYSTIC_READ=     0x01

    OLED_CLEAR=      0x01
    OLED_TEXT_XY=    0x02
    OLED_IMAGE=      0x03
    OLED_SHAPE=      0x04

    DISPLAY_NUM=        0x01
    DISPLAY_CHAR=       0x02
    DISPLAY_SYMBOL=     0x03
    DISPLAY_COLOR=      0x04
    DISPLAY_BRIGHT=     0x05
    DISPLAY_XY=         0x06
    DISPLAY_EFFECT=     0x07
    DISPLAY_ROW=        0x08

    BUZZER_BEEP=        0x01
    BUZZER_MELODY=      0x02
    BUZZER_NOTE=        0x03

    TOUCH_INIT=         0x01
    TOUCH_VALUES=       0x02

    DIGITAL_OUTPUT=     0x01
    DIGITAL_INPUT=      0x02
    DIGITAL_PULLUP=     0x03

    ANALOG_OUTPUT=      0x01
    ANALOG_INPUT=       0x02

    RCCAR_FORWARD=      0x01
    RCCAR_BACKWARD=     0x02
    RCCAR_RLSPEED=      0x03
    RCCAR_STOP=         0X04
    RCCAR_DISTANCE=     0x05
    RCCAR_LINESENSOR=   0x06
    RCCAR_INITIALIZE=   0x10

# 파이썬 라이브러리는 HEADER를 0x77로 설정한다. 0.4버전 부터 
NULL_COMMAND_PACKET = [0xff,0x77,0x11,0x00,0x00,
                       0x00,0x00,0x00,0x00,0x00,
                       0x00,0x00,0x00,0x00,0x00,
                       0x00,0x00,0x00,0x00,0x5a]
LENGTH_OF_PACKET = 20

class BBPACKET:
    START= 0
    HEADER= 1
    LENGTH= 2
    INDEX= 3
    ACTION= 4
    DATA0= 5
    DATA1= 6
    DATA2= 7
    DATA3= 8
    DATA4= 9
    DATA5= 10
    DATA6= 11
    DATA7= 12
    DATA8= 13
    DATA9= 14
    DATA10= 15
    DATA11= 16
    DATA12= 17
    DATA13= 18
    END=    19


class BBRETURN:
    HEADER_1= 0
    HEADER_2= 1
    LENGTH= 2
    INDEX= 3
    ACTION= 4
    DATA1= 5
    DATA2= 6
    DATA3= 7
    DATA4= 8
    DATA5= 9
    DATA6= 10
    DATA7= 11
    DATA8= 12
    DATA9= 13
    DATA10= 14
    DATA11= 15
    DATA12= 16
    DATA13= 17 # ACTION
    DATA14= 18 # 10
    END=    19    # 13

class BLEUUID:
    SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
    CHARACTERISTIC_UUID_RX = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
    CHARACTERISTIC_UUID_TX = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class ERROR:
    WRONG_PACKET_INDEX = "🔥 리턴 패킷의 인덱스가 옳지않습니다."



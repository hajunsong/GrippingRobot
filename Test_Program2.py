import serial
import PythonLibMightyZap
import threading
import time
import dynamixel_sdk
from pynput.keyboard import Key, Listener
import Tkinter
'''
Global variable
'''
g_Cmd = 0
IRR_Grip_pos = 100
IRR_Release_pos = 0


# variable to share With thread

#lock = threading.rock()
class GripingRobot(threading.Thread):
    g_Trgt_Pos_IRR1_1 = 0
    g_Trgt_Pos_IRR1_2 = 0
    g_Crrt_Pos_IRR1_1 = 0
    g_Crrt_Pos_IRR1_2 = 0
    g_bfr_Pos_IRR1_1 = 0
    g_bfr_Pos_IRR1_2 = 0
    g_flgComm_IRR = False
    g_flgGrip_IRR = False
    g_flgRls_IRR = False
    g_flgForce_IRR = False
    g_flgGripCnt = 0
    g_Crrt_State_IRR1 = 0
    g_flgComm_Move_IRR = False
    g_cnt = 0


    # Control table address
    ADDR_PRO_TORQUE_ENABLE = 562            # Control table address is different in Dynamixel model
    ADDR_PRO_GOAL_POSITION = 596
    ADDR_PRO_PRESENT_POSITION = 611
    g_flgComm_DXL = False
    g_flgMove_DXL = False
    g_flgServo_DXL = False
    g_flgForce_DXL = False
    # Protocol version
    PROTOCOL_VERSION = 2.0                  # See which protocol version is used in the Dynamixel
    # Default setting
    DXL_ID_Axis1 = 1                        # Dynamixel ID : 1
    DXL_ID_Axis2 = 2                        # Dynamixel ID : 1
    BAUDRATE = 57600                        # Dynamixel default baudrate : 57600
    DEVICENAME = '/dev/ttyUSB0'                     # Check which port is being used on your controller
                                            # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

    TORQUE_ENABLE = 1                       # Value for enabling the torque
    TORQUE_DISABLE = 0                      # Value for disabling the torque
    DXL_MINIMUM_POSITION_VALUE = 10         # Dynamixel will rotate between this value
    DXL_MAXIMUM_POSITION_VALUE = 4000       # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
    Axis1_TarPos = int(0)
    Axis2_TarPos = int(0)
    Axis1_CurPos = int(0)
    Axis2_CurPos = int(0)
    DXL_MOVING_STATUS_THRESHOLD = 20        # Dynamixel moving status threshold

    portHandler = dynamixel_sdk.PortHandler(DEVICENAME)
    packetHandler = dynamixel_sdk.PacketHandler(PROTOCOL_VERSION)

    #win = Tkinter.Tk()
    #frm = Tkinter.Frame(win, width=100, height=1000)
    #frm.pack()
    #varText1 = Tkinter.StringVar()
    #varText2 = Tkinter.StringVar()
    #varText1.set('hello')
    #varText2.set('hello')

    #TWindow1 = Tkinter.Label(win, textvariable=varText1)
    #TWindow1.pack()
    #TWindow2 = Tkinter.Label(win, textvariable=varText2)
    #TWindow2.pack()

    Tick = 10
    """
    Griper Function
    """
    #def PortOpenGriper(self):
    #    # Port open
    #    try:
    #        # !!KSH!![001]
    #        rst = PythonLibMightyZap.OpenMightyZap("COM7", 57600)
    #    # Error handling : serial open
    #    except serial.serialutil.SerialException:
    #        print("IRR Device RS485 - Connection Fail")
    #        self.g_flgComm_IRR = False
    #    # OK
    #    else:
    #        print("Connection")
    #        self.g_flgComm_IRR = True

    def moveGriper(self):
        if self.g_flgComm_DXL:
            self.g_flgComm_Move_IRR = True
            # Grip
            if self.g_Crrt_Pos_IRR1_1 < self.g_Trgt_Pos_IRR1_1 and self.g_Crrt_Pos_IRR1_2 < self.g_Trgt_Pos_IRR1_2:
                self.g_flgForce_IRR = True
                self.g_flgGripCnt = 0
            # Realese
            else:
                self.g_flgForce_IRR = False
                self.g_flgGripCnt = 0

    #def PortCloseGriper(self):
    #    if self.g_flgComm_IRR:
    #        PythonLibMightyZap.CloseMightyZap()
    """
    Robot Function
    """
    # Open Port
    def PortOpenDXL(self):
        if self.portHandler.openPort():
            print("Succeeded to Open the Port")
            self.g_flgComm_DXL = True
        else:
            print("Failed to Open the Port")
            self.g_flgComm_DXL = False

        # Set port baudrate
        if self.portHandler.setBaudRate(self.BAUDRATE) and self.g_flgComm_DXL:
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            self.g_flgComm_DXL = False

    # Close Port
    def PortCloseDXL(self):
        if self.g_flgComm_DXL:
            self.portHandler.closePort()

    def ErrorPrint(self, comm_result, error, AxisID):
        if comm_result != dynamixel_sdk.COMM_SUCCESS:
            print("AsisID ", AxisID, ": %s" % self.packetHandler.getTxRxResult(comm_result))
            return False
        elif error != 0:
            print("AsisID ", AxisID, ": %s" % self.packetHandler.getRxPacketError(error))
            return False
        else:
            return True

    def DXL_TrqEnable(self):
        if self.g_flgComm_DXL:
            self.g_flgServo_DXL = True
            self.g_flgForce_DXL = True


    def DXL_TrqDisable(self):
        if self.g_flgComm_DXL:
            self.g_flgServo_DXL = True
            self.g_flgForce_DXL = False

    def run(self):
        # init
        # print("Start")
        # self.stime = time.time()
        self.g_flgComm_Move_IRR= False
        # initial
        if self.g_flgComm_DXL:
            self.g_Crrt_Pos_IRR1_1 = PythonLibMightyZap.presentPosition(self.portHandler,0)
            self.g_Crrt_Pos_IRR1_2 = PythonLibMightyZap.presentPosition(self.portHandler,4)
            self.g_Trgt_Pos_IRR1_1 = self.g_Crrt_Pos_IRR1_1
            self.g_Trgt_Pos_IRR1_2 = self.g_Crrt_Pos_IRR1_2

        # print(g_Crrt_Pos_IRR1_1,g_Crrt_Pos_IRR1_2)41
        if self.g_flgComm_DXL:
            tmp, dxl_comm_result, dxl_error \
                = self.packetHandler.read4ByteTxRx(self.portHandler,
                                                   self.DXL_ID_Axis1,
                                                   self.ADDR_PRO_PRESENT_POSITION)
            if tmp & 0x80000000:
                tmp = -(((~tmp)&0xffffffff) + 1)
            self.Axis1_CurPos = tmp
            tmp, dxl_comm_result, dxl_error \
                = self.packetHandler.read4ByteTxRx(self.portHandler,
                                                   self.DXL_ID_Axis2,
                                                   self.ADDR_PRO_PRESENT_POSITION)
            if tmp & 0x80000000:
                tmp = -(((~tmp)&0xffffffff) + 1)
            self.Axis2_CurPos = tmp
            self.Axis1_TarPos = self.Axis1_CurPos
            self.Axis2_TarPos = self.Axis2_CurPos
        time.sleep(0.2)
        while True:
            # Update : position
            if self.g_flgComm_DXL:
                tmp, dxl_comm_result, dxl_error \
                    = self.packetHandler.read4ByteTxRx(self.portHandler,
                                                       self.DXL_ID_Axis1,
                                                       self.ADDR_PRO_PRESENT_POSITION)
                if tmp & 0x80000000:
                    tmp = -(((~tmp)&0xffffffff) + 1)
                self.Axis1_CurPos = tmp
                tmp, dxl_comm_result, dxl_error \
                    = self.packetHandler.read4ByteTxRx(self.portHandler,
                                                       self.DXL_ID_Axis2,
                                                       self.ADDR_PRO_PRESENT_POSITION)
                if tmp & 0x80000000:
                    tmp = -(((~tmp) & 0xffffffff) + 1)
                self.Axis2_CurPos = tmp
                # Excution command : Move
                if self.g_flgMove_DXL:
                    dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler,
                                                                                   self.DXL_ID_Axis1,
                                                                                   self.ADDR_PRO_GOAL_POSITION,
                                                                                   self.Axis1_TarPos)
                    dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler,
                                                                                   self.DXL_ID_Axis2,
                                                                                   self.ADDR_PRO_GOAL_POSITION,
                                                                                   self.Axis2_TarPos)
                    self.g_flgMove_DXL = False
                # Excution command : Survo On/Off
                if self.g_flgServo_DXL:
                    self.g_flgServo_DXL = 0
                    if self.g_flgForce_DXL:
                        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler,
                                                                                       self.DXL_ID_Axis1,
                                                                                       self.ADDR_PRO_TORQUE_ENABLE,
                                                                                       self.TORQUE_ENABLE)
                        if self.ErrorPrint(dxl_comm_result, dxl_error, self.DXL_ID_Axis1):
                            print("Axis1 : Torque [On]")

                        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler,
                                                                                       self.DXL_ID_Axis2,
                                                                                       self.ADDR_PRO_TORQUE_ENABLE,
                                                                                       self.TORQUE_ENABLE)
                        if self.ErrorPrint(dxl_comm_result, dxl_error, self.DXL_ID_Axis2):
                            print("Axis2 : Torque [On]")
                    else:
                        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler,
                                                                                       self.DXL_ID_Axis1,
                                                                                       self.ADDR_PRO_TORQUE_ENABLE,
                                                                                       self.TORQUE_DISABLE)
                        if self.ErrorPrint(dxl_comm_result, dxl_error, self.DXL_ID_Axis1):
                            print("Axis1 : Torque [Off]")

                        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler,
                                                                                       self.DXL_ID_Axis2,
                                                                                       self.ADDR_PRO_TORQUE_ENABLE,
                                                                                       self.TORQUE_DISABLE)
                        if self.ErrorPrint(dxl_comm_result, dxl_error, self.DXL_ID_Axis1):
                            print("Axis2 : Torque [Off]")
            if self.g_flgComm_DXL:
                # === Get Position
                self.g_Crrt_Pos_IRR1_1 = PythonLibMightyZap.presentPosition(self.portHandler, 0)
                self.g_Crrt_Pos_IRR1_2 = PythonLibMightyZap.presentPosition(self.portHandler, 4)
                # self.stime = time.time()
                # === Get State
                # None
                # === Get Error
                # None
                # === Excute Command ===
                # 1. Move position
                if self.g_flgComm_Move_IRR:
                    PythonLibMightyZap.goalPosition(self.portHandler, 0, self.g_Trgt_Pos_IRR1_1)
                    PythonLibMightyZap.goalPosition(self.portHandler, 4, self.g_Trgt_Pos_IRR1_2)
                    self.g_flgComm_Move_IRR = False
                # 2. Grip_End
                elif self.g_flgForce_IRR:
                    if self.g_flgGripCnt > 2:
                        if (abs(self.g_Crrt_Pos_IRR1_1 - self.g_bfr_Pos_IRR1_1) < 40 or abs(self.g_Crrt_Pos_IRR1_2 - self.g_bfr_Pos_IRR1_2) < 40):
                            self.g_flgForce_IRR = False
                            PythonLibMightyZap.forceEnable(self.portHandler, 0, 0)
                            PythonLibMightyZap.forceEnable(self.portHandler, 4, 0)
                            self.g_Trgt_Pos_IRR1_1 = self.g_Crrt_Pos_IRR1_1
                            self.g_Trgt_Pos_IRR1_2 = self.g_Crrt_Pos_IRR1_2
                            PythonLibMightyZap.goalPosition(self.portHandler, 0, self.g_Trgt_Pos_IRR1_1)
                            PythonLibMightyZap.goalPosition(self.portHandler, 4, self.g_Trgt_Pos_IRR1_2)
                            self.g_flgGripCnt = 0
                            print("!!F-OFF!! Vel1: [%05d]"%(self.g_Crrt_Pos_IRR1_1 - self.g_bfr_Pos_IRR1_1), "Vel2: [%05d]"%(self.g_Crrt_Pos_IRR1_2 - self.g_bfr_Pos_IRR1_2),"Pos1 : [%05d"%self.g_Crrt_Pos_IRR1_1 ,"/%05d]"%self.g_Trgt_Pos_IRR1_1, "Pos2 : [%05d/"%self.g_Crrt_Pos_IRR1_2, "%05d]"%self.g_Trgt_Pos_IRR1_2)
                    else:
                        self.g_flgGripCnt += 1
                # 3. print
                if abs(self.g_Trgt_Pos_IRR1_1 - self.g_Crrt_Pos_IRR1_1) > 10 and abs(self.g_Trgt_Pos_IRR1_2 - self.g_Crrt_Pos_IRR1_2) > 10:
                    print("Vel1: [%05d]"%(self.g_Crrt_Pos_IRR1_1 - self.g_bfr_Pos_IRR1_1), "Vel2: [%05d]"%(self.g_Crrt_Pos_IRR1_2 - self.g_bfr_Pos_IRR1_2),"Pos1 : [%05d"%self.g_Crrt_Pos_IRR1_1 ,"/%05d]"%self.g_Trgt_Pos_IRR1_1, "Pos2 : [%05d/"%self.g_Crrt_Pos_IRR1_2, "%05d]"%self.g_Trgt_Pos_IRR1_2)

                if self.g_flgGrip_IRR:
                    if self.g_Crrt_Pos_IRR1_1 >= 1400 and self.g_Crrt_Pos_IRR1_2 >= 1400 :
                        PythonLibMightyZap.goalPosition(self.portHandler, 0, 1400)
                        PythonLibMightyZap.goalPosition(self.portHandler, 4, 1400)
                        self.g_flgGrip_IRR = 0
                    elif abs(self.g_Trgt_Pos_IRR1_1 - self.g_Crrt_Pos_IRR1_1) < 50 and abs(self.g_Trgt_Pos_IRR1_2 - self.g_Crrt_Pos_IRR1_2) < 50 :
                        self.g_Trgt_Pos_IRR1_1 = self.g_Crrt_Pos_IRR1_1 + 200
                        self.g_Trgt_Pos_IRR1_2 = self.g_Crrt_Pos_IRR1_2 + 200
                        PythonLibMightyZap.goalPosition(self.portHandler,0, self.g_Trgt_Pos_IRR1_1)
                        PythonLibMightyZap.goalPosition(self.portHandler,4, self.g_Trgt_Pos_IRR1_2)

                self.g_bfr_Pos_IRR1_1 = self.g_Crrt_Pos_IRR1_1
                self.g_bfr_Pos_IRR1_2 = self.g_Crrt_Pos_IRR1_2
                # 2. Force Off Function
        if g_Cmd == 0:
                # if ...

            # Update Time : 10 ms
            self.g_cnt += 1
            time.sleep(0.01)

            # UI Update
            '''
            if(self.Tick == 10):
                self.varText1.set("Pos1 : "+ str((self.Axis1_CurPos)) + "/" +str((self.Axis1_TarPos)))
                self.varText2.set("Pos2 : "+ str((self.Axis2_CurPos)) + "/" +str((self.Axis2_TarPos)))
                self.TWindow1.update()
                self.TWindow2.update()
                self.Tick = 0
            self.Tick += 1
            '''
    def moveDXL(self):
        self.g_flgMove_DXL = True

g_move_cnt = 0
g_move_flg = False
from pynput.keyboard import Listener, Key

def on_press(key):
    global g_Cmd
    global IRR_Grip_pos
    global IRR_Release_pos
    try:
        if key == Key.esc:
            g_Cmd = 6
        else:
            # print key.char
            if(key.char == 'a' or key.char == 'b' or key.char == 'c' or key.char == '1'):
                IRR_Grip_pos = 2700
                g_Cmd = 4
            elif(key.char == '2'):
                IRR_Grip_pos = 1450
                g_Cmd = 4
            elif (key.char == '3'):
                g_Cmd = 14
            elif (key.char == '4'):
                g_Cmd = 2
            elif (key.char == '5'):
                g_Cmd = 3
            else:
                g_Cmd = 0
    except Exception as e:
        print e.message
    return False

if __name__ == '__main__':
    DXL_Origin_Axis_1 = 0
    DXL_Down_Axis_2 = -62978
    DXL_Turn_Axis_1 = 131592
    DXL_Up_Axis_2 = -125432
    DXL_OffSet_Axis1 = 200
    DXL_OffSet_Axis2 = 200
    g_Cmd = 0
    robot = GripingRobot()
    robot.PortOpenDXL()
    #robot.PortOpenGriper()
    robot.start()
    #g_Cmd = 4
    #time.sleep(1)
    print("=== Start Main-loop ===")
    while True:
        if g_Cmd == 0:
            print("==== Command ====")
            print("1. Move")
            print("2. Move")
            print("3. Set-FingerPosition")
            print("4. Set-Robot-Servo")
            print("5. Set-Robot-Position")
            with Listener(on_press=on_press) as listener:
                listener.join()

        print("==== Excution ====")
        if g_Cmd == 1:
            s = input("left-finger : ")
            tmp = int(s)
            if tmp >= 0 and tmp <= 4095:
                robot.g_Trgt_Pos_IRR1_1 = tmp
            s = input("right-finger : ")
            tmp = int(s)
            if tmp >= 0 and tmp <= 4095:
                robot.g_Trgt_Pos_IRR1_2 = tmp
            robot.moveGriper()
            g_Cmd = 0
        elif g_Cmd == 2:
            s = input("Servo On(1)/Off(0) : ")
            tmp = int(s)
            print tmp
            if tmp == 0 or tmp == 40:
                robot.DXL_TrqDisable()
            elif tmp == 1 or tmp == 41:
                robot.DXL_TrqEnable()
            else:
                print ("Wrong-command")
            g_Cmd = 0
        elif g_Cmd == 3:
            s = input("Axis-1 Position : ")
            tmp = int(s)
            if robot.Axis2_CurPos > -62640 and robot.Axis2_CurPos < -62680:
                print("Axis-2 Position Error")
            elif tmp >= -131592 and tmp <= 0:
                robot.Axis1_TarPos = tmp
            else:
                print("Axis-1 Position input range Error")

            s = input("Axis-2 Position : ")
            tmp = int(s)
            if robot.Axis1_CurPos > 20 and robot.Axis1_CurPos < -20:
                print("Axis-1 Position Error")
            elif tmp >= -62662 and tmp <= -528:
                robot.Axis2_TarPos = tmp
            else:
                print("Axis-2 Position input range Error")
            robot.moveDXL()
            g_Cmd = 0
        elif g_Cmd == 4:
            if g_move_flg:
                print(">> Wait ")
                if abs(robot.Axis1_CurPos - robot.Axis1_TarPos) < DXL_OffSet_Axis1 and abs(robot.Axis2_CurPos - robot.Axis2_TarPos) < DXL_OffSet_Axis2 :
                    if abs(robot.g_Trgt_Pos_IRR1_1 - robot.g_Crrt_Pos_IRR1_1) < 100 and abs(robot.g_Trgt_Pos_IRR1_2 - robot.g_Crrt_Pos_IRR1_2) < 100:
                        if robot.g_flgForce_IRR == False:
                             g_move_flg = False
                else:
                    print("R Pos Error :",robot.Axis1_CurPos - robot.Axis1_TarPos,robot.Axis2_CurPos - robot.Axis2_TarPos , "Mode:",g_move_cnt)
                    #else:
                    #    griper1.move()
            elif g_move_cnt == 0: # Set Position
                print(">> Set Robot Position ")
                robot.Axis1_TarPos = robot.Axis1_CurPos
                robot.Axis2_TarPos = DXL_Up_Axis_2
                robot.moveDXL()
                DXL_OffSet_Axis1 = 10000
                DXL_OffSet_Axis2 = 10000
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 1: #
                print(">> Move Griper : <<==>> ")
                robot.g_Trgt_Pos_IRR1_1 = IRR_Release_pos
                robot.g_Trgt_Pos_IRR1_2 = IRR_Release_pos
                robot.moveGriper()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 2:  #
                print(">> Set Robot Position : to Bottom")
                robot.Axis1_TarPos = DXL_Origin_Axis_1
                robot.Axis2_TarPos = DXL_Up_Axis_2
                DXL_OffSet_Axis1 = 10000
                DXL_OffSet_Axis2 = 10000
                robot.moveDXL()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 3:  #
                print(">> Set Wait")
                robot.Axis1_TarPos = DXL_Origin_Axis_1
                robot.Axis2_TarPos = DXL_Down_Axis_2
                DXL_OffSet_Axis1 = 20000
                DXL_OffSet_Axis2 = 20000
                robot.moveDXL()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 4:
                print(">> Move Griper : >>==<< ")
                robot.g_Trgt_Pos_IRR1_1 = IRR_Grip_pos
                robot.g_Trgt_Pos_IRR1_2 = IRR_Grip_pos
                robot.moveGriper()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 5:
                print(">> Set Robot Position : to Top")
                robot.Axis1_TarPos = DXL_Origin_Axis_1
                robot.Axis2_TarPos = DXL_Up_Axis_2
                DXL_OffSet_Axis1 = 20000
                DXL_OffSet_Axis2 = 20000
                robot.moveDXL()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 6:
                print(">> Set Robot Position : to left")
                robot.Axis1_TarPos = DXL_Turn_Axis_1
                robot.Axis2_TarPos = DXL_Up_Axis_2
                DXL_OffSet_Axis1 = 20000
                DXL_OffSet_Axis2 = 20000
                robot.moveDXL()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 7:
                print(">> Set Robot Position : to Down")
                robot.Axis1_TarPos = DXL_Turn_Axis_1
                robot.Axis2_TarPos = DXL_Down_Axis_2
                DXL_OffSet_Axis1 = 20000
                DXL_OffSet_Axis2 = 20000
                robot.moveDXL()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 8:
                print(">> Move Griper : <<==>> ")
                robot.g_Trgt_Pos_IRR1_1 = IRR_Release_pos
                robot.g_Trgt_Pos_IRR1_2 = IRR_Release_pos
                robot.moveGriper()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 9:
                print(">> Set Robot Position : to Down")
                robot.Axis1_TarPos = DXL_Turn_Axis_1
                robot.Axis2_TarPos = DXL_Up_Axis_2
                DXL_OffSet_Axis1 = 20000
                DXL_OffSet_Axis2 = 20000
                robot.moveDXL()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 10:
                print(">> Set Robot Position : to Down")
                robot.Axis1_TarPos = DXL_Origin_Axis_1
                robot.Axis2_TarPos = DXL_Up_Axis_2
                DXL_OffSet_Axis1 = 20000
                DXL_OffSet_Axis2 = 20000
                robot.moveDXL()
                g_move_cnt += 1
                g_move_flg = True
            elif g_move_cnt == 11:
                DXL_OffSet_Axis1 = 500
                DXL_OffSet_Axis2 = 500
                g_move_cnt = 0
                g_Cmd = 0
                g_move_flg = False
        elif g_Cmd == 5:
            robot.g_flgGrip_IRR = True
            g_Cmd = 0
        elif g_Cmd == 6:
            break
        if (g_Cmd == 0 and g_move_cnt == 0):
            print("Pos", robot.g_Crrt_Pos_IRR1_1, robot.g_Crrt_Pos_IRR1_2,"cnt",robot.g_cnt)
            print("==== Result ====")
            time.sleep(0.1)
        else:
            time.sleep(0.1)

    print 'Good bye!!'







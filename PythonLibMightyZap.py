import serial
from dynamixel_sdk.port_handler import *

PROTOCOL_TX_BUF_SIZE = 50
PROTOCOL_RX_BUF_SIZE = 50
MIGHTYZAP_PING = 0xf1
MIGHTYZAP_READ_DATA = 0xf2
MIGHTYZAP_WRITE_DATA = 0xf3
MIGHTYZAP_REG_WRITE = 0xf4
MIGHTYZAP_ACTION = 0xf5
MIGHTYZAP_RESET = 0xf6
MIGHTYZAP_RESTART = 0xf8
MIGHTYZAP_FACTORY_RESET = 0xf9
MIGHTYZAP_SYNC_WRITE = 0x73

TxBuffer = [0] * PROTOCOL_TX_BUF_SIZE
TxBuffer_index = 0
RxBuffer = [0] * PROTOCOL_RX_BUF_SIZE
RxBuffer_size = 0

ErollService = 0
ErollService_Instruction = 0
ErollService_ID = 0x00
ErollService_Addr = 0x00
ErollService_Size = 0x00
ErollService_ModelNum = 0x0000
ActuatorID = 0
checksum = 0
MZap = serial.Serial()


def SetProtocalHeader():
    global TxBuffer_index
    global TxBuffer
    TxBuffer_index = 0
    TxBuffer[TxBuffer_index] = 0xff
    TxBuffer_index += 1
    TxBuffer[TxBuffer_index] = 0xff
    TxBuffer_index += 1
    TxBuffer[TxBuffer_index] = 0xff
    TxBuffer_index += 1
    TxBuffer[TxBuffer_index] = ActuatorID
    TxBuffer_index += 1


def SetProtocolInstruction(ins):
    global TxBuffer_index
    global TxBuffer
    global ErollService_Instruction

    TxBuffer_index = 5
    ErollService_Instruction = ins
    TxBuffer[TxBuffer_index] = ins
    TxBuffer_index += 1


def AddProtocolFactor(para):
    global TxBuffer_index
    global TxBuffer
    TxBuffer[TxBuffer_index] = para
    TxBuffer_index += 1


def SetProtocollength_checksum():
    global TxBuffer_index
    global TxBuffer
    global checksum
    checksum = 0
    start_i = 0

    TxBuffer[4] = TxBuffer_index - 4
    start_i = 3

    for i in range(start_i, TxBuffer_index):
        checksum += TxBuffer[i]
    TxBuffer[TxBuffer_index] = (checksum & 0x000000ff) ^ 0x000000ff
    TxBuffer_index += 1


def getID():
    global ActuatorID
    return ActuatorID;


def setID(ID):
    global ActuatorID
    ActuatorID = ID


def MightyZap(ID):
    global ErollService
    global ErollService_Instruction
    global ErollService_ID
    global ErollService_Addr
    global ErollService_Size
    global ErollService_Size

    ErollService = 0
    ErollService_Instruction = 0
    ErollService_ID = 0x00
    ErollService_Addr = 0x00
    ErollService_Size = 0x00
    ErollService_ModelNum = 0x0000

    setID(ID)


def OpenMightyZap(portname, BaudRate):
    MZap.port = portname
    MZap.baudrate = BaudRate
    MZap.timeout = 100

    MZap.open()


def CloseMightyZap():
    MZap.close()


def SendPacket(port):
    global TxBuffer_index
    global TxBuffer
    port.clearPort()
    port.writePort(TxBuffer[0:TxBuffer_index])
    # for i in range(0,TxBuffer_index):
    #    port.writePort(TxBuffer[i]])
    # print("Tx" , TxBuffer[0:TxBuffer_index])


def ReceivePacket(port, ID, size):
    global TxBuffer_index
    global TxBuffer
    global RxBuffer
    rxpacket = []
    timeout = 0
    temp = 0
    i = 0
    head_count = 0
    Time = port.getCurrentTime()
    nTime = port.getCurrentTime()
    while len(rxpacket) < 3:
        rxpacket.extend(port.readPort(1))
        # print(3)
        if len(rxpacket) > 0:
            if rxpacket[len(rxpacket) - 1] == b'\xff':
                RxBuffer[head_count] = 0xff
                head_count += 1
            else:
                RxBuffer[0] = 0
                head_count = 0
                temp += 1
        nTime = port.getCurrentTime() - Time
        if nTime > 100:
            print("Time-out", rxpacket, ID, nTime)
            return -1
    for i in range(3, size):
        rxpacket.extend(port.readPort(1))
        if (i + 1) == len(rxpacket):
            RxBuffer[i] = rxpacket[i]
        else:
            i = len(rxpacket) - 1
    # print("Rx", rxpacket)
    return 0


def read_data(port, ID, addr, size):
    global MIGHTYZAP_READ_DATA

    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_READ_DATA)
    AddProtocolFactor(addr)
    AddProtocolFactor(size)
    SetProtocollength_checksum()
    SendPacket(port)


def ead_data_model_num(port, ID):
    global MIGHTYZAP_READ_DATA
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_READ_DATA)
    AddProtocolFactor(0);
    ErollService_Addr = 0
    AddProtocolFactor(2);
    ErollService_Size = 2
    SetProtocollength_checksum()
    SendPacket(port)


def write_data(port, ID, addr, data, size):
    global MIGHTYZAP_WRITE_DATA
    i = 0
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_WRITE_DATA)
    AddProtocolFactor(addr)
    for i in range(0, size):
        AddProtocolFactor(data[i])
    SetProtocollength_checksum()
    SendPacket(port)


def reg_write(port, ID, addr, data, size):
    global MIGHTYZAP_WRITE_DATA
    i = 0
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_REG_WRITE)
    AddProtocolFactor(addr)
    for i in range(0, size):
        AddProtocolFactor(data[i])
    SetProtocollength_checksum()
    SendPacket(port)


def reg_write(port, addr, data, size):
    reg_write(port, ActuatorID, addr, data, size)


def action(port, ID):
    global MIGHTYZAP_WRITE_DATA
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_ACTION)
    SetProtocollength_checksum()
    SendPacket(port)


def action(port):
    global ActuatorID
    action(port, ActuatorID)


def reset_write(port, ID, option):
    global MIGHTYZAP_RESET
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_RESET)
    AddProtocolFactor(option)
    SetProtocollength_checksum()
    SendPacket(port)


def reset_write(port, option):
    global ActuatorID
    reset_write(port, ActuatorID, option)


def Restart(port, ID):
    global MIGHTYZAP_RESTART
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_RESTART)
    SetProtocollength_checksum()
    SendPacket(port)


def Restart(port):
    global ActuatorID
    Restart(port, ActuatorID)


def factory_reset_write(port, ID, option):
    global MIGHTYZAP_FACTORY_RESET
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_FACTORY_RESET)
    AddProtocolFactor(option)
    SetProtocollength_checksum()
    SendPacket(port)


def factory_reset_write(port, option):
    global ActuatorID
    factory_reset_write(port, ActuatorID, option)


def ping(port, ID):
    global MIGHTYZAP_PING
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_PING)
    SetProtocollength_checksum()
    SendPacket(port)


def goalPosition(port, bID, position):
    pByte = [0] * 2
    pByte[0] = (position & 0x00ff)
    pByte[1] = (position >> 8)
    write_data(port, bID, 0x86, pByte, 2)


def presentPosition(port, bID):
    global RxBuffer
    if port.is_using:
        return -1
    port.is_using = True
    read_data(port, bID, 0x8C, 2)
    rst = ReceivePacket(port, bID, 9)
    if rst == -1:
        # print("time-out" , bID)
        port.is_using = False
        return 0
    port.is_using = False
    return (RxBuffer[7] * 256) + (RxBuffer[6])


def movingSpeed(port, bID, speed):
    pByte = [0] * 2

    pByte[0] = (byte)(speed & 0x00ff)
    pByte[1] = (byte)(speed >> 8)
    write_data(port, bID, 0x88, pByte, 2)


def forceEnable(port, bID, enable):
    pByte = [0] * 2

    if enable == 1:
        pByte[0] = 1
    else:
        pByte[0] = 0

    write_data(port, bID, 0x80, pByte, 1)
    SendPacket(port)


def SetErrorShutDownEnable(port, bID, flag):
    pByte = [0] * 1
    pByte[0] = flag
    write_data(port, bID, 0x12, pByte, 1)


def GetErrorShutDownEnable(port, bID):
    read_data(port, bID, 0x12, 1)
    ReceivePacket(port, bID, 8)
    return RxBuffer[6]


def SetErrorIndicatorEnable(port, bID, flag):
    pByte = [0] * 1
    pByte[0] = flag
    write_data(port, bID, 0x11, pByte, 1)


def GetErrorIndicatorEnable(port, bID):
    read_data(port, bID, 0x11, 1)
    ReceivePacket(port, bID, 8)
    return RxBuffer[6]


def ReadError(port, bID):
    ping(port, bID)
    ReceivePacket(port, bID, 7)
    return RxBuffer[5]


def write_Addr(port, bID, addr, size, data):
    if size == 2:
        pByte = [0] * 2
        pByte[0] = (data & 0x00ff)
        pByte[1] = (data // 256)
        write_data(port, bID, addr, pByte, 2)
    else:
        pByte = [0] * 1
        pByte[0] = data
        write_data(port, bID, addr, pByte, 1)


def read_Addr(port, bID, addr, size):
    if size == 2:
        read_data(port, bID, addr, 2)
        ReceivePacket(port, bID, 9)
        return (RxBuffer[7] * 256) + RxBuffer[6]
    else:
        read_data(port, bID, addr, 1)
        ReceivePacket(port, bID, 8)
        return RxBuffer[6]
import os
import time
import grpc
import cyberdog_app_pb2
import cyberdog_app_pb2_grpc
import keyboard
import functools

grpc_timeout = 1 # grpc connection timeout 10
MAX_SPEED = 16 # maximum speed: 16 (In the following code, it is divided by 10)
speed_lv = 1 # Default speed: 1 (In the following code, it is divided by 10)
gait_str = "trot" # Default gait: trot
motion_str = "None" # Default motion: None
stubs = []
channels = []

# read by file "ip.txt"
# cyberdog_ips = ["192.168.1.1", "192.168.1.2"]
try:
    with open("ip.txt", "r") as f:
        cyberdog_ips = [line.rstrip() for line in f]
except FileNotFoundError:
    cyberdog_ips = []

class Vector3:
    x: float = 0
    y: float = 0
    z: float = 0

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        pass

linear = Vector3(0, 0, 0)
angular = Vector3(0, 0, 0)

def OpenGrpc():
    # Open grpc channel 
    global cyberdog_ips, stubs, channels
    
    if not cyberdog_ips:
        cyberdog_ips = input("Cyberdog IPs (separated by \',\'): ")
        cyberdog_ips = cyberdog_ips.split(',')

    for cyberdog_ip in cyberdog_ips:
        print(cyberdog_ip)
        channel = grpc.insecure_channel(str(cyberdog_ip) + ':50051')
        print(f"Waiting connect for {cyberdog_ip}")
        try:
            grpc.channel_ready_future(channel).result(timeout=grpc_timeout)
        except grpc.FutureTimeoutError:
            print(f"Connect error for {cyberdog_ip}, Timeout={grpc_timeout}")
            continue
        channels.append(channel)
        # Get stub from channel
        stub = cyberdog_app_pb2_grpc.CyberdogAppStub(channel)
        print(f"Connect success for {cyberdog_ip}")
        stubs.append(stub)

def StandUp(stub):
    global stubs,cyberdog_ips
    # Stand up
    response = stub.setMode(
        cyberdog_app_pb2.CheckoutMode_request(
            next_mode=cyberdog_app_pb2.ModeStamped(
                header=cyberdog_app_pb2.Header(
                    stamp=cyberdog_app_pb2.Timestamp(
                        sec=0,      # seem not need
                        nanosec=0   # seem not need
                    ),
                    frame_id=""     # seem not need
                ),
                mode=cyberdog_app_pb2.Mode(
                    control_mode=cyberdog_app_pb2.CheckoutMode_request.MANUAL,
                    mode_type=0     # seem not need
                )),
            timeout=10))
    succeed_state = False
    for resp in response:
        succeed_state = resp.succeed
        print(f"Execute Stand up for {cyberdog_ips[stubs.index(stub)]} , result:" + str(succeed_state))
        return succeed_state

def SitDown(stub):
    global cyberdog_ips, stubs
    # Get down
    response = stub.setMode(
        cyberdog_app_pb2.CheckoutMode_request(
            next_mode=cyberdog_app_pb2.ModeStamped(
                header=cyberdog_app_pb2.Header(
                    stamp=cyberdog_app_pb2.Timestamp(
                        sec=0,      # seem not need
                        nanosec=0   # seem not need
                    ),
                    frame_id=""     # seem not need
                ),
                mode=cyberdog_app_pb2.Mode(
                    control_mode=cyberdog_app_pb2.CheckoutMode_request.DEFAULT,
                    mode_type=0     # seem not need
                )),
            timeout=10))
    succeed_state = False
    for resp in response:
        succeed_state = resp.succeed
        print(f"Execute Sit down for {cyberdog_ips[stubs.index(stub)]} , result:" + str(succeed_state))

def ChangeGait(GAIT_str, Event):
    global stubs,cyberdog_ips,gait_str
    gait_str = GAIT_str
    # Convert GAIT_str to GAIT value
    if GAIT_str == "amble":
        GAIT = cyberdog_app_pb2.Pattern.GAIT_AMBLE
    elif GAIT_str == "walk":
        GAIT = cyberdog_app_pb2.Pattern.GAIT_WALK
    elif GAIT_str == "slow_trot":
        GAIT = cyberdog_app_pb2.Pattern.GAIT_SLOW_TROT
    elif GAIT_str == "trot":
        GAIT = cyberdog_app_pb2.Pattern.GAIT_TROT
    elif GAIT_str == "fly_trot":
        GAIT = cyberdog_app_pb2.Pattern.GAIT_FLYTROT
    elif GAIT_str == "bound":
        GAIT = cyberdog_app_pb2.Pattern.GAIT_BOUND
    elif GAIT_str == "pronk":
        GAIT = cyberdog_app_pb2.Pattern.GAIT_PRONK
    else:
        return
    for stub in stubs:
        # Change gait to walk
        response = stub.setPattern(
            cyberdog_app_pb2.CheckoutPattern_request(
                patternstamped=cyberdog_app_pb2.PatternStamped(
                    header=cyberdog_app_pb2.Header(
                        stamp=cyberdog_app_pb2.Timestamp(
                            sec=0,      # seem not need
                            nanosec=0   # seem not need
                        ),
                        frame_id=""     # seem not need
                    ),
                    pattern=cyberdog_app_pb2.Pattern(
                        gait_pattern=GAIT
                    )
                ),
                timeout=10
            )
        )
        succeed_state = False
        for resp in response:
            succeed_state = resp.succeed
            print(f"Change gait to {GAIT_str} for {cyberdog_ips[stubs.index(stub)]} , result:" + str(succeed_state))
    
def ChangeMotion(MOTION_str, Event):
    global stubs,cyberdog_ips,motion_str
    motion_str = MOTION_str

    # Convert GAIT_str to GAIT value
    if MOTION_str == "stand_up":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_STAND_UP
    elif MOTION_str == "prostrate":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_PROSTRATE
    elif MOTION_str == "come_here":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_COME_HERE
    elif MOTION_str == "step_back":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_STEP_BACK
    elif MOTION_str == "turn_around":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_TURN_AROUND
    elif MOTION_str == "hi_five":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_HI_FIVE
    elif MOTION_str == "dance":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_DANCE
    elif MOTION_str == "welcome":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_WELCOME
    elif MOTION_str == "turn_over":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_TURN_OVER
    elif MOTION_str == "sit":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_SIT
    elif MOTION_str == "bow":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_BOW
    elif MOTION_str == "max":
        MOTION = cyberdog_app_pb2.MonOrder.MONO_ORDER_MAX
    else:
        return
    for stub in stubs:
        # Execute motion order
        response = stub.setExtmonOrder(
            cyberdog_app_pb2.ExtMonOrder_Request(
                order=cyberdog_app_pb2.MonOrder(
                    id=MOTION,
                    para=0      # seem not need
                ),
                timeout=50))
        for resp in response:
            succeed_state = resp.succeed
            print(f"Execute {MOTION_str} order for {cyberdog_ips[stubs.index(stub)]} , result:" + str(succeed_state))
    os.system('cls || clear')
    PrintMotion()

def ChangeOther(OTHER_str, Event):
    global stubs,cyberdog_ips,other_str
    other_str = OTHER_str

    # Convert GAIT_str to GAIT value
    if OTHER_str == "stand_up":
        for stub in stubs:
            stub.setMode(
                cyberdog_app_pb2.CheckoutMode_request(
                    next_mode=cyberdog_app_pb2.ModeStamped(
                        header=cyberdog_app_pb2.Header(
                            stamp=cyberdog_app_pb2.Timestamp(
                                sec=0,      # seem not need
                                nanosec=0   # seem not need
                            ),
                            frame_id=""     # seem not need
                        ),
                        mode=cyberdog_app_pb2.Mode(
                            control_mode=cyberdog_app_pb2.CheckoutMode_request.MANUAL,
                            mode_type=0     # seem not need
                        )),
                    timeout=10))
    elif OTHER_str == "sit_down":
        for stub in stubs:
            stub.setMode(
                cyberdog_app_pb2.CheckoutMode_request(
                    next_mode=cyberdog_app_pb2.ModeStamped(
                        header=cyberdog_app_pb2.Header(
                            stamp=cyberdog_app_pb2.Timestamp(
                                sec=0,      # seem not need
                                nanosec=0   # seem not need
                            ),
                            frame_id=""     # seem not need
                        ),
                        mode=cyberdog_app_pb2.Mode(
                            control_mode=cyberdog_app_pb2.CheckoutMode_request.DEFAULT,
                            mode_type=0     # seem not need
                        )),
                    timeout=10))
    else:
        return

def PrintGait():
    global gait_str
    print("Now speed:%.1fm/s  " % float(speed_lv*0.1) + "Now gait: \'" + gait_str + "\'")
    print("--------------------------")
    print("t: Stand Up")
    print("g: Sit Down")
    print("--------------------------")
    print("W: GoFront")
    print("S: GoBack")
    print("A: GoLeft")
    print("D: GoRight")
    print("Q: TurnLeft")
    print("E: TurnRight")
    print("U: SpeedUp")
    print("I: SpeedDown")
    print("--------------------------")
    print("1: change gait to amble")
    print("2: change gait to walk")
    print("3: change gait to slow_trot")
    print("4: change gait to trot")
    print("5: change gait to fly_trot")
    print("6: change gait to bound")
    print("7: change gait to pronk")
    print("--------------------------")
    print("ESC: Exit Control")

def PrintMotion():
    global motion_str
    print("Now Motion: \'" + motion_str + "\'")
    print("--------------------------")
    print("t: Stand Up")
    print("g: Sit Down")
    print("--------------------------")
    print("1: change motion to stand_up")
    print("2: change motion to prostrate")
    print("3: change motion to come_here")
    print("4: change motion to step_back")
    print("5: change motion to turn_around")
    print("6: change motion to hi_five")
    print("7: change motion to dance")
    print("8: change motion to welcome")
    print("9: change motion to turn_over")
    print("0: change motion to sit")
    print("-: change motion to bow")
    print("+: change motion to max")
    print("--------------------------")
    print("ESC: Exit Control")

def SendData():
    global cyberdog_ips, stubs
    for stub in stubs:
        print(f"SendData for {cyberdog_ips[stubs.index(stub)]}")
        response = stub.sendAppDecision(
            cyberdog_app_pb2.Decissage(
                twist=cyberdog_app_pb2.Twist(
                    linear=cyberdog_app_pb2.Vector3(
                        x=linear.x,
                        y=linear.y,
                        z=linear.z
                    ),
                    angular=cyberdog_app_pb2.Vector3(
                        x=angular.x,
                        y=angular.y,
                        z=angular.z
                    )
                )
            )
        )
        # for resp in response:
        #     succeed_state = resp.succeed
        #     print(f"SendData for {cyberdog_ips[stubs.index(stub)]} , result:" + str(succeed_state))
    os.system('cls || clear')
    PrintGait()

def GoForward(Event):
    linear.x = 0.1 * speed_lv
    linear.y = 0
    angular.z = 0
    print("hello")
    SendData()

def GoBack(Event):
    linear.x = -0.1 * speed_lv
    linear.y = 0
    angular.z = 0
    SendData()

def GoLeft(Event):
    linear.x = 0
    linear.y = 0.1 * speed_lv
    angular.z = 0
    SendData()

def GoRight(Event):
    linear.x = 0
    linear.y = -0.1 * speed_lv
    angular.z = 0
    SendData()

def TurnLeft(Event):
    linear.x = 0
    linear.y = 0
    angular.z = 0.1 * speed_lv
    SendData()

def TurnRight(Event):
    linear.x = 0
    linear.y = 0
    angular.z = -0.1 * speed_lv
    SendData()

def Stop(Event):
    linear.x = 0
    linear.y = 0
    angular.z = 0
    SendData()

def SpeedUp(Event):
    global speed_lv
    speed_lv += 1
    speed_lv = min(speed_lv, MAX_SPEED)

def SpeedDown(Event):
    global speed_lv
    speed_lv -= 1
    speed_lv = max(speed_lv, 1)


# Send Move Cmd to Cyberdog
def RunGaitCMD():
    os.system('cls || clear')
    global cyberdog_ips, stubs
    # for stub in stubs:
    #     StandUp(stub)
        # succeed_state = False
        # succeed_state = StandUp(stub)
        # if (succeed_state == False):
        #     continue
        
    PrintGait()
    keyboard.on_press_key('w', GoForward)
    keyboard.on_press_key('s', GoBack)
    keyboard.on_press_key('a', GoLeft)
    keyboard.on_press_key('d', GoRight)
    keyboard.on_press_key('j', TurnLeft)
    keyboard.on_press_key('l', TurnRight)
    keyboard.on_press_key('i', SpeedUp)
    keyboard.on_press_key('k', SpeedDown)
    keyboard.on_press_key('1', functools.partial(ChangeGait, "amble"))
    keyboard.on_press_key('2', functools.partial(ChangeGait, "walk"))
    keyboard.on_press_key('3', functools.partial(ChangeGait, "slow_trot"))
    keyboard.on_press_key('4', functools.partial(ChangeGait, "trot"))
    keyboard.on_press_key('5', functools.partial(ChangeGait, "fly_trot"))
    keyboard.on_press_key('6', functools.partial(ChangeGait, "bound"))
    keyboard.on_press_key('7', functools.partial(ChangeGait, "pronk"))
    keyboard.on_press_key('t', functools.partial(ChangeOther, "stand_up"))
    keyboard.on_press_key('g', functools.partial(ChangeOther, "sit_down"))
    keyboard.on_release(Stop)
    keyboard.wait('esc')
    
    # for stub in stubs:
    #     SitDown(stub)

    os.system('cls || clear')
    keyboard.unhook_all()

# Send Order Cmd to Cyberdog
def RunMotionCMD():
    os.system('cls || clear')
    global cyberdog_ips, stubs
    # for stub in stubs:
    #     StandUp(stub)
        # succeed_state = False
        # succeed_state = StandUp(stub)
        # if (succeed_state == False):
        #     continue

    PrintMotion()
    keyboard.on_press_key('1', functools.partial(ChangeMotion, "stand_up"))
    keyboard.on_press_key('2', functools.partial(ChangeMotion, "prostrate"))
    keyboard.on_press_key('3', functools.partial(ChangeMotion, "come_here"))
    keyboard.on_press_key('4', functools.partial(ChangeMotion, "step_back"))
    keyboard.on_press_key('5', functools.partial(ChangeMotion, "turn_around"))
    keyboard.on_press_key('6', functools.partial(ChangeMotion, "hi_five"))
    keyboard.on_press_key('7', functools.partial(ChangeMotion, "dance"))
    keyboard.on_press_key('8', functools.partial(ChangeMotion, "welcome"))
    keyboard.on_press_key('9', functools.partial(ChangeMotion, "turn_over"))
    keyboard.on_press_key('0', functools.partial(ChangeMotion, "sit"))
    keyboard.on_press_key('-', functools.partial(ChangeMotion, "bow"))
    keyboard.on_press_key('+', functools.partial(ChangeMotion, "max"))
    keyboard.on_press_key('t', functools.partial(ChangeOther, "stand_up"))
    keyboard.on_press_key('g', functools.partial(ChangeOther, "sit_down"))
    keyboard.wait('esc')

    # # Get down
    # for stub in stubs:
    #     SitDown(stub)

    os.system('cls || clear')
    keyboard.unhook_all()

if __name__ == '__main__':
    OpenGrpc()
    print("Initialization completed, sleeping 1s......")
    time.sleep(1)
    while True:
        os.system('cls || clear')
        print("Choose mode [1: Motion, 2: Gait, q: Exit]:")
        char = keyboard.read_event().name
        if char == '1':
            RunMotionCMD()
        elif char == '2':
            RunGaitCMD()
        elif char == 'q':
            print("Program is exiting.......")
            for channel in channels:
                channel.Close()
            break
        else:
            continue

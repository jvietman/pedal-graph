from inputs import get_gamepad
import threading

class controller(object):
    def __init__(self):
        self.connected = True
        self.debug = False
        
        self.brakeadjust = 2.55
        self.gasadjust = 2.55
        
        self.brakebind = "ABS_Z"
        self.gasbind = "ABS_RZ"
        
        self.brakepedal = 0
        self.gaspedal = 0

        self._thread = threading.Thread(target=self._event, args=())
        self._thread.start()

    def _event(self):
        while True:
            try:
                self.connected = True
                events = get_gamepad()
                for event in events:
                    if self.debug:
                        print("Code: "+str(event.code)+" | State: "+str(event.state))
                    
                    if event.code == self.brakebind:
                        self.brakepedal = int(event.state / self.brakeadjust)
                    if event.code == self.gasbind:
                        self.gaspedal = int(event.state / self.gasadjust)
            except Exception as e:
                print(e)
                self.connected = False
                exit()
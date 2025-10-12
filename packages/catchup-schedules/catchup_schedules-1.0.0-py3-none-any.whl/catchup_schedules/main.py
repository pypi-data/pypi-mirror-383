import datetime
import re

def run(run_func: callable, looptime: str, cycle_type: bool, resume: bool, starttime: dict = [datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")],running:list=[True]):
        
    """A Persistent Python Scheduler that Remembers Missed Events and Maintains its Cycle.

    A robust scheduling module designed to catch up on periodic tasks that were skipped due to system pauses or downtime.   
    
    :param run_func: The function to be executed repeatedly.  
    :param looptime: Sets the repeat interval (period). You can specify multiple values and units (w, d, h, m, s) separated by spaces.
    :param cycle_type: Determines the method for handling missed cycles. Sets when the next schedule should occur after code execution has been paused and resumed. | - True (Maintain Cycle): Maintains the original period. It calculates the time the function should have last run, updates starttime to that point, and the next execution is scheduled looptime after this updated time. | - False (Start New Cycle): Updates starttime to the current time and starts a new cycle from now.
    :param resume: 	Determines whether to immediately execute run_func once upon starting the module if any schedules were missed while the code was paused. | Note: This setting operates independently of the cycle_type setting. The function will execute when resume is True if any cycles were missed, regardless of the value of cycle_type.	
    :param starttime: 	(Optional) A list used to store and remember the previous execution time. It must contain a string in the format of ["YYYY-MM-DDTHH:MM:SSZ"] or [""]. The default value is the current time if the variable is not passed, and it is also initialized to the current time if the variable's value is an empty string ([""]).
    :param running: 	(Optional) 	A list used to control the execution state of a function. It is expected to contain a single boolean value (True or False). When the value is [True], the function continues execution. When it is [False], the function terminates and exits. The default value is [True].
    """
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    if starttime[0] == '""':
        starttime[0] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    start_datatime = datetime.datetime.strptime(starttime[0], datetime_format)

    def parse_looptime(looptime_str):
        pattern = r'(\d+)\s*([wdhms])'
        matches = re.findall(pattern, looptime_str)
        if not matches:
            raise ValueError("Invalid looptime format")
        kwargs = {}
        for value, unit in matches:
            if unit == 'w':
                kwargs['weeks'] = kwargs.get('weeks', 0) + int(value)
            elif unit == 'd':
                kwargs['days'] = kwargs.get('days', 0) + int(value)
            elif unit == 'h':
                kwargs['hours'] = kwargs.get('hours', 0) + int(value)
            elif unit == 'm':
                kwargs['minutes'] = kwargs.get('minutes', 0) + int(value)
            elif unit == 's':
                kwargs['seconds'] = kwargs.get('seconds', 0) + int(value)
        return datetime.timedelta(**kwargs)

    loop_timedelta = parse_looptime(looptime)
            
            
    current_datetime = datetime.datetime.now()
    if start_datatime + loop_timedelta <= current_datetime:

        #2주마다 실행일때 1주일 후 멈추고 2주가 지낫ㅇㄹ때
        # start_datatime을 마지막으로 놓친 실행주기 시간으로 설정해서 2주 주기를 유지할것인가
        if cycle_type:
            while start_datatime + loop_timedelta < current_datetime:
                start_datatime += loop_timedelta
        #아니면 함수 실행 후 start_datatime을 현재시간으로 해서 2주 주기를 바꿀것인가
        else:
            start_datatime = current_datetime

        if resume:
            run_func()    
        starttime[0] = start_datatime.strftime(datetime_format)
    # while resume:
    while running[0]:
        current_datetime = datetime.datetime.now()
        if start_datatime + loop_timedelta <= current_datetime: 
            start_datatime += loop_timedelta
            run_func()
            starttime[0] = start_datatime.strftime(datetime_format)

# catchup_schedules.run(test,"10s ",True,True)#Example

#TODO: pypi, DOCS, async version
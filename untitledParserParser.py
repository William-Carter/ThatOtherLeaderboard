import subprocess
import os
import regex as re
from typing import Union
dirPath = os.path.dirname(os.path.realpath(__file__))

class DemoParse:
    def __init__(self, demoFile):
        self.uPOutput = str(subprocess.check_output((dirPath+"\\UntitledParser.exe", demoFile)))
        self.valid = self.checkParsingSucceeded()
        if self.valid:
            self.specialTimingPoint = False
            self.ticks = self.timeDemo()
            self.time = self.timeDemo(convertTime=True)
            self.map = self.getMap()
            self.name = self.fetchName()



    def checkParsingSucceeded(self):
        e = re.findall(r"(?<=Parsing .+\.\.\. )[^\\\n]+", self.uPOutput)
        if e[0] == "done.":
            return True
        elif e[0] == "failed.":
            return False


    def timeDemo(self, convertTime: bool = False) -> Union[int, float]:
        lines = self.uPOutput.split("Adjusted ticks")
        if len(lines) > 1:
            ticks = int(lines[1].split(": ")[1].split(" ")[0])
            self.specialTimingPoint = True
        else:
            lines = self.uPOutput.split("Measured ticks")
            ticks = int(lines[1].split(": ")[1].split("\\r")[0])
            
        
        if not convertTime:
            return int(ticks)
        else:
            
            seconds = round(ticks*0.015, 3)
            return seconds


    def fetchName(self):
        e = re.findall(r"(?<=Client name\s+:\s)[^\\]+", self.uPOutput)
        if len(e) > 0:
            return e[0]
        else:
            return ""
        


    def getMap(self) -> str:
        lines = self.uPOutput.split("Map name")
        mapName = lines[1].split(": ")[1].split("\\n")[0]
        return mapName
    
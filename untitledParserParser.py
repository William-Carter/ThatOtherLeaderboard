import subprocess
import os
from typing import Union
dirPath = os.path.dirname(os.path.realpath(__file__))

class DemoParse:
    def __init__(self, demoFile):
        self.uPOutput = str(subprocess.check_output((dirPath+"\\UntitledParser.exe", demoFile)))
        self.ticks = self.timeDemo()
        self.time = self.timeDemo(convertTime=True)
        self.map = self.getMap()


    def timeDemo(self, convertTime: bool = False) -> Union[int, float]:
        lines = self.uPOutput.split("Adjusted ticks")
        if len(lines) > 1:
            ticks = int(lines[1].split(": ")[1].split(" ")[0])
        else:
            lines = self.uPOutput.split("Measured ticks")
            ticks = int(lines[1].split(": ")[1].split("\\r")[0])
            
        
        if not convertTime:
            return int(ticks)
        else:
            
            seconds = round(ticks*0.015, 3)
            return seconds


    def getMap(self) -> str:
        lines = self.uPOutput.split("Map name")
        mapName = lines[1].split(": ")[1].split("\\n")[0]
        return mapName
    
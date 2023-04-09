# Cura PostProcessingPlugin
# Author:   Chris Jackson
# Date:     10 April 2023

# Description:  This script searches for feature types and overrides the fan speed to the setting specified. 
# When any other feature type is found, it sets the fan speed back to whatever the speed was before it was overridden.

from ..Script import Script
import re

class FeatureFanSpeed(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name":"Feature Fan Speed",
            "key":"FeatureFanSpeed",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "innerFanSpeedEnable":
                {
                    "label": "Adjust Inner Fan Speed",
                    "description": "Select to adjust the inner wall fan speed",
                    "type": "bool",
                    "default_value": false
                },
                "innerFanSpeed":
                {
                    "label": "Fan Speed on Inner Wall",
                    "description": "Fan Speed (0-100)",
                    "unit": "%",
                    "type": "int",
                    "default_value": 100,
                    "minimum_value": "0",
                    "minimum_value_warning": "5",
                    "maximum_value_warning": "100"
                },
                "outerFanSpeedEnable":
                {
                    "label": "Adjust Outer Fan Speed",
                    "description": "Select to adjust the outer wall fan speed",
                    "type": "bool",
                    "default_value": false
                },
                "outerFanSpeed":
                {
                    "label": "Fan Speed on Outer Wall",
                    "description": "Fan Speed (0-100)",
                    "unit": "%",
                    "type": "int",
                    "default_value": 100,
                    "minimum_value": "0",
                    "minimum_value_warning": "5",
                    "maximum_value_warning": "100"
                },
                "skinFanSpeedEnable":
                {
                    "label": "Adjust Skin Fan Speed",
                    "description": "Select to adjust the skin fan speed",
                    "type": "bool",
                    "default_value": false
                },
                "skinFanSpeed":
                {
                    "label": "Fan Speed on Skin",
                    "description": "Fan Speed (0-100)",
                    "unit": "%",
                    "type": "int",
                    "default_value": 100,
                    "minimum_value": "0",
                    "minimum_value_warning": "5",
                    "maximum_value_warning": "100"
                },
                "fillFanSpeedEnable":
                {
                    "label": "Adjust Fill Fan Speed",
                    "description": "Select to adjust the fill fan speed",
                    "type": "bool",
                    "default_value": false
                },
                "fillFanSpeed":
                {
                    "label": "Fan Speed on Fill",
                    "description": "Fan Speed (0-100)",
                    "unit": "%",
                    "type": "int",
                    "default_value": 100,
                    "minimum_value": "0",
                    "minimum_value_warning": "5",
                    "maximum_value_warning": "100"
                },
                "layer0FanSpeedEnable":
                {
                    "label": "Adjust Layer 0 Fan Speed",
                    "description": "Select to adjust the fan speed on layer 0",
                    "type": "bool",
                    "default_value": false
                },
                "layer0FanSpeed":
                {
                    "label": "Fan Speed for Layer 0",
                    "description": "Fan Speed (0-100)",
                    "unit": "%",
                    "type": "int",
                    "default_value": 100,
                    "minimum_value": "0",
                    "minimum_value_warning": "5",
                    "maximum_value_warning": "100"
                }
            }
        }"""

    def getValue(self, line, key, default = None): #replace default getvalue due to comment-reading feature
        if not key in line or (";" in line and line.find(key) > line.find(";") and
                                   not ";LAYER:" in key):
            return default
        subPart = line[line.find(key) + len(key):] #allows for string lengths larger than 1
        if ";LAYER:" in key:
            m = re.search("^[+-]?[0-9]*", subPart)
        else:
            m = re.search("^[-]?[0-9]*\.?[0-9]*", subPart)
        if m == None:
            return default
        try:
            return float(m.group(0))
        except:
            return default

    def valueToPercent(self, value):
        return int((value * 100) / 255)

    def percentToValue(self, value):
        return int((value / 100) * 255)

    def execute(self, data):
      curaFanSpeed = 0

      innerFanSpeedEnable = self.getSettingValueByKey("innerFanSpeedEnable")
      innerFanSpeed = self.percentToValue(self.getSettingValueByKey("innerFanSpeed"))
      outerFanSpeedEnable = self.getSettingValueByKey("outerFanSpeedEnable")
      outerFanSpeed = self.percentToValue(self.getSettingValueByKey("outerFanSpeed"))
      skinFanSpeedEnable = self.getSettingValueByKey("skinFanSpeedEnable")
      skinFanSpeed = self.percentToValue(self.getSettingValueByKey("skinFanSpeed"))
      fillFanSpeedEnable = self.getSettingValueByKey("fillFanSpeedEnable")
      fillFanSpeed = self.percentToValue(self.getSettingValueByKey("fillFanSpeed"))
      layer0FanSpeedEnable = self.getSettingValueByKey("layer0FanSpeedEnable")
      layer0FanSpeed = self.percentToValue(self.getSettingValueByKey("layer0FanSpeed"))

      speedSet = False
      layer = 0              
      index = 0
      for active_layer in data:
        modified_gcode = ""
        lines = active_layer.split("\n")

        for line in lines:
          if "M106" in line:
            curaFanSpeed = self.getValue(line, "S", curaFanSpeed)   
          
          if "M107" in line:
            curaFanSpeed = 0
          
          if ";LAYER:" in line:
            layer = self.getValue(line, ";LAYER:", layer)
          
          if layer == 0 and ";TYPE:" in line and layer0FanSpeedEnable: 
              modified_gcode += ";Layer 0 Fan Speed %d%%\nM106 S%d\n" % (self.valueToPercent(layer0FanSpeed), layer0FanSpeed)
              speedSet = True
              layer0FanSpeedEnable = False
          elif layer > 0:
            if ";TYPE:WALL-OUTER" in line and outerFanSpeedEnable is True:
              modified_gcode += ";Outer Wall Fan Speed %d%%\nM106 S%d\n" % (self.valueToPercent(outerFanSpeed), outerFanSpeed)
              speedSet = True
            elif ";TYPE:WALL-INNER" in line and innerFanSpeedEnable is True:
              modified_gcode += ";Inner Wall Fan Speed %d%%\nM106 S%d\n" % (self.valueToPercent(innerFanSpeed), innerFanSpeed)
              speedSet = True
            elif ";TYPE:SKIN" in line and skinFanSpeedEnable is True:
              modified_gcode += ";Skin Fan Speed %d%%\nM106 S%d\n" % (self.valueToPercent(skinFanSpeed), skinFanSpeed)
              speedSet = True
            elif ";TYPE:FILL" in line and fillFanSpeedEnable is True:
              modified_gcode += ";Fill Fan Speed %d%%\nM106 S%d\n" % (self.valueToPercent(fillFanSpeed), fillFanSpeed)
              speedSet = True
            elif ";TYPE:" in line and speedSet is True:
              modified_gcode += ";Fan Speed restored %d%%\nM106 S%d\n" % (self.valueToPercent(curaFanSpeed), curaFanSpeed)
              speedSet = False

          modified_gcode += line + "\n"
          
        data[index] = modified_gcode
        index += 1
        
      return data

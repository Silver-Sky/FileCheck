import datetime
import logging
import getpass
import threading
import time

#configuration
pathToConfig = "Property.properties"


logger = logging.getLogger('LogFileChecker')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('LogFileChecker.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

'''# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message') '''

class Property():
    
    def __init__(self, checkname):
        self.__checkname = str(checkname)
        self.__type = None
        self.__dateformate = '%b %d %Y'
        self.__position = 0
        self.__separator = ","
        self.__searchPattern = "not defined"
        self.__validation = "not defined"
        self.__positionToCheck = self.__position+1
        self.__scanPath = "/testfile"
        #__result and __comparedValue will be set during the execution
        self.__result = False
        self.__comparedValue = ""

    def addType(self, t):
        self.__type = t

    def addPostion(self, pos):
        self.__position = pos

    def addSeparator(self, sep):
        self.__separater = sep
    
    def addPattern(self, pattern):
        self.__searchPattern = pattern

    def addPTC(self, ptc):
        self.__positionToCheck = ptc

    def addScanPath(self, path):
        self.__scanPath = path 

    def addValidation(self, valid):
        self.__validation = valid

    def setResult(self, result, comparedValue):
        self.__result = result
        self.__comparedValue = str(comparedValue)
    
    def setPassIfnoMatch(self):
        self.__result = True        

    def setDateFormat(self, vFormat):
        self.__dateformate = vFormat
    
    def getResult(self):
        return self.__result

    def getComparedValue(self):
        return self.__comparedValue

    def getName(self):
        return self.__checkname
    
    def getType(self):
        return self.__type

    def getPostion(self):
        return int(self.__position)

    def getSeparator(self):
        return self.__separater
    
    def getPattern(self):
        return self.__searchPattern

    def getPTC(self):
        return int(self.__positionToCheck)

    def getScanPath(self):
        return self.__scanPath

    def getValidation(self):
        return self.__validation

    def getDateFormat(self):
        return self.__dateformate

    def __str__(self):
        return ("Class Property with values - getName: " + self.getName() + " getType: " + self.getType() + " getPostion: " + str(self.getPostion()) + " getSeparator: " + str(self.getSeparator()) + " getPattern: " + str(self.getPattern()) + " getValidation: " + self.getValidation() + " getPTC: " + str(self.getPTC()) + " getScanPath: " + self.getScanPath() + " Pass check if the pattern is not matching: " + str(self.__result))

    def __repr__(self):
        return self.__str__()

class LoadFile():
    
    def __init__(self, pfad):

        try:
            self.__file = open(pfad, "r")
        except Exception as ex:
        # THis will catch any exception!
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.info(message)

        
        self.__filelist = []

        for line in self.__file:
            self.__filelist.append(line.strip())
            logger.debug("loadFile() line -> " + line.strip())
        
    def getFileAsList(self):
        #Get file as list as it is.
        return self.__filelist
    
    def getFileAsListWOComments(self):
        #Get File as a list without comment and empty rows
        listWOComments = []

        for line in self.__filelist:
            if line.strip()[:1] == "#" or line.strip() == "" or not line:    
                logger.debug("Line with # or None -> " + str(line))
            else:
                listWOComments.append(line.strip())

        logger.debug("Return list w/o Comments: " + str(listWOComments))
        return listWOComments


class ResultOutput():
    def __init__(self,filename):
        self.__file = open(filename, "w")
        self.writeHeader()

    def writeHeader(self):
        writeValue = "**** Scan Log " + str(datetime.datetime.now()) + " by " + getpass.getuser() + " ****\n\n"
        self.__file.write(writeValue)
        logger.info(writeValue)
    
    def saveResult(self, prop):
        writeValue = "    " + str(prop.getName()) + "\t type: \t" + prop.getType() + " Compared Value: " + prop.getComparedValue()
        if prop.getResult():
            writeValue = writeValue + "\n>   Passed\n"
        else: 
            writeValue = writeValue + "\n!-> Failed!!!\n"
        logger.info(writeValue)
        self.__file.write(writeValue)

    def writeEOF(self):
        writeValue= "\n**** All Test executed: " + str(datetime.datetime.now()) + " ****"
        self.__file.write(writeValue)
        logger.info(writeValue)


class LoadProperties():
    def __init__(self, propertiesRAWFile):
        self.__properties = []
        self.__importProperties(propertiesRAWFile)
        
    def __importProperties(self, fileAsList):
        prop = None
        propstring = "No Properties"
        for line in fileAsList:
            logger.debug("RAW Line: "+ str(line))
            if len(line.split("=")) < 1 and len(line.split("=")) > 1:
                logger.debug("Invalid line ignored: " + line)
                continue
            else:
                identifier = line.split("=")[0].strip().lower()
                value = line.split("=")[1]

            logger.debug("LINE: identifier=" + identifier + " Value="+value)

            if prop == None and identifier == "name":
                prop = Property(value.strip())
                self.__properties.append(prop)
                continue
            elif prop != None and identifier == "name":
                prop = Property(value.strip())
                self.__properties.append(prop)
                continue
            elif identifier == "type":
                prop.addType(value.strip())
                continue
            elif identifier == "position":
                prop.addPostion(int(value.strip()))
                continue
            elif identifier == "separator":
                prop.addSeparator(value)
                continue
            elif identifier == "searchpattern":
                prop.addPattern(value.strip())
                continue
            elif identifier == "dateformat":
                prop.setDateFormat(value.strip())
                continue
            elif identifier == "validation":
                prop.addValidation(value.strip())
                continue
            elif identifier == "postiontocheck":
                prop.addPTC(int(value.strip()))
                continue
            elif identifier == "scanpath":
                prop.addScanPath(value.strip())
                continue
            elif identifier == "passifnomatch" and value.strip() == "True":
                prop.setPassIfnoMatch()
                logger.debug("Set PassIfnoMatch to true")
                continue
            
        logger.debug("Propertiies list: " + str(self.__properties))


    def getPropertiesAsList(self):
        return self.__properties

class Scan():

    def __init__(self, propertiesList, resultOutput):
        self.__propertiesList = propertiesList
        self.__resultOutput = resultOutput
         
    def startScan(self):
        logger.debug("Start file scan")
        for prop in self.__propertiesList:
            
            try:
                self.__check(prop)
            except Exception as ex:
                # THis will catch any exception!
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                logger.info(message)
                prop.setResult(False, message)

            self.__resultOutput.saveResult(prop)
    
    def __check(self, prop):
        file = LoadFile(prop.getScanPath()).getFileAsListWOComments()
        dataFromFile = []
        patternFound = False
        cResult = True
        for line in file:
            sLine = line.split(prop.getSeparator())
            patternYes = self.__line(sLine, prop)
            
            if patternYes == "":
                continue
            else:
                logger.debug("Data from File: " + (line[prop.getPTC()]))
                dataFromFile.append(sLine[prop.getPTC()].strip())
        
        logger.debug("Data to compare: " +str(dataFromFile))
        
        for itmeToCheck in dataFromFile:
            if cResult == True:
                cResult = self.__compare(prop, itmeToCheck)
                logger.debug("Scan Result: "+ str(cResult) + " Compared Value: " + itmeToCheck)
                prop.setResult(cResult, itmeToCheck)
            else:
                logger.debug("Scan Result: "+ str(cResult) + " Compared Value: " + itmeToCheck)
                cResult = False
                continue
            
    def __compare(self, prop, dataFromFile):
        passedBol = False

        if prop.getType().lower() == "date":
            today = datetime.datetime.combine(datetime.datetime.today().date(), datetime.datetime.min.time())
            dateToCompare = today - datetime.timedelta(days=int(prop.getValidation()))
            logger.debug("Validation Date: " + str(dateToCompare))
            logger.debug("Date from file Plain String: " + dataFromFile)
            logger.debug("ValidateToCompare dation Date: " + str(datetime.datetime.strptime(dataFromFile, prop.getDateFormat())))

            if dateToCompare <= datetime.datetime.strptime(dataFromFile, prop.getDateFormat()):
                passedBol = True
            else:
                passedBol = False

        elif prop.getType().lower() == "integer":
            logger.debug("Validation int: " + str(prop.getValidation()))
            logger.debug("Date from file Plain int: " + str(dataFromFile))

            if int(dataFromFile) == int(prop.getValidation()):
                passedBol = True
            else:
                passedBol = False
        elif prop.getType().lower() == "string":
            logger.debug("Validation String: " + str(prop.getValidation()))
            logger.debug("Date from file Plain String: " + str(dataFromFile))
            if str(dataFromFile) == str(prop.getValidation()):
                passedBol = True
            else:
                passedBol = False

        return passedBol


    def __line(self, splitedLine, prop):
        returnVar = ""
        if len(splitedLine) >= prop.getPTC():
            logger.debug("Line on position: " + splitedLine[prop.getPostion()].strip() )
            if splitedLine[prop.getPostion()].strip() == prop.getPattern().strip():
                logger.debug("Pattern found: " + str(splitedLine) + " Pattern: " + splitedLine[prop.getPostion()])
                returnVar = splitedLine[prop.getPTC()]
            else:
                logger.debug("Pattern NOT found: " + str(prop.getPattern()) + " String: " + str(splitedLine))
                returnVar = ""
        else:
            logger.debug("Pattern line is empty or out of range " + str(splitedLine))
            returnVar = ""
        
        return returnVar




#Start

properties = LoadProperties(LoadFile(pathToConfig).getFileAsListWOComments()).getPropertiesAsList()
output = ResultOutput("Scan Result " + datetime.datetime.now().strftime('%Y-%b-%d-%H%M') + "by " + getpass.getuser() +".log")

Scan(properties, output).startScan()

output.writeEOF()
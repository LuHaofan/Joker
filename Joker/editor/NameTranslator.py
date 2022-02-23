import json


class NameTranslator():
    def __init__(self):
        self.ntdbPath = "editor/static/editor/json/ntdb.json"
        f = open(self.ntdbPath, "r")
        self.json = json.load(f)
        f.close()
    
    def i2d(self, innerName):
        '''
        Translate innerName to displayName
        '''
        db = self.json["i2d"]
        return db[innerName]

    def d2i(self, displayName):
        '''
        Translate displayName to innerName
        '''
        db = self.json["d2i"]
        return db[displayName]

    def addEntry(self, innerName, displayName):
        '''
        Add new entry to the name translation database
        '''
        self.json["i2d"][innerName] = displayName
        self.json["d2i"][displayName] = innerName
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)

    def updateEntry(self, innerName, displayName):
        '''
        update entry in the name translation database
        '''
        if innerName in self.json["i2d"].keys():
            old_displayName = self.json["i2d"][innerName]
            self.json["i2d"][innerName] = displayName
            self.json["d2i"][old_displayName] = innerName
            with open(self.ntdbPath, 'w') as f:
                json.dump(self.json, f)
        else:
            print("Note file does not exist")

    def deleteEntry(self, displayName):
        if displayName in self.json["d2i"].keys():
            innerName = self.json["d2i"][displayName]
            del self.json["d2i"][displayName]
            del self.json["i2d"][innerName]
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)

    def clear(self):
        self.json["i2d"] = {}
        self.json["d2i"] = {}
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)

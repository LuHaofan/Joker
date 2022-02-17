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
        Also use this function for update the name translation database
        '''
        self.json["i2d"][innerName] = displayName
        self.json["d2i"][displayName] = innerName
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)

    def deleteEntry(self, innerName, displayName):
        if innerName in self.json["i2d"].keys():
            del self.json["i2d"][innerName]
        if displayName in self.json["d2i"].keys():
            del self.json["d2i"][displayName]
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)

    def clear(self):
        self.json["i2d"] = {}
        self.json["d2i"] = {}
        with open(self.ntdbPath, 'w') as f:
            json.dump(self.json, f)


if __name__ == "__main__":
    nt = NameTranslator()
    nt.addEntry("3387514.3405866", "WiTAG")
    nt.addEntry("3422604.3425951", "Polite WiFi")
    # nt.deleteEntry("3387514.3405866", "WiTAG")
    print(nt.d2i("WiTAG"))
    # nt.clear()




    
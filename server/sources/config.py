class config:
    def __init__(self, file, parseToken):
        self.configFile = file
        self.configOptions = self.readConfigFile(parseToken)

    def __init__(self, file):
        self.configFile = file
        self.configOptions = readConfigFile(':')

    def readConfigFile(self, parseToken):
        f = open(self.configFile, 'r')
        lines = [l for l in f.readlines()]
        dict = {}
        for l in lines:
            parts = l.split(parseToken)
            for part in parts:
                part = part.strip()
            dict[ parts[0] ] = parts[1]
        return dict

    def get(self, option):
        try:
            opt = self.configOptions[option]
            return opt
        except KeyError as e:
            return None


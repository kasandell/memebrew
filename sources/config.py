class config(object):
    fname = '/Users/kylesandell/Desktop/Developer/MachineLearningMemes/conf.cfg'
    opts = None
    @staticmethod
    def readConfigFile( parseToken):
        f = open(config.fname, 'r')
        lines = [l for l in f.readlines()]
        dict = {}
        for l in lines:
            parts = l.split(parseToken)
            for part in parts:
                part = part.strip()
            dict[ parts[0].strip()] = parts[1].strip()
        return dict

    @staticmethod
    def get( option):
        if config.opts is None:
            config.opts = config.readConfigFile(';')
            print config.get('databaseLocation')

        try:
            opt = config.opts[option]
            return opt
        except KeyError as e:
            return None


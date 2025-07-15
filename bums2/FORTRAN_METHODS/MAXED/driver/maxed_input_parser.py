#This is a new script that will take the file parsing logic from main.pl in the original MAXED directory
import numpy as np

class MaxedInputParser:
    def __init__(self, input_path, response_path):
        self.input_path = input_path
        self.response_path = response_path

        self.input_data = {}
        self.response_data = {}

    def parse(self):
        self._parse_input_file()
        self._parse_response_file()

    def _parse_input_file(self):
        with open(self.input_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        self.input_data['M'], self.input_data['N0'] = map(int, lines[0].split(","))
        M, N0 = self.input_data['M'], self.input_data['N0']

        self.input_data['RFN'] = []
        self.input_data['D'] = []
        self.input_data['S'] = []

        for i in range(1, M+1):
            rfn_i, d_i, s_i = map(float, lines[i].split(","))
            self.input_data['RFN'].append(int(rfn_i))
            self.input_data['D'].append(d_i)
            self.input_data['S'].append(s_i)

        self.input_data['ENBZKL'] = []
        self.input_data['ZKL'] = []

        for i in range(M+1, M+1+N0):
            e, z = map(float, lines[i].split(","))
            self.input_data['ENBZKL'].append(e)
            self.input_data['ZKL'].append(z)

    def _parse_response_file(self):
        with open(self.response_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        MMM = int(lines[0])
        N1 = int(lines[1])
        units = lines[2]

        ENBR = [float(lines[3])]
        RES_rows = []

        for line in lines[4:]:
            parts = line.split(",")
            ENBR.append(float(parts[0]))
            RES_rows.append([float(x) for x in parts[1:]])

        RES = np.array(RES_rows).T.tolist()

        self.response_data['MMM'] = MMM
        self.response_data['N1'] = N1
        self.response_data['UNITS'] = units
        self.response_data['ENBR'] = ENBR
        self.response_data['RES'] = RES

    def get_input_data(self):
        return self.input_data
    
    def get_response_data(self):
        return self. response_data


        
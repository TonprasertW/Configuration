'''
888888b.             888 888                      888               
888  "88b            888 888                      888               
888  .88P            888 888                      888               
8888888K.   888  888 888 888  8888b.  888d888 .d88888 .d8888b       
888  "Y88b  888  888 888 888     "88b 888P"  d88" 888 88K           
888    888  888  888 888 888 .d888888 888    888  888 "Y8888b.      
888   d88P  Y88b 888 888 888 888  888 888    Y88b 888      X88      
8888888P"    "Y88888 888 888 "Y888888 888     "Y88888  88888P'
________________________________________________________________
55 6E 69 76 65 72 73 69 74 79  6F 66  43 61 6D 62 72 69 64 67 65
U  N  I  V  E  R  S  I  T  Y   O  F   C  A  M  B  R  I  D  G  E
________________________________________________________________
@Author: Tonprasert, W. | Github: GitHub/WuttjinanTonprasert.git                                                                   
Wed 4 Dec 17:28:30 GMT 2024
'''
import argparse
from pyrocko.gui import marker as pm

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help='File name of File created needed!')
    args = parser.parse_args()

    return args

def main(args):
    '''
    # this function aims to transform PhaseMarker and EventMarker from manual picks
    # to readable a csv.
    '''
    markers = pm.load_markers(args.filename)
    Ev ,YY ,JDay ,_ = args.filename.split('.')

    for marker in markers:
        if isinstance(marker, pm.PhaseMarker):
            '''
            # print out PhaseMarker first.
            # PhaseNET csv has the following columns.
            # station_id, begin_time, phase_index, phase_time, phase_score, phase_type, file_name, phase_amplitude, phase_amp
            # MY.TNM..BH
            '''
            print(marker._phasename)
            
    return None

if __name__ == "__main__":
    args = read_args()
    main(args)



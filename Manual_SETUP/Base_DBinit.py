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
Thu 12 Dec 10:34:30 GMT 2024

Short Note: Basefile, the initial operations for Database initi-
            alisation.
'''
import sys
import os
import glob
from pyrocko.gui import marker as pm
import argparse
from datetime import datetime, timedelta
import mysql.connector
import pandas as pd
import numpy as np
sys.path.append('/raid2/wt301/Library')

# Import Project's packages
try:
    from core import Borneo_DIR
    NB = Borneo_DIR('/raid2/wt301')
except:
    print('Exit Status == 00')

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath", default = None, help='File name of File created needed!')
    args = parser.parse_args()

    return args

def main(args, pick_count, PreRe, FN):
    '''
    # this function aims to transform PhaseMarker and EventMarker from manual picks
    # to readable a csv.
    '''
    # search for a Specific File Pattern.
    Manual_files = glob.glob('/home/wt301/Desktop/manual/*.Manual')

    '''
    # init the database
    '''
    connection, cursor = SQL_Authorisation()
    cursor.execute("SHOW TABLES LIKE 'ManualPick';") # the problem for unread result, probably because Cursor being used repeatedly.
    if not cursor.fetchone():
        '''
        # the dataset is not exist.
        '''
        SQL_CREATE_TABLE(connection, cursor)

    insert_query = SQL_INSERT_QUERY()
    # loop through manual files and save to Database.
    for file in Manual_files:
        '''
        # a loop within Marker files
        '''
        markers = pm.load_markers(file)
        Ev ,YY ,JDay ,_ = file.split('.')
        Event_ID= int(file.split('/')[5].split('.')[0])
        Data_Insert = []
        
        '''
        # in some cases, Event_Time is not attached to the file, because it is newly picked
        '''
        try:
            Event_Time = datetime.fromtimestamp(markers[0]._event_time)
        except:
            Event_Time = datetime.strptime(NB.NBorneo_CAT.iloc[Event_ID - 1]['DT'], "%Y-%m-%dT%H:%M:%S.%fZ")

        '''
        # PhaseNet fectch search and Data imports
        '''
        PhaseNET_DPATH = PhaseNET_FetchPath(Event_ID)
        MY_Status = False # availibility of Predictions in MY Network.
        YC_Status = False # availibility of Predictions in YC Network.
        if os.path.exists(os.path.join(PhaseNET_DPATH, 'MY.20HZ.PredARR.csv')):
            MY_Pred = pd.read_csv(os.path.join(PhaseNET_DPATH,'MY.20HZ.PredARR.csv'))
            MY_Status = True
        
        if os.path.exists(os.path.join(PhaseNET_DPATH, 'YC.50HZ.PredARR.csv')):
            YC_Pred = pd.read_csv(os.path.join(PhaseNET_DPATH,'YC.50HZ.PredARR.csv'))
            YC_Status = True

        for index, marker in enumerate(markers):
            print(index, marker)
            if isinstance(marker, pm.PhaseMarker):
                '''
                # print out PhaseMarker first.
                # PhaseNET csv has the following columns.
                # station_id, begin_time, phase_index, phase_time, phase_score, phase_type, file_name, phase_amplitude, phase_amp
                # MY.TNM..BH
                '''
                Phase_Type = marker._phasename
                if Phase_Type is not None and marker.tmin == marker.tmax:
                    '''
                    # if PhaseType is not None, mean that one is an error
                    '''
                    NET, STA, _, COMP = marker.nslc_ids[0]
                    Arrival = datetime.fromtimestamp(marker.tmin)
                    Uncertainty_Score = marker.kind
                    Polarity      = marker._polarity if marker._polarity is not None else '0'
                    '''
                    # Append PhaseNET result.
                    '''
                    exit_status = False
                    if NET == 'MY' and MY_Status:
                        Time, Score = PhaseNET_FetchSearch(MY_Pred, NET, STA, Phase_Type)
                        exit_status = True

                    elif NET == 'YC' and YC_Status:
                        Time, Score = PhaseNET_FetchSearch(YC_Pred, NET, STA, Phase_Type)
                        exit_status = True
                    
                    '''
                    # Filtering the dataset and set into the proper files.
                    '''
                    if ( exit_status and Time is None ) or not exit_status:
                        Data_Insert.append((NET, STA, COMP, Event_ID, Phase_Type, Uncertainty_Score, Event_Time, Arrival, None, None, Polarity))
                        if Uncertainty_Score != 0 :
                            FN[Phase_Type][str(Uncertainty_Score)] += 1
                        PreRe['Q'] += 1
                    
                    elif isinstance(Time, list) and exit_status:
                        for indexa in range(len(Time)):
                            Data_Insert.append((NET, STA, COMP, Event_ID, Phase_Type , Uncertainty_Score, Event_Time, Arrival, Time[indexa], Score[indexa], Polarity))
                            '''
                            # Precision and Recall functions.
                            '''
                            PreRe = Temp_PrecisionRecall(Arrival, Time[indexa], Score[indexa], Uncertainty_Score, Phase_Type, PreRe)

                    else:
                        # the function is presented in Index
                        Data_Insert.append((NET, STA, COMP, Event_ID, Phase_Type, Uncertainty_Score, Event_Time, Arrival, Time, Score,  Polarity))
                        '''
                        # Precision and Recall functions
                        '''
                        PreRe = Temp_PrecisionRecall(Arrival, Time, Score, Uncertainty_Score, Phase_Type, PreRe)

                    '''
                    # Counting part
                    '''
                    pick_count = Temp_Counting(pick_count, Phase_Type, Uncertainty_Score) # counting for Picking.

        if Data_Insert:
            '''
            # the data to insert is exist.
            '''
            cursor.fetchall()
            cursor.executemany(insert_query, Data_Insert)
            connection.commit()
    
    if connection:
        connection.close()
    if cursor:
        cursor.close()

    return pick_count, PreRe, FN

def SQL_Authorisation():
    '''
    # SQL connections establised
    '''
    connection = mysql.connector.connect(user="wt301", password="Nanittuw@140220", database="wt301_db")
    cursor = connection.cursor()

    return connection, cursor

def SQL_CREATE_TABLE(connection, cursor):
    '''
    # Create file from the directory
    '''
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ManualPick (
        Network CHAR(3),
        Station VARCHAR(6),
        Component CHAR(4),
        Event_ID SMALLINT(5),
        PhaseType CHAR(2),
        Uncertainty TINYINT(3),
        Event_time DATETIME(6),
        Arrival DATETIME(6),
        PNETARR DATETIME(6),
        PSCORE DOUBLE,
        Polarity TINYINT(3)
    );
    """
    cursor.execute(create_table_query)
    print(cursor.execute("SHOW TABLES"))
    return None

def SQL_INSERT_QUERY():
    '''
    # Create a query list to the data type.
    '''
    insert_query = """
    INSERT INTO ManualPick (Network, Station, Component, Event_ID, PhaseType, Uncertainty, Event_time, Arrival, PNETARR, PSCORE, Polarity)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    return insert_query

def PhaseNET_FetchPath(Event_ID):
    '''
    # a function to search for PhaseNET predictions search
    '''
    Search_DIR = os.path.join(NB.PredARR, 'MSEED', f'MSEED_{Event_ID}', 'Result')
    return Search_DIR

def PhaseNET_FetchSearch(df, NET, STA, PhaseType):
    '''
    # a function to fetch a PhaseNET's Prediction.
    # Parameters
    # - df | Pandas Dataframe class | DataFrame class
    '''
    search_criteria = NET + '.' + STA + '..BH'
    
    index = df.loc[ (df['station_id'] == search_criteria) & (df['phase_type'] == PhaseType) ].index
    if len(index) == 0:
        index = None
    
    if index is not None:
        if len(index) > 1:
            PhaseTime = [ datetime.strptime(df.iloc[I]['phase_time'], "%Y-%m-%dT%H:%M:%S.%f") for I in index ]
            PhaseScore= [ float(df.iloc[I]['phase_score']) for I in index ]
            #PhaseAmps = [ df.iloc[I]['phase_amp'] for I in index ]

        else:
            # len index = 0
            PhaseTime = datetime.strptime(df.iloc[index[0]]['phase_time'], "%Y-%m-%dT%H:%M:%S.%f")
            PhaseScore= float(df.iloc[index[0]]['phase_score'])
            #PhaseAmps = df.iloc[index[0]]['phase_amp']
        return PhaseTime, PhaseScore
    
    else:
        # no PhaseNET predictions.
        return None, None

def Temp_Counting(dicta, Phase_Type, Score):
    '''
    # A temporary function to count the number of the functions.
    '''
    if Phase_Type != 'P' and Phase_Type != 'S':
        dicta['Q'] += 1
    
    else:
        if Score >= 1 and Score <= 4:
            Score = str(Score)
            dicta[Phase_Type][Score] += 1

    return dicta

def Temp_PrecisionRecall(Time1, Time2, PNScore, PScore, PhaseType, PreRe):
    '''
    # A Precision and Recall Temporary
    '''
    difference = abs(Time1 - Time2)
    one_hour   = timedelta(hours = 1)
    adjusted_difference = abs(difference - one_hour).total_seconds()

    Score = str(PScore)
    PreRe[PhaseType][str(Score)].append([adjusted_difference, PNScore])
    return PreRe

def precision(TP, FP):
    return TP/(TP + FP)

def recall(TP, FN):
    return TP/(TP+FN)

def F1(pre, re):
    return 2*(pre*re)/(pre*re)

def Plot(plot_list, plot_list_b, FN_P, FN_S, fig):
    '''
    # a function to plot.
    '''
    ax = fig.axes
    
    x_vals = np.array([ point[0] for point in plot_list ])
    y_vals = np.array([ point[1] for point in plot_list ])
    x_val  = np.array([ point[0] for point in plot_list_b ])
    y_val  = np.array([ point[1] for point in plot_list_b ])
    
    TP_P = len(x_vals[ x_vals <= 0.4 ])
    TP_S = len(x_val[ x_val <= 0.4 ])

    FP_P = len(x_vals[ (x_vals > 0.4) & (x_vals < 4) ])
    FP_S = len(x_val[ (x_val > 0.4) & (x_val < 4) ])

    P_precision = precision(TP_P, FP_P)
    S_precision = precision(TP_S, FP_S)

    P_recall = recall(TP_P, FN_P)
    S_recall = recall(TP_S, FN_S)

    P_F1 = F1(P_precision, P_recall)
    S_F1 = F1(S_precision, S_recall)
    
    print(TP_P,FP_P,FN_P)
    print(TP_S,FP_S,FN_S)
    print('P', P_precision, P_recall, P_F1)
    print('S', S_precision, S_recall, S_F1)

    ax[0].scatter(x_vals, y_vals, c= 'coral',label = f'P, N = {len(x_vals)}')
    ax[1].scatter(x_val,  y_val, c = 'royalblue', label = f'S, N = {len(x_val)}')
    #ax[0].set_xlabel('Time Residual (Seconds)')
    ax[0].set_ylabel('PhaseScore from PhaseNET')
    ax[1].set_xlabel('Time Residual (Seconds)')
    ax[1].set_ylabel('PhaseScore from PhaseNET')
    ax[0].set_xlim(0,1)
    ax[1].set_xlim(0,1)
    ax[0].legend()
    ax[1].legend()
    ax[0].set_title('A Correlation between Time Residual(s) and PhaseNET score for that picks \n Assigning Score: 1' )
    plt.show()

if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    args = read_args()
    '''
    # A part to count the pickings. 
    '''
    num_picks = { 'P': {'1': 0,
                        '2': 0,
                        '3': 0,
                        '4': 0},
                  'S': {'1': 0,
                        '2': 0,
                        '3': 0,
                        '4': 0},
                  'Q': 0} # Picks counts for Statistical Analysis 
    PreRe     = {
                'P': {'1': [],
                      '2': [],
                      '3': [],
                      '4': []},
                'S': {'1': [],
                      '2': [],
                      '3': [],
                      '4': []},
                'Q': 0} # Picks counts for Precision and Recall analysis.

    FN = { 'P': {'1': 0,
                 '2': 0,
                 '3': 0,
                 '4': 0},
           'S': {'1': 0,
                 '2': 0,
                 '3': 0,
                 '4': 0}}

    num_picks, PreRe, FN = main(args, num_picks, PreRe, FN)
    print(num_picks)
    print(PreRe)

    
    # PhaseNET
    fig, ax = plt.subplots(figsize=(8,16), nrows=2,ncols=1)
    Plot(PreRe['P']['4'], PreRe['S']['4'], FN['P']['4'], FN['S']['4'], fig)






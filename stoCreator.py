#!/usr/bin/env python3

import os 
import numpy as np
import quaternion 
import math 

'''DIRECTORY DOVE SONO REGISTRATI I DATI'''
path = "/home/simone/Desktop/daler/data" 
filedir = os.listdir(path) 

'''METTERE A TRUE PER CREARE IL .STO DI CALIBRAZIONE E A FALSE PER IL MOVIMENTO'''
is_calibrating = False 

'''LE COLONNE DEVONO ESSERE SEPARATE DA TAB'''
sep = '\t'

'''SCRIVE I DATI SUL FILE'''
def writeData(head, data, file, frq):
    '''ESEMPIO DI INTESTAZIONE DEL FILE'''
    '''
        DataRate=100.000000
        DataType=Quaternion
        version=3
        OpenSimVersion=4.1
        endheader
    '''
    file.write('DataRate=' + str(frq) + '\r\n')
    file.write('DataType=Quaternion\r\n')
    file.write('version=3\r\n')
    file.write('OpenSimVersion=4.1\r\n')
    file.write('endheader\r\n')
    file.write(head)
    file.write('\r\n')
    for i in range(data.shape[0]):
        file.write(data[i])
        file.write('\r\n')

'''FA LA MEDIA DELLE FREQUENZE TRA I FILE DEI SENSORI'''
def getAvgFrequency(files):
    frq_list = []
    for i in range(12):
        if 'sto' not in files[i] :
            frequency = getFrequency(files[i])
            frq_list.append(frequency)
    return int (sum(frq_list)/len(frq_list))

'''FREQUENZA DEL SINGOLO FILE'''
def getFrequency(f):
    tstamps = np.loadtxt(open(os.path.join(path, f), "rb"), delimiter=",", skiprows=0,usecols=(0))
    # print(((tstamps[15]-tstamps[0])/1e9))
    return int(np.shape(tstamps)[0]/((tstamps[-1]-tstamps[0])/1e9))

'''CREA LA PARTE DEL FILE CONTENENTE I DATI'''
def createFileBody(rows, freq):
    rows = evenLength(rows)
    rows = np.column_stack(rows)
    return stackCols(rows, freq).ravel()

'''CREA LA STRINGA CON I NOMI DELLE COLONNE (TEMPO E SENSORI)'''
def createHeader():
    header_row = [file.split('-')[0]+'_imu' for file in sorted(filedir) if 'sto' not in file]
    header_row.insert(0, 'MC5_imu')
    header_row.insert(0, 'MC4_imu')
    header_row.insert(0, 'MC1_imu')
    header_row = sep.join(header_row)
    header_row = 'time' + sep + header_row 
    return header_row

'''UTILITY PER CAMBIARE LA FORMA DELLA MATRICE DI DATI'''
def stackCols(arr, freq):
    lst = []
    for i in range(arr.shape[0]):
        stringa = ''
        for j in range(arr.shape[1]):
            stringa = stringa + sep + arr[i,j]
            if j == 0:
                stringa = arr[i,j]
        '''aggiungo il timestamp'''
        stringa = str((1/freq) * i) + sep + stringa
        lst.append(stringa)
    # print('lunghezza lista', len(lst))
    return np.row_stack(lst)
    # print('the shape of array is:',lst.shape)

'''TAGLIA LE SEQUENZE PER MATCHARE LA PIU CORTA'''
def evenLength(list2d):
    min_len = math.inf
    min_len = len(min(list2d, key=len))
    # print(min_len)
    for i in range(len(list2d)):
        list2d[i] = list2d[i][:min_len]
    return list2d

'''LEGGE UN QUATERNIONE DA FILE, LO RIORDINA E LO TRASFORMA IN QUATERNION'''
def quatFromFile(filerow):
    q_imu = [float(s) for s in filerow.split(',')[1:5]]
    q_imu = changeOrder(q_imu)
    return quaternion.as_quat_array(q_imu)

def quatStringFromFile(filerow):
    #','.join(list)
    list = [s for s in filerow.split(',')[1:5]]
    return ','.join(list)



def quatFromString(str):
    q_imu = [float(s) for s in str.split(',')]
    return quaternion.as_quat_array(q_imu)
 
'''DA XYZW A WXYZ'''
def changeOrder(quat):
    quat2 = []
    quat2.append(quat[3])
    for i in range(3):
        quat2.append(quat[i])
    return quat2

'''DA WXYZ A XYZW'''
def changeOrderReverse(quat):
    quat2 = []
    for i in range(3):
        quat2.append(quat[i+1])
    quat2.append(quat[0])
    return quat2

def changeReference(data):
    rotlist = []
    new_data = []
    riferimento = ' '
    for i in range(data.shape[0]):
        # print(data[i].split(sep)[1:])

        # print(len(data[i].split(sep)[1:]))
        t = data[i].split(sep)[0]
        qs = data[i].split(sep)[1:]
        
        if i == 0:
            riferimento = qs[0]
        # print(riferimento)
        '''BACK'''
        rotlist.append(getRot(qs[0],qs[0]))
        '''PD1'''
        rotlist.append(getRot(qs[1],qs[6]))
        '''PD1'''
        rotlist.append(getRot(qs[2],qs[7]))
        '''BACK'''
        rotlist.append(getRot(qs[3],qs[8]))
        '''BACK'''
        rotlist.append(getRot(qs[4],qs[9]))
        '''BACK'''
        rotlist.append(getRot(qs[5],qs[10]))
        '''BACK'''
        rotlist.append(getRot(qs[6],qs[0]))
        '''BACK'''
        rotlist.append(getRot(qs[7],qs[0]))
        '''BACK'''
        rotlist.append(getRot(qs[8],qs[0]))
        '''BACK'''
        rotlist.append(getRot(qs[9],qs[0]))
        '''BACK'''
        rotlist.append(getRot(qs[10],qs[0]))
        

        '''ROTATE'''
        new_qs = ''
        for j in range(len(qs)):
            if j == 0:
                # new_qs = new_qs + quatToString(rotate(qs[j], rotlist[j])) + sep + quatToString(rotate(qs[j], rotlist[j])) + sep + quatToString(rotate(qs[j], rotlist[j])) + sep + quatToString(rotate(qs[j], rotlist[j])) 
                new_qs = new_qs + quatToString(rotlist[j]) + sep + quatToString(rotlist[j]) + sep + quatToString(rotlist[j]) + sep + quatToString(rotlist[j]) 

            # if j == 8:
            # #     print(quatToString(rotate(qs[j], rotlist[j])))
            #     print(qs[8])
                # new_qs = new_qs + quatToString(rotate(qs[j], rotlist[j])) 
            else:
                # new_qs = new_qs + sep + quatToString(rotate(qs[j], rotlist[j])) 
                new_qs = new_qs + sep + quatToString(rotlist[j]) 
        new_data.append( t + sep + new_qs)
        rotlist.clear()

    new_data = np.asarray(new_data)
    return new_data


        #130.251.21.8, 130.251.200.1
def getRot(q1, ref):
    q1 = quatFromString(q1)
    ref = quatFromString(ref)
    return ref * q1.inverse()

def rotate(q, rt):
    q = quatFromString(q)
    return rt * q

'''RITORNA LA RAPPRESENTAZIONE IN STRINGA DEL QUATERNIONE'''
def quatToString(quat):
    print(quat)
    list = quaternion.as_float_array(quat)
    list = [str(n) for n in list]
    list = changeOrderReverse(list)
    string = ','.join(list)
    # print(string,'\n')
    return string

# q = ['x', 'y', 'z', 'w']
# print(q)
# q = changeOrder(q)
# print(q)

# q = changeOrderReverse(q)
# print(q)
# exit()
'''RIFERIMENTO A ROTAZIONE NULLA'''
# reference = quaternion.as_quat_array([1, 0, 0, 0])
# rot = reference
frequency = getAvgFrequency(filedir)

new_rows_list = []
new_row = []

'''CARICA I DATI DAI FILE'''
print('Filenames:')
for file in sorted(filedir):
    if 'sto' in file:
        print(sep, 'Salto la cartella\n')
        continue
    print(sep, file.split('-')[0])
    
    with open(os.path.join(path, file)) as f:
        for idx, row in enumerate(f):
            # q_imu = quatStringFromFile(row)

            '''aggiungere il tempo alla stringa'''
            new_row.append(quatStringFromFile(row))
            if is_calibrating:
                break
    new_rows_list.append(new_row.copy())
    new_row.clear()
header = createHeader()
data_rows = createFileBody(new_rows_list, frequency)
print(header.split(sep)[1:])
# data_rows = changeReference(data_rows)

'''INFO SU FREQUENZA E FORMA DELLE COLONNE'''
print('Average Frequency:', frequency)
print('Number of Header Columns:',len(header.split(sep)))
print('Number of Data Columns:',len(data_rows[0].split(sep)))
print('Data shape:', data_rows.shape)

'''SCRITTURA FILE'''

fname = 'sto/imu_data.sto'
if is_calibrating:
    fname = 'sto/imu_data_calib.sto'
with open(os.path.join(path, fname), 'w+') as f:
    writeData(header, data_rows, f, frequency)
    
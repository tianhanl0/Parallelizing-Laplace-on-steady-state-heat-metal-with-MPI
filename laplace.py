#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from mpi4py import MPI
import numpy as np
import time
#import matplotlib.pyplot as plt

begin = time.time()

ROWS_total , COLUMNS = 1000 , 1000

my_pe_num = MPI.COMM_WORLD.Get_rank()
total_pe = MPI.COMM_WORLD.Get_size()
lar_pe = total_pe-1

ROWS=int(ROWS_total/total_pe)

MAX_TEMP_ERROR = 0.01
temperature      = np.empty(( ROWS+2 , COLUMNS+2 ))
temperature_last = np.empty(( ROWS+2 ,COLUMNS+2  ))


def initialize_temperature(temp):

    temp[:,:] = 0
    Min = (my_pe_num)*100/total_pe
    Max = (my_pe_num+1)*100/total_pe

    #Set right side boundery condition
    for i in range(ROWS+1):
        temp[ i , COLUMNS+1 ] = Min + ((Max-Min)/ROWS)*i

    #Set bottom boundery condition
    if my_pe_num == lar_pe:
        for i in range(COLUMNS+1):
            temp[ ROWS+1 , i ] = ( 100/COLUMNS ) * i

    return temp


def output(data):
    data.tofile("plate.out")
    

    
initialize_temperature(temperature_last)

max_iterations = 1

if my_pe_num == 0:
    max_iterations = int (input("Maximum iterations: "))
    
    
max_iterations=MPI.COMM_WORLD.bcast(max_iterations, root=0)


dt_global = 100

iteration = 1

while ( dt_global > MAX_TEMP_ERROR ) and ( iteration < max_iterations ):

    for i in range( 1 , ROWS+1 ):
        for j in range( 1 , COLUMNS+1 ):
            temperature[ i , j ] = 0.25 * ( temperature_last[i+1,j] + temperature_last[i-1,j] +
                                            temperature_last[i,j+1] + temperature_last[i,j-1]   )
    
    dt = 0

    for i in range( 1 , ROWS+1 ):
        for j in range( 1 , COLUMNS+1 ):
            dt = max( dt, temperature[i,j] - temperature_last[i,j])
            temperature_last[ i , j ] = temperature [ i , j ]

    dt_global=MPI.COMM_WORLD.reduce(dt, op=MPI.MAX, root=0)
    dt_global=MPI.COMM_WORLD.bcast(dt_global, root=0)
    
    #send down
    if (my_pe_num!=lar_pe):
        MPI.COMM_WORLD.send(temperature[ROWS][:], dest=my_pe_num+1, tag=2)
            
    #receive up   
    if (my_pe_num!=0):
        temperature_last[0][:] = MPI.COMM_WORLD.recv(source=my_pe_num-1, tag=2)
            
    #send up
    if (my_pe_num!=0):
        MPI.COMM_WORLD.send(temperature[1][:], dest=my_pe_num-1, tag=1)
    
    #receive down
    if (my_pe_num!=lar_pe):
        temperature_last[ROWS+1][:] = MPI.COMM_WORLD.recv(source=my_pe_num+1, tag=1)

    iteration += 1
    
    MPI.COMM_WORLD.barrier()


#send all the temperature_last to pe_0
if (my_pe_num!= 0):
    MPI.COMM_WORLD.send(temperature_last, dest=0, tag=0)


#concatenate together
if my_pe_num==0:
    temperature_last=np.array(temperature_last[0:ROWS+1][:])
    
    for i in range(1,lar_pe):
        result=MPI.COMM_WORLD.recv(source=i, tag=0)
        temperature_last=np.concatenate((temperature_last,np.array(result)[1:ROWS+1,:]))

    result=MPI.COMM_WORLD.recv(source=lar_pe, tag=0)
    
    temperature_last=np.concatenate((temperature_last,np.array(result)[1:ROWS+2,:]))
    
    time.sleep(1)
    end = time.time()

    print(f"total runtime of the program is {end - begin}")
    print(f"total iteration is {iteration}")
    
    output(temperature_last)
#    plate = np.fromfile("plate.out", dtype=float).reshape((ROWS_Global+2,COLUMNS+2))
#    plt.imshow(plate, norm=matplotlib.colors.LogNorm(0.1,50,clip=True))
#    plt.show()


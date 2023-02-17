# Parallelizing-Laplace-on-steady-state-heat-metal-with-MPI

· 1000*1000 metal plate | 1000*250 for each

· Decomposed python code into 4 processors, allocated an extra row for boundary of each processor to send boundary data back and forth and get a global view of dataset

· Operated python code in MPI inside bridges2, exported final dataset and visualized final stage of heat metal plate using matplotlib of ​​a thermally conductive image

Final image
<img width="562" alt="截屏2023-02-17 12 07 35" src="https://user-images.githubusercontent.com/112505253/219718101-cc1f8e0c-d6de-40a0-aaef-a2bfc38edbf9.png">

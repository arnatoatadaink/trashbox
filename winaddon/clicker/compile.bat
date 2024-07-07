windres -i icon.rc -o icon.o
g++ -std=c++0x main.c icon.o -o main.exe -lgdi32 -finput-charset=UTF-8 -fexec-charset=CP932
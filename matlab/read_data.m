clc;
clear all;
close all;

M = csvread('/home/rs/Programs/city-sensor/serial_plot/save_data/03182021_223014_200hz.csv');
fs = 200;
M_time = timetable(seconds((0:length(M)-1)'/fs), M);

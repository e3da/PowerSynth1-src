function [data_mat] = List2Mat(data_list)
%LIST2MAT Converts PowerSynth numerical lists to MATLAB double arrays.
%   PowerSynth sends over x, y, and z coordinate start and end locations of
%   features as a list of paired values as text. This function converts
%   them to MATLAB doubles compatible with ParaPower formatting.
data_mat = double([data_list(1) data_list(2)]);

end


function [parapower_name] = NameLookUp(ps_name)
%NAMELOOKUP Converts PowerSynth material names to those used in ParaPower.
%   This function is a temporary solution only until the material library
%   linking is completed.
if isempty(ps_name)
    ps_name = 'SiC';
end
ps_mats = {'copper', 'Pb-Sn Solder Alloy', 'MarkeTech AlN 160', 'SiC', 'Aluminum', 'Al_N'};
pp_mats = {'Cu', 'SAC405', 'AlN', 'SiC', 'Al', 'AlN'};
if any(strcmp(ps_mats, ps_name))
    mat_map = containers.Map(ps_mats, pp_mats);
    parapower_name = mat_map(ps_name);
else
    parapower_name = ps_name;
end


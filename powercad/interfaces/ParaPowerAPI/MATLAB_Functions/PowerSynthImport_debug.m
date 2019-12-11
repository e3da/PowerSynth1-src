function [maxtemp, temp_res, model_input] = PowerSynthImport(jsondata, visualize)
% Accepts a JSON text stream when called from PowerSynth and builds up
% the model for ParaPower execution.


%jsondata = fileread(test_model_name);

test_model = jsondecode(jsondata);
%test_model = load('./testoutput.mat');
%base_model = load('./TestProfiles/test1.ppmodel');

for i = 1:numel(test_model.Features)
    % Compare material names (to be removed later).
    test_model.Features(i).Matl = NameLookUp(test_model.Features(i).Matl);
    % Convert PowerSynth coordinate pairs from text to MATLAB doubles then
    % convert units from microns to meters.
    test_model.Features(i).x = List2Mat(test_model.Features(i).x)*1e-6;
    test_model.Features(i).y = List2Mat(test_model.Features(i).y)*1e-6;
    test_model.Features(i).z = List2Mat(test_model.Features(i).z)*1e-6;
end

num_features = numel(test_model.Features);
test_model.Features = reshape(test_model.Features, [1 num_features]);

% Use the example material library.
matlib = load('./PackMats_Update.mat');
base_matlib = matlib.MatLib;
test_model.MatLib = base_matlib;
save('./ImportedPowerSynthModel.mat', 'test_model');
model = FormModel(test_model);
model.ExternalConditions = test_model.ExternalConditions;
model.Features = test_model.Features;
model.Params = test_model.Params;
model.PottingMaterial = 0;
TestCaseModel = model;
save('./TestModel.mat', 'TestCaseModel');


[Tprnt, ModelInput, PHres] = ParaPowerThermal(model);
sz = size(Tprnt);
[maxtemp, ind] = max(Tprnt(:));
model_input = ModelInput;
temp_res = Tprnt;

if visualize == 1
    MI = model;
    Visualize('Thermal Results',MI,'state', Tprnt(:,:,:,2))
end

end
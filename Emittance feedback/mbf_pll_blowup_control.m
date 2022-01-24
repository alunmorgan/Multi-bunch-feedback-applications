function mbf_pll_blowup_control(hemit_target,vemit_target)

validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
p = inputParser;
addRequired(p, 'hemit_target', validScalarPosNum);
addRequired(p, 'vemit_target', validScalarPosNum);
parse(p,hemit_target,vemit_target);

existing_excitation_x = lcaGet('SR23C-DI-TMBF-01:X:NCO2:GAIN_DB_S');
existing_excitation_y = lcaGet('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S');

mbf_pll_setup_blowup('excitation_x',existing_excitation_x,...
    'excitation_y',existing_excitation_y)

slew_rate_limit = 0.2;
low_limit = -78;
while true
    error_x_user = lcaGet('SR23C-DI-TMBF-01:X:PLL:CTRL:STOP:STOP');
    error_x_detector_overflow = lcaGet('SR23C-DI-TMBF-01:X:PLL:CTRL:STOP:DET_OVF');
    error_x_offset = lcaGet('SR23C-DI-TMBF-01:X:PLL:CTRL:STOP:OFFSET_OVF');
    error_x_magnitude = lcaGet('SR23C-DI-TMBF-01:X:PLL:CTRL:STOP:MAG_ERROR');
    error_y_user = lcaGet('SR23C-DI-TMBF-01:Y:PLL:CTRL:STOP:STOP');
    error_y_detector_overflow = lcaGet('SR23C-DI-TMBF-01:Y:PLL:CTRL:STOP:DET_OVF');
    error_y_offset = lcaGet('SR23C-DI-TMBF-01:Y:PLL:CTRL:STOP:OFFSET_OVF');
    error_y_magnitude = lcaGet('SR23C-DI-TMBF-01:Y:PLL:CTRL:STOP:MAG_ERROR');
    if ~strcmp(error_x_detector_overflow{1}, 'Ok') ||...
            ~strcmp(error_x_offset{1}, 'Ok') ||...
            ~strcmp(error_x_magnitude{1}, 'Ok') ||...
            ~strcmp(error_x_user{1}, 'Ok')
        error('Horizontal frequency locked loop has stopped');
    end %if
    if ~strcmp(error_y_detector_overflow{1}, 'Ok') ||...
            ~strcmp(error_y_offset{1}, 'Ok') ||...
            ~strcmp(error_y_magnitude{1}, 'Ok') ||...
            ~strcmp(error_y_user{1}, 'Ok')
        error('Vertical frequency locked loop has stopped');
    end %if
    
    tune_x = lcaGet('SR23C-DI-TMBF-01:X:TUNE:CENTRE:TUNE');
    tune_y = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:CENTRE:TUNE');
    hemit=lcaGet('SR-DI-EMIT-01:HEMIT_MEAN');
    vemit=lcaGet('SR-DI-EMIT-01:VEMIT_MEAN');
    hpower=lcaGet('SR23C-DI-TMBF-01:X:NCO2:GAIN_DB_S');
    vpower=lcaGet('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S');
    % Too much excitation casues the tune value to be lost. The solution is
    % to reduce the exciation value
    if isnan(tune_x)
        lcaPut('SR23C-DI-TMBF-01:X:NCO2:GAIN_DB_S',hpower-0.2);
    else
        herror=log10(hemit/hemit_target);
        if abs(herror) > slew_rate_limit
            herror = sign(herror) * slew_rate_limit;
        end %if
        if hpower-herror > low_limit
            lcaPut('SR23C-DI-TMBF-01:X:NCO2:GAIN_DB_S',hpower-herror);
        end %if
    end %if
    if isnan(tune_y)
        lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S',vpower-0.2);
    else
        verror=log10(vemit/vemit_target);
        if abs(verror) > slew_rate_limit
            verror = sign(verror) * slew_rate_limit;
        end %if
        if vpower - verror > low_limit
            lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S',vpower-verror);
        end %if
    end %if
    
    pause(0.5)
end

function unpacked_data = unpack_old_growdamp_sweeps(requested_data)

ck =1;
for sh = 1:length(requested_data)
    if ~iscell(requested_data{sh}.data)
        unpacked_data{ck} = requested_data{sh};
        ck = ck +1;
    else
        for naw = 1:length(requested_data{sh}.data)
            unpacked_data{ck} = requested_data{sh};
            unpacked_data{ck} = rmfield(unpacked_data{ck}, 'data');
            unpacked_data{ck}.data = requested_data{sh}.data{naw};
            unpacked_data{ck} = rmfield(unpacked_data{ck}, 'data_freq');
            unpacked_data{ck}.data_freq = requested_data{sh}.data_freq{naw};
            if isfield(unpacked_data, 'tune')
                if iscell(unpacked_data.tune)
                    unpacked_data{ck} = rmfield(unpacked_data{ck}, 'tune');
                    unpacked_data{ck}.tune = requested_data{sh}.tune{naw};
                end %if
            end %if
            ck = ck +1;
        end %for

    end %if
end %for

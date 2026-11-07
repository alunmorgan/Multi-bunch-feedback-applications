function scanResults = id_gap_control(varargin)

%% MAIN_ID_GAP_CONTROL.M
% =========================================================================
% Function for controlling Insertion Device (ID) gaps via setIDGap.
% Features:
%   1. Pre-motion initialization: Option to set all IDs to 100% (open) or 0% (closed).
%   2. Sequential Scan: Step ID gaps one by one through 0-20-40-60-80-100-80-60-40-20-0%.
%   3. Random Motion: Move random IDs to random percentages within their limits.
% =========================================================================

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
%% 1. USER CONFIGURATION

% IDs to include in the motion run (default is all 25 IDs)
% ACTIVE_IDS = { ...
%     'I03',  'I04',  'J04',  ...
%     'I06A', 'I06B', 'I07',  'I08',  'I09',  ...
%     'J09',  'I10A', 'I10B', 'I11',  'I13',  ...
%     'J13',  'I14',  'I16',  'I18',  'I19',  ...
%     'I20',  'I21',  'I22',  'I23',  'I24'   ...
%     };
ACTIVE_IDS = { ...
    'I13',  ...
    'J13',  'I14',  'I16',  'I18',  'I19',  ...
    'I20',  'I21',  'I22',  'I23',  'I24'   ...
    };

% --- GENERAL / MONITORING SETTINGS ---
% EPICS PVs to monitor at each step (e.g., beam current). Leave {''} if none.
MONITOR_PVs = {'SR-DI-DCCT-01:SIGNAL';'SR-DI-EMIT-01:VEMIT'; 'SR-DI-EMIT-01:HEMIT';...
    'SR23C-DI-TMBF-01:X:NCO2:GAIN_SCALAR_S'; 'SR23C-DI-TMBF-01:Y:NCO2:GAIN_SCALAR_S';...
    'SR01A-PC-SQUAD-04:I';...
    'SR23C-DI-TMBF-01:X:PLL:NCO:FREQ_S';'SR23C-DI-TMBF-01:X:PLL:NCO:FREQ';...
    'SR23C-DI-TMBF-01:X:PLL:NCO:OFFSET';'SR23C-DI-TMBF-01:X:PLL:FILT:MAG';...
    'SR23C-DI-TMBF-01:X:PLL:FILT:PHASE';...
    'SR23C-DI-TMBF-01:Y:PLL:NCO:FREQ_S';'SR23C-DI-TMBF-01:Y:PLL:NCO:FREQ';...
    'SR23C-DI-TMBF-01:Y:PLL:NCO:OFFSET';'SR23C-DI-TMBF-01:Y:PLL:FILT:MAG';...
    'SR23C-DI-TMBF-01:Y:PLL:FILT:PHASE'}; 

% --- INITIAL STATE OPTION (Pre-movement conditioning) ---
% Options:
%   'open'   -> Set all IDs to 100% (Maximum gap) before starting motion
%   'closed' -> Set all IDs to 0%   (Minimum gap) before starting motion
%   'none'   -> Keep current gaps; do not initialize all IDs
initial_state =  @(x) any(validatestring(x,{'open', 'closed', 'user', 'start','none'}));

% --- MODE 1: SEQUENTIAL STEP-WISE PATTERN ---
% --- MODE 2: RANDOM ID & RANDOM PERCENTAGE MOTION ---
scan_type =  @(x) any(validatestring(x,{'sequential', 'random'}));

% 'continuous' (any % in [0, 100]) or 'discrete' (0, 20, 40, 60, 80, 100%)
random_type =  @(x) any(validatestring(x,{'continuous', 'discrete'}));

valid_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);

addParameter(p, 'active_ids', ACTIVE_IDS);
addParameter(p, 'monitor_pvs', MONITOR_PVs);
addParameter(p, 'initial_id_state', 'closed', initial_state);
addParameter(p, 'scan_mode', 'sequential', scan_type);
addParameter(p, 'step_wait', 10.0, valid_number); % Pause (seconds) after each percentage step or random movement
addParameter(p, 'random_percent_type', 'continuous', random_type);
addParameter(p, 'num_random_moves', 15, valid_number);
parse(p, varargin{:});

%% 2. Parameters settings and lookups for the IDs
[~, lookups] = ID_parameters;

%% 3. PRE-MOTION INITIALIZATION (ALL 100% OPEN OR 0% CLOSED)
% if ~strcmpi(p.Results.initial_id_state, 'none')
%     fprintf('\n>>> [PRE-CONDITIONING] Setting all IDs phases to HORIZONTAL...\n');
%     % Set any phases to horizontal
%     phase_PV = lookups.phases_set(ID);
%     phase_setups = lookups.phases_settings(ID);
%     lcaPutNoWait(phase_PV, phase_setups(1,:)') % The first entry is horizontal
% end %if
switch lower(p.Results.initial_id_state)
    case 'open'
        fprintf('\n>>> [PRE-CONDITIONING] Setting all IDs to 100%% (FULLY OPEN / MAX GAP)...\n');
        for k = 1:numel(p.Results.active_ids)
            id_k = p.Results.active_ids{k};
            maxGap = lookups.gaps_max(id_k);
            gap_pv = lookups.gaps_set(id_k);
            lcaPutNoWait(gap_pv, maxGap)
        end %for
        fprintf('>>> Please check all active IDs are successfully OPENED\n');
        fprintf('>>> Then press any key to continue\n');
        pause
    case 'start'
        fprintf('\n>>> [PRE-CONDITIONING] Setting all IDs to 100%% (HALF OPEN)...\n');
        for k = 1:numel(p.Results.active_ids)
            id_k = p.Results.active_ids{k};
            startGap = lookups.gaps_max(id_k) / 2;
            gap_pv = lookups.gaps_set(id_k);
            lcaPutNoWait(gap_pv, startGap)
        end %for
        fprintf('>>> Please check all active IDs are successfully OPENED\n');
        fprintf('>>> Then press any key to continue\n');
        pause

    case 'closed'
        fprintf('\n>>> [PRE-CONDITIONING] Setting all IDs to 0%% (FULLY CLOSED / MIN GAP)...\n');
        for k = 1:numel(p.Results.active_ids)
            id_k = p.Results.active_ids{k};
            minGap = lookups.gaps_min(id_k);
            gap_pv = lookups.gaps_set(id_k);
            lcaPutNoWait(gap_pv, minGap)
            lcaPutNoWait(lookups.gaps_execute(id_k), 1);
        end %for
        fprintf('>>> Please check all active IDs are successfully CLOSED\n');
        fprintf('>>> Then press any key to continue\n');
        pause
    case 'user'
        fprintf('\n>>> [PRE-CONDITIONING] Setting all IDs to 0%% (USER GAP)...\n');
        for k = 1:numel(p.Results.active_ids)
            id_k = p.Results.active_ids{k};
            userGap = lookups.gaps_user(id_k);
            gap_pv = lookups.gaps_set(id_k);
            lcaPutNoWait(gap_pv, userGap)
        end %for
        fprintf('>>> Please check all active IDs are successfully CLOSED\n');
        fprintf('>>> Then press any key to continue\n');
        pause
    case 'none'
        fprintf('\n>>> [PRE-CONDITIONING] Skipped (leaving current ID positions intact).\n\n');
end %switch

if strcmpi(p.Results.scan_mode, 'sequential')
    %% 4. PATTERN 1: SEQUENTIAL STEP-WISE SCAN (ONE BY ONE)
    fprintf('\n>>> MODE 1 (SEQUENTIAL SCAN).\n');
    %     Determine percentage profile
    if strcmpi(p.Results.initial_id_state, 'open') ||...
        strcmpi(p.Results.initial_id_state, 'user') ||...
        strcmpi(p.Results.initial_id_state, 'start')
        % Start open (100%), close in 20% steps to 0%, then open back to 100%
        pct_steps = [0.80, 0.60, 0.40, 0.20, 0.00, 0.20, 0.40, 0.60, 0.80, 1.00];
    else
        % Start closed (0%), open in 20% steps to 100%, then close back to 0%
        pct_steps = [0.20, 0.40, 0.60, 0.80, 1.00, 0.80, 0.60, 0.40, 0.20, 0.00];
        % change to 50% max
        pct_steps = pct_steps /2;
    end %if

    for k = 1:numel(p.Results.active_ids)
        currID = p.Results.active_ids{k};
        minGap = lookups.gaps_min(currID);
        maxGap = lookups.gaps_max(currID);
        gapRange = maxGap - minGap;

        % Convert percentage trajectory to physical gap values (mm)
        % Formula: Gap = MinGap + Percentage * (MaxGap - MinGap)
        targetGaps = minGap + pct_steps .* gapRange;

        fprintf('\n--- Moving ID: %s (%d/%d) ---\n', currID, k, numel(p.Results.active_ids));
        fprintf('    Min Gap: %.3f mm | Max Gap: %.3f mm\n', minGap, maxGap);
        fprintf('    Trajectory Steps (%d points):\n    [', numel(targetGaps));
        fprintf('%.2f ', targetGaps);
        fprintf('] mm\n');

        % Call setIDGap with the trajectory vector
        [monitored_pvs, scanResults.sequential.(currID).gapscan] = setIDGap(currID, targetGaps,...
            p.Results.monitor_pvs, p.Results.step_wait);
        % Saving a file each time an ID completes as the full scan will take a
        % long time and something is likely to go wrong requiring a restart.
        save(strcat('~/gap_scan', datestr(datetime), '.mat'), 'scanResults',"monitored_pvs")
    end %for
    fprintf('\n>>> SEQUENTIAL STEP-WISE SCAN COMPLETED FOR ALL IDS.\n\n');
elseif strcmpi(p.Results.scan_mode, 'random')
    %% 5. PATTERN 2: RANDOM ID & RANDOM PERCENTAGE MOTION

    fprintf('Total Random Steps to perform: %d\n', p.Results.num_random_moves);

    scanResults.randomLog = cell(p.Results.num_random_moves, 5); % {Step, ID, Pct, TargetGap, MonitorResult}

    for m = 1:p.Results.num_random_moves
        % 1. Pick a random ID from p.Results.active_ids
        randIDIdx = randi(numel(p.Results.active_ids));
        selectedID = p.Results.active_ids{randIDIdx};

        % 2. Determine random percentage (0% to 100%)
        if strcmpi(p.Results.random_percent_type, 'discrete')
            discreteOptions = [0.0, 0.20, 0.40, 0.60, 0.80, 1.00];
            randPct = discreteOptions(randi(numel(discreteOptions)));
        else
            randPct = rand(); % Continuous random in [0.0, 1.0]
        end %if

        % 3. Calculate target gap in mm
        minGap = gaps_min(selectedID);
        maxGap = gaps_max(selectedID);
        targetGap = minGap + randPct * (maxGap - minGap);

        fprintf('  [Random Move %d/%d] ID: %s | Pct: %5.1f%% | Target Gap: %.4f mm\n', ...
            m, p.Results.num_random_moves, selectedID, randPct * 100, targetGap);

        % 4. Call setIDGap for this single random target
        res = setIDGap(selectedID, targetGap, p.Results.monitor_pvs, p.Results.step_wait);

        % Log record
        scanResults.randomLog{m, 1} = m;
        scanResults.randomLog{m, 2} = selectedID;
        scanResults.randomLog{m, 3} = randPct * 100;
        scanResults.randomLog{m, 4} = targetGap;
        scanResults.randomLog{m, 5} = res;
    end %for
    save(strcat('~/gap_scan', datestr(datetime), '.mat'), scanResults)
    fprintf('\n>>> RANDOM ID MOTION COMPLETED.\n\n');
end %if

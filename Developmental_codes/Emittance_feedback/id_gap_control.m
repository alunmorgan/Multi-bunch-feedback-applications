%% MAIN_ID_GAP_CONTROL.M
% =========================================================================
% Script for controlling Insertion Device (ID) gaps via setIDGap.
% Features:
%   1. Pre-motion initialization: Option to set all IDs to 100% (open) or 0% (closed).
%   2. Sequential Scan: Step ID gaps one by one through 0-20-40-60-80-100-80-60-40-20-0%.
%   3. Random Motion: Move random IDs to random percentages within their limits.
%   4. Separate boolean flags to independently enable/disable Sequential and Random modes.
% =========================================================================
clear; clc;
%% 1. USER CONFIGURATION
% --- INITIAL STATE OPTION (Pre-movement conditioning) ---
% Options:
%   'open'   -> Set all IDs to 100% (Maximum gap) before starting motion
%   'closed' -> Set all IDs to 0%   (Minimum gap) before starting motion
%   'none'   -> Keep current gaps; do not initialize all IDs
INITIAL_ID_STATE = 'open'; % 'open' | 'closed' | 'none'
SCAN_MODE = 'sequential'; % or 'random'
% --- MODE 1: SEQUENTIAL STEP-WISE PATTERN (True/False toggle) ---
SCAN_STEP_WAIT         = 10.0;   % Pause (seconds) at each percentage step

% --- MODE 2: RANDOM ID & RANDOM PERCENTAGE MOTION (True/False toggle) ---
NUM_RANDOM_MOVES       = 15;    % Total number of random movements to perform
RANDOM_STEP_WAIT       = 10;   % Pause (seconds) after each random movement
RANDOM_PERCENT_TYPE    = 'continuous'; % 'continuous' (any % in [0, 100]) or 'discrete' (0, 20, 40, 60, 80, 100%)

% --- GENERAL / MONITORING SETTINGS ---
% EPICS PV to monitor at each step (e.g., beam current). Leave '' if none.
MONITOR_PV = {'SR-DI-DCCT-01:SIGNAL';'SR-DI-EMIT-01:VEMIT'; 'SR-DI-EMIT-01:HEMIT';...
    'SR23C-DI-TMBF-01:X:NCO2:GAIN_SCALAR_S'; 'SR23C-DI-TMBF-01:Y:NCO2:GAIN_SCALAR_S';...
    'SR01A-PC-SQUAD-04:I'}; %% We can put many PVs if we want to save the data

% IDs to include in the motion run (default is all 25 IDs)
ACTIVE_IDS = { ...
    'I02',  'J02',  'I03',  'I04',  'J04',  'I05',  ...
    'I06A', 'I06B', 'I07',  'I08',  'I09',  ...
    'J09',  'I10A', 'I10B', 'I11',  'I13',  ...
    'J13',  'I14',  'I16',  'I18',  'I19',  ...
    'I20',  'I21',  'I22',  'I23',  'I24'   ...
    };
[params] = ID_parameters;

%% 2. ID MINIMUM AND MAXIMUM GAP LIMITS (From ID Control Screen)
% and PVs to set gaps.
gaps_max = containers.Map(params.IDs, params.gaps_max);
gaps_min = containers.Map(params.IDs, params.gaps_min);

gap_sets = containers.Map(params.IDs, params.gap_sets);

%% 3. PRE-MOTION INITIALIZATION (ALL 100% OPEN OR 0% CLOSED)
switch lower(INITIAL_ID_STATE)
    case 'open'
        fprintf('\n>>> [PRE-CONDITIONING] Setting all IDs to 100%% (FULLY OPEN / MAX GAP)...\n');
        for k = 1:numel(ACTIVE_IDS)
            id_k = ACTIVE_IDS{k};
            maxGap = gaps_max(id_k);
            gap_pv = gap_sets(id_k);
            lcaPutNoWait(gap_pv, maxGap)
        end %for
        fprintf('>>> Please check all active IDs are successfully OPENED\n');
        fprintf('>>> Then press any key to continue\n');
        pause

    case 'closed'
        fprintf('\n>>> [PRE-CONDITIONING] Setting all IDs to 0%% (FULLY CLOSED / MIN GAP)...\n');
        for k = 1:numel(ACTIVE_IDS)
            id_k = ACTIVE_IDS{k};
            minGap = gaps_min(id_k);
            gap_pv = gap_sets(id_k);
            lcaPutNoWait(gap_pv, minGap)
        end
        fprintf('>>> Please check all active IDs are successfully CLOSED\n');
        fprintf('>>> Then press any key to continue\n');
        pause

    case 'none'
        fprintf('\n>>> [PRE-CONDITIONING] Skipped (leaving current ID positions intact).\n\n');

    otherwise
        error('Invalid INITIAL_ID_STATE "%s". Choose ''open'', ''closed'', or ''none''.', INITIAL_ID_STATE);
end

if strcmpi(SCAN_MODE, 'sequential')
    %% 4. PATTERN 1: SEQUENTIAL STEP-WISE SCAN (ONE BY ONE)
    fprintf('\n>>> MODE 1 (SEQUENTIAL SCAN).\n');
    %     Determine percentage profile
    if strcmpi(INITIAL_ID_STATE, 'open')
        % Start open (100%), close in 20% steps to 0%, then open back to 100%
        pct_steps = [0.80, 0.60, 0.40, 0.20, 0.00, 0.20, 0.40, 0.60, 0.80, 1.00];
    else
        % Start closed (0%), open in 20% steps to 100%, then close back to 0%
        pct_steps = [0.20, 0.40, 0.60, 0.80, 1.00, 0.80, 0.60, 0.40, 0.20, 0.00];
    end %if

    for k = 6:numel(ACTIVE_IDS)
        currID = ACTIVE_IDS{k};
        minGap = gaps_min(currID);
        maxGap = gaps_max(currID);
        gapRange = maxGap - minGap;

        % Convert percentage trajectory to physical gap values (mm)
        % Formula: Gap = MinGap + Percentage * (MaxGap - MinGap)
        targetGaps = minGap + pct_steps .* gapRange;

        fprintf('\n--- Moving ID: %s (%d/%d) ---\n', currID, k, numel(ACTIVE_IDS));
        fprintf('    Min Gap: %.3f mm | Max Gap: %.3f mm\n', minGap, maxGap);
        fprintf('    Trajectory Steps (%d points):\n    [', numel(targetGaps));
        fprintf('%.2f ', targetGaps);
        fprintf('] mm\n');

        % Call setIDGap with the trajectory vector
        scanResults.(currID).gapscan = setIDGap(currID, targetGaps, MONITOR_PV, SCAN_STEP_WAIT);
    end %for

    fprintf('\n>>> SEQUENTIAL STEP-WISE SCAN COMPLETED FOR ALL IDS.\n\n');
elseif strcmpi(SCAN_MODE, 'random')
    %% 5. PATTERN 2: RANDOM ID & RANDOM PERCENTAGE MOTION

    fprintf('Total Random Steps to perform: %d\n', NUM_RANDOM_MOVES);

    randomLog = cell(NUM_RANDOM_MOVES, 5); % {Step, ID, Pct, TargetGap, MonitorResult}

    for m = 1:NUM_RANDOM_MOVES
        % 1. Pick a random ID from ACTIVE_IDS
        randIDIdx = randi(numel(ACTIVE_IDS));
        selectedID = ACTIVE_IDS{randIDIdx};

        % 2. Determine random percentage (0% to 100%)
        if strcmpi(RANDOM_PERCENT_TYPE, 'discrete')
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
            m, NUM_RANDOM_MOVES, selectedID, randPct * 100, targetGap);

        % 4. Call setIDGap for this single random target
        res = setIDGap(selectedID, targetGap, MONITOR_PV, RANDOM_STEP_WAIT);

        % Log record
        randomLog{m, 1} = m;
        randomLog{m, 2} = selectedID;
        randomLog{m, 3} = randPct * 100;
        randomLog{m, 4} = targetGap;
        randomLog{m, 5} = res;
    end %for

    fprintf('\n>>> RANDOM ID MOTION COMPLETED.\n\n');
else
    fprintf('\n>>> Invalid SCAN_MODE should be sequential or random\n\n');
end %if

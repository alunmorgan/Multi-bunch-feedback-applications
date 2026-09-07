function generate_emittance_database(select_axis, log_data_file)
% GENERATE_EMITTANCE_DATABASE Builds and formats DD-PID database from recorded data
%
% Inputs:
%   log_data_file : Path to .mat file containing:
%                   - r_log (target emittance values)
%                   - y_log (measured emittance values)
%                   - u_log (excitation power gain values)
%   output_db_file: Path to save database (e.g. 'emittance_dd_database.mat')
%   initial_PID   : [Kp, Ki, Kd] baseline PID gains (e.g. [1e-4, 5e-5, 2e-5])
%
% Example:
%   generate_emittance_database('emittance_log_data.mat', 'emittance_dd_database.mat', [1e-4, 5e-5, 2e-5]);
if nargin < 1 || isempty(log_data_file)
    log_data_file = char(strcat('emittance_log_data_',select_axis,'.mat'));
end
% if nargin < 2 || isempty(output_db_file)
    output_db_file = char(strcat('emittance_dd_database_',select_axis,'.mat'));
% end
% if nargin < 3 || isempty(initial_PID)
    initial_PID = [1e-4, 5e-5, 2e-5]; % Default [Kp, Ki, Kd]
% end
% 1. Load the recorded log file
if ~isfile(log_data_file)
    error('File %s not found! Run data collection first.', log_data_file);
end
raw = load(log_data_file);
r = raw.r_log(:);  % Target emittance (pm rad or nm rad)
y = raw.y_log(:);  % Measured emittance (emit)
u = raw.u_log(:);  % Control power (gain_scalar)
N = length(y);
fprintf('Processing %d operating data points from %s...\n', N, log_data_file);
% 2. Construct Information Vectors phi_bar(j) (Eq. 6 of paper)
% Format: phi_bar(j) = [r(j+1), r(j), y(j), y(j-1), u(j-1)]
ny = 2; nu = 2;
L = ny + nu + 1; % 5 elements
DB_phi = zeros(N, L);
for t = 3:N-1
    r_lead = r(min(t+1, N));
    r_curr = r(t);
    y_hist = [y(t), y(t-1)];
    u_hist = u(t-1);
    DB_phi(t, :) = [r_lead, r_curr, y_hist, u_hist];
end
DB_phi(1:2, :) = repmat(DB_phi(3, :), 2, 1);
DB_phi(N, :) = DB_phi(N-1, :);
% 3. Initialize PID Gain Database K(j) (Eq. 7 of paper)
DB_K = repmat(initial_PID(:)', N, 1);
% 4. Compute normalization bounds for distance calculation (Eq. 8)
phi_max = max(DB_phi, [], 1);
phi_min = min(DB_phi, [], 1);
% 5. Save the structured database file
save(output_db_file, 'DB_phi', 'DB_K', 'phi_max', 'phi_min', 'initial_PID', 'r', 'y', 'u');
fprintf('Database successfully saved to: %s\n', output_db_file);
fprintf('Contains:\n');
fprintf('  - DB_phi : [%d x %d] Information vectors [r(t+1), r(t), y(t), y(t-1), u(t-1)]\n', size(DB_phi,1), size(DB_phi,2));
fprintf('  - DB_K   : [%d x 3] PID Gains [Kp, Ki, Kd]\n', size(DB_K,1));
fprintf('  - phi_max, phi_min : Normalization ranges\n\n');
end
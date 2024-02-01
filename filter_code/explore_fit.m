% Tool for exploring FIR fit
function explore_fit
    fig = figure('MenuBar', 'none', 'Toolbar', 'figure', ...
        'Position', [0 0 900 600]);

    h_pos = 10; v_pos = 20;
    h = {};
    h.alpha = control(h_pos, v_pos, 'edit', [1e-5 1e-3], 100, 'Range of alpha');
    h.beta = control(h_pos, v_pos, 'edit', 1e-3, 100, 'Beta');
    h.tune = control(h_pos, v_pos, 'edit', 0.2, 120, 'Select tune');
    h.delta = control(h_pos, v_pos, 'edit', 0.05, 60, 'Delta tune');
    h.delay = control(h_pos, v_pos, 'edit', 1, 60, 'Filter delay at tune');
    h.phase = control(h_pos, v_pos, 'edit', 0, 120, 'Phase offset');
    h.N = control(h_pos, v_pos, 'edit', 10, 60, 'Points in filter');

    guidata(fig, h);
    redraw(fig, 0);
end


% Places control with specified style, value, width  and tooltip.
function result = control(h_pos, v_pos, style, value, width, tooltip, varargin)
    position = [h_pos v_pos width 20];
    h_pos = h_pos + width + 5;
    result = uicontrol( ...
        'Style', style, 'String', num2str(value), 'Position', position, ...
        'TooltipString', tooltip, 'Callback', @redraw, varargin{:});
end


function redraw(fig)
    h = guidata(fig);
    alpha = get_value(h.alpha);
    beta = get_value(h.beta);
    tune = get_value(h.tune);
    delta = get_value(h.delta);
    delay = get_value(h.delay);
    phase = get_value(h.phase);
    N = get_value(h.N);

    test_fit(tune, delta, delay, phase, N, alpha, beta);
end

function value = get_value(control)
    value = str2num(get(control, 'String'));
end

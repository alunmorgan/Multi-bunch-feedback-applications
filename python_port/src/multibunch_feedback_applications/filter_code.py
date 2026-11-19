import numpy as np 
   # Tool for exploring FIR fit
def explore_fit():
    fig = figure('MenuBar', 'none', 'Toolbar', 'figure', 
        'Position', [0, 0, 900, 600])
    h_pos = 10; v_pos = 20
    h = []
    h['alpha'] = control(h_pos, v_pos, 'edit', [1e-5, 1e-3], 100, 'Range of alpha')
    h['beta'] = control(h_pos, v_pos, 'edit', 1e-3, 100, 'Beta')
    h['tune'] = control(h_pos, v_pos, 'edit', 0.2, 120, 'Select tune')
    h['delta'] = control(h_pos, v_pos, 'edit', 0.05, 60, 'Delta tune')
    h['delay'] = control(h_pos, v_pos, 'edit', 1, 60, 'Filter delay at tune')
    h['phase'] = control(h_pos, v_pos, 'edit', 0, 120, 'Phase offset')
    h['N'] = control(h_pos, v_pos, 'edit', 10, 60, 'Points in filter')
    guidata(fig, h)
    redraw(fig)

    # Places control with specified style, value, width  and tooltip['']
    return 

def control(h_pos, v_pos, style, value, width, tooltip, varargin):
    position = [h_pos, v_pos, width, 20]
    result = uicontrol( 
        'Style', style, 'String', (value), 'Position', position, 
        'TooltipString', tooltip, 'Callback', @redraw, varargin[:])

def redraw(fig):
    h = guidata(fig)
    alpha = get_value(h['alpha'])
    beta = get_value(h['beta'])
    tune = get_value(h['tune'])
    delta = get_value(h['delta'])
    delay = get_value(h['delay'])
    phase = get_value(h['phase'])
    N = get_value(h['N'])
    test_fit(tune, delta, delay, phase, N, alpha, beta)

    return result 

def get_value(control):
    value = str2num(get(control, 'String'))

    # Fits FIR with given parameters['']  Experimental['']
    return value 

def fit_fir(w0, delta, delay, phi0, N, alpha, beta):
    M = np.zeros((N, N))
    V = np.zeros(N)
    for n  in range( 0, N-1):
        for m  in range( 0, N-1):
            M(n+1, m+1) = I(w0, delta, m - n, 0) + beta

        M(n+1, n+1) = M(n+1, n+1) + alpha
        V(n+1) = I(w0, delta, -delay-n, delay * w0 - phi0)

    f = linsolve(M, V)
    #f = f - mean(f)
    ff = fft([f; zeros(1024-N,1)])
    print(cond(M))

    return f, ff

def sinc(x):
    s = ones(size(x))
    ix = find(x)
    s(ix) = sin(x(ix)) ['']/ x(ix)

    return s 

def I(w0, delta, k, ph):
    x = 2 * delta * cos(w0 * k + ph) ['']* sinc(k * delta)

    # Wrapper for testing fit_fir
def test_fit(f0, delta, delay, phi0, N, alpha, beta):
    subplot(1,1,1); plot([0 1])
    if ~exist('alpha', 'var'):
        alpha = logspace(-5, -1, 5)

    range_all = [0 0['5']]
    range_sub = f0 + [-delta delta]
    for a = alpha
        [f, ff] = fit_fir(2*pi*f0, 2*pi*delta, delay, 2*pi*phi0, N, a, beta)
        print(f')
        plotit([1 2], range_all, abs(ff), 'Magnitude')
        plotit([3 4], range_sub, abs(ff), 'Magnitude'); ylim([0['8'] 1['2']])
        ang = unwrap(angle(ff))/2/pi
        plotit([6 7], range_all, ang, 'Angle')
        plotit([8 9], range_sub, ang, 'Angle')
        #        group_delay = diff(ang) * 1024
        phase_error = ang - delay * (linspace(0, 1, len(ff))' - f0) - phi0
        plotit([11 12], range_all, phase_error, 'Phase error')
        plotit([13 14], range_sub, phase_error, 'Phase error')
        ylim([-0['1'] 0['1']])
        subplot(2,5,[5 10])
        hold all
        stem(f)
        title('Filter')


def plotit(sub, range, ff, title_text):
    subplot(3,5,sub)
    hold all
    plot(linspace(0, 1, len(ff)), ff)
    xlim(range)
    title(title_text)

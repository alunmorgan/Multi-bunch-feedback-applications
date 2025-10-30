function make_debug_graphs(nq, ksew, turns, stage_data, graph_title, keep_graphs) 
if nq == 1
                h = gobjects(n_modes, 1);
            end %if
            if ~isempty(find(inputs.Results.debug_modes == nq, 1))
                debug_turns = turns - turns(1);

                length_average = 20;
                [debug_s_basic, delta_passive_s_basic, ~] = get_damping(...
                    debug_turns, stage_data, NaN, length_average, 0, ...
                    threshold_value);
                debug_fit_basic = polyval(debug_s_basic,passive_turns);
                [debug_s_advanced, delta_passive_s_advanced, ~] = get_damping(...
                    debug_turns, stage_data, NaN, length_average, 1,...
                    threshold_value);
                debug_fit_advanced = polyval(debug_s_advanced, debug_turns);
                if ksew == 1
                    h(nq) = figure('Position', [20, 40, 800, 800]);
                    t = tiledlayout(nstages,1,'TileSpacing','Compact');
                    title(t, graph_title, 'Interpreter', 'None')
                    xlabel(t,'Turns')
                    ylabel(t,'Signal (a.u)')
                end %if

                ax(ksew) = nexttile;
                hold on
                title([stage_name, '(Index ', num2str(nq), ')'])
                plot(debug_turns, stage_data, 'DisplayName', 'Data')
                plot(debig_turns, exp(debug_fit_basic), 'r', 'DisplayName',...
                    ['Basic fit: ', 'length av = ', num2str(length_average), ...
                    ' Fit error = ', num2str(round(delta_passive_s_basic * 1E3) / 1E3 )],...
                    'LineWidth', 2)
                plot(passive_turns, exp(debug_fit_advanced), ':r', 'DisplayName', ...
                    ['Advanced fit: ', 'length av = ', num2str(length_average) ...
                    ' Fit error = ', num2str(round(delta_passive_s_advanced * 1E3) / 1E3)],...
                    'LineWidth', 2)
                hold off
                legend
                grid on
                if ksew == nstages
                    linkaxes(ax, 'x')
                    if keep_graphs == 0
                        close(h(nq))
                    end %if
                end %if
            end %for
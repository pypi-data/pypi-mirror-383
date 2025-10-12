// HKJC Race Info - Trade Calculator
const TradeCalculator = {
    state: new Map(),
    
    getState(raceNum) {
        if (!this.state.has(raceNum)) {
            this.state.set(raceNum, {
                excludedRunners: new Set(),
                plaCover: new Set(),
                qplBanker: '1',
                qplCover: new Set(),
                qplFilter: false,
                plaParetoController: null,
                qplParetoController: null
            });
        }
        return this.state.get(raceNum);
    },
    
    showLoadingIndicator(plotContainer) {
        plotContainer.innerHTML = `<div style="text-align: center; padding: 60px 20px; color: #667eea;">
            <div style="font-size: 1.2em; margin-bottom: 10px;">⏳ Loading Pareto Frontier...</div>
            <div style="font-size: 0.9em; color: #999;">Computing optimal trade combinations</div>
        </div>`;
    },
    
    showErrorIndicator(plotContainer) {
        plotContainer.innerHTML = '<div style="text-align: center; padding: 20px; color: #e53e3e;">Error loading Pareto data</div>';
    },
    
    showTab(raceNum, tabName) {
        const validRaceNum = Utils.validateRaceNum(raceNum);
        const raceContent = Utils.$(`#race-${validRaceNum}`);
        if (!raceContent) return;
        
        this.updateTabButtons(raceContent, tabName);
        this.updateTabContent(raceContent, validRaceNum, tabName);
        this.syncExcludeButtons(validRaceNum, tabName);
        this.loadParetoForTab(validRaceNum, tabName);
    },
    
    updateTabButtons(raceContent, tabName) {
        Utils.removeClass(Utils.$$('.trade-tab-btn', raceContent), 'active');
        const tabTextMap = { 'pla': 'PLA', 'qpl': 'QPL' };
        const activeTabBtn = Utils.$$('.trade-tab-btn', raceContent)
            .find(btn => btn.textContent.trim() === tabTextMap[tabName]);
        if (activeTabBtn) Utils.addClass(activeTabBtn, 'active');
    },
    
    updateTabContent(raceContent, raceNum, tabName) {
        Utils.removeClass(Utils.$$('.trade-tab-content', raceContent), 'active');
        Utils.addClass(Utils.$(`#trade-${tabName}-${raceNum}`), 'active');
    },
    
    syncExcludeButtons(raceNum, tabName) {
        const state = this.getState(raceNum);
        const excludeButtons = Utils.$$(`#${tabName}-pareto-exclude-${raceNum} .runner-select-btn`);
        
        excludeButtons.forEach(btn => {
            const runnerNo = btn.dataset.runner;
            if (state.excludedRunners.has(runnerNo)) {
                Utils.addClass(btn, 'selected');
            } else {
                Utils.removeClass(btn, 'selected');
            }
        });
    },
    
    loadParetoForTab(raceNum, tabName) {
        if (tabName === 'pla') {
            this.loadPLAParetoData(raceNum);
        } else if (tabName === 'qpl') {
            this.loadQPLParetoData(raceNum);
        }
    },
    
    toggleSetMember(raceNum, set, selector, runnerNo, reloadCallback = null) {
        const btn = Utils.$(selector);
        
        if (set.has(runnerNo)) {
            set.delete(runnerNo);
            Utils.removeClass(btn, 'selected');
        } else {
            set.add(runnerNo);
            Utils.addClass(btn, 'selected');
        }
        
        if (reloadCallback) reloadCallback();
    },
    
    toggleParetoExclude(raceNum, type, runnerNo) {
        const validRaceNum = Utils.validateRaceNum(raceNum);
        const state = this.getState(validRaceNum);
        
        if (state.excludedRunners.has(runnerNo)) {
            state.excludedRunners.delete(runnerNo);
        } else {
            state.excludedRunners.add(runnerNo);
        }
        
        this.updateExcludeButtonsForRunner(validRaceNum, runnerNo);
        
        const activeRace = Utils.$('.race-content.active');
        if (activeRace && activeRace.id === `race-${validRaceNum}`) {
            const activeTab = Utils.$('.trade-tab-content.active', activeRace);
            if (activeTab?.id === `trade-pla-${validRaceNum}`) {
                this.loadPLAParetoData(validRaceNum);
            } else if (activeTab?.id === `trade-qpl-${validRaceNum}`) {
                this.loadQPLParetoData(validRaceNum);
            }
        }
    },
    
    updateExcludeButtonsForRunner(raceNum, runnerNo) {
        const state = this.getState(raceNum);
        const isExcluded = state.excludedRunners.has(runnerNo);
        
        ['pla', 'qpl'].forEach(type => {
            const btn = Utils.$(`#${type}-pareto-exclude-${raceNum} [data-runner="${runnerNo}"]`);
            if (btn) {
                if (isExcluded) {
                    Utils.addClass(btn, 'selected');
                } else {
                    Utils.removeClass(btn, 'selected');
                }
            }
        });
    },
    
    toggleCover(raceNum, type, runnerNo) {
        const validRaceNum = Utils.validateRaceNum(raceNum);
        const state = this.getState(validRaceNum);
        const coverSet = type === 'pla' ? state.plaCover : state.qplCover;
        const selector = `#${type}-cover-${validRaceNum} [data-runner="${runnerNo}"]`;
        
        this.toggleSetMember(validRaceNum, coverSet, selector, runnerNo);
    },
    
    selectBanker(raceNum, runnerNo) {
        const validRaceNum = Utils.validateRaceNum(raceNum);
        const state = this.getState(validRaceNum);
        
        Utils.removeClass(Utils.$$(`#qpl-banker-${validRaceNum} .runner-radio-btn`), 'selected');
        
        const btn = Utils.$(`#qpl-banker-${validRaceNum} [data-runner="${runnerNo}"]`);
        state.qplBanker = runnerNo;
        Utils.addClass(btn, 'selected');
        
        this.loadQPLParetoData(validRaceNum);
    },
    
    toggleFilter(raceNum) {
        const validRaceNum = Utils.validateRaceNum(raceNum);
        const state = this.getState(validRaceNum);
        const btn = Utils.$(`#qpl-filter-${validRaceNum}`);
        
        state.qplFilter = !state.qplFilter;
        btn.dataset.filter = state.qplFilter.toString();
        btn.textContent = state.qplFilter ? 'ON' : 'OFF';
        
        this.loadQPLParetoData(validRaceNum);
    },
    
    async loadParetoData(raceNum, type) {
        const validRaceNum = Utils.validateRaceNum(raceNum);
        const state = this.getState(validRaceNum);
        const controllerKey = `${type}ParetoController`;
        
        if (state[controllerKey]) {
            state[controllerKey].abort();
        }
        
        state[controllerKey] = new AbortController();
        
        try {
            const plotContainer = Utils.$(`#${type}-pareto-plot-${raceNum}`);
            if (!plotContainer) return;
            
            this.showLoadingIndicator(plotContainer);
            
            const exclude = Array.from(state.excludedRunners)
                .sort((a, b) => parseInt(a) - parseInt(b))
                .join(',');
            
            let data;
            if (type === 'pla') {
                data = await API.fetchParetoData(validRaceNum, exclude, state[controllerKey].signal);
            } else {
                const banker = state.qplBanker || '1';
                const filter = state.qplFilter;
                data = await API.fetchQParetoData(validRaceNum, banker, exclude, filter, state[controllerKey].signal);
            }
            
            this.drawParetoPlot(validRaceNum, type, data);
        } catch (error) {
            if (error.name === 'AbortError') {
                Utils.log(`${type.toUpperCase()} Pareto request cancelled for race ${raceNum}`);
                return;
            }
            
            console.error(`Error loading ${type.toUpperCase()} Pareto data for race ${raceNum}:`, error);
            const plotContainer = Utils.$(`#${type}-pareto-plot-${raceNum}`);
            if (plotContainer) this.showErrorIndicator(plotContainer);
        }
    },
    
    async loadPLAParetoData(raceNum) {
        return this.loadParetoData(raceNum, 'pla');
    },
    
    async loadQPLParetoData(raceNum) {
        return this.loadParetoData(raceNum, 'qpl');
    },
    
    async calculatePLA(raceNum) {
        try {
            const validRaceNum = Utils.validateRaceNum(raceNum);
            const state = this.getState(validRaceNum);
            
            if (state.plaCover.size === 0) {
                alert('Please select at least one runner to cover');
                return;
            }
            
            const cover = Array.from(state.plaCover)
                .sort((a, b) => parseInt(a) - parseInt(b))
                .join(',');
            const data = await API.fetchPLAData(validRaceNum, cover);
            this.updateMetrics(validRaceNum, 'pla', data);
        } catch (error) {
            console.error(`Error calculating PLA for race ${raceNum}:`, error);
            alert('Error calculating PLA. Please try again.');
        }
    },
    
    async calculateQPL(raceNum) {
        try {
            const validRaceNum = Utils.validateRaceNum(raceNum);
            const state = this.getState(validRaceNum);
            
            if (!state.qplBanker) {
                alert('Please select a banker');
                return;
            }
            
            if (state.qplCover.size === 0) {
                alert('Please select at least one runner to cover');
                return;
            }
            
            const cover = Array.from(state.qplCover)
                .sort((a, b) => parseInt(a) - parseInt(b))
                .join(',');
            const data = await API.fetchQPLData(validRaceNum, state.qplBanker, cover, state.qplFilter);
            this.updateMetrics(validRaceNum, 'qpl', data);
        } catch (error) {
            console.error(`Error calculating QPL for race ${raceNum}:`, error);
            alert('Error calculating QPL. Please try again.');
        }
    },
    
    updateMetrics(raceNum, type, data) {
        const metricsContainer = Utils.$(`#${type}-metrics-${raceNum}`);
        if (!metricsContainer) return;
        
        const metrics = [
            data.Covered?.length || 0,
            data.WinProb !== undefined ? `${(data.WinProb * 100).toFixed(2)}%` : '-',
            data.ExpValue !== undefined ? data.ExpValue.toFixed(2) : '-',
            data.AvgOdds !== undefined ? data.AvgOdds.toFixed(2) : '-'
        ];
        
        const cards = Utils.$$('.metric-card', metricsContainer);
        metrics.forEach((value, i) => {
            const valueEl = Utils.$('.metric-value', cards[i]);
            if (valueEl) valueEl.textContent = value;
        });
    },
    
    drawParetoPlot(raceNum, type, data) {
        const plotContainer = Utils.$(`#${type}-pareto-plot-${raceNum}`);
        if (!plotContainer) return;
        
        if (!data || data.length === 0) {
            plotContainer.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;">No Pareto trade</div>';
            return;
        }
        
        const groupedByCost = data.reduce((acc, trade) => {
            const cost = trade.Covered.length;
            if (!acc[cost]) acc[cost] = [];
            acc[cost].push(trade);
            return acc;
        }, {});
        
        const traces = Object.keys(groupedByCost)
            .sort((a, b) => parseInt(a) - parseInt(b))
            .map(cost => {
                const trades = groupedByCost[cost];
                return {
                    x: trades.map(t => t.WinProb),
                    y: trades.map(t => t.ExpValue),
                    mode: 'markers',
                    type: 'scatter',
                    name: `Cost ${cost}`,
                    marker: { size: 8, line: { width: 1, color: 'white' } },
                    text: trades.map(t => 
                        `Cost: ${cost}<br>Covered: [${t.Covered.join(', ')}]<br>` +
                        `Win Prob: ${t.WinProb.toFixed(2)}%<br>Exp Value: ${t.ExpValue.toFixed(2)}<br>` +
                        `Avg Odds: ${t.AvgOdds.toFixed(2)}`
                    ),
                    hovertemplate: '%{text}<extra></extra>'
                };
            });
        
        const isMobile = window.innerWidth <= 768;
        const layout = {
            xaxis: { title: 'Win Probability (%)' },
            yaxis: { title: 'Expected Value' },
            hovermode: 'closest',
            margin: { l: 60, r: 20, t: isMobile ? 60 : 80, b: 50 },
            height: isMobile ? 300 : 400,
            showlegend: true,
            legend: { 
                orientation: 'h',
                x: 0.5,
                xanchor: 'center',
                y: isMobile ? 1.18 : 1.15,
                yanchor: 'top',
                font: { size: isMobile ? 9 : 11 }
            },
            plot_bgcolor: '#fafafa',
            paper_bgcolor: 'white'
        };
        
        Plotly.newPlot(plotContainer, traces, layout, { responsive: true, displayModeBar: false });
    },
    
    async updateParetoForOddsChange(raceNum) {
        const activeRace = Utils.$('.race-content.active');
        if (!activeRace || activeRace.id !== `race-${raceNum}`) return;
        
        const activeTab = Utils.$('.trade-tab-content.active', activeRace);
        if (activeTab?.id === `trade-pla-${raceNum}`) {
            await this.loadPLAParetoData(raceNum);
        } else if (activeTab?.id === `trade-qpl-${raceNum}`) {
            await this.loadQPLParetoData(raceNum);
        }
    },
    
    initAll() {
        Utils.$$('.race-content').forEach(raceContent => {
            const raceNum = raceContent.id.replace('race-', '');
            this.getState(raceNum);
            
            const bankerBtn = Utils.$(`#qpl-banker-${raceNum} [data-runner="1"]`);
            if (bankerBtn) Utils.addClass(bankerBtn, 'selected');
            
            this.syncExcludeButtons(raceNum, 'pla');
            this.syncExcludeButtons(raceNum, 'qpl');
        });
        
        const activeRace = Utils.$('.race-content.active');
        if (activeRace) {
            const raceNum = activeRace.id.replace('race-', '');
            this.loadPLAParetoData(raceNum);
        }
    }
};


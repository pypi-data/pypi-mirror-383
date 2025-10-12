// HKJC Race Info - Race UI & Visualization
const PreferredHighlight = {
    columns: [
        { name: 'draw', index: 2, check: v => [3, 4, 5].includes(parseInt(v)) },
        { name: 'favStyle', index: 7, check: v => v === 'FrontRunner' },
        { name: 'lastTime', index: 8, type: 'min' },
        { name: 'rating', index: 9, type: 'max' },
        { name: 'fitness', index: 10, check: v => parseFloat(v) >= 3 },
        { name: 'energyDiff', index: 11, type: 'max' },
        { name: 'energyDiffAdj', index: 12, type: 'max' },
        { name: 'win', index: 13, type: 'min' },
        { name: 'pla', index: 15, type: 'min' }
    ],
    updateTimers: new Map(),
    
    calculateRacePreferred(raceNum, runnerRows = null) {
        if (!runnerRows) {
            const raceContent = Utils.$(`#race-${raceNum}`);
            if (!raceContent) return null;
            runnerRows = Utils.$$('.runner-row', raceContent);
        }
        
        const preferred = {};
        const typedColumns = this.columns.filter(col => col.type);
        
        typedColumns.forEach(col => {
            preferred[col.name] = col.type === 'max' ? -Infinity : Infinity;
        });
        
        runnerRows.forEach(row => {
            typedColumns.forEach(col => {
                const textValue = row.cells[col.index]?.textContent.trim();
                if (textValue === '-') return;
                
                const value = Utils.parseNum(textValue, col.type === 'max' ? -Infinity : Infinity);
                
                if (col.type === 'max') {
                    if (value > preferred[col.name]) preferred[col.name] = value;
                } else if (value > 0 && value < preferred[col.name]) {
                    preferred[col.name] = value;
                }
            });
        });
        
        return preferred;
    },
    
    checkColumnUniformity(runnerRows) {
        const uniformColumns = new Set();
        this.columns.forEach(col => {
            const values = new Set();
            runnerRows.forEach(row => {
                const value = row.cells[col.index]?.textContent.trim();
                if (value) values.add(value);
            });
            if (values.size <= 1) uniformColumns.add(col.name);
        });
        return uniformColumns;
    },
    
    applyHighlighting(raceNum) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        if (!raceContent) return;
        
        const runnerRows = Utils.$$('.runner-row', raceContent);
        const racePreferred = this.calculateRacePreferred(raceNum, runnerRows);
        if (!racePreferred) return;
        
        const uniformColumns = this.checkColumnUniformity(runnerRows);
        const horseCounts = this.highlightPreferredCells(runnerRows, racePreferred, uniformColumns);
        this.markMostPreferredHorses(runnerRows, horseCounts);
    },
    
    highlightPreferredCells(runnerRows, racePreferred, uniformColumns) {
        const horseCounts = new Map();
        
        runnerRows.forEach(row => {
            Utils.removeClass(Array.from(row.cells), 'preferred-cell');
            let count = 0;
            
            this.columns.forEach(col => {
                const cell = row.cells[col.index];
                const value = cell?.textContent.trim();
                
                if (uniformColumns.has(col.name) || value === '-') return;
                
                const isPreferred = this.isCellPreferred(col, value, racePreferred);
                if (isPreferred) {
                    Utils.addClass(cell, 'preferred-cell');
                    count++;
                }
            });
            
            horseCounts.set(row.dataset.horse, count);
        });
        
        return horseCounts;
    },
    
    isCellPreferred(col, value, racePreferred) {
        if (col.check) {
            return col.check(value);
        }
        
        if (col.type && racePreferred[col.name] !== undefined) {
            const numValue = Utils.parseNum(value, col.type === 'max' ? -Infinity : Infinity);
            return numValue === racePreferred[col.name] && (col.type === 'max' || numValue > 0);
        }
        
        return false;
    },
    
    markMostPreferredHorses(runnerRows, horseCounts) {
        const maxCount = Math.max(...horseCounts.values());
        
        runnerRows.forEach(row => {
            const count = horseCounts.get(row.dataset.horse);
            Utils.removeClass(row, 'most-preferred-horse');
            Utils.$('.most-preferred-badge', row)?.remove();
            
            if (count === maxCount && maxCount > 0) {
                Utils.addClass(row, 'most-preferred-horse');
                this.addPreferredBadge(row.cells[4], count);
            }
        });
    },
    
    addPreferredBadge(nameCell, count) {
        if (!nameCell || Utils.$('.most-preferred-badge', nameCell)) return;
        
        const badge = document.createElement('span');
        badge.className = 'most-preferred-badge';
        badge.textContent = `${count}★`;
        badge.title = `${count} preferred attribute${count > 1 ? 's' : ''}`;
        nameCell.appendChild(badge);
    },
    
    update(raceNum) {
        if (this.updateTimers.has(raceNum)) clearTimeout(this.updateTimers.get(raceNum));
        this.updateTimers.set(raceNum, setTimeout(() => {
            this.applyHighlighting(raceNum);
            this.updateTimers.delete(raceNum);
        }, CONFIG.HIGHLIGHT_DEBOUNCE_DELAY));
    },
    
    initAll() {
        Utils.$$('.race-content').forEach(rc => this.applyHighlighting(rc.id.replace('race-', '')));
    }
};

const FavStyleChart = {
    styleColors: {
        'FrontRunner': '#48bb78',
        'Pacer': '#667eea',
        'Closer': '#f56565',
        'Unknown': '#a0aec0'
    },
    
    draw(raceNum) {
        const container = Utils.$(`#fav-style-chart-${raceNum}`);
        if (!container) return;
        
        const raceContent = Utils.$(`#race-${raceNum}`);
        if (!raceContent) return;
        
        const distribution = this.getStyleDistribution(raceContent);
        const entries = Object.entries(distribution).sort((a, b) => b[1] - a[1]);
        
        if (!entries.length) {
            container.innerHTML = '';
            return;
        }
        
        const labels = entries.map(([style]) => style);
        const values = entries.map(([, count]) => count);
        const colors = labels.map(s => this.styleColors[s] || '#a0aec0');
        
        const data = [{
            values,
            labels,
            type: 'pie',
            marker: { colors, line: { color: 'white', width: 2 } },
            textposition: 'inside',
            textinfo: 'label+percent',
            hovertemplate: '%{label}<br>%{value} horses (%{percent})<extra></extra>',
            direction: 'clockwise',
            sort: false
        }];
        
        const layout = {
            showlegend: true,
            legend: {
                orientation: 'h',
                x: 0.5,
                xanchor: 'center',
                y: -0.1,
                font: { size: 10 }
            },
            margin: { l: 10, r: 10, t: 10, b: 40 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            height: 280
        };
        
        Plotly.newPlot(container, data, layout, { responsive: true, displayModeBar: false });
    },
    
    getStyleDistribution(raceContent) {
        return Utils.$$('.fav-style', raceContent).reduce((dist, cell) => {
            const style = cell.textContent.trim();
            if (style) dist[style] = (dist[style] || 0) + 1;
            return dist;
        }, {});
    },
    
    update(raceNum) {
        const rc = Utils.$(`#race-${raceNum}`);
        if (rc?.classList.contains('active')) this.draw(raceNum);
    },
    
    initAll() {
        const activeRace = Utils.$('.race-content.active');
        if (activeRace) this.draw(activeRace.id.replace('race-', ''));
    }
};

const UI = {
    showRace(raceNum) {
        try {
            const validRaceNum = Utils.validateRaceNum(raceNum);
            
            Utils.removeClass(Utils.$$('.tab-btn'), 'active');
            Utils.addClass(Utils.$(`#tab-${validRaceNum}`), 'active');
            Utils.removeClass(Utils.$$('.race-content'), 'active');
            Utils.addClass(Utils.$(`#race-${validRaceNum}`), 'active');
            
            sessionStorage.setItem('activeRaceTab', validRaceNum);
            
            if (!Cache.has('odds', validRaceNum)) Odds.load(validRaceNum);
            FavStyleChart.draw(validRaceNum);
            PreferredHighlight.update(validRaceNum);
            TradeCalculator.loadPLAParetoData(validRaceNum);
        } catch (error) {
            console.error('Error showing race:', error);
        }
    },
    
    updateExpandAllButtonState(raceNum) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        const expandAllBtn = Utils.$('.expand-all-btn', raceContent);
        const detailsRows = Utils.$$('.runner-details-row', raceContent);
        const allExpanded = detailsRows.length > 0 && 
                           detailsRows.every(row => row.classList.contains('expanded'));
        
        Utils.toggleClass(expandAllBtn, 'all-expanded', allExpanded);
        Utils.$('.expand-all-text', expandAllBtn).textContent = allExpanded ? 'Collapse All' : 'Expand All';
        
        const icon = Utils.$('.expand-all-icon', expandAllBtn);
        if (icon) icon.textContent = allExpanded ? '▲' : '▼';
    },
    
    sortTable(raceNum, columnIndex, type) {
        try {
            const validRaceNum = Utils.validateRaceNum(raceNum);
            const table = Utils.$(`#race-${validRaceNum} .runners-table`);
            if (!table) return;
            
            const tbody = Utils.$('tbody', table);
            const header = Utils.$$('thead th', table)[columnIndex];
            if (!tbody || !header) return;
            
            const isAscending = header.classList.contains('sort-desc') || !header.classList.contains('sort-asc');
            const rowPairs = this.extractRowPairs(tbody, columnIndex, type, isAscending);
            
            if (rowPairs.length === 0) return;
            
            this.sortRowPairs(rowPairs, type, isAscending);
            this.updateSortIndicators(table, header, isAscending);
            this.replaceTableBody(tbody, rowPairs);
            
            PreferredHighlight.update(validRaceNum);
        } catch (error) {
            console.error('Error sorting table:', error);
        }
    },
    
    extractRowPairs(tbody, columnIndex, type, isAscending) {
        const rowPairs = [];
        const allRows = Array.from(tbody.children);
        
        for (let i = 0; i < allRows.length; i++) {
            const row = allRows[i];
            if (!row.classList?.contains('runner-row')) continue;
            
            const detailsRow = allRows[i + 1];
            const cell = row.cells[columnIndex];
            
            if (cell) {
                rowPairs.push({
                    runnerRow: row,
                    detailsRow: detailsRow?.classList?.contains('runner-details-row') ? detailsRow : null,
                    sortValue: this.getSortValue(cell.textContent.trim(), type, isAscending)
                });
            }
            i++;
        }
        
        return rowPairs;
    },
    
    getSortValue(rawValue, type, isAscending) {
        if (type === 'number') {
            if (rawValue === '-' || rawValue === '') {
                return isAscending ? Infinity : -Infinity;
            }
            return Utils.parseNum(rawValue, isAscending ? Infinity : -Infinity);
        }
        return rawValue.toLowerCase();
    },
    
    sortRowPairs(rowPairs, type, isAscending) {
        rowPairs.sort((a, b) => {
            if (type === 'number') {
                return isAscending ? a.sortValue - b.sortValue : b.sortValue - a.sortValue;
            }
            const cmp = a.sortValue < b.sortValue ? -1 : a.sortValue > b.sortValue ? 1 : 0;
            return isAscending ? cmp : -cmp;
        });
    },
    
    updateSortIndicators(table, activeHeader, isAscending) {
        Utils.$$('thead th.sortable', table).forEach(h => {
            Utils.removeClass(h, ['sort-asc', 'sort-desc']);
            const arrow = Utils.$('.sort-arrow', h);
            if (arrow) arrow.textContent = '⇅';
        });
        
        Utils.addClass(activeHeader, isAscending ? 'sort-asc' : 'sort-desc');
        const arrow = Utils.$('.sort-arrow', activeHeader);
        if (arrow) arrow.textContent = isAscending ? '▲' : '▼';
    },
    
    replaceTableBody(tbody, rowPairs) {
        while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
        
        const fragment = document.createDocumentFragment();
        rowPairs.forEach(({ runnerRow, detailsRow }) => {
            fragment.appendChild(runnerRow);
            if (detailsRow) fragment.appendChild(detailsRow);
        });
        
        tbody.appendChild(fragment);
    },
    
    openTrackWorkoutVideo(raceDate, raceNum) {
        try {
            const validDate = Utils.validateDate(raceDate);
            const validRaceNum = Utils.validateRaceNum(raceNum);
            const dateParts = validDate.split('-');
            const url = `https://streaminghkjc-a.akamaihd.net/hdflash/twstarter/${dateParts[0]}/${dateParts.join('')}/${validRaceNum.padStart(2, '0')}/novo/twstarter_${dateParts.join('')}_${validRaceNum.padStart(2, '0')}_novo_2500kbps.mp4`;
            window.open(url, 'trackWorkoutVideo', 'width=600,height=400,resizable=yes,scrollbars=yes');
        } catch (error) {
            console.error('Error opening track workout video:', error);
            alert(`Unable to open track workout video: ${error.message}`);
        }
    },
    
    openTipsIndex(raceNum) {
        try {
            const validRaceNum = Utils.validateRaceNum(raceNum);
            const url = `https://racing.hkjc.com/racing/English/tipsindex/tips_index.asp?RaceNo=${validRaceNum}`;
            window.open(url, 'tipsIndex', 'width=800,height=600,resizable=yes,scrollbars=yes');
        } catch (error) {
            console.error('Error opening tips index:', error);
            alert(`Unable to open tips index: ${error.message}`);
        }
    }
};


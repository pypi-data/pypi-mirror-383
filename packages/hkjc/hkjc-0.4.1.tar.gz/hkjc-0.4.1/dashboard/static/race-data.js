// HKJC Race Info - Race Data Management
const Odds = {
    async load(raceNum) {
        try {
            const validRaceNum = Utils.validateRaceNum(raceNum);
            if (!RaceReadiness.isReady(validRaceNum)) {
                Utils.log(`Skipping odds for race ${validRaceNum} - race not ready`);
                return null;
            }
            const data = await API.fetchOdds(validRaceNum);
            Cache.set('odds', validRaceNum, data);
            this.updateDisplay(validRaceNum, data);
            return data;
        } catch (error) {
            console.error(`Error loading odds for race ${raceNum}:`, error);
            return null;
        }
    },
    
    updateDisplay(raceNum, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return;
        
        this.updateRawOdds(raceNum, oddsData);
        this.updateFitOdds(raceNum, oddsData);
        this.updateAllOddsTables(raceNum, oddsData);
        
        PreferredHighlight.update(raceNum);
        TradeCalculator.updateParetoForOddsChange(raceNum);
    },
    
    updateRawOdds(raceNum, oddsData) {
        const updates = [
            ['.odds-win', oddsData.Raw.WIN],
            ['.odds-pla', oddsData.Raw.PLA]
        ];
        
        updates.forEach(([selector, data]) => {
            Utils.$$(`${selector}[data-race="${raceNum}"]`).forEach(cell => {
                const odds = data?.[cell.dataset.horse];
                if (odds !== undefined) cell.textContent = odds;
            });
        });
    },
    
    updateFitOdds(raceNum, oddsData) {
        const updates = [
            ['.odds-win-fit', oddsData.Raw.WIN, oddsData.Fit.WIN],
            ['.odds-pla-fit', oddsData.Raw.PLA, oddsData.Fit.PLA]
        ];
        
        updates.forEach(([selector, rawData, fitData]) => {
            Utils.$$(`${selector}[data-race="${raceNum}"]`).forEach(cell => {
                this.updateDiffCell(cell, rawData, fitData);
            });
        });
    },
    
    updateDiffCell(cell, rawData, fitData) {
        const horseNo = cell.dataset.horse;
        const rawOdds = rawData?.[horseNo];
        const fitOdds = fitData?.[horseNo];
        
        Utils.removeClass(cell, ['odds-diff-positive', 'odds-diff-negative']);
        
        if (rawOdds !== undefined && fitOdds !== undefined) {
            const diff = fitOdds - rawOdds;
            cell.textContent = `${diff >= 0 ? '+' : ''}${diff.toFixed(1)}`;
            
            if (diff !== 0) {
                Utils.addClass(cell, diff < 0 ? 'odds-diff-negative' : 'odds-diff-positive');
            }
        }
    },
    
    updateAllOddsTables(raceNum, oddsData) {
        Utils.$$(`.odds-table[data-race="${raceNum}"]`).forEach(table => {
            this.updateOddsTable(table, table.dataset.horse, oddsData);
        });
    },
    
    updateOddsTable(table, horseNo, oddsData) {
        const otherHorses = Object.keys(oddsData.Raw.WIN || {})
            .sort((a, b) => parseInt(a) - parseInt(b))
            .filter(h => h !== horseNo);
        const rows = Utils.$$('tbody tr', table);
        if (rows.length < 4) return;
        
        const configs = [
            { data: oddsData.Raw.QIN, rawData: null },
            { data: oddsData.Fit.QIN, rawData: oddsData.Raw.QIN },
            { data: oddsData.Raw.QPL, rawData: null },
            { data: oddsData.Fit.QPL, rawData: oddsData.Raw.QPL }
        ];
        
        configs.forEach(({ data, rawData }, rowIdx) => {
            Utils.$$('td:not(.odds-type-label)', rows[rowIdx]).forEach((cell, colIdx) => {
                const h = otherHorses[colIdx];
                const odds = data?.[horseNo]?.[h] || data?.[h]?.[horseNo];
                
                Utils.removeClass(cell, ['odds-diff-positive', 'odds-diff-negative']);
                
                if (rawData) {
                    const rawOdds = rawData?.[horseNo]?.[h] || rawData?.[h]?.[horseNo];
                    if (odds !== undefined && rawOdds !== undefined) {
                        const diff = odds - rawOdds;
                        cell.textContent = `${diff >= 0 ? '+' : ''}${diff.toFixed(1)}`;
                        if (diff !== 0) {
                            Utils.addClass(cell, diff < 0 ? 'odds-diff-negative' : 'odds-diff-positive');
                        }
                    } else {
                        cell.textContent = '-';
                    }
                } else {
                    cell.textContent = odds !== undefined ? odds : '-';
                }
            });
        });
    },
    
    createSection(raceNum, horseNo, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return '';
        
        const otherHorses = Object.keys(oddsData.Raw.WIN || {})
            .sort((a, b) => parseInt(a) - parseInt(b))
            .filter(h => h !== horseNo);
        
        if (!otherHorses.length) return '';
        
        const createRow = (label, data, rawData = null) => {
            const cells = otherHorses.map(h => {
                const odds = data?.[horseNo]?.[h] || data?.[h]?.[horseNo];
                
                if (rawData) {
                    const rawOdds = rawData?.[horseNo]?.[h] || rawData?.[h]?.[horseNo];
                    if (odds !== undefined && rawOdds !== undefined) {
                        const diff = odds - rawOdds;
                        const className = diff < 0 ? 'odds-diff-negative' : (diff > 0 ? 'odds-diff-positive' : '');
                        return `<td class="${className}">${diff >= 0 ? '+' : ''}${diff.toFixed(1)}</td>`;
                    }
                    return '<td>-</td>';
                }
                
                return `<td>${odds !== undefined ? odds : '-'}</td>`;
            }).join('');
            
            return `<tr><td class="odds-type-label">${label}</td>${cells}</tr>`;
        };
        
        const rowConfigs = [
            ['QIN', oddsData.Raw.QIN],
            ['QIN (fit)', oddsData.Fit.QIN, oddsData.Raw.QIN],
            ['QPL', oddsData.Raw.QPL],
            ['QPL (fit)', oddsData.Fit.QPL, oddsData.Raw.QPL]
        ];
        
        const headerCells = otherHorses.map(h => `<th>vs ${h}</th>`).join('');
        const bodyRows = rowConfigs.map(args => createRow(...args)).join('');
        
        return `<div class="odds-table-container">
            <table class="odds-table" data-race="${raceNum}" data-horse="${horseNo}">
                <thead><tr><th>Type</th>${headerCells}</tr></thead>
                <tbody>${bodyRows}</tbody>
            </table></div>`;
    },
    
    startPolling() {
        const allRaceNums = Utils.$$('.race-content').map(el => el.id.replace('race-', ''));
        allRaceNums.forEach(raceNum => this.load(raceNum));
        
        if (State.polling.oddsIntervalId) clearTimeout(State.polling.oddsIntervalId);
        
        const scheduleNextPoll = () => {
            const jitter = Math.random() * CONFIG.POLL_JITTER - (CONFIG.POLL_JITTER / 2);
            State.polling.oddsIntervalId = setTimeout(() => {
                allRaceNums.forEach(raceNum => this.load(raceNum));
                scheduleNextPoll();
            }, CONFIG.ODDS_POLL_INTERVAL + jitter);
        };
        scheduleNextPoll();
    },
    
    stopPolling() {
        if (State.polling.oddsIntervalId) {
            clearTimeout(State.polling.oddsIntervalId);
            State.polling.oddsIntervalId = null;
        }
    }
};

const RunnerDetails = {
    parseHistoryTable(historyHtml) {
        const doc = new DOMParser().parseFromString(historyHtml, 'text/html');
        const table = Utils.$('table', doc);
        if (!table) return null;
        return { table, headerRow: Utils.$('thead tr', table) };
    },
    
    findColumnIndex(headerRow, columnNames) {
        return Utils.$$('th', headerRow).findIndex(th => {
            const text = th.textContent.trim().toLowerCase();
            return columnNames.some(name => text === name || text.includes(name));
        });
    },
    
    columnExtractors: [
        {
            name: 'favStyle',
            selector: '.fav-style',
            extract: (historyHtml) => {
                const parsed = RunnerDetails.parseHistoryTable(historyHtml);
                if (!parsed) return null;
                
                const styleIdx = RunnerDetails.findColumnIndex(parsed.headerRow, ['style']);
                if (styleIdx === -1) return null;
                
                return Utils.$$('tbody tr', parsed.table).slice(0, 5)
                    .map(row => row.querySelectorAll('td')[styleIdx]?.textContent.trim())
                    .filter(Boolean);
            },
            process: (rawData) => {
                if (!rawData?.length) return 'Unknown';
                const freq = {};
                rawData.forEach(val => freq[val] = (freq[val] || 0) + 1);
                return Object.entries(freq)
                    .reduce((max, [val, count]) => count > max[1] ? [val, count] : max, [null, 0])[0] || 'Unknown';
            },
            onUpdate: (raceNum) => FavStyleChart.update(raceNum)
        },
        {
            name: 'lastTime',
            selector: '.last-finish-time',
            extract: (historyHtml) => {
                const parsed = RunnerDetails.parseHistoryTable(historyHtml);
                if (!parsed) return null;
                
                const timeIdx = RunnerDetails.findColumnIndex(parsed.headerRow, ['finish time', 'time']);
                if (timeIdx === -1) {
                    Utils.log('Finish Time column not found');
                    return null;
                }
                
                const firstRow = Utils.$('tbody tr', parsed.table);
                const timeValue = firstRow?.querySelectorAll('td')[timeIdx]?.textContent.trim() || null;
                Utils.log(`Extracted finish time: ${timeValue}`);
                return timeValue;
            },
            process: (rawData) => rawData || '-',
            onUpdate: null
        }
    ],
    
    updateAllColumns(raceNum, horseNo, historyHtml) {
        Utils.log(`Updating all columns for race ${raceNum}, horse ${horseNo}`);
        let needsHighlight = false;
        
        this.columnExtractors.forEach(({ name, selector, extract, process, onUpdate }) => {
            const cell = Utils.$(`${selector}[data-race="${raceNum}"][data-horse="${horseNo}"]`);
            if (!cell) {
                Utils.log(`Cell not found for ${name}`);
                return;
            }
            
            try {
                cell.textContent = process(extract(historyHtml));
                Utils.log(`Updated ${name} for horse ${horseNo}: ${cell.textContent}`);
                if (onUpdate) onUpdate(raceNum);
                needsHighlight = true;
            } catch (error) {
                console.error(`Error updating ${name} for horse ${horseNo}:`, error);
                cell.textContent = name === 'favStyle' ? 'Unknown' : '-';
            }
        });
        
        if (needsHighlight) PreferredHighlight.update(raceNum);
    },
    
    async load(raceNum, horseNo, going, track, distance, venue) {
        const validRaceNum = Utils.validateRaceNum(raceNum);
        const validHorseNo = Utils.validateHorseNo(horseNo);
        const cacheKey = Utils.makeCacheKey(validRaceNum, validHorseNo);
        
        if (Cache.has('runnerDetails', cacheKey)) {
            const cachedHtml = Cache.get('runnerDetails', cacheKey);
            this.updateAllColumns(validRaceNum, validHorseNo, cachedHtml);
            return cachedHtml;
        }
        
        const html = await API.fetchHorseHistory(validHorseNo, going, track, distance, venue);
        Cache.set('runnerDetails', cacheKey, html);
        this.updateAllColumns(validRaceNum, validHorseNo, html);
        return html;
    },
    
    createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml) {
        const oddsSection = oddsData ? `<div class="details-left">${Odds.createSection(raceNum, runnerNo, oddsData)}</div>` : '';
        return `<div class="runner-details-wrapper">${historyHtml}<div class="details-right">${oddsSection}</div></div>`;
    },
    
    async toggle(rowElement, raceNum, horseNo, going, track, distance) {
        const detailsRow = Utils.$(`#runner-details-${raceNum}-${horseNo}`);
        const expandIcon = Utils.$('.expand-icon', rowElement);
        const isExpanded = detailsRow.classList.contains('expanded');
        
        Utils.toggleClass([detailsRow, expandIcon], 'expanded', !isExpanded);
        
        if (!isExpanded) {
            const detailsContent = Utils.$(`#runner-details-content-${raceNum}-${horseNo}`);
            const runnerNo = Utils.$('.odds-win', rowElement)?.dataset.horse || horseNo;
            const oddsData = Cache.get('odds', raceNum);
            const cacheKey = Utils.makeCacheKey(raceNum, horseNo);
            const venue = rowElement.dataset.venue || '';
            
            if (!Cache.has('runnerDetails', cacheKey)) {
                detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData,
                    '<div class="details-loading">Loading race history...</div>');
                try {
                    const historyHtml = await this.load(raceNum, horseNo, going, track, distance, venue);
                    detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml);
                } catch (error) {
                    detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData,
                        `<div class="details-loading error">Error: ${error.message}</div>`);
                }
            } else {
                const cachedHtml = Cache.get('runnerDetails', cacheKey);
                detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData, cachedHtml);
                this.updateAllColumns(raceNum, horseNo, cachedHtml);
            }
        }
        UI.updateExpandAllButtonState(raceNum);
    },
    
    async loadRunnerData(raceNum, runnerData) {
        const { horseNo, runnerNo, going, track, distance, venue } = runnerData;
        const cacheKey = Utils.makeCacheKey(raceNum, horseNo);
        const detailsRow = Utils.$(`#runner-details-${raceNum}-${horseNo}`);
        
        if (!detailsRow.classList.contains('expanded')) return;
        
        if (Cache.has('runnerDetails', cacheKey)) {
            this.updateAllColumns(raceNum, horseNo, Cache.get('runnerDetails', cacheKey));
            return;
        }
        
        const detailsContent = Utils.$(`#runner-details-content-${raceNum}-${horseNo}`);
        try {
            const historyHtml = await this.load(raceNum, horseNo, going, track, distance, venue);
            detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, Cache.get('odds', raceNum), historyHtml);
        } catch (error) {
            detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, Cache.get('odds', raceNum),
                `<div class="details-loading error">Error: ${error.message}</div>`);
        }
    },
    
    async toggleAll(raceNum, buttonElement) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        const runnerRows = Utils.$$('.runner-row', raceContent);
        const isExpanding = !buttonElement.classList.contains('all-expanded');
        
        if (isExpanding) {
            const oddsData = Cache.get('odds', raceNum);
            const runners = runnerRows.map(row => {
                const runnerData = Utils.getRunnerData(row);
                const cacheKey = Utils.makeCacheKey(raceNum, runnerData.horseNo);
                const detailsRow = Utils.$(`#runner-details-${raceNum}-${runnerData.horseNo}`);
                const detailsContent = Utils.$(`#runner-details-content-${raceNum}-${runnerData.horseNo}`);
                
                Utils.addClass([detailsRow, Utils.$('.expand-icon', row)], 'expanded');
                
                if (Cache.has('runnerDetails', cacheKey)) {
                    const cachedHtml = Cache.get('runnerDetails', cacheKey);
                    detailsContent.innerHTML = this.createContent(raceNum, runnerData.runnerNo, runnerData.horseNo, oddsData, cachedHtml);
                    this.updateAllColumns(raceNum, runnerData.horseNo, cachedHtml);
                } else {
                    detailsContent.innerHTML = this.createContent(raceNum, runnerData.runnerNo, runnerData.horseNo, oddsData,
                        '<div class="details-loading">Loading race history...</div>');
                }
                return runnerData;
            });
            
            UI.updateExpandAllButtonState(raceNum);
            (async () => {
                for (const runnerData of runners) await this.loadRunnerData(raceNum, runnerData);
            })();
        } else {
            runnerRows.forEach(row => {
                Utils.removeClass([Utils.$(`#runner-details-${raceNum}-${row.dataset.horse}`), 
                                  Utils.$('.expand-icon', row)], 'expanded');
            });
            UI.updateExpandAllButtonState(raceNum);
        }
    },
    
    async prefetchAll(priorityRaceNum = null) {
        Utils.log('Starting background prefetch...');
        const sortedRaces = Utils.$$('.race-content').sort((a, b) => {
            const aNum = a.id.replace('race-', '');
            const bNum = b.id.replace('race-', '');
            if (priorityRaceNum) {
                if (aNum === priorityRaceNum) return -1;
                if (bNum === priorityRaceNum) return 1;
            }
            return parseInt(aNum) - parseInt(bNum);
        });
        
        for (const raceContent of sortedRaces) {
            const raceNum = raceContent.id.replace('race-', '');
            Utils.log(`Prefetching race ${raceNum}${raceNum === priorityRaceNum ? ' (priority)' : ''}...`);
            
            for (const row of Utils.$$('.runner-row', raceContent)) {
                const { horseNo, going, track, distance, venue } = Utils.getRunnerData(row);
                const cacheKey = Utils.makeCacheKey(raceNum, horseNo);
                
                if (!horseNo || Cache.has('runnerDetails', cacheKey)) continue;
                
                try {
                    await this.load(raceNum, horseNo, going, track, distance, venue);
                    Utils.log(`✓ Prefetched race ${raceNum} - horse ${horseNo}`);
                } catch (error) {
                    console.error(`✗ Error prefetching race ${raceNum} - horse ${horseNo}:`, error);
                }
            }
        }
        Utils.log('✓ Prefetch completed');
    }
};

const Speedmap = {
    async load(raceNum) {
        try {
            const validRaceNum = Utils.validateRaceNum(raceNum);
            const container = Utils.$(`#race-${validRaceNum} .speedmap-container`);
            if (!container) return;
            
            if (Cache.has('speedmaps', validRaceNum)) {
                this.displayCached(validRaceNum, container);
                return;
            }
            
            const img = Utils.$(`#speedmap-${validRaceNum}`);
            if (img) img.style.display = 'none';
            
            const base64String = await API.fetchSpeedmap(validRaceNum);
            
            if (!base64String?.trim()) {
                Cache.set('speedmaps', validRaceNum, null);
                container.innerHTML = '<div class="race-not-ready">Speedmap not available</div>';
                return;
            }
            
            Cache.set('speedmaps', validRaceNum, base64String);
            this.displayImage(validRaceNum, container, base64String);
        } catch (error) {
            console.error(`Error loading speedmap for race ${raceNum}:`, error);
        }
    },
    
    displayCached(raceNum, container) {
        const cached = Cache.get('speedmaps', raceNum);
        if (cached) {
            this.displayImage(raceNum, container, cached);
        } else {
            container.innerHTML = '<div class="race-not-ready">Speedmap not available</div>';
        }
    },
    
    displayImage(raceNum, container, src) {
        if (!Utils.$('img', container)) {
            container.innerHTML = `<img id="speedmap-${raceNum}" class="speedmap-image" alt="Race ${raceNum} Speed Map" />`;
        }
        const img = Utils.$(`#speedmap-${raceNum}`);
        img.src = src;
        img.style.display = 'block';
    },
    
    async loadAll() {
        for (const img of Utils.$$('.speedmap-image')) {
            await this.load(img.id.replace('speedmap-', ''));
        }
    }
};


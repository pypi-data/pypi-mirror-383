// HKJC Race Info - Main Application Script
const CONFIG = {
    ODDS_POLL_INTERVAL: 90000,
    POLL_JITTER: 10000,
    MIN_REQUEST_DELAY: 80,
    MAX_REQUEST_DELAY: 250,
    MAX_CONCURRENT_REQUESTS: 3,
    REQUEST_TIMEOUT: 10000,
    HIGHLIGHT_DEBOUNCE_DELAY: 100,
    DEBUG: false
};

const Utils = {
    getRunnerData(row) {
        return {
            raceNum: row.dataset.race,
            horseNo: row.dataset.horse,
            going: row.dataset.going || '',
            track: row.dataset.track || '',
            distance: row.dataset.dist || '',
            venue: row.dataset.venue || '',
            runnerNo: row.querySelector('.odds-win')?.dataset.horse || row.dataset.horse
        };
    },
    
    log(...args) { if (CONFIG.DEBUG) console.log(...args); },
    
    $(selector, context = document) { return context.querySelector(selector); },
    $$(selector, context = document) { return Array.from(context.querySelectorAll(selector)); },
    
    addClass(elements, className) {
        (Array.isArray(elements) ? elements : [elements]).forEach(el => el?.classList.add(className));
    },
    removeClass(elements, className) {
        (Array.isArray(elements) ? elements : [elements]).forEach(el => el?.classList.remove(className));
    },
    toggleClass(elements, className, force) {
        (Array.isArray(elements) ? elements : [elements]).forEach(el => el?.classList.toggle(className, force));
    },
    
    parseNum(value, fallback = 0) {
        const num = parseFloat(value);
        return isNaN(num) ? fallback : num;
    },
    
    validateRaceNum(raceNum) {
        const num = parseInt(raceNum);
        if (isNaN(num) || num < 1 || num > 99) throw new Error(`Invalid race number: ${raceNum}`);
        return num.toString();
    },
    validateHorseNo(horseNo) {
        if (!horseNo || typeof horseNo !== 'string' || !horseNo.trim()) 
            throw new Error(`Invalid horse number: ${horseNo}`);
        return horseNo.trim();
    },
    validateDate(dateStr) {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) 
            throw new Error(`Invalid date format: ${dateStr}. Expected YYYY-MM-DD`);
        return dateStr;
    }
};

const State = {
    caches: { runnerDetails: new Map(), speedmaps: new Map(), odds: new Map() },
    polling: { oddsIntervalId: null },
    raceReadiness: new Map()
};

const RequestQueue = {
    queue: [],
    activeCount: 0,
    
    enqueue(requestFn, priority = 0) {
        return new Promise((resolve, reject) => {
            this.queue.push({ requestFn, resolve, reject, priority });
            this.queue.sort((a, b) => b.priority - a.priority);
            this.process();
        });
    },
    
    async process() {
        if (this.activeCount >= CONFIG.MAX_CONCURRENT_REQUESTS || !this.queue.length) return;
        
        const { requestFn, resolve, reject } = this.queue.shift();
        this.activeCount++;
        
        try {
            resolve(await requestFn());
        } catch (error) {
            reject(error);
        } finally {
            this.activeCount--;
            await new Promise(r => setTimeout(r, 
                Math.random() * (CONFIG.MAX_REQUEST_DELAY - CONFIG.MIN_REQUEST_DELAY) + CONFIG.MIN_REQUEST_DELAY));
            this.process();
        }
    },
    
    clear() { this.queue = []; }
};

const API = {
    async fetch(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);
        
        try {
            const response = await fetch(url, { ...options, signal: controller.signal });
            clearTimeout(timeoutId);
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') throw new Error('Request timeout');
            throw error;
        }
    },
    
    fetchOdds(raceNum) {
        return RequestQueue.enqueue(async () => 
            (await this.fetch(`/live_odds/${Utils.validateRaceNum(raceNum)}`)).json(), 1);
    },
    
    fetchHorseHistory(horseNo, going, track, distance, venue) {
        return RequestQueue.enqueue(async () => {
            const params = new URLSearchParams({ going: going || '', track: track || '', dist: distance || '', venue: venue || '' });
            return (await this.fetch(`/horse_info/${Utils.validateHorseNo(horseNo)}?${params}`)).text();
        }, 0);
    },
    
    fetchSpeedmap(raceNum) {
        return RequestQueue.enqueue(async () => 
            (await this.fetch(`/speedmap/${Utils.validateRaceNum(raceNum)}`)).text(), 0);
    }
};

const Cache = {
    get(cacheName, key) { return State.caches[cacheName]?.get(key); },
    set(cacheName, key, value) {
        if (!State.caches[cacheName]) State.caches[cacheName] = new Map();
        State.caches[cacheName].set(key, value);
    },
    has(cacheName, key) { return State.caches[cacheName]?.has(key) || false; },
    clear(cacheName) {
        cacheName ? State.caches[cacheName]?.clear() : Object.values(State.caches).forEach(c => c.clear());
    }
};

const RaceReadiness = {
    isReady(raceNum) {
        if (State.raceReadiness.has(raceNum)) return State.raceReadiness.get(raceNum);
        const runnerRows = Utils.$$(`#race-${raceNum} .runner-row`);
        const ready = runnerRows.length > 0 && runnerRows.some(row => {
            const fitness = Utils.parseNum(row.cells[10]?.textContent.trim());
            const energy = Utils.parseNum(row.cells[11]?.textContent.trim());
            return fitness !== 0 || energy !== 0;
        });
        State.raceReadiness.set(raceNum, ready);
        return ready;
    }
};

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
        
        // Update raw odds normally
        [['.odds-win', oddsData.Raw.WIN], ['.odds-pla', oddsData.Raw.PLA]]
            .forEach(([cls, data]) => this.updateCells(`${cls}[data-race="${raceNum}"]`, data));
        
        // Update fit odds as differences
        [['.odds-win-fit', oddsData.Raw.WIN, oddsData.Fit.WIN],
         ['.odds-pla-fit', oddsData.Raw.PLA, oddsData.Fit.PLA]]
            .forEach(([cls, rawData, fitData]) => 
                this.updateCellsWithDiff(`${cls}[data-race="${raceNum}"]`, rawData, fitData));
        
        Utils.$$(`.odds-table[data-race="${raceNum}"]`).forEach(table => 
            this.updateOddsTable(table, table.dataset.horse, oddsData));
        
        PreferredHighlight.update(raceNum);
    },
    
    updateCells(selector, oddsData) {
        Utils.$$(selector).forEach(cell => {
            const odds = oddsData?.[cell.dataset.horse];
            if (odds !== undefined) cell.textContent = odds;
        });
    },
    
    updateCellsWithDiff(selector, rawData, fitData) {
        Utils.$$(selector).forEach(cell => {
            const horseNo = cell.dataset.horse;
            const rawOdds = rawData?.[horseNo];
            const fitOdds = fitData?.[horseNo];
            
            // Remove existing diff classes
            Utils.removeClass(cell, ['odds-diff-positive', 'odds-diff-negative']);
            
            if (rawOdds !== undefined && fitOdds !== undefined) {
                const diff = fitOdds - rawOdds;
                const sign = diff >= 0 ? '+' : '';
                cell.textContent = `${sign}${diff.toFixed(1)}`;
                
                // Add appropriate class
                if (diff < 0) {
                    Utils.addClass(cell, 'odds-diff-negative');
                } else if (diff > 0) {
                    Utils.addClass(cell, 'odds-diff-positive');
                }
            }
        });
    },
    
    updateOddsTable(table, horseNo, oddsData) {
        const otherHorses = Object.keys(oddsData.Raw.WIN || {})
            .sort((a, b) => parseInt(a) - parseInt(b)).filter(h => h !== horseNo);
        const rows = Utils.$$('tbody tr', table);
        if (rows.length < 4) return;
        
        // Row 0: QIN (raw), Row 1: QIN (fit), Row 2: QPL (raw), Row 3: QPL (fit)
        const dataConfig = [
            { data: oddsData.Raw.QIN, isFit: false, rawData: null },
            { data: oddsData.Fit.QIN, isFit: true, rawData: oddsData.Raw.QIN },
            { data: oddsData.Raw.QPL, isFit: false, rawData: null },
            { data: oddsData.Fit.QPL, isFit: true, rawData: oddsData.Raw.QPL }
        ];
        
        dataConfig.forEach(({ data, isFit, rawData }, i) => {
            Utils.$$('td:not(.odds-type-label)', rows[i]).forEach((cell, idx) => {
                const h = otherHorses[idx];
                const odds = data?.[horseNo]?.[h] || data?.[h]?.[horseNo];
                
                // Remove existing diff classes
                Utils.removeClass(cell, ['odds-diff-positive', 'odds-diff-negative']);
                
                if (isFit && rawData) {
                    // Calculate and display difference
                    const rawOdds = rawData[horseNo]?.[h] || rawData[h]?.[horseNo];
                    if (odds !== undefined && rawOdds !== undefined) {
                        const diff = odds - rawOdds;
                        const sign = diff >= 0 ? '+' : '';
                        cell.textContent = `${sign}${diff.toFixed(1)}`;
                        
                        if (diff < 0) {
                            Utils.addClass(cell, 'odds-diff-negative');
                        } else if (diff > 0) {
                            Utils.addClass(cell, 'odds-diff-positive');
                        }
                    } else {
                        cell.textContent = '-';
                    }
                } else {
                    // Display raw odds normally
                    cell.textContent = odds !== undefined ? odds : '-';
                }
            });
        });
    },
    
    createSection(raceNum, horseNo, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return '';
        const otherHorses = Object.keys(oddsData.Raw.WIN || {})
            .sort((a, b) => parseInt(a) - parseInt(b)).filter(h => h !== horseNo);
        if (!otherHorses.length) return '';
        
        const createRow = (label, data, isFit = false, rawData = null) => `<tr><td class="odds-type-label">${label}</td>${
            otherHorses.map(h => {
                const odds = data?.[horseNo]?.[h] || data?.[h]?.[horseNo];
                
                if (isFit && rawData) {
                    const rawOdds = rawData?.[horseNo]?.[h] || rawData?.[h]?.[horseNo];
                    if (odds !== undefined && rawOdds !== undefined) {
                        const diff = odds - rawOdds;
                        const sign = diff >= 0 ? '+' : '';
                        const className = diff < 0 ? 'odds-diff-negative' : (diff > 0 ? 'odds-diff-positive' : '');
                        return `<td class="${className}">${sign}${diff.toFixed(1)}</td>`;
                    }
                    return `<td>-</td>`;
                }
                
                return `<td>${odds !== undefined ? odds : '-'}</td>`;
            }).join('')}</tr>`;
        
        return `<div class="odds-table-container">
            <table class="odds-table" data-race="${raceNum}" data-horse="${horseNo}">
                <thead><tr><th>Type</th>${otherHorses.map(h => `<th>vs ${h}</th>`).join('')}</tr></thead>
                <tbody>${[
                    ['QIN', oddsData.Raw.QIN, false, null], 
                    ['QIN (fit)', oddsData.Fit.QIN, true, oddsData.Raw.QIN], 
                    ['QPL', oddsData.Raw.QPL, false, null], 
                    ['QPL (fit)', oddsData.Fit.QPL, true, oddsData.Raw.QPL]
                ].map(([label, data, isFit, rawData]) => createRow(label, data, isFit, rawData)).join('')}</tbody>
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
        const headerRow = Utils.$('thead tr', table);
        return { table, headerRow };
    },
    
    columnExtractors: [
        {
            name: 'favStyle',
            selector: '.fav-style',
            extract: (historyHtml) => {
                const parsed = RunnerDetails.parseHistoryTable(historyHtml);
                if (!parsed) return null;
                const styleIdx = Utils.$$('th', parsed.headerRow)
                    .findIndex(th => th.textContent.trim().toLowerCase() === 'style');
                if (styleIdx === -1) return null;
                return Utils.$$('tbody tr', parsed.table).slice(0, 5)
                    .map(row => row.querySelectorAll('td')[styleIdx]?.textContent.trim())
                    .filter(Boolean);
            },
            process: (rawData) => {
                if (!rawData?.length) return 'Unknown';
                const freq = rawData.reduce((acc, val) => (acc[val] = (acc[val] || 0) + 1, acc), {});
                return Object.entries(freq).reduce((max, [val, f]) => f > max[1] ? [val, f] : max, [null, 0])[0] || 'Unknown';
            },
            onUpdate: (raceNum) => FavStyleChart.update(raceNum)
        },
        {
            name: 'lastTime',
            selector: '.last-finish-time',
            extract: (historyHtml) => {
                const parsed = RunnerDetails.parseHistoryTable(historyHtml);
                if (!parsed) return null;
                const timeIdx = Utils.$$('th', parsed.headerRow)
                    .findIndex(th => ['finish time', 'time'].includes(th.textContent.trim().toLowerCase()));
                if (timeIdx === -1) { Utils.log('Finish Time column not found'); return null; }
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
            if (!cell) { Utils.log(`Cell not found for ${name}`); return; }
            
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
        const cacheKey = `${validRaceNum}-${validHorseNo}`;
        
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
            const cacheKey = `${raceNum}-${horseNo}`;
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
        const cacheKey = `${raceNum}-${horseNo}`;
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
                const cacheKey = `${raceNum}-${runnerData.horseNo}`;
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
            const aNum = a.id.replace('race-', ''), bNum = b.id.replace('race-', '');
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
                if (!horseNo || Cache.has('runnerDetails', `${raceNum}-${horseNo}`)) continue;
                
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
            const img = Utils.$(`#speedmap-${validRaceNum}`);
            if (!img || !container) return;
            
            if (Cache.has('speedmaps', validRaceNum)) {
                const cached = Cache.get('speedmaps', validRaceNum);
                if (cached) {
                    if (!Utils.$('img', container)) {
                        container.innerHTML = `<img id="speedmap-${validRaceNum}" class="speedmap-image" alt="Race ${validRaceNum} Speed Map" />`;
                    }
                    Utils.$(`#speedmap-${validRaceNum}`).src = cached;
                    Utils.$(`#speedmap-${validRaceNum}`).style.display = 'block';
                } else {
                    img.style.display = 'none';
                    container.innerHTML = '<div class="race-not-ready">Speedmap not available</div>';
                }
                return;
            }
            
            img.style.display = 'none';
            const base64String = await API.fetchSpeedmap(validRaceNum);
            
            if (!base64String?.trim()) {
                Cache.set('speedmaps', validRaceNum, null);
                container.innerHTML = '<div class="race-not-ready">Speedmap not available</div>';
                return;
            }
            
            Cache.set('speedmaps', validRaceNum, base64String);
            if (!Utils.$('img', container)) {
                container.innerHTML = `<img id="speedmap-${validRaceNum}" class="speedmap-image" alt="Race ${validRaceNum} Speed Map" />`;
            }
            Utils.$(`#speedmap-${validRaceNum}`).src = base64String;
            Utils.$(`#speedmap-${validRaceNum}`).style.display = 'block';
        } catch (error) {
            console.error(`Error loading speedmap for race ${raceNum}:`, error);
        }
    },
    
    async loadAll() {
        for (const img of Utils.$$('.speedmap-image')) {
            await this.load(img.id.replace('speedmap-', ''));
        }
    }
};

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
        this.columns.filter(col => col.type).forEach(col => {
            preferred[col.name] = col.type === 'max' ? -Infinity : Infinity;
        });
        
        runnerRows.forEach(row => {
            this.columns.filter(col => col.type).forEach(col => {
                const textValue = row.cells[col.index]?.textContent.trim();
                if (textValue === '-') return;
                const value = Utils.parseNum(textValue, col.type === 'max' ? -Infinity : Infinity);
                if (col.type === 'max' && value > preferred[col.name]) preferred[col.name] = value;
                else if (col.type === 'min' && value > 0 && value < preferred[col.name]) preferred[col.name] = value;
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
        const horseCounts = new Map();
        
        runnerRows.forEach(row => {
            Utils.removeClass(Array.from(row.cells), 'preferred-cell');
            let count = 0;
            
            this.columns.forEach(col => {
                const cell = row.cells[col.index];
                const value = cell?.textContent.trim();
                if (uniformColumns.has(col.name) || value === '-') return;
                
                let isPreferred = false;
                if (col.check) {
                    isPreferred = col.check(value);
                } else if (col.type && racePreferred[col.name] !== undefined) {
                    const numValue = Utils.parseNum(value, col.type === 'max' ? -Infinity : Infinity);
                    isPreferred = numValue === racePreferred[col.name] && (col.type === 'max' || numValue > 0);
                }
                
                if (isPreferred) { Utils.addClass(cell, 'preferred-cell'); count++; }
            });
            horseCounts.set(row.dataset.horse, count);
        });
        
        const maxCount = Math.max(...horseCounts.values());
        runnerRows.forEach(row => {
            const count = horseCounts.get(row.dataset.horse);
            Utils.removeClass(row, 'most-preferred-horse');
            Utils.$('.most-preferred-badge', row)?.remove();
            
            if (count === maxCount && maxCount > 0) {
                Utils.addClass(row, 'most-preferred-horse');
                const nameCell = row.cells[4];
                if (nameCell && !Utils.$('.most-preferred-badge', nameCell)) {
                    const badge = document.createElement('span');
                    badge.className = 'most-preferred-badge';
                    badge.textContent = `${count}★`;
                    badge.title = `${count} preferred attribute${count > 1 ? 's' : ''}`;
                    nameCell.appendChild(badge);
                }
            }
        });
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
    charts: new Map(),
    styleColors: { 'FrontRunner': '#48bb78', 'Pacer': '#667eea', 'Closer': '#f56565', 'Unknown': '#a0aec0' },
    
    draw(raceNum) {
        const canvas = Utils.$(`#fav-style-chart-${raceNum}`);
        if (!canvas) return;
        
        const raceContent = Utils.$(`#race-${raceNum}`);
        if (!raceContent) return;
        
        const distribution = Utils.$$('.fav-style', raceContent).reduce((dist, cell) => {
            const style = cell.textContent.trim();
            if (style) dist[style] = (dist[style] || 0) + 1;
            return dist;
        }, {});
        
        const entries = Object.entries(distribution).sort((a, b) => b[1] - a[1]);
        if (this.charts.has(raceNum)) this.charts.get(raceNum).destroy();
        if (!entries.length) return;
        
        const labels = entries.map(([style]) => style);
        const data = entries.map(([, count]) => count);
        const colors = labels.map(s => this.styleColors[s] || '#a0aec0');
        
        this.charts.set(raceNum, new Chart(canvas.getContext('2d'), {
            type: 'pie',
            data: { labels, datasets: [{ data, backgroundColor: colors, borderColor: '#fff', borderWidth: 2 }] },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 8,
                            font: { size: 10 },
                            generateLabels: chart => {
                                const d = chart.data;
                                if (d.labels.length && d.datasets.length) {
                                    const ds = d.datasets[0];
                                    const total = ds.data.reduce((a, b) => a + b, 0);
                                    return d.labels.map((label, i) => ({
                                        text: `${label}: ${ds.data[i]} (${((ds.data[i] / total) * 100).toFixed(1)}%)`,
                                        fillStyle: ds.backgroundColor[i],
                                        hidden: false,
                                        index: i
                                    }));
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                return `${ctx.label}: ${ctx.parsed} (${((ctx.parsed / total) * 100).toFixed(1)}%)`;
                            }
                        }
                    }
                }
            }
        }));
    },
    
    update(raceNum) {
        const rc = Utils.$(`#race-${raceNum}`);
        if (this.charts.has(raceNum) || rc?.classList.contains('active')) this.draw(raceNum);
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
            if (!FavStyleChart.charts.has(validRaceNum)) FavStyleChart.draw(validRaceNum);
            PreferredHighlight.update(validRaceNum);
        } catch (error) {
            console.error('Error showing race:', error);
        }
    },
    
    updateExpandAllButtonState(raceNum) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        const expandAllBtn = Utils.$('.expand-all-btn', raceContent);
        const detailsRows = Utils.$$('.runner-details-row', raceContent);
        const allExpanded = detailsRows.length > 0 && detailsRows.every(row => row.classList.contains('expanded'));
        
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
            if (!header) return;
            
            const allHeaders = Utils.$$('thead th.sortable', table);
            const rows = Utils.$$('tr', tbody).filter((_, i) => i % 2 === 0);
            const isAscending = !header.classList.contains('sort-asc');
            
            allHeaders.forEach(h => {
                Utils.removeClass(h, ['sort-asc', 'sort-desc']);
                const arrow = Utils.$('.sort-arrow', h);
                if (arrow) arrow.textContent = '⇅';
            });
            
            rows.sort((a, b) => {
                const getValue = (row) => {
                    const val = row.cells[columnIndex].textContent.trim();
                    if (type === 'number' && val === '-') return Infinity;
                    return type === 'number' ? Utils.parseNum(val, -Infinity) : val.toLowerCase();
                };
                const [aComp, bComp] = [getValue(a), getValue(b)];
                return isAscending ? (aComp > bComp ? 1 : aComp < bComp ? -1 : 0) : 
                                     (aComp < bComp ? 1 : aComp > bComp ? -1 : 0);
            });
            
            Utils.addClass(header, isAscending ? 'sort-asc' : 'sort-desc');
            const arrow = Utils.$('.sort-arrow', header);
            if (arrow) arrow.textContent = isAscending ? '▲' : '▼';
            
            rows.forEach(row => {
                tbody.appendChild(row);
                if (row.nextElementSibling) tbody.appendChild(row.nextElementSibling);
            });
            
            PreferredHighlight.update(validRaceNum);
        } catch (error) {
            console.error('Error sorting table:', error);
        }
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

const App = {
    init() {
        console.log('Initializing HKJC Race Info...');
        const savedRaceTab = sessionStorage.getItem('activeRaceTab');
        if (savedRaceTab && Utils.$(`#tab-${savedRaceTab}`)) UI.showRace(savedRaceTab);
        
        const activeRaceNum = Utils.$('.race-content.active')?.id.replace('race-', '');
        Speedmap.loadAll();
        FavStyleChart.initAll();
        PreferredHighlight.initAll();
        Odds.startPolling();
        RunnerDetails.prefetchAll(activeRaceNum).catch(error => 
            console.error('Error in background prefetch:', error));
        console.log('Application initialized successfully');
    },
    
    cleanup() {
        Odds.stopPolling();
        RequestQueue.clear();
        Cache.clear();
        FavStyleChart.charts.forEach(chart => chart.destroy());
        FavStyleChart.charts.clear();
    }
};

window.showRace = (raceNum) => UI.showRace(raceNum);
window.toggleRunnerHistory = (row, raceNum, horseNo, going, track, dist) => 
    RunnerDetails.toggle(row, raceNum, horseNo, going, track, dist);
window.toggleAllRunners = (raceNum, btn) => RunnerDetails.toggleAll(raceNum, btn);
window.sortTable = (raceNum, colIdx, type) => UI.sortTable(raceNum, colIdx, type);
window.openTrackWorkoutVideo = (date, raceNum) => UI.openTrackWorkoutVideo(date, raceNum);
window.openTipsIndex = (raceNum) => UI.openTipsIndex(raceNum);

document.addEventListener('DOMContentLoaded', () => App.init());
window.addEventListener('beforeunload', () => App.cleanup());

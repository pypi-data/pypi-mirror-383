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
        const classes = Array.isArray(className) ? className : [className];
        const els = Array.isArray(elements) ? elements : [elements];
        els.forEach(el => el && classes.forEach(cls => el.classList.add(cls)));
    },
    
    removeClass(elements, className) {
        const classes = Array.isArray(className) ? className : [className];
        const els = Array.isArray(elements) ? elements : [elements];
        els.forEach(el => el && classes.forEach(cls => el.classList.remove(cls)));
    },
    
    toggleClass(elements, className, force) {
        const els = Array.isArray(elements) ? elements : [elements];
        els.forEach(el => el?.classList.toggle(className, force));
    },
    
    parseNum(value, fallback = 0) {
        const num = parseFloat(value);
        return isNaN(num) ? fallback : num;
    },
    
    makeCacheKey(...parts) {
        return parts.join('-');
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
    },
    
    fetchParetoData(raceNum, exclude = '', abortSignal = null) {
        return RequestQueue.enqueue(async () => {
            const url = `/plarec/${Utils.validateRaceNum(raceNum)}${exclude ? `?exclude=${exclude}` : ''}`;
            return (await this.fetch(url, { signal: abortSignal })).json();
        }, 1);
    },
    
    fetchQParetoData(raceNum, banker, exclude = '', filter = false, abortSignal = null) {
        return RequestQueue.enqueue(async () => {
            const url = `/qprec/${Utils.validateRaceNum(raceNum)}/${banker}?exclude=${exclude}&filter=${filter}`;
            return (await this.fetch(url, { signal: abortSignal })).json();
        }, 1);
    },
    
    fetchPLAData(raceNum, cover) {
        return RequestQueue.enqueue(async () => 
            (await this.fetch(`/pla/${Utils.validateRaceNum(raceNum)}/${cover}`)).json(), 0);
    },
    
    fetchQPLData(raceNum, banker, cover, filter) {
        return RequestQueue.enqueue(async () => {
            const url = `/qp/${Utils.validateRaceNum(raceNum)}/${banker}/${cover}?filter=${filter}`;
            return (await this.fetch(url)).json();
        }, 0);
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

const App = {
    init() {
        console.log('Initializing HKJC Race Info...');
        const savedRaceTab = sessionStorage.getItem('activeRaceTab');
        if (savedRaceTab && Utils.$(`#tab-${savedRaceTab}`)) UI.showRace(savedRaceTab);
        
        const activeRaceNum = Utils.$('.race-content.active')?.id.replace('race-', '');
        Speedmap.loadAll();
        FavStyleChart.initAll();
        PreferredHighlight.initAll();
        TradeCalculator.initAll();
        Odds.startPolling();
        RunnerDetails.prefetchAll(activeRaceNum).catch(error => 
            console.error('Error in background prefetch:', error));
        console.log('Application initialized successfully');
    },
    
    cleanup() {
        Odds.stopPolling();
        RequestQueue.clear();
        Cache.clear();
    }
};

window.showRace = (raceNum) => UI.showRace(raceNum);
window.toggleRunnerHistory = (row, raceNum, horseNo, going, track, dist) => 
    RunnerDetails.toggle(row, raceNum, horseNo, going, track, dist);
window.toggleAllRunners = (raceNum, btn) => RunnerDetails.toggleAll(raceNum, btn);
window.sortTable = (raceNum, colIdx, type) => UI.sortTable(raceNum, colIdx, type);
window.openTrackWorkoutVideo = (date, raceNum) => UI.openTrackWorkoutVideo(date, raceNum);
window.openTipsIndex = (raceNum) => UI.openTipsIndex(raceNum);
window.showTradeTab = (raceNum, tabName) => TradeCalculator.showTab(raceNum, tabName);
window.toggleParetoExclude = (raceNum, type, runnerNo) => TradeCalculator.toggleParetoExclude(raceNum, type, runnerNo);
window.toggleCover = (raceNum, type, runnerNo) => TradeCalculator.toggleCover(raceNum, type, runnerNo);
window.selectBanker = (raceNum, runnerNo) => TradeCalculator.selectBanker(raceNum, runnerNo);
window.toggleFilter = (raceNum) => TradeCalculator.toggleFilter(raceNum);
window.calculatePLA = (raceNum) => TradeCalculator.calculatePLA(raceNum);
window.calculateQPL = (raceNum) => TradeCalculator.calculateQPL(raceNum);

document.addEventListener('DOMContentLoaded', () => App.init());
window.addEventListener('beforeunload', () => App.cleanup());

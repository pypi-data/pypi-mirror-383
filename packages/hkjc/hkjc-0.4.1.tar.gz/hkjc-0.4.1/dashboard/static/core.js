// HKJC Race Info - Core Infrastructure
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


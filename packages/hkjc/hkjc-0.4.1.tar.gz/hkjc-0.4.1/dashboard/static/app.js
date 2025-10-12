// HKJC Race Info - Application Bootstrap
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


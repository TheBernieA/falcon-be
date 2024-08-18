// globalState.mjs
let autoTrading = false;
let isAnalyzing = false;

export function getAutoTrading() {
    return autoTrading;
}

export function setAutoTrading(value) {
    autoTrading = value;
}

export function getIsAnalyzing() {
    return isAnalyzing;
}

export function setIsAnalyzing(value) {
    isAnalyzing = value;
}

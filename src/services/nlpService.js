const nlpParse = (query) => {
    const queryLower = query.toLowerCase();

    if (queryLower.includes("failed") && queryLower.includes("login")) {
        return { intent: "find_failed_logins" };
    } else if (queryLower.includes("malware")) {
        return { intent: "find_malware" };
    } else if ((queryLower.includes("count") || queryLower.includes("chart")) && queryLower.includes("host")) {
        return { intent: "count_alerts_by_host" };
    } else {
        return { intent: "unknown" };
    }
};

// This line makes the nlpParse function available to other files
module.exports = { nlpParse };
// Progression and Difficulty Scaling Systems

// Wealth Curves - Defines how wealth impacts player growth and game difficulty
const wealthCurves = (wealth) => {
    return (wealth * 0.1) + 1; // Example calculation
};

// Heat Escalation Formulas - Defines how heat increases with player actions
const heatEscalation = (playerActions) => {
    return playerActions * 2; // Example calculation
};

// Police Response Scaling - Defines police response rates based on player heat
const policeResponseScaling = (heat) => {
    if (heat < 5) return 'Low';
    else if (heat < 15) return 'Moderate';
    else return 'High';
};

// Market Volatility - Defines how market prices fluctuate
const marketVolatility = (resourceAvailability) => {
    return Math.random() > 0.5 ? 'Stable' : 'Volatile';
};

// NPC Behavior Evolution - Defines how NPCs adapt based on player actions
const npcBehaviorEvolution = (playerInteractions) => {
    return playerInteractions > 10 ? 'Adaptive' : 'Static';
};

// Collapse Trigger Accumulation - Defines conditions for system collapse
const collapseTriggerAccumulation = (accruedTriggers) => {
    return accruedTriggers > 20 ? 'Crisis' : 'Stable';
};

// Exporting the functions for use in other parts of the game
module.exports = {
    wealthCurves,
    heatEscalation,
    policeResponseScaling,
    marketVolatility,
    npcBehaviorEvolution,
    collapseTriggerAccumulation
};

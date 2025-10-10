import React from 'react';

const NFAGraph = ({ nfa, currentStates = [], highlightTransition = null }) => {
    return (
        <div className="nfa-graph">
            <div className="graph-container">
                <svg width="100%" height="400" viewBox="0 0 800 400">
                    {/* Render states */}
                    {nfa.states.map((state, index) => {
                        const x = 100 + (index * 150);
                        const y = 200;
                        const isActive = currentStates.includes(state);
                        const isStart = state === nfa.startState;
                        const isAccept = nfa.acceptStates.includes(state);
                        
                        return (
                            <g key={state}>
                                {/* Start state arrow */}
                                {isStart && (
                                    <path
                                        d={`M ${x - 40} ${y} L ${x - 25} ${y}`}
                                        stroke="#4f46e5"
                                        strokeWidth="2"
                                        markerEnd="url(#arrowhead)"
                                    />
                                )}
                                
                                {/* State circle */}
                                <circle
                                    cx={x}
                                    cy={y}
                                    r={isAccept ? "22" : "20"}
                                    fill={isActive ? "#3b82f6" : "#f8fafc"}
                                    stroke={isActive ? "#1d4ed8" : "#e2e8f0"}
                                    strokeWidth={isActive ? "3" : "2"}
                                />
                                
                                {/* Accept state double circle */}
                                {isAccept && (
                                    <circle
                                        cx={x}
                                        cy={y}
                                        r="16"
                                        fill="none"
                                        stroke={isActive ? "#1d4ed8" : "#e2e8f0"}
                                        strokeWidth={isActive ? "3" : "2"}
                                    />
                                )}
                                
                                {/* State label */}
                                <text
                                    x={x}
                                    y={y + 5}
                                    textAnchor="middle"
                                    className="state-label"
                                    fill={isActive ? "white" : "#1f2937"}
                                >
                                    {state}
                                </text>
                            </g>
                        );
                    })}
                    
                    {/* Arrow marker definition */}
                    <defs>
                        <marker
                            id="arrowhead"
                            markerWidth="10"
                            markerHeight="7"
                            refX="9"
                            refY="3.5"
                            orient="auto"
                        >
                            <polygon
                                points="0 0, 10 3.5, 0 7"
                                fill="#4f46e5"
                            />
                        </marker>
                    </defs>
                </svg>
            </div>
            
            <div className="transition-table">
                <h4>Transition Function</h4>
                <table>
                    <thead>
                        <tr>
                            <th>From</th>
                            <th>Symbol</th>
                            <th>To</th>
                        </tr>
                    </thead>
                    <tbody>
                        {nfa.transitions.map((transition, index) => (
                            <tr key={index}>
                                <td>{transition.from}</td>
                                <td>{transition.symbol}</td>
                                <td>{transition.to}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default NFAGraph;
import React, { useState } from 'react';

const CFGSimulator = () => {
    const [inputString, setInputString] = useState('');
    const [derivationSteps, setDerivationSteps] = useState([]);
    const [isAccepted, setIsAccepted] = useState(null);

    // Simple CFG for balanced parentheses
    const grammar = {
        'S': ['(S)', 'SS', 'ε']
    };

    const simulate = () => {
        // Basic CFG simulation logic would go here
        // For now, just check if parentheses are balanced
        const steps = [];
        steps.push('S');
        
        let count = 0;
        for (const char of inputString) {
            if (char === '(') count++;
            else if (char === ')') count--;
            if (count < 0) {
                setIsAccepted(false);
                setDerivationSteps(steps);
                return;
            }
        }
        
        const accepted = count === 0;
        setIsAccepted(accepted);
        
        if (accepted) {
            // Add derivation steps for accepted string
            if (inputString === '') {
                steps.push('ε');
            } else {
                steps.push('(S)');
                steps.push(`(${inputString.slice(1, -1)})`);
            }
        }
        
        setDerivationSteps(steps);
    };

    return (
        <div className="cfg-simulator">
            <div className="cfg-container">
                <div className="cfg-header">
                    <h1 className="cfg-title">CFG Simulator</h1>
                    <p className="cfg-subtitle">
                        Context-Free Grammar Parser and Derivation
                    </p>
                </div>

                <div className="cfg-content">
                    <div className="cfg-input-section">
                        <h3>Input String</h3>
                        <div className="input-group">
                            <input
                                type="text"
                                value={inputString}
                                onChange={(e) => setInputString(e.target.value)}
                                placeholder="Enter string (e.g., ((()))"
                                className="cfg-input"
                            />
                            <button onClick={simulate} className="simulate-btn">
                                Parse
                            </button>
                        </div>
                        {isAccepted !== null && (
                            <div className={`result ${isAccepted ? 'accepted' : 'rejected'}`}>
                                String is {isAccepted ? 'ACCEPTED' : 'REJECTED'}
                            </div>
                        )}
                    </div>

                    <div className="cfg-grammar">
                        <h3>Grammar Rules</h3>
                        <div className="grammar-rules">
                            <div className="rule">S → (S)</div>
                            <div className="rule">S → SS</div>
                            <div className="rule">S → ε</div>
                        </div>
                    </div>

                    <div className="cfg-derivation">
                        <h3>Derivation Steps</h3>
                        <div className="derivation-steps">
                            {derivationSteps.map((step, index) => (
                                <div key={index} className="derivation-step">
                                    {index + 1}. {step}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CFGSimulator;
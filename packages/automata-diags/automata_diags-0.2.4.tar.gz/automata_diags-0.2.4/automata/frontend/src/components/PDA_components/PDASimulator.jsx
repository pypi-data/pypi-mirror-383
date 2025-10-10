import React, { useState } from 'react';

const PDASimulator = () => {
    const [inputString, setInputString] = useState('');
    const [stack, setStack] = useState(['Z0']); // Initial stack symbol
    const [currentState, setCurrentState] = useState('q0');
    const [isAccepted, setIsAccepted] = useState(null);

    // Simple PDA for balanced parentheses
    const transitions = [
        { from: 'q0', to: 'q0', input: '(', stackTop: 'Z0', stackPush: '(Z0' },
        { from: 'q0', to: 'q0', input: '(', stackTop: '(', stackPush: '((' },
        { from: 'q0', to: 'q0', input: ')', stackTop: '(', stackPush: '' },
        { from: 'q0', to: 'q1', input: 'ε', stackTop: 'Z0', stackPush: 'Z0' },
    ];

    const simulate = () => {
        // Basic PDA simulation logic would go here
        // For now, just check if parentheses are balanced
        let count = 0;
        for (const char of inputString) {
            if (char === '(') count++;
            else if (char === ')') count--;
            if (count < 0) {
                setIsAccepted(false);
                return;
            }
        }
        setIsAccepted(count === 0);
    };

    return (
        <div className="pda-simulator">
            <div className="pda-container">
                <div className="pda-header">
                    <h1 className="pda-title">PDA Simulator</h1>
                    <p className="pda-subtitle">
                        Pushdown Automaton for Context-Free Languages
                    </p>
                </div>

                <div className="pda-content">
                    <div className="pda-input-section">
                        <h3>Input String</h3>
                        <div className="input-group">
                            <input
                                type="text"
                                value={inputString}
                                onChange={(e) => setInputString(e.target.value)}
                                placeholder="Enter string (e.g., ((()))"
                                className="pda-input"
                            />
                            <button onClick={simulate} className="simulate-btn">
                                Simulate
                            </button>
                        </div>
                        {isAccepted !== null && (
                            <div className={`result ${isAccepted ? 'accepted' : 'rejected'}`}>
                                String is {isAccepted ? 'ACCEPTED' : 'REJECTED'}
                            </div>
                        )}
                    </div>

                    <div className="pda-visualization">
                        <div className="stack-display">
                            <h3>Stack</h3>
                            <div className="stack">
                                {stack.map((symbol, index) => (
                                    <div key={index} className="stack-item">
                                        {symbol}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="state-display">
                            <h3>Current State</h3>
                            <div className="current-state">{currentState}</div>
                        </div>
                    </div>

                    <div className="pda-transitions">
                        <h3>Transition Function</h3>
                        <div className="transitions-list">
                            <p>δ(q₀, '(', Z₀) = {'{q₀, (Z₀}'}</p>
                            <p>δ(q₀, '(', '(') = {'{q₀, (('}</p>
                            <p>δ(q₀, ')', '(') = {'{q₀, ε}'}</p>
                            <p>δ(q₀, ε, Z₀) = {'{q₁, Z₀}'}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PDASimulator;
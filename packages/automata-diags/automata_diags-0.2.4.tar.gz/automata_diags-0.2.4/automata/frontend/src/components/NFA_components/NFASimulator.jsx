import React, { useState, useEffect } from 'react';
import './stylings/NFASimulator.css';
import NFAGraph from './NFAGraph';
import { NFAControlPanel } from './NFAControlPanel';
import { NFATestCases } from './NFATestCases';
import { useExamples } from './examples';
import { useNFA } from './useNFA';

const NFASimulator = () => {
    const { examples } = useExamples();
    const [currentExampleName, setCurrentExampleName] = useState('basic_nfa');
    
    const nfa = useNFA({
        states: examples['basic_nfa'].states,
        alphabet: examples['basic_nfa'].alphabet,
        transitions: examples['basic_nfa'].transitions,
        startState: examples['basic_nfa'].startState,
        acceptStates: examples['basic_nfa'].acceptStates,
    });

    const [inputString, setInputString] = useState('');
    const [simulationSteps, setSimulationSteps] = useState([]);
    const [currentStep, setCurrentStep] = useState(-1);
    const [isPlaying, setIsPlaying] = useState(false);
    const [playbackSpeed, setPlaybackSpeed] = useState(500);

    const isComplete = currentStep >= 0 && currentStep === simulationSteps.length - 1;
    const isAccepted = isComplete && simulationSteps[currentStep]?.accepted;

    // Auto-play simulation
    useEffect(() => {
        let timer;
        if (isPlaying && currentStep < simulationSteps.length - 1) {
            timer = setTimeout(() => {
                setCurrentStep(currentStep + 1);
            }, playbackSpeed);
        } else if (currentStep >= simulationSteps.length - 1) {
            setIsPlaying(false);
        }
        return () => clearTimeout(timer);
    }, [isPlaying, currentStep, simulationSteps.length, playbackSpeed]);

    const simulateString = () => {
        setSimulationSteps([]);
        setCurrentStep(-1);

        let steps = [];
        let currentStates = new Set([nfa.startState]);

        // Add epsilon closure for start state
        currentStates = getEpsilonClosure(currentStates, nfa.transitions);

        // Initial step
        steps.push({
            states: Array.from(currentStates),
            remainingInput: inputString,
            description: `Starting in states ${Array.from(currentStates).join(', ')}`,
            transition: null,
            accepted: false
        });

        // Process each symbol
        for (let i = 0; i < inputString.length; i++) {
            const symbol = inputString[i];
            const nextStates = new Set();

            // Find all transitions for current symbol from current states
            currentStates.forEach(state => {
                const validTransitions = nfa.transitions.filter(t => 
                    t.from === state && t.symbol === symbol
                );
                validTransitions.forEach(t => nextStates.add(t.to));
            });

            // Add epsilon closure for next states
            const closureStates = getEpsilonClosure(nextStates, nfa.transitions);
            currentStates = closureStates;

            steps.push({
                states: Array.from(currentStates),
                remainingInput: inputString.slice(i + 1),
                description: `Read '${symbol}', now in states ${Array.from(currentStates).join(', ')}`,
                transition: { symbol, from: steps[i].states, to: Array.from(currentStates) },
                accepted: false
            });
        }

        // Final acceptance check
        const finalAccepted = Array.from(currentStates).some(state => 
            nfa.acceptStates.includes(state)
        );
        
        if (steps.length > 0) {
            steps[steps.length - 1].accepted = finalAccepted;
            steps[steps.length - 1].description += finalAccepted ? ' - ACCEPTED' : ' - REJECTED';
        }

        setSimulationSteps(steps);
    };

    const getEpsilonClosure = (states, transitions) => {
        const closure = new Set(states);
        const stack = Array.from(states);

        while (stack.length > 0) {
            const state = stack.pop();
            const epsilonTransitions = transitions.filter(t => 
                t.from === state && (t.symbol === 'ε' || t.symbol === 'epsilon')
            );
            
            epsilonTransitions.forEach(t => {
                if (!closure.has(t.to)) {
                    closure.add(t.to);
                    stack.push(t.to);
                }
            });
        }

        return closure;
    };

    const loadExample = (exampleName) => {
        const example = examples[exampleName];
        if (example) {
            setCurrentExampleName(exampleName);
            nfa.loadDefinition(example);
            setInputString('');
            setSimulationSteps([]);
            setCurrentStep(-1);
            setIsPlaying(false);
        }
    };

    const resetSimulation = () => {
        setCurrentStep(-1);
        setIsPlaying(false);
    };

    const stepForward = () => {
        if (currentStep < simulationSteps.length - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const stepBackward = () => {
        if (currentStep > -1) {
            setCurrentStep(currentStep - 1);
        }
    };

    const togglePlayback = () => {
        if (simulationSteps.length === 0) {
            simulateString();
        }
        setIsPlaying(!isPlaying);
    };

    return (
        <div className="nfa-simulator-new">
            <div className="nfa-container">
                <div className="nfa-header">
                    <h1 className="nfa-title">NFA Simulator</h1>
                    <p className="nfa-subtitle">
                        Interactive Non-deterministic Finite Automaton with ε-transitions
                    </p>
                </div>

                <div className="nfa-example-selector">
                    <span className="nfa-selector-label">Choose Example:</span>
                    <div className="nfa-selector-buttons">
                        {Object.keys(examples).map(name => (
                            <button
                                key={name}
                                className={`nfa-selector-btn ${currentExampleName === name ? 'active' : ''}`}
                                onClick={() => loadExample(name)}
                            >
                                {examples[name].name}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="nfa-grid">
                    <div className="nfa-left-col">
                        <div className="nfa-graph-card">
                            <h3 className="nfa-card-title">NFA Visualization</h3>
                            <NFAGraph 
                                nfa={nfa} 
                                currentStates={currentStep >= 0 ? simulationSteps[currentStep]?.states || [] : []}
                                highlightTransition={currentStep >= 0 ? simulationSteps[currentStep]?.transition : null}
                            />
                        </div>

                        <div className="nfa-input-card">
                            <h3 className="nfa-card-title">Input String</h3>
                            <div className="nfa-input-group">
                                <input
                                    type="text"
                                    value={inputString}
                                    onChange={(e) => setInputString(e.target.value)}
                                    placeholder="Enter input string..."
                                    className="nfa-input"
                                />
                                <button 
                                    onClick={simulateString}
                                    className="nfa-simulate-btn"
                                >
                                    Simulate
                                </button>
                            </div>
                            <p className="nfa-input-help">
                                Use alphabet: {nfa.alphabet.join(', ')}. ε represents epsilon transitions.
                            </p>
                            {isComplete && (
                                <div className={`nfa-result ${isAccepted ? 'accepted' : 'rejected'}`}>
                                    String is {isAccepted ? 'ACCEPTED' : 'REJECTED'}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="nfa-right-col">
                        <NFAControlPanel 
                            onTogglePlayback={togglePlayback}
                            onStepForward={stepForward}
                            onStepBackward={stepBackward}
                            onReset={resetSimulation}
                            isPlaying={isPlaying}
                            canStepForward={currentStep < simulationSteps.length - 1}
                            canStepBackward={currentStep > -1}
                            speed={playbackSpeed}
                            onSpeedChange={setPlaybackSpeed}
                        />

                        <div className="nfa-steps-card">
                            <h3 className="nfa-card-title">Simulation Steps</h3>
                            <div className="nfa-step-display">
                                {currentStep >= 0 && simulationSteps[currentStep] ? (
                                    <div className="nfa-current-step">
                                        <div className="step-number">Step {currentStep + 1}</div>
                                        <div className="step-description">
                                            {simulationSteps[currentStep].description}
                                        </div>
                                        <div className="step-details">
                                            <div>Current States: {simulationSteps[currentStep].states.join(', ')}</div>
                                            <div>Remaining Input: "{simulationSteps[currentStep].remainingInput}"</div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="no-step">
                                        Click "Simulate" to begin simulation
                                    </div>
                                )}
                            </div>
                        </div>

                        <NFATestCases 
                            nfa={nfa}
                            onTestString={(testString) => {
                                setInputString(testString);
                                setSimulationSteps([]);
                                setCurrentStep(-1);
                                setIsPlaying(false);
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NFASimulator;
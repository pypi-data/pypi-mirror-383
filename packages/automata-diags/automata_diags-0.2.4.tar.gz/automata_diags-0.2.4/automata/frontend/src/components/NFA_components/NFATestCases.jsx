import React from 'react';

export const NFATestCases = ({ nfa, onTestString }) => {
    const testCases = [
        { input: 'ab', expected: true, description: 'Simple accepted string' },
        { input: 'aab', expected: true, description: 'Multiple a\'s accepted' },
        { input: 'ba', expected: false, description: 'Wrong order rejected' },
        { input: 'abb', expected: false, description: 'Extra b rejected' },
        { input: '', expected: false, description: 'Empty string' },
    ];

    const runTest = (testCase) => {
        onTestString(testCase.input);
    };

    return (
        <div className="nfa-test-card">
            <h3 className="nfa-card-title">Test Cases</h3>
            
            <div className="test-cases-list">
                {testCases.map((testCase, index) => (
                    <div key={index} className="test-case-item">
                        <div className="test-case-info">
                            <div className="test-input">"{testCase.input || 'ε'}"</div>
                            <div className="test-description">{testCase.description}</div>
                            <div className={`test-expected ${testCase.expected ? 'accept' : 'reject'}`}>
                                Expected: {testCase.expected ? 'Accept' : 'Reject'}
                            </div>
                        </div>
                        <button 
                            onClick={() => runTest(testCase)}
                            className="test-btn"
                        >
                            Test
                        </button>
                    </div>
                ))}
            </div>
            
            <div className="custom-test">
                <h4>Custom Test</h4>
                <p>Enter any string in the input box above and click "Simulate" to test it.</p>
            </div>
        </div>
    );
};
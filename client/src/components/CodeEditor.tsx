import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { submitSolution, runSolution } from '../api';

interface CodeEditorProps {
    problemId: string;
    templates?: string; // JSON string of templates
    testCases?: Array<{input: string, output: string}>;
    onSubmission?: (result: any) => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ problemId, templates, testCases = [], onSubmission }) => {
    const defaultBoilerplates: {[key: string]: string} = {
        python: 'class Solution:\n    def solution(self, args):\n        pass',
        cpp: 'class Solution {\npublic:\n    void solution() {\n        \n    }\n};',
        java: 'class Solution {\n    public void solution() {\n        \n    }\n}'
    };

    const [language, setLanguage] = useState<string>('python');
    const [code, setCode] = useState<string>('');
    const [output, setOutput] = useState<string>('');
    const [status, setStatus] = useState<string>('');
    const [boilerplates, setBoilerplates] = useState<{[key: string]: string}>(defaultBoilerplates);
    
    const [activeTab, setActiveTab] = useState(0);
    const [runOutput, setRunOutput] = useState<{output: string, error?: string} | null>(null);
    const [isRunning, setIsRunning] = useState(false);

    const [editorHeight, setEditorHeight] = useState(60); // percentage
    const [isDragging, setIsDragging] = useState(false);

    useEffect(() => {
        if (templates) {
            try {
                const parsed = JSON.parse(templates);
                setBoilerplates(prev => ({...prev, ...parsed}));
            } catch (e) {
                console.error("Failed to parse templates", e);
            }
        }
    }, [templates]);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!isDragging) return;
            // Calculate percentage relative to the container height (viewport - 60px navbar)
            const navbarHeight = 60;
            const containerHeight = window.innerHeight - navbarHeight;
            const relativeY = e.clientY - navbarHeight;
            const newHeight = (relativeY / containerHeight) * 100;
            
            if (newHeight > 20 && newHeight < 80) {
                setEditorHeight(newHeight);
            }
        };

        const handleMouseUp = () => {
            if (isDragging) {
                setIsDragging(false);
                document.body.style.cursor = 'default';
                document.body.style.userSelect = 'auto';
            }
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
             document.removeEventListener('mousemove', handleMouseMove);
             document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging]);

    const handleMouseDown = () => {
        setIsDragging(true);
        document.body.style.cursor = 'row-resize';
        document.body.style.userSelect = 'none';
    };

    useEffect(() => {
        setCode(boilerplates[language] || defaultBoilerplates[language] || '');
    }, [language, boilerplates]);

    const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setLanguage(e.target.value);
    };

    const handleEditorChange = (value: string | undefined) => {
        setCode(value || '');
    };

    const handleSubmit = async () => {
        try {
            setOutput('Running...');
            const result = await submitSolution(problemId, language, code);
            setOutput(result.output);
            setStatus(result.status);
            if (onSubmission) onSubmission(result);
        } catch (error) {
            console.error('Error executing code:', error);
            setOutput('Error executing code');
            setStatus('error');
            if (onSubmission) onSubmission({ status: 'error', output: 'Error executing code' });
        }
    };

    const handleRun = async () => {
        if (!testCases.length) return;
        setIsRunning(true);
        setRunOutput(null);
        try {
            const input = testCases[activeTab].input;
            const res = await runSolution(problemId, language, code, input);
            setRunOutput(res);
        } catch (error) {
            const err: any = error;
            console.error('Error running code:', err);
            let msg = 'Failed to run code';
            if (err.response) {
                if (err.response.status === 401) {
                    msg = 'Session expired/Invalid. Please Logout and Login again.';
                } else if (err.response.data && err.response.data.error) {
                    msg = err.response.data.error;
                }
            } else if (err.message) {
                 msg = err.message;
            }
            setRunOutput({ output: '', error: msg });
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ height: `${editorHeight}%`, display: 'flex', flexDirection: 'column', borderBottom: '1px solid #eee' }}>
                <div style={{ padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#fafafa', borderBottom: '1px solid #eee' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <select value={language} onChange={handleLanguageChange} style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #ccc' }}>
                            <option value="python">Python</option>
                            <option value="cpp">C++</option>
                            <option value="java">Java</option>
                        </select>
                        <button onClick={handleRun} disabled={isRunning} style={{ padding: '4px 12px', background: isRunning ? '#ccc' : '#f5f5f5', color: isRunning ? '#666' : '#333', border: '1px solid #ddd', cursor: 'pointer', borderRadius: '4px' }}>
                            {isRunning ? 'Running...' : 'Run Code'}
                        </button>
                        <button onClick={handleSubmit} style={{ padding: '4px 12px', background: '#2196f3', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px' }}>
                            Submit
                        </button>
                    </div>
                </div>

                <div style={{ flex: 1, overflow: 'hidden' }}>
                    <Editor
                        height="100%"
                        language={language}
                        value={code}
                        theme="light"
                        onChange={handleEditorChange}
                        options={{
                            minimap: { enabled: false },
                            scrollBeyondLastLine: false,
                            fontSize: 14,
                            automaticLayout: true,
                        }}
                    />
                </div>
            </div>

            <div 
                onMouseDown={handleMouseDown}
                style={{
                    height: '5px',
                    cursor: 'row-resize',
                    backgroundColor: '#ddd',
                    width: '100%',
                    zIndex: 10,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2196f3'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#ddd'}
            >
                 <div style={{width: '30px', height: '3px', backgroundColor: '#999', borderRadius: '2px', pointerEvents: 'none'}} />
            </div>

            <div style={{ height: `${100 - editorHeight}%`, overflowY: 'auto', backgroundColor: '#fff', display: 'flex', flexDirection: 'column' }}>
                {testCases.length > 0 ? (
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                        <div style={{ display: 'flex', borderBottom: '1px solid #eee', backgroundColor: '#fafafa' }}>
                            {testCases.map((_, idx) => (
                                <div 
                                    key={idx}
                                    onClick={() => { setActiveTab(idx); setRunOutput(null); }}
                                    style={{ 
                                        padding: '10px 20px', 
                                        cursor: 'pointer',
                                        borderBottom: activeTab === idx ? '2px solid #2196f3' : '2px solid transparent',
                                        borderRight: '1px solid #eee',
                                        fontWeight: activeTab === idx ? 'bold' : 'normal',
                                        backgroundColor: activeTab === idx ? 'white' : 'transparent',
                                        color: activeTab === idx ? '#2196f3' : '#666',
                                        fontSize: '13px'
                                    }}
                                >
                                    Case {idx + 1}
                                </div>
                            ))}
                        </div>
                        
                        <div style={{ padding: '20px' }}>
                            <div style={{ marginBottom: '20px' }}>
                                <div style={{ fontSize: '11px', color: '#666', marginBottom: '8px', textTransform: 'uppercase', fontWeight: 'bold' }}>Input</div>
                                <pre style={{ background: '#f7f9fa', padding: '12px', borderRadius: '4px', margin: 0, border: '1px solid #e1e4e8', fontSize: '13px', whiteSpace: 'pre-wrap', wordWrap: 'break-word', fontFamily: 'Menlo, monospace' }}>{testCases[activeTab].input}</pre>
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <div style={{ fontSize: '11px', color: '#666', marginBottom: '8px', textTransform: 'uppercase', fontWeight: 'bold' }}>Expected Output</div>
                                <pre style={{ background: '#f7f9fa', padding: '12px', borderRadius: '4px', margin: 0, border: '1px solid #e1e4e8', fontSize: '13px', whiteSpace: 'pre-wrap', wordWrap: 'break-word', fontFamily: 'Menlo, monospace' }}>{testCases[activeTab].output}</pre>
                            </div>
                            
                            {runOutput && (
                                <div style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
                                    <div style={{ fontSize: '11px', marginBottom: '8px', textTransform: 'uppercase', fontWeight: 'bold', color: runOutput.error ? '#d32f2f' : '#2e7d32' }}>Your Output</div>
                                    <pre style={{ 
                                        background: runOutput.error ? '#fff5f5' : '#f0fcf4', 
                                        padding: '12px', 
                                        margin: 0,
                                        borderRadius: '4px',
                                        color: runOutput.error ? '#c62828' : '#1b5e20',
                                        width: '100%',
                                        boxSizing: 'border-box',
                                        fontSize: '13px',
                                        border: runOutput.error ? '1px solid #ffcdd2' : '1px solid #c8e6c9',
                                        whiteSpace: 'pre-wrap',
                                        wordWrap: 'break-word',
                                        fontFamily: 'Menlo, monospace'
                                    }}>
                                        {runOutput.error ? runOutput.error : runOutput.output}
                                    </pre>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    <div style={{ padding: '20px', color: '#666', textAlign: 'center' }}>No test cases available.</div>
                )}
            </div>
        </div>
    );
};

export default CodeEditor;

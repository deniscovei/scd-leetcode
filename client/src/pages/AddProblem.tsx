import React, { useState, useEffect } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { createProblem, fetchProblem, updateProblem } from '../api';

interface TestCase {
    id: number;
    input: string;
    output: string;
}

interface LanguageData {
    template: string;
    driver: string;
    timeout: number;
}

const AVAILABLE_LANGUAGES = ['python', 'cpp', 'java'];

const AddProblem: React.FC = () => {
    const history = useHistory();
    const { id } = useParams<{ id: string }>();
    const isEditMode = !!id;

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [difficulty, setDifficulty] = useState('Easy');
    const [tags, setTags] = useState('');
    
    // Per-language configuration
    const [languageData, setLanguageData] = useState<{[key: string]: LanguageData}>({
        python: {
            template: 'class Solution:\n    def solve(self, args):\n        pass',
            driver: 'import sys\nimport json\n\nif __name__ == "__main__":\n    # read from sys.stdin\n    pass',
            timeout: 2.0
        },
        cpp: {
            template: 'class Solution {\npublic:\n    void solve() {\n        \n    }\n};',
            driver: 'using namespace std;\n\nint main() {\n    return 0;\n}',
            timeout: 1.0
        },
        java: {
            template: 'class Solution {\n    public void solve() {\n        \n    }\n}',
            driver: 'class Driver {\n    public static void main(String[] args) {\n        \n    }\n}',
            timeout: 2.0
        }
    });

    const [testCases, setTestCases] = useState<TestCase[]>([
        { id: 1, input: '', output: '' }
    ]);

    const [activeTab, setActiveTab] = useState<'details' | 'testcases' | 'code'>('details');
    const [activeLang, setActiveLang] = useState('python');

    useEffect(() => {
        if (id) {
            const loadProblem = async () => {
                try {
                    const data = await fetchProblem(id);
                    setTitle(data.title);
                    setDescription(data.description);
                    setDifficulty(data.difficulty);
                    setTags(data.tags || '');
                    
                    if (data.test_cases) {
                        try {
                            const tcs = JSON.parse(data.test_cases);
                            setTestCases(tcs.map((tc: any, idx: number) => ({ id: idx + 1, ...tc })));
                        } catch (e) {
                            console.error("Failed to parse test cases", e);
                        }
                    }
                    
                    const templates = data.templates ? JSON.parse(data.templates) : {};
                    const drivers = data.drivers ? JSON.parse(data.drivers) : {};
                    const timeouts = data.time_limits ? JSON.parse(data.time_limits) : {};
                    
                    setLanguageData(prev => {
                        const next = { ...prev };
                        AVAILABLE_LANGUAGES.forEach(lang => {
                            if (!next[lang]) next[lang] = { template: '', driver: '', timeout: 1.0 };
                            if (templates[lang]) next[lang].template = templates[lang];
                            if (drivers[lang]) next[lang].driver = drivers[lang];
                            if (timeouts[lang]) next[lang].timeout = timeouts[lang];
                        });
                        return next;
                    });
                } catch (error) {
                    console.error('Error fetching problem details:', error);
                }
            };
            loadProblem();
        }
    }, [id]);

    const handleLanguageDataChange = (field: keyof LanguageData, value: string | number) => {
        setLanguageData(prev => ({
            ...prev,
            [activeLang]: {
                ...prev[activeLang],
                [field]: value
            }
        }));
    };

    const addTestCase = () => {
        setTestCases(prev => [
            ...prev,
            { id: prev.length + 1, input: '', output: '' }
        ]);
    };

    const updateTestCase = (id: number, field: 'input' | 'output', value: string) => {
        setTestCases(prev => prev.map(tc => 
            tc.id === id ? { ...tc, [field]: value } : tc
        ));
    };

    const removeTestCase = (id: number) => {
        setTestCases(prev => prev.filter(tc => tc.id !== id));
    };

    const handleSubmit = async () => {
        try {
            // Transform data for API
            const drivers: {[key: string]: string} = {};
            const templates: {[key: string]: string} = {};
            const timeLimits: {[key: string]: number} = {};

            AVAILABLE_LANGUAGES.forEach(lang => {
                drivers[lang] = languageData[lang].driver;
                templates[lang] = languageData[lang].template;
                timeLimits[lang] = languageData[lang].timeout;
            });

            const problemData = {
                title,
                description,
                difficulty,
                tags,
                test_cases: testCases.map(({input, output}) => ({input, output})),
                drivers: drivers,
                templates: templates,
                time_limits: timeLimits
            };

            if (isEditMode) {
                await updateProblem(id, problemData);
                alert('Problem updated successfully!');
            } else {
                await createProblem(problemData);
                alert('Problem created successfully!');
            }
            history.push('/');
        } catch (error) {
            console.error('Failed to save problem:', error);
            alert('Failed to save problem. See console for details.');
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', height: 'calc(100vh - 60px)', display: 'flex', flexDirection: 'column' }}>
            <h1 style={{ marginBottom: '20px' }}>{isEditMode ? 'Edit Problem' : 'Add New Problem'}</h1>
            
            <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: '20px' }}>
                <button 
                    style={{ padding: '10px 20px', background: activeTab === 'details' ? '#eee' : 'white', border: '1px solid #ddd', borderBottom: 'none', cursor: 'pointer' }}
                    onClick={() => setActiveTab('details')}
                >
                    Problem Details
                </button>
                <button 
                    style={{ padding: '10px 20px', background: activeTab === 'testcases' ? '#eee' : 'white', border: '1px solid #ddd', borderBottom: 'none', cursor: 'pointer' }}
                    onClick={() => setActiveTab('testcases')}
                >
                    Test Cases
                </button>
                <button 
                    style={{ padding: '10px 20px', background: activeTab === 'code' ? '#eee' : 'white', border: '1px solid #ddd', borderBottom: 'none', cursor: 'pointer' }}
                    onClick={() => setActiveTab('code')}
                >
                    Templates & Drivers
                </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '20px' }}>
                {activeTab === 'details' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                        <div>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Title:</label>
                            <input 
                                type="text" 
                                value={title} 
                                onChange={e => setTitle(e.target.value)} 
                                style={{ width: '100%', padding: '8px', fontSize: '16px' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Description:</label>
                            <textarea 
                                value={description} 
                                onChange={e => setDescription(e.target.value)} 
                                style={{ width: '100%', height: '200px', padding: '8px', fontSize: '14px', fontFamily: 'monospace' }}
                            />
                        </div>
                        <div style={{ display: 'flex', gap: '20px' }}>
                            <div>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Difficulty:</label>
                                <select 
                                    value={difficulty} 
                                    onChange={e => setDifficulty(e.target.value)}
                                    style={{ padding: '8px' }}
                                >
                                    <option value="Easy">Easy</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Hard">Hard</option>
                                </select>
                            </div>
                            <div style={{ flex: 1 }}>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Tags (comma separated):</label>
                                <input 
                                    type="text" 
                                    value={tags} 
                                    onChange={e => setTags(e.target.value)} 
                                    style={{ width: '100%', padding: '8px' }}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'testcases' && (
                    <div>
                        {testCases.map((tc, idx) => (
                            <div key={tc.id} style={{ marginBottom: '20px', padding: '15px', border: '1px solid #eee', borderRadius: '4px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                    <strong>Test Case #{idx + 1}</strong>
                                    <button onClick={() => removeTestCase(tc.id)} style={{ color: 'red', cursor: 'pointer', border: 'none', background: 'none' }}>Remove</button>
                                </div>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <div style={{ flex: 1 }}>
                                        <label>Input:</label>
                                        <textarea 
                                            value={tc.input} 
                                            onChange={e => updateTestCase(tc.id, 'input', e.target.value)}
                                            style={{ width: '100%', height: '80px', fontFamily: 'monospace' }}
                                        />
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <label>Output:</label>
                                        <textarea 
                                            value={tc.output} 
                                            onChange={e => updateTestCase(tc.id, 'output', e.target.value)}
                                            style={{ width: '100%', height: '80px', fontFamily: 'monospace' }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                        <button onClick={addTestCase} style={{ padding: '8px 16px', cursor: 'pointer' }}>+ Add Test Case</button>
                    </div>
                )}

                {activeTab === 'code' && (
                    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                         <div style={{ marginBottom: '15px' }}>
                            <label style={{ marginRight: '10px' }}>Language:</label>
                            <select value={activeLang} onChange={e => setActiveLang(e.target.value)} style={{ padding: '5px' }}>
                                {AVAILABLE_LANGUAGES.map(lang => (
                                    <option key={lang} value={lang}>{lang}</option>
                                ))}
                            </select>
                            
                            <label style={{ marginLeft: '20px', marginRight: '10px' }}>Time Limit (s):</label>
                            <input 
                                type="number" 
                                step="0.1" 
                                value={languageData[activeLang].timeout} 
                                onChange={e => handleLanguageDataChange('timeout', parseFloat(e.target.value))}
                                style={{ width: '60px', padding: '5px' }}
                            />
                        </div>

                        <div style={{ display: 'flex', gap: '20px', height: '500px' }}>
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                                <label style={{ marginBottom: '5px', fontWeight: 'bold' }}>Template ({activeLang}):</label>
                                <div style={{ flex: 1, border: '1px solid #ccc' }}>
                                    <Editor
                                        height="100%"
                                        language={activeLang}
                                        value={languageData[activeLang].template}
                                        onChange={val => handleLanguageDataChange('template', val || '')}
                                        options={{ minimap: { enabled: false }, scrollBeyondLastLine: false }}
                                    />
                                </div>
                            </div>
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                                <label style={{ marginBottom: '5px', fontWeight: 'bold' }}>Driver Code ({activeLang}):</label>
                                <div style={{ flex: 1, border: '1px solid #ccc' }}>
                                    <Editor
                                        height="100%"
                                        language={activeLang}
                                        value={languageData[activeLang].driver}
                                        onChange={val => handleLanguageDataChange('driver', val || '')}
                                        options={{ minimap: { enabled: false }, scrollBeyondLastLine: false }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div style={{ borderTop: '1px solid #ddd', padding: '20px 0', textAlign: 'right' }}>
                <button 
                    onClick={handleSubmit} 
                    style={{ 
                        padding: '12px 24px', 
                        backgroundColor: '#2196f3', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px', 
                        fontSize: '16px',
                        cursor: 'pointer'
                    }}
                >
                    {isEditMode ? 'Update Problem' : 'Create Problem'}
                </button>
            </div>
        </div>
    );
};

export default AddProblem;

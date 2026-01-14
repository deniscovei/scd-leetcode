import React, { useEffect, useState } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import ProblemDescription from '../components/ProblemDescription';
import CodeEditor from '../components/CodeEditor';
import { fetchProblem, fetchSubmissions, deleteProblem } from '../api';
import keycloak from '../keycloak';

const ProblemPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const history = useHistory();
    const [problem, setProblem] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [leftWidth, setLeftWidth] = useState(50); // percentage
    const [isDragging, setIsDragging] = useState(false);
    const [activeTab, setActiveTab] = useState<'description' | 'submissions'>('description');
    const [submissionResult, setSubmissionResult] = useState<any>(null);
    const [submissions, setSubmissions] = useState<any[]>([]);
    const [submissionView, setSubmissionView] = useState<'list' | 'detail'>('list');

    useEffect(() => {
        const getProblem = async () => {
            if (!id) return;
            try {
                const data = await fetchProblem(id);
                setProblem(data);
            } catch (error) {
                console.error('Error fetching problem:', error);
            } finally {
                setLoading(false);
            }
        };

        getProblem();
    }, [id]);

    useEffect(() => {
        if (activeTab === 'submissions' && id) {
             const getSubmissions = async () => {
                 try {
                     const data = await fetchSubmissions(id);
                     setSubmissions(data);
                 } catch (error) {
                     console.error('Error fetching submissions:', error);
                 }
             };
             getSubmissions();
        }
    }, [activeTab, id]);

    const handleMouseDown = () => {
        setIsDragging(true);
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    };

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!isDragging) return;
            const newWidth = (e.clientX / window.innerWidth) * 100;
            if (newWidth > 10 && newWidth < 90) {
                setLeftWidth(newWidth);
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

    const handleSubmission = (result: any) => {
        setSubmissionResult(result);
        setSubmissionView('detail');
        setActiveTab('submissions');
        // Refresh submissions list
        if (id) {
            fetchSubmissions(id).then(data => setSubmissions(data));
        }
    };

    const handleDelete = async () => {
        if (!id) return;
        if (window.confirm('Are you sure you want to delete this problem? This action cannot be undone.')) {
            try {
                await deleteProblem(id);
                history.push('/');
            } catch (error) {
                console.error('Error deleting problem:', error);
                alert('Failed to delete problem');
            }
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!problem) {
        return <div>Problem not found.</div>;
    }

    let examples: string[] = [];
    let parsedTestCases: any[] = [];
    if (problem.test_cases) {
        try {
            parsedTestCases = JSON.parse(problem.test_cases);
            // We do not show examples here as they are in the description
            // examples = parsedTestCases.map((tc: any) => `Input:\n${tc.input}\nOutput:\n${tc.output}`);
        } catch (e) {
            console.error("Failed to parse test cases", e);
        }
    }

    return (
        <div style={{ display: 'flex', height: 'calc(100vh - 60px)', width: '100%', overflow: 'hidden' }}>
            <div style={{ width: `${leftWidth}%`, overflowY: 'auto', padding: '20px', boxSizing: 'border-box' }}>
                <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: '15px' }}>
                    <div 
                        onClick={() => setActiveTab('description')}
                        style={{ 
                            padding: '10px 15px', 
                            cursor: 'pointer',
                            borderBottom: activeTab === 'description' ? '2px solid #2196f3' : 'none',
                            fontWeight: activeTab === 'description' ? 'bold' : 'normal'
                        }}
                    >
                        Description
                    </div>
                    <div 
                        onClick={() => { setActiveTab('submissions'); setSubmissionView('list'); }}
                        style={{ 
                            padding: '10px 15px', 
                            cursor: 'pointer',
                            borderBottom: activeTab === 'submissions' ? '2px solid #2196f3' : 'none',
                            fontWeight: activeTab === 'submissions' ? 'bold' : 'normal'
                        }}
                    >
                        Submissions
                    </div>
                </div>

                {activeTab === 'description' ? (
                    <>
                        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                            <h1 style={{ marginTop: 0, color: '#333' }}>{problem.title}</h1>
                            {problem.owner_username === (keycloak.tokenParsed?.preferred_username || keycloak.tokenParsed?.sub) && (
                                <div>
                                    <button
                                        onClick={() => history.push(`/edit-problem/${id}`)}
                                        style={{
                                            padding: '5px 10px',
                                            backgroundColor: '#ffa000',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            marginRight: '10px'
                                        }}
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={handleDelete}
                                        style={{
                                            padding: '5px 10px',
                                            backgroundColor: '#d32f2f',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        Delete
                                    </button>
                                </div>
                            )}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
                            <span style={{ 
                                padding: '4px 12px', 
                                borderRadius: '16px', 
                                fontSize: '12px', 
                                fontWeight: 'bold',
                                backgroundColor: problem.difficulty === 'Easy' ? '#e8f5e9' : problem.difficulty === 'Medium' ? '#fff3e0' : '#ffebee',
                                color: problem.difficulty === 'Easy' ? '#2e7d32' : problem.difficulty === 'Medium' ? '#ef6c00' : '#c62828',
                                marginRight: '10px'
                            }}>
                                {problem.difficulty}
                            </span>
                            <span style={{ fontSize: '12px', color: '#666' }}>{problem.tags}</span>
                        </div>
                        <ProblemDescription 
                            title={undefined} 
                            description={problem.description} 
                            examples={examples}
                        />
                    </>
                ) : (
                    <div>
                        {submissionView === 'list' ? (
                            <div>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ borderBottom: '1px solid #ddd', textAlign: 'left' }}>
                                            <th style={{ padding: '10px' }}>Status</th>
                                            <th style={{ padding: '10px' }}>Language</th>
                                            <th style={{ padding: '10px' }}>Date</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {submissions.map((sub, idx) => (
                                            <tr 
                                                key={idx} 
                                                onClick={() => { setSubmissionResult(sub); setSubmissionView('detail'); }}
                                                style={{ cursor: 'pointer', borderBottom: '1px solid #eee' }}
                                            >
                                                <td style={{ padding: '10px', color: sub.status === 'Accepted' ? 'green' : 'red' }}>{sub.status}</td>
                                                <td style={{ padding: '10px' }}>{sub.language}</td>
                                                <td style={{ padding: '10px' }}>{new Date(sub.created_at).toLocaleString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                {submissions.length === 0 && <p style={{ padding: '10px', color: '#666' }}>No submissions yet.</p>}
                            </div>
                        ) : (
                            <div>
                                <div 
                                    onClick={() => setSubmissionView('list')}
                                    style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', color: '#2196f3', marginBottom: '15px' }}
                                >
                                    <span style={{ marginRight: '5px' }}>&#8592;</span> All Submissions
                                </div>
                                <h3>Submission Result</h3>
                                {submissionResult ? (
                                    <div style={{ 
                                        padding: '15px', 
                                        backgroundColor: submissionResult.status === 'Accepted' ? '#e8f5e9' : '#ffebee',
                                        borderRadius: '4px',
                                        border: '1px solid #ddd'
                                    }}>
                                        <h4 style={{ marginTop: 0, color: submissionResult.status === 'Accepted' ? 'green' : 'red' }}>
                                            {submissionResult.status}
                                        </h4>
                                        <div style={{ marginBottom: '10px', fontSize: '12px', color: '#666' }}>Language: {submissionResult.language}</div>
                                        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                                            {submissionResult.output}
                                        </pre>
                                    </div>
                                ) : (
                                    <p>No submission selected.</p>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </div>
            
            <div 
                onMouseDown={handleMouseDown}
                style={{
                    width: '5px',
                    cursor: 'col-resize',
                    backgroundColor: '#ddd',
                    transition: 'background-color 0.2s',
                    height: '100%',
                    zIndex: 10,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2196f3'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#ddd'}
            >
                <div style={{width: '2px', height: '30px', backgroundColor: '#999', borderRadius: '2px', pointerEvents: 'none'}} />
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden', minWidth: 0 }}>
                <CodeEditor problemId={id} templates={problem.templates} testCases={parsedTestCases} onSubmission={handleSubmission} />
            </div>
        </div>
    );
};


export default ProblemPage;
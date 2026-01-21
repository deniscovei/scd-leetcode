import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchMyProblems, deleteProblem } from '../api';
import keycloak from '../keycloak';

const MyProblems: React.FC = () => {
    const [problems, setProblems] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const loadProblems = async () => {
         try {
             const data = await fetchMyProblems();
             setProblems(data);
         } catch (e) {
             console.error(e);
         } finally {
             setLoading(false);
         }
    };

    useEffect(() => {
        if (keycloak.authenticated) {
            loadProblems();
        }
    }, []);

    const handleDelete = async (problemId: number, problemTitle: string) => {
        if (!window.confirm(`Are you sure you want to delete "${problemTitle}"? This action cannot be undone.`)) {
            return;
        }
        try {
            await deleteProblem(problemId);
            // Reload problems list
            loadProblems();
        } catch (e: any) {
            alert(e.response?.data?.error || 'Failed to delete problem');
            console.error(e);
        }
    };
    
    const isAdmin = keycloak.tokenParsed?.preferred_username === 'admin';
    const title = isAdmin ? "All Problems (Admin View)" : "My Problems";

    if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;

    return (
        <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '0 20px' }}>
            <h1 style={{ marginBottom: '20px', color: '#262626' }}>{title}</h1>
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ backgroundColor: '#f8f9fa', color: '#666', borderBottom: '1px solid #eee' }}>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>#</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Title</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Difficulty</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Status</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {problems.map((p, index) => (
                            <tr key={p.id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '15px', color: '#888' }}>{p.id}</td>
                                <td style={{ padding: '15px' }}>
                                    <Link to={`/problems/${p.id}`} style={{ color: '#2c3e50', fontWeight: '500' }}>
                                        {p.title}
                                    </Link>
                                    <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                                        {p.tags}
                                    </div>
                                    {isAdmin && (
                                        <div style={{ fontSize: '10px', color: '#aaa', marginTop: '2px' }}>
                                            Owner: {p.owner_username || `ID: ${p.owner_id}`}
                                        </div>
                                    )}
                                </td>
                                <td style={{ padding: '15px' }}>
                                    <span style={{ 
                                        padding: '4px 8px', 
                                        borderRadius: '12px', 
                                        fontSize: '12px', 
                                        fontWeight: 'bold',
                                        backgroundColor: p.difficulty === 'Easy' ? '#e8f5e9' : p.difficulty === 'Medium' ? '#fff3e0' : '#ffebee',
                                        color: p.difficulty === 'Easy' ? '#2e7d32' : p.difficulty === 'Medium' ? '#ef6c00' : '#c62828'
                                    }}>
                                        {p.difficulty}
                                    </span>
                                </td>
                                <td style={{ padding: '15px' }}>
                                    {p.status === 'Solved' ? (
                                        <span style={{ color: '#2e7d32', fontWeight: 'bold' }}>Solved</span>
                                    ) : p.status === 'Attempted' ? (
                                        <span style={{ color: '#ef6c00', fontWeight: 'bold' }}>Attempted</span>
                                    ) : (
                                        <span style={{ color: '#aaa' }}>-</span>
                                    )}
                                </td>
                                <td style={{ padding: '15px' }}>
                                    {/* Edit button is always available here because this is "My Problems" or Admin view */}
                                    <Link to={`/edit-problem/${p.id}`} style={{ 
                                        padding: '6px 12px', 
                                        backgroundColor: '#ff9800', 
                                        color: 'white', 
                                        textDecoration: 'none', 
                                        borderRadius: '4px', 
                                        fontSize: '14px',
                                        marginRight: '8px'
                                    }}>
                                        Edit
                                    </Link>
                                    <button 
                                        onClick={() => handleDelete(p.id, p.title)}
                                        style={{ 
                                            padding: '6px 12px', 
                                            backgroundColor: '#dc3545', 
                                            color: 'white', 
                                            border: 'none',
                                            borderRadius: '4px', 
                                            fontSize: '14px',
                                            cursor: 'pointer'
                                        }}>
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {problems.length === 0 && (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                        No problems found.
                    </div>
                )}
            </div>
        </div>
    );
};

export default MyProblems;

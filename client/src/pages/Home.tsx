import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchProblems } from '../api';

const Home: React.FC = () => {
    const [problems, setProblems] = useState<any[]>([]);

    useEffect(() => {
        const loadProblems = async () => {
             try {
                 const data = await fetchProblems();
                 setProblems(data);
             } catch (e) {
                 console.error(e);
             }
        };
        loadProblems();
    }, []);

    return (
        <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '0 20px' }}>
            <h1 style={{ marginBottom: '20px', color: '#262626' }}>Problems</h1>
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ backgroundColor: '#f8f9fa', color: '#666', borderBottom: '1px solid #eee' }}>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>#</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Title</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Difficulty</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {problems.map((p, index) => (
                            <tr key={p.id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '15px', color: '#888' }}>{index + 1}</td>
                                <td style={{ padding: '15px' }}>
                                    <Link to={`/problems/${p.id}`} style={{ color: '#2c3e50', fontWeight: '500' }}>
                                        {p.title}
                                    </Link>
                                    <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                                        {p.tags}
                                    </div>
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
                                <td style={{ padding: '15px', color: '#aaa', fontSize: '20px' }}>
                                    {/* Placeholder for status */}
                                    -
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


export default Home;

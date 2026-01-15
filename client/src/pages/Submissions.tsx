import React, { useEffect, useState } from 'react';
import { fetchAllSubmissions } from '../api';
import keycloak from '../keycloak';

const Submissions: React.FC = () => {
    const [submissions, setSubmissions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadSubmissions = async () => {
             try {
                 const data = await fetchAllSubmissions();
                 setSubmissions(data);
             } catch (e) {
                 console.error(e);
             } finally {
                 setLoading(false);
             }
        };
        if (keycloak.authenticated) {
            loadSubmissions();
        }
    }, []);

    if (loading) {
        return <div style={{ padding: '20px' }}>Loading submissions...</div>;
    }

    return (
        <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '0 20px' }}>
            <h1 style={{ marginBottom: '20px', color: '#262626' }}>Submission History</h1>
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ backgroundColor: '#f8f9fa', color: '#666', borderBottom: '1px solid #eee' }}>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Date</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>User</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Problem</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Language</th>
                            <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {submissions.map((sub) => (
                            <tr key={sub.id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '15px', color: '#666' }}>{new Date(sub.created_at).toLocaleString()}</td>
                                <td style={{ padding: '15px', fontWeight: '500' }}>{sub.username}</td>
                                <td style={{ padding: '15px' }}>{sub.problem_title}</td>
                                <td style={{ padding: '15px' }}>{sub.language}</td>
                                <td style={{ padding: '15px' }}>
                                    <span style={{ 
                                        color: sub.status === 'Accepted' ? '#2e7d32' : '#c62828',
                                        fontWeight: 'bold'
                                    }}>
                                        {sub.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {submissions.length === 0 && (
                     <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                        No submissions found.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Submissions;

import React, { useEffect, useState } from 'react';
import keycloak from '../keycloak';

const MyAccount: React.FC = () => {
    const [stats, setStats] = useState<{
        totalSubmissions: number;
        acceptedSubmissions: number;
        solvedProblems: number;
    }>({ totalSubmissions: 0, acceptedSubmissions: 0, solvedProblems: 0 });

    const username = keycloak.tokenParsed?.preferred_username || 'User';
    const email = keycloak.tokenParsed?.email || 'No email';

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await fetch('http://localhost:5001/api/problems/submissions', {
                    headers: {
                        'Authorization': `Bearer ${keycloak.token}`
                    }
                });
                if (response.ok) {
                    const submissions = await response.json();
                    const accepted = submissions.filter((s: any) => s.status === 'Accepted').length;
                    const solvedProblemIds = new Set(
                        submissions.filter((s: any) => s.status === 'Accepted').map((s: any) => s.problem_id)
                    );
                    setStats({
                        totalSubmissions: submissions.length,
                        acceptedSubmissions: accepted,
                        solvedProblems: solvedProblemIds.size
                    });
                }
            } catch (e) {
                console.error('Failed to fetch stats:', e);
            }
        };
        fetchStats();
    }, []);

    const handleLogout = () => {
        keycloak.logout({ redirectUri: window.location.origin });
    };

    const handleChangePassword = () => {
        // Redirect to Keycloak account management
        window.open(`http://localhost:8081/realms/scd-leetcode/account/#/security/signingin`, '_blank');
    };

    return (
        <div style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px' }}>
            <h1 style={{ marginBottom: '30px', color: '#262626' }}>My Account</h1>
            
            {/* Profile Card */}
            <div style={{ 
                backgroundColor: 'white', 
                borderRadius: '12px', 
                boxShadow: '0 2px 10px rgba(0,0,0,0.08)', 
                padding: '30px',
                marginBottom: '20px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '30px' }}>
                    <div style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '50%',
                        backgroundColor: '#4CAF50',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '32px',
                        color: 'white',
                        fontWeight: 'bold',
                        marginRight: '20px'
                    }}>
                        {username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h2 style={{ margin: 0, color: '#333' }}>{username}</h2>
                        <p style={{ margin: '5px 0 0 0', color: '#666' }}>{email}</p>
                    </div>
                </div>

                <div style={{ borderTop: '1px solid #eee', paddingTop: '20px' }}>
                    <h3 style={{ marginBottom: '15px', color: '#333' }}>Statistics</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
                        <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#4CAF50' }}>{stats.solvedProblems}</div>
                            <div style={{ color: '#666', fontSize: '14px' }}>Problems Solved</div>
                        </div>
                        <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#2196F3' }}>{stats.totalSubmissions}</div>
                            <div style={{ color: '#666', fontSize: '14px' }}>Total Submissions</div>
                        </div>
                        <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#ff9800' }}>{stats.acceptedSubmissions}</div>
                            <div style={{ color: '#666', fontSize: '14px' }}>Accepted</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Actions Card */}
            <div style={{ 
                backgroundColor: 'white', 
                borderRadius: '12px', 
                boxShadow: '0 2px 10px rgba(0,0,0,0.08)', 
                padding: '30px'
            }}>
                <h3 style={{ marginBottom: '20px', color: '#333' }}>Account Actions</h3>
                <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
                    <button
                        onClick={handleChangePassword}
                        style={{
                            padding: '12px 24px',
                            backgroundColor: '#2196F3',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '500'
                        }}
                    >
                        Change Password
                    </button>
                    <button
                        onClick={handleLogout}
                        style={{
                            padding: '12px 24px',
                            backgroundColor: '#f44336',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '500'
                        }}
                    >
                        Logout
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MyAccount;

import React, { useEffect, useState } from 'react';

interface RankingEntry {
    rank: number;
    user_id: number;
    username: string;
    solved_problems: number;
    total_submissions: number;
    acceptance_rate: number;
}

const Ranking: React.FC = () => {
    const [ranking, setRanking] = useState<RankingEntry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRanking = async () => {
            try {
                const response = await fetch('http://localhost:5001/api/problems/ranking');
                if (response.ok) {
                    const data = await response.json();
                    setRanking(data);
                }
            } catch (e) {
                console.error('Failed to fetch ranking:', e);
            } finally {
                setLoading(false);
            }
        };
        fetchRanking();
    }, []);

    const getMedalColor = (rank: number) => {
        if (rank === 1) return '#FFD700'; // Gold
        if (rank === 2) return '#C0C0C0'; // Silver
        if (rank === 3) return '#CD7F32'; // Bronze
        return 'transparent';
    };

    return (
        <div style={{ maxWidth: '900px', margin: '40px auto', padding: '0 20px' }}>
            <h1 style={{ marginBottom: '30px', color: '#262626' }}>
                🏆 Ranking
            </h1>
            
            <div style={{ 
                backgroundColor: 'white', 
                borderRadius: '12px', 
                boxShadow: '0 2px 10px rgba(0,0,0,0.08)', 
                overflow: 'hidden'
            }}>
                {loading ? (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                        Loading...
                    </div>
                ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f8f9fa', color: '#666', borderBottom: '2px solid #eee' }}>
                                <th style={{ padding: '15px', textAlign: 'center', fontWeight: '600', width: '80px' }}>Rank</th>
                                <th style={{ padding: '15px', textAlign: 'left', fontWeight: '600' }}>User</th>
                                <th style={{ padding: '15px', textAlign: 'center', fontWeight: '600' }}>Solved</th>
                                <th style={{ padding: '15px', textAlign: 'center', fontWeight: '600' }}>Submissions</th>
                                <th style={{ padding: '15px', textAlign: 'center', fontWeight: '600' }}>Acceptance</th>
                            </tr>
                        </thead>
                        <tbody>
                            {ranking.map((entry) => (
                                <tr 
                                    key={entry.user_id} 
                                    style={{ 
                                        borderBottom: '1px solid #eee',
                                        backgroundColor: entry.rank <= 3 ? `${getMedalColor(entry.rank)}15` : 'white'
                                    }}
                                >
                                    <td style={{ padding: '15px', textAlign: 'center' }}>
                                        {entry.rank <= 3 ? (
                                            <span style={{ 
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                width: '32px',
                                                height: '32px',
                                                borderRadius: '50%',
                                                backgroundColor: getMedalColor(entry.rank),
                                                color: entry.rank === 1 ? '#333' : 'white',
                                                fontWeight: 'bold',
                                                fontSize: '14px'
                                            }}>
                                                {entry.rank}
                                            </span>
                                        ) : (
                                            <span style={{ color: '#888', fontWeight: '500' }}>{entry.rank}</span>
                                        )}
                                    </td>
                                    <td style={{ padding: '15px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center' }}>
                                            <div style={{
                                                width: '36px',
                                                height: '36px',
                                                borderRadius: '50%',
                                                backgroundColor: '#4CAF50',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                color: 'white',
                                                fontWeight: 'bold',
                                                marginRight: '12px',
                                                fontSize: '14px'
                                            }}>
                                                {entry.username.charAt(0).toUpperCase()}
                                            </div>
                                            <span style={{ fontWeight: '500', color: '#333' }}>{entry.username}</span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '15px', textAlign: 'center' }}>
                                        <span style={{ 
                                            fontWeight: 'bold', 
                                            color: '#4CAF50',
                                            fontSize: '16px'
                                        }}>
                                            {entry.solved_problems}
                                        </span>
                                    </td>
                                    <td style={{ padding: '15px', textAlign: 'center', color: '#666' }}>
                                        {entry.total_submissions}
                                    </td>
                                    <td style={{ padding: '15px', textAlign: 'center' }}>
                                        <span style={{
                                            padding: '4px 10px',
                                            borderRadius: '12px',
                                            fontSize: '13px',
                                            fontWeight: '500',
                                            backgroundColor: entry.acceptance_rate >= 50 ? '#e8f5e9' : '#fff3e0',
                                            color: entry.acceptance_rate >= 50 ? '#2e7d32' : '#ef6c00'
                                        }}>
                                            {entry.acceptance_rate}%
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
                {!loading && ranking.length === 0 && (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
                        No ranking data yet. Be the first to solve a problem!
                    </div>
                )}
            </div>
        </div>
    );
};

export default Ranking;

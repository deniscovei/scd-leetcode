import React from 'react';
import { Link } from 'react-router-dom';
import keycloak from '../keycloak';

const Navbar: React.FC = () => {
    const isLoggedIn = keycloak.authenticated;
    const username = keycloak.tokenParsed?.preferred_username || keycloak.tokenParsed?.sub;

    const handleLogin = () => keycloak.login({ redirectUri: window.location.origin });
    const handleRegister = () => keycloak.register({ redirectUri: window.location.origin });
    const handleLogout = () => keycloak.logout({ redirectUri: window.location.origin });

    return (
        <nav style={styles.nav}>
            <div style={styles.brand}>
                <Link to="/" style={styles.brandLink}>SCD.Code</Link>
            </div>
            <ul style={styles.menu}>
                <li style={styles.menuItem}>
                    <Link to="/" style={styles.link}>Problems</Link>
                </li>
                {isLoggedIn ? (
                    <>
                        <li style={styles.menuItem}>
                            <Link to="/add-problem" style={styles.link}>Add Problem</Link>
                        </li>
                        <li style={styles.menuItem}>
                            <span style={styles.userText}>Logged in as {username}</span>
                        </li>
                        <li style={styles.menuItem}>
                            <button onClick={handleLogout} style={styles.button}>Logout</button>
                        </li>
                    </>
                ) : (
                    <>
                        <li style={styles.menuItem}>
                            <button onClick={handleLogin} style={{...styles.link, background: 'none', border: 'none', cursor: 'pointer', fontSize: '1rem'}}>Login</button>
                        </li>
                        <li style={styles.menuItem}>
                             <button onClick={handleRegister} style={{...styles.link, background: 'none', border: 'none', cursor: 'pointer', fontSize: '1rem'}}>Register</button>
                        </li>
                    </>
                )}
            </ul>
        </nav>
    );
};

const styles = {
    nav: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        backgroundColor: '#262626',
        color: '#fff',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    },
    brand: {
        fontSize: '1.5rem',
        fontWeight: 'bold',
    },
    brandLink: {
        color: '#fff',
        textDecoration: 'none',
    },
    menu: {
        display: 'flex',
        listStyle: 'none',
        margin: 0,
        padding: 0,
        alignItems: 'center',
    },
    menuItem: {
        marginLeft: '1.5rem',
    },
    link: {
        color: '#ccc',
        textDecoration: 'none',
        fontSize: '1rem',
        transition: 'color 0.3s',
    },
    userText: {
        color: '#4db8ff',
        fontWeight: 'bold',
        marginRight: '1rem',
    },

    button: {
        backgroundColor: 'transparent',
        border: '1px solid #ccc',
        color: '#ccc',
        padding: '0.5rem 1rem',
        cursor: 'pointer',
        borderRadius: '4px',
    }
};

export default Navbar;

import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';
import keycloak from './keycloak';

/* ...existing code... */

// Initialize Keycloak
keycloak.init({ 
  onLoad: 'check-sso',
  checkLoginIframe: false
}).then((authenticated: boolean) => {
    console.log(`User is ${authenticated ? 'authenticated' : 'not authenticated'}`);
    ReactDOM.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
      document.getElementById('root')
    );
}).catch(console.error);

// ResizeObserver loop error suppression
const resizeObserverLoopErr = /ResizeObserver loop limit exceeded|ResizeObserver loop completed with undelivered notifications/;

const originalError = console.error;
console.error = (...args) => {
    if (args.some(arg => typeof arg === 'string' && resizeObserverLoopErr.test(arg))) {
        return;
    }
    originalError.call(console, ...args);
};

window.addEventListener('error', (event) => {
    if (resizeObserverLoopErr.test(event.message)) {
        event.stopImmediatePropagation();
    }
});

window.onerror = (message, source, lineno, colno, error) => {
    if (typeof message === 'string' && resizeObserverLoopErr.test(message)) {
        return true;
    }
    return false;
};


/* ReactDOM.render handled in keycloak.init */


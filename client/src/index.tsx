import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';
import keycloak from './keycloak';

// ResizeObserver loop error suppression - MUST be before any rendering
// This is a known benign error that occurs with Monaco Editor and other resize-aware components
const resizeObserverLoopErr = /ResizeObserver loop/;

// Suppress console errors
const originalError = console.error;
console.error = (...args) => {
    if (args.some(arg => typeof arg === 'string' && resizeObserverLoopErr.test(arg))) {
        return;
    }
    originalError.call(console, ...args);
};

// Suppress window errors
window.addEventListener('error', (event) => {
    if (event.message && resizeObserverLoopErr.test(event.message)) {
        event.stopImmediatePropagation();
        event.preventDefault();
        return true;
    }
}, true);

// Suppress unhandled rejection errors related to ResizeObserver
window.addEventListener('unhandledrejection', (event) => {
    if (event.reason && typeof event.reason.message === 'string' && resizeObserverLoopErr.test(event.reason.message)) {
        event.preventDefault();
        return true;
    }
});

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


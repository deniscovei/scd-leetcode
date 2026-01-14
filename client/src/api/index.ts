import axios from 'axios';
import keycloak from '../keycloak';

const API_URL = 'http://localhost:5001/api';


const api = axios.create({
    baseURL: API_URL
});

api.interceptors.request.use(async (config) => {
    if (keycloak.authenticated) {
        try {
           await keycloak.updateToken(30);
           config.headers.Authorization = `Bearer ${keycloak.token}`;
        } catch (error) {
           console.error('Token refresh failed');
           keycloak.login();
        }
    }
    return config;
});

export const login = async (username: string, password: string) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
};

export const register = async (username: string, email: string, password: string) => {
    const response = await api.post('/auth/register', { username, email, password });
    return response.data;
};

export const fetchProblems = async () => {
    const response = await api.get('/problems/');
    return response.data;
};

export const fetchProblem = async (id: string | number) => {
    const response = await api.get(`/problems/${id}`);
    return response.data;
};

export const submitSolution = async (problemId: string, language: string, code: string) => {
    const response = await api.post(`/problems/${problemId}/submit`, { language, code });
    return response.data;
};

export const runSolution = async (problemId: string, language: string, code: string, input: string) => {
    const response = await api.post(`/problems/${problemId}/run`, { language, code, input });
    return response.data;
};

export const createProblem = async (problemData: any) => {
    const response = await api.post('/problems/', problemData);
    return response.data;
};

export const updateProblem = async (id: string, problemData: any) => {
    const response = await api.put(`/problems/${id}`, problemData);
    return response.data;
};

export const deleteProblem = async (id: string | number) => {
    const response = await api.delete(`/problems/${id}`);
    return response.data;
};

export const fetchSubmissions = async (problemId: string | number) => {
    const response = await api.get(`/problems/${problemId}/submissions`);
    return response.data;
};

export default api;

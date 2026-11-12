import axios from 'axios';
import { supabase } from './supabaseClient';

const API_URL = 'https://corte-vertical-ia-clasificador-de.onrender.com';

//const API_URL = 'http://localhost:8000'; 

export const classifyImage = async (file) => {
  // 1. Obtener el token de la sesión actual de Supabase
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_URL}/predict`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`, // <-- Enviamos el token
      },
    });
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      throw new Error(error.response.data.error || error.response.data.detail);
    }
    throw new Error('No se pudo conectar con el servidor.');
  }
};

export const getStats = async () => {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  try {
    const response = await axios.get(`${API_URL}/stats`, {
      headers: {
        'Authorization': `Bearer ${token}`, // <-- Enviamos el token
      },
    });
    return response.data;
  } catch (error) {
    throw new Error('No se pudieron cargar las estadísticas.');
  }
};

export const registerCompany = async (companyName, token) => {
  try {
    const response = await axios.post(`${API_URL}/register-company`, 
      { name: companyName },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Error al registrar la empresa.');
  }
};

export const getHistory = async (skip = 0, limit = 50) => {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  try {
    const response = await axios.get(`${API_URL}/history?skip=${skip}&limit=${limit}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    throw new Error('No se pudo cargar el historial.');
  }
};

export const verifyPrediction = async (predictionId, categoriaCorrecta) => {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  try {
    const response = await axios.patch(
      `${API_URL}/predict/${predictionId}/verify`,
      { categoria_correcta: categoriaCorrecta },
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Error al verificar la predicción.');
  }
};

export const getCompanyInfo = async () => {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  try {
    const response = await axios.get(`${API_URL}/company-info`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    throw new Error('No se pudo cargar la información de la empresa.');
  }
};
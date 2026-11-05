import axios from 'axios';

const API_URL = 'https://corte-vertical-ia-clasificador-de.onrender.com';

export const classifyImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_URL}/predict`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
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
  try {
    const response = await axios.get(`${API_URL}/stats`);
    return response.data;
  } catch (error) {
    throw new Error('No se pudieron cargar las estadísticas.');
  }
};
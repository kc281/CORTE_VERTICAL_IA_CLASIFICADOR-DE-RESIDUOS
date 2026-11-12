import React, { useEffect, useState } from 'react';
import { getHistory, verifyPrediction } from '../api';

const CATEGORIAS = ['biological', 'cardboard', 'metal', 'paper', 'plastic'];

const HistoryTable = () => {
  const [history, setHistory] = useState({ total: 0, records: [] });
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null); // Para saber qué fila estamos editando
  const [selectedCategory, setSelectedCategory] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await getHistory();
      setHistory(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleVerify = async (id) => {
    if (!selectedCategory) return;
    setSaving(true);
    try {
      await verifyPrediction(id, selectedCategory);
      setEditingId(null); // Cerrar el modo edición
      await fetchHistory(); // Recargar los datos actualizados
    } catch (error) {
      alert(error.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="text-center py-10">Cargando historial...</div>;

  return (
    <div className="w-full max-w-5xl mx-auto p-6 bg-white rounded-xl shadow-lg mt-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Historial y Verificación Humana</h2>
      
      {history.records.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No hay clasificaciones registradas aún.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500">
            <thead className="text-xs text-gray-700 uppercase bg-gray-100">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Fecha</th>
                <th className="px-4 py-3">Predicción IA</th>
                <th className="px-4 py-3">Confianza</th>
                <th className="px-4 py-3">Categoría Confirmada</th>
                <th className="px-4 py-3">Acción</th>
              </tr>
            </thead>
            <tbody>
              {history.records.map((record) => (
                <tr key={record.id} className="bg-white border-b hover:bg-gray-50">
                  <td className="px-4 py-4 font-medium text-gray-900">{record.id}</td>
                  <td className="px-4 py-4">{new Date(record.fecha).toLocaleString()}</td>
                  <td className="px-4 py-4 font-semibold capitalize">{record.clase_predicha}</td>
                  <td className="px-4 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${record.confianza >= 0.60 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                      {(record.confianza * 100).toFixed(1)}%
                    </span>
                  </td>
                  
                  {/* COLUMNA DE VERIFICACIÓN */}
                  <td className="px-4 py-4 font-bold text-primary capitalize">
                    {record.categoria_confirmada ? (
                      <span className="flex items-center gap-1">
                        ✅ {record.categoria_confirmada}
                      </span>
                    ) : (
                      <span className="text-gray-400 italic text-xs font-normal">Sin verificar</span>
                    )}
                  </td>

                  <td className="px-4 py-4">
                    {record.categoria_confirmada ? (
                      <span className="text-green-600 text-sm font-semibold">Verificado</span>
                    ) : editingId === record.id ? (
                      <div className="flex items-center space-x-2">
                        <select 
                          className="border rounded p-1 text-sm bg-white text-gray-700"
                          value={selectedCategory}
                          onChange={(e) => setSelectedCategory(e.target.value)}
                        >
                          <option value="">Seleccionar...</option>
                          {CATEGORIAS.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                          ))}
                        </select>
                        <button 
                          onClick={() => handleVerify(record.id)} 
                          disabled={saving || !selectedCategory}
                          className="bg-primary text-white px-2 py-1 rounded text-xs hover:bg-green-800 disabled:opacity-50"
                        >
                          Guardar
                        </button>
                        <button 
                          onClick={() => setEditingId(null)} 
                          className="text-gray-500 text-xs hover:underline"
                        >
                          Cancelar
                        </button>
                      </div>
                    ) : (
                      <button 
                        onClick={() => { setEditingId(record.id); setSelectedCategory(record.clase_predicha); }}
                        className="bg-secondary text-white px-3 py-1 rounded text-xs font-semibold hover:bg-blue-800"
                      >
                        Revisar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      <div className="mt-4 text-sm text-gray-500">
        Mostrando {history.records.length} de {history.total} registros.
      </div>
    </div>
  );
};

export default HistoryTable;
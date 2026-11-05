import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { getStats } from '../api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const StatsDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats();
        setStats(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <div className="text-center py-10">Cargando estadísticas...</div>;
  if (!stats) return <div className="text-center py-10 text-red-500">Error al cargar datos.</div>;

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-lg mt-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Panel de Control </h2>
      
      {/* Tarjetas de Métricas Globales */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg text-center border border-blue-100">
          <p className="text-sm text-gray-500">Total Consultas</p>
          <p className="text-2xl font-bold text-blue-700">{stats.total_consultas}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg text-center border border-green-100">
          <p className="text-sm text-gray-500">Confianza Promedio</p>
          <p className="text-2xl font-bold text-green-700">{(stats.confianza_promedio_global * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg text-center border border-yellow-100">
          <p className="text-sm text-gray-500">T. Inferencia Prom.</p>
          <p className="text-2xl font-bold text-yellow-700">{stats.tiempo_inferencia_promedio_ms} ms</p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg text-center border border-red-100">
          <p className="text-sm text-gray-500">Baja Confianza</p>
          <p className="text-2xl font-bold text-red-700">{stats.total_advertencias_baja_confianza}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Gráfica de Barras: Conteo por clase */}
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-700 mb-4 text-center">Distribución de Residuos</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.distribucion_clases}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="clase" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="cantidad" fill="#2E7D32" name="Cantidad" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Gráfica de Pastel */}
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-700 mb-4 text-center">Proporción de Clasificaciones</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stats.distribucion_clases}
                dataKey="cantidad"
                nameKey="clase"
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                label
              >
                {stats.distribucion_clases.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default StatsDashboard;
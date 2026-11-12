import React, { useState } from 'react';
import { supabase } from '../supabaseClient';
import { registerCompany } from '../api'; 

const AuthScreen = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);



  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        onLogin(data.session);
      } else {
        // 1. Registrar en Supabase Auth
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        
        // 2. Como desactivamos la confirmación, data.session debería existir inmediatamente
        if (data.session) {
          // 3. Llamamos al backend para crear la empresa
          await registerCompany(companyName, data.session.access_token);
          onLogin(data.session); // Entramos a la app
        } else {
          setError('Revisa tu correo para confirmar la cuenta.');
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-center text-primary mb-6">
          {isLogin ? 'Iniciar Sesión' : 'Registrar Empresa'}
        </h2>
        
        {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">{error}</div>}

        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Correo Electrónico</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full p-2 border border-gray-300 rounded focus:ring-primary focus:border-primary" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full p-2 border border-gray-300 rounded focus:ring-primary focus:border-primary" />
          </div>
          
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Nombre de la Empresa</label>
              <input type="text" required value={companyName} onChange={(e) => setCompanyName(e.target.value)}
                className="mt-1 w-full p-2 border border-gray-300 rounded focus:ring-primary focus:border-primary" />
            </div>
          )}

          <button type="submit" disabled={loading}
            className="w-full bg-primary text-white font-bold py-2 rounded hover:bg-green-800 transition-colors">
            {loading ? 'Procesando...' : (isLogin ? 'Entrar' : 'Registrarse')}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button onClick={() => setIsLogin(!isLogin)} className="text-sm text-secondary hover:underline">
            {isLogin ? '¿No tienes cuenta? Registra tu empresa' : '¿Ya tienes cuenta? Inicia sesión'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthScreen;
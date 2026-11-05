import React from 'react';

const colorMap = {
  verde: 'bg-green-500 text-white',
  blanco: 'bg-gray-100 text-gray-800 border border-gray-300',
  negro: 'bg-gray-800 text-white'
};

const ResultCard = ({ result, onReset }) => {
  const sortedProbs = Object.entries(result.probabilidades).sort((a, b) => b[1] - a[1]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 w-full max-w-md mx-auto animate-fade-in">
      <h2 className="text-xl font-bold text-center mb-4">Resultado de la Clasificación</h2>
      
      <div className="text-center mb-6">
        <p className="text-sm text-gray-500 uppercase tracking-wide">Categoría predicha</p>
        <p className="text-4xl font-extrabold text-primary mb-2">{result.clase_etiqueta}</p>
        
        <div className="flex items-center justify-center space-x-2">
          <span className="text-gray-600">Confianza:</span>
          <span className="font-bold text-lg">{(result.confianza * 100).toFixed(1)}%</span>
        </div>
        
        <div className="mt-3 flex items-center justify-center space-x-2 text-sm">
          <span className="text-gray-600">Disposición:</span>
          <span className={`px-3 py-1 rounded-full font-bold ${colorMap[result.color_disposicion] || 'bg-gray-200'}`}>
            Caneca {result.color_disposicion}
          </span>
        </div>
      </div>

      {result.advertencia && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-3 mb-6 text-sm" role="alert">
          <p className="font-bold">⚠️ Confianza Baja</p>
          <p>La confianza de esta predicción es menor al 60%. Se recomienda verificar manualmente el tipo de residuo.</p>
        </div>
      )}

      <div className="mb-6">
        <p className="text-sm font-semibold text-gray-700 mb-2">Probabilidades por clase:</p>
        <div className="space-y-2">
          {sortedProbs.map(([clase, prob]) => (
            <div key={clase} className="flex items-center text-sm">
              <span className="w-24 capitalize">{clase}</span>
              <div className="flex-1 bg-gray-200 rounded-full h-2.5 ml-2">
                <div 
                  className="bg-secondary h-2.5 rounded-full" 
                  style={{ width: `${prob * 100}%` }}
                ></div>
              </div>
              <span className="w-12 text-right text-gray-500">{(prob * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={onReset}
        className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors"
      >
        Clasificar otro residuo
      </button>
    </div>
  );
};

export default ResultCard;
import React from 'react';

const PrivacyModal = ({ onAccept }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Aviso de Privacidad</h2>
        <div className="text-gray-600 space-y-3 mb-6 text-sm">
          <p>Para clasificar el residuo, esta aplicación requiere acceso a la cámara de su computador o la carga de una imagen.</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>La imagen será enviada a nuestro servidor <strong>únicamente</strong> para generar la predicción.</li>
            <li>La imagen <strong>no se almacena</strong> en ningún disco ni base de datos.</li>
            <li>No recopilamos datos personales ni utilizamos cookies de seguimiento.</li>
          </ul>
          <p className="font-semibold text-primary mt-2">Cumplimiento de la Ley 1581 de 2012.</p>
        </div>
        <button
          onClick={onAccept}
          className="w-full bg-primary hover:bg-green-800 text-white font-bold py-2 px-4 rounded transition-colors"
        >
          Acepto y continúo
        </button>
      </div>
    </div>
  );
};

export default PrivacyModal;
import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { classifyImage } from './api';
import PrivacyModal from './components/PrivacyModal';
import ResultCard from './components/ResultCard';

function App() {
  const [hasConsent, setHasConsent] = useState(false);
  const [imageSrc, setImageSrc] = useState(null);
  const [fileToSend, setFileToSend] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  
  const webcamRef = useRef(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImageSrc(imageSrc);
    setErrorMsg('');
    
    fetch(imageSrc)
      .then(res => res.blob())
      .then(blob => {
        const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
        setFileToSend(file);
      });
  }, [webcamRef]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setErrorMsg('Formato no permitido. Use JPG, PNG o WEBP.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg('El archivo supera el tamaño máximo de 5 MB.');
      return;
    }

    setFileToSend(file);
    setImageSrc(URL.createObjectURL(file));
    setErrorMsg('');
  };

  const handleClassify = async () => {
    if (!fileToSend) return;

    setIsLoading(true);
    setErrorMsg('');
    
    try {
      const result = await classifyImage(fileToSend);
      setPrediction(result);
    } catch (error) {
      setErrorMsg(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setImageSrc(null);
    setFileToSend(null);
    setPrediction(null);
    setErrorMsg('');
  };

  if (!hasConsent) {
    return <PrivacyModal onAccept={() => setHasConsent(true)} />;
  }

  return (
    <div className="min-h-screen py-10 px-4 flex flex-col items-center">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-extrabold text-primary mb-2">Clasificador de Residuos IA</h1>
        <p className="text-gray-600">Captura o sube una imagen para identificar el tipo de residuo</p>
      </header>

      <main className="w-full max-w-2xl bg-white rounded-xl shadow-lg overflow-hidden">
        {errorMsg && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 m-4 rounded" role="alert">
            <p className="font-bold">Error</p>
            <p>{errorMsg}</p>
            <button onClick={() => setErrorMsg('')} className="mt-2 text-sm underline font-semibold">Cerrar</button>
          </div>
        )}

        {prediction ? (
          <div className="p-6">
            <ResultCard result={prediction} onReset={handleReset} />
          </div>
        ) : (
          <div className="p-6 flex flex-col items-center">
            {imageSrc ? (
              <div className="w-full flex flex-col items-center">
                <img src={imageSrc} alt="Preview" className="w-full max-h-80 object-contain bg-gray-100 rounded-lg mb-6" />
                
                <div className="flex space-x-4 w-full">
                  <button 
                    onClick={handleReset}
                    disabled={isLoading}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-4 rounded transition-colors disabled:opacity-50"
                  >
                    Volver a capturar
                  </button>
                  <button 
                    onClick={handleClassify}
                    disabled={isLoading}
                    className="flex-1 bg-primary hover:bg-green-800 text-white font-bold py-3 px-4 rounded transition-colors disabled:opacity-50 flex justify-center items-center"
                  >
                    {isLoading ? (
                      <span className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
                    ) : 'Clasificar Imagen'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="w-full flex flex-col items-center">
                <div className="w-full rounded-lg overflow-hidden border-2 border-dashed border-gray-300 mb-6 bg-gray-50">
                  <Webcam
                    audio={false}
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    videoConstraints={{ facingMode: "environment" }}
                    className="w-full object-cover max-h-80"
                  />
                </div>

                <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 w-full">
                  <button 
                    onClick={capture}
                    className="flex-1 bg-secondary hover:bg-blue-800 text-white font-bold py-3 px-4 rounded transition-colors"
                  >
                    📸 Tomar Foto
                  </button>
                  
                  <div className="flex-1 relative">
                    <input 
                      type="file" 
                      accept="image/jpeg, image/png, image/webp"
                      onChange={handleFileUpload}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <button className="w-full bg-gray-700 hover:bg-gray-900 text-white font-bold py-3 px-4 rounded transition-colors pointer-events-none">
                      📁 Cargar Archivo
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="mt-8 text-sm text-gray-500 text-center max-w-md">
        <p>Prototipo académico - Universidad Central</p>
        <p>Alineado con la Resolución 2184 de 2019 (Código de Colores para la Separacion de Residuos)</p>
      </footer>
    </div>
  );
}

export default App;
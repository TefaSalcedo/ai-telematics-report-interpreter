# Frontend Documentation

## ⚛️ Frontend React + Next.js Development Guide

El frontend del proyecto AI Telematics es una aplicación web moderna construida con React y Next.js que proporciona una interfaz intuitiva para el análisis de reportes telemétricos con inteligencia artificial.

---

## 🏗️ Arquitectura del Frontend

### Estructura del Proyecto
```
frontend/
├── public/
│   └── index.html           # HTML template
├── src/
│   ├── index.js             # Punto de entrada Next.js
│   ├── index.css            # Estilos globales
│   └── App.js               # Componente principal
├── package.json             # Dependencias npm
├── Dockerfile              # Configuración Docker
└── .dockerignore           # Ignorar archivos en Docker
```

### Flujo de Arquitectura
```
User Interface → React Components → API Calls → Backend FastAPI → Response Rendering
```

---

## 📦 Dependencias y Tecnologías

### Core Dependencies
```json
{
  "dependencies": {
    "chart.js": "^4.5.1",
    "date-fns": "^4.1.0",
    "groq-sdk": "^0.37.0",
    "lodash": "^4.17.23",
    "next": "16.1.6",
    "react": "19.2.3",
    "react-chartjs-2": "^5.3.1",
    "react-dom": "19.2.3",
    "recharts": "^3.7.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.1.6",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}
```

### Tecnologías Utilizadas
- **Next.js 16.1**: Framework React de producción
- **React 19.2**: Librería UI con hooks avanzados
- **TypeScript**: Tipado estático para mejor desarrollo
- **TailwindCSS 4**: Framework CSS utility-first
- **Chart.js/Recharts**: Visualización de datos
- **Lucide Icons**: Iconos modernos

---

## 🔧 Configuración del Entorno

### Variables de Entorno
```bash
# .env.local
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENV=development
```

### Configuración de Next.js
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### Configuración de TailwindCSS
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
      },
    },
  },
  plugins: [],
};
```

---

## 🚀 Componentes Principales

### App.js - Componente Principal
```jsx
// src/App.js
import React, { useState } from 'react';
import Head from 'next/head';
import './index.css';

function App() {
  const [reportData, setReportData] = useState(null);
  const [selectedProfile, setSelectedProfile] = useState('gerente');
  const [interpretation, setInterpretation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Cargar datos de ejemplo
  React.useEffect(() => {
    loadSampleData();
  }, []);

  const loadSampleData = async () => {
    try {
      const response = await fetch('/sample_report.json');
      const data = await response.json();
      setReportData(data);
    } catch (err) {
      console.error('Error loading sample data:', err);
      setError('No se pudieron cargar los datos de ejemplo');
    }
  };

  const handleInterpret = async () => {
    if (!reportData) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/interpret`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report: reportData,
          profile: selectedProfile,
        }),
      });

      const result = await response.json();

      if (result.success) {
        setInterpretation(result.data.interpretation);
      } else {
        setError(result.error?.message || 'Error en la interpretación');
      }
    } catch (err) {
      console.error('Error interpreting report:', err);
      setError('Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>AI Telematics - Interpretación de Reportes</title>
        <meta name="description" content="Sistema de interpretación de reportes telemétricos con IA" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <ReportUploader 
            reportData={reportData} 
            setReportData={setReportData} 
          />
          <ProfileSelector 
            selectedProfile={selectedProfile}
            setSelectedProfile={setSelectedProfile}
          />
          <InterpretButton 
            onInterpret={handleInterpret}
            loading={loading}
            disabled={!reportData}
          />
          {error && <ErrorMessage error={error} />}
          {interpretation && <InterpretationResult interpretation={interpretation} />}
        </main>
      </div>
    </>
  );
}

export default App;
```

### Componentes de UI

#### Header Component
```jsx
// src/components/Header.js
import React from 'react';

function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Telematics</h1>
              <p className="text-sm text-gray-600">Interpretación Inteligente de Reportes</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
              Sistema Activo
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
```

#### Report Uploader Component
```jsx
// src/components/ReportUploader.js
import React, { useRef } from 'react';

function ReportUploader({ reportData, setReportData }) {
  const fileInputRef = useRef(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        setReportData(data);
      } catch (error) {
        alert('El archivo no tiene un formato JSON válido');
      }
    };
    reader.readAsText(file);
  };

  const handleClearData = () => {
    setReportData(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        📊 Datos del Reporte
      </h2>
      
      <div className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          
          <div className="mt-4">
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="mt-2 block text-sm font-medium text-gray-900">
                Cargar archivo JSON
              </span>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                className="sr-only"
                accept=".json"
                ref={fileInputRef}
                onChange={handleFileUpload}
              />
              <span className="mt-1 block text-xs text-gray-500">
                Formato JSON con datos telemétricos
              </span>
            </label>
          </div>
        </div>

        {reportData && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-green-800">
                  ✅ Reporte cargado correctamente
                </h3>
                <p className="text-sm text-green-600 mt-1">
                  Cliente: {reportData.cliente} | 
                  Período: {reportData.periodo} | 
                  Vehículos: {reportData.vehiculos?.length || 0}
                </p>
              </div>
              <button
                onClick={handleClearData}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                Limpiar datos
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ReportUploader;
```

#### Profile Selector Component
```jsx
// src/components/ProfileSelector.js
import React from 'react';

function ProfileSelector({ selectedProfile, setSelectedProfile }) {
  const profiles = [
    {
      id: 'gerente',
      name: 'Gerente de Flota',
      description: 'Enfoque ejecutivo y estratégico',
      icon: '👔',
      color: 'blue'
    },
    {
      id: 'operaciones',
      name: 'Jefe de Operaciones',
      description: 'Enfoque técnico y operativo',
      icon: '🔧',
      color: 'green'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        👤 Perfil de Interpretación
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {profiles.map((profile) => (
          <div
            key={profile.id}
            className={`relative rounded-lg border-2 p-4 cursor-pointer transition-all ${
              selectedProfile === profile.id
                ? `border-${profile.color}-500 bg-${profile.color}-50`
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSelectedProfile(profile.id)}
          >
            <div className="flex items-start space-x-3">
              <span className="text-2xl">{profile.icon}</span>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">{profile.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{profile.description}</p>
              </div>
              {selectedProfile === profile.id && (
                <div className={`absolute top-2 right-2 w-6 h-6 bg-${profile.color}-500 rounded-full flex items-center justify-center`}>
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProfileSelector;
```

#### Interpretation Result Component
```jsx
// src/components/InterpretationResult.js
import React from 'react';

function InterpretationResult({ interpretation }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        📋 Resultados de la Interpretación
      </h2>
      
      {/* Resumen Ejecutivo */}
      <div className="mb-6">
        <h3 className="text-md font-medium text-gray-900 mb-3">
          📊 Resumen Ejecutivo
        </h3>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-gray-800">{interpretation.resumen_ejecutivo}</p>
        </div>
      </div>

      {/* KPIs Principales */}
      {interpretation.kpis_principales && (
        <div className="mb-6">
          <h3 className="text-md font-medium text-gray-900 mb-3">
            📈 KPIs Principales
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(interpretation.kpis_principales).map(([key, value]) => (
              <div key={key} className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-600 capitalize">
                  {key.replace(/_/g, ' ')}
                </h4>
                <p className="text-lg font-semibold text-gray-900 mt-1">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recomendaciones */}
      {interpretation.recomendaciones && interpretation.recomendaciones.length > 0 && (
        <div className="mb-6">
          <h3 className="text-md font-medium text-gray-900 mb-3">
            💡 Recomendaciones
          </h3>
          <div className="space-y-3">
            {interpretation.recomendaciones.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 bg-green-50 rounded-lg p-4">
                <span className="text-green-600 mt-0.5">•</span>
                <p className="text-gray-800">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vehículos Destacados */}
      {interpretation.vehiculos_destacados && interpretation.vehiculos_destacados.length > 0 && (
        <div className="mb-6">
          <h3 className="text-md font-medium text-gray-900 mb-3">
            🚗 Vehículos Destacados
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Placa
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Consumo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recomendación
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {interpretation.vehiculos_destacados.map((vehicle, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {vehicle.placa}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        vehicle.estado === 'Crítico' 
                          ? 'bg-red-100 text-red-800'
                          : vehicle.estado === 'Atención'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {vehicle.estado}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {vehicle.consumo}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {vehicle.recomendacion}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default InterpretationResult;
```

---

## 🎨 Estilos y Diseño

### Estilos Globales
```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }
  
  body {
    @apply bg-gray-50 text-gray-900;
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-sm border border-gray-200;
  }
  
  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent;
  }
}

@layer utilities {
  .text-gradient {
    @apply bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent;
  }
  
  .shadow-glow {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.15);
  }
}
```

### Componentes Reutilizables
```jsx
// src/components/ui/Button.js
import React from 'react';

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  disabled = false, 
  className = '', 
  ...props 
}) => {
  const baseClasses = 'font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white focus:ring-primary-500',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900 focus:ring-gray-500',
    success: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white focus:ring-yellow-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500'
  };
  
  const sizes = {
    sm: 'py-1.5 px-3 text-sm',
    md: 'py-2 px-4 text-base',
    lg: 'py-3 px-6 text-lg'
  };
  
  const classes = `${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`;
  
  return (
    <button
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {children}
    </button>
  );
};

export default Button;
```

---

## 📊 Visualización de Datos

### Chart Components
```jsx
// src/components/charts/FuelEfficiencyChart.js
import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function FuelEfficiencyChart({ vehicles }) {
  const data = {
    labels: vehicles.map(v => v.placa),
    datasets: [
      {
        label: 'Eficiencia (km/L)',
        data: vehicles.map(v => (v.distancia_km / v.consumo_litros).toFixed(2)),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Eficiencia de Combustible por Vehículo',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'km/Litro',
        },
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <Bar data={data} options={options} />
    </div>
  );
}

export default FuelEfficiencyChart;
```

### Dashboard Components
```jsx
// src/components/Dashboard.js
import React from 'react';
import FuelEfficiencyChart from './charts/FuelEfficiencyChart';
import { calculateKPIs } from '../utils/analytics';

function Dashboard({ reportData, interpretation }) {
  const kpis = calculateKPIs(reportData);

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Distancia Total"
          value={`${kpis.totalDistance.toLocaleString()} km`}
          icon="🚗"
          color="blue"
        />
        <KPICard
          title="Consumo Total"
          value={`${kpis.totalConsumption.toLocaleString()} L`}
          icon="⛽"
          color="green"
        />
        <KPICard
          title="Eficiencia Promedio"
          value={`${kpis.averageEfficiency.toFixed(1)} km/L`}
          icon="⚡"
          color="yellow"
        />
        <KPICard
          title="Vehículos Analizados"
          value={kpis.vehicleCount}
          icon="📊"
          color="purple"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FuelEfficiencyChart vehicles={reportData.vehiculos} />
        <PerformanceChart vehicles={reportData.vehiculos} />
      </div>
    </div>
  );
}

function KPICard({ title, value, icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-800 border-blue-200',
    green: 'bg-green-50 text-green-800 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    purple: 'bg-purple-50 text-purple-800 border-purple-200',
  };

  return (
    <div className={`border rounded-lg p-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  );
}

export default Dashboard;
```

---

## 🔧 Desarrollo Local

### Setup del Entorno
```bash
# Instalar dependencias
npm install

# O con yarn
yarn install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local

# Iniciar servidor de desarrollo
npm run dev

# O con yarn
yarn dev
```

### Scripts Disponibles
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### Desarrollo con Hot Reload
```bash
# Desarrollo con hot reload
npm run dev

# Puerto específico
npm run dev -- -p 3001

# Con host específico
npm run dev -- -H 0.0.0.0
```

---

## 🧪 Testing

### Configuración de Jest
```javascript
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
};

module.exports = createJestConfig(customJestConfig);
```

### Component Tests
```jsx
// __tests__/components/ProfileSelector.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ProfileSelector from '@/components/ProfileSelector';

describe('ProfileSelector', () => {
  it('renders profile options', () => {
    const mockSetSelectedProfile = jest.fn();
    render(
      <ProfileSelector 
        selectedProfile="gerente" 
        setSelectedProfile={mockSetSelectedProfile} 
      />
    );
    
    expect(screen.getByText('Gerente de Flota')).toBeInTheDocument();
    expect(screen.getByText('Jefe de Operaciones')).toBeInTheDocument();
  });

  it('calls setSelectedProfile when a profile is clicked', () => {
    const mockSetSelectedProfile = jest.fn();
    render(
      <ProfileSelector 
        selectedProfile="gerente" 
        setSelectedProfile={mockSetSelectedProfile} 
      />
    );
    
    fireEvent.click(screen.getByText('Jefe de Operaciones'));
    expect(mockSetSelectedProfile).toHaveBeenCalledWith('operaciones');
  });
});
```

### Integration Tests
```jsx
// __tests__/integration/ReportInterpretation.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '@/App';

// Mock fetch
global.fetch = jest.fn();

describe('Report Interpretation Flow', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('should interpret report successfully', async () => {
    const mockResponse = {
      success: true,
      data: {
        interpretation: {
          resumen_ejecutivo: 'Test summary',
          kpis_principales: { eficiencia: '7.5 km/L' },
          recomendaciones: ['Test recommendation'],
          vehiculos_destacados: []
        }
      }
    };
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    render(<App />);
    
    // Wait for sample data to load
    await waitFor(() => {
      expect(screen.getByText('Interpretar con IA')).toBeInTheDocument();
    });
    
    // Click interpret button
    fireEvent.click(screen.getByText('Interpretar con IA'));
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('Test summary')).toBeInTheDocument();
    });
  });
});
```

---

## 🚀 Despliegue

### Build de Producción
```bash
# Build optimizado
npm run build

# Verificar build
npm run start

# Análisis de bundle
npm run analyze
```

### Docker Deployment
```bash
# Construir imagen
docker build -t ai-telematics-frontend .

# Ejecutar contenedor
docker run -p 3000:3000 ai-telematics-frontend

# Con docker-compose
docker-compose up -d frontend
```

### Vercel Deployment
```bash
# Instalar Vercel CLI
npm i -g vercel

# Desplegar
vercel

# Desplegar en producción
vercel --prod
```

---

## 📈 Performance Optimization

### Code Splitting
```jsx
// Lazy loading de componentes
import dynamic from 'next/dynamic';

const Dashboard = dynamic(() => import('@/components/Dashboard'), {
  loading: () => <p>Cargando dashboard...</p>,
  ssr: false
});

function App() {
  return (
    <div>
      {/* Otros componentes */}
      <Dashboard />
    </div>
  );
}
```

### Image Optimization
```jsx
import Image from 'next/image';

function Logo() {
  return (
    <Image
      src="/logo.png"
      alt="AI Telematics"
      width={40}
      height={40}
      priority
    />
  );
}
```

### Bundle Analysis
```bash
# Analizar tamaño del bundle
npm run build
npm run analyze

# O con webpack-bundle-analyzer
npx @next/bundle-analyzer
```

---

## 🔒 Security Best Practices

### Environment Variables
```javascript
// Usar variables de entorno seguras
const API_URL = process.env.NEXT_PUBLIC_API_URL;
const IS_DEV = process.env.NODE_ENV === 'development';
```

### Input Validation
```jsx
// Validar inputs del usuario
const validateFile = (file) => {
  const allowedTypes = ['application/json'];
  const maxSize = 5 * 1024 * 1024; // 5MB
  
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Tipo de archivo no permitido');
  }
  
  if (file.size > maxSize) {
    throw new Error('Archivo demasiado grande');
  }
};
```

### XSS Prevention
```jsx
// Sanitizar contenido dinámico
import DOMPurify from 'dompurify';

function SafeHTML({ content }) {
  return (
    <div 
      dangerouslySetInnerHTML={{ 
        __html: DOMPurify.sanitize(content) 
      }} 
    />
  );
}
```

---

## 📊 Analytics y Monitoring

### Error Tracking
```javascript
// Error boundary con logging
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Enviar a servicio de logging
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

### Performance Monitoring
```javascript
// Medir performance de componentes
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor';

function MyComponent() {
  usePerformanceMonitor('MyComponent');
  
  return <div>Component content</div>;
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Build Errors
```bash
# Limpiar cache
rm -rf .next
npm run build

# Verificar dependencias
npm ls
npm audit fix
```

#### 2. CORS Issues
```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
    },
  ];
}
```

#### 3. Memory Issues
```bash
# Aumentar Node.js memory limit
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

---

## 📚 Referencias y Recursos

### Documentación Oficial
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

### Herramientas de Desarrollo
- [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/)
- [Next.js Bundle Analyzer](https://www.npmjs.com/package/@next/bundle-analyzer)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)

### Tutoriales y Guías
- [Next.js Learn Course](https://nextjs.org/learn)
- [React Patterns](https://reactpatterns.com/)
- [TailwindCSS UI Components](https://tailwindui.com/)

import React, { useState } from 'react';
import axios from 'axios';
import { 
  Sun, 
  Cloud, 
  CloudRain, 
  CloudSnow, 
  Search, 
  Shirt,
  Zap,
  RefreshCw,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import './App.css';

function App() {
  const [city, setCity] = useState('amizour');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [view, setView] = useState('smart'); // 'smart' or 'basic'

  const getWeatherIcon = (condition) => {
    const icons = {
      'sunny': <Sun className="w-12 h-12 text-yellow-500" />,
      'clear': <Sun className="w-12 h-12 text-yellow-500" />,
      'cloudy': <Cloud className="w-12 h-12 text-gray-500" />,
      'rainy': <CloudRain className="w-12 h-12 text-blue-500" />,
      'rain': <CloudRain className="w-12 h-12 text-blue-500" />,
      'snow': <CloudSnow className="w-12 h-12 text-blue-300" />,
      'snowy': <CloudSnow className="w-12 h-12 text-blue-300" />
    };
    return icons[condition?.toLowerCase()] || <Cloud className="w-12 h-12 text-gray-400" />;
  };

  const getTemperatureColor = (temp) => {
    if (temp < 10) return 'text-blue-600';
    if (temp < 20) return 'text-green-600';
    if (temp < 30) return 'text-orange-500';
    return 'text-red-500';
  };

  const fetchOutfitRecommendation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const endpoint = view === 'smart' 
        ? `http://localhost:8000/smart-outfit/${city}`
        : `http://localhost:8000/outfit-for-city/${city}`;
      
      const response = await axios.get(endpoint);
      setData(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch data');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const ServiceStatus = ({ status }) => (
    <div className="flex items-center gap-2 text-sm">
      {status === 'live' ? (
        <CheckCircle2 className="w-4 h-4 text-green-500" />
      ) : (
        <AlertCircle className="w-4 h-4 text-yellow-500" />
      )}
      <span className={status === 'live' ? 'text-green-600' : 'text-yellow-600'}>
        {status === 'live' ? 'Live' : 'Fallback'}
      </span>
    </div>
  );

  return (
    <div className="min-h-screen py-8 px-4">
      {/* Header */}
      <div className="max-w-4xl mx-auto text-center mb-8 animate-fade-in">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Shirt className="w-10 h-10 text-purple-600" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Smart Wardrobe AI
          </h1>
          <Zap className="w-10 h-10 text-blue-500" />
        </div>
        <p className="text-gray-600 text-lg">
          Get real-time weather-based outfit recommendations from your actual wardrobe!
        </p>
      </div>

      {/* Input Section */}
      <div className="max-w-2xl mx-auto mb-8 animate-slide-up">
        <div className="glass-card rounded-2xl p-6">
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter City Name
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="e.g., amizour, algiers, paris..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onKeyPress={(e) => e.key === 'Enter' && fetchOutfitRecommendation()}
                />
              </div>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={fetchOutfitRecommendation}
                disabled={loading}
                className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <RefreshCw className="w-5 h-5 animate-spin" />
                ) : (
                  <Zap className="w-5 h-5" />
                )}
                {loading ? 'Thinking...' : 'Get Outfit'}
              </button>
            </div>
          </div>

          {/* View Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setView('basic')}
              className={`flex-1 py-2 px-4 rounded-lg transition-all ${
                view === 'basic' 
                  ? 'bg-blue-500 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Basic Recommendation
            </button>
            <button
              onClick={() => setView('smart')}
              className={`flex-1 py-2 px-4 rounded-lg transition-all ${
                view === 'smart' 
                  ? 'bg-purple-500 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Smart Wardrobe
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="max-w-2xl mx-auto mb-6 animate-fade-in">
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <div>
              <p className="text-red-800 font-medium">Oops! Something went wrong</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {data && !loading && (
        <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
          {/* System Status */}
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">System Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-blue-700">Weather Service</span>
                <ServiceStatus status={data.system_status?.weather_service} />
              </div>
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <span className="text-purple-700">Outfit Service</span>
                <ServiceStatus status={data.system_status?.outfit_service} />
              </div>
              {view === 'smart' && (
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-green-700">Wardrobe Service</span>
                  <ServiceStatus status={data.system_status?.wardrobe_service} />
                </div>
              )}
            </div>
          </div>

          {/* Weather Card */}
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">{data.city}</h2>
                <p className="text-gray-600">Current Weather Conditions</p>
              </div>
              {getWeatherIcon(data.real_weather?.condition)}
            </div>
            
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">Temperature</p>
                <p className={`text-3xl font-bold ${getTemperatureColor(data.real_weather?.temperature)}`}>
                  {data.real_weather?.temperature}°C
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Condition</p>
                <p className="text-xl font-semibold text-gray-800 capitalize">
                  {data.real_weather?.condition}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Humidity</p>
                <p className="text-xl font-semibold text-gray-800">
                  {data.real_weather?.humidity || 'N/A'}%
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Source</p>
                <p className="text-sm font-medium text-gray-700 capitalize">
                  {data.real_weather?.source || 'Live'}
                </p>
              </div>
            </div>
          </div>

          {/* Outfit Recommendations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* General Recommendation */}
            <div className="glass-card rounded-2xl p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Shirt className="w-6 h-6 text-blue-500" />
                General Recommendation
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Base Layer</span>
                  <span className="font-semibold text-gray-800">{data.general_recommendation?.base}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Layers</span>
                  <span className="font-semibold text-gray-800">
                    {data.general_recommendation?.layers?.join(', ') || 'None needed'}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Footwear</span>
                  <span className="font-semibold text-gray-800">{data.general_recommendation?.footwear}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-gray-600">Accessories</span>
                  <span className="font-semibold text-gray-800">
                    {data.general_recommendation?.accessories?.join(', ') || 'None'}
                  </span>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-blue-800 text-sm">
                  💡 {data.general_recommendation?.style_tip}
                </p>
              </div>
            </div>

            {/* Smart Wardrobe Match */}
            {view === 'smart' && data.your_actual_outfit && (
              <div className="glass-card rounded-2xl p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <Zap className="w-6 h-6 text-purple-500" />
                  Your Actual Outfit
                  {data.wardrobe_confidence && (
                    <span className={`text-sm px-2 py-1 rounded-full ${
                      data.wardrobe_confidence > 0.7 
                        ? 'bg-green-100 text-green-800' 
                        : data.wardrobe_confidence > 0.4 
                        ? 'bg-yellow-100 text-yellow-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {Math.round(data.wardrobe_confidence * 100)}% Match
                    </span>
                  )}
                </h3>

                <div className="space-y-4">
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <p className="text-sm text-gray-600 mb-1">Top</p>
                    <p className="font-semibold text-gray-800">{data.your_actual_outfit.top?.name}</p>
                    <p className="text-sm text-gray-500">{data.your_actual_outfit.top?.color} • {data.your_actual_outfit.top?.type}</p>
                  </div>

                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <p className="text-sm text-gray-600 mb-1">Bottom</p>
                    <p className="font-semibold text-gray-800">{data.your_actual_outfit.bottom?.name}</p>
                    <p className="text-sm text-gray-500">{data.your_actual_outfit.bottom?.color} • {data.your_actual_outfit.bottom?.type}</p>
                  </div>

                  {data.your_actual_outfit.layer && (
                    <div className="bg-white rounded-lg p-4 shadow-sm">
                      <p className="text-sm text-gray-600 mb-1">Layer</p>
                      <p className="font-semibold text-gray-800">{data.your_actual_outfit.layer.name}</p>
                      <p className="text-sm text-gray-500">{data.your_actual_outfit.layer.color}</p>
                    </div>
                  )}

                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <p className="text-sm text-gray-600 mb-1">Footwear</p>
                    <p className="font-semibold text-gray-800">{data.your_actual_outfit.footwear?.name}</p>
                    <p className="text-sm text-gray-500">{data.your_actual_outfit.footwear?.color}</p>
                  </div>

                  <div className="bg-purple-50 rounded-lg p-3">
                    <p className="text-purple-800 text-sm">
                      ✨ {data.your_actual_outfit.fashion_advice || "You'll look amazing!"}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Fun Message */}
          {data.fun_message && (
            <div className="glass-card rounded-2xl p-6 text-center">
              <p className="text-lg text-gray-700">{data.fun_message}</p>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="max-w-2xl mx-auto text-center animate-fade-in">
          <div className="glass-card rounded-2xl p-12">
            <RefreshCw className="w-16 h-16 text-blue-500 animate-spin mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              AI is thinking about your outfit...
            </h3>
            <p className="text-gray-600">
              Analyzing weather data and matching with your wardrobe
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
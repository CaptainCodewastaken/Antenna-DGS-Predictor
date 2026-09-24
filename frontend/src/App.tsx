import { useState } from 'react'
import { Layout } from './components/Layout/Layout'
import { PredictionCards } from './components/Predictions/PredictionCards'
import { PhysicsReveal } from './components/Predictions/PhysicsReveal'
import { AntennaCanvas } from './components/AntennaCanvas/AntennaCanvas'
import { PolarPattern } from './components/Patterns/PolarPattern'
import { Pattern3D } from './components/Patterns/Pattern3D'
import { SParameterPlot } from './components/Patterns/SParameterPlot'
import { ModelArena } from './components/ModelComparison/ModelArena'
import { usePrediction } from './hooks/usePrediction'
import { usePattern } from './hooks/usePattern'
import './components/Patterns/Patterns.css'
import './App.css'

function App() {
  const [model, setModel] = useState<string>('xgboost')
  const [revealPhysics, setRevealPhysics] = useState<boolean>(false)

  return (
    <Layout>
      {(config) => {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const { data, loading, error } = usePrediction(config)
        
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const { patternData, sParamData } = usePattern(config)

        return (
          <div className="app-container">
            <header className="app-header">
              <h1>Antenna DGS Predictor</h1>
            </header>
            
            <main className="app-main">
              <div className="dashboard-grid">
                {/* Left column: SVG Canvas */}
                <div className="canvas-section">
                  <AntennaCanvas config={config} />
                </div>
                
                {/* Right column: Predictions */}
                <div className="predictions-section">
                  <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '1rem' }}>
                    <label htmlFor="model-select" style={{ color: 'var(--text-secondary)' }}>Model:</label>
                    <select 
                      id="model-select"
                      className="control-input" 
                      value={model} 
                      onChange={(e) => setModel(e.target.value)}
                      style={{ width: '200px' }}
                    >
                      <option value="physics_baseline">Physics Baseline (HFSS)</option>
                      <option value="xgboost">XGBoost (Recommended)</option>
                      <option value="random_forest">Random Forest</option>
                      <option value="svr">SVR</option>
                      <option value="linear_regression">Linear Regression</option>
                      <option value="ridge">Ridge</option>
                      <option value="lasso">Lasso</option>
                      <option value="knn">KNN</option>
                      <option value="decision_tree">Decision Tree</option>
                    </select>
                  </div>

                  {error ? (
                    <div role="alert" style={{ color: 'var(--accent-danger)', textAlign: 'center', padding: '2rem' }}>
                      Error fetching predictions: {error.message}
                    </div>
                  ) : (
                    <button 
                      onClick={() => setRevealPhysics(!revealPhysics)} 
                      aria-expanded={revealPhysics}
                      aria-label="Toggle physics equations"
                      style={{ cursor: 'pointer', background: 'transparent', border: 'none', width: '100%', textAlign: 'left', display: 'block' }} 
                      title="Click to reveal physics equations"
                    >
                      <PredictionCards data={data} loading={loading} selectedModel={model} />
                    </button>
                  )}

                  <PhysicsReveal 
                    config={config} 
                    data={data} 
                    expanded={revealPhysics} 
                    onClose={() => setRevealPhysics(false)} 
                  />
                </div>
              </div>

              {/* Lower Section: Plots */}
              <div className="s11-section">
                <SParameterPlot data={sParamData} />
              </div>

              <div className="patterns-grid">
                <PolarPattern data={patternData} />
                <Pattern3D data={patternData} />
              </div>

              {/* Lowest Section: Model Comparison (Layer 3) */}
              <ModelArena />
            </main>
          </div>
        )
      }}
    </Layout>
  )
}

export default App

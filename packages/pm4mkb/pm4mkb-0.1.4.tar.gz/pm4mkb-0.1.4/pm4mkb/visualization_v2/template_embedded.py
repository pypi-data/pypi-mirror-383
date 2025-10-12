"""
Embedded HTML template for conformance visualization.
"""

CONFORMANCE_TEMPLATE = """<!doctype html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Анализ конформности процессов</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f0f2f5;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        #header {
            background: white;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        #main {
            flex: 1;
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 0;
            overflow: hidden;
        }
        
        #panel {
            background: white;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 4px rgba(0,0,0,0.05);
        }
        
        #viz-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            padding: 10px;
            background: #f0f2f5;
        }
        
        .cy-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: relative;
        }
        
        .cy-title {
            position: absolute;
            top: 10px;
            left: 10px;
            background: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 10;
        }
        
        #cy-baseline, #cy-deviations {
            width: 100%;
            height: 100%;
        }
        
        .conformance-score {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .conformance-score .score {
            font-size: 42px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .conformance-score .label {
            font-size: 12px;
            opacity: 0.9;
        }
        
        .kpi-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
        
        .kpi-section h3 {
            font-size: 16px;
            color: #2c3e50;
            margin-bottom: 12px;
        }
        
        table.kpi-table {
            width: 100%;
            font-size: 13px;
            border-collapse: collapse;
        }
        
        .kpi-table td {
            padding: 8px 4px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .kpi-table td:first-child {
            color: #666;
        }
        
        .kpi-table td:last-child {
            font-weight: 600;
            text-align: right;
        }
        
        .deviation-row {
            background: #fff5f5;
        }
        
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            background: #f8d7da;
            color: #721c24;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.0/cytoscape.min.js"></script>
</head>
<body>
    <div id="header">
        <h2>🏦 Анализ конформности процессов</h2>
        <div style="margin-left: auto; font-size: 14px; color: #666;">
            Сравнение с эталонной моделью
        </div>
    </div>
    
    <div id="main">
        <div id="panel">
            <div class="conformance-score">
                <div class="label">УРОВЕНЬ КОНФОРМНОСТИ</div>
                <div class="score">{{CONFORMANCE_RATE}}%</div>
                <div class="label">{{CONFORMANT_TRANSITIONS}}/{{TOTAL_TRANSITIONS}} переходов</div>
            </div>
            
            <div class="kpi-section">
                <h3>📊 Статистика процесса</h3>
                <table class="kpi-table">
                    <tr><td>Всего активностей</td><td>{{TOTAL_ACTIVITIES}}</td></tr>
                    <tr><td>Уникальных переходов</td><td>{{TOTAL_TRANSITIONS}}</td></tr>
                    <tr><td>Отклонений от эталона</td><td>{{DEVIATION_COUNT}}</td></tr>
                </table>
            </div>
            
            <div class="kpi-section">
                <h3>⚠️ Отклонения от эталона</h3>
                <table class="kpi-table">
                    {{DEVIATIONS_TABLE}}
                </table>
            </div>
        </div>
        
        <div id="viz-container">
            <div class="cy-container">
                <div class="cy-title">✅ Эталонная модель</div>
                <div id="cy-baseline"></div>
            </div>
            <div class="cy-container">
                <div class="cy-title">📊 Фактический процесс</div>
                <div id="cy-deviations"></div>
            </div>
        </div>
    </div>
    
    <script>
        const referenceData = {{REFERENCE_DATA}};
        const actualData = {{ACTUAL_DATA}};
        const deviationIndices = {{DEVIATION_INDICES}};
        
        const graphStyle = [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'background-color': '#3498db',
                    'color': '#fff',
                    'width': 50,
                    'height': 50,
                    'font-size': '11px',
                    'font-weight': 'bold',
                    'border-width': 2,
                    'border-color': '#2980b9'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#95a5a6',
                    'target-arrow-color': '#95a5a6',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            },
            {
                selector: '.deviation',
                style: {
                    'line-color': '#e74c3c',
                    'target-arrow-color': '#e74c3c',
                    'width': 4
                }
            },
            {
                selector: '.conformant',
                style: {
                    'line-color': '#27ae60',
                    'target-arrow-color': '#27ae60'
                }
            }
        ];
        
        // Initialize reference model
        const cyReference = cytoscape({
            container: document.getElementById('cy-baseline'),
            elements: referenceData,
            style: graphStyle,
            layout: {
                name: 'breadthfirst',
                directed: true,
                spacingFactor: 1.5,
                fit: true,
                padding: 30
            }
        });
        
        // Initialize actual process
        const cyActual = cytoscape({
            container: document.getElementById('cy-deviations'),
            elements: actualData,
            style: graphStyle,
            layout: {
                name: 'breadthfirst',
                directed: true,
                spacingFactor: 1.5,
                fit: true,
                padding: 30
            }
        });
        
        // Mark deviations
        setTimeout(() => {
            deviationIndices.forEach(edgeId => {
                cyActual.$('#' + edgeId).addClass('deviation');
            });
            
            // Mark conformant edges
            cyActual.edges().forEach(edge => {
                if (!deviationIndices.includes(edge.id())) {
                    edge.addClass('conformant');
                }
            });
        }, 100);
    </script>
</body>
</html>"""

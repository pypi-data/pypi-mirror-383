"""
Enhanced HTML template - Clean with dark logo in header.
Version 0.1.3 - Support for activity codes mapping and automatic initials
"""

ENHANCED_CONFORMANCE_TEMPLATE = """<!doctype html>
<html>
<head>
    <meta charset="utf-8" />
    <title>PM4MKB - Процесс Майнинг МКБ | Case {{CASE_ID}}</title>
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
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 15px 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: white;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header-logo {
            height: 35px;
            filter: brightness(0) invert(1);  /* Make dark logo white */
        }
        
        .header-title {
            font-size: 22px;
            font-weight: 600;
            color: white;
        }
        
        .case-info {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }
        
        #main {
            flex: 1;
            display: grid;
            grid-template-columns: 400px 1fr;
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
        
        #cy-standard, #cy-actual {
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
            position: relative;
            overflow: hidden;
        }
        
        .conformance-score::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .conformance-score .score {
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
            position: relative;
            z-index: 1;
        }
        
        .conformance-score .label {
            font-size: 12px;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        .category-legend {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .category-legend h4 {
            font-size: 14px;
            margin-bottom: 10px;
            color: #495057;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 12px;
        }
        
        .legend-color {
            width: 24px;
            height: 3px;
            margin-right: 10px;
            border-radius: 2px;
        }
        
        .legend-color.conformant { background: #27ae60; }
        .legend-color.normal { background: #3498db; }
        .legend-color.rework { background: #f39c12; }
        .legend-color.exception { background: #9b59b6; }
        .legend-color.deviation { background: #e74c3c; }
        .legend-color.forbidden { background: #c0392b; }
        
        .category-stats {
            margin-top: 20px;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
            font-size: 13px;
        }
        
        .stat-label {
            color: #6c757d;
        }
        
        .stat-value {
            font-weight: 600;
        }
        
        .activities-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }
        
        .activities-section h4 {
            font-size: 14px;
            color: #495057;
            margin-bottom: 10px;
        }
        
        .activity-list {
            font-size: 12px;
            color: #6c757d;
        }
        
        .activity-item {
            padding: 4px 0;
        }
        
        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            margin-left: 5px;
        }
        
        .badge.optional { background: #e3f2fd; color: #1976d2; }
        .badge.required { background: #e8f5e9; color: #2e7d32; }
        .badge.forbidden { background: #ffebee; color: #c62828; }
        
        .footer-branding {
            text-align: center;
            padding: 12px;
            color: #888;
            font-size: 11px;
            border-top: 1px solid #e0e0e0;
            margin-top: 20px;
        }
        
        /* Tooltip styles */
        .node-tooltip {
            position: fixed;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            pointer-events: none;
            z-index: 10000;
            display: none;
            max-width: 250px;
            white-space: nowrap;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .node-tooltip.show {
            display: block;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.0/cytoscape.min.js"></script>
</head>
<body>
    <div id="header">
        <div class="header-left">
            <img src="data:image/png;base64,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" alt="PM4MKB" class="header-logo" />
            <div class="header-title">Анализ процессов</div>
        </div>
        <div class="case-info">Case ID: {{CASE_ID}}</div>
    </div>
    
    <div id="main">
        <div id="panel">
            <div class="conformance-score">
                <div class="label">УРОВЕНЬ КОНФОРМНОСТИ</div>
                <div class="score">{{CONFORMANCE_LEVEL}}%</div>
                <div class="label">Case {{CASE_ID}}</div>
            </div>
            
            <div class="category-legend">
                <h4>📊 Категории переходов</h4>
                <div class="legend-item">
                    <div class="legend-color conformant"></div>
                    <span>Соответствует стандарту</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color normal"></div>
                    <span>Нормальная вариация (PAUSE)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color rework"></div>
                    <span>Повторная обработка</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color deviation"></div>
                    <span>Отклонение от стандарта</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color forbidden"></div>
                    <span>Недопустимое действие</span>
                </div>
            </div>
            
            <div class="category-stats">
                <h4>📈 Статистика</h4>
                {{STATISTICS}}
            </div>
            
            <div class="activities-section">
                <h4>⚠️ Проблемные переходы</h4>
                <div class="activity-list">
                    {{PROBLEMS}}
                </div>
            </div>
            
            <div class="footer-branding">
                Powered by PM4MKB © 2025
            </div>
        </div>
        
        <div id="viz-container">
            <div class="cy-container">
                <div class="cy-title">✅ Стандарт процесса</div>
                <div id="cy-standard"></div>
            </div>
            <div class="cy-container">
                <div class="cy-title">📊 Case {{CASE_ID}}</div>
                <div id="cy-actual"></div>
            </div>
        </div>
    </div>
    
    <!-- Tooltip element -->
    <div id="node-tooltip" class="node-tooltip"></div>
    
    <script>
        const standardData = {{STANDARD_DATA}};
        const actualData = {{ACTUAL_DATA}};
        const edgeCategories = {{EDGE_CATEGORIES}};
        
        // Activity codes mapping - will be replaced during generation
        const activityCodes = {{ACTIVITY_CODES}};
        
        console.log('PM4MKB v0.1.3: Initializing with activity codes...');
        
        // Function to get activity code or initial
        const getActivityCode = (label) => {
            // Check if custom code exists
            if (activityCodes && activityCodes[label]) {
                return activityCodes[label];
            }
            
            // Fallback to first letter + dot
            if (label && label.length > 0) {
                // Handle special cases
                if (label.startsWith('PAUSE')) {
                    return 'P.';
                }
                if (label.startsWith('ERROR')) {
                    return 'E!';
                }
                
                // Get first letter and add dot
                const firstChar = label.charAt(0).toUpperCase();
                return firstChar + '.';
            }
            
            return label;
        };
        
        // Process node data to add codes
        const processNodeData = (data) => {
            if (data.nodes) {
                data.nodes.forEach(node => {
                    if (node.data && node.data.label) {
                        // Store original label
                        node.data.fullLabel = node.data.label;
                        // Create code or initial
                        const code = getActivityCode(node.data.label);
                        // Only use code if it's different from full label
                        if (code !== node.data.label) {
                            node.data.label = code;
                        }
                    }
                });
            }
            return data;
        };
        
        // Process data to add codes
        const processedStandardData = processNodeData(JSON.parse(JSON.stringify(standardData)));
        const processedActualData = processNodeData(JSON.parse(JSON.stringify(actualData)));
        
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
                    'font-size': '14px',
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
                selector: '.conformant',
                style: {
                    'line-color': '#27ae60',
                    'target-arrow-color': '#27ae60',
                    'width': 3
                }
            },
            {
                selector: '.normal',
                style: {
                    'line-color': '#3498db',
                    'target-arrow-color': '#3498db',
                    'width': 3
                }
            },
            {
                selector: '.rework',
                style: {
                    'line-color': '#f39c12',
                    'target-arrow-color': '#f39c12',
                    'line-style': 'dashed',
                    'width': 3
                }
            },
            {
                selector: '.deviation',
                style: {
                    'line-color': '#e74c3c',
                    'target-arrow-color': '#e74c3c',
                    'width': 4,
                    'z-index': 999
                }
            },
            {
                selector: '.forbidden',
                style: {
                    'line-color': '#c0392b',
                    'target-arrow-color': '#c0392b',
                    'width': 5,
                    'z-index': 1000
                }
            }
        ];
        
        // Tooltip element
        const tooltip = document.getElementById('node-tooltip');
        
        // Function to add tooltip handlers
        const addTooltipHandlers = (cy) => {
            cy.on('mouseover', 'node', function(event) {
                const node = event.target;
                const fullLabel = node.data('fullLabel');
                const shortLabel = node.data('label');
                
                // Show tooltip with full label if it exists and differs
                if (fullLabel && fullLabel !== shortLabel) {
                    tooltip.textContent = fullLabel;
                    tooltip.classList.add('show');
                    
                    // Position tooltip above node
                    const renderedPos = node.renderedPosition();
                    const container = cy.container().getBoundingClientRect();
                    
                    tooltip.style.left = (container.left + renderedPos.x - tooltip.offsetWidth / 2) + 'px';
                    tooltip.style.top = (container.top + renderedPos.y - 45) + 'px';
                }
            });
            
            cy.on('mouseout', 'node', function() {
                tooltip.classList.remove('show');
            });
            
            // Hide tooltip when panning or zooming
            cy.on('pan zoom', function() {
                tooltip.classList.remove('show');
            });
        };
        
        const cyStandard = cytoscape({
            container: document.getElementById('cy-standard'),
            elements: processedStandardData,
            style: graphStyle,
            layout: {
                name: 'breadthfirst',
                directed: true,
                spacingFactor: 1.5,
                fit: true,
                padding: 30
            }
        });
        
        const cyActual = cytoscape({
            container: document.getElementById('cy-actual'),
            elements: processedActualData,
            style: graphStyle,
            layout: {
                name: 'breadthfirst',
                directed: true,
                spacingFactor: 1.5,
                fit: true,
                padding: 30
            }
        });
        
        // Add tooltip handlers to both graphs
        addTooltipHandlers(cyStandard);
        addTooltipHandlers(cyActual);
        
        cyActual.ready(function() {
            for (const [edgeId, category] of Object.entries(edgeCategories)) {
                const edges = cyActual.edges().filter(function(edge) {
                    return edge.id() === edgeId || 
                           edge.id().startsWith(edgeId + '_');
                });
                
                edges.forEach(function(edge) {
                    edge.addClass(category);
                });
            }
            
            cyActual.style().update();
        });
    </script>
</body>
</html>"""
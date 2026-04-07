/**
 * JavaScript Principal - Análise ATS de Currículo
 * 
 * Gerencia upload de arquivo, chamada à API e exibição de resultados.
 */

// =============================================================================
// ELEMENTOS DOM
// =============================================================================

const uploadSection = document.getElementById('uploadSection');
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFileBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');

let selectedFile = null;

// =============================================================================
// EVENT LISTENERS
// =============================================================================

// Click no botão de selecionar arquivo
selectFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

// Click na área de upload
uploadBox.addEventListener('click', () => {
    fileInput.click();
});

// Arquivo selecionado
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileSelect(file);
    }
});

// Drag and drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('drag-over');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    
    const file = e.dataTransfer.files[0];
    if (file) {
        handleFileSelect(file);
    }
});

// Remover arquivo
removeFileBtn.addEventListener('click', () => {
    clearFileSelection();
});

// Analisar
analyzeBtn.addEventListener('click', () => {
    if (selectedFile) {
        analyzeFile(selectedFile);
    }
});

// Nova análise
newAnalysisBtn.addEventListener('click', () => {
    resetInterface();
});

// =============================================================================
// FUNÇÕES
// =============================================================================

/**
 * Processa arquivo selecionado
 */
function handleFileSelect(file) {
    // Validar extensão
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Por favor, selecione um arquivo PDF.');
        return;
    }
    
    // Validar tamanho (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError('Arquivo muito grande. O tamanho máximo é 16MB.');
        return;
    }
    
    selectedFile = file;
    
    // Mostrar preview
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    uploadBox.classList.add('hidden');
    filePreview.classList.remove('hidden');
    analyzeBtn.classList.remove('hidden');
}

/**
 * Limpa seleção de arquivo
 */
function clearFileSelection() {
    selectedFile = null;
    fileInput.value = '';
    uploadBox.classList.remove('hidden');
    filePreview.classList.add('hidden');
    analyzeBtn.classList.add('hidden');
}

/**
 * Envia arquivo para análise
 */
async function analyzeFile(file) {
    // Mostrar loading
    uploadSection.classList.add('hidden');
    loading.classList.remove('hidden');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Erro ao analisar currículo.');
            resetInterface();
        }
    } catch (error) {
        console.error('Erro:', error);
        showError('Erro de conexão. Tente novamente.');
        resetInterface();
    } finally {
        loading.classList.add('hidden');
    }
}

/**
 * Exibe resultados da análise
 */
function displayResults(data) {
    const { extraction, analysis } = data;
    
    // Score principal
    document.getElementById('scoreValue').textContent = analysis.final_score;
    document.getElementById('matchLevel').textContent = analysis.match_level;
    document.getElementById('recommendation').textContent = analysis.recommendation;
    
    // Cor do score
    const scoreCard = document.getElementById('scoreCard');
    scoreCard.classList.remove('score-excellent', 'score-good', 'score-regular', 'score-weak');
    if (analysis.final_score >= 80) {
        scoreCard.classList.add('score-excellent');
    } else if (analysis.final_score >= 60) {
        scoreCard.classList.add('score-good');
    } else if (analysis.final_score >= 40) {
        scoreCard.classList.add('score-regular');
    } else {
        scoreCard.classList.add('score-weak');
    }
    
    // Barras de score
    setScoreBar('keywordBar', 'keywordScore', analysis.keyword_score);
    setScoreBar('structureBar', 'structureScore', analysis.structure_score);
    setScoreBar('readabilityBar', 'readabilityScore', analysis.readability_score);
    
    // Keywords
    displayKeywords(analysis.keywords_found);
    displayAreas(analysis.keywords_by_area);
    
    // Estrutura
    displaySections(analysis.sections_detected, analysis.sections_missing);
    
    // Contato
    displayContact(analysis.contact_info);
    
    // Feedback
    displayFeedback('warnings', analysis.warnings);
    displayFeedback('suggestions', analysis.suggestions);
    displayFeedback('positives', analysis.positives);
    
    // Extração
    displayExtraction(extraction, analysis);
    
    // Dados estruturados extraídos
    if (analysis.extracted_data) {
        displayExtractedData(analysis.extracted_data);
    }
    
    // Mostrar resultados
    resultsSection.classList.remove('hidden');
}

/**
 * Define valor da barra de score
 */
function setScoreBar(barId, valueId, score) {
    document.getElementById(barId).style.width = score + '%';
    document.getElementById(valueId).textContent = score + '%';
}

/**
 * Exibe keywords encontradas
 */
function displayKeywords(keywords) {
    const grid = document.getElementById('keywordsGrid');
    grid.innerHTML = '';
    
    if (!keywords || keywords.length === 0) {
        grid.innerHTML = '<p class="no-data">Nenhuma keyword técnica identificada</p>';
        return;
    }
    
    // Contar keywords por importância
    const counts = {critical: 0, high: 0, medium: 0};
    keywords.forEach(kw => {
        if (counts[kw.importance] !== undefined) counts[kw.importance]++;
    });
    
    // Legenda de cores
    const legend = document.createElement('div');
    legend.className = 'keywords-legend';
    legend.innerHTML = `
        <span class="legend-item">
            <span class="keyword-tag critical">●</span> Principal (${counts.critical})
        </span>
        <span class="legend-item">
            <span class="keyword-tag high">●</span> Secundária (${counts.high})
        </span>
        <span class="legend-item">
            <span class="keyword-tag medium">●</span> Contexto (${counts.medium})
        </span>
    `;
    grid.appendChild(legend);
    
    // Tags de keywords
    keywords.forEach(kw => {
        const tag = document.createElement('span');
        tag.className = `keyword-tag ${kw.importance}`;
        tag.textContent = kw.keyword;
        tag.title = `Encontrado como: ${kw.found_as} (${kw.match_type})`;
        grid.appendChild(tag);
    });
}

/**
 * Exibe áreas de atuação
 */
function displayAreas(areas) {
    const list = document.getElementById('areasList');
    list.innerHTML = '';
    
    if (!areas || Object.keys(areas).length === 0) {
        list.innerHTML = '<p class="no-data">Nenhuma área específica detectada</p>';
        return;
    }
    
    // Ordenar por quantidade
    const sortedAreas = Object.entries(areas).sort((a, b) => b[1].count - a[1].count);
    
    sortedAreas.forEach(([area, data]) => {
        const item = document.createElement('div');
        item.className = 'area-item';
        item.innerHTML = `
            <span class="area-name">${capitalizeFirst(area)}</span>
            <div class="area-bar">
                <div class="area-bar-fill" style="width: ${Math.min(data.percentage, 100)}%"></div>
            </div>
            <span class="area-count">${data.count} keywords</span>
        `;
        list.appendChild(item);
    });
}

/**
 * Exibe seções detectadas e faltantes
 */
function displaySections(detected, missing) {
    const listDetected = document.getElementById('sectionsList');
    const listMissing = document.getElementById('sectionsMissing');
    
    listDetected.innerHTML = '';
    listMissing.innerHTML = '';
    
    if (detected && detected.length > 0) {
        detected.forEach(section => {
            const item = document.createElement('div');
            item.className = 'section-item detected';
            item.innerHTML = `
                <span class="section-icon">✅</span>
                <span class="section-name">${section.name}</span>
            `;
            listDetected.appendChild(item);
        });
    } else {
        listDetected.innerHTML = '<p class="no-data">Nenhuma seção detectada</p>';
    }
    
    if (missing && missing.length > 0) {
        missing.forEach(section => {
            const item = document.createElement('div');
            item.className = 'section-item missing';
            item.innerHTML = `
                <span class="section-icon">❌</span>
                <span class="section-name">${section}</span>
            `;
            listMissing.appendChild(item);
        });
    } else {
        listMissing.innerHTML = '<p class="no-data">Todas as seções essenciais foram detectadas</p>';
    }
}

/**
 * Exibe informações de contato
 */
function displayContact(contact) {
    const grid = document.getElementById('contactGrid');
    grid.innerHTML = '';
    
    const icons = {
        email: '📧',
        telefone: '📱',
        linkedin: '💼',
        github: '💻'
    };
    
    const labels = {
        email: 'Email',
        telefone: 'Telefone',
        linkedin: 'LinkedIn',
        github: 'GitHub'
    };
    
    Object.entries(contact).forEach(([key, value]) => {
        const item = document.createElement('div');
        item.className = `contact-item ${value ? 'found' : 'missing'}`;
        item.innerHTML = `
            <span class="contact-icon">${icons[key] || '📋'}</span>
            <div class="contact-details">
                <span class="contact-label">${labels[key] || key}</span>
                <span class="contact-value">${value || 'Não encontrado'}</span>
            </div>
        `;
        grid.appendChild(item);
    });
}

/**
 * Exibe lista de feedback
 */
function displayFeedback(sectionId, items) {
    const section = document.getElementById(sectionId);
    const list = section.querySelector('.feedback-list');
    list.innerHTML = '';
    
    if (!items || items.length === 0) {
        section.classList.add('hidden');
        return;
    }
    
    section.classList.remove('hidden');
    
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'feedback-item';
        div.textContent = item;
        list.appendChild(div);
    });
}

/**
 * Exibe informações de extração
 */
function displayExtraction(extraction, analysis) {
    const grid = document.getElementById('extractionGrid');
    grid.innerHTML = `
        <div class="extraction-item">
            <div class="extraction-value">${extraction.page_count}</div>
            <div class="extraction-label">Páginas</div>
        </div>
        <div class="extraction-item">
            <div class="extraction-value">${extraction.word_count}</div>
            <div class="extraction-label">Palavras</div>
        </div>
        <div class="extraction-item">
            <div class="extraction-value">${analysis.unique_keywords}</div>
            <div class="extraction-label">Keywords</div>
        </div>
        <div class="extraction-item">
            <div class="extraction-value">${analysis.processing_time_ms}ms</div>
            <div class="extraction-label">Tempo</div>
        </div>
    `;
}

/**
 * Exibe dados estruturados extraídos do currículo
 */
function displayExtractedData(data) {
    const container = document.getElementById('extractedDataContent');
    if (!container) return;
    
    if (!data) {
        container.innerHTML = '<p class="no-data">Nenhum dado estruturado extraído</p>';
        return;
    }
    
    let html = '';
    
    // Nome e Localização
    if (data.name || data.location) {
        html += `<div class="extracted-section">
            <h4>👤 Dados Pessoais</h4>
            <div class="extracted-details">`;
        if (data.name) html += `<div class="extracted-row"><strong>Nome:</strong> ${data.name}</div>`;
        if (data.location) html += `<div class="extracted-row"><strong>Localização:</strong> ${data.location}</div>`;
        if (data.email) html += `<div class="extracted-row"><strong>Email:</strong> ${data.email}</div>`;
        if (data.phone) html += `<div class="extracted-row"><strong>Telefone:</strong> ${data.phone}</div>`;
        if (data.linkedin) html += `<div class="extracted-row"><strong>LinkedIn:</strong> ${data.linkedin}</div>`;
        html += `</div></div>`;
    }
    
    // Resumo/Objetivo
    if (data.summary || data.objective) {
        html += `<div class="extracted-section">
            <h4>📝 Resumo Profissional</h4>
            <div class="extracted-details">`;
        if (data.summary) html += `<div class="extracted-text">${data.summary}</div>`;
        if (data.objective) html += `<div class="extracted-text"><strong>Objetivo:</strong> ${data.objective}</div>`;
        html += `</div></div>`;
    }
    
    // Experiências
    if (data.experiences && data.experiences.length > 0) {
        html += `<div class="extracted-section">
            <h4>💼 Experiência Profissional (${data.experiences.length} encontrada${data.experiences.length > 1 ? 's' : ''})</h4>
            <div class="experiences-list">`;
        data.experiences.forEach((exp, idx) => {
            html += `<div class="experience-item">
                <div class="experience-header">`;
            if (exp.role) html += `<span class="exp-role">${exp.role}</span>`;
            if (exp.company) html += `<span class="exp-company">@ ${exp.company}</span>`;
            html += `</div>`;
            if (exp.period) html += `<div class="exp-period">📅 ${exp.period}</div>`;
            if (exp.description) html += `<div class="exp-description">${exp.description.substring(0, 200)}${exp.description.length > 200 ? '...' : ''}</div>`;
            html += `</div>`;
        });
        html += `</div></div>`;
    }
    
    // Formação
    if (data.education && data.education.length > 0) {
        html += `<div class="extracted-section">
            <h4>🎓 Formação Acadêmica</h4>
            <div class="education-list">`;
        data.education.forEach(edu => {
            html += `<div class="education-item">📚 ${edu}</div>`;
        });
        html += `</div></div>`;
    }
    
    // Habilidades por Categoria
    if (data.skills_by_category && Object.keys(data.skills_by_category).length > 0) {
        html += `<div class="extracted-section">
            <h4>🛠️ Habilidades Técnicas (por categoria)</h4>
            <div class="skills-categories">`;
        const categoryNames = {
            cloud: '☁️ Cloud',
            devops: '🔧 DevOps',
            programacao: '💻 Programação',
            banco_dados: '🗃️ Banco de Dados',
            infra: '🖥️ Infraestrutura',
            seguranca: '🔒 Segurança',
            metodologias: '📋 Metodologias',
            ferramentas: '🔨 Ferramentas',
            outros: '📦 Outros'
        };
        Object.entries(data.skills_by_category).forEach(([cat, skills]) => {
            html += `<div class="skill-category">
                <div class="category-name">${categoryNames[cat] || capitalizeFirst(cat)}</div>
                <div class="category-skills">`;
            skills.forEach(skill => {
                html += `<span class="skill-tag">${skill}</span>`;
            });
            html += `</div></div>`;
        });
        html += `</div></div>`;
    }
    
    // Idiomas
    if (data.languages && data.languages.length > 0) {
        html += `<div class="extracted-section">
            <h4>🌐 Idiomas</h4>
            <div class="languages-list">`;
        data.languages.forEach(lang => {
            html += `<span class="language-tag">${lang}</span>`;
        });
        html += `</div></div>`;
    }
    
    // Certificações
    if (data.certifications && data.certifications.length > 0) {
        html += `<div class="extracted-section">
            <h4>📜 Certificações</h4>
            <div class="certifications-list">`;
        data.certifications.forEach(cert => {
            html += `<div class="certification-item">🏆 ${cert}</div>`;
        });
        html += `</div></div>`;
    }
    
    container.innerHTML = html || '<p class="no-data">Nenhum dado estruturado encontrado no currículo</p>';
}

/**
 * Reseta interface para nova análise
 */
function resetInterface() {
    clearFileSelection();
    resultsSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
}

/**
 * Exibe mensagem de erro
 */
function showError(message) {
    alert(message);
}

/**
 * Formata tamanho do arquivo
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Capitaliza primeira letra
 */
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
}

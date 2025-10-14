/**
 * Interactive Status Management for BDD Reports
 * Allows users to override test status and assign bug IDs directly from the web UI
 */

class StatusManager {
    constructor() {
        this.baseUrl = window.location.origin;
        this.init();
    }

    init() {
        this.addStatusManagementUI();
        this.loadExistingData();
        this.setupEventListeners();
    }

    addStatusManagementUI() {
        // Add status management panel to the page
        const panel = document.createElement('div');
        panel.id = 'status-management-panel';
        panel.innerHTML = `
            <div class="status-panel">
                <div class="panel-header">
                    <h3>🔧 Test Status Management</h3>
                    <button class="panel-toggle" onclick="toggleStatusPanel()">−</button>
                </div>
                <div class="panel-content">
                    <div class="management-tabs">
                        <button class="tab-btn active" onclick="showTab('override')">Status Override</button>
                        <button class="tab-btn" onclick="showTab('bug')">Bug Tracking</button>
                        <button class="tab-btn" onclick="showTab('list')">View All</button>
                    </div>
                    
                    <!-- Status Override Tab -->
                    <div id="override-tab" class="tab-content active">
                        <h4>Override Test Status</h4>
                        <form id="override-form">
                            <div class="form-group">
                                <label>Test Name:</label>
                                <select id="test-select-override" required>
                                    <option value="">Select a test...</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>New Status:</label>
                                <select id="new-status" required>
                                    <option value="passed">Passed</option>
                                    <option value="failed">Failed</option>
                                    <option value="skipped">Skipped</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Reason:</label>
                                <textarea id="override-reason" placeholder="Business justification for status change..." required></textarea>
                            </div>
                            <div class="form-group">
                                <label>User:</label>
                                <input type="text" id="override-user" placeholder="Your name" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Apply Override</button>
                        </form>
                    </div>
                    
                    <!-- Bug Tracking Tab -->
                    <div id="bug-tab" class="tab-content">
                        <h4>Assign Bug ID</h4>
                        <form id="bug-form">
                            <div class="form-group">
                                <label>Test Name:</label>
                                <select id="test-select-bug" required>
                                    <option value="">Select a test...</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Bug ID:</label>
                                <input type="text" id="bug-id" placeholder="e.g., JIRA-123, GH-456" required>
                            </div>
                            <div class="form-group">
                                <label>Description:</label>
                                <textarea id="bug-description" placeholder="Bug description..." required></textarea>
                            </div>
                            <div class="form-group">
                                <label>Priority:</label>
                                <select id="bug-priority" required>
                                    <option value="Low">Low</option>
                                    <option value="Medium" selected>Medium</option>
                                    <option value="High">High</option>
                                    <option value="Critical">Critical</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>User:</label>
                                <input type="text" id="bug-user" placeholder="Your name" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Assign Bug</button>
                        </form>
                    </div>
                    
                    <!-- List Tab -->
                    <div id="list-tab" class="tab-content">
                        <h4>Current Overrides & Bugs</h4>
                        <div id="status-list">
                            <div class="loading">Loading...</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add CSS styles
        const styles = document.createElement('style');
        styles.textContent = `
            .status-panel {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 400px;
                background: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                font-family: Arial, sans-serif;
            }
            
            .panel-header {
                background: #f8f9fa;
                padding: 15px;
                border-bottom: 1px solid #dee2e6;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-radius: 8px 8px 0 0;
            }
            
            .panel-header h3 {
                margin: 0;
                font-size: 16px;
                color: #333;
            }
            
            .panel-toggle {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .panel-content {
                padding: 20px;
                max-height: 600px;
                overflow-y: auto;
            }
            
            .panel-content.collapsed {
                display: none;
            }
            
            .management-tabs {
                display: flex;
                margin-bottom: 20px;
                border-bottom: 1px solid #dee2e6;
            }
            
            .tab-btn {
                background: none;
                border: none;
                padding: 10px 15px;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                font-size: 14px;
            }
            
            .tab-btn.active {
                border-bottom-color: #007bff;
                color: #007bff;
                font-weight: bold;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .form-group {
                margin-bottom: 15px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                font-size: 12px;
                color: #555;
            }
            
            .form-group input,
            .form-group select,
            .form-group textarea {
                width: 100%;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
                box-sizing: border-box;
            }
            
            .form-group textarea {
                height: 80px;
                resize: vertical;
            }
            
            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
            }
            
            .btn-primary {
                background: #007bff;
                color: white;
            }
            
            .btn-primary:hover {
                background: #0056b3;
            }
            
            .btn-danger {
                background: #dc3545;
                color: white;
            }
            
            .btn-danger:hover {
                background: #c82333;
            }
            
            .status-item {
                background: #f8f9fa;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 4px;
                border-left: 4px solid #007bff;
            }
            
            .status-item.bug {
                border-left-color: #ffc107;
            }
            
            .status-item h5 {
                margin: 0 0 8px 0;
                font-size: 14px;
                color: #333;
            }
            
            .status-item p {
                margin: 4px 0;
                font-size: 12px;
                color: #666;
            }
            
            .status-actions {
                margin-top: 10px;
            }
            
            .status-actions button {
                margin-right: 5px;
                padding: 4px 8px;
                font-size: 11px;
            }
            
            .success-message {
                background: #d4edda;
                color: #155724;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 15px;
                border: 1px solid #c3e6cb;
            }
            
            .error-message {
                background: #f8d7da;
                color: #721c24;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 15px;
                border: 1px solid #f5c6cb;
            }
            
            @media (max-width: 768px) {
                .status-panel {
                    position: relative;
                    width: 100%;
                    margin: 20px 0;
                    right: auto;
                    top: auto;
                }
            }
        `;
        
        document.head.appendChild(styles);
        document.body.appendChild(panel);
    }

    setupEventListeners() {
        // Override form submission
        document.getElementById('override-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleOverride();
        });

        // Bug form submission
        document.getElementById('bug-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleBugAssignment();
        });

        // Populate test dropdowns
        this.populateTestDropdowns();
    }

    populateTestDropdowns() {
        const tests = this.getTestsFromPage();
        const overrideSelect = document.getElementById('test-select-override');
        const bugSelect = document.getElementById('test-select-bug');

        tests.forEach(test => {
            const option1 = new Option(test.name, test.name);
            const option2 = new Option(test.name, test.name);
            overrideSelect.appendChild(option1);
            bugSelect.appendChild(option2);
        });
    }

    getTestsFromPage() {
        const tests = [];
        // Extract test names from the current page
        document.querySelectorAll('.test-name, .scenario-name').forEach(element => {
            const name = element.textContent.trim();
            if (name) {
                tests.push({ name });
            }
        });
        return tests;
    }

    handleOverride() {
        const testName = document.getElementById('test-select-override').value;
        const newStatus = document.getElementById('new-status').value;
        const reason = document.getElementById('override-reason').value;
        const user = document.getElementById('override-user').value;

        const override = {
            testName,
            originalStatus: 'failed', // Assume failed for now
            newStatus,
            reason,
            user,
            timestamp: new Date().toISOString()
        };

        this.saveOverride(override);
        this.showMessage('Status override applied successfully!', 'success');
        this.updatePageDisplay();
        document.getElementById('override-form').reset();
    }

    handleBugAssignment() {
        const testName = document.getElementById('test-select-bug').value;
        const bugId = document.getElementById('bug-id').value;
        const description = document.getElementById('bug-description').value;
        const priority = document.getElementById('bug-priority').value;
        const user = document.getElementById('bug-user').value;

        const bug = {
            testName,
            bugId,
            description,
            priority,
            user,
            status: 'Open',
            timestamp: new Date().toISOString()
        };

        this.saveBug(bug);
        this.showMessage('Bug ID assigned successfully!', 'success');
        this.updatePageDisplay();
        document.getElementById('bug-form').reset();
    }

    saveOverride(override) {
        const overrides = this.getStoredOverrides();
        const key = this.normalizeTestName(override.testName);
        overrides[key] = override;
        localStorage.setItem('bdd_status_overrides', JSON.stringify(overrides));
    }

    saveBug(bug) {
        const bugs = this.getStoredBugs();
        const key = this.normalizeTestName(bug.testName);
        bugs[key] = bug;
        localStorage.setItem('bdd_bug_tracking', JSON.stringify(bugs));
    }

    getStoredOverrides() {
        const stored = localStorage.getItem('bdd_status_overrides');
        return stored ? JSON.parse(stored) : {};
    }

    getStoredBugs() {
        const stored = localStorage.getItem('bdd_bug_tracking');
        return stored ? JSON.parse(stored) : {};
    }

    normalizeTestName(name) {
        return name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    }

    loadExistingData() {
        this.updateListTab();
        this.updatePageDisplay();
    }

    updateListTab() {
        const listContainer = document.getElementById('status-list');
        const overrides = this.getStoredOverrides();
        const bugs = this.getStoredBugs();

        let html = '';

        // Show overrides
        Object.values(overrides).forEach(override => {
            html += `
                <div class="status-item">
                    <h5>📋 Status Override: ${override.testName}</h5>
                    <p><strong>Status:</strong> ${override.originalStatus} → ${override.newStatus}</p>
                    <p><strong>Reason:</strong> ${override.reason}</p>
                    <p><strong>User:</strong> ${override.user} | <strong>Date:</strong> ${new Date(override.timestamp).toLocaleString()}</p>
                    <div class="status-actions">
                        <button class="btn btn-danger" onclick="statusManager.removeOverride('${override.testName}')">Remove</button>
                    </div>
                </div>
            `;
        });

        // Show bugs
        Object.values(bugs).forEach(bug => {
            html += `
                <div class="status-item bug">
                    <h5>🐛 Bug: ${bug.testName}</h5>
                    <p><strong>Bug ID:</strong> ${bug.bugId} | <strong>Priority:</strong> ${bug.priority}</p>
                    <p><strong>Description:</strong> ${bug.description}</p>
                    <p><strong>User:</strong> ${bug.user} | <strong>Date:</strong> ${new Date(bug.timestamp).toLocaleString()}</p>
                    <div class="status-actions">
                        <button class="btn btn-danger" onclick="statusManager.removeBug('${bug.testName}')">Remove</button>
                    </div>
                </div>
            `;
        });

        if (!html) {
            html = '<p>No status overrides or bug assignments found.</p>';
        }

        listContainer.innerHTML = html;
    }

    updatePageDisplay() {
        const overrides = this.getStoredOverrides();
        const bugs = this.getStoredBugs();

        // Update test rows in the main report
        document.querySelectorAll('tr[data-name]').forEach(row => {
            const testName = row.dataset.name;
            const normalizedName = this.normalizeTestName(testName);

            // Check for overrides
            if (overrides[normalizedName]) {
                const override = overrides[normalizedName];
                this.applyOverrideToRow(row, override);
            }

            // Check for bugs
            if (bugs[normalizedName]) {
                const bug = bugs[normalizedName];
                this.applyBugToRow(row, bug);
            }
        });

        this.updateListTab();
    }

    applyOverrideToRow(row, override) {
        const statusCell = row.querySelector('.status-passed, .status-failed, .status-skipped');
        if (statusCell) {
            statusCell.innerHTML = `
                ${override.newStatus.toUpperCase()}
                <br><small style="color: #007bff;">OVERRIDDEN</small>
            `;
            statusCell.className = `status-${override.newStatus}`;
        }

        const messageCell = row.cells[4]; // Assuming message is the 5th column
        if (messageCell) {
            const overrideDiv = document.createElement('div');
            overrideDiv.style.cssText = 'color: #007bff; font-size: 11px; margin-bottom: 3px;';
            overrideDiv.innerHTML = `<strong>Override:</strong> ${override.reason}`;
            messageCell.insertBefore(overrideDiv, messageCell.firstChild);
        }
    }

    applyBugToRow(row, bug) {
        const statusCell = row.querySelector('.status-passed, .status-failed, .status-skipped');
        if (statusCell) {
            statusCell.innerHTML += `<br><small style="color: #ffc107;">${bug.bugId}</small>`;
        }

        const messageCell = row.cells[4]; // Assuming message is the 5th column
        if (messageCell) {
            const bugDiv = document.createElement('div');
            bugDiv.style.cssText = 'color: #ffc107; font-size: 11px; margin-bottom: 3px;';
            bugDiv.innerHTML = `<strong>${bug.bugId}:</strong> ${bug.description.substring(0, 50)}${bug.description.length > 50 ? '...' : ''}`;
            messageCell.insertBefore(bugDiv, messageCell.firstChild);
        }
    }

    removeOverride(testName) {
        const overrides = this.getStoredOverrides();
        const key = this.normalizeTestName(testName);
        delete overrides[key];
        localStorage.setItem('bdd_status_overrides', JSON.stringify(overrides));
        this.showMessage('Override removed successfully!', 'success');
        this.updatePageDisplay();
    }

    removeBug(testName) {
        const bugs = this.getStoredBugs();
        const key = this.normalizeTestName(testName);
        delete bugs[key];
        localStorage.setItem('bdd_bug_tracking', JSON.stringify(bugs));
        this.showMessage('Bug assignment removed successfully!', 'success');
        this.updatePageDisplay();
    }

    showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${type}-message`;
        messageDiv.textContent = message;

        const activeTab = document.querySelector('.tab-content.active');
        activeTab.insertBefore(messageDiv, activeTab.firstChild);

        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

// Global functions for UI interaction
function toggleStatusPanel() {
    const content = document.querySelector('.panel-content');
    const toggle = document.querySelector('.panel-toggle');
    
    content.classList.toggle('collapsed');
    toggle.textContent = content.classList.contains('collapsed') ? '+' : '−';
}

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Initialize when page loads
let statusManager;
document.addEventListener('DOMContentLoaded', function() {
    statusManager = new StatusManager();
});
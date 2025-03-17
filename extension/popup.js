document.addEventListener('DOMContentLoaded', function () {
    // Elements
    const loginScreen = document.getElementById('login-screen');
    const mainScreen = document.getElementById('main-screen');
    const apiKeyInput = document.getElementById('api-key');
    const saveApiKeyBtn = document.getElementById('save-api-key');
    const currentProfile = document.getElementById('current-profile');
    const profileName = document.getElementById('profile-name');
    const profileHeadline = document.getElementById('profile-headline');
    const tagsInput = document.getElementById('tags');
    const notesInput = document.getElementById('notes');
    const addToCrmBtn = document.getElementById('add-to-crm');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');
    const usernameSpan = document.getElementById('username');
    const logoutBtn = document.getElementById('logout');
    const noProfileMessage = document.getElementById('no-profile-message') || document.createElement('div');

    // Add no profile message if it doesn't exist
    if (!document.getElementById('no-profile-message')) {
        noProfileMessage.id = 'no-profile-message';
        noProfileMessage.className = 'alert alert-warning';
        noProfileMessage.innerHTML = '<p>No LinkedIn profile detected. Please navigate to a LinkedIn profile page to import a contact.</p>';

        // Insert before currentProfile element
        currentProfile.parentNode.insertBefore(noProfileMessage, currentProfile);
    }

    let apiKey = '';
    let currentProfileData = null;

    // Check if API key is already saved
    chrome.storage.sync.get(['apiKey', 'username'], function (result) {
        if (result.apiKey) {
            apiKey = result.apiKey;
            if (result.username) {
                usernameSpan.textContent = result.username;
            }

            validateApiKey(apiKey);
        } else {
            showLoginScreen();
        }
    });

    // Save API key
    saveApiKeyBtn.addEventListener('click', function () {
        apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            alert('Please enter a valid API key');
            return;
        }

        validateApiKey(apiKey);
    });

    // Validate API key against the server
    function validateApiKey(key) {
        // Show loading state
        saveApiKeyBtn.textContent = 'Validating...';
        saveApiKeyBtn.disabled = true;

        // Parse the API key (format: user_id_username)
        const keyParts = key.split('_');
        if (keyParts.length !== 2) {
            alert('Invalid API key format. It should be in the format: user_id_username');
            saveApiKeyBtn.textContent = 'Save API Key';
            saveApiKeyBtn.disabled = false;
            return;
        }

        // Get the CRM URL
        getCrmUrl().then(crmUrl => {
            console.log('Using CRM URL:', crmUrl);
            // Make a request to check if the key is valid
            fetch(`${crmUrl}/api/token_check`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${key}`
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Invalid API key (Status: ${response.status})`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Token check successful:', data);
                    // Save API key and username
                    chrome.storage.sync.set({
                        'apiKey': key,
                        'username': data.username
                    });

                    // Update UI
                    usernameSpan.textContent = data.username;

                    // Show main screen
                    showMainScreen();

                    // Check if we're on a LinkedIn profile page
                    checkCurrentTab();
                })
                .catch(error => {
                    console.error('API key validation error:', error);
                    alert('Error validating API key: ' + error.message);
                    saveApiKeyBtn.textContent = 'Save API Key';
                    saveApiKeyBtn.disabled = false;
                });
        });
    }

    // Logout function
    logoutBtn.addEventListener('click', function () {
        chrome.storage.sync.remove(['apiKey', 'username'], function () {
            showLoginScreen();
        });
    });

    // Add to CRM button
    addToCrmBtn.addEventListener('click', function () {
        if (!currentProfileData) {
            alert('No profile data available');
            return;
        }

        // Add tags and notes
        currentProfileData.tags = tagsInput.value;
        currentProfileData.notes = notesInput.value;

        // Disable button
        addToCrmBtn.textContent = 'Adding...';
        addToCrmBtn.disabled = true;

        // Hide previous messages
        successMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');

        // Get the CRM URL
        getCrmUrl().then(crmUrl => {
            console.log('Sending contact data to CRM:', currentProfileData);
            // Send data to CRM
            fetch(`${crmUrl}/api/contacts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify(currentProfileData)
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Contact saved successfully:', data);
                    // Show success message
                    successMessage.textContent = data.message || 'Contact added successfully!';
                    successMessage.classList.remove('hidden');

                    // Reset form
                    tagsInput.value = '';
                    notesInput.value = '';

                    // Re-enable button
                    addToCrmBtn.textContent = 'Add to CRM';
                    addToCrmBtn.disabled = false;
                })
                .catch(error => {
                    console.error('Error saving contact:', error);
                    // Show error message
                    errorMessage.textContent = 'Error adding contact: ' + error.message;
                    errorMessage.classList.remove('hidden');

                    // Re-enable button
                    addToCrmBtn.textContent = 'Add to CRM';
                    addToCrmBtn.disabled = false;
                });
        });
    });

    // Check current tab for LinkedIn profile
    function checkCurrentTab() {
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            const currentTab = tabs[0];
            console.log('Current tab:', currentTab.url);

            if (currentTab.url && currentTab.url.includes('linkedin.com/in/')) {
                console.log('LinkedIn profile detected, requesting profile data');

                // Extract profile data from the page
                chrome.tabs.sendMessage(currentTab.id, { action: 'getProfileData' }, function (response) {
                    console.log('Received response from content script:', response);

                    if (response && response.data) {
                        displayProfileData(response.data);
                        currentProfile.classList.remove('hidden');
                        noProfileMessage.classList.add('hidden');
                    } else {
                        console.error('No profile data received from content script');
                        currentProfile.classList.add('hidden');
                        noProfileMessage.classList.remove('hidden');
                        noProfileMessage.innerHTML = '<p>Could not extract profile data. Please try refreshing the page.</p>';
                    }
                });
            } else {
                console.log('Not on a LinkedIn profile page');
                currentProfile.classList.add('hidden');
                noProfileMessage.classList.remove('hidden');
            }
        });
    }

    // Display profile data
    function displayProfileData(data) {
        currentProfileData = data;
        console.log('Displaying profile data:', data);

        // Update UI
        profileName.textContent = `${data.first_name} ${data.last_name}`;

        let headline = '';
        if (data.position) headline += data.position;
        if (data.position && data.company) headline += ' at ';
        if (data.company) headline += data.company;

        profileHeadline.textContent = headline || data.headline || 'LinkedIn Member';
    }

    // Helper function to get CRM URL
    function getCrmUrl() {
        return new Promise((resolve) => {
            chrome.storage.sync.get('crmUrl', function (result) {
                // Use stored URL or default to localhost for development
                if (result.crmUrl) {
                    resolve(result.crmUrl);
                } else {
                    // Set default URL to match your Flask server
                    const defaultUrl = 'http://localhost:5001';
                    // Save this URL for future use
                    chrome.storage.sync.set({ 'crmUrl': defaultUrl });
                    resolve(defaultUrl);
                }
            });
        });
    }

    // Show login screen
    function showLoginScreen() {
        loginScreen.classList.remove('hidden');
        mainScreen.classList.add('hidden');

        // Reset login form
        apiKeyInput.value = '';
        saveApiKeyBtn.textContent = 'Save API Key';
        saveApiKeyBtn.disabled = false;
    }

    // Show main screen
    function showMainScreen() {
        loginScreen.classList.add('hidden');
        mainScreen.classList.remove('hidden');
    }
}); 
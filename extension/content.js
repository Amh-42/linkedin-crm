// Listen for messages from the popup
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.action === 'getProfileData') {
        console.log('Received request to extract profile data');
        const profileData = extractProfileData();
        console.log('Sending response with profile data:', profileData);
        sendResponse({ data: profileData });
    }
    return true;
});

// Add a test button to the page if we're on LinkedIn
if (window.location.href.includes('linkedin.com/in/')) {
    console.log('LinkedIn profile detected, adding test button');
    // Wait for page to fully load
    window.addEventListener('load', function () {
        setTimeout(function () {
            // Create a test button
            const testButton = document.createElement('button');
            testButton.textContent = 'Test CRM Extraction';
            testButton.style.position = 'fixed';
            testButton.style.top = '10px';
            testButton.style.right = '10px';
            testButton.style.zIndex = '9999';
            testButton.style.backgroundColor = '#0073b1';
            testButton.style.color = 'white';
            testButton.style.border = 'none';
            testButton.style.padding = '8px 16px';
            testButton.style.borderRadius = '4px';
            testButton.style.cursor = 'pointer';

            // Add click event to test extraction
            testButton.addEventListener('click', function () {
                const data = extractProfileData();
                console.log('Extracted data (test):', data);
                alert('Profile data extracted! Check the console for details.');
            });

            // Add to page
            document.body.appendChild(testButton);

            // Also log the DOM structure for debugging
            console.log('LinkedIn page structure for debugging:');
            console.log('h1 elements:', document.querySelectorAll('h1'));
            console.log('text-heading-xlarge elements:', document.querySelectorAll('[class*="text-heading-xlarge"]'));
        }, 2000); // Wait 2 seconds for the page to fully load
    });
}

// Extract profile data from LinkedIn page
function extractProfileData() {
    try {
        console.log('Extracting profile data from LinkedIn...');
        console.log('Current URL:', window.location.href);

        // Get LinkedIn URL and ID
        const linkedinUrl = window.location.href.split('?')[0];
        const linkedinId = linkedinUrl.split('/in/')[1];

        // Extract name - multiple possible selectors to handle different page layouts
        let firstName = '';
        let lastName = '';
        let fullName = '';

        // Log all potential name elements for debugging
        console.log('Potential name elements:');
        document.querySelectorAll('h1').forEach(el => console.log('h1:', el.textContent));
        document.querySelectorAll('[class*="text-heading-xlarge"]').forEach(el => console.log('xlarge:', el.textContent));

        // Modern LinkedIn profile layout - multiple possible selectors
        const nameElement = document.querySelector('h1[class*="text-heading-xlarge"]') ||
            document.querySelector('h1.text-heading-xlarge') ||
            document.querySelector('h1.inline.t-24') ||
            document.querySelector('.pv-top-card--list li.inline.t-24') ||
            // For very modern layouts, try these broader selectors
            document.querySelector('h1') ||
            document.querySelector('[class*="text-heading-xlarge"]');

        if (nameElement) {
            fullName = nameElement.textContent.trim();
            console.log('Found name:', fullName);
            const nameParts = fullName.split(' ');
            if (nameParts.length >= 2) {
                firstName = nameParts[0];
                lastName = nameParts.slice(1).join(' ');
            } else {
                firstName = fullName;
            }
        } else {
            console.warn('Could not find name element');
        }

        // Extract headline - log potential elements for debugging
        console.log('Potential headline elements:');
        document.querySelectorAll('[class*="text-body-medium"]').forEach(el => console.log('medium:', el.textContent));

        // Try multiple selectors for headline
        const headlineElement = document.querySelector('.pv-text-details__left-panel .text-body-medium') ||
            document.querySelector('[class*="text-body-medium"]') ||
            document.querySelector('.text-body-medium') ||
            document.querySelector('.pv-top-card .pv-top-card__headline') ||
            document.querySelector('.ph5 .mt2');

        const headline = headlineElement ? headlineElement.textContent.trim() : '';
        console.log('Found headline:', headline);

        // Extract company and position from headline or dedicated sections
        let company = '';
        let position = '';

        // Try to extract from headline
        if (headline.includes(' at ')) {
            const parts = headline.split(' at ');
            position = parts[0].trim();
            company = parts[1].trim();
            console.log('Extracted from headline - Position:', position, 'Company:', company);
        } else {
            // Log experience section elements for debugging
            console.log('Experience section elements:');
            document.querySelectorAll('[class*="experience-item"]').forEach(el => console.log('exp item:', el.textContent.substring(0, 50) + '...'));
            document.querySelectorAll('[class*="pvs-entity"]').forEach(el => console.log('pvs entity:', el.textContent.substring(0, 50) + '...'));

            // Try to extract from experience section with multiple selector patterns
            const experienceElements = document.querySelectorAll('[class*="experience-item"]') ||
                document.querySelectorAll('.pvs-entity') ||
                document.querySelectorAll('[class*="pvs-entity"]') ||
                document.querySelectorAll('.experience-section .pv-entity__position-group');

            if (experienceElements && experienceElements.length > 0) {
                console.log('Found', experienceElements.length, 'experience elements');
                // Get most recent position
                const latestExperience = experienceElements[0];

                // Try multiple selector patterns for position and company
                const positionElement = latestExperience.querySelector('[class*="t-bold"]') ||
                    latestExperience.querySelector('.t-bold span') ||
                    latestExperience.querySelector('[class*="hoverable-link-text"]') ||
                    latestExperience.querySelector('.pv-entity__summary-info h3');

                const companyElement = latestExperience.querySelector('[class*="t-normal"]') ||
                    latestExperience.querySelector('.t-normal span') ||
                    latestExperience.querySelector('[class*="pvs-entity__caption-wrapper"]') ||
                    latestExperience.querySelector('.pv-entity__secondary-title');

                if (positionElement) {
                    position = positionElement.textContent.trim();
                    console.log('Found position element:', position);
                }

                if (companyElement) {
                    company = companyElement.textContent.trim();
                    console.log('Found company element:', company);
                }
            }
        }

        // Extract profile image URL
        let profileImageUrl = '';
        const profileImage = document.querySelector('.pv-top-card__photo img') ||
            document.querySelector('.profile-photo-edit__preview') ||
            document.querySelector('.profile-picture img') ||
            document.querySelector('[class*="profile-photo"] img') ||
            document.querySelector('.pv-top-card .presence-entity__image');

        if (profileImage) {
            profileImageUrl = profileImage.src;
            console.log('Found profile image:', profileImageUrl);
        } else {
            console.warn('Could not find profile image');
        }

        // Return extracted data
        const profileData = {
            first_name: firstName,
            last_name: lastName,
            headline: headline,
            position: position,
            company: company,
            linkedin_url: linkedinUrl,
            linkedin_id: linkedinId,
            profile_image_url: profileImageUrl
        };

        console.log('Extracted profile data:', profileData);
        return profileData;
    } catch (error) {
        console.error('Error extracting profile data:', error);
        return null;
    }
} 
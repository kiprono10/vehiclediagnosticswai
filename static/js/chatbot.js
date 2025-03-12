// Auto Advisor - Chatbot Functionality
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const chatContainer = document.getElementById('chat-container');
    
    // Initial greeting message
    addBotMessage("Hello! I'm your Auto Advisor chatbot. I can help diagnose vehicle problems. Describe your car's issue, and I'll do my best to help.");
    
    // Handle chat form submission
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get user message
            const message = userInput.value.trim();
            if (!message) return;
            
            // Display user message
            addUserMessage(message);
            
            // Clear input field
            userInput.value = '';
            
            // Show loading indicator
            const loadingElement = document.createElement('div');
            loadingElement.className = 'chat-message bot-message';
            loadingElement.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            chatMessages.appendChild(loadingElement);
            
            // Scroll to bottom
            scrollToBottom();
            
            // Send message to server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'message': message
                })
            })
            .then(response => response.json())
            .then(data => {
                // Remove loading indicator
                chatMessages.removeChild(loadingElement);
                
                // Display response
                if (data.error) {
                    addBotMessage(`Sorry, there was an error: ${data.error}`);
                } else if (data.response) {
                    // Convert markdown formatting to HTML
                    addBotMessage(formatMarkdown(data.response));
                } else {
                    addBotMessage("I'm sorry, I couldn't process your request. Please try again.");
                }
            })
            .catch(error => {
                // Remove loading indicator
                chatMessages.removeChild(loadingElement);
                
                console.error('Error:', error);
                addBotMessage("I'm sorry, there was an error communicating with the server. Please try again later.");
            });
        });
    }
    
    // Add a user message to the chat
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message user-message';
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    // Add a bot message to the chat
    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message bot-message';
        messageElement.innerHTML = message;
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Simple markdown to HTML formatter
    function formatMarkdown(text) {
        // Bold text
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Line breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }
    
    // Example questions
    const exampleQuestions = [
        "My engine is making a knocking sound",
        "Car won't start and makes clicking noise",
        "Brakes are squeaking",
        "Check engine light is on",
        "Car is overheating",
        "Transmission is slipping"
    ];
    
    // Add example questions if the element exists
    const exampleSection = document.getElementById('example-questions');
    if (exampleSection) {
        const exampleList = document.createElement('div');
        exampleList.className = 'list-group';
        
        exampleQuestions.forEach(question => {
            const questionElement = document.createElement('button');
            questionElement.className = 'list-group-item list-group-item-action';
            questionElement.textContent = question;
            
            questionElement.addEventListener('click', function() {
                userInput.value = question;
                // Focus on input to encourage submission
                userInput.focus();
            });
            
            exampleList.appendChild(questionElement);
        });
        
        exampleSection.appendChild(exampleList);
    }
});

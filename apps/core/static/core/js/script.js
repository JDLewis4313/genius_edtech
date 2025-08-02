// GeNiUS EdTech Base JavaScript

// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Mentari Chat System
class MentariChat {
    constructor() {
        this.chatContainer = document.getElementById("chat-container");
        this.userInput = document.getElementById("user-input");
        this.statsElement = document.getElementById("conversation-stats");
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Bind methods to maintain context
        this.sendMessage = this.sendMessage.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.submitQuizAnswer = this.submitQuizAnswer.bind(this);
        this.triggerRandomReflection = this.triggerRandomReflection.bind(this);

        // Make methods globally available for onclick handlers
        window.sendMessage = this.sendMessage;
        window.submitQuizAnswer = this.submitQuizAnswer;
        window.triggerRandomReflection = this.triggerRandomReflection;
        window.handleKeyPress = this.handleKeyPress;
    }

    sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        this.addMessage("player", message);
        this.userInput.value = "";

        fetch("/ai/chat/api/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ 
                message: message, 
                context: "GeNiUS EdTech Chat" 
            })
        })
        .then(res => res.json())
        .then(data => {
            const responseText = typeof data.response === "string"
                ? data.response
                : data.response?.text || "Mentari is thinking...";

            this.addMessage("guide", responseText);

            if (data.card) {
                this.displayCard(data.card);
            }

            if (data.redirect_url) {
                this.displayQuizRedirect(data.redirect_url);
            }

            this.updateStats(data.conversation_stats);
        })
        .catch(error => {
            console.error("Mentari error:", error);
            this.addMessage("guide", "Mentari Mentor is momentarily gathering wisdom…");
        });
    }

    displayCard(card) {
        const cardDiv = document.createElement("div");
        cardDiv.className = "card mt-3 mb-3 shadow-sm";

        switch (card.type) {
            case "quiz_question":
                cardDiv.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">📝 Quiz Question</h5>
                        <div class="list-group list-group-flush mt-3">
                            ${card.choices.map(choice => `
                                <button class="list-group-item list-group-item-action py-3 text-start"
                                        onclick="submitQuizAnswer('${choice.letter}')">
                                    <strong>${choice.letter}.</strong> ${choice.text}
                                </button>
                            `).join('')}
                        </div>
                        <div class="mt-3 text-muted small">
                            <i class="fas fa-info-circle"></i> Click an option or type A, B, C, or D
                        </div>
                    </div>
                `;
                break;

            case "quiz_complete":
                const emoji = card.percentage >= 80 ? '🏆' : card.percentage >= 60 ? '😊' : '📚';
                cardDiv.innerHTML = `
                    <div class="card-body text-center">
                        <h5 class="card-title">Quiz Complete!</h5>
                        <div class="my-4">
                            <div class="display-1">${emoji}</div>
                            <h3 class="mt-3">${card.score}/${card.total}</h3>
                            <p class="text-muted">${card.percentage.toFixed(0)}%</p>
                        </div>
                        <button class="btn btn-primary" onclick="sendMessage('quiz on atoms')">
                            Try Another Quiz
                        </button>
                    </div>
                `;
                break;
        }

        this.chatContainer.appendChild(cardDiv);
        this.scrollToBottom();
    }

    displayQuizRedirect(redirectUrl) {
        const div = document.createElement("div");
        div.className = "alert alert-success mt-2";
        div.innerHTML = `
            <strong>📝 Quiz Ready!</strong><br>
            <a href="${redirectUrl}" class="btn btn-sm btn-success mt-2">👉 Start your quiz</a>
        `;
        this.chatContainer.appendChild(div);
        this.scrollToBottom();
    }

    submitQuizAnswer(answer) {
        this.userInput.value = `answer: ${answer}`;
        this.sendMessage();
    }

    triggerRandomReflection() {
        fetch("/mentari/random_appearance?character_name=Student&action=reflecting")
        .then(res => res.json())
        .then(data => {
            const div = document.createElement("div");
            div.className = "alert alert-warning mt-2 small";
            div.innerHTML = `<strong>Reflection:</strong><br>${data.appearance}`;
            this.chatContainer.appendChild(div);
            this.scrollToBottom();
        })
        .catch(error => {
            console.error("Reflection error:", error);
        });
    }

    addMessage(sender, text) {
        const div = document.createElement("div");
        div.className = `alert ${sender === "player" ? "alert-primary text-end" : "alert-secondary"}`;
        div.innerHTML = `<strong>${sender === "player" ? "You" : "Mentari"}:</strong> ${text}`;
        this.chatContainer.appendChild(div);
        this.scrollToBottom();
    }

    updateStats(stats) {
        if (this.statsElement && stats) {
            this.statsElement.textContent = 
                `Interactions: ${stats.total_interactions}, Growth: ${stats.growth_indicators}, Support: ${stats.support_needed}`;
        }
    }

    scrollToBottom() {
        this.chatContainer.scrollTo({ 
            top: this.chatContainer.scrollHeight, 
            behavior: 'smooth' 
        });
    }

    handleKeyPress(e) {
        if (e.key === "Enter") {
            this.sendMessage();
        }
    }
}

// Navbar Effects
class NavbarEffects {
    constructor() {
        this.navbar = document.querySelector('.navbar');
        this.initializeScrollEffect();
    }

    initializeScrollEffect() {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                this.navbar.style.background = 'rgba(10, 14, 39, 0.98)';
                this.navbar.style.boxShadow = '0 8px 32px rgba(0, 184, 148, 0.3)';
            } else {
                this.navbar.style.background = 'rgba(10, 14, 39, 0.95)';
                this.navbar.style.boxShadow = '0 8px 32px rgba(0, 184, 148, 0.2)';
            }
        });
    }
}

// Animation Utilities
class AnimationUtils {
    static addStaggeredFadeIn(elements, baseDelay = 100) {
        elements.forEach((element, index) => {
            element.style.animationDelay = `${index * baseDelay}ms`;
            element.classList.add('fade-in');
        });
    }

    static addHoverEffects() {
        // Add hover effects to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }
}

// Utility Functions for Global Use
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show border-glow bg-glass`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                alertDiv.classList.remove('show');
                setTimeout(() => alertDiv.remove(), 150);
            }
        }, 5000);
    }
}

function smoothScrollTo(target, offset = 90) {
    const element = document.querySelector(target);
    if (element) {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize main components
    const navbarEffects = new NavbarEffects();
    
    // Initialize Mentari chat if elements exist
    if (document.getElementById("chat-container")) {
        const mentariChat = new MentariChat();
    }
    
    // Initialize animations
    AnimationUtils.addHoverEffects();
    
    // Add staggered fade-in to elements with stagger classes
    const staggerElements = document.querySelectorAll('[class*="stagger-"]');
    if (staggerElements.length > 0) {
        AnimationUtils.addStaggeredFadeIn(Array.from(staggerElements));
    }
    
    // Initialize Bootstrap tooltips if any exist
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers if any exist
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    console.log('GeNiUS EdTech initialized successfully! 🚀');
});

// CSS for ripple effect (to be added via JavaScript)
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

// Export for module use if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        MentariChat,
        NavbarEffects,
        AnimationUtils,
        showNotification,
        smoothScrollTo,
        getCookie
    };
}
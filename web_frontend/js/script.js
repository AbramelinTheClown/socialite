// web_frontend/js/script.js

// --- Functions to control character visuals and animations ---

function setLuminaExpression(expression) {
    const lumina = document.getElementById('lumina');
    // Example: Add/remove a class based on expression
    lumina.classList.remove('happy', 'sad', 'neutral'); // Remove existing
    lumina.classList.add(expression); // Add the new one
    // CSS in lumina.css will define the look for .lumina.happy, .lumina.sad, etc.
    console.log("Lumina expression set to:", expression);
}

function setLuminaMouth(mouth_shape) {
    // Hide all mouth shapes
    document.getElementById('lumina-mouth-neutral').style.display = 'none';
    document.getElementById('lumina-mouth-mid').style.display = 'none';
    document.getElementById('lumina-mouth-wide').style.display = 'none';
    document.getElementById('lumina-blinks').style.display = 'none'; // Hide blinks when talking

    // Show the specified mouth shape
    if (mouth_shape === 'neutral') {
        document.getElementById('lumina-mouth-neutral').style.display = 'block';
    } else if (mouth_shape === 'mid') {
        document.getElementById('lumina-mouth-mid').style.display = 'block';
    } else if (mouth_shape === 'wide') {
        document.getElementById('lumina-mouth-wide').style.display = 'block';
    } else if (mouth_shape === 'blink') {
        document.getElementById('lumina-blinks').style.display = 'block';
         // Hide neutral mouth temporarily if needed during blink
         document.getElementById('lumina-mouth-neutral').style.display = 'none';
    }
     console.log("Lumina mouth set to:", mouth_shape);
}

function triggerPropAnimation(prop_id, animation_name) {
    const prop = document.getElementById(prop_id);
    if (prop) {
        prop.style.display = 'block'; // Make prop visible
        prop.classList.add(animation_name); // Add a class to trigger CSS animation
        // Add event listener to remove the class after animation ends if it's a one-time animation
         prop.addEventListener('animationend', () => {
             prop.classList.remove(animation_name);
             // Optionally hide prop again after animation if it's a temporary effect
             // prop.style.display = 'none';
         }, { once: true });
         console.log("Triggered animation", animation_name, "for prop", prop_id);
    }
}

function panCanvas(x, y, duration = 1) {
    const canvas = document.getElementById('giant-canvas');
    canvas.style.transition = `transform ${duration}s ease-in-out`;
    canvas.style.transform = `translate(${x}px, ${y}px)`;
     console.log("Panning canvas to:", x, y);
}

// --- Function to handle incoming commands from the orchestration script ---
// This function will be called by your Python script (via WebSockets or Playwright)

function handleOrchestratorCommand(command) {
    console.log("Received command from orchestrator:", command);

    if (command.type === 'set_expression') {
        setLuminaExpression(command.expression);
    } else if (command.type === 'set_mouth') {
        setLuminaMouth(command.shape);
    } else if (command.type === 'trigger_prop') {
        triggerPropAnimation(command.prop_id, command.animation);
    } else if (command.type === 'pan_to') {
         panCanvas(command.x, command.y, command.duration);
    } else if (command.type === 'speak_text') {
        // This command might be used to trigger lip sync based on text analysis
        // or prepare for audio playback
        console.log("Lumina is preparing to speak:", command.text);
        // You'll need more advanced logic here for lip sync
    }
    // Add handlers for other commands from your orchestrator
}


// --- Initial setup or testing ---
// You can add code here to set the initial state or test functions
// Example: Set initial expression and mouth shape
document.addEventListener('DOMContentLoaded', () => {
    setLuminaExpression('neutral');
    setLuminaMouth('neutral');

    // Example test commands (remove for production livestream)
    // setTimeout(() => handleOrchestratorCommand({ type: 'set_mouth', shape: 'wide' }), 1000);
    // setTimeout(() => handleOrchestratorCommand({ type: 'set_mouth', shape: 'neutral' }), 2000);
    // setTimeout(() => handleOrchestratorCommand({ type: 'set_mouth', shape: 'blink' }), 2500);
    // setTimeout(() => handleOrchestratorCommand({ type: 'set_mouth', shape: 'neutral' }), 3000);
    // setTimeout(() => handleOrchestratorCommand({ type: 'set_expression', expression: 'happy' }), 3500);
    // setTimeout(() => handleOrchestratorCommand({ type: 'pan_to', x: -500, y: -300, duration: 2 }), 4000);
});

// --- WebSocket setup (conceptual, if you choose this method) ---
// const websocket = new WebSocket("ws://localhost:8765"); // Replace with your WebSocket server address

// websocket.onmessage = (event) => {
//     const command = JSON.parse(event.data);
//     handleOrchestratorCommand(command);
// };

// websocket.onopen = () => {
//     console.log("WebSocket connected");
// };

// websocket.onerror = (error) => {
//     console.error("WebSocket error:", error);
// };

// websocket.onclose = (event) => {
//     console.log("WebSocket closed:", event);
// };

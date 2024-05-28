STYLES="""
    <style>
        .st-emotion-cache-18ni7ap {
            position: fixed;
            top: 0px;
            left: 0px;
            right: 0px;
            height: 2.885rem;
            background: rgb(255, 255, 255);
            outline: none;
            z-index: 999990;
            display: block;
        }
        .top-banner {
            background-color: #ff589e;
            color: white;
            padding: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .top-banner img {
            width: 45px;
            height: 40px;
            border-radius: 50%;
        }
        .status-indicator {
            display: flex;
            align-items: center;
        }
        .green-dot {
            width: 10px;
            height: 10px;
            background-color: green;
            border-radius: 50%;
            margin-right: 5px;
        }
        .chat-container {
            padding-left: 2px;
            padding-right: 2px;
            margin: 0 auto;
            min-width: 600px;
            max-width: 1700px;
            padding-top: 4rem; /* Adjust to prevent overlap with the fixed header */
        }
        .chat-bubble {
            padding: 3px;
            margin: 3px 0;
            border-radius: 10px;
            align-items: center;
            word-wrap: break-word;
            overflow-wrap: break-word;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        .user-bubble {
            align-self: flex-end;
            background-color: #dcf8c6;
            color: #000;
        }
        .assistant-bubble {
            align-self: flex-start;
            background-color: #f1f0f0;
            color: #000;
        }
        .chat-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .typing {
            font-style: italic;
            color: #888;
        }
        .chat-message {
            max-height: 170px;
            overflow-y: auto;
            white-space: pre-wrap; /* Preserve whitespace and wrap text */
            word-break: break-word; /* Break long words */
        }
        /* Override max-width limitation */
        @media (max-width: 50.5rem) {
            .st-emotion-cache-11kmii3 {
                max-width: 100vw; /* Removed calc(-4.5rem + 100vw) */
            }
        }
    </style>
"""

BANNER="""
    <div class="st-emotion-cache-18ni7ap top-banner">
        <div>
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQG1JzTwTj8b1jzq2zKlBbLEf3i-rOLwnmZqQ&usqp=CAU" alt="Bot Logo">
            <span>IVA Bot</span>
        </div>
        <div class="status-indicator">
            <div class="green-dot"></div>
            <div>Status: Online</div>
        </div>
    </div>
"""
TYPING ="""
            <div class="chat-bubble assistant-bubble typing">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQG1JzTwTj8b1jzq2zKlBbLEf3i-rOLwnmZqQ&usqp=CAU" class="chat-avatar">
                Typing...
            </div>
        """

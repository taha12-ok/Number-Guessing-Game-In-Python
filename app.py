import streamlit as st
import random
import time
from datetime import datetime
import pandas as pd
import altair as alt

# Page configuration
st.set_page_config(
    page_title="Number Master Pro 🎯",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #26A69A;
        margin-bottom: 1rem;
    }
    .success-text {
        color: #4CAF50;
        font-weight: bold;
    }
    .warning-text {
        color: #FF9800;
        font-weight: bold;
    }
    .danger-text {
        color: #F44336;
        font-weight: bold;
    }
    .info-text {
        color: #2196F3;
        font-weight: bold;
    }
    .stat-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .emoji-large {
        font-size: 2rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #9E9E9E;
        font-size: 0.8rem;
    }
    .help-box {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .tip-box {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .tab-content {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'target_number' not in st.session_state:
    st.session_state.target_number = None
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'max_attempts' not in st.session_state:
    st.session_state.max_attempts = float('inf')
if 'min_range' not in st.session_state:
    st.session_state.min_range = 1
if 'max_range' not in st.session_state:
    st.session_state.max_range = 100
if 'game_history' not in st.session_state:
    st.session_state.game_history = []
if 'high_score' not in st.session_state:
    st.session_state.high_score = float('inf')
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'hints_used' not in st.session_state:
    st.session_state.hints_used = 0
if 'hint_penalty' not in st.session_state:
    st.session_state.hint_penalty = 2
if 'game_won' not in st.session_state:
    st.session_state.game_won = False
if 'guesses' not in st.session_state:
    st.session_state.guesses = []
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Game"
if 'first_time_user' not in st.session_state:
    st.session_state.first_time_user = True

# Function to start a new game
def start_new_game():
    st.session_state.target_number = random.randint(
        st.session_state.min_range, st.session_state.max_range
    )
    st.session_state.attempts = 0
    st.session_state.game_active = True
    st.session_state.start_time = time.time()
    st.session_state.hints_used = 0
    st.session_state.game_won = False
    st.session_state.guesses = []
    st.session_state.current_tab = "Game"

# Function to reset the game
def reset_game():
    st.session_state.game_active = False
    st.session_state.target_number = None
    st.session_state.attempts = 0
    st.session_state.start_time = None
    st.session_state.hints_used = 0
    st.session_state.game_won = False
    st.session_state.guesses = []

# Function to calculate score
def calculate_score(attempts, max_range, min_range, time_taken, hints_used, hint_penalty):
    range_factor = (max_range - min_range) / 100
    base_score = 1000 * range_factor
    attempt_penalty = attempts * 50
    time_penalty = time_taken * 5
    hint_penalty_total = hints_used * hint_penalty * 25
    
    score = max(0, base_score - attempt_penalty - time_penalty - hint_penalty_total)
    return int(score)

# Function to provide a hint
def get_hint():
    if st.session_state.hints_used < 3:
        st.session_state.hints_used += 1
        target = st.session_state.target_number
        if st.session_state.hints_used == 1:
            # First hint: Even or Odd
            return f"Hint #{st.session_state.hints_used}: The number is {'even 🔢' if target % 2 == 0 else 'odd 🔢'}."
        elif st.session_state.hints_used == 2:
            # Second hint: Divisibility
            divisors = [3, 5, 7]
            for div in divisors:
                if target % div == 0:
                    return f"Hint #{st.session_state.hints_used}: The number is divisible by {div} ✖️."
            return f"Hint #{st.session_state.hints_used}: The number is not divisible by 3, 5, or 7 ❌."
        elif st.session_state.hints_used == 3:
            # Third hint: Closer range
            range_size = (st.session_state.max_range - st.session_state.min_range) // 4
            lower = target - random.randint(1, range_size)
            upper = target + random.randint(1, range_size)
            lower = max(lower, st.session_state.min_range)
            upper = min(upper, st.session_state.max_range)
            return f"Hint #{st.session_state.hints_used}: The number is between {lower} and {upper} 🔍."
    else:
        return "You've used all your hints! 🚫"

# Function to change tab
def change_tab(tab_name):
    st.session_state.current_tab = tab_name

# Main app header
st.markdown("<h1 class='main-header'>Number Master Pro 🎮</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>The ultimate number guessing challenge!</p>", unsafe_allow_html=True)

# Sidebar for game settings
with st.sidebar:
    st.markdown("<h2 class='sub-header'>Game Settings ⚙️</h2>", unsafe_allow_html=True)
    
    # Number range settings
    st.markdown("### Set Your Number Range 📏")
    min_range = st.number_input("Minimum Value", value=1, min_value=1, max_value=9999)
    max_range = st.number_input("Maximum Value", value=100, min_value=2, max_value=10000)
    
    if min_range >= max_range:
        st.error("Minimum value must be less than maximum value!")
    else:
        st.session_state.min_range = min_range
        st.session_state.max_range = max_range
    
    # Difficulty settings
    st.markdown("### Select Difficulty 🔥")
    difficulty = st.select_slider(
        "Difficulty Level",
        options=["Easy 😊", "Medium 😐", "Hard 😓", "Expert 🥵", "Unlimited ♾️"]
    )
    
    # Set max attempts based on difficulty
    range_size = max_range - min_range + 1
    if difficulty == "Easy 😊":
        st.session_state.max_attempts = int(range_size * 0.3)
        st.session_state.hint_penalty = 1
    elif difficulty == "Medium 😐":
        st.session_state.max_attempts = int(range_size * 0.2)
        st.session_state.hint_penalty = 2
    elif difficulty == "Hard 😓":
        st.session_state.max_attempts = int(range_size * 0.1)
        st.session_state.hint_penalty = 3
    elif difficulty == "Expert 🥵":
        st.session_state.max_attempts = int(range_size * 0.05)
        st.session_state.hint_penalty = 4
    else:  # Unlimited
        st.session_state.max_attempts = float('inf')
        st.session_state.hint_penalty = 2
    
    if difficulty != "Unlimited ♾️":
        st.info(f"You'll have {st.session_state.max_attempts} attempts to guess the number.")
    
    # Start game button
    if st.button("Start New Game 🎮", use_container_width=True):
        start_new_game()
    
    # Reset game button
    if st.button("Reset Game 🔄", use_container_width=True):
        reset_game()
    
    # Navigation buttons
    st.markdown("### Navigation 🧭")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Game 🎮", use_container_width=True):
            change_tab("Game")
    with col2:
        if st.button("History 📊", use_container_width=True):
            change_tab("History")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("How to Play ❓", use_container_width=True):
            change_tab("How to Play")
    with col2:
        if st.button("Stats 📈", use_container_width=True):
            change_tab("Stats")
    
    # High score
    if st.session_state.high_score != float('inf'):
        st.markdown("### High Score 🏆")
        st.markdown(f"""
        <div class='stat-container success-text'>
            <span class='emoji-large'>🏆</span> {st.session_state.high_score} points
        </div>
        """, unsafe_allow_html=True)

# Main content area with tabs
if st.session_state.current_tab == "Game":
    # Game tab content
    if not st.session_state.game_active:
        st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <span style='font-size: 4rem;'>🎲 🎯 🎮</span>
            <h2>Welcome to Number Master Pro!</h2>
            <p>Set your desired range and difficulty in the sidebar, then click "Start New Game" to begin.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # First-time user guidance
        if st.session_state.first_time_user:
            st.markdown("""
            <div class='help-box'>
                <h3>👋 New to Number Master Pro?</h3>
                <p>Click the "How to Play" button in the sidebar to learn the rules and get tips!</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Got it! 👍"):
                st.session_state.first_time_user = False
    else:
        # Game is active
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"<h2 class='sub-header'>Guess the Number! 🤔</h2>", unsafe_allow_html=True)
            st.markdown(f"I'm thinking of a number between **{st.session_state.min_range}** and **{st.session_state.max_range}**.")
            
            # User input for guess
            guess = st.number_input(
                "Enter your guess:",
                min_value=st.session_state.min_range,
                max_value=st.session_state.max_range,
                step=1,
                key="guess_input"
            )
            
            # Submit guess button
            if st.button("Submit Guess 🚀", use_container_width=True):
                if not st.session_state.game_won:
                    st.session_state.attempts += 1
                    
                    # Record the guess
                    st.session_state.guesses.append({
                        'attempt': st.session_state.attempts,
                        'guess': guess,
                        'target': st.session_state.target_number,
                        'result': 'correct' if guess == st.session_state.target_number else 'too low' if guess < st.session_state.target_number else 'too high'
                    })
                    
                    if guess == st.session_state.target_number:
                        # Player wins
                        st.session_state.game_won = True
                        time_taken = time.time() - st.session_state.start_time
                        score = calculate_score(
                            st.session_state.attempts,
                            st.session_state.max_range,
                            st.session_state.min_range,
                            time_taken,
                            st.session_state.hints_used,
                            st.session_state.hint_penalty
                        )
                        
                        # Update high score
                        if score > st.session_state.high_score or st.session_state.high_score == float('inf'):
                            st.session_state.high_score = score
                        
                        # Add to game history
                        st.session_state.game_history.append({
                            'min_range': st.session_state.min_range,
                            'max_range': st.session_state.max_range,
                            'attempts': st.session_state.attempts,
                            'score': score,
                            'time_taken': time_taken,
                            'difficulty': difficulty,
                            'target': st.session_state.target_number,
                            'hints_used': st.session_state.hints_used,
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'guesses': st.session_state.guesses.copy()
                        })
                        
                        st.balloons()
                        st.success(f"🎉 CONGRATULATIONS! 🎉 You guessed the number in {st.session_state.attempts} attempts!")
                        st.markdown(f"""
                        <div class='stat-container success-text'>
                            <h3>Game Summary:</h3>
                            <p>🎯 Target Number: {st.session_state.target_number}</p>
                            <p>🔢 Attempts: {st.session_state.attempts}</p>
                            <p>⏱️ Time: {time_taken:.2f} seconds</p>
                            <p>💡 Hints Used: {st.session_state.hints_used}</p>
                            <p>🏆 Score: {score} points</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif guess < st.session_state.target_number:
                        st.markdown("<p class='info-text'>📈 Too low! Try a higher number.</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p class='info-text'>📉 Too high! Try a lower number.</p>", unsafe_allow_html=True)
                    
                    # Check if max attempts reached
                    if st.session_state.attempts >= st.session_state.max_attempts and not st.session_state.game_won:
                        st.error(f"Game Over! 😢 You've used all {st.session_state.max_attempts} attempts.")
                        st.markdown(f"<p class='danger-text'>The number was {st.session_state.target_number}.</p>", unsafe_allow_html=True)
                        
                        # Add to game history
                        time_taken = time.time() - st.session_state.start_time
                        st.session_state.game_history.append({
                            'min_range': st.session_state.min_range,
                            'max_range': st.session_state.max_range,
                            'attempts': st.session_state.attempts,
                            'score': 0,
                            'time_taken': time_taken,
                            'difficulty': difficulty,
                            'target': st.session_state.target_number,
                            'hints_used': st.session_state.hints_used,
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'guesses': st.session_state.guesses.copy()
                        })
            
            # Hint button
            if st.button("Get a Hint 💡", use_container_width=True) and not st.session_state.game_won:
                hint = get_hint()
                st.markdown(f"<p class='warning-text'>{hint}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='danger-text'>Note: Using hints reduces your final score!</p>", unsafe_allow_html=True)
            
            # Show guess history for current game
            if st.session_state.guesses:
                st.markdown("<h3>Your Guesses This Game:</h3>", unsafe_allow_html=True)
                for g in st.session_state.guesses:
                    if g['result'] == 'correct':
                        emoji = "✅"
                        color = "success-text"
                    elif g['result'] == 'too low':
                        emoji = "⬆️"
                        color = "info-text"
                    else:  # too high
                        emoji = "⬇️"
                        color = "info-text"
                    
                    st.markdown(f"""
                    <div class='stat-container'>
                        <span class='{color}'>Attempt #{g['attempt']}: {g['guess']} {emoji}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<h3 class='sub-header'>Game Stats 📊</h3>", unsafe_allow_html=True)
            
            # Game statistics
            st.markdown(f"""
            <div class='stat-container'>
                <p><strong>🔢 Attempts:</strong> {st.session_state.attempts}</p>
                <p><strong>🎚️ Range:</strong> {st.session_state.min_range} - {st.session_state.max_range}</p>
                <p><strong>💡 Hints Used:</strong> {st.session_state.hints_used}/3</p>
                <p><strong>⏱️ Time:</strong> {time.time() - st.session_state.start_time:.1f}s</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Attempts visualization
            if st.session_state.max_attempts != float('inf'):
                attempts_left = st.session_state.max_attempts - st.session_state.attempts
                st.markdown("<p><strong>Attempts Remaining:</strong></p>", unsafe_allow_html=True)
                
                # Create a visual progress bar
                progress_percentage = st.session_state.attempts / st.session_state.max_attempts
                st.progress(progress_percentage)
                
                # Color-coded attempts remaining
                if attempts_left > st.session_state.max_attempts * 0.6:
                    st.markdown(f"<p class='success-text'>{attempts_left} attempts left</p>", unsafe_allow_html=True)
                elif attempts_left > st.session_state.max_attempts * 0.3:
                    st.markdown(f"<p class='warning-text'>{attempts_left} attempts left</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p class='danger-text'>{attempts_left} attempts left</p>", unsafe_allow_html=True)
            
            # Quick tips
            st.markdown("""
            <div class='tip-box'>
                <h4>💡 Quick Tips</h4>
                <ul>
                    <li>Try guessing the middle of the range first</li>
                    <li>Use hints strategically when stuck</li>
                    <li>Remember your previous guesses</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.current_tab == "History":
    # History tab content
    st.markdown("<h2 class='sub-header'>Game History 📜</h2>", unsafe_allow_html=True)
    
    if not st.session_state.game_history:
        st.info("You haven't played any games yet. Start a new game to build your history!")
    else:
        # Convert game history to DataFrame for easier manipulation
        history_df = pd.DataFrame(st.session_state.game_history)
        
        # Add some filters
        col1, col2 = st.columns(2)
        with col1:
            if 'difficulty' in history_df.columns:
                difficulties = ['All'] + list(history_df['difficulty'].unique())
                selected_difficulty = st.selectbox("Filter by Difficulty", difficulties)
        with col2:
            sort_by = st.selectbox("Sort by", ["Most Recent", "Highest Score", "Fewest Attempts"])
        
        # Apply filters
        filtered_df = history_df.copy()
        if 'difficulty' in filtered_df.columns and selected_difficulty != 'All':
            filtered_df = filtered_df[filtered_df['difficulty'] == selected_difficulty]
        
        # Apply sorting
        if sort_by == "Highest Score":
            filtered_df = filtered_df.sort_values(by='score', ascending=False)
        elif sort_by == "Fewest Attempts":
            filtered_df = filtered_df.sort_values(by='attempts')
        else:  # Most Recent
            filtered_df = filtered_df.iloc[::-1].reset_index(drop=True)
        
        # Display history
        for i, game in enumerate(filtered_df.to_dict('records')):
            with st.expander(f"Game {i+1}: {game['date']} - Score: {game['score']}"):
                st.markdown(f"""
                <div class='stat-container'>
                    <h4>Game Details:</h4>
                    <p><strong>Date:</strong> {game['date']}</p>
                    <p><strong>Range:</strong> {game['min_range']} - {game['max_range']}</p>
                    <p><strong>Target Number:</strong> {game['target']}</p>
                    <p><strong>Attempts:</strong> {game['attempts']}</p>
                    <p><strong>Score:</strong> {game['score']}</p>
                    <p><strong>Time Taken:</strong> {game.get('time_taken', 'N/A'):.2f} seconds</p>
                    <p><strong>Hints Used:</strong> {game.get('hints_used', 'N/A')}</p>
                    <p><strong>Difficulty:</strong> {game.get('difficulty', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show guesses for this game if available
                if 'guesses' in game and game['guesses']:
                    st.markdown("<h4>Guess History:</h4>", unsafe_allow_html=True)
                    guesses_df = pd.DataFrame(game['guesses'])
                    
                    # Create a chart of guesses
                    if len(guesses_df) > 1:
                        chart = alt.Chart(guesses_df).mark_line(point=True).encode(
                            x=alt.X('attempt:Q', title='Attempt Number'),
                            y=alt.Y('guess:Q', title='Guess Value', scale=alt.Scale(domain=[game['min_range'], game['max_range']])),
                            tooltip=['attempt', 'guess', 'result']
                        ).properties(
                            title='Guess Progression',
                            width=500,
                            height=300
                        )
                        
                        # Add a horizontal line for the target
                        target_line = alt.Chart(pd.DataFrame({'target': [game['target']]})).mark_rule(color='red').encode(
                            y='target:Q'
                        )
                        
                        st.altair_chart(chart + target_line)
                    
                    # Show guess list
                    for g in game['guesses']:
                        if g['result'] == 'correct':
                            emoji = "✅"
                        elif g['result'] == 'too low':
                            emoji = "⬆️"
                        else:  # too high
                            emoji = "⬇️"
                        
                        st.markdown(f"Attempt #{g['attempt']}: {g['guess']} {emoji}")
        
        # Summary statistics
        st.markdown("<h3>Your Gaming Statistics</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Games", len(history_df))
        with col2:
            win_rate = (history_df['score'] > 0).mean() * 100
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col3:
            avg_attempts = history_df['attempts'].mean()
            st.metric("Avg. Attempts", f"{avg_attempts:.1f}")
        
        # Visualizations
        if len(history_df) >= 3:
            st.markdown("<h3>Performance Over Time</h3>", unsafe_allow_html=True)
            
            # Add game number for tracking
            history_df['game_number'] = range(1, len(history_df) + 1)
            
            # Score over time
            score_chart = alt.Chart(history_df).mark_line(point=True).encode(
                x=alt.X('game_number:Q', title='Game Number'),
                y=alt.Y('score:Q', title='Score'),
                tooltip=['date', 'score', 'attempts']
            ).properties(
                title='Score Progression',
                width=700,
                height=300
            )
            
            st.altair_chart(score_chart)

elif st.session_state.current_tab == "How to Play":
    # How to Play tab content
    st.markdown("<h2 class='sub-header'>How to Play Number Master Pro 📖</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='help-box'>
        <h3>🎮 Game Objective</h3>
        <p>Number Master Pro is a number guessing game where you try to guess a randomly generated number within a specified range. The goal is to find the number in as few attempts as possible!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3>📋 Step-by-Step Guide</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <ol>
        <li><strong>Setup the Game:</strong>
            <ul>
                <li>Use the sidebar to set your desired number range (minimum and maximum values)</li>
                <li>Choose a difficulty level that determines how many attempts you'll have</li>
                <li>Click "Start New Game" to begin playing</li>
            </ul>
        </li>
        <li><strong>Make Your Guess:</strong>
            <ul>
                <li>Enter a number within the specified range</li>
                <li>Click "Submit Guess" to check if your guess is correct</li>
                <li>You'll receive feedback telling you if your guess is too high or too low</li>
            </ul>
        </li>
        <li><strong>Use Hints Strategically:</strong>
            <ul>
                <li>If you're stuck, you can use up to 3 hints per game</li>
                <li>Each hint provides different information about the target number</li>
                <li>Be careful! Using hints reduces your final score</li>
            </ul>
        </li>
        <li><strong>Win the Game:</strong>
            <ul>
                <li>Guess the correct number before running out of attempts</li>
                <li>Your score is calculated based on the number of attempts, time taken, and hints used</li>
                <li>Try to beat your high score!</li>
            </ul>
        </li>
    </ol>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3>💡 Pro Tips</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='tip-box'>
            <h4>Strategy Tips</h4>
            <ul>
                <li><strong>Binary Search:</strong> Start with the middle of the range, then eliminate half the possibilities with each guess</li>
                <li><strong>Pattern Recognition:</strong> Pay attention to the feedback patterns to narrow down possibilities</li>
                <li><strong>Time Management:</strong> Don't rush, but remember that taking too long reduces your score</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='tip-box'>
            <h4>Score Maximization</h4>
            <ul>
                <li><strong>Minimize Attempts:</strong> Each additional attempt reduces your score</li>
                <li><strong>Use Hints Sparingly:</strong> Hints are helpful but each one reduces your final score</li>
                <li><strong>Play Faster:</strong> Quicker games earn higher scores, so try to be efficient</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3>🧭 Navigation Guide</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='help-box'>
        <p>Number Master Pro has several sections you can navigate to using the buttons in the sidebar:</p>
        <ul>
            <li><strong>Game:</strong> The main game screen where you make your guesses</li>
            <li><strong>History:</strong> View detailed records of all your past games, including guess patterns and statistics</li>
            <li><strong>Stats:</strong> See your overall performance metrics and achievements</li>
            <li><strong>How to Play:</strong> This guide with rules and tips</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3>🏆 Scoring System</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    Your score is calculated based on several factors:
    
    - **Base Score:** Determined by the range size (larger ranges = higher potential scores)
    - **Attempt Penalty:** Each attempt reduces your score
    - **Time Penalty:** Taking longer reduces your score
    - **Hint Penalty:** Each hint used reduces your score
    
    The formula is:"
    "Score = (Base Score) - (Attempt Penalty) - (Time Penalty) - (Hint Penalty)""
    
Different difficulty levels have different hint penalties and maximum attempts.
""")

# Ready to play button
if st.button("I'm Ready to Play! 🚀", use_container_width=True):
    change_tab("Game")

elif st.session_state.current_tab == "Stats":
# Stats tab content

  st.markdown("<h2 class='sub-header'>Your Gaming Statistics 📈</h2>", unsafe_allow_html=True)

if not st.session_state.game_history:
    st.info("You haven't played any games yet. Start playing to see your statistics!")
else:
    # Convert game history to DataFrame
    history_df = pd.DataFrame(st.session_state.game_history)
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Games", len(history_df))
    with col2:
        wins = (history_df['score'] > 0).sum()
        st.metric("Games Won", wins)
    with col3:
        win_rate = (wins / len(history_df)) * 100
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with col4:
        avg_score = history_df['score'].mean()
        st.metric("Avg. Score", f"{avg_score:.1f}")
    
    # More detailed stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>Attempt Statistics</h3>", unsafe_allow_html=True)
        avg_attempts = history_df['attempts'].mean()
        min_attempts = history_df['attempts'].min()
        max_attempts = history_df['attempts'].max()
        
        st.markdown(f"""
        <div class='stat-container'>
            <p><strong>Average Attempts:</strong> {avg_attempts:.1f}</p>
            <p><strong>Best Game:</strong> {min_attempts} attempts</p>
            <p><strong>Most Challenging Game:</strong> {max_attempts} attempts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h3>Score Statistics</h3>", unsafe_allow_html=True)
        high_score = history_df['score'].max()
        recent_avg = history_df.iloc[-5:]['score'].mean() if len(history_df) >= 5 else history_df['score'].mean()
        
        st.markdown(f"""
        <div class='stat-container'>
            <p><strong>High Score:</strong> {high_score}</p>
            <p><strong>Recent Average (last 5 games):</strong> {recent_avg:.1f}</p>
            <p><strong>Total Points Earned:</strong> {history_df['score'].sum()}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Visualizations
    if len(history_df) >= 3:
        # Add game number for tracking
        history_df['game_number'] = range(1, len(history_df) + 1)
        
        # Attempts distribution
        st.markdown("<h3>Attempts Distribution</h3>", unsafe_allow_html=True)
        attempts_chart = alt.Chart(history_df).mark_bar().encode(
            x=alt.X('attempts:Q', bin=True, title='Number of Attempts'),
            y=alt.Y('count()', title='Frequency')
        ).properties(
            title='Distribution of Attempts per Game',
            width=700,
            height=300
        )
        
        st.altair_chart(attempts_chart)
        
        # Performance by difficulty
        if 'difficulty' in history_df.columns:
            st.markdown("<h3>Performance by Difficulty</h3>", unsafe_allow_html=True)
            diff_chart = alt.Chart(history_df).mark_boxplot().encode(
                x=alt.X('difficulty:N', title='Difficulty Level'),
                y=alt.Y('score:Q', title='Score')
            ).properties(
                title='Score Distribution by Difficulty',
                width=700,
                height=300
            )
            
            st.altair_chart(diff_chart)
        
        # Learning curve
        st.markdown("<h3>Your Learning Curve</h3>", unsafe_allow_html=True)
        
        # Calculate moving average
        window_size = min(5, len(history_df))
        history_df['moving_avg_attempts'] = history_df['attempts'].rolling(window=window_size).mean()
        
        learning_chart = alt.Chart(history_df).mark_line(point=True).encode(
            x=alt.X('game_number:Q', title='Game Number'),
            y=alt.Y('moving_avg_attempts:Q', title=f'{window_size}-Game Moving Average of Attempts')
        ).properties(
            title='Learning Curve (Lower is Better)',
            width=700,
            height=300
        )
        
        st.altair_chart(learning_chart)
        
        # Achievement section
        st.markdown("<h3>🏆 Achievements</h3>", unsafe_allow_html=True)
        
        achievements = []
        
        # Check for achievements
        if len(history_df) >= 10:
            achievements.append("🎮 Dedicated Player: Played 10+ games")
        
        if wins >= 5:
            achievements.append("🏅 Winner: Won 5+ games")
        
        if win_rate >= 70:
            achievements.append("🌟 Master Guesser: 70%+ win rate")
        
        if min_attempts <= 3:
            achievements.append("🔍 Sharp Eye: Guessed correctly in 3 or fewer attempts")
        
        if high_score >= 500:
            achievements.append("💯 High Scorer: Scored 500+ points in a single game")
        
        if 'hints_used' in history_df.columns and (history_df['hints_used'] == 0).any():
            achievements.append("🧠 Pure Skill: Won a game without using hints")
        
        if not achievements:
            achievements.append("Keep playing to unlock achievements!")
        
        for achievement in achievements:
            st.markdown(f"<div class='stat-container success-text'>{achievement}</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
<p>Number Master Pro v1.0 | Created with ❤️ using Streamlit</p>
<p>© 2023 Number Master Games</p>
</div>
""", unsafe_allow_html=True)
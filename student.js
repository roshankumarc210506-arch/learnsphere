// student.js - Enhanced with new features
let stuChart = null;
let summaryChart = null;
let quizTimer = null;
let finalTimer = null;
let eventModal; // for Bootstrap modal instance
let calendarDate = new Date();

// IMPORTANT: Replace "" with your own Google AI Gemini API key for the AI Tutor to work.
const GEMINI_API_KEY = "";
let chatHistory = [];

let notifications = [
    {id: 1, title: 'Welcome to LearnSphere! 🎉', message: 'Explore your dashboard and start your learning journey.', timestamp: new Date(Date.now() - 86400000), read: false},
    {id: 2, title: 'New Achievement Available', message: 'Complete a quiz to unlock the "Quiz Whiz" badge!', timestamp: new Date(Date.now() - 3600000), read: false},
    {id: 3, title: 'Study Reminder', message: 'Don\'t forget to review your weak topics today.', timestamp: new Date(Date.now() - 7200000), read: false}
];

// Mock Data
const ACHIEVEMENTS = {
    'first_step': { name: 'First Step', description: 'Complete your first module.', icon: 'fa-shoe-prints' },
    'quiz_whiz': { name: 'Quiz Whiz', description: 'Score 100% on a quiz.', icon: 'fa-star' },
    'streak_starter': { name: 'Streak Starter', description: 'Maintain a 3-day streak.', icon: 'fa-fire' },
    'perfectionist': { name: 'Perfectionist', description: 'Score 100% on final test.', icon: 'fa-crown' },
    'speedster': { name: 'Speedster', description: 'Complete quiz in under 5 minutes.', icon: 'fa-bolt' }
};

const LEADERBOARD_DATA = [
    { name: 'Chaitanya', score: 92, completed: 5 },
    { name: 'Rahul', score: 88, completed: 4 },
    { name: 'Priya', score: 85, completed: 4 }
];

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const response = await fetch('http://localhost:5000/api/auth/status', {
      credentials: 'include'
    });
    const authData = await response.json();
    if (!authData.authenticated || authData.role !== 'student') {
      alert('Not logged in as student. Redirecting to login.');
      location.href = 'login.html';
      return;
    }

    const userResponse = await fetch('http://localhost:5000/api/student/info', {
      credentials: 'include'
    });
    const me = await userResponse.json();
  } catch (error) {
    console.error('Failed to authenticate:', error);
    alert('Failed to authenticate. Please try logging in again.');
    location.href = 'login.html';
    return;
  }
  if (!me) {
    me = {
        username: user.username,
        id:'id_'+Math.random().toString(36).slice(2,8),
        name:user.username,
        weak_topics:['Algebra'],
        quiz_scores:{},
        completed_modules:[],
        final_test_score:null,
        streak: 1,
        achievements: [],
        last_active: null,
        study_time: 0,
        notes: {},
        bookmarks: [],
        study_plan: [],
        lastLoginDate: null
    };
    students.push(me);
    localStorage.setItem('learnsphere_students', JSON.stringify(students));
  }

  // Initialize new properties if missing
  if (!me.study_time) me.study_time = 0;
  if (!me.notes) me.notes = {};
  if (!me.bookmarks) me.bookmarks = [];
  if (!me.study_plan) me.study_plan = [];
  if (!me.lastLoginDate) me.lastLoginDate = null;
  
  eventModal = new bootstrap.Modal(document.getElementById('eventModal'));

  // THEME
  const toggleButtons = document.querySelectorAll('#toggle-theme');
  function updateTheme(isDark) {
    document.body.classList.toggle('dark', isDark);
    toggleButtons.forEach(btn => btn.innerText = isDark ? 'Light' : 'Dark');
  }
  const savedTheme = localStorage.getItem('learnsphere_theme');
  updateTheme(savedTheme === 'dark');
  toggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const newIsDark = !document.body.classList.contains('dark');
      updateTheme(newIsDark);
      localStorage.setItem('learnsphere_theme', newIsDark ? 'dark' : 'light');
    });
  });

  document.getElementById('stu-name').innerText = `Hello, ${me.name}`;
  document.getElementById('btn-logout').addEventListener('click', () => {
    localStorage.removeItem('learnsphere_user');
    location.href = 'index.html';
  });

  // EVENT LISTENERS
  document.getElementById('quiz-form').addEventListener('submit', handleQuizSubmit);
  document.getElementById('final-form').addEventListener('submit', handleFinalTestSubmit);
  document.getElementById('chat-send-btn').addEventListener('click', sendMessage);
  document.getElementById('chat-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
  });
  document.getElementById('modules-list').addEventListener('click', handleModuleClick);
  
  document.getElementById('start-study-timer')?.addEventListener('click', startStudyTimer);
  document.getElementById('stop-study-timer')?.addEventListener('click', stopStudyTimer);
  document.getElementById('export-progress')?.addEventListener('click', exportProgress);
  
  document.getElementById('save-note-btn')?.addEventListener('click', saveNote);

  document.getElementById('btn-notifications')?.addEventListener('click', toggleNotifications);
  document.getElementById('btn-close-notifications')?.addEventListener('click', toggleNotifications);

  document.getElementById('calendar-prev')?.addEventListener('click', () => {
      calendarDate.setMonth(calendarDate.getMonth() - 1);
      renderCalendar();
  });
  document.getElementById('calendar-next')?.addEventListener('click', () => {
      calendarDate.setMonth(calendarDate.getMonth() + 1);
      renderCalendar();
  });
  document.getElementById('save-event-btn')?.addEventListener('click', saveStudyEvent);
  
  document.getElementById('event-list').addEventListener('click', handleDeleteEvent);
  document.getElementById('notes-content').addEventListener('click', handleDeleteNote);

  document.getElementById('start-final-test-btn').addEventListener('click', startFinalTest);


  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  updateOnlineStatus();

  // Navigation
  const navButtons = document.querySelectorAll('.nav-btn');
  function showScreen(name){
    navButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.screen === name));
    ['dashboard','modules','quiz','final','summary', 'leaderboard', 'ai_tutor', 'progress', 'notes', 'study-plans'].forEach(s => {
        const screen = document.getElementById('screen-' + s);
        if (screen) screen.classList.add('hidden');
    });
    document.getElementById('screen-' + name)?.classList.remove('hidden');
    
    if (name === 'progress') renderProgressScreen();
    if (name === 'notes') renderNotesScreen();
    if (name === 'study-plans') {
        renderCalendar();
        requestNotificationPermission();
    }
    if (name === 'ai_tutor') initAITutor();
    if (name === 'final') renderFinal(); // Re-render final test screen to reset its state
  }
  navButtons.forEach(btn=>{
    btn.addEventListener('click', ()=> showScreen(btn.dataset.screen));
  });

  renderDashboard();
  renderModules();
  renderQuiz();
  renderFinal();
  renderSummary();
  renderGamificationSidebar();
  renderLeaderboard();
  renderAITutor();
  showScreen('dashboard');
  updateStreakAndAchievements();
  updateNotifications();
  checkReminders(); // Initial check
  setInterval(checkReminders, 10000); // Check every 10 seconds for better responsiveness

  // UTILITY FUNCTIONS
  function saveMe(){
    const studentsArr = JSON.parse(localStorage.getItem('learnsphere_students') || '[]');
    const idx = studentsArr.findIndex(s=>s.username === me.username);
    if (idx >= 0) studentsArr[idx] = me; else studentsArr.push(me);
    localStorage.setItem('learnsphere_students', JSON.stringify(studentsArr));
    localStorage.setItem('learnsphere_notifications', JSON.stringify(notifications));
  }
  
  function getISODateString(date) { return date.toISOString().split('T')[0]; }
  
  function updateStreakAndAchievements() {
      const today = new Date();
      const todayStr = getISODateString(today);
      const lastLoginStr = me.lastLoginDate;

      if (lastLoginStr !== todayStr) {
          const yesterday = new Date(today);
          yesterday.setDate(today.getDate() - 1);
          const yesterdayStr = getISODateString(yesterday);
          
          if (lastLoginStr === yesterdayStr) {
              me.streak = (me.streak || 0) + 1;
          } else {
              me.streak = 1;
          }
          me.lastLoginDate = todayStr;
      }
      
      if (me.streak >= 3 && !me.achievements.includes('streak_starter')) {
          me.achievements.push('streak_starter');
          addNotification('Achievement Unlocked!', 'You earned the "Streak Starter" badge!');
      }
      
      saveMe();
      renderGamificationSidebar();
  }
  
  function showNotification(message) {
      const notif = document.createElement('div');
      notif.className = 'notification';
      notif.textContent = message;
      document.body.appendChild(notif);
      setTimeout(() => notif.classList.add('show'), 10);
      setTimeout(() => {
          notif.classList.remove('show');
          setTimeout(() => notif.remove(), 300);
      }, 3000);
  }

  // EVENT HANDLERS
  function handleModuleClick(e) {
      if (e.target && e.target.classList.contains('mark-complete-btn')) {
          const topic = e.target.dataset.topic;
          if (!me.completed_modules.includes(topic)) {
              me.completed_modules.push(topic);
              if (me.completed_modules.length === 1 && !me.achievements.includes('first_step')) {
                  me.achievements.push('first_step');
                  addNotification('Achievement Unlocked!', 'You earned the "First Step" badge!');
              }
              updateStreakAndAchievements();
          }
          saveMe();
          renderModules();
          renderDashboard();
      }
      
      if (e.target && e.target.classList.contains('bookmark-btn')) {
          const topic = e.target.dataset.topic;
          if (!me.bookmarks) me.bookmarks = [];
          const idx = me.bookmarks.indexOf(topic);
          if (idx === -1) {
              me.bookmarks.push(topic);
              showNotification(`Bookmarked ${topic}`);
          } else {
              me.bookmarks.splice(idx, 1);
              showNotification(`Removed bookmark from ${topic}`);
          }
          saveMe();
          renderModules();
      }
  }

  function handleQuizSubmit(ev) {
      ev.preventDefault();
      if (quizTimer) clearInterval(quizTimer);
      
      const startTime = parseInt(document.getElementById('quiz-form').dataset.startTime || Date.now());
      const timeTaken = Math.floor((Date.now() - startTime) / 1000);
      
      const quizBankNow = JSON.parse(localStorage.getItem('learnsphere_quizbank') || '{}');
      let totalCorrect = 0, totalQ = 0;
      let detailedResults = [];

      me.weak_topics.forEach(t=>{
        const questions = quizBankNow[t] || [];
        if (questions.length === 0) return;
        let correct = 0;
        questions.forEach((q,qi)=>{
          totalQ++;
          const sel = document.querySelector(`input[name="q_${t}_${qi}"]:checked`);
          const isCorrect = sel && sel.value === q.ans;
          if (isCorrect) correct++;
          detailedResults.push({ topic: t, q: q.q, ans: q.ans, explanation: q.explanation, selected: sel ? sel.value : "Not answered", isCorrect });
        });
        const score = correct / questions.length;
        me.quiz_scores[t] = score;
        if (score === 1 && !me.achievements.includes('quiz_whiz')) {
            me.achievements.push('quiz_whiz');
            addNotification('Achievement Unlocked!', 'You earned the "Quiz Whiz" badge!');
        }
        totalCorrect += correct;
      });
      
      if (timeTaken < 300 && !me.achievements.includes('speedster')) {
          me.achievements.push('speedster');
          addNotification('Achievement Unlocked!', 'You earned the "Speedster" badge!');
      }
      
      updateStreakAndAchievements();
      renderLeaderboard();
      saveMe();
      renderDashboard();
      
      const scorePercent = Math.round((totalCorrect / totalQ) * 100);
      document.getElementById('quiz-form').innerHTML = ''; // Clear the form
      document.getElementById('quiz-result').innerHTML = `<div class="result-card success">
        <strong>Quiz Submitted!</strong> You answered ${totalCorrect}/${totalQ} correctly (${scorePercent}%) in ${Math.floor(timeTaken / 60)}:${(timeTaken % 60).toString().padStart(2, '0')}
        <div class="accordion mt-3" id="quizExplanations">
        ${detailedResults.map((result, idx) => `<div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#explanation${idx}">
                <span class="me-2">${result.isCorrect ? '✅' : '❌'}</span>
                Question ${idx + 1}: ${result.topic}
                </button>
            </h2>
            <div id="explanation${idx}" class="accordion-collapse collapse" data-bs-parent="#quizExplanations">
                <div class="accordion-body">
                    <p><strong>Question:</strong> ${result.q}</p>
                    <p><strong>Your Answer:</strong> <span style="color: ${result.isCorrect ? 'green' : 'red'};">${result.selected}</span></p>
                    <p><strong>Correct Answer:</strong> <span style="color: green;">${result.ans}</span></p>
                    ${result.explanation ? `<hr><p><strong>Explanation:</strong> ${result.explanation}</p>` : ''}
                </div>
            </div>
            </div>`).join('')}
        </div>
      </div>`;
  }

  function handleFinalTestSubmit(ev) {
      ev.preventDefault();
      if (finalTimer) clearInterval(finalTimer);
      
      const finalTestQuestions = JSON.parse(localStorage.getItem('learnsphere_final_test') || '[]');
      const quizBank = JSON.parse(localStorage.getItem('learnsphere_quizbank') || '{}');
      let correct = 0;

      finalTestQuestions.forEach(qInfo => {
          const question = quizBank[qInfo.topic][qInfo.index];
          if (!question) return;
          const inputName = `final_${qInfo.topic}_${qInfo.index}`;
          const selected = document.querySelector(`input[name="${inputName}"]:checked`);
          if (selected && selected.value === question.ans) correct++;
      });
      
      me.final_test_score = Math.round((correct / Math.max(finalTestQuestions.length, 1)) * 100);
      
      if (me.final_test_score === 100 && !me.achievements.includes('perfectionist')) {
          me.achievements.push('perfectionist');
          addNotification('Achievement Unlocked!', 'You earned the "Perfectionist" badge!');
      }
      
      saveMe();
      renderDashboard();
      renderSummary();
      document.getElementById('final-result').innerHTML = `<div class="result-card ${me.final_test_score >= 80 ? 'success' : 'warning'}"><strong>Test Complete!</strong><p>Your final score is: <strong>${me.final_test_score}%</strong></p></div>`;
      document.getElementById('final-form').innerHTML = '';
  }

  async function sendMessage() {
      const chatContainer = document.getElementById('chat-container');
      const chatInput = document.getElementById('chat-input');
      const userMessage = chatInput.value.trim();
      if (!userMessage || !GEMINI_API_KEY) return;

      chatContainer.innerHTML += `<div class="chat-bubble user">${userMessage}</div>`;
      chatInput.value = '';
      chatContainer.scrollTop = chatContainer.scrollHeight;
      chatHistory.push({ role: "user", parts: [{ text: userMessage }] });
      
      chatContainer.innerHTML += `<div class="chat-bubble ai" id="loading-bubble"><span class="loading-spinner"></span> Thinking...</div>`;
      chatContainer.scrollTop = chatContainer.scrollHeight;

      const systemPrompt = `You are "LearnSphere AI," an expert, encouraging AI tutor. Current Student: ${me.name}. Weak Topics: ${me.weak_topics.join(', ')}. Quiz Scores: ${JSON.stringify(me.quiz_scores)}. Be supportive, use Markdown for lists and bolding, and keep responses concise.`;
      const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`;
      const payload = {
          contents: chatHistory,
          systemInstruction: { parts: [{ text: systemPrompt }] },
          safetySettings: [{ category: 'HARM_CATEGORY_HARASSMENT', threshold: 'BLOCK_MEDIUM_AND_ABOVE' }],
          generationConfig: { temperature: 0.7, maxOutputTokens: 2048 },
      };

      try {
          const response = await fetch(apiUrl, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
          });
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          const result = await response.json();
          const candidate = result.candidates?.[0];
          let aiResponse = "Sorry, I couldn't generate a response. Please try again.";
          if (candidate?.content?.parts?.[0]?.text) {
              aiResponse = candidate.content.parts[0].text.replace(/\n/g, '<br>');
          }
          document.getElementById('loading-bubble').innerHTML = aiResponse;
          chatHistory.push({ role: "model", parts: [{ text: aiResponse.replace(/<br>/g, '\n') }] });
      } catch (error) {
          console.error("Error calling Gemini API:", error);
          document.getElementById('loading-bubble').innerHTML = `I'm having connection issues. Please check the console for details.`;
      }
      chatContainer.scrollTop = chatContainer.scrollHeight;
  }
  
  // NEW FEATURES
  let studyTimerInterval = null;
  let studyStartTime = null;
  
  function startStudyTimer() {
      if (studyTimerInterval) return;
      studyStartTime = Date.now();
      const display = document.getElementById('study-timer-display');
      studyTimerInterval = setInterval(() => {
          const elapsed = Math.floor((Date.now() - studyStartTime) / 1000);
          const minutes = Math.floor(elapsed / 60);
          const seconds = elapsed % 60;
          display.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
      }, 1000);
      document.getElementById('start-study-timer').disabled = true;
      document.getElementById('stop-study-timer').disabled = false;
  }
  
  function stopStudyTimer() {
      if (!studyTimerInterval) return;
      clearInterval(studyTimerInterval);
      studyTimerInterval = null;
      const elapsed = Math.floor((Date.now() - studyStartTime) / 1000);
      me.study_time += elapsed;
      saveMe();
      document.getElementById('start-study-timer').disabled = false;
      document.getElementById('stop-study-timer').disabled = true;
      showNotification(`Study session saved: ${Math.floor(elapsed / 60)} minutes`);
  }
  
  function exportProgress() {
      const data = {
          name: me.name,
          completed_modules: me.completed_modules,
          quiz_scores: me.quiz_scores,
          final_test_score: me.final_test_score,
          achievements: me.achievements,
          study_time_minutes: Math.floor(me.study_time / 60)
      };
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${me.name}_progress.json`;
      a.click();
      URL.revokeObjectURL(url);
      showNotification('Progress exported successfully!');
  }
  
  function saveNote() {
      const topic = document.getElementById('note-topic').value;
      const content = document.getElementById('note-content').value.trim();
      if (!topic || !content) {
          alert('Please select a topic and write a note.');
          return;
      }
      if (!me.notes) me.notes = {};
      if (!me.notes[topic]) me.notes[topic] = [];
      me.notes[topic].push({ content, date: new Date().toISOString() });
      saveMe();
      document.getElementById('note-content').value = '';
      renderNotesScreen();
      showNotification('Note saved!');
  }

  // CALENDAR & NOTIFICATION FUNCTIONS
  function requestNotificationPermission() {
      if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
          Notification.requestPermission().then(permission => {
              if (permission === 'granted') {
                  new Notification('LearnSphere Notifications Enabled! ✅', { 
                      body: 'You will now receive reminders about your study sessions.',
                      icon: 'https://img.icons8.com/plasticine/100/book.png'
                  });
                  addNotification('Notifications Enabled', 'You will be reminded about upcoming study sessions.');
              }
          });
      } else if (Notification.permission === 'granted') {
          // Show info about the test reminder
          const reminderExists = me.study_plan.some(e => e.reminder && !e.notified);
          if (reminderExists) {
              showNotification('💡 Tip: A test reminder is set for 30 seconds from now!');
          }
      }
  }

  function renderCalendar() {
      const month = calendarDate.getMonth();
      const year = calendarDate.getFullYear();
      document.getElementById('calendar-month-year').textContent = new Date(year, month).toLocaleString('default', { month: 'long', year: 'numeric' });
      const weekdaysContainer = document.getElementById('calendar-weekdays');
      weekdaysContainer.innerHTML = '';
      ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(day => {
          weekdaysContainer.innerHTML += `<div>${day}</div>`;
      });
      
      const daysContainer = document.getElementById('calendar-days');
      daysContainer.innerHTML = '';
      const firstDayOfMonth = new Date(year, month, 1).getDay();
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      for (let i = 0; i < firstDayOfMonth; i++) {
          daysContainer.innerHTML += `<div class="calendar-day empty"></div>`;
      }
      for (let day = 1; day <= daysInMonth; day++) {
          const dayEl = document.createElement('div');
          dayEl.className = 'calendar-day';
          dayEl.textContent = day;
          const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          if (me.study_plan.some(e => e.date === dateStr)) dayEl.classList.add('has-event');
          const today = new Date();
          if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) dayEl.classList.add('today');
          dayEl.addEventListener('click', () => openEventModal(dateStr));
          daysContainer.appendChild(dayEl);
      }
      displayEventsForDay(getISODateString(calendarDate));
  }

  function openEventModal(date) {
      document.getElementById('event-form').reset();
      document.getElementById('event-date').value = date;
      document.getElementById('eventModalLabel').textContent = `Add Study Session for ${date}`;
      displayEventsForDay(date);
      eventModal.show();
  }

  function displayEventsForDay(date) {
      const events = me.study_plan.filter(e => e.date === date).sort((a,b) => a.time.localeCompare(b.time));
      const eventList = document.getElementById('event-list');
      if (events.length === 0) {
          eventList.innerHTML = `<p class="small-muted">No sessions for ${date}. Click the date to add one.</p>`;
      } else {
          eventList.innerHTML = events.map(event => `
              <div class="event-item">
                  <span><strong>${event.time}</strong> - ${event.title} ${event.reminder ? '<i class="fas fa-bell ms-2 text-info"></i>' : ''}</span>
                  <button class="btn-delete-item" data-event-id="${event.id}"><i class="fas fa-trash"></i></button>
              </div>`).join('');
      }
  }

  function saveStudyEvent() {
      const date = document.getElementById('event-date').value;
      const title = document.getElementById('event-title').value.trim();
      const time = document.getElementById('event-time').value;
      const reminder = document.getElementById('event-reminder').checked;
      if (!title || !time) { alert('Please provide a title and time.'); return; }
      me.study_plan.push({ id: Date.now(), date, time, title, reminder, notified: false });
      saveMe();
      renderCalendar();
      displayEventsForDay(date);
      eventModal.hide();
  }
  
  function checkReminders() {
      if (!('Notification' in window) || Notification.permission !== 'granted') {
          return;
      }

      const now = new Date();
      me.study_plan.forEach(event => {
          if (event.reminder && !event.notified) {
              const eventDateTime = new Date(`${event.date}T${event.time}`);
              const timeDiff = (eventDateTime - now) / 60000; // difference in minutes
              
              // Trigger if reminder is within 1 minute and event hasn't passed more than 5 minutes ago
              if (timeDiff <= 1 && timeDiff > -5) { 
                  new Notification('📚 Study Reminder!', {
                      body: `Time for your study session: ${event.title}`,
                      icon: 'https://img.icons8.com/plasticine/100/book.png',
                      requireInteraction: true
                  });
                  addNotification('Study Reminder', `It's time to study: ${event.title} at ${event.time}`);
                  event.notified = true;
                  saveMe();
              }
          }
      });
  }

  function handleDeleteEvent(e) {
      const deleteButton = e.target.closest('.btn-delete-item');
      if (deleteButton) {
          const eventId = deleteButton.dataset.eventId;
          const currentEvent = me.study_plan.find(event => event.id.toString() === eventId);
          if (confirm('Are you sure you want to delete this study session?')) {
              me.study_plan = me.study_plan.filter(event => event.id.toString() !== eventId);
              saveMe();
              renderCalendar(); 
              if (currentEvent) {
                  displayEventsForDay(currentEvent.date);
              }
          }
      }
  }
  
  function handleDeleteNote(e) {
      const deleteButton = e.target.closest('.btn-delete-item');
      if (deleteButton) {
          const topic = deleteButton.dataset.noteTopic;
          const index = parseInt(deleteButton.dataset.noteIndex, 10);

          if (confirm('Are you sure you want to delete this note?')) {
              if (me.notes[topic] && me.notes[topic][index]) {
                  me.notes[topic].splice(index, 1);
                  if (me.notes[topic].length === 0) {
                      delete me.notes[topic];
                  }
                  saveMe();
                  renderNotesScreen();
              }
          }
      }
  }

  function toggleNotifications() {
    const panel = document.getElementById('notifications-panel');
    panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
    if (panel.style.display === 'block') markNotificationsAsRead();
  }

  function updateNotifications() {
    const unreadCount = notifications.filter(n => !n.read).length;
    const badge = document.getElementById('notification-count');
    badge.textContent = unreadCount;
    badge.classList.toggle('hidden', unreadCount === 0);
    
    const listHTML = notifications.map(n => {
        const timeAgo = getTimeAgo(new Date(n.timestamp));
        return `<div class="notification-item ${n.read ? '' : 'unread'}">
            <div><strong>${n.title}</strong></div>
            <div class="small-muted">${n.message}</div>
            <div class="small-muted" style="font-size: 0.75rem; margin-top: 0.25rem; color: var(--text-muted-light);">${timeAgo}</div>
        </div>`;
    }).join('');
    
    document.getElementById('notifications-list').innerHTML = listHTML || '<div class="small-muted text-center p-3">No notifications yet</div>';
  }
  
  function getTimeAgo(date) {
      const seconds = Math.floor((new Date() - date) / 1000);
      const intervals = {
          year: 31536000,
          month: 2592000,
          week: 604800,
          day: 86400,
          hour: 3600,
          minute: 60
      };
      
      for (const [name, secondsInInterval] of Object.entries(intervals)) {
          const interval = Math.floor(seconds / secondsInInterval);
          if (interval >= 1) {
              return interval === 1 ? `1 ${name} ago` : `${interval} ${name}s ago`;
          }
      }
      return 'Just now';
  }

  function addNotification(title, message) {
    notifications.unshift({id: Date.now(), title, message, timestamp: new Date(), read: false});
    updateNotifications();
    saveMe();
  }

  function markNotificationsAsRead() {
    notifications.forEach(n => { n.read = true; });
    updateNotifications();
    saveMe();
  }

  function updateOnlineStatus() {
      document.getElementById('offline-indicator').style.display = navigator.onLine ? 'none' : 'block';
  }

  // RENDER FUNCTIONS
  function renderDashboard(){
    const statsContainer = document.getElementById('dashboard-stats');
    const avgScore = (Object.values(me.quiz_scores).reduce((a, b) => a + b, 0) / (Object.keys(me.quiz_scores).length || 1)) * 100;
    const studyHours = (me.study_time / 3600).toFixed(1);
    statsContainer.innerHTML = `
      <div class="stat-card"><div class="stat-value">${me.completed_modules.length}</div><div class="stat-label">Modules Completed</div></div>
      <div class="stat-card"><div class="stat-value">${avgScore.toFixed(0)}%</div><div class="stat-label">Average Score</div></div>
      <div class="stat-card"><div class="stat-value">${me.final_test_score ?? 'N/A'}</div><div class="stat-label">Final Test</div></div>
      <div class="stat-card"><div class="stat-value">${studyHours}h</div><div class="stat-label">Study Time</div></div>`;
    const topics = Object.keys(me.quiz_scores);
    const scores = topics.map(t => (me.quiz_scores[t] || 0) * 100);
    if (stuChart) stuChart.destroy();
    const ctx = document.getElementById('stu-chart').getContext('2d');
    stuChart = new Chart(ctx, {
      type: 'bar',
      data: { labels: topics.length?topics:['No quizzes yet'], datasets:[{label:'Score %', data: scores.length?scores:[0], backgroundColor: document.body.classList.contains('dark') ? '#ff6fd8' : '#7b2ff7'}] },
      options:{plugins:{legend:{display:false}}, responsive:true, scales:{y:{beginAtZero:true, max: 100}}}
    });
    const recDiv = document.getElementById('recommendations');
    recDiv.innerHTML = '';
    if(me.weak_topics.length === 0) { recDiv.innerHTML = '<p>No specific weaknesses detected. Great job!</p>'; return; }
    me.weak_topics.forEach(t=>{
      const card = document.createElement('div');
      card.className = 'recommendation-card';
      card.innerHTML = `<h4>${t}</h4><div class="small-muted">Our AI suggests focusing here.</div><div class="mt"><button class="btn primary small-btn">Start Module</button></div>`;
      card.style.cursor = 'pointer';
      card.addEventListener('click', () => { showScreen('modules'); });
      recDiv.appendChild(card);
    });
  }

  function renderModules(){
    const list = document.getElementById('modules-list');
    list.innerHTML = '';
    list.className = 'modules-grid';
    const allTopics = [...new Set([...Object.keys(JSON.parse(localStorage.getItem('learnsphere_quizbank')||'{}')), ...me.weak_topics])];
    allTopics.forEach(t=>{
      const isCompleted = me.completed_modules.includes(t);
      const isBookmarked = me.bookmarks && me.bookmarks.includes(t);
      const score = me.quiz_scores[t];
      let progress = isCompleted ? 100 : (score !== undefined ? Math.max(20, score * 100) : 0);
      const card = document.createElement('div');
      card.className = 'module-card';
      card.id = `module-card-${t}`;
      let actionButtonHTML = !isCompleted
        ? `<button class="btn primary mt mark-complete-btn" data-topic="${t}">Mark as Completed</button>`
        : `<p class="small-muted mt">✅ Completed!</p>`;
      const bookmarkIcon = isBookmarked ? 'fa-bookmark' : 'fa-regular fa-bookmark';
      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <h4>${t}</h4>
          <button class="bookmark-btn" data-topic="${t}" style="background: none; border: none; cursor: pointer; font-size: 1.2rem; color: var(--accent1);"><i class="fas ${bookmarkIcon}"></i></button>
        </div>
        <p class="small-muted">Master the fundamentals.</p>
        <div class="progress-bar"><div class="progress-bar-fill" style="width: ${progress}%;"></div></div>
        ${actionButtonHTML}`;
      list.appendChild(card);
    });
  }
  
  function renderQuiz(){
    const form = document.getElementById('quiz-form');
    form.innerHTML = '';
    form.dataset.startTime = Date.now();
    document.getElementById('quiz-result').innerHTML = '';
    const quizBank = JSON.parse(localStorage.getItem('learnsphere_quizbank') || '{}');
    let hasQuestions = false;
    me.weak_topics.forEach(t=>{
      const questions = quizBank[t] || [];
      if (questions.length === 0) return;
      hasQuestions = true;
      const section = document.createElement('div'); section.className = 'panel mb';
      section.innerHTML = `<h4>${t}</h4>`;
      questions.forEach((q, qi)=>{
        const qid = `q_${t}_${qi}`;
        const qdiv = document.createElement('div'); qdiv.className = 'quiz-question-wrapper';
        let optionsHTML = '';
        q.options.forEach(opt=>{
          optionsHTML += `<label class="radio-option">${opt}<input type="radio" name="${qid}" value="${opt}"><span class="checkmark"></span></label>`;
        });
        let hintHTML = q.hint ? `<button type="button" class="btn ghost btn-sm mb-2" onclick="this.nextElementSibling.classList.toggle('hidden')">Show Hint</button><div class="panel hidden mb-2">${q.hint}</div>` : '';
        qdiv.innerHTML = `<div class="small-muted">${q.q}</div>${hintHTML}${optionsHTML}`;
        section.appendChild(qdiv);
      });
      form.appendChild(section);
    });
    if (!hasQuestions) { form.innerHTML = '<p class="small-muted">No quiz questions available.</p>'; return; }
    const btn = document.createElement('button'); btn.type = 'submit'; btn.className='btn primary large'; btn.innerText = 'Submit Quiz';
    form.appendChild(btn);
    
    // Start timer
    let timeLeft = 600;
    if (quizTimer) clearInterval(quizTimer);
    quizTimer = setInterval(() => {
        timeLeft--;
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        document.getElementById('quiz-timer').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        if (timeLeft <= 0) {
            clearInterval(quizTimer);
            form.dispatchEvent(new Event('submit'));
        }
    }, 1000);
  }

  function renderFinal() {
      document.getElementById('final-test-start-screen').classList.remove('hidden');
      document.getElementById('final-test-wrapper').classList.add('hidden');
      document.getElementById('final-form').innerHTML = '';
      document.getElementById('final-result').innerHTML = '';
      if (finalTimer) clearInterval(finalTimer);

      const form = document.getElementById('final-form');
      const finalTestQuestions = JSON.parse(localStorage.getItem('learnsphere_final_test') || '[]');
      const quizBank = JSON.parse(localStorage.getItem('learnsphere_quizbank') || '{}');
      
      if (finalTestQuestions.length === 0) {
          document.getElementById('final-test-start-screen').innerHTML = '<p class="small-muted">The final exam has not been set by the teacher yet.</p>';
          return;
      }
      
      finalTestQuestions.forEach(qInfo => {
          const question = quizBank[qInfo.topic]?.[qInfo.index];
          if (!question) return;
          const block = document.createElement('div');
          block.className = 'panel mb';
          let optionsHTML = '';
          const inputName = `final_${qInfo.topic}_${qInfo.index}`;
          question.options.forEach((opt) => {
              optionsHTML += `<label class="radio-option">${opt}<input type="radio" name="${inputName}" value="${opt}"><span class="checkmark"></span></label>`;
          });
          block.innerHTML = `<h4>${qInfo.topic}</h4><div class="quiz-question-wrapper"><div class="small-muted">${question.q}</div>${optionsHTML}</div>`;
          form.appendChild(block);
      });
      const btn = document.createElement('button');
      btn.type = 'submit';
      btn.className = 'btn primary large';
      btn.innerText = 'Submit Final Exam';
      form.appendChild(btn);
  }
  
  function startFinalTest() {
      document.getElementById('final-test-start-screen').classList.add('hidden');
      document.getElementById('final-test-wrapper').classList.remove('hidden');
      
      let timeLeft = 1200; // 20 minutes
      if (finalTimer) clearInterval(finalTimer);
      finalTimer = setInterval(() => {
          timeLeft--;
          const minutes = Math.floor(timeLeft / 60);
          const seconds = timeLeft % 60;
          document.getElementById('final-test-timer').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
          if (timeLeft <= 0) {
              clearInterval(finalTimer);
              document.getElementById('final-form').dispatchEvent(new Event('submit'));
          }
      }, 1000);
  }

  function renderSummary(){
    const topics = Object.keys(me.quiz_scores || {});
    const scores = topics.map(t => (me.quiz_scores[t] || 0) * 100);
    const summaryStatsContainer = document.getElementById('summary-stats');
    const validScores = scores.filter(s => s !== undefined && s !== null);
    const highestScore = validScores.length > 0 ? Math.max(...validScores) : 0;
    const lowestScore = validScores.length > 0 ? Math.min(...validScores) : 0;
    summaryStatsContainer.innerHTML = `
        <div class="stat-card"><div class="stat-value">${highestScore.toFixed(0)}%</div><div class="stat-label">Highest Score</div></div>
        <div class="stat-card"><div class="stat-value">${lowestScore.toFixed(0)}%</div><div class="stat-label">Lowest Score</div></div>
        <div class="stat-card"><div class="stat-value">${topics.length}</div><div class="stat-label">Quizzes Taken</div></div>`;
    if (summaryChart) summaryChart.destroy();
    const ctx = document.getElementById('summary-chart').getContext('2d');
    summaryChart = new Chart(ctx, {
      type: 'line',
      data: { labels: topics.length?topics:['No data'], datasets:[{label:'Scores %',data:scores.length?scores:[0],borderColor: document.body.classList.contains('dark') ? '#ff6fd8' : '#7b2ff7',fill:true, backgroundColor: document.body.classList.contains('dark') ? 'rgba(255, 111, 216, 0.1)' : 'rgba(123, 47, 247, 0.1)', tension: 0.3 }]},
      options:{responsive:true, scales:{y:{beginAtZero:true, max: 100}}}
    });
    const tipsContainer = document.getElementById('ai-tips');
    tipsContainer.innerHTML = '';
    if (me.weak_topics.length > 0) {
        me.weak_topics.forEach(t=> {
            const tipCard = document.createElement('div');
            tipCard.className = 'ai-tip-card';
            tipCard.innerHTML = `<div class="tip-icon"><i class="fas fa-lightbulb"></i></div><div class="tip-content"><strong>Focus on ${t}</strong><p>This is a key area for improvement.</p></div>`;
            tipsContainer.appendChild(tipCard);
        });
    } else {
        const greatJobCard = document.createElement('div');
        greatJobCard.className = 'ai-tip-card';
        greatJobCard.innerHTML = `<div class="tip-icon"><i class="fas fa-check-circle"></i></div><div class="tip-content"><strong>Excellent Work!</strong><p>No specific weak areas detected.</p></div>`;
        tipsContainer.appendChild(greatJobCard);
    }
  }
  
  function renderGamificationSidebar() {
    const container = document.getElementById('gamification-sidebar');
    let achievementsHTML = '<h6>Achievements</h6>';
    if (me.achievements.length > 0) {
        me.achievements.forEach(achId => {
            const ach = ACHIEVEMENTS[achId];
            achievementsHTML += `<div class="achievement-badge" title="${ach.description}"><i class="fas ${ach.icon}"></i> ${ach.name}</div>`;
        });
    } else {
        achievementsHTML += '<p class="small-muted">None yet. Keep learning!</p>';
    }
    container.innerHTML = `<div class="streak-counter"><div class="streak-icon">🔥</div><div class="streak-days">${me.streak} Day Streak</div></div>${achievementsHTML}`;
  }

  function renderLeaderboard() {
      const container = document.getElementById('leaderboard-list');
      container.innerHTML = '';
      const allStudents = JSON.parse(localStorage.getItem('learnsphere_students') || '[]');
      
      const leaderboard = allStudents.map(student => {
          const avgScore = (Object.values(student.quiz_scores).reduce((a, b) => a + b, 0) / (Object.keys(student.quiz_scores).length || 1)) * 100;
          return {
              name: student.name,
              username: student.username,
              score: Math.round(avgScore || 0),
              completed: student.completed_modules.length
          };
      }).sort((a, b) => b.score - a.score);

      leaderboard.forEach((player, index) => {
          const rank = index + 1;
          const isCurrentUser = player.username === me.username;
          const item = document.createElement('div');
          item.className = 'leaderboard-item';
          if (rank <= 3) item.classList.add(`rank-${rank}`);
          if (isCurrentUser) item.classList.add('current-user-rank');
          item.innerHTML = `<div class="leaderboard-rank">#${rank}</div><div class="leaderboard-details"><strong>${player.name} ${isCurrentUser ? '(You)' : ''}</strong><div class="small-muted">${player.completed} modules completed</div></div><div class="leaderboard-score">${player.score}%</div>`;
          container.appendChild(item);
      });
  }

  function renderAITutor() {
      const chatContainer = document.getElementById('chat-container');
      const chatInput = document.getElementById('chat-input');
      const sendButton = document.getElementById('chat-send-btn');
      
      if (!GEMINI_API_KEY) {
          chatContainer.innerHTML = `<div class="chat-bubble ai">The AI Tutor is offline. A developer needs to add a Gemini API key.</div>`;
          chatInput.disabled = true;
          sendButton.disabled = true;
      } else {
          chatContainer.innerHTML = `<div class="chat-bubble ai">Hello! How can I help you with your weak topics today?</div>`;
          chatInput.disabled = false;
          sendButton.disabled = false;
      }
  }

  function initAITutor() {
    chatHistory = []; // Reset history for the new session
    const chatContainer = document.getElementById('chat-container');
    const initialPrompt = `Hello, ${me.name}. I am your AI learning assistant. I see your current weak topics are: ${me.weak_topics.join(', ')}. How can I help you improve today?`;
    chatContainer.innerHTML = `<div class="chat-bubble ai">${initialPrompt}</div>`;
    chatHistory.push({ role: "model", parts: [{ text: initialPrompt }] });
  }
  
  function renderProgressScreen() {
      const container = document.getElementById('progress-content');
      const studyHours = (me.study_time / 3600).toFixed(1);
      const studyMinutes = Math.floor((me.study_time % 3600) / 60);
      
      container.innerHTML = `
          <div class="progress-overview">
              <div class="stat-card">
                  <div class="stat-value">${studyHours}h ${studyMinutes}m</div>
                  <div class="stat-label">Total Study Time</div>
              </div>
              <div class="stat-card">
                  <div class="stat-value">${me.achievements.length}/${Object.keys(ACHIEVEMENTS).length}</div>
                  <div class="stat-label">Achievements Unlocked</div>
              </div>
              <div class="stat-card">
                  <div class="stat-value">${me.bookmarks ? me.bookmarks.length : 0}</div>
                  <div class="stat-label">Bookmarked Topics</div>
              </div>
          </div>
          
          <div class="panel mt">
              <h4>Study Timer</h4>
              <div class="study-timer-controls">
                  <div id="study-timer-display" class="timer-display">0:00</div>
                  <div class="form-actions">
                      <button id="start-study-timer" class="btn primary">Start Session</button>
                      <button id="stop-study-timer" class="btn ghost" disabled>Stop Session</button>
                  </div>
              </div>
          </div>
          
          <div class="panel mt">
              <h4>Bookmarked Topics</h4>
              <div class="bookmarks-list">
                  ${me.bookmarks && me.bookmarks.length > 0
                      ? me.bookmarks.map(topic => `<div class="bookmark-item">${topic}</div>`).join('')
                      : '<p class="small-muted">No bookmarks yet. Bookmark topics from the Modules page.</p>'}
              </div>
          </div>
          
          <div class="panel mt">
              <h4>Export Progress</h4>
              <p class="small-muted">Download your learning data as a JSON file.</p>
              <button id="export-progress" class="btn primary mt">Export Data</button>
          </div>
      `;
      
      // Re-attach event listeners
      document.getElementById('start-study-timer')?.addEventListener('click', startStudyTimer);
      document.getElementById('stop-study-timer')?.addEventListener('click', stopStudyTimer);
      document.getElementById('export-progress')?.addEventListener('click', exportProgress);
  }
  
  function renderNotesScreen() {
      const container = document.getElementById('notes-content');
      const allTopics = [...new Set([...Object.keys(JSON.parse(localStorage.getItem('learnsphere_quizbank')||'{}')), ...me.weak_topics])];
      
      let notesHTML = '';
      if (me.notes && Object.keys(me.notes).length > 0) {
          for (const topic in me.notes) {
              notesHTML += `<div class="notes-topic-section"><h4>${topic}</h4>`;
              me.notes[topic].forEach((note, idx) => {
                  const date = new Date(note.date).toLocaleDateString();
                  notesHTML += `
                      <div class="note-card">
                          <div class="note-header">
                              <span class="note-date">${date}</span>
                              <button class="btn-delete-item" data-note-topic="${topic}" data-note-index="${idx}"><i class="fas fa-trash"></i></button>
                          </div>
                          <p>${note.content}</p>
                      </div>`;
              });
              notesHTML += `</div>`;
          }
      } else {
          notesHTML = '<p class="small-muted">No notes yet. Start taking notes below!</p>';
      }
      
      container.innerHTML = `
          <div class="panel mb">
              <h4>Add New Note</h4>
              <div class="mb">
                  <label>Topic</label>
                  <select id="note-topic" class="input">
                      ${allTopics.map(t => `<option value="${t}">${t}</option>`).join('')}
                  </select>
              </div>
              <div class="mb">
                  <label>Note Content</label>
                  <textarea id="note-content" class="input" rows="4" placeholder="Write your notes here..."></textarea>
              </div>
              <button id="save-note-btn" class="btn primary">Save Note</button>
          </div>
          
          <div class="notes-list">
              ${notesHTML}
          </div>
      `;
      
      // Re-attach event listener
      document.getElementById('save-note-btn')?.addEventListener('click', saveNote);
  }
});
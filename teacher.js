// teacher.js - Enhanced with new features
document.addEventListener('DOMContentLoaded', () => {
  // AI-POWERED QUESTION BANK GENERATION
  function autoGenerateQuizBank() {
    if (localStorage.getItem('learnsphere_quizbank')) return;
    const aiBank = {
      'Algebra': [
        { q: 'Solve: 2x + 5 = 15', options: ['x=5', 'x=10', 'x=2.5'], ans: 'x=5', difficulty: 'easy', hint: 'Isolate the variable x.', explanation: 'Subtract 5 from both sides to get 2x = 10, then divide by 2.' },
        { q: 'What is the slope of the line y = 3x - 7?', options: ['3', '-7', '7'], ans: '3', difficulty: 'easy', hint: 'The equation is in slope-intercept form (y = mx + b).', explanation: 'In the form y = mx + b, "m" represents the slope. Here, m = 3.' },
        { q: 'Factor the expression: x² - 4', options: ['(x-2)(x+2)', '(x-2)(x-2)', '(x+4)(x-1)'], ans: '(x-2)(x+2)', difficulty: 'medium', hint: 'This is a difference of squares.', explanation: 'The difference of squares formula is a² - b² = (a-b)(a+b). Here, a=x and b=2.'}
      ],
      'Calculus': [
        { q: 'What is the derivative of x²?', options: ['2x', 'x', 'x³/3'], ans: '2x', difficulty: 'easy', hint: 'Use the power rule for derivatives.', explanation: 'The power rule states d/dx(x^n) = nx^(n-1). For x², n=2, so the derivative is 2x^(2-1) = 2x.' },
        { q: 'What is the integral of 3x² dx?', options: ['x³ + C', '6x + C', '3x³ + C'], ans: 'x³ + C', difficulty: 'medium', hint: 'Use the reverse power rule.', explanation: 'The integral of x^n is (x^(n+1))/(n+1). For 3x², it becomes 3 * (x³/3) = x³.' },
      ],
      'Statistics': [
          { q: 'What is the mean of the numbers 2, 4, 6?', options: ['4', '3', '5'], ans: '4', difficulty: 'easy', hint: 'The mean is the average of the numbers.', explanation: 'The sum is 2+4+6=12. The count is 3. The mean is 12 / 3 = 4.'},
          { q: 'What measure of central tendency is the middle value in a sorted dataset?', options: ['Median', 'Mean', 'Mode'], ans: 'Median', difficulty: 'easy', hint: 'Think "middle".', explanation: 'The median is the value separating the higher half from the lower half of a data sample.'}
      ],
      'Geometry': [
          { q: 'What is the area of a circle with radius r?', options: ['πr²', '2πr', 'πr'], ans: 'πr²', difficulty: 'easy', hint: 'Area involves squaring the radius.', explanation: 'The formula for the area of a circle is Pi times the radius squared.'}
      ]
    };
    localStorage.setItem('learnsphere_quizbank', JSON.stringify(aiBank));
  }
  
  // Auto-set a final test so it's not empty for the student
  function autoSetFinalTest() {
    if (localStorage.getItem('learnsphere_final_test')) return;
    const finalTestQuestions = [
        { topic: 'Algebra', index: 1 },
        { topic: 'Calculus', index: 0 },
        { topic: 'Statistics', index: 1 },
        { topic: 'Geometry', index: 0 },
        { topic: 'Algebra', index: 2 }
    ];
    localStorage.setItem('learnsphere_final_test', JSON.stringify(finalTestQuestions));
  }
  
  autoGenerateQuizBank();
  autoSetFinalTest();

  // THEME & AUTH
  const user = JSON.parse(localStorage.getItem('learnsphere_user'));
  if (!user || user.role !== 'teacher') {
    if(window.location.pathname.endsWith('teacher_dashboard.html')) {
        alert('Not a teacher. Redirecting...');
        location.href='login.html';
    }
    return;
  }
  document.getElementById('teacher-name').innerText = `Hello, ${user.username}`;
  document.getElementById('btn-logout').addEventListener('click', () => {
    localStorage.removeItem('learnsphere_user');
    location.href='index.html';
  });
  
  const toggleButtons = document.querySelectorAll('#toggle-theme');
  function updateTheme(isDark) {
    document.body.classList.toggle('dark', isDark);
    toggleButtons.forEach(btn => btn.innerText = isDark ? 'Light' : 'Dark');
  }
  updateTheme(localStorage.getItem('learnsphere_theme') === 'dark');
  toggleButtons.forEach(btn => btn.addEventListener('click', () => {
      const newIsDark = !document.body.classList.contains('dark');
      updateTheme(newIsDark);
      localStorage.setItem('learnsphere_theme', newIsDark ? 'dark' : 'light');
  }));

  // NAVIGATION
  const navButtons = document.querySelectorAll('.nav-btn');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      navButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.panel[id^="screen-"]').forEach(p => p.classList.add('hidden'));
      const screenId = 'screen-' + btn.dataset.tScreen;
      document.getElementById(screenId)?.classList.remove('hidden');
      
      if (btn.dataset.tScreen === 'overview') renderOverview();
      if (btn.dataset.tScreen === 'final_test') renderSetFinalTest();
      if (btn.dataset.tScreen === 'analytics') renderAnalytics();
      if (btn.dataset.tScreen === 'announcements') renderAnnouncements();
      if (btn.dataset.tScreen === 'assignments') renderAssignments();
      if (btn.dataset.tScreen === 'gradebook') renderGradebook();
      if (btn.dataset.tScreen === 'reports') renderReports();
    });
  });
  
  document.getElementById('student-search-input').addEventListener('input', renderOverview);
  document.getElementById('sort-select')?.addEventListener('change', renderOverview);
  
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  updateOnlineStatus();

  function updateOnlineStatus() {
      document.getElementById('offline-indicator').style.display = navigator.onLine ? 'none' : 'block';
  }

  // CORE LOGIC HELPERS (stubs, as teacher UI is simplified)
  function renderOverview() { console.log("Rendering overview"); }
  function renderSetFinalTest() { console.log("Rendering set final test"); }
  function renderAnalytics() { console.log("Rendering analytics"); }
  function renderAnnouncements() { console.log("Rendering announcements"); }
  
  // Stubs for new Teacher screens
  function renderAssignments() {
      document.getElementById('screen-assignments').innerHTML = `<h3><i class="fas fa-clipboard-list"></i> Assignments</h3><p class="small-muted">Feature coming soon: Create and manage assignments for your students.</p>`;
  }
  function renderGradebook() {
      document.getElementById('screen-gradebook').innerHTML = `<h3><i class="fas fa-book"></i> Gradebook</h3><p class="small-muted">Feature coming soon: A comprehensive gradebook to track student scores.</p>`;
  }
  function renderReports() {
      document.getElementById('screen-reports').innerHTML = `<h3><i class="fas fa-file-alt"></i> Reports</h3><p class="small-muted">Feature coming soon: Generate detailed performance and progress reports.</p>`;
  }


  // Initial Load
  document.querySelector('[data-t-screen="overview"]').click();
});
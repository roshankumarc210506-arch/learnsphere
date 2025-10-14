// login.js - Handles user authentication
document.addEventListener('DOMContentLoaded', () => {
  // --- HEALTH CHECK BUTTON ---
  const btnHealthCheck = document.getElementById('btn-health-check');
  if (btnHealthCheck) {
    btnHealthCheck.addEventListener('click', async () => {
      loginMsg.innerText = 'Checking server status...';
      loginMsg.className = 'info-msg mt text-center';
      try {
        const res = await fetch('http://localhost:5000/api/health');
        if (!res.ok) throw new Error('Server error');
        const data = await res.json();
        loginMsg.innerText = `Server: ${data.status}, Database: ${data.database}, AI: ${data.ai_service}`;
        loginMsg.className = 'success-msg mt text-center';
      } catch (e) {
        loginMsg.innerText = '❌ Cannot reach backend server at http://localhost:5000. Make sure it is running!';
        loginMsg.className = 'error-msg mt text-center';
      }
    });
  }
  const toggleButtons = document.querySelectorAll('#toggle-theme');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const roleSelect = document.getElementById('role');
  const loginMsg = document.getElementById('login-msg');

  // --- PERSISTENT THEME LOGIC ---
  function updateTheme(isDark) {
    document.body.classList.toggle('dark', isDark);
    localStorage.setItem('learnsphere_theme', isDark ? 'dark' : 'light');
    toggleButtons.forEach(btn => {
      btn.innerText = isDark ? 'Light' : 'Dark';
    });
  }

  // Load theme preference on page load
  const savedTheme = localStorage.getItem('learnsphere_theme');
  const initialIsDark = savedTheme === 'dark';
  updateTheme(initialIsDark);

  // Toggle button handler
  toggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const newIsDark = !document.body.classList.contains('dark');
      updateTheme(newIsDark);
    });
  });
  // ------------------------------

  // --- LOGIN & REGISTER HANDLERS ---
  const btnLogin = document.getElementById('btn-login');
  const btnRegister = document.getElementById('btn-register');
  const toggleFormLink = document.getElementById('toggle-form-link');
  const formTitle = document.getElementById('form-title');
  const formDesc = document.getElementById('form-desc');
  const loginForm = document.getElementById('login-form');

  let isRegisterMode = false;

  function setFormMode(registerMode) {
    isRegisterMode = registerMode;
    if (registerMode) {
      btnLogin.classList.add('hidden');
      btnRegister.classList.remove('hidden');
      formTitle.innerText = 'Create a New Account';
      formDesc.innerText = 'Register as a student or teacher to get started.';
      toggleFormLink.innerText = 'Already have an account? Login';
    } else {
      btnLogin.classList.remove('hidden');
      btnRegister.classList.add('hidden');
      formTitle.innerText = 'Login to Your Account';
      formDesc.innerText = 'Use demo credentials or create a new user.';
      toggleFormLink.innerText = "Don't have an account? Register";
    }
    loginMsg.innerText = '';
    loginMsg.className = 'small-muted mt text-center';
    usernameInput.value = '';
    passwordInput.value = '';
    roleSelect.value = '';
  }

  toggleFormLink.addEventListener('click', () => setFormMode(!isRegisterMode));

  document.getElementById('btn-sample-student').addEventListener('click', () => {
    usernameInput.value = 'student';
    passwordInput.value = '1234';
    roleSelect.value = 'student';
    loginMsg.innerText = 'Student demo credentials filled. Click Login to continue.';
    loginMsg.className = 'small-muted mt text-center';
  });

  document.getElementById('btn-sample-teacher').addEventListener('click', () => {
    usernameInput.value = 'teacher';
    passwordInput.value = '1234';
    roleSelect.value = 'teacher';
    loginMsg.innerText = 'Teacher demo credentials filled. Click Login to continue.';
    loginMsg.className = 'small-muted mt text-center';
  });

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    const role = roleSelect.value;

    if (!username || !password || !role) {
      loginMsg.innerText = 'Please fill in all fields.';
      loginMsg.className = 'error-msg mt text-center';
      return;
    }

    if (isRegisterMode) {
      // Registration logic
      loginMsg.innerText = 'Registering...';
      loginMsg.className = 'info-msg mt text-center';
      try {
        const response = await fetch('http://localhost:5000/api/auth/register', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password, role })
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || data.message || 'Registration failed');
        }
        loginMsg.innerText = 'Registration successful! Logging you in...';
        loginMsg.className = 'success-msg mt text-center';
        setTimeout(() => {
          location.href = data.user.role === 'teacher' ? 'teacher_dashboard.html' : 'student_dashboard.html';
        }, 700);
      } catch (error) {
        loginMsg.innerText = error.message || 'Registration failed. Please try again.';
        loginMsg.className = 'error-msg mt text-center';
      }
    } else {
      // Login logic
      loginMsg.innerText = 'Logging in...';
      loginMsg.className = 'info-msg mt text-center';
      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password, role })
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || data.message || 'Login failed');
        }
        loginMsg.innerText = 'Login successful, redirecting...';
        loginMsg.className = 'success-msg mt text-center';
        setTimeout(() => {
          location.href = data.user.role === 'teacher' ? 'teacher_dashboard.html' : 'student_dashboard.html';
        }, 700);
      } catch (error) {
        loginMsg.innerText = error.message || 'Login failed. Please try again.';
        loginMsg.className = 'error-msg mt text-center';
        if (!navigator.onLine) {
          loginMsg.innerText = 'Please check your internet connection and try again.';
        }
      }
    }
  });

  // Default to login mode
  setFormMode(false);
});